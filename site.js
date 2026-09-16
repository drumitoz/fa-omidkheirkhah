'use strict';
const $=s=>document.querySelector(s), $$=s=>[...document.querySelectorAll(s)];
const overlay=$('#menuOverlay'), menuButton=$('#menuBtn');
let currentScene='hub', category='all', initialized=false;
function closeMenu(restore=true){
  overlay.classList.remove('open');overlay.hidden=true;overlay.inert=true;
  $('#main-content').inert=false;$('.site-nav').inert=false;
  document.body.classList.remove('menu-open');menuButton.setAttribute('aria-expanded','false');
  if(restore)menuButton.focus();
}
function openMenu(){
  overlay.hidden=false;overlay.inert=false;overlay.classList.add('open');
  $('#main-content').inert=true;$('.site-nav').inert=true;
  document.body.classList.add('menu-open');menuButton.setAttribute('aria-expanded','true');$('#menuClose').focus();
}
menuButton.addEventListener('click',openMenu);$('#menuClose').addEventListener('click',()=>closeMenu());
overlay.addEventListener('keydown',e=>{
  if(e.key==='Escape'){e.preventDefault();closeMenu();}
  if(e.key==='Tab'){
    const items=[...overlay.querySelectorAll('a[href],button:not([disabled])')];
    const first=items[0],last=items.at(-1);
    if(e.shiftKey&&document.activeElement===first){e.preventDefault();last.focus();}
    else if(!e.shiftKey&&document.activeElement===last){e.preventDefault();first.focus();}
  }
});
function normalizeText(s){return s.normalize('NFKC').replace(/ي/g,'ی').replace(/ك/g,'ک').replace(/[\u064B-\u065F\u0670\u0640]/g,'').replace(/[\u200c\s]+/g,' ').trim().toLocaleLowerCase('fa');}
function applyArticleCategory(cat='all'){
  category=['all','dental','civil'].includes(cat)?cat:'all';
  $$('.art-filter').forEach(f=>{let on=f.dataset.cat===category;f.classList.toggle('active',on);f.setAttribute('aria-pressed',String(on));});
  const words=normalizeText($('#articleSearch').value).split(' ').filter(Boolean);let count=0;
  $$('.art-row').forEach(row=>{const text=normalizeText(row.textContent+' '+(row.dataset.keywords||''));const shown=(category==='all'||row.dataset.cat===category)&&words.every(w=>text.includes(w));row.hidden=!shown;if(shown)count++;});
  $('#articleCount').textContent=count.toLocaleString('fa-IR')+' مقاله'+(words.length?' مطابق جست‌وجوی شما':' برای مطالعه');
  $('#noArticles').hidden=count!==0;$('#clearSearch').hidden=!$('#articleSearch').value;
  $('#articlesTitle').textContent={all:'برای فهم عمیق‌تر، بخوانید.',dental:'مقالات سلامت دهان',civil:'پژوهش‌های مهندسی عمران'}[category];
}
function readRoute(){
  const [path,query='']=location.hash.slice(1).split('?');const match=path.match(/^kesifet(?:-(all|dental|civil))?$/);
  const id=match?'kesifet':path;const target=document.getElementById(id);
  return {id:target?.classList.contains('scene')?id:'hub',cat:match?.[1]||'all',q:new URLSearchParams(query).get('q')||''};
}
function setScene(id,{cat='all',q='',focus=false}={}){
  if(!document.getElementById(id)?.classList.contains('scene'))id='hub';
  currentScene=id;$$('.scene').forEach(s=>s.classList.toggle('active',s.id===id));closeMenu(false);
  if(id==='kesifet'){$('#articleSearch').value=q;applyArticleCategory(cat);}
  $$('.desktop-nav a').forEach(a=>{if(a.dataset.goto===id)a.setAttribute('aria-current','page');else a.removeAttribute('aria-current');});
  document.title=({hub:'دکتر امید خیرخواه — دندان‌پزشک · نوآور · نویسنده',kesifet:'مقالات علمی | دکتر امید خیرخواه',universiteler:'تحصیل در قبرس شمالی | دکتر امید خیرخواه',iletisim:'تماس | دکتر امید خیرخواه',credentials:'سوابق و مدارک | دکتر امید خیرخواه',benkimim:'درباره من | دکتر امید خیرخواه',civil:'مهندسی عمران | دکتر امید خیرخواه',dental:'سلامت دهان | دکتر امید خیرخواه',lab:'نوآوری | دکتر امید خیرخواه',writing:'نوشته‌ها | دکتر امید خیرخواه'})[id];
  if(id==='hub')initHub();
  window.scrollTo({top:0,behavior:'instant'});
  if(focus){const heading=document.querySelector('#'+id+' h1, #'+id+' h2');if(heading){heading.tabIndex=-1;heading.focus({preventScroll:true});}}
}
function routeURL(cat,q){return '#kesifet-'+cat+(q?'?q='+encodeURIComponent(q):'');}
function navigate(id,opts={}){
  const hash=id==='kesifet'?routeURL(opts.cat||'all',opts.q||''):'#'+id;
  if(location.hash!==hash)history.pushState(null,'',hash);
  setScene(id,{...opts,focus:true});
}
document.addEventListener('click',e=>{
  const a=e.target.closest('a[data-goto]');if(!a||e.ctrlKey||e.metaKey||e.shiftKey||e.altKey||e.button!==0)return;
  e.preventDefault();navigate(a.dataset.goto,{cat:a.dataset.cat||'all'});
});
window.addEventListener('popstate',()=>{const r=readRoute();setScene(r.id,r);});
window.addEventListener('hashchange',()=>{const r=readRoute();setScene(r.id,r);});
function filterArt(cat){applyArticleCategory(cat);history.replaceState(null,'',routeURL(category,$('#articleSearch').value.trim()));}
$$('.art-filter').forEach(f=>f.addEventListener('click',()=>filterArt(f.dataset.cat)));
$('#articleSearch').addEventListener('input',()=>filterArt(category));
$('#clearSearch').addEventListener('click',()=>{$('#articleSearch').value='';filterArt(category);$('#articleSearch').focus();});
function initHub(){
  $('#hub').classList.add('hub-ready');if(initialized)return;initialized=true;
  const entries=$$('#hub .worlds-head,#hub .wcard,#hub .hub-contact');
  if(!('IntersectionObserver' in window)||matchMedia('(prefers-reduced-motion: reduce)').matches){entries.forEach(e=>e.classList.add('in'));return;}
  const io=new IntersectionObserver(list=>list.forEach(e=>{if(e.isIntersecting){e.target.classList.add('in');io.unobserve(e.target);}}),{threshold:.05});entries.forEach(e=>io.observe(e));
}
const WHATSAPP_NUMBER='905338481611';
function formValue(form,name){return(form.elements[name]?.value||'').trim();}
function formSelectedText(form,name){const f=form.elements[name];return f?.value?f.selectedOptions[0].textContent.trim():'مشخص نشده';}
function buildWhatsAppURL(form){
  const university=form.id==='faUniversityForm';
  const lines=['سلام آقای دکتر خیرخواه،',university?'از سایت فارسی برای راهنمایی تحصیل پیام می‌دهم.':'از سایت فارسی پیام می‌دهم.','',`نام: ${formValue(form,'name')}`];
  const email=formValue(form,'email');if(email)lines.push(`ایمیل: ${email}`);
  if(university){const phone=formValue(form,'phone');if(phone)lines.push(`شمارهٔ واتساپ: ${phone}`);lines.push(`دانشگاه: ${formSelectedText(form,'university')}`,`رشته: ${formSelectedText(form,'field')}`);}
  else lines.push(`موضوع: ${formSelectedText(form,'subject')}`);
  lines.push(`پیام: ${formValue(form,'message')||'درخواست راهنمایی اولیه'}`);
  return `https://wa.me/${WHATSAPP_NUMBER}?text=${encodeURIComponent(lines.join('\n'))}`;
}
$$('form').forEach(form=>form.addEventListener('submit',e=>{
  e.preventDefault();for(const el of form.querySelectorAll('[required]'))el.setCustomValidity(el.value.trim()?'':'لطفاً این بخش را تکمیل کنید.');
  if(!form.reportValidity())return;
  const url=buildWhatsAppURL(form),status=form.querySelector('.form-status');status.replaceChildren(document.createTextNode('متن آماده است؛ ارسال نهایی در واتساپ انجام می‌شود. '));
  const fallback=document.createElement('a');fallback.href=url;fallback.textContent='اگر واتساپ باز نشد، اینجا بزنید.';status.append(fallback);
  window.location.assign(url);
}));
$$('input,textarea').forEach(el=>el.addEventListener('input',()=>el.setCustomValidity('')));
const initial=readRoute();setScene(initial.id,initial);
