"""Build static articles from reviewed Persian copy. Requires beautifulsoup4."""
from pathlib import Path
from bs4 import BeautifulSoup
import re, json, html, math, subprocess
ROOT=Path(__file__).resolve().parents[1]
BASE='4d341262b4cb526bdac8885ce8d1e33e93f79441'
DATE='2026-09-16'
FA=str.maketrans('0123456789','۰۱۲۳۴۵۶۷۸۹')
def fa(x): return str(x).translate(FA)
def original(name): return subprocess.check_output(['git','show',f'{BASE}:{name}'],cwd=ROOT,text=True)
def soup(x): return BeautifulSoup(x,'html.parser')
def esc(x): return html.escape(x,quote=True)
def paragraphs(text):
 def ref(m): return ' '.join(f'<a class="cite" href="#ref-{n}" aria-label="منبع {fa(n)}">[{fa(n)}]</a>' for n in m[1].split(','))
 return '\n'.join('<p>'+re.sub(r'\[(\d+(?:,\d+)*)\]',ref,esc(p))+'</p>' for p in text.strip().splitlines() if p.strip())
sources={}
for line in (ROOT/'content/sources.tsv').read_text().splitlines():
 key,org,title,url=line.split('\t');sources[key]=(org,title,url)
idx=soup((ROOT/'index.html').read_text())
cards=idx.select('.art-row');active=[c['href'] for c in cards];categories={c['href']:c['data-cat'] for c in cards}
rewrites={}
for block in (ROOT/'content/dental-revisions.txt').read_text().split('@@')[1:]:
 meta,body=block.split('\n',1);slug,title,refs=meta.split('|')
 if slug=='noma': refs='noma'
 rewrites['makale-'+slug+'.html']=(title,refs.split(','),body)
supplements={}
for block in (ROOT/'content/supplements.txt').read_text().split('@@')[1:]:
 slug,body=block.split('\n',1);supplements['makale-'+slug+'.html']=body
assert len(rewrites)==36 and len(supplements)==8
articles={};archive=[]
for name in active:
 old=soup(original(name));oldbody=old.select_one('.article-body')
 if name in rewrites:
  title,keys,raw=rewrites[name];parts=raw.split('## ');lead=parts.pop(0).strip();sections=[]
  for i,part in enumerate(parts):
   heading,body=part.split('\n',1);anchor='limits' if heading.startswith('محدودیت') else f'section-{i+1}'
   sections.append(f'<section aria-labelledby="{anchor}"><h2 id="{anchor}">{esc(heading)}</h2>{paragraphs(body)}</section>')
  refhtml=[]
  for i,key in enumerate(keys,1):
   org,st,url=sources[key]
   access='چکیده و اطلاعات ناشر؛ متن کامل بررسی نشد' if key=='microbiome' else 'صفحهٔ رسمی بررسی شد'
   refhtml.append(f'<li id="ref-{i}"><span lang="en" dir="ltr" class="source-title">{esc(org)}. <a href="{esc(url)}" target="_blank" rel="noopener noreferrer">{esc(st)}</a></span><small>{access} · تاریخ مشاهده: <time datetime="{DATE}">۲۵ شهریور ۱۴۰۵</time></small></li>')
  content=f'<p class="lead">{esc(lead)}</p>'+''.join(sections)+f'<section class="source-box" aria-labelledby="sources"><h2 id="sources">منابع و پیوندهای اصلی</h2><p>این متن بازنویسی آموزشی فارسی بر پایهٔ منابع زیر است؛ پژوهش اصیل یا مرور نظام‌مند مستقل نیست. تاریخ مشاهده، سال انتشار منبع نیست.</p><ol>{"".join(refhtml)}</ol></section>'
  evidence='مرور آموزشی منابع رسمی سلامت و منابع حرفه‌ای؛ با تفکیک توصیه از محدودیت شواهد.'
  citations=[sources[k][2] for k in keys]
  previous=old.select_one('.source-box')
  archive.append(f'## {name}\n\n'+(previous.get_text(' ',strip=True) if previous else 'فاقد بلوک منبع مشخص')+'\n\nپیوندهای نسخهٔ قبلی:\n'+ '\n'.join('- '+a['href'] for a in (previous.select('a[href]') if previous else []))+'\n\nدلیل بازنویسی: متن کوتاه، ارجاع‌های کلی یا ادعاهای نیازمند محدودسازی؛ منابع مستقیمِ متناسب با متن جدید جایگزین شدند. سابقه برای ردیابی حفظ شده و تأیید اعتبار ارجاع قبلی نیست.\n')
 else:
  title=old.h1.get_text(' ',strip=True);lead=oldbody.select_one('.lead').get_text(' ',strip=True)
  evidence=oldbody.select_one('.evidence-label').get_text(' ',strip=True).replace('پشتوانهٔ این مرور:','').strip()
  schema=json.loads(old.select_one('script[type="application/ld+json"]').string);citations=schema['citation']
  for sel in ['.science-summary','.science-toc','.author-box','.next-article','.disclaimer']:
   for n in oldbody.select(sel): n.decompose()
  target=oldbody.find(id='limits')
  for i,part in enumerate(supplements[name].split('## ')[1:],1):
   heading,body=part.split('\n',1)
   fragment=soup(f'<section aria-labelledby="expanded-{i}"><h2 id="expanded-{i}">{esc(heading)}</h2>{paragraphs(body)}</section>')
   target.insert_before(fragment)
  for n in oldbody.select('.source-box p,.source-box li'):
   # Preserve original source-publication metadata and prior access dates; add new access explicitly below.
   pass
  content=oldbody.decode_contents()
  content=content.replace('</ol>',f'</ol><p>بازبینی پیوندها و توضیحات تکمیلی: <time datetime="{DATE}">۲۵ شهریور ۱۴۰۵</time>. محدودیت دسترسی به متن کامل، در موارد مربوط، همچنان برقرار است.</p>')
 fragment=soup(content)
 # Existing sections already have stable IDs; ensure any new headings are linkable.
 for i,h in enumerate(fragment.select('h2'),1):
  if not h.get('id'):h['id']=f'part-{i}'
 for a in fragment.select('a[target="_blank"]'):a['rel']=['noopener','noreferrer']
 countnode=soup(str(fragment));[n.decompose() for n in countnode.select('.source-box')]
 words=len(countnode.get_text(' ',strip=True).split());minutes=max(1,math.ceil(words/180))
 toc=''.join(f'<a href="#{h["id"]}">{esc(h.get_text(" ",strip=True))}</a>' for h in fragment.select('h2'))
 desc=lead.split('؟')[0].split('!')[0];desc=(desc[:167].rsplit(' ',1)[0]+'…') if len(desc)>170 else desc
 articles[name]=dict(title=title,lead=lead,desc=desc,content=str(fragment),toc=toc,evidence=evidence,citations=citations,words=words,minutes=minutes,cat=categories[name])
