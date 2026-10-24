const fs=require('fs'),vm=require('vm');
const source=fs.readFileSync(__dirname+'/../week10/week10.js','utf8');
const qmd=fs.readFileSync(__dirname+'/../week10/week10.qmd','utf8');
const dom={};
function register(id,value=''){
  dom[id]={id,value,innerHTML:'',textContent:'',handlers:{},
    addEventListener:function(type,cb){this.handlers[type]=cb;},
    setPointerCapture:function(){}, getScreenCTM:function(){return {inverse(){return {}}}},
    getAttribute:function(k){return this[k]}};
}
for(const m of qmd.matchAll(/\bid="([^"]+)"/g))register(m[1]);
for(const m of qmd.matchAll(/<input[^>]+>/g)){
 const id=m[0].match(/id="([^"]+)"/)?.[1],v=m[0].match(/value="([^"]+)"/)?.[1];if(id)dom[id].value=v||'';
}
for(const m of qmd.matchAll(/<select[^>]*id="([^"]+)"[^>]*>([\s\S]*?)<\/select>/g)){
 const choices=[...m[2].matchAll(/<option[^>]*value="([^"]+)"([^>]*)>/g)];
 const defaultOpt=choices.find(x=>x[2].includes('selected'))||choices[0];
 if(defaultOpt)dom[m[1]].value=defaultOpt[1];
}
const document={readyState:'complete',getElementById(id){return dom[id]||null;},querySelectorAll(sel){return [];}};
const context={document,window:{addEventListener(){}},Math,Number,Array,String,Set,console,DOMPoint:function(x,y){this.x=x;this.y=y;this.matrixTransform=()=>({x,y});}};
vm.runInNewContext(source,context,{timeout:10000});
function fire(id,type='input'){const e=dom[id]; if(e?.handlers[type])e.handlers[type]({pointerId:1,clientX:100,clientY:100});}
function check(){for(const id of ['rocSvg','powerSvg','randomSvg']){
 const text=dom[id].innerHTML; if(!text||text.includes('NaN')||text.includes('undefined'))throw new Error('bad SVG '+id+' '+text.slice(0,300));
 }}
check();
console.log('INIT confusion',dom.cmSensBig.textContent,dom.cmSpecBig.textContent,dom.cmPpvBig.textContent,dom.cmNpvBig.textContent,'grid=',(dom.cmMetrics.innerHTML.match(/class="w10-metric /g)||[]).length);
console.log('INIT ROC',dom.rocAuc.textContent,'sensor',dom.rocSen.textContent,'special n',dom.rocBest.textContent);
const original=dom.rocAuc.textContent;
for(const value of ['0','110']){dom.rocCut.value=value;fire('rocCut');check();console.log('ROC ferritin cutoff',value,'Se=',dom.rocSen.textContent,'Sp=',dom.rocSpe.textContent,'AUC=',dom.rocAuc.textContent);if(dom.rocAuc.textContent!==original)throw new Error('AUC changed with cutoff');}
dom.rocMarker.value='folate';fire('rocMarker','change');check();console.log('ROC folate AUC',dom.rocAuc.textContent);
console.log('POWER default',dom.powN.textContent,dom.powTotal.textContent,dom.powAttained.textContent);
for(const [effect,sd,alpha,target] of [[.1,100,.01,.95],[5,12,.05,.8],[15,5,.10,.8]]){
 dom.powEffect.value=effect;dom.powSd.value=sd;dom.powAlpha.value=alpha;dom.powTarget.value=target;fire('powEffect');check();
 console.log('POWER',effect,sd,alpha,target,'n',dom.powN.textContent,'attained',dom.powAttained.textContent);
}
for(const [tp,fn,fp,tn] of [[0,0,0,0],[0,0,25,0],[30,10,5,60]]){
 for(const [id,val] of Object.entries({cmTP:tp,cmFN:fn,cmFP:fp,cmTN:tn}))dom[id].value=String(val);
 fire('cmTP');console.log('MATRIX',tp,fn,fp,tn,dom.cmSensBig.textContent,dom.cmSpecBig.textContent,dom.cmPpvBig.textContent,dom.cmNpvBig.textContent);
 if(dom.cmMetrics.innerHTML.includes('NaN')||dom.cmMetrics.innerHTML.includes('undefined'))throw new Error('Diagnostic invalid denominator');
}
fire('ranTen','click');fire('ranTen','click');check();console.log('RAND',dom.ranCounts.textContent,dom.ranProbability.textContent,dom.ranTotal.textContent);
