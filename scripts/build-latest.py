#!/usr/bin/env python3
"""Build static, crawlable journal pages using only the Python standard library."""
from pathlib import Path
import json, html, re, math
from datetime import date
from email.utils import format_datetime
from datetime import datetime, timezone
R=Path(__file__).resolve().parents[1]
D=json.loads((R/'content/latest.json').read_text()); L=D['locale']; FA=L=='fa'
BASE='https://'+(R/'CNAME').read_text().strip()
OTHER='https://omidkheirkhah.com' if FA else 'https://fa.omidkheirkhah.com'
A=sorted(D['articles'],key=lambda a:(a['published'],a['id']),reverse=True)
T= dict(title='جدیدترین‌ها',brand='دکتر امید خیرخواه',home='صفحهٔ اصلی',intro='پژوهش تازه، با نگاهی دقیق‌تر.',deck='دندان‌پزشکی، پزشکی و سلامت؛ خواندنی‌های علمی با روایت روشن، منابع اصلی و توجه به محدودیت شواهد.',all='همه',dentistry='دندان‌پزشکی',medicine='پزشکی',health='سلامت',read='مطالعهٔ کامل',archive='آرشیو جدیدترین‌ها',search='جست‌وجو در عنوان و متن',empty='هنوز مطلبی با این انتخاب منتشر نشده است.',source='منابع اصلی',related='برای مطالعهٔ بیشتر',quick='اگر فقط یک دقیقه وقت دارید',contents='در این مقاله',published='انتشار این مطلب',study='انتشار پژوهش',minute='دقیقه مطالعه',policy='شیوهٔ انتخاب و نگارش',policytext='تازگی تنها معیار نیست. منابع اصلی، نوع مطالعه و محدودیت‌ها بررسی می‌شوند. متن‌ها بازنویسی تحلیلی و آموزشی‌اند؛ پژوهش دیگران به نام این سایت معرفی نمی‌شود. انتشار به وجود مطلب تازه و معتبر وابسته است.',disclaimer='این مطلب برای آگاهی عمومی است و جایگزین تشخیص یا درمان فردی نیست.',copy='کپی پیوند',copied='پیوند کپی شد',failed='لطفاً پیوند را از نوار نشانی کپی کنید.',results='مطلب',photo='عکس و منبع',language='Türkçe',skip='رفتن به محتوا',edition='دانش برای زندگی',toc='فهرست مطالب',back='بازگشت به جدیدترین‌ها',new='تازه‌ترین خواندنی',rss='خوراک RSS') if FA else dict(title='En Yeniler',brand='Dr. Omid Kheirkhah',home='Ana sayfa',intro='Yeni araştırmalara daha yakından bakın.',deck='Diş hekimliği, tıp ve sağlık: anlaşılır anlatım, birincil kaynaklar ve kanıtların sınırlarını gözeten bilim yazıları.',all='Tümü',dentistry='Diş hekimliği',medicine='Tıp',health='Sağlık',read='Yazıyı okuyun',archive='En Yeniler arşivi',search='Başlık ve metinde arayın',empty='Bu seçim için henüz bir yazı yayımlanmadı.',source='Birincil kaynaklar',related='Okumaya devam edin',quick='Bir dakikada ana fikir',contents='Bu yazıda',published='Yazının yayın tarihi',study='Araştırmanın yayın tarihi',minute='dakika okuma',policy='Seçim ve yazım yaklaşımı',policytext='Yalnızca yeni olması yeterli değil. Birincil kaynaklar, çalışma türü ve sınırlılıklar değerlendirilir. Yazılar özgün bir anlatımla hazırlanan eğitici değerlendirmelerdir; başkalarının araştırmaları bu siteye mal edilmez. Yayın, yeni ve güvenilir içerik bulunmasına bağlıdır.',disclaimer='Bu yazı genel bilgilendirme amaçlıdır; kişiye özel tanı veya tedavinin yerini tutmaz.',copy='Bağlantıyı kopyala',copied='Bağlantı kopyalandı',failed='Lütfen adres çubuğundaki bağlantıyı kopyalayın.',results='yazı',photo='Fotoğraf ve kaynak',language='فارسی',skip='İçeriğe geç',edition='Yaşam için bilim',toc='İçindekiler',back='En Yeniler’e dön',new='Son yayın',rss='RSS akışı')
def e(v): return html.escape(str(v),quote=True)
def num(v): return str(v).translate(str.maketrans('0123456789','۰۱۲۳۴۵۶۷۸۹')) if FA else str(v)
def dt(v):
    d=date.fromisoformat(v); months=['ژانویه','فوریه','مارس','آوریل','مه','ژوئن','ژوئیه','اوت','سپتامبر','اکتبر','نوامبر','دسامبر'] if FA else ['Ocak','Şubat','Mart','Nisan','Mayıs','Haziran','Temmuz','Ağustos','Eylül','Ekim','Kasım','Aralık']
    return f'{num(d.day)} {months[d.month-1]} {num(d.year)}'
