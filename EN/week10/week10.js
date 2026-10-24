/* Week 10: one scoped script, initialized once. The QMD embeds this verbatim. */
(function(){
'use strict';
const $=id=>document.getElementById(id);
const clamp=(x,a,b)=>Math.max(a,Math.min(b,x));
const N=(id,fallback)=>{const el=$(id);const v=el?Number(el.value):fallback;return Number.isFinite(v)?v:fallback;};
const out=(id,v)=>{const el=$(id);if(el)el.textContent=String(v);};
const svgLine=(x1,y1,x2,y2,cls='w10-axis')=>`<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" class="${cls}"></line>`;
const svgPath=(pts,cls)=>`<path class="${cls}" d="${pts.map((p,i)=>`${i?'L':'M'}${p[0].toFixed(2)},${p[1].toFixed(2)}`).join(' ')}"></path>`;
const txt=(x,y,string,cls='w10-tick',anchor='middle')=>`<text x="${x}" y="${y}" text-anchor="${anchor}" class="${cls}">${string}</text>`;
const pct=p=>Number.isFinite(p)?(100*p).toFixed(1)+'%':'—';
const fixed=(x,d=2)=>Number.isNaN(x)?'—':x===Infinity?'∞':x===-Infinity?'−∞':Number.isFinite(x)?x.toFixed(d):'—';
const safe=(a,b)=>b===0?NaN:a/b;
const axes=(L,R,T,B,xlabels,ylabels)=>{
 let s=svgLine(L,B,R,B)+svgLine(L,T,L,B);
 for(const [v,x] of xlabels)s+=svgLine(x,B,x,B+6)+txt(x,B+26,v);
 for(const [v,y] of ylabels)s+=svgLine(L,y,R,y,'w10-gridline')+txt(L-10,y+5,v,'w10-tick','end');
 return s;
};

/* --------------------------------------------------------
   Diagnostic 5 × 6 display
   -------------------------------------------------------- */
function renderConfusion(){
 const tp=Math.max(0,Math.floor(N('cmTP',0))),fn=Math.max(0,Math.floor(N('cmFN',0)));
 const fp=Math.max(0,Math.floor(N('cmFP',0))),tn=Math.max(0,Math.floor(N('cmTN',0)));
 const sick=tp+fn,healthy=tn+fp,pos=tp+fp,neg=tn+fn,total=sick+healthy;
 const sen=safe(tp,sick),spec=safe(tn,healthy),ppv=safe(tp,pos),npv=safe(tn,neg);
 const fpr=safe(fp,healthy),fnr=safe(fn,sick),fdr=safe(fp,pos),forate=safe(fn,neg);
 const acc=safe(tp+tn,total),bacc=(sen+spec)/2;
 const f1=safe(2*tp,2*tp+fp+fn),fowl= Math.sqrt(ppv*sen);
 const inf=sen+spec-1,marked=ppv+npv-1;
 const mcc=safe(tp*tn-fp*fn,Math.sqrt(pos*sick*healthy*neg));
 const lrp=safe(sen,fpr),lrm=safe(fnr,spec),dor=safe(lrp,lrm);
 const prevTh=safe(Math.sqrt(fpr),Math.sqrt(sen)+Math.sqrt(fpr));
 const jacc=safe(tp,tp+fp+fn);
 out('cmSensBig',pct(sen));out('cmSpecBig',pct(spec));out('cmPpvBig',pct(ppv));out('cmNpvBig',pct(npv));
 // Exactly 5 columns × 6 rows, ordered like the course outline.
 const specs=[
  [['Total',total,'n'],['Healthy',healthy,'n'],['Sick',sick,'n'],['Prevalence',safe(sick,total),'pct'],['Accuracy',acc,'pct'],['Balanced accuracy',bacc,'pct']],
  [['Positive',pos,'n'],['TP',tp,'n'],['FP',fp,'n'],['PPV',ppv,'pct'],['FDR',fdr,'pct'],['F1',f1,'decimal']],
  [['Negative',neg,'n'],['FN',fn,'n'],['TN',tn,'n'],['FOR',forate,'pct'],['NPV',npv,'pct'],['Fowlkes–Mallows',fowl,'decimal']],
  [['Informedness',inf,'decimal'],['Sensitivity',sen,'pct'],['FPR / fall-out',fpr,'pct'],['LR+',lrp,'decimal'],['Markedness',marked,'decimal'],['Matthews (MCC)',mcc,'decimal']],
  [['Prev. threshold',prevTh,'pct'],['FNR / miss rate',fnr,'pct'],['Specificity',spec,'pct'],['LR−',lrm,'decimal'],['Diagnostic OR',dor,'decimal'],['Jaccard / threat',jacc,'decimal']]
 ];
 const fmt=(v,type)=>type==='n'?String(v):type==='pct'?pct(v):fixed(v,2);
 const main=new Set(['Sensitivity','Specificity','PPV','NPV','Balanced accuracy','Accuracy']);
 const el=$('cmMetrics');
 if(el)el.innerHTML=specs.map(column=>'<div class="w10-metric-col">'+column.map(([name,value,type])=>
  `<div class="w10-metric ${main.has(name)?'primary':''}"><strong>${name}</strong><span>${fmt(value,type)}</span></div>`).join('')+'</div>').join('');
}

/* --------------------------------------------------------
   Diagnostic biomarker + receiver operating characteristic.
   LOW biomarker value is defined as test-positive in BOTH
   synthetic datasets. Sample and ROC remain fixed as slider moves.
   -------------------------------------------------------- */
const markerCache={};
function makeRng(seed){let state=seed>>>0;return ()=>{state^=state<<13;state^=state>>>17;state^=state<<5;return ((state>>>0)+.5)/4294967296;};}
function normalDraw(rand){return Math.sqrt(-2*Math.log(Math.max(1e-12,rand())))*Math.cos(2*Math.PI*rand());}
function genMarker(which){
 const rand=makeRng(which==='ferritin'?640091:94741);
 const max=which==='ferritin'?110:22, healthy=[],sick=[];
 for(let i=0;i<72;i++){
  const mh=which==='ferritin'?62:11.1,sh=which==='ferritin'?19:3.2;
  const ms=which==='ferritin'?24:9.9,ss=which==='ferritin'?14:3.6;
  healthy.push(clamp(mh+normalDraw(rand)*sh,.5,max-.5));
  sick.push(clamp(ms+normalDraw(rand)*ss,.5,max-.5));
 }
 return {max,healthy,sick,unit:which==='ferritin'?'ng/mL':'ng/mL'};
}
function markerRates(data,cut){
 const tp=data.sick.filter(v=>v<=cut).length,fn=data.sick.length-tp;
 const fp=data.healthy.filter(v=>v<=cut).length,tn=data.healthy.length-fp;
 return {tp,fn,fp,tn,tpr:tp/data.sick.length,fpr:fp/data.healthy.length};
}
function markerCurve(data){
 const sorted=[...data.healthy,...data.sick].sort((a,b)=>a-b);
 const cuts=[-1,...sorted, data.max+1];
 const seen=new Set(),points=[];let bestCut=0,bestJ=-Infinity;
 for(const c of cuts){if(seen.has(c))continue;seen.add(c);
  const r=markerRates(data,c);points.push({x:r.fpr,y:r.tpr,cut:c});
  const J=r.tpr-r.fpr;if(J>bestJ){bestJ=J;bestCut=c;}
 }
 points.sort((a,b)=>a.x-b.x || a.y-b.y);
 // AUC: U statistic, disease values are positive on the low end.
 let wins=0;
 for(const s of data.sick)for(const h of data.healthy)wins+=s<h?1:s===h?.5:0;
 const auc=wins/(data.sick.length*data.healthy.length);
 return {points,auc,bestCut};
}
function changeMarker(){
 const which=$('rocMarker').value;
 const data=markerCache[which]||(markerCache[which]=genMarker(which));
 const slider=$('rocCut');slider.max=String(data.max);slider.min='0';slider.step=which==='ferritin'?'1':'.2';slider.value=which==='ferritin'?'30':'10';
 renderRoc();
}
function renderRoc(){
 const which=$('rocMarker')?.value||'ferritin',data=markerCache[which]||(markerCache[which]=genMarker(which));
 const cut=N('rocCut',30),scores=markerCurve(data),current=markerRates(data,cut);
 out('rocCutVal',cut.toFixed(which==='ferritin'?0:1)+' '+data.unit);
 out('rocSen',pct(current.tpr));out('rocSpe',pct(1-current.fpr));out('rocAuc',scores.auc.toFixed(3));out('rocBest',scores.bestCut.toFixed(1)+' '+data.unit);
 const svg=$('rocSvg');if(!svg)return;
 const L=66,R=495,T=78,B=372,L2=610,R2=845,T2=91,B2=333;
 const mx=x=>L+x/data.max*(R-L),rX=x=>L2+x*(R2-L2),rY=y=>B2-y*(B2-T2);
 let h=`<defs><clipPath id="w10RocClip"><rect x="${L}" y="${T}" width="${R-L}" height="${B-T}"></rect></clipPath></defs>`;
 h+=`<rect x="${L}" y="${T}" width="${mx(cut)-L}" height="${B-T}" class="w10-hist-selected"></rect>`;
 h+=txt(L,34,'Biomarker values by reference group','w10-svg-title','start')+txt(L2,34,'Receiver operating characteristic','w10-svg-title','start');
 h+=svgLine(L,B,R,B)+svgLine(L,T,L,B)+svgLine(L2,B2,R2,B2)+svgLine(L2,T2,L2,B2);
 for(const f of [0,.25,.5,.75,1]){
   const x=rX(f),y=rY(f);
   h+=svgLine(x,B2,x,B2+6)+txt(x,B2+25,f.toFixed(2));
   h+=svgLine(L2,y,R2,y,'w10-gridline')+txt(L2-8,y+5,f.toFixed(2),'w10-tick','end');
 }
 for(let i=0;i<=5;i++){const v=i/5*data.max;h+=svgLine(mx(v),B,mx(v),B+6)+txt(mx(v),B+25,v.toFixed(which==='ferritin'?0:1));}
 h+=txt((L+R)/2,B+57,which==='ferritin'?'Ferritin (ng/mL)':'Folate (ng/mL)','w10-svg-label');
 h+=txt((L2+R2)/2,B2+58,'False-positive rate (1 − specificity)','w10-svg-label');
 h+=txt(L2-36,(T2+B2)/2,'TPR','w10-svg-label');
 h+=txt(L+6,116,'Healthy · blue','w10-svg-label','start');h+=txt(L+6,266,'Sick · orange','w10-svg-label','start');
 const rand=makeRng(97621);let dots='';
 for(const [className,values,y] of [['w10-healthy',data.healthy,164],['w10-sick',data.sick,315]]){
   for(const v of values){const yy=y+(rand()-.5)*75;
    dots+=`<circle cx="${mx(v).toFixed(2)}" cy="${yy.toFixed(2)}" r="4.0" class="${className}"></circle>`;}
 }
 h+=`<g clip-path="url(#w10RocClip)">${dots}${svgLine(mx(cut),T,mx(cut),B,'w10-marker-line')}</g>`;
 h+=txt(clamp(mx(cut)+9,L+20,R-20),T+25,'cutoff','w10-svg-muted','start');
 h+=svgLine(L2,B2,R2,T2,'w10-gridline');
 h+=svgPath(scores.points.map(p=>[rX(p.x),rY(p.y)]),'w10-roc-line');
 const br=markerRates(data,scores.bestCut);
 h+=`<circle cx="${rX(br.fpr)}" cy="${rY(br.tpr)}" r="6" fill="#18864b" stroke="white" stroke-width="2"></circle>`;
 h+=`<circle cx="${rX(current.fpr)}" cy="${rY(current.tpr)}" r="8" class="w10-roc-dot"></circle>`;
 h+=txt(R2,60,`AUC ${scores.auc.toFixed(3)} · sample Youden max marked in green`,'w10-svg-muted','end');
 svg.innerHTML=h;
}
let rocDrag=false;
function rocPointer(event){
 const svg=$('rocSvg');if(!svg)return;
 const ctm=svg.getScreenCTM();if(!ctm)return;
 const loc=new DOMPoint(event.clientX,event.clientY).matrixTransform(ctm.inverse());
 const which=$('rocMarker').value,data=markerCache[which];
 const L=66,R=495,T=78,B=372;
 if(loc.x<L-15||loc.x>R+15||loc.y<T-15||loc.y>B+15)return;
 const value=clamp((loc.x-L)/(R-L)*data.max,0,data.max);
 const step=which==='ferritin'?1:.2;
 $('rocCut').value=String(Math.round(value/step)*step);
 renderRoc();
}

/* --------------------------------------------------------
   Sequential randomization. Mode only alters next assignment.
   No clinical outcome information is ever used.
   -------------------------------------------------------- */
let randState=90418, allocations=[];
function randomU(){randState^=randState<<13;randState^=randState>>>17;randState^=randState<<5;return ((randState>>>0)+.5)/4294967296;}
function assignmentProb(){const t=allocations.filter(x=>x===1).length,c=allocations.length-t;
 if($('ranMode')?.value!=='biased'||t===c)return .5;
 return t<c?.75:.25;
}
function assignPatients(n){for(let i=0;i<n;i++){const p=assignmentProb();allocations.push(randomU()<p?1:0);}renderRandom();}
function renderRandom(){
 const t=allocations.filter(x=>x===1).length,c=allocations.length-t;
 out('ranCounts',`${t} / ${c}`);out('ranProbability',assignmentProb().toFixed(2));out('ranTotal',allocations.length);out('ranGap',Math.abs(t-c));
 const svg=$('randomSvg');if(!svg)return;
 let h=txt(60,35,'Allocations in arrival order','w10-svg-title','start')+txt(495,35,'Accumulated arm balance','w10-svg-title','start');
 h+=`<rect x="60" y="60" width="395" height="330" rx="12" fill="#f8fafc" stroke="#d9e1ea"></rect>`;
 const boxes=allocations.slice(-120);
 boxes.forEach((v,i)=>{const col=i%15,row=Math.floor(i/15);h+=`<rect x="${70+col*25.5}" y="${70+row*36.5}" width="20.5" height="24" rx="4" class="${v?'w10-ranT':'w10-ranC'}"></rect>`;});
 h+=txt(62,420,'Last 120 assignments · green treatment / blue control','w10-svg-muted','start');
 const L=525,R=850,T=88,B=374;h+=svgLine(L,B,R,B)+svgLine(L,T,L,B);
 const maxN=Math.max(20,allocations.length);const maxIm=Math.max(4,Math.ceil(Math.sqrt(Math.max(1,allocations.length))*2));
 const mx=i=>L+i/maxN*(R-L),my=v=>(B+T)/2-v/maxIm*(B-T)/2;
 h+=svgLine(L,my(0),R,my(0),'w10-gridline');
 for(const v of [-maxIm,0,maxIm])h+=txt(L-10,my(v)+5,v,'w10-tick','end');
 for(const i of [0,.25,.5,.75,1])h+=txt(mx(i*maxN),B+25,Math.round(i*maxN));
 if(allocations.length){let bal=0;const coords=[[mx(0),my(0)]];
   for(let i=0;i<allocations.length;i++){bal+=allocations[i]?1:-1;coords.push([mx(i+1),my(clamp(bal,-maxIm,maxIm))]);}
   h+=svgPath(coords,'w10-power-line');
   h+=`<circle cx="${mx(allocations.length)}" cy="${my(clamp(bal,-maxIm,maxIm))}" r="6" fill="#c93838"></circle>`;
 }
 h+=txt(695,447,'Treatment − control assignment count','w10-svg-muted');
 svg.innerHTML=h;
}

/* --------------------------------------------------------
   Planning calculator: t-critical from finite-df expansion;
   power under a normal approximation to noncentral-t power.
   Explicitly described as approximate on the slide.
   -------------------------------------------------------- */
function normCdf(x){
 // Hastings polynomial (absolute error near 1e-7 for N(0,1)).
 const t=1/(1+0.2316419*Math.abs(x));
 const d=0.3989422804014327*Math.exp(-x*x/2);
 const tail=d*t*(0.319381530+t*(-0.356563782+t*(1.781477937+t*(-1.821255978+t*1.330274429))));
 return x>=0?1-tail:tail;
}
function normInv(p){
 // Acklam rational approximation; all caller p are strictly between zero and one.
 const a=[-39.6968302866538,220.946098424521,-275.928510446969,138.357751867269,-30.6647980661472,2.50662827745924];
 const b=[-54.4760987982241,161.585836858041,-155.698979859887,66.8013118877197,-13.2806815528857];
 const c=[-0.00778489400243029,-0.322396458041136,-2.40075827716184,-2.54973253934373,4.37466414146497,2.93816398269878];
 const d=[0.00778469570904146,0.32246712907004,2.445134137143,3.75440866190742];
 if(p<.02425){const q=Math.sqrt(-2*Math.log(p));return (((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5])/((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1);}
 if(p>1-.02425)return -normInv(1-p);
 const q=p-.5,r=q*q;
 return (((((a[0]*r+a[1])*r+a[2])*r+a[3])*r+a[4])*r+a[5])*q/(((((b[0]*r+b[1])*r+b[2])*r+b[3])*r+b[4])*r+1);
}
function approxTCrit(p,df){const z=normInv(p),z2=z*z,z3=z*z2,z5=z3*z2,z7=z5*z2;
 return z+(z3+z)/(4*df)+(5*z5+16*z3+3*z)/(96*df*df)+(3*z7+19*z5+17*z3-15*z)/(384*df*df*df);
}
function approxPower(n,delta,sd,alpha){
 if(n<2)return 0;
 const ncp=Math.abs(delta)/(sd*Math.sqrt(2/n)),crit=approxTCrit(1-alpha/2,2*n-2);
 return clamp(1-normCdf(crit-ncp)+normCdf(-crit-ncp),0,1);
}
function renderPower(){
 const delta=Math.abs(N('powEffect',5)),sd=N('powSd',12),alpha=N('powAlpha',.05),target=N('powTarget',.8);
 if(!(sd>0&&delta>0)){
 for(const id of ['powN','powTotal','powD','powAttained'])out(id,'—');out('powNote','Enter positive anticipated effect and SD.');$('powerSvg').innerHTML='';return;
 }
 const MAX=20000;let targetN=null;
 for(let n=2;n<=MAX;n++){if(approxPower(n,delta,sd,alpha)>=target){targetN=n;break;}}
 const shown=targetN||MAX;
 out('powN',targetN?shown.toLocaleString():'>20,000');out('powTotal',targetN?(shown*2).toLocaleString():'>40,000');out('powD',(delta/sd).toFixed(2));
 out('powAttained',targetN?pct(approxPower(shown,delta,sd,alpha)):'< target by 20,000');
 out('powNote',targetN?'Approximate t-test power using a finite-df t critical value and normal tail approximation; no dropout adjustment.':'Required n exceeds the displayed search limit; investigate feasibility and assumptions.');
 const svg=$('powerSvg');if(!svg)return;
 const L=85,R=854,T=58,B=375,maxN=Math.max(40,Math.min(2000,Math.round(shown*1.35)));
 const mx=n=>L+(n-2)/(maxN-2)*(R-L),my=p=>B-(p-.0)*(B-T);
 let h=axes(L,R,T,B,[[2,mx(2)],[Math.round(maxN/4),mx(maxN/4)],[Math.round(maxN/2),mx(maxN/2)],[Math.round(maxN*3/4),mx(maxN*3/4)],[maxN,mx(maxN)]],[[0,my(0)],[.25,my(.25)],[.5,my(.5)],[.75,my(.75)],[1,my(1)]]);
 h+=txt(L,28,'Planning power vs patients per arm','w10-svg-title','start');
 h+=svgLine(L,my(target),R,my(target),'w10-marker-line');
 const pts=Array.from({length:220},(_,i)=>{const n=2+(maxN-2)*i/219;return[mx(n),my(approxPower(n,delta,sd,alpha))];});
 h+=svgPath(pts,'w10-power-line');
 if(targetN&&targetN<=maxN){h+=svgLine(mx(shown),my(0),mx(shown),my(target),'w10-marker-line');
 h+=`<circle cx="${mx(shown)}" cy="${my(approxPower(shown,delta,sd,alpha))}" r="8" class="w10-power-dot"></circle>`;}
 h+=txt((L+R)/2,443,'Patients per arm (equal allocation)','w10-svg-label');h+=txt(R,36,`Target ${Math.round(target*100)}% · two-sided α = ${alpha}`,'w10-svg-muted','end');
 svg.innerHTML=h;
}

const quizAnswers={
 '1':['C','NPV = TN / (TN + FN); the denominator includes all negative test results.'],
 '2':['B','A cutoff changes sensitivity and specificity. The AUC for fixed biomarker scores remains constant.'],
 '3':['C','Randomization removes systematic assignment mechanisms on average, not random variation.'],
 '4':['A','Between-study differences require inspection of heterogeneity, bias and applicability.']
};
function answerQuiz(button){
 const card=button.closest('.w10-quiz'),spec=quizAnswers[card?.dataset.quiz];if(!spec)return;
 const correct=button.dataset.choice===spec[0];
 card.querySelectorAll('.w10-choice').forEach(b=>b.classList.remove('correct','wrong'));
 button.classList.add(correct?'correct':'wrong');
 const el=card.querySelector('.w10-quiz-feedback');if(el){el.className='w10-quiz-feedback '+(correct?'correct':'wrong');el.textContent=(correct?'Correct. ':'Not quite. ')+spec[1];}
}

let initialized=false;
function initWeek10(){
 if(initialized||!$('confWidget'))return;
 initialized=true;
 for(const id of ['cmTP','cmFN','cmFP','cmTN'])$(id)?.addEventListener('input',renderConfusion);
 $('rocMarker')?.addEventListener('change',changeMarker);
 $('rocCut')?.addEventListener('input',renderRoc);
 const rs=$('rocSvg');
 rs?.addEventListener('pointerdown',e=>{const ctm=rs.getScreenCTM();if(!ctm)return;const p=new DOMPoint(e.clientX,e.clientY).matrixTransform(ctm.inverse());
  if(p.x>=51&&p.x<=510&&p.y>=65&&p.y<=395){rocDrag=true;rs.setPointerCapture?.(e.pointerId);rocPointer(e);}
 });
 rs?.addEventListener('pointermove',e=>{if(rocDrag)rocPointer(e);});
 rs?.addEventListener('pointerup',()=>{rocDrag=false;});
 rs?.addEventListener('pointercancel',()=>{rocDrag=false;});
 $('ranOne')?.addEventListener('click',()=>assignPatients(1));
 $('ranTen')?.addEventListener('click',()=>assignPatients(10));
 $('ranReset')?.addEventListener('click',()=>{allocations=[];randState=90418;renderRandom();});
 $('ranMode')?.addEventListener('change',renderRandom);
 for(const id of ['powEffect','powSd','powAlpha','powTarget'])$(id)?.addEventListener('input',renderPower);
 document.querySelectorAll('.w10-choice').forEach(b=>b.addEventListener('click',()=>answerQuiz(b)));
 renderConfusion();changeMarker();renderRandom();renderPower();
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',initWeek10);else initWeek10();
window.addEventListener('load',initWeek10);
if(window.Reveal&&typeof window.Reveal.on==='function'){
 window.Reveal.on('ready',initWeek10);window.Reveal.on('slidechanged',initWeek10);
}
})();
