// Behavioral checks with browser API doubles. Rendered layout is checked separately.
import fs from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';
const script=fs.readFileSync(new URL('../site.js',import.meta.url),'utf8');
function node(classes=[],cat,text=''){
 const values=new Set(classes),attrs={},events={};
 return {classList:{add:x=>values.add(x),remove:x=>values.delete(x),contains:x=>values.has(x),toggle(x,on){if(on)values.add(x);else values.delete(x);}},dataset:{cat},textContent:text,value:'',hidden:false,inert:false,attrs,events,setAttribute(k,v){attrs[k]=v;},removeAttribute(k){delete attrs[k];},addEventListener(k,fn){events[k]=fn;},focus(){this.focused=true;},querySelectorAll(){return[];}};
}
function setup(hash=''){
 const ids={},handlers={},sceneNames=['hub','kesifet','universiteler','benkimim','iletisim','dental','civil','lab','writing','credentials'];
 for(const id of sceneNames){ids[id]=node(['scene']);ids[id].id=id;}
 for(const id of ['menuOverlay','menuBtn','menuClose','main-content','articleSearch','clearSearch','articleCount','noArticles','articlesTitle'])ids[id]=node();
 const nav=node(),body=node(),filters=['all','dental','civil'].map(c=>node([],c));
 const rows=[...Array.from({length:39},(_,i)=>node([],'dental',i===0?'خونریزی لثه':'سلامت دندان')),...Array.from({length:5},()=>node([],'civil','بتن کم‌کربن'))];
 const document={body,activeElement:null,getElementById:id=>ids[id]||null,querySelector:s=>s[0]==='#'?ids[s.slice(1)]||null:s==='.site-nav'?nav:null,querySelectorAll:s=>s==='.art-filter'?filters:s==='.art-row'?rows:s==='.scene'?sceneNames.map(n=>ids[n]):[],addEventListener(){}};
 const location={hash},history={pushState(a,b,url){location.hash=url;},replaceState(a,b,url){location.hash=url;}};
 const window={scrollTo(){},addEventListener(k,fn){handlers[k]=fn;}};
 const ctx=vm.createContext({document,location,history,window,URLSearchParams,encodeURIComponent,matchMedia:()=>({matches:true})});
 vm.runInContext(script,ctx);
 return{ctx,ids,rows,filters,location,handlers,nav};
}
for(const hash of ['', '#credentials', '#civil','#dental','#kesifet','#kesifet-all','#kesifet-dental','#kesifet-civil','#trading','#kesifet-trade','#bad']){
 const t=setup(hash),expected=hash==='#credentials'?'credentials':hash==='#civil'?'civil':hash==='#dental'?'dental':/^#kesifet(?:-(all|dental|civil))?$/.test(hash)?'kesifet':'hub';
 assert(t.ids[expected].classList.contains('active'),hash);
 assert.equal(Object.values(t.ids).filter(n=>n.classList.contains('scene')&&n.classList.contains('active')).length,1);
 if(hash==='#kesifet-civil')assert.equal(t.rows.filter(r=>!r.hidden).length,5);
 if(hash==='#kesifet-dental')assert.equal(t.rows.filter(r=>!r.hidden).length,39);
}
const t=setup();
vm.runInContext("navigate('kesifet',{cat:'civil'});",t.ctx);assert.equal(t.location.hash,'#kesifet-civil');
t.ids.articleSearch.value='بتن كم كربن';vm.runInContext("filterArt('civil')",t.ctx);assert.equal(t.rows.filter(r=>!r.hidden).length,5);
t.ids.articleSearch.value='خونريزي';vm.runInContext("filterArt('dental')",t.ctx);assert.equal(t.rows.filter(r=>!r.hidden).length,1);
t.ids.articleSearch.value='موضوع ناموجود';vm.runInContext("filterArt('all')",t.ctx);assert.equal(t.rows.filter(r=>!r.hidden).length,0);assert.equal(t.ids.noArticles.hidden,false);
t.location.hash='#kesifet-civil';t.handlers.popstate();assert.equal(t.rows.filter(r=>!r.hidden).length,5);assert.equal(t.ids.articleSearch.value,'');
t.location.hash='#iletisim';t.handlers.popstate();assert(t.ids.iletisim.classList.contains('active'));
vm.runInContext('openMenu()',t.ctx);assert.equal(t.ids.menuOverlay.hidden,false);assert.equal(t.ids['main-content'].inert,true);assert.equal(t.ids.menuBtn.attrs['aria-expanded'],'true');
t.ids.menuOverlay.events.keydown({key:'Escape',preventDefault(){}});assert.equal(t.ids.menuOverlay.hidden,true);assert.equal(t.ids['main-content'].inert,false);assert.equal(t.ids.menuBtn.focused,true);
const form={id:'faContactForm',elements:{name:{value:' آزمایش & + '},email:{value:''},subject:{value:'همکاری',selectedOptions:[{textContent:'همکاری و نوآوری'}]},message:{value:'خط اول\nخط دوم؟ & +'}}};
t.ctx.testForm=form;let url=new URL(vm.runInContext('buildWhatsAppURL(testForm)',t.ctx));assert.equal(url.origin,'https://wa.me');assert.equal(url.pathname,'/905338481611');let message=url.searchParams.get('text');assert(message.includes('نام: آزمایش & +'));assert(message.includes('خط اول\nخط دوم؟ & +'));assert(!message.includes('ایمیل:'));
form.id='faUniversityForm';form.elements.email.value='test@example.invalid';form.elements.university={value:'EMU',selectedOptions:[{textContent:'EMU - دانشگاه مدیترانه شرقی'}]};form.elements.field={value:''};url=new URL(vm.runInContext('buildWhatsAppURL(testForm)',t.ctx));message=url.searchParams.get('text');assert(message.includes('دانشگاه: EMU'));assert(message.includes('رشته: مشخص نشده'));assert(message.includes('ایمیل: test@example.invalid'));
console.log('PASS: deep links, retired routes, filters, Persian/Arabic search normalization, empty state, browser Back, menu/Escape/focus, and encoded WhatsApp drafts for both forms. No messages sent.');
