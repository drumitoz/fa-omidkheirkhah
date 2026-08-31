// Source-level navigation tests using lightweight browser API doubles.
// This is not a rendered-browser or visual test.
import fs from 'node:fs';
import vm from 'node:vm';
import assert from 'node:assert/strict';
const html=fs.readFileSync(new URL('../index.html',import.meta.url),'utf8');
const script=[...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m=>m[1]).join('\n');
function node(classes=[],cat){
  const values=new Set(classes);
  return {classList:{add:x=>values.add(x),remove:x=>values.delete(x),contains:x=>values.has(x)},style:{},dataset:{cat},appendChild(){},addEventListener(){},textContent:''};
}
function setup(hash){
  const ids={};
  for(const id of ['hub','kesifet','universiteler','benkimim','iletisim','dental','civil','lab','writing'])ids[id]=node(id==='hub'?['scene','active']:['scene']);
  for(const id of ['particles','menuOverlay','menuBtn','menuClose','articlesTitle','articlesLead'])ids[id]=node();
  const filters=['all','dental','civil'].map(c=>node(c==='all'?['active']:[],c));
  const rows=[...Array.from({length:39},()=>node([],'dental')),...Array.from({length:5},()=>node([],'civil'))];
  const document={getElementById:id=>ids[id]||null,createElement:()=>node(),querySelectorAll:s=>s==='.art-filter'?filters:s==='.art-row'?rows:[],querySelector:s=>filters.find(n=>s.includes('"'+n.dataset.cat+'"'))||null};
  const history={pushState(a,b,url){this.url=url},replaceState(a,b,url){this.url=url}};
  const ctx=vm.createContext({document,history,location:{hash},window:{scrollTo(){},matchMedia:()=>({matches:false})},setTimeout:f=>f(),IntersectionObserver:class{observe(){} disconnect(){}}});
  vm.runInContext(script,ctx);
  return {ctx,ids,rows,filters,history};
}
for(const hash of ['', '#civil','#dental','#kesifet','#kesifet-all','#kesifet-dental','#kesifet-civil','#trading','#kesifet-trade','#bad']){
  const t=setup(hash);
  const expected=hash==='#civil'?'civil':hash==='#dental'?'dental':/^#kesifet(?:-(all|dental|civil))?$/.test(hash)?'kesifet':'hub';
  assert(t.ids[expected].classList.contains('active'),hash);
  assert.equal(Object.values(t.ids).filter(n=>n.classList.contains('scene')&&n.classList.contains('active')).length,1);
  if(hash==='#kesifet-civil')assert.equal(t.rows.filter(r=>r.style.display!=='none').length,5);
  if(hash==='#kesifet-dental')assert.equal(t.rows.filter(r=>r.style.display!=='none').length,39);
}
const t=setup('');
vm.runInContext("navigate('civil'); navigate('kesifet',{cat:'civil'});",t.ctx);
assert.equal(t.rows.filter(r=>r.style.display!=='none').length,5);
vm.runInContext("filterArt('dental');",t.ctx);
assert.equal(t.rows.filter(r=>r.style.display!=='none').length,39);
assert.equal(t.history.url,'#kesifet-dental');
vm.runInContext("filterArt('all');",t.ctx);
assert.equal(t.rows.filter(r=>r.style.display!=='none').length,44);
vm.runInContext("applyArticleCategory('trade'); navigate('trading');",t.ctx);
assert.equal(t.rows.filter(r=>r.style.display!=='none').length,44);
assert(t.ids.hub.classList.contains('active'));
console.log('PASS: 10 deep links, civil/dental/all filters, scene switching, invalid routes and retired categories.');
