'use strict';
const copyButton=document.getElementById('copyArticle'), shareStatus=document.getElementById('shareStatus');
copyButton.addEventListener('click',async()=>{
 const url=document.querySelector('link[rel="canonical"]').href;
 try{await navigator.clipboard.writeText(url);shareStatus.textContent='پیوند مقاله کپی شد.';}
 catch{shareStatus.replaceChildren(document.createTextNode('پیوند برای انتخاب و کپی: '));const link=document.createElement('a');link.href=url;link.textContent=url;link.dir='ltr';shareStatus.append(link);}
});
document.getElementById('printArticle').addEventListener('click',()=>window.print());
const progress=document.getElementById('readingProgress'), article=document.getElementById('article-content');
let scheduled=false;
function updateProgress(){const bounds=article.getBoundingClientRect();const total=Math.max(1,article.offsetHeight-innerHeight+120);progress.style.width=Math.max(0,Math.min(100,(120-bounds.top)/total*100))+'%';scheduled=false;}
addEventListener('scroll',()=>{if(!scheduled){scheduled=true;requestAnimationFrame(updateProgress);}},{passive:true});addEventListener('resize',updateProgress);updateProgress();