def url(a): return 'latest/'+a['id']+'.html'
def words(a): return len(' '.join(p for s in a['sections'] for p in s['paragraphs']).split())
def header(prefix):
    return f'<a class="j-skip" href="#content">{T["skip"]}</a><header class="j-nav"><a class="j-brand" href="{prefix}index.html">{T["brand"]}</a><nav aria-label="{T["title"]}"><a href="{prefix}index.html">{T["home"]}</a><a href="{prefix}latest.html">{T["title"]}</a><a lang="{"tr" if FA else "fa"}" href="{{alternate}}">{T["language"]}</a></nav></header>'
def shell(title,desc,path,body,article=None):
    pre='../' if path.startswith('latest/') else ''
    schema={'@context':'https://schema.org','@type':'Article' if article else 'CollectionPage','headline':title,'description':desc,'url':BASE+'/'+path,'inLanguage':L}
    if article: schema.update(datePublished=article['published'],dateModified=article['published'],image=BASE+'/'+article['image'],publisher={'@type':'Organization','name':T['brand']},citation=[s['url'] for s in article['sources']])
    return f'''<!doctype html><html lang="{L}" dir="{'rtl' if FA else 'ltr'}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{e(title)} | {T['brand']}</title><meta name="description" content="{e(desc)}"><link rel="canonical" href="{BASE}/{path}"><link rel="alternate" hreflang="{L}" href="{BASE}/{path}"><link rel="alternate" hreflang="{'tr' if FA else 'fa'}" href="{OTHER}/{path}"><link rel="alternate" type="application/rss+xml" title="{T['title']}" href="{pre}latest.xml"><meta property="og:type" content="{'article' if article else 'website'}"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}"><meta property="og:url" content="{BASE}/{path}"><meta property="og:image" content="{BASE}/{article['image'] if article else 'tooth.jpg'}"><meta name="twitter:card" content="summary_large_image"><link rel="preconnect" href="https://fonts.googleapis.com"><link href="https://fonts.googleapis.com/css2?family=Vazirmatn:wght@400;500;600;700&family=Manrope:wght@400;500;600;700&display=swap" rel="stylesheet"><link rel="stylesheet" href="{pre}latest.css"><script defer src="{pre}latest.js"></script><script type="application/ld+json">{json.dumps(schema,ensure_ascii=False).replace('<','\\u003c')}</script></head><body class="journal">{header(pre).replace('{alternate}',OTHER+'/'+path)}<main id="content">{body}</main><footer class="j-footer"><a href="{pre}latest.html">{T['title']}</a><p>{T['disclaimer']}</p><a href="{pre}latest.xml">{T['rss']}</a><span>© {num(2026)} · {T['brand']}</span></footer></body></html>'''
