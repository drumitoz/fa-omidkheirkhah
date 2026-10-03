/* motion.js — shared visual layer for fa.omidkheirkhah.com and omidkheirkhah.com.
   Keep this file byte-identical in both repositories. Purely decorative: it never
   changes content or navigation, and backs off for reduced motion and touch. */
(()=>{
'use strict';
const root=document.documentElement;
const reduce=matchMedia('(prefers-reduced-motion: reduce)').matches;
const fine=matchMedia('(hover: hover) and (pointer: fine)').matches;
const rtl=(root.dir||document.body.dir)==='rtl';
const $=(s,c=document)=>c.querySelector(s), $$=(s,c=document)=>[...c.querySelectorAll(s)];
root.classList.add('fx');

/* Scroll progress */
const bar=document.createElement('div');bar.className='fx-progress';bar.setAttribute('aria-hidden','true');
bar.style.setProperty('--p-origin',rtl?'right':'left');document.body.append(bar);
// The Persian site scrolls the window; the Turkish site scrolls inside each .scene. Listen in capture to cover both.
let ticking=false,scroller=document.scrollingElement||root;
const updateBar=()=>{ticking=false;const max=scroller.scrollHeight-scroller.clientHeight;bar.style.setProperty('--p',max>0?Math.min(1,scroller.scrollTop/max):0);};
addEventListener('scroll',e=>{const t=e.target;scroller=t===document?(document.scrollingElement||root):t;if(!ticking){ticking=true;requestAnimationFrame(updateBar);}},{passive:true,capture:true});
addEventListener('resize',updateBar);updateBar();

/* Latest articles: a horizontal reel that slides sideways as you scroll down.
   Built from content/latest.json; the static block from build-latest.py stays as the fallback. */
const latest=$('.latest-home');
if(latest&&window.fetch){
  const fa=(root.lang||'').startsWith('fa');
  const T=fa?{cat:{dentistry:'دندان‌پزشکی',medicine:'پزشکی',health:'سلامت'},read:'مطالعهٔ کامل ↗',all:'همهٔ جدیدترین‌ها',locale:'fa-IR-u-ca-gregory'}
            :{cat:{dentistry:'Diş Hekimliği',medicine:'Tıp',health:'Sağlık'},read:'Devamını oku ↗',all:'Tüm yeni yazılar',locale:'tr-TR'};
  const num=n=>String(n).padStart(2,'0').replace(/\d/g,d=>fa?'۰۱۲۳۴۵۶۷۸۹'[d]:d);
  const el=(tag,cls,text)=>{const e=document.createElement(tag);if(cls)e.className=cls;if(text!=null)e.textContent=text;return e;};
  fetch('content/latest.json').then(r=>r.ok?r.json():Promise.reject()).then(data=>{
    const items=(data.articles||[]).slice().sort((a,b)=>b.published.localeCompare(a.published));
    if(items.length<2)return;
    const reel=el('div','fx-reel'),sticky=el('div','fx-reel-sticky'),track=el('div','fx-reel-track');
    reel.setAttribute('aria-label',latest.querySelector('h2')?.textContent||'');
    items.forEach(a=>{
      const card=el('a','fx-reel-card');card.href='latest/'+a.id+'.html';
      const media=el('div','fx-reel-media');
      if(a.image){const img=el('img');img.src=a.image;img.alt=a.alt||'';img.loading='lazy';img.decoding='async';media.append(img);}
      if(T.cat[a.category])media.append(el('span','fx-reel-chip',T.cat[a.category]));
      const body=el('div','fx-reel-body');
      let date=a.published;try{date=new Date(a.published+'T12:00:00').toLocaleDateString(T.locale,{day:'numeric',month:'long',year:'numeric'});}catch(e){}
      body.append(el('span','fx-reel-date',date),el('h3','fx-reel-title',a.title),el('p','fx-reel-sum',a.summary),el('span','fx-reel-more',T.read));
      card.append(media,body);track.append(card);
    });
    const end=el('a','fx-reel-card fx-reel-end');end.href='latest.html';end.append(el('span',null,fa?'←':'→'),el('b',null,T.all));track.append(end);
    const meta=el('div','fx-reel-meta'),count=el('span','fx-reel-count'),line=el('span','fx-reel-line');line.append(el('i'));
    line.style.setProperty('--p-origin',rtl?'right':'left');meta.append(count,line);
    sticky.append(track,meta);reel.append(sticky);latest.after(reel);latest.classList.add('fx-has-reel');
    // Sticky needs ancestors that clip without becoming scroll containers. Swap only an
    // existing 'hidden' for 'clip' (same look) so nothing that was visible gets cropped.
    for(let a=reel.parentElement;a;a=a.parentElement){
      const cs=getComputedStyle(a);
      if(cs.overflowX==='hidden')a.style.overflowX='clip';
      if(cs.overflowY==='hidden')a.style.overflowY='clip';
    }
    const cards=[...track.children],total=items.length;
    count.textContent=num(1)+' / '+num(total);
    if(reduce){reel.classList.add('fx-static');return;}
    let span=0,raf=0;
    const layout=()=>{span=Math.max(0,track.scrollWidth-innerWidth);reel.style.height=`calc(100svh - var(--nav-h,72px) + ${span}px)`;update();};
    const update=()=>{
      raf=0;if(!reel.offsetParent)return;
      const top=reel.getBoundingClientRect().top-(parseFloat(getComputedStyle(root).getPropertyValue('--nav-h'))||72);
      const p=span?Math.min(1,Math.max(0,-top/span)):0;
      track.style.transform=`translate3d(${(rtl?1:-1)*p*span}px,0,0)`;
      line.style.setProperty('--rp',p);
      const mid=innerWidth/2;
      cards.forEach(c=>{
        const r=c.getBoundingClientRect(),d=(r.left+r.width/2-mid)/innerWidth,ad=Math.min(1,Math.abs(d));
        c.style.transform=`rotateY(${(-d*18).toFixed(2)}deg) scale(${(1-ad*.12).toFixed(3)}) translateZ(${(-ad*80).toFixed(1)}px)`;
        c.style.opacity=(1-ad*.55).toFixed(3);
        const img=c.querySelector('img');if(img)img.style.setProperty('--par',(d*-40).toFixed(1)+'px');
      });
      count.textContent=num(Math.min(total,Math.round(p*total)+1))+' / '+num(total);
    };
    const req=()=>{if(!raf)raf=requestAnimationFrame(update);};
    addEventListener('scroll',req,{passive:true,capture:true});addEventListener('resize',layout);
    new ResizeObserver(layout).observe(track);
    new MutationObserver(layout).observe(latest.closest('.scene')||document.body,{attributes:true,attributeFilter:['class']});
    layout();
  }).catch(()=>{});
}

if(reduce)return;

/* Hero headline: split into words that rise one after another */
const h1=$('h1.hero-h');
if(h1){
  let i=0;
  const walk=node=>{
    for(const n of [...node.childNodes]){
      if(n.nodeType===3){
        if(!n.textContent.trim())continue;
        const frag=document.createDocumentFragment();
        n.textContent.split(/(\s+)/).forEach(part=>{
          if(!part)return;
          if(/^\s+$/.test(part)){frag.append(part);return;}
          const w=document.createElement('span');w.className='fx-w';
          const inner=document.createElement('span');inner.textContent=part;inner.style.setProperty('--i',i++);
          w.append(inner);frag.append(w);
        });
        n.replaceWith(frag);
      }else if(n.nodeType===1)walk(n);
    }
  };
  walk(h1);h1.classList.add('fx-split');
}

/* Hero: gold dust. Plain CSS-animated dots behind the hero; a <canvas> here made
   Chrome paint the profile photo and tooth black on desktop. */
const hero=$('.hero');
if(hero){
  const host=hero.parentElement;if(getComputedStyle(host).position==='static')host.style.position='relative';
  const dust=document.createElement('div');dust.className='fx-dust';dust.setAttribute('aria-hidden','true');
  const n=innerWidth<700?18:36;
  for(let i=0;i<n;i++){
    const d=document.createElement('i'),sz=(Math.random()*2.2+1).toFixed(1);
    d.style.cssText=`left:${(Math.random()*100).toFixed(2)}%;top:${(Math.random()*100).toFixed(2)}%;width:${sz}px;height:${sz}px;--dur:${(Math.random()*10+9).toFixed(1)}s;--del:${(-Math.random()*18).toFixed(1)}s;--dx:${((Math.random()-.5)*60).toFixed(0)}px`;
    dust.append(d);
  }
  host.insertBefore(dust,hero);
  const place=()=>{dust.style.top=Math.max(0,hero.offsetTop-80)+'px';dust.style.height=(hero.offsetHeight+120)+'px';};
  place();new ResizeObserver(place).observe(hero);
}

/* Hero: tooth follows the pointer (or device tilt) */
const tooth=$('.hero-arch .tooth-3d');
if(tooth){
  let tx=0,ty=0,cx=0,cy=0,raf=0;
  const loop=()=>{cx+=(tx-cx)*.06;cy+=(ty-cy)*.06;tooth.style.setProperty('--tx',cx.toFixed(2)+'deg');tooth.style.setProperty('--ty',cy.toFixed(2)+'deg');
    raf=Math.abs(tx-cx)+Math.abs(ty-cy)>.02?requestAnimationFrame(loop):0;};
  const aim=(x,y)=>{tx=-y*14;ty=x*18;if(!raf)raf=requestAnimationFrame(loop);};
  if(fine)addEventListener('pointermove',e=>aim(e.clientX/innerWidth-.5,e.clientY/innerHeight-.5),{passive:true});
  else addEventListener('deviceorientation',e=>{if(e.gamma==null)return;aim(Math.max(-1,Math.min(1,e.gamma/35))*.5,Math.max(-1,Math.min(1,(e.beta-45)/35))*.5);},{passive:true});
}

/* Reveal on scroll: earlier trigger plus a stagger, across every scene */
const revealSel=['.scene h2','.s-label','.dental-card','.t-card','.uni-card','.lab-card','.lab-cta','.eg-step','.art-row','.resume-panel','.credentials-gallery figure','.bk-philo','.c-item','.consult-form','.latest-home','.digital-home-banner','.stat'].join(',');
const own='.wcard,.worlds-head,.hub-contact';
const io=new IntersectionObserver(list=>list.forEach(e=>{if(e.isIntersecting){e.target.classList.add('fx-in','in');io.unobserve(e.target);}}),{rootMargin:'0px 0px 12% 0px',threshold:0});
const prime=scope=>{
  $$(revealSel,scope).forEach(el=>{
    if(el.closest('.hero,#menuOverlay,.wcard')||el.classList.contains('fx-r'))return;
    const r=el.getBoundingClientRect();if(r.height&&r.top<innerHeight)return; // already on screen: leave as is
    el.classList.add('fx-r');io.observe(el);
  });
  $$(own,scope).forEach(el=>{if(!el.classList.contains('in'))io.observe(el);});
  const groups=new Map();
  $$('.fx-r,.wcard',scope).forEach(el=>{const p=el.parentElement;const k=groups.get(p)||0;groups.set(p,k+1);el.style.setProperty('--d',Math.min(k,6)*0.08+'s');});
};
prime(document);

/* World cards: 3D tilt and a light that follows the pointer */
if(fine)$$('.wcard').forEach(card=>{
  card.addEventListener('pointermove',e=>{
    const r=card.getBoundingClientRect(),x=(e.clientX-r.left)/r.width,y=(e.clientY-r.top)/r.height;
    card.classList.add('fx-tilting');
    card.style.setProperty('--mx',x*100+'%');card.style.setProperty('--my',y*100+'%');
    card.style.setProperty('--ry',((x-.5)*9).toFixed(2)+'deg');card.style.setProperty('--rx',((.5-y)*7).toFixed(2)+'deg');
  });
  card.addEventListener('pointerleave',()=>{card.classList.remove('fx-tilting');card.style.setProperty('--rx','0deg');card.style.setProperty('--ry','0deg');});
});

/* Scene changes: gold sweep, then re-prime reveals in the new scene */
const sweep=document.createElement('div');sweep.className='fx-sweep';sweep.setAttribute('aria-hidden','true');document.body.append(sweep);
let first=true;
const mo=new MutationObserver(muts=>{
  for(const m of muts){
    const s=m.target;
    if(s.classList.contains('active')&&!(m.oldValue||'').includes('active')){
      if(!first){sweep.classList.remove('go');void sweep.offsetWidth;sweep.classList.add('go');}
      requestAnimationFrame(()=>{prime(s);scroller=s.scrollHeight>s.clientHeight+1?s:(document.scrollingElement||root);updateBar();});
    }
  }
  first=false;
});
$$('.scene').forEach(s=>mo.observe(s,{attributes:true,attributeFilter:['class'],attributeOldValue:true}));
setTimeout(()=>{first=false;},800);

/* Magnetic small buttons */
if(fine)$$('#menuBtn,.lang-switch a,#faSiteLink,#trSiteLink').forEach(b=>{
  b.dataset.magnetic='';
  b.addEventListener('pointermove',e=>{const r=b.getBoundingClientRect();b.style.transform=`translate(${(e.clientX-r.left-r.width/2)*.25}px,${(e.clientY-r.top-r.height/2)*.25}px)`;});
  b.addEventListener('pointerleave',()=>{b.style.transform='';});
});

/* Custom cursor */
if(fine){
  const dot=document.createElement('div'),ring=document.createElement('div');
  dot.className='fx-cursor dot';ring.className='fx-cursor ring';dot.setAttribute('aria-hidden','true');ring.setAttribute('aria-hidden','true');
  document.body.append(dot,ring);root.classList.add('fx-cursor-hide');
  let x=-100,y=-100,rx=x,ry=y,on=false;
  const hotSel='a,button,[data-goto],label,summary,.wcard,input[type=submit]';
  addEventListener('pointermove',e=>{
    if(e.pointerType!=='mouse')return;
    x=e.clientX;y=e.clientY;dot.style.transform=`translate(${x}px,${y}px)`;
    if(!on){on=true;rx=x;ry=y;root.classList.add('fx-cursor-on');}
    ring.classList.toggle('hot',!!e.target.closest?.(hotSel));
  },{passive:true});
  addEventListener('pointerdown',()=>ring.classList.add('down'));
  addEventListener('pointerup',()=>ring.classList.remove('down'));
  document.addEventListener('pointerleave',()=>{on=false;root.classList.remove('fx-cursor-on');});
  const follow=()=>{rx+=(x-rx)*.18;ry+=(y-ry)*.18;ring.style.transform=`translate(${rx}px,${ry}px)`;requestAnimationFrame(follow);};
  follow();
}
})();
