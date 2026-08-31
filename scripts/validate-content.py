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

index = (ROOT / 'index.html').read_text()
home = Page(index)
assert 'civil' in home.ids
assert not re.search(r'ترید|تریدر|فارکس|کریپتو|GoldPulse|trading|data-cat="trade"', index, re.I)
cards = [a for t, a in home.tags if 'art-row' in a.get('class', '').split()]
assert len([a for a in cards if a.get('data-cat') == 'civil']) == 5
assert len([a for a in cards if a.get('data-cat') == 'dental']) == 39
for tag, attrs in home.tags:
    if 'data-goto' in attrs:
        assert attrs['data-goto'] in home.ids

for slug in NEW + REVISED:
    html = (ROOT / f'{slug}.html').read_text()
    page = Page(html)
    assert len([t for t, _ in page.tags if t == 'h1']) == 1
    assert {'sources', 'limits', 'ref-1', 'ref-2'} <= page.ids
    assert '<html lang="fa" dir="rtl">' in html
    assert not re.search('[يـك]', re.sub(r'<[^>]+>', '', html)), f'Nonstandard Persian character in {slug}'
    schema = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', html, re.S).group(1))
    assert schema['dateModified'] == '2026-08-31'
    assert schema['headline'] in html
    assert len(schema['citation']) >= 2
    assert all(url.startswith('https://') for url in schema['citation'])
    for link in page.links:
        if link.startswith('#'):
            assert link[1:] in page.ids, (slug, link)
        elif not re.match(r'^[a-z]+:', link):
            assert (ROOT / link.split('#')[0]).exists(), (slug, link)
    assert 'article-science.css' in page.links

urls = [el.text for el in ET.fromstring((ROOT / 'sitemap.xml').read_text()).iter('{http://www.sitemaps.org/schemas/sitemap/0.9}loc')]
assert len(urls) == 45 and len(set(urls)) == 45
assert all(f'https://fa.omidkheirkhah.com/{s}.html' in urls for s in NEW + REVISED)
baseline = 'c3294524a88c8cdd32ece01ec4669e8f4af34bc9'
names = subprocess.check_output(['git', 'ls-tree', '-r', '--name-only', baseline], cwd=ROOT, text=True).splitlines()
preserved = 0
for name in names:
    if name.startswith('makale-') and name.endswith('.html') and name[:-5] not in REVISED:
        original = subprocess.check_output(['git', 'show', f'{baseline}:{name}'], cwd=ROOT)
        assert (ROOT / name).read_bytes() == original, f'Unexpected article modification: {name}'
        preserved += 1
scripts = re.findall(r'<script>(.*?)</script>', index, re.S)
for script in scripts:
    subprocess.run(['node', '--check'], input=script, text=True, check=True, capture_output=True)
subprocess.run(['git', 'diff', '--check'], cwd=ROOT, check=True)
print(f'PASS: 8 scientific articles, 5 civil + 39 dental cards, 45 sitemap URLs, {preserved} unchanged existing articles, valid HTML nesting, local links, citations, JSON-LD and JavaScript syntax.')
