from pathlib import Path
from html.parser import HTMLParser
import json, xml.etree.ElementTree as ET
from urllib.parse import urlsplit
R=Path(__file__).resolve().parents[1]
d=json.loads((R/'content/latest.json').read_text())
class Page(HTMLParser):
    def __init__(self): super().__init__(); self.links=[];self.ids=set();self.lang=None;self.canonical=[];self.alternates=[];self.jsonld=False
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a: assert a['id'] not in self.ids,a['id'];self.ids.add(a['id'])
        if tag=='html':self.lang=a.get('lang')
        if tag in ('a','img','script','link'):
            link=a.get('href',a.get('src'))
            if link:self.links.append(link)
        if tag=='img':assert a.get('alt') and a.get('width') and a.get('height')
        if tag=='link' and a.get('rel')=='canonical':self.canonical.append(a['href'])
        if tag=='link' and a.get('hreflang'):self.alternates.append(a['hreflang'])
        if tag=='script' and a.get('type')=='application/ld+json':self.jsonld=True
    def handle_data(self,data):
        if self.jsonld:json.loads(data);self.jsonld=False
files=[R/'latest.html']+[R/'latest'/f'{a["id"]}.html' for a in d['articles']]
for f in files:
    p=Page();p.feed(f.read_text());assert p.lang==d['locale'];assert len(p.canonical)==1;assert set(p.alternates)=={'fa','tr'}
    for link in p.links:
        u=urlsplit(link)
        if u.scheme or u.netloc:continue
        target=(f.parent/u.path) if u.path else f
        assert target.exists(),(f,link)
        if u.fragment and target==f:assert u.fragment in p.ids,(f,link)
for name in ['sitemap.xml','latest.xml']:ET.parse(R/name)
home=(R/'index.html').read_text();assert home.count('<!-- LATEST:START -->')==1 and home.count('<!-- LATEST:END -->')==1
assert len({a['id'] for a in d['articles']})==len(d['articles'])
print(d['locale'],': static pages, anchors, assets, canonical/hreflang, JSON-LD, RSS and sitemap passed')
