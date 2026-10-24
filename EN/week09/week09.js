(function(){
'use strict';
const $=id=>document.getElementById(id);
const clamp=(x,a,b)=>Math.max(a,Math.min(b,x));
const num=(id,def)=>{const el=$(id);return el?Number(el.value):def;};
const setText=(id,v)=>{const e=$(id);if(e)e.textContent=String(v);};
const sigmoid=z=>1/(1+Math.exp(-clamp(z,-35,35)));
const axis=(x1,y1,x2,y2,cls='w9-axis')=>`<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" class="${cls}"></line>`;
const curve=(xy,cls)=>`<path class="${cls}" d="${xy.map((p,i)=>`${i?'L':'M'}${p[0].toFixed(2)},${p[1].toFixed(2)}`).join(' ')}"></path>`;
function axes({L=65,R=840,T=65,B=390,x0,x1,y0,y1,xticks,yticks,xlabel,ylabel}){
 const mx=x=>L+(x-x0)/(x1-x0)*(R-L),my=y=>B-(y-y0)/(y1-y0)*(B-T);
 let html='';
 for(const y of yticks){const yy=my(y);html+=axis(L,yy,R,yy,'w9-gridline')+`<text x="${L-11}" y="${yy+4}" text-anchor="end" class="w9-tick">${y}</text>`;}
 for(const x of xticks){const xx=mx(x);html+=axis(xx,B,xx,B+7)+`<text x="${xx}" y="${B+27}" text-anchor="middle" class="w9-tick">${x}</text>`;}
 html+=axis(L,T,L,B)+axis(L,B,R,B)+`<text x="${(L+R)/2}" y="${B+63}" text-anchor="middle" class="w9-axis-title">${xlabel}</text>`;
 html+=`<text transform="translate(18 ${(T+B)/2}) rotate(-90)" text-anchor="middle" class="w9-axis-title">${ylabel}</text>`;
 return {mx,my,html,L,R,T,B};
}
function renderOdds(){
 const p=num('oddsP',50)/100;
 setText('oddsPVal',p.toFixed(2));setText('oddsProbOut',p.toFixed(2));
 setText('oddsOddsOut',p===1?'∞':(p/(1-p)).toFixed(2));
 setText('oddsLogitOut',p===0?'−∞':p===1?'+∞':Math.log(p/(1-p)).toFixed(2));
 const svg=$('oddsSvg');if(!svg)return;
 let html='';const panes=[{left:70,right:425,title:'Odds = p / (1−p)',type:'odds',color:'#18864b'},{left:525,right:860,title:'Logit = ln(odds)',type:'logit',color:'#7b4ab5'}];
 for(const pane of panes){
  const {left:L,right:R,type,color}=pane,T=67,B=395;
  const mx=x=>L+x*(R-L);
  const range=type==='odds'?[0,12]:[-6,6];const my=y=>B-(y-range[0])/(range[1]-range[0])*(B-T);
  const clip=v=>clamp(v,...range);
  const f=x=>type==='odds'?x/(1-x):Math.log(x/(1-x));
  html+=`<text x="${L}" y="31" class="w9-plot-title">${pane.title}</text>`;
  const yt=type==='odds'?[0,3,6,9,12]:[-6,-3,0,3,6];
  for(const v of yt)html+=axis(L,my(v),R,my(v),'w9-gridline')+`<text x="${L-8}" y="${my(v)+5}" text-anchor="end" class="w9-tick">${v}</text>`;
  for(const v of [0,.25,.5,.75,1])html+=axis(mx(v),B,mx(v),B+6)+`<text x="${mx(v)}" y="${B+25}" text-anchor="middle" class="w9-tick">${v.toFixed(2)}</text>`;
  html+=axis(L,T,L,B)+axis(L,B,R,B)+`<text x="${(L+R)/2}" y="${B+57}" text-anchor="middle" class="w9-axis-title">Event probability p</text>`;
  const xy=Array.from({length:299},(_,i)=>{const v=.001+.998*i/298;return[mx(v),my(clip(f(v)))];});
  html+=curve(xy,type==='odds'?'w9-curve-odds':'w9-curve-logit');
  html+=axis(mx(p),T,mx(p),B,'w9-guide');
  let y;if(p===0)y=type==='logit'?range[0]:0;else if(p===1)y=range[1];else y=clip(f(p));
  html+=`<circle cx="${mx(p)}" cy="${my(y)}" r="7" fill="${color}" stroke="white" stroke-width="2"></circle>`;
  if(type==='odds')html+=`<text x="${R-4}" y="${T+18}" text-anchor="end" class="w9-plot-note">top clipped at odds = 12</text>`;
 }
 svg.innerHTML=html;
}
function renderLogistic(){
 const b0=num('logB0',-2.3),b1=num('logB1',.34),b2=num('logB2',.68),b3=num('logB3',.26);
 for(const [id,v] of [['logB0Value',b0],['logB1Value',b1],['logB2Value',b2],['logB3Value',b3]])setText(id,v.toFixed(2));
 setText('logOrNon',Math.exp(b1).toFixed(2));setText('logOrSm',Math.exp(b1+b3).toFixed(2));setText('logRatio',Math.exp(b3).toFixed(2));
 const svg=$('logisticSvg');if(!svg)return;
 const G=axes({L:80,R:855,T:56,B:397,x0:90,x1:180,y0:0,y1:1,xticks:[90,105,120,135,150,165,180],yticks:[0,.2,.4,.6,.8,1],xlabel:'Systolic blood pressure (mmHg)',ylabel:'Modeled probability of ACS'});
 let html=G.html;
 const f=(bp,smoker)=>sigmoid(b0+b1*((bp-120)/10)+smoker*(b2+b3*((bp-120)/10)));
 for(const smoker of [0,1]){
  const pts=Array.from({length:181},(_,i)=>{const bp=90+i*.5;return[G.mx(bp),G.my(f(bp,smoker))];});
  html+=curve(pts,smoker?'w9-smoker-line':'w9-nonsmoker-line');
  html+=`<circle cx="${G.mx(120)}" cy="${G.my(f(120,smoker))}" r="6.5" class="${smoker?'w9-smoker-point':'w9-nonsmoker-point'}"></circle>`;
 }
 html+=axis(G.mx(120),G.T,G.mx(120),G.B,'w9-reference-line');
 html+=`<line x1="580" y1="26" x2="614" y2="26" class="w9-nonsmoker-line"></line><text x="621" y="31" class="w9-legend-a">Non-smoker</text>`;
 html+=`<line x1="731" y1="26" x2="765" y2="26" class="w9-smoker-line"></line><text x="772" y="31" class="w9-legend-b">Smoker</text>`;
 svg.innerHTML=html;
}
const answers={
 family:{ans:'B',why:'An episode total is a count. Check overdispersion, exposure duration and zero inflation if relevant.'},
 odds:{ans:'B',why:'An odds ratio multiplies conditional odds. It is not a percentage-point change in probability.'},
 interaction:{ans:'C',why:'β₃ changes the slope when s switches from 0 to 1; exp(β₃) is the ratio of the two SBP odds ratios.'},
 ranks:{ans:'B',why:'Different shapes can yield a rank-based difference without a simple interpretation as a shift in means or medians.'}
};
function answerQuiz(button){
 const key=button.dataset.q,entry=answers[key];if(!entry)return;
 const card=button.closest('.w9-quiz');if(!card)return;
 card.querySelectorAll('.w9-choice').forEach(b=>b.classList.remove('is-correct','is-wrong'));
 const correct=button.dataset.a===entry.ans;
 button.classList.add(correct?'is-correct':'is-wrong');
 const fb=$('quiz'+key[0].toUpperCase()+key.slice(1)+'Feedback');
 if(fb){fb.textContent=(correct?'Correct. ':'Not quite. ')+entry.why;fb.className='w9-quiz-feedback '+(correct?'correct':'wrong');}
}
let initialized=false;
function initWeek09(){
 if(initialized||!$('oddsWidget'))return;
 initialized=true;
 $('oddsP')?.addEventListener('input',renderOdds);
 for(const id of ['logB0','logB1','logB2','logB3'])$(id)?.addEventListener('input',renderLogistic);
 document.querySelectorAll('.w9-choice').forEach(b=>b.addEventListener('click',()=>answerQuiz(b)));
 renderOdds();renderLogistic();
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',initWeek09);else initWeek09();
window.addEventListener('load',initWeek09);
if(window.Reveal&&typeof window.Reveal.on==='function'){window.Reveal.on('ready',initWeek09);window.Reveal.on('slidechanged',initWeek09);}
})();