def card(a,featured=False):
    return f'''<article class="j-card {'j-featured' if featured else ''}" data-category="{a['category']}" data-search="{e(a['title']+' '+a['summary']+' '+' '.join(p for section in a['sections'] for p in section['paragraphs']))}"><div class="j-card-art"><img src="{e(a['image'])}" width="236" height="118" alt="{e(a['alt'])}" {'loading="lazy"' if not featured else 'fetchpriority="high"'}><span>{T['photo']} · {e(a['imageCredit'])}</span></div><div class="j-card-content"><div class="j-meta"><span>{T[a['category']]}</span><time datetime="{a['published']}">{dt(a['published'])}</time></div><h2><a href="{url(a)}">{e(a['title'])}</a></h2><p>{e(a['summary'])}</p><div class="j-evidence">{e(a['evidence'])}</div><a class="j-read" href="{url(a)}">{T['read']} <span aria-hidden="true">{'←' if FA else '→'}</span></a><small>{num(math.ceil(words(a)/180))} {T['minute']}</small></div></article>'''
assert D['schemaVersion']==1 and L in ('fa','tr')
assert len({a['id'] for a in A})==len(A)
for a in A:
    assert re.fullmatch(r'\d{4}-\d{2}-\d{2}-[a-z0-9-]+',a['id'])
    assert a['category'] in ('dentistry','medicine','health')
    assert date.fromisoformat(a['studyDate'])<=date.fromisoformat(a['published'])
    assert a['imageRights'] and a['alt'] and a['sources'] and a['access']
    assert (R/a['image']).is_file()
    assert all((R/x['path']).is_file() for x in a['related'])
    assert all(s['url'].startswith('https://') for s in a['sources'])
filters=''.join(f'<button type="button" data-filter="{k}" aria-pressed="{str(k=="all").lower()}">{T[k]} <span>{num(len(A) if k=="all" else sum(a["category"]==k for a in A))}</span></button>' for k in ('all','dentistry','medicine','health'))
body=f'''<section class="j-hero j-wrap"><div class="j-kicker">{T['edition']} <span>01 / JOURNAL</span></div><h1>{T['title']}<span>.</span></h1><div class="j-intro"><h2>{T['intro']}</h2><p>{T['deck']}</p></div></section><section class="j-wrap j-archive" aria-label="{T['archive']}"><div class="j-tools"><div class="j-filters" aria-label="{T['archive']}">{filters}</div><label class="j-search">{T['search']}<input type="search" id="journal-search" placeholder="{T['search']}"></label></div><p id="journal-count" class="j-count" aria-live="polite">{num(len(A))} {T['results']}</p><div class="j-grid">{''.join(card(a,i==0) for i,a in enumerate(A))}</div><p id="journal-empty" hidden>{T['empty']}</p></section><section class="j-wrap j-policy"><span class="j-kicker">{T['policy']}</span><p>{T['policytext']}</p></section>'''
(R/'latest.html').write_text(shell(T['title'],T['deck'],'latest.html',body))
(R/'latest').mkdir(exist_ok=True)
for a in A:
    sources=''.join(f'<li id="source-{i}"><a href="{e(s["url"])}" rel="noopener noreferrer">{e(s["label"])}</a>'+ (f' · <a dir="ltr" href="https://doi.org/{e(s["doi"])}">DOI: {e(s["doi"])}</a>' if s.get('doi') else '')+'</li>' for i,s in enumerate(a['sources'],1))
    def cite(p):
        return re.sub(r'\[([0-9۰-۹،, ]+)\]',lambda m:'<sup>'+ ' '.join(f'<a href="#source-{int(n.translate(str.maketrans("۰۱۲۳۴۵۶۷۸۹","0123456789")))}">[{n}]</a>' for n in re.findall(r'[0-9۰-۹]+',m[1]))+'</sup>',e(p))
    sections=''.join(f'<section id="section-{i}"><h2>{e(s["heading"])}</h2>'+''.join('<p>'+cite(p)+'</p>' for p in s['paragraphs'])+'</section>' for i,s in enumerate(a['sections']))
    toc=''.join(f'<li><a href="#section-{i}">{e(s["heading"])}</a></li>' for i,s in enumerate(a['sections']))
    related=''.join(f'<a href="../{e(x["path"])}">{e(x["label"])} <span aria-hidden="true">↗</span></a>' for x in a['related'])
    body=f'''<div class="j-wrap j-article-head"><a class="j-back" href="../latest.html">{T['back']}</a><div class="j-meta"><span>{T[a['category']]}</span><span>{e(a['evidence'])}</span></div><h1>{e(a['title'])}</h1><p class="j-deck">{e(a['summary'])}</p><div class="j-dates"><span>{T['published']}: <time datetime="{a['published']}">{dt(a['published'])}</time></span><span>{T['study']}: <time datetime="{a['studyDate']}">{dt(a['studyDate'])}</time></span><span>{num(math.ceil(words(a)/180))} {T['minute']}</span></div></div><div class="j-wrap j-reading"><aside class="j-toc"><strong>{T['toc']}</strong><ol>{toc}<li><a href="#sources">{T['source']}</a></li></ol><button type="button" id="copy-link" data-done="{T['copied']}" data-failed="{T['failed']}">{T['copy']}</button><p id="copy-status" role="status"></p></aside><article class="j-prose"><div class="j-takeaway"><span>{T['quick']}</span><p>{e(a['takeaway'])}</p></div><figure class="j-figure"><img src="../{a['image']}" width="236" height="118" alt="{e(a['alt'])}"><figcaption>{e(a['caption'])} <a href="{e(a['imageSource'])}">NIDCR ↗</a></figcaption></figure>{sections}<section id="sources"><h2>{T['source']}</h2><p class="j-access">{e(a['access'])}</p><ol class="j-sources">{sources}</ol></section><p class="j-disclaimer">{T['disclaimer']}</p><section class="j-related"><h2>{T['related']}</h2>{related}</section></article></div>'''
    (R/url(a)).write_text(shell(a['title'],a['summary'],url(a),body,a))
