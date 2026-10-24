(function(){
'use strict';
/* One script / one initializer. Every widget is scoped to Week 08. */
const $=id=>document.getElementById(id);
const num=(id,def)=>{const el=$(id);return el?Number(el.value):def;};
const clamp=(x,a,b)=>Math.max(a,Math.min(b,x));
const setText=(id,value)=>{if($(id))$(id).textContent=String(value);};
const pFormat=p=>!Number.isFinite(p)?'—':p<.001?'<0.001':p.toFixed(3);
const axis=(x1,y1,x2,y2,cls='w8-axis')=>`<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" class="${cls}"></line>`;
const path=(xy,cls)=>`<path class="${cls}" d="${xy.map((p,i)=>`${i?'L':'M'}${p[0].toFixed(2)},${p[1].toFixed(2)}`).join(' ')}"></path>`;
const rng32=seed=>()=>{let t=seed+=0x6d2b79f5;t=Math.imul(t^t>>>15,t|1);t^=t+Math.imul(t^t>>>7,t|61);return((t^t>>>14)>>>0)/4294967296;};
function randn(r){const u=Math.max(1e-12,r()),v=r();return Math.sqrt(-2*Math.log(u))*Math.cos(2*Math.PI*v);}
function logGamma(z){const p=[.9999999999998099,676.5203681218851,-1259.1392167224028,771.32342877765313,-176.61502916214059,12.507343278686905,-.1385710952657201,9.9843695780195716e-6,1.5056327351493116e-7];if(z<.5)return Math.log(Math.PI)-Math.log(Math.sin(Math.PI*z))-logGamma(1-z);z--;let a=p[0];for(let i=1;i<9;i++)a+=p[i]/(z+i);const t=z+7.5;return .5*Math.log(2*Math.PI)+(z+.5)*Math.log(t)-t+Math.log(a);}
function betacf(a,b,x){const EPS=3e-12,FPMIN=1e-300;let qab=a+b,qap=a+1,qam=a-1,c=1,d=1-qab*x/qap;if(Math.abs(d)<FPMIN)d=FPMIN;d=1/d;let h=d;for(let m=1;m<201;m++){const m2=2*m;let aa=m*(b-m)*x/((qam+m2)*(a+m2));d=1+aa*d;if(Math.abs(d)<FPMIN)d=FPMIN;c=1+aa/c;if(Math.abs(c)<FPMIN)c=FPMIN;d=1/d;h*=d*c;aa=-(a+m)*(qab+m)*x/((a+m2)*(qap+m2));d=1+aa*d;if(Math.abs(d)<FPMIN)d=FPMIN;c=1+aa/c;if(Math.abs(c)<FPMIN)c=FPMIN;d=1/d;const del=d*c;h*=del;if(Math.abs(del-1)<EPS)break;}return h;}
function betai(a,b,x){if(x<=0)return 0;if(x>=1)return 1;const bt=Math.exp(logGamma(a+b)-logGamma(a)-logGamma(b)+a*Math.log(x)+b*Math.log(1-x));return x<(a+1)/(a+b+2)?bt*betacf(a,b,x)/a:1-bt*betacf(b,a,1-x)/b;}
function tCdf(t,v){let x=v/(v+t*t),b=betai(v/2,.5,x);return t>=0?1-.5*b:.5*b;}
function tInv(p,v){let a=-40,b=40;for(let i=0;i<65;i++){let mid=(a+b)/2;if(tCdf(mid,v)<p)a=mid;else b=mid;}return(a+b)/2;}
function gammaQ(a,x){if(x<=0)return 1;const EPS=3e-12,FPMIN=1e-300;if(x<a+1){let ap=a,sum=1/a,d=sum;for(let j=1;j<=200;j++){ap++;d*=x/ap;sum+=d;if(Math.abs(d)<Math.abs(sum)*EPS)break;}return clamp(1-sum*Math.exp(-x+a*Math.log(x)-logGamma(a)),0,1);}let b=x+1-a,c=1/FPMIN,d=1/b,h=d;for(let i=1;i<=200;i++){const an=-i*(i-a);b+=2;d=an*d+b;if(Math.abs(d)<FPMIN)d=FPMIN;c=b+an/c;if(Math.abs(c)<FPMIN)c=FPMIN;d=1/d;const del=d*c;h*=del;if(Math.abs(del-1)<EPS)break;}return clamp(Math.exp(-x+a*Math.log(x)-logGamma(a))*h,0,1);}
function chiInv(p,df){let low=0,high=df+12*Math.sqrt(df+1)+20;for(let i=0;i<75;i++){let m=(low+high)/2;if(1-gammaQ(df/2,m/2)<p)low=m;else high=m;}return(low+high)/2;}
function reg(xs,ys){const n=xs.length,xbar=xs.reduce((a,b)=>a+b,0)/n,ybar=ys.reduce((a,b)=>a+b,0)/n;let sxx=0,sxy=0,syy=0;for(let i=0;i<n;i++){const dx=xs[i]-xbar,dy=ys[i]-ybar;sxx+=dx*dx;sxy+=dx*dy;syy+=dy*dy;}const b=sxy/sxx,a=ybar-b*xbar,sse=xs.reduce((s,x,i)=>s+(ys[i]-a-b*x)**2,0),df=n-2,s=Math.sqrt(sse/df),r2=syy>0?clamp(1-sse/syy,0,1):1,t=b/(s/Math.sqrt(sxx)),p=2*(1-tCdf(Math.abs(t),df));return{n,a,b,sse,s,df,r2,p,xbar,sxx};}
function axesFrame({L=75,R=856,T=40,B=410,x0=0,x1=12,y0=0,y1=1.1,xticks=[0,2,4,6,8,10,12],yticks=[0,.2,.4,.6,.8,1],xlabel='Concentration (mg/L)',ylabel='Absorbance (AU)'}){
 const mx=x=>L+(x-x0)/(x1-x0)*(R-L),my=y=>B-(y-y0)/(y1-y0)*(B-T);
 let s='';for(const v of yticks){const y=my(v);s+=axis(L,y,R,y,'w8-gridline')+`<text x="${L-12}" y="${y+5}" text-anchor="end" class="w8-tick">${v.toFixed(1)}</text>`;}for(const v of xticks){const x=mx(v);s+=axis(x,B,x,B+7)+`<text x="${x}" y="${B+24}" class="w8-tick" text-anchor="middle">${v}</text>`;}s+=axis(L,T,L,B)+axis(L,B,R,B)+`<text x="${(L+R)/2}" y="${B+64}" class="w8-axis-title" text-anchor="middle">${xlabel}</text><text x="21" y="${(T+B)/2}" transform="rotate(-90 21 ${(T+B)/2})" text-anchor="middle" class="w8-axis-title">${ylabel}</text>`;return{html:s,mx,my,L,R,T,B};}
function points(xy,cls='w8-point',radius=5){return xy.map(([x,y])=>`<circle cx="${x.toFixed(2)}" cy="${y.toFixed(2)}" r="${radius}" class="${cls}"></circle>`).join('');}
function lineSamples(fn,mx,my,lo,hi,N=100){const ar=[];for(let i=0;i<=N;i++){const x=lo+i*(hi-lo)/N;ar.push([mx(x),my(fn(x))]);}return ar;}
function filledBetween(lower,upper,mx,my,x0=0,x1=12,fillCls='w8-band-mean'){
 const top=[],bottom=[];for(let i=0;i<=90;i++){const x=x0+(x1-x0)*i/90;top.push([mx(x),my(upper(x))]);bottom.push([mx(x),my(lower(x))]);}return `<path class="${fillCls}" d="${top.concat(bottom.reverse()).map((p,i)=>`${i?'L':'M'}${p[0].toFixed(1)},${p[1].toFixed(1)}`).join(' ')}Z"></path>`;
}
/* CALIBRATION HAND-FIT */
const olsX=[.6,1.6,2.5,3.4,4.4,5.5,6.5,7.4,8.5,9.6,10.7,11.6];
const olsY=olsX.map((x,i)=>.048+.075*x+[.012,-.025,.026,-.019,.012,.037,-.021,.014,-.006,.031,-.013,.008][i]);
let showTrueOLS=false;
function renderOLS(){const a=num('olsIntercept',.22),b=num('olsSlope',.04),f=reg(olsX,olsY);setText('olsInterceptValue',a.toFixed(2));setText('olsSlopeValue',b.toFixed(3));setText('olsSseOut',olsX.reduce((s,x,i)=>s+(olsY[i]-a-b*x)**2,0).toFixed(4));setText('olsFit',showTrueOLS?'Hide least-squares fit':'Show least-squares fit');const svg=$('olsSvg');if(!svg)return;
 const G=axesFrame({});let out=G.html+`<defs><clipPath id="olsClip"><rect x="${G.L}" y="${G.T}" width="${G.R-G.L}" height="${G.B-G.T}"></rect></clipPath></defs><g clip-path="url(#olsClip)">`;
 olsX.forEach((x,i)=>{out+=axis(G.mx(x),G.my(olsY[i]),G.mx(x),G.my(a+b*x),'w8-residual');});
 out+=path(lineSamples(x=>a+b*x,G.mx,G.my,0,12),'w8-guess');if(showTrueOLS)out+=path(lineSamples(x=>f.a+f.b*x,G.mx,G.my,0,12),'w8-fit');out+=points(olsX.map((x,i)=>[G.mx(x),G.my(olsY[i])]))+'</g>';
 out+=`<text x="${G.L+8}" y="23" class="w8-plot-note">purple: your line</text>`+(showTrueOLS?`<text x="${G.R-8}" y="23" text-anchor="end" class="w8-plot-note">green: OLS · intercept ${f.a.toFixed(3)}, slope ${f.b.toFixed(3)}</text>`:'');svg.innerHTML=out;}
/* CONFIDENCE, PREDICTION, TOLERANCE EXPLORER */
let bandSeed=0,bandData=[];
function bandInit(){
 const sd=num('bandSd',.06);
 bandData=olsX.map((x,i)=>({x,z:(olsY[i]-(.05+.075*x))/.06,y:olsY[i]}));
 renderBands();
}
function bandNew(){
 bandSeed++;
 const r=rng32(80808+bandSeed*733),sd=num('bandSd',.06);
 bandData=[];
 for(let i=0;i<12;i++){
   const x=olsX[i],z=randn(r);
   bandData.push({x,z,y:.05+.075*x+sd*z});
 }
 renderBands();
}
function bandAdd(){
 const r=rng32(88000+bandSeed*1357+bandData.length*911);
 const sd=num('bandSd',.06),x=.6+11*r(),z=randn(r);
 bandData.push({x,z,y:.05+.075*x+sd*z});
 renderBands();
}
function bandRedrawNoise(){
 const sd=num('bandSd',.06);
 for(const p of bandData)p.y=.05+.075*p.x+sd*p.z;
 renderBands();
}
function renderBands(){const svg=$('bandSvg');if(!svg||bandData.length<5)return;const xs=bandData.map(o=>o.x),ys=bandData.map(o=>o.y),f=reg(xs,ys),kind=$('bandType')?.value||'all';setText('bandSdValue',num('bandSd',.06).toFixed(3));setText('bandNOut',f.n);setText('bandR2Out',f.r2.toFixed(3));setText('bandPOut',pFormat(f.p));
 const G=axesFrame({y0:-.20,y1:1.35,yticks:[-.2,0,.2,.4,.6,.8,1,1.2]});let out=G.html+`<defs><clipPath id="bandClip"><rect x="${G.L}" y="${G.T}" width="${G.R-G.L}" height="${G.B-G.T}"></rect></clipPath></defs><g clip-path="url(#bandClip)">`;
 const tcrit=tInv(.975,f.df),tBonf=tInv(.9875,f.df),upperSig=f.s*Math.sqrt(f.df/chiInv(.025,f.df));const h=x=>1/f.n+(x-f.xbar)**2/f.sxx;
 const meanW=x=>tcrit*f.s*Math.sqrt(h(x)),predW=x=>tcrit*f.s*Math.sqrt(1+h(x));
 // Conservative 95%-confidence / 95%-content conditional normal tolerance envelope:
 // Bonferroni 97.5% mean bound + 97.5% upper confidence bound on sigma.
 const tolW=x=>tBonf*f.s*Math.sqrt(h(x))+1.95996398454*upperSig;
 const selected=(name)=>kind==='all'||kind===name;
 const addBand=(fn,cls)=>filledBetween(x=>f.a+f.b*x-fn(x),x=>f.a+f.b*x+fn(x),G.mx,G.my,0,12,cls);
 if(selected('tolerance'))out+=addBand(tolW,'w8-band-tolerance');
 if(selected('prediction'))out+=addBand(predW,'w8-band-prediction');
 if(selected('mean'))out+=addBand(meanW,'w8-band-mean');
 out+=path(lineSamples(x=>f.a+f.b*x,G.mx,G.my,0,12),'w8-fit');out+=path(lineSamples(x=>.05+.075*x,G.mx,G.my,0,12),'w8-true');out+=points(bandData.map(o=>[G.mx(o.x),G.my(o.y)]),'w8-point',4.1)+'</g>';
 out+=`<text x="${G.L}" y="23" class="w8-plot-note">Dashed orange = generating mean · green = fitted mean</text>`;
 svg.innerHTML=out;}
/* DIAGNOSTICS AND TRANSFORMS: STATIC READY-TO-USE SVGS */
const diagNotes={good_tight:'Residuals roughly random, QQ close to line; high R² is not the only check.',good_loose:'Weak correlation does not automatically mean the linear model is invalid.',nonnormal:'QQ departures indicate a skewed conditional error distribution.',curvature:'Residual-vs-fitted trend reveals an omitted nonlinear relationship.',outliers:'Check high standardized residuals and leverage/influence; do not delete mechanically.',hetero:'Residual spread increases with fitted response: constant-variance assumption fails.'};
function renderDiagnostic(){const k=$('diagChoice')?.value||'good_tight';if($('diagImage'))$('diagImage').src=`figures/diagnostic_${k}.svg`;setText('diagInterpretation',diagNotes[k]);}
const transformDescriptions={exponential:'ln(y) = ln(a) + b x  (y > 0)',power:'ln(y) = ln(a) + b ln(x)  (x,y > 0)',hyperbolic:'1/y = 1/Vmax + (Km/Vmax)(1/x)',logarithmic:'y = a + b ln(x)  (x > 0)'};
function renderTransform(){const key=$('transformChoice')?.value||'exponential';if($('transformImage'))$('transformImage').src=`figures/transform_${key}.svg`;setText('transformEquation',transformDescriptions[key]);}
/* NONLINEAR TITRATION: 2-parameter sigmoid, fixed experimentally known asymptotes */
const nlX=Array.from({length:36},(_,i)=>1.1+11.8*i/35),nlTrue={base:35,range:170,v:7.1,k:.7};
const nlRng=rng32(8999),nlY=nlX.map(x=>35+170/(1+Math.exp(-(x-7.1)/.7))+4*randn(nlRng));
let nlHistory=[],nlCurrent=0,nlToken=0;
const sigmoid=(x,v,k)=>35+170/(1+Math.exp(-clamp((x-v)/k,-30,30)));
const nlSse=(v,k)=>nlX.reduce((acc,x,i)=>acc+(nlY[i]-sigmoid(x,v,k))**2,0);
function nonlinearHistory(){const maxSteps=Math.round(num('nlSteps',12)),initV=num('nlV',5),initK=num('nlK',1.8);let v=initV,k=initK,lam=.04;const hist=[{v,k,sse:nlSse(v,k)}];for(let iter=0;iter<maxSteps;iter++){
 let a=0,b=0,c=0,d=0,e=0;for(let i=0;i<nlX.length;i++){const x=nlX[i],z=clamp((x-v)/k,-30,30),g=1/(1+Math.exp(-z)),common=170*g*(1-g),jv=-common/k,jk=-common*(x-v)/(k*k),res=nlY[i]-sigmoid(x,v,k);a+=jv*jv;b+=jv*jk;c+=jk*jk;d+=jv*res;e+=jk*res;}
 let improved=false;for(let tr=0;tr<9;tr++){const aa=a*(1+lam),cc=c*(1+lam),det=aa*cc-b*b;if(det<=1e-12){lam*=8;continue;}const dv=clamp((cc*d-b*e)/det,-2,2),dk=clamp((aa*e-b*d)/det,-.6,.6),vv=clamp(v+dv,1,13),kk=clamp(k+dk,.15,4),loss=nlSse(vv,kk);if(loss<=nlSse(v,k)+1e-8){v=vv;k=kk;lam=Math.max(1e-8,lam*.6);improved=true;break;}lam*=5;}
 hist.push({v,k,sse:nlSse(v,k)});if(!improved)break;
 }return hist;}
function renderNL(i=nlCurrent){if(!nlHistory.length)return;const svg=$('nlSvg');if(!svg)return;nlCurrent=clamp(i,0,nlHistory.length-1);const cur=nlHistory[nlCurrent];setText('nlVValue',num('nlV',5).toFixed(1));setText('nlKValue',num('nlK',1.8).toFixed(1));setText('nlStepsValue',num('nlSteps',12));setText('nlVOut',cur.v.toFixed(2));setText('nlKOut',cur.k.toFixed(2));const m=nlY.reduce((a,b)=>a+b,0)/nlY.length;
 const syy=nlY.reduce((sum,y)=>sum+(y-m)**2,0);
 setText('nlR2Out',(1-cur.sse/syy).toFixed(3));
 let a11=0,a12=0,a22=0;
 for(const x of nlX){const z=clamp((x-cur.v)/cur.k,-30,30),g=1/(1+Math.exp(-z)),common=170*g*(1-g),jv=-common/cur.k,jk=-common*(x-cur.v)/(cur.k**2);a11+=jv*jv;a12+=jv*jk;a22+=jk*jk;}
 const det=a11*a22-a12*a12,s2=cur.sse/(nlX.length-2);
 setText('nlSeVOut',det>0?Math.sqrt(s2*a22/det).toFixed(3):'—');
 setText('nlSeKOut',det>0?Math.sqrt(s2*a11/det).toFixed(3):'—');
 setText('nlStepOut',`${nlCurrent}/${nlHistory.length-1} · ${cur.sse.toFixed(0)}`);
 const G=axesFrame({x0:1,x1:13,y0:10,y1:230,xticks:[1,3,5,7,9,11,13],yticks:[25,75,125,175,225],xlabel:'Titrant volume (mL)',ylabel:'Electrode potential (mV)'});let s=G.html+`<defs><clipPath id="nlClip"><rect x="${G.L}" y="${G.T}" width="${G.R-G.L}" height="${G.B-G.T}"></rect></clipPath></defs><g clip-path="url(#nlClip)">`;
 s+=path(lineSamples(x=>sigmoid(x,cur.v,cur.k),G.mx,G.my,1,13,180),'w8-fit');s+=path(lineSamples(x=>sigmoid(x,nlTrue.v,nlTrue.k),G.mx,G.my,1,13,180),'w8-true');s+=points(nlX.map((x,i)=>[G.mx(x),G.my(nlY[i])]),'w8-point',4.1)+'</g>';s+=`<text x="${G.L}" y="23" class="w8-plot-note">Green: iteratively fitted · orange dashed: generating curve</text>`;svg.innerHTML=s;}
function resetNL(){nlToken++;nlHistory=nonlinearHistory();nlCurrent=0;renderNL(0);}
function runNL(){nlToken++;const token=nlToken;nlHistory=nonlinearHistory();nlCurrent=0;renderNL(0);function step(){if(token!==nlToken)return;if(nlCurrent>=nlHistory.length-1)return;nlCurrent++;renderNL(nlCurrent);setTimeout(step,220);}setTimeout(step,220);}
/* POLYNOMIAL MODEL CAPACITY + AIC */
let polySeed=1,polyPoints=[];
function polyNew(){polySeed++;const r=rng32(81817+polySeed*319);polyPoints=Array.from({length:35},(_,i)=>{const x=-1+.02+1.96*i/34;return{x,y:.8+.85*x-.50*x*x+1.15*x*x*x+.26*randn(r)};});renderPoly();}
function solve(A,b){const n=b.length;const a=A.map((row,i)=>row.slice().concat(b[i]));for(let c=0;c<n;c++){let pivot=c;for(let r=c+1;r<n;r++)if(Math.abs(a[r][c])>Math.abs(a[pivot][c]))pivot=r;[a[c],a[pivot]]=[a[pivot],a[c]];const d=a[c][c];if(Math.abs(d)<1e-13)return null;for(let j=c;j<=n;j++)a[c][j]/=d;for(let r=0;r<n;r++){if(r===c)continue;const k=a[r][c];for(let j=c;j<=n;j++)a[r][j]-=k*a[c][j];}}return a.map(row=>row[n]);}
function fitPoly(deg){const k=deg+1,A=Array.from({length:k},()=>Array(k).fill(0)),b=Array(k).fill(0);for(const p of polyPoints){let powers=[1];for(let i=1;i<=2*deg;i++)powers.push(powers[i-1]*p.x);for(let i=0;i<k;i++){b[i]+=p.y*powers[i];for(let j=0;j<k;j++)A[i][j]+=powers[i+j];}}const coef=solve(A,b);if(!coef)return null;const predict=x=>coef.reduce((s,c,j)=>s+c*x**j,0);const SSE=polyPoints.reduce((s,p)=>s+(p.y-predict(p.x))**2,0),mean=polyPoints.reduce((s,p)=>s+p.y,0)/polyPoints.length,SST=polyPoints.reduce((s,p)=>s+(p.y-mean)**2,0),r2=1-SSE/SST;const n=polyPoints.length,aic=n*Math.log(Math.max(1e-9,SSE)/n)+2*k;return{deg,coef,predict,r2,aic};}
function renderPoly(){if(!polyPoints.length)return;const deg=num('polyDegree',3);setText('polyDegreeValue',deg);const models=Array.from({length:8},(_,i)=>fitPoly(i+1)),chosen=models[deg-1],best=models.reduce((a,b)=>a.aic<b.aic?a:b);setText('polyR2Out',chosen.r2.toFixed(3));setText('polyAicOut',chosen.aic.toFixed(1));setText('polyBestOut',best.deg);const svg=$('polySvg');if(!svg)return;
 const L=70,R=515,T=47,B=412,mx=x=>L+(x+1)/2*(R-L),my=y=>B-(y+1.5)/4.5*(B-T);let s='';for(const y of [-1,0,1,2,3]){s+=axis(L,my(y),R,my(y),'w8-gridline')+`<text x="${L-9}" y="${my(y)+4}" class="w8-tick" text-anchor="end">${y}</text>`;}for(const x of [-1,-.5,0,.5,1]){s+=axis(mx(x),B,mx(x),B+7)+`<text x="${mx(x)}" y="${B+25}" class="w8-tick" text-anchor="middle">${x}</text>`;}s+=axis(L,T,L,B)+axis(L,B,R,B)+`<text x="${(L+R)/2}" y="466" class="w8-axis-title" text-anchor="middle">Scaled cell size</text><text x="${L}" y="24" class="w8-plot-caption">Data and degree-${deg} fit</text>`;
 s+=`<defs><clipPath id="polyClip"><rect x="${L}" y="${T}" width="${R-L}" height="${B-T}"></rect></clipPath></defs><g clip-path="url(#polyClip)">`;
 s+=path(lineSamples(chosen.predict,mx,my,-1,1,200),'w8-fit');s+=points(polyPoints.map(p=>[mx(p.x),my(p.y)]),'w8-point',3.6)+'</g>';
 const al=600,ar=862,at=56,ab=412,values=models.map(o=>o.aic),min=Math.min(...values)-6,max=Math.max(...values)+6,fy=y=>ab-(y-min)/(max-min)*(ab-at),fx=d=>al+(d-1)/7*(ar-al);for(let d=1;d<=8;d++){const x=fx(d);s+=axis(x,ab,x,ab+6)+`<text x="${x}" y="${ab+23}" class="w8-tick" text-anchor="middle">${d}</text>`;}for(let j=0;j<=4;j++){const v=min+j*(max-min)/4,y=fy(v);s+=axis(al,y,ar,y,'w8-gridline')+`<text x="${al-9}" y="${y+5}" class="w8-tick" text-anchor="end">${v.toFixed(0)}</text>`;}s+=axis(al,at,al,ab)+axis(al,ab,ar,ab)+`<text x="${(al+ar)/2}" y="466" class="w8-axis-title" text-anchor="middle">Polynomial degree</text><text x="${al}" y="24" class="w8-plot-caption">AIC (lower is better)</text>`;
 s+=path(models.map(m=>[fx(m.deg),fy(m.aic)]),'w8-guess');models.forEach(m=>{s+=`<circle cx="${fx(m.deg)}" cy="${fy(m.aic)}" r="${m.deg===deg?7:4}" fill="${m.deg===best.deg?'#18864b':m.deg===deg?'#c93838':'#7b4ab5'}" stroke="white" stroke-width="2"></circle>`;});svg.innerHTML=s;}
/* FOUR QUIZ FEEDBACK CHANNELS */
const answerKey={model:{ans:'B',ok:'Simple linear regression models continuous absorbance against known concentration.'},coef:{ans:'B',ok:'The coefficient is a conditional association at the same modeled height, not an automatic causal effect.'},diag:{ans:'B',ok:'A strong R² can coexist with functional-form misspecification; investigate nonlinear terms and mechanism.'},extra:{ans:'B',ok:'This is extrapolation beyond validated standards. Re-measure at a suitable dilution.'}};
function answerQuiz(btn){const key=btn.dataset.q,ans=btn.dataset.a,quiz=btn.closest('.w8-quiz'),feedback=$(`quiz${key[0].toUpperCase()+key.slice(1)}Feedback`),correct=answerKey[key].ans===ans;quiz.querySelectorAll('.w8-choice').forEach(b=>b.classList.remove('is-correct','is-wrong'));btn.classList.add(correct?'is-correct':'is-wrong');if(feedback){feedback.textContent=(correct?'Correct. ':'Not quite. ')+answerKey[key].ok;feedback.className='w8-quiz-feedback '+(correct?'correct':'wrong');}}
/* INITIALIZE ONCE: no nested listeners / no duplicate rendering scripts */
let initialized=false;
function initWeek08(){if(initialized||!$('olsWidget'))return;initialized=true;
 $('olsIntercept')?.addEventListener('input',renderOLS);$('olsSlope')?.addEventListener('input',renderOLS);$('olsFit')?.addEventListener('click',()=>{showTrueOLS=!showTrueOLS;renderOLS();});
 $('bandType')?.addEventListener('change',renderBands);$('bandSd')?.addEventListener('input',bandRedrawNoise);$('bandNew')?.addEventListener('click',bandNew);$('bandAdd')?.addEventListener('click',bandAdd);
 $('diagChoice')?.addEventListener('change',renderDiagnostic);$('transformChoice')?.addEventListener('change',renderTransform);
 for(const id of ['nlV','nlK','nlSteps'])$(id)?.addEventListener('input',resetNL);$('nlRun')?.addEventListener('click',runNL);
 $('polyDegree')?.addEventListener('input',renderPoly);$('polyNew')?.addEventListener('click',polyNew);
 document.querySelectorAll('.w8-choice').forEach(b=>b.addEventListener('click',()=>answerQuiz(b)));
 renderOLS();bandInit();renderDiagnostic();renderTransform();resetNL();polyNew();
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',initWeek08);else initWeek08();
window.addEventListener('load',initWeek08);
if(window.Reveal&&typeof window.Reveal.on==='function'){window.Reveal.on('ready',initWeek08);window.Reveal.on('slidechanged',initWeek08);}
})();