for name,a in articles.items():
 catname='سلامت دهان' if a['cat']=='dental' else 'مهندسی عمران';url='https://fa.omidkheirkhah.com/'+name
 # Related reading uses shared subject sources for dental pages; civil pages stay within their field.
 candidates=[n for n in active if n!=name and articles[n]['cat']==a['cat']]
 candidates.sort(key=lambda n:len(set(a['citations'])&set(articles[n]['citations'])),reverse=True)
 related=''.join(f'<a href="{n}"><span>{catname} · {fa(articles[n]["minutes"])} دقیقه</span><h3>{esc(articles[n]["title"])}</h3><span class="read-more">ادامهٔ مطالعه ←</span></a>' for n in candidates[:3])
 schema={'@context':'https://schema.org','@type':'Article','headline':a['title'],'description':a['desc'],'inLanguage':'fa-IR','dateModified':DATE,'mainEntityOfPage':url,'publisher':{'@type':'Person','name':'دکتر امید خیرخواه','url':'https://fa.omidkheirkhah.com/'},'citation':a['citations'],'wordCount':a['words']}
 note='این متن آموزشی است و جایگزین معاینه، تشخیص یا درمان فردی توسط دندان‌پزشک نیست.' if a['cat']=='dental' else 'این متن آموزشی است و جایگزین طراحی، ارزیابی ایمنی یا تأیید مهندس مسئول پروژه نیست.'
 page=f'''<!DOCTYPE html>
<html lang="fa" dir="rtl"><head><meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(a['title'])} | دکتر امید خیرخواه</title><meta name="description" content="{esc(a['desc'])}"><link rel="canonical" href="{url}">
<meta property="og:type" content="article"><meta property="og:site_name" content="دکتر امید خیرخواه"><meta property="og:locale" content="fa_IR"><meta property="og:title" content="{esc(a['title'])}"><meta property="og:description" content="{esc(a['desc'])}"><meta property="og:url" content="{url}"><meta property="og:image" content="https://fa.omidkheirkhah.com/profile.jpg"><meta name="twitter:card" content="summary">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin><link href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;500;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="article-science.css?v=20260916"><script src="article.js?v=20260916" defer></script><script type="application/ld+json">{json.dumps(schema,ensure_ascii=False,separators=(',',':'))}</script></head>
<body><a class="skip-link" href="#article-content">رفتن به متن مقاله</a><div class="reading-progress" aria-hidden="true"><span id="readingProgress"></span></div>
<nav class="article-nav" aria-label="ناوبری اصلی"><a class="nav-logo" href="index.html#hub">دکتر امید خیرخواه<span>دانش، تجربه، نگاه تازه</span></a><a class="nav-back" href="index.html#kesifet-{a['cat']}">همهٔ مقاله‌های {catname} ←</a></nav>
<main><header class="article-hero"><div class="article-category"><a href="index.html#kesifet-{a['cat']}">{catname}</a><span>مقالهٔ آموزشی و تحلیلی</span></div><h1 class="article-title">{esc(a['title'])}</h1><div class="article-meta"><span>حدود {fa(a['minutes'])} دقیقه مطالعه</span><span>به‌روزرسانی متن: <time datetime="{DATE}">۲۵ شهریور ۱۴۰۵</time></span><a href="#sources">{fa(len(a['citations']))} منبع مستقیم</a></div><div class="article-tools"><button type="button" id="copyArticle">کپی پیوند مقاله</button><button type="button" id="printArticle">چاپ / ذخیرهٔ PDF</button><span id="shareStatus" role="status" aria-live="polite"></span></div></header>
<div class="reading-layout"><aside class="reading-toc"><details open><summary>در این مقاله می‌خوانید</summary><nav aria-label="فهرست مطالب">{a['toc']}</nav></details><p>پشتوانهٔ متن</p><div class="evidence-label">{esc(a['evidence'])}</div></aside><article class="article-body" id="article-content" tabindex="-1">{a['content']}<p class="disclaimer">{note}</p><div class="author-box"><img src="profile.jpg" alt="دکتر امید خیرخواه" width="64" height="64" loading="lazy" decoding="async"><div><h2>دکتر امید خیرخواه</h2><p>انتشار و بازنویسی آموزشی برای این وب‌سایت؛ یافته‌های علمی متعلق به پژوهشگران و نهادهای ارجاع‌شده‌اند. این متن داوری تخصصی انسانی مستقل نشده است.</p><a href="index.html#benkimim">دربارهٔ من ←</a></div></div></article></div>
<section class="related-reading" aria-labelledby="related-title"><p class="eyebrow">ادامهٔ مسیر مطالعه</p><h2 id="related-title">این موضوع‌ها را هم بخوانید</h2><div class="related-grid">{related}</div></section>
<section class="article-contact"><div><h2>پرسشی دربارهٔ این مطلب دارید؟</h2><p>برای پیشنهاد موضوع، اصلاح محتوا یا گفت‌وگو در ارتباط باشید.</p></div><a href="index.html#iletisim">راه‌های ارتباط ←</a></section></main><footer><a href="index.html#hub">دکتر امید خیرخواه</a><a href="index.html#kesifet">کتابخانهٔ مقاله‌ها</a><a href="#article-content">بازگشت به متن ↑</a></footer></body></html>'''
 (ROOT/name).write_text(page)
for card in cards:
 a=articles[card['href']];card.select_one('.art-title').string=a['title']
 for n in card.select('.art-excerpt'):n.decompose()
 excerpt=idx.new_tag('p',attrs={'class':'art-excerpt'});excerpt.string=a['desc'];card.select_one('.art-title').insert_after(excerpt)
 card.select_one('.art-meta').string=f'{fa(a["minutes"])} دقیقه مطالعه · {fa(len(a["citations"]))} منبع'
 card['data-keywords']=' '.join(soup(a['content']).get_text(' ',strip=True).split()[:70])
(ROOT/'index.html').write_text(str(idx))
(ROOT/'docs/PREVIOUS-SOURCES-2026-09-16.md').write_text('# سابقهٔ منابع پیش از بازنویسی\n\nمبنای ثبت: commit '+BASE+'\n\n'+'\n'.join(archive))
(ROOT/'content/article-manifest.json').write_text(json.dumps({n:{k:a[k] for k in ['title','cat','words','minutes','citations']} for n,a in articles.items()},ensure_ascii=False,indent=2)+'\n')
print('Built',len(articles),'articles. Body words:',min(a['words'] for a in articles.values()),'to',max(a['words'] for a in articles.values()))