# Rebuild the bounded journal fragment only; preserve all other home content.
p=R/'index.html'; home=p.read_text(); start='<!-- LATEST:START -->'; end='<!-- LATEST:END -->'
fragment=start+f'<section class="latest-home" aria-labelledby="latest-home-title"><div><span>{T["edition"]}</span><h2 id="latest-home-title">{T["title"]}</h2><p>{T["deck"]}</p><a href="latest.html">{T["archive"]} ↗</a></div><article><span>{T["new"]} · {dt(A[0]["published"])}</span><h3><a href="{url(A[0])}">{e(A[0]["title"])}</a></h3><p>{e(A[0]["summary"])}</p><a href="{url(A[0])}">{T["read"]} ↗</a></article></section>'+end
if start in home: home=re.sub(re.escape(start)+'.*?'+re.escape(end),lambda _:fragment,home,flags=re.S)
else:
    target='<div class="wrap hub-contact">' if FA else '      <div class="hub-contact'
    pos=home.index(target); home=home[:pos]+fragment+'\n'+home[pos:]
if 'href="latest.css"' not in home: home=home.replace('</head>','<link rel="stylesheet" href="latest.css">\n</head>')
p.write_text(home)
# Only add journal URLs to the existing sitemap; leave historical entries untouched.
p=R/'sitemap.xml'; sitemap=p.read_text()
for path in ['latest.html']+[url(a) for a in A]:
    if BASE+'/'+path not in sitemap: sitemap=sitemap.replace('</urlset>',f'<url><loc>{BASE}/{path}</loc></url>\n</urlset>')
p.write_text(sitemap)
items=''.join(f'<item><title>{e(a["title"])}</title><link>{BASE}/{url(a)}</link><guid isPermaLink="true">{BASE}/{url(a)}</guid><description>{e(a["summary"])}</description><pubDate>{format_datetime(datetime.fromisoformat(a["published"]).replace(tzinfo=timezone.utc))}</pubDate></item>' for a in A)
(R/'latest.xml').write_text(f'<?xml version="1.0" encoding="UTF-8"?><rss version="2.0"><channel><title>{T["title"]}</title><link>{BASE}/latest.html</link><description>{e(T["deck"])}</description><language>{L}</language>{items}</channel></rss>')
print(f'{L}: built {len(A)} article(s), archive, RSS, home fragment and sitemap; words: '+str([words(a) for a in A]))
