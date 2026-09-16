"""Read-only checks for the 2026-08 editorial release; no browser required."""
from html.parser import HTMLParser
from pathlib import Path
import json
import re
import subprocess
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
NEW = ['makale-beton-energy', 'makale-beton-self-healing', 'makale-zalzale-functional-recovery', 'makale-beton-low-carbon', 'makale-digital-twin-bridge']
REVISED = ['makale-dis-curugu', 'makale-dis-firca', 'makale-florayd']
VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}

class Page(HTMLParser):
    def __init__(self, html):
        super().__init__(convert_charrefs=True)
        self.stack, self.ids, self.links, self.tags = [], set(), [], []
        self.feed(html)
        assert not self.stack, f'Unclosed tags: {self.stack}'

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.tags.append((tag, attrs))
        if 'id' in attrs:
            assert attrs['id'] not in self.ids, f'Duplicate ID: {attrs["id"]}'
            self.ids.add(attrs['id'])
        for key in ('href', 'src'):
            if key in attrs:
                self.links.append(attrs[key])
        if tag not in VOID:
            self.stack.append(tag)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            self.handle_endtag(tag)

    def handle_endtag(self, tag):
        assert self.stack and self.stack[-1] == tag, f'Unexpected closing {tag}: {self.stack[-4:]}'
        self.stack.pop()

from urllib.parse import urlsplit
manifest=json.loads((ROOT/'content/article-manifest.json').read_text())
index=(ROOT/'index.html').read_text();home=Page(index)
assert len(manifest)==44
assert not re.search(r'ترید|تریدر|فارکس|کریپتو|GoldPulse|trading|data-cat="trade"',index,re.I)
cards=[a for t,a in home.tags if 'art-row' in a.get('class','').split()]
assert len([a for a in cards if a.get('data-cat')=='civil'])==5
assert len([a for a in cards if a.get('data-cat')=='dental'])==39
assert {a['href'] for a in cards}==set(manifest)
assert all(t=='a' for t,a in home.tags if 'art-row' in a.get('class','').split())
labels={a.get('for') for t,a in home.tags if t=='label'}
for t,a in home.tags:
 if 'data-goto' in a:assert a['data-goto'] in home.ids
 if t in ('input','select','textarea'):assert a.get('id') in labels,(t,a)
 if t=='input' and a.get('name')=='email':assert 'required' not in a
assert any(t=='button' and a.get('id')=='menuBtn' and a.get('aria-controls')=='menuOverlay' for t,a in home.tags)
for name in ['index.html',*manifest]:
 text=(ROOT/name).read_text();page=Page(text)
 for link in page.links:
  path=urlsplit(link)
  if path.scheme or path.netloc:continue
  if not path.path and path.fragment:
   assert path.fragment in page.ids or (name=='index.html' and re.fullmatch(r'kesifet-(all|dental|civil)',path.fragment)),(name,link)
  elif path.path:
   assert (ROOT/path.path).exists(),(name,link)
 for t,a in page.tags:
  assert not any(k.startswith('on') for k in a),(name,t,'inline handler')
  if a.get('target')=='_blank':assert 'noopener' in a.get('rel',''),(name,a)
 if name=='index.html':continue
 assert len([t for t,_ in page.tags if t=='h1'])==1
 assert {'sources','limits','ref-1','article-content'}<=page.ids
 assert '<html lang="fa" dir="rtl">' in text
 schema=json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>',text,re.S).group(1))
 assert schema['dateModified']=='2026-09-16'
 assert schema['citation']==manifest[name]['citations']
 assert schema['wordCount']>=400
 assert all(url.startswith('https://') for url in schema['citation'])
 assert any('article-science.css' in l for l in page.links)
 assert len([t for t,a in page.tags if t=='h2'])>=7
 assert not re.search(r'\[\d+(?:,\d+)+\]',text),(name,'unrendered citations')
urls=[el.text for el in ET.fromstring((ROOT/'sitemap.xml').read_text()).iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
assert len(urls)==len(set(urls))==45
assert all('https://fa.omidkheirkhah.com/'+s in urls for s in manifest)
baseline='4d341262b4cb526bdac8885ce8d1e33e93f79441'
names=subprocess.check_output(['git','ls-tree','-r','--name-only',baseline],cwd=ROOT,text=True).splitlines()
preserved=0
for name in names:
 if name.startswith('makale-') and name.endswith('.html') and name not in manifest:
  original=subprocess.check_output(['git','show',f'{baseline}:{name}'],cwd=ROOT)
  assert (ROOT/name).read_bytes()==original, f'Inactive article changed: {name}'
  preserved+=1
assert preserved==27
for js in ['site.js','article.js']:
 subprocess.run(['node','--check',str(ROOT/js)],check=True,capture_output=True)
subprocess.run(['git','diff','--check'],cwd=ROOT,check=True)
print('PASS: 44 articles, 44 real article links, 45 sitemap URLs, 27 inactive articles preserved; HTML nesting, unique IDs, local assets, citations, metadata, accessible form labels and JS syntax.')
