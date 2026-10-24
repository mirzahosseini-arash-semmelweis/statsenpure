/* Week 11 interactive laboratories · standalone; no external libraries.
   All data synthetic, fixed-size; initialized once for RevealJS. */
(()=>{'use strict';
const $=id=>document.getElementById(id);
const C={obs:'#1f6feb',model:'#c65d09',est:'#18864b',warn:'#c93838',unc:'#7b4ab5',ink:'#101828',muted:'#667085',grid:'#e5eaf1'};
const clamp=(v,a,b)=>Math.max(a,Math.min(b,v));
const numeric=(id,fallback=0)=>{const n=Number($(id)?.value);return Number.isFinite(n)?n:fallback;};
const text=(id,v)=>{const e=$(id);if(e)e.textContent=String(v);};
const esc=s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;');
function rand(seed){let x=(seed>>>0)||1;return()=>((x=(1664525*x+1013904223)>>>0)/4294967296);}
function gauss(r){let u=0;while(u===0)u=r();return Math.sqrt(-2*Math.log(u))*Math.cos(2*Math.PI*r());}
const path=(pts,opts='')=>`<path d="${pts.map((v,i)=>`${i?'L':'M'}${v[0].toFixed(2)},${v[1].toFixed(2)}`).join(' ')}" ${opts}/>`;
const line=(x1,y1,x2,y2,color=C.grid,w=1.3,dash='')=>`<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" stroke="${color}" stroke-width="${w}" ${dash?`stroke-dasharray="${dash}"`:''}/>`;
const label=(x,y,t,color=C.muted,size=13,anchor='middle',weight=720)=>`<text x="${x}" y="${y}" text-anchor="${anchor}" fill="${color}" font-size="${size}" font-weight="${weight}">${esc(t)}</text>`;
function axes(L,R,T,B,xt=[],yt=[],title='',xlabel=''){
 let h=line(L,T,L,B,'#98a2b3',1.6)+line(L,B,R,B,'#98a2b3',1.6);
 for(const [v,x] of xt){h+=line(x,B,x,B+7,'#98a2b3',1.3)+label(x,B+27,v);}
 for(const [v,y] of yt){h+=line(L,y,R,y,C.grid,1.3,'4 5')+label(L-10,y+4,v,C.muted,12,'end');}
 if(title)h+=label(L,28,title,C.ink,18,'start',850);
 if(xlabel)h+=label((L+R)/2,449,xlabel,C.ink,14);
 return h;
}
function solve(mat,vec){ // scaled partial-pivot Gauss elimination; small dense systems
 const n=vec.length,A=mat.map((row,i)=>row.slice().concat(vec[i]));
 for(let k=0;k<n;k++){
  let ix=k;for(let i=k+1;i<n;i++)if(Math.abs(A[i][k])>Math.abs(A[ix][k]))ix=i;
  if(Math.abs(A[ix][k])<1e-13)return Array(n).fill(NaN);
  if(ix!==k)[A[k],A[ix]]=[A[ix],A[k]];
  const pivot=A[k][k];for(let j=k;j<=n;j++)A[k][j]/=pivot;
  for(let i=k+1;i<n;i++){const f=A[i][k];if(!f)continue;for(let j=k;j<=n;j++)A[i][j]-=f*A[k][j];}
 }
 const out=Array(n).fill(0);for(let i=n-1;i>=0;i--){let sum=A[i][n];for(let j=i+1;j<n;j++)sum-=A[i][j]*out[j];out[i]=sum;}
 return out;
}
function bind(id,event,fn){const el=$(id);if(el)el.addEventListener(event,fn);}

// LAB 1: regression to the mean, selection from noisy measurement of latent uniform trait.
let rtmSeed=291101,rtmR=rand(rtmSeed),rtmPeople=[],rtmSelection=[],rtmRepeat=null;
function rtmInitPeople(){rtmR=rand(++rtmSeed);rtmPeople=Array.from({length:500},()=>{const mu=rtmR();return{mu,first:mu+.19*gauss(rtmR)};});rtmRepeat=null;rtmPick();}
function rtmPick(){const top=numeric('rtmTop',10),n=Math.max(1,Math.round(500*top/100));rtmSelection=rtmPeople.map((p,i)=>({i,v:p.first})).sort((a,b)=>b.v-a.v).slice(0,n).map(o=>o.i);rtmRepeat=null;renderRtm();}
function repeatRtm(){rtmRepeat=rtmPeople.map(p=>p.mu+.19*gauss(rtmR));renderRtm();}
function renderRtm(){
  const svg = $('rtmSvg'); if (!svg) return;
  const L = 100, R = 835, T = 55, B = 398, my = y => B - (y + .55) / 2.15 * (B - T), x0 = 215, x1 = 690, set = new Set(rtmSelection);
  let h = axes(L, R, T, B, [], [[-.5, my(-.5)], [0, my(0)], [.5, my(.5)], [1, my(1)], [1.5, my(1.5)]], 'Extreme original values regress toward the center');
  const gPath = (cx, dir) => {
    let pts = [];
    for (let i = 0; i <= 40; i++) {
      const y = -.55 + 2.15 * i / 40, z = (y - .5) / .346, d = Math.exp(-.5 * z * z);
      pts.push(`${(cx + dir * 42 * d).toFixed(1)},${my(y).toFixed(1)}`);
    }
    return `M ${cx},${my(-.55).toFixed(1)} L ` + pts.join(' L ') + ` L ${cx},${my(1.6).toFixed(1)} Z`;
  };
  h += `<path d="${gPath(x0 - 25, -1)}" fill="${C.obs}" fill-opacity=".09" stroke="${C.obs}" stroke-opacity=".25" stroke-width="1.2"/>`;
  h += `<path d="${gPath(x1 + 25, 1)}" fill="${C.obs}" fill-opacity=".09" stroke="${C.obs}" stroke-opacity=".25" stroke-width="1.2"/>`;
  h += label(x0, B + 27, 'Screening', C.ink, 16) + label(x1, B + 27, 'Repeat', C.ink, 16);

  rtmPeople.forEach((p, i) => {
    let y1 = my(clamp(p.first, -.55, 1.6));
    h += `<circle cx="${x0}" cy="${y1}" r="1.8" fill="${C.obs}" fill-opacity=".19"/>`;
    if (rtmRepeat) h += `<circle cx="${x1}" cy="${my(clamp(rtmRepeat[i], -.55, 1.6))}" r="1.8" fill="${C.obs}" fill-opacity=".16"/>`;
  });
  const initial = rtmSelection.map(i => rtmPeople[i].first);
  const after = rtmRepeat ? rtmSelection.map(i => rtmRepeat[i]) : [];
  const cutoff = initial.length ? Math.min(...initial) : 0;
  h += `<line x1="${x0 - 45}" y1="${my(cutoff)}" x2="${x0 + 45}" y2="${my(cutoff)}" stroke="${C.warn}" stroke-width="1.2" stroke-dasharray="4 3" stroke-opacity=".85"/>`;
  h += label(x0 + 48, my(cutoff) + 4, 'Cutoff', C.warn, 10, 'start');
  rtmSelection.forEach(i => {
    const a = my(clamp(rtmPeople[i].first, -.55, 1.6));
    if (rtmRepeat) {
      const b = my(clamp(rtmRepeat[i], -.55, 1.6));
      h += line(x0, a, x1, b, C.warn, 1, .0) + `<circle cx="${x1}" cy="${b}" r="3.4" fill="${C.est}" fill-opacity=".67"/>`;
    }
    h += `<circle cx="${x0}" cy="${a}" r="3.4" fill="${C.warn}" fill-opacity=".88"/>`;
  });
  const mean = v => v.reduce((a, b) => a + b, 0) / v.length;
  let m0 = mean(initial);
  h += line(x0 - 22, my(m0), x0 + 22, my(m0), C.warn, 4);
  if (after.length) h += line(x1 - 22, my(mean(after)), x1 + 22, my(mean(after)), C.est, 4);

  h += label(795, 52, 'Blue: population · Red: selected mean/dots · Green: repeat', C.muted, 12, 'end');
  svg.innerHTML = h;
  text('rtmTopV', numeric('rtmTop')); text('rtmOldMean', m0.toFixed(2)); text('rtmNewMean', after.length ? mean(after).toFixed(2) : 'not repeated'); text('rtmCount', rtmSelection.length);
}

// LAB 2: smoothing: moving average, local polynomial (SG), discrete curvature penalty.
let smSeed=291102,smData=[];
const smTruth=x=>2+.032*x+1.6*Math.sin(x/4.5)+1.5*Math.exp(-.5*((x-25)/4)**2);
function smNew(){const r=rand(++smSeed);smData=Array.from({length:49},(_,i)=>({x:i,truth:smTruth(i),y:smTruth(i)+.73*gauss(r)}));renderSmooth();}
function moving(y,w){const k=(w-1)/2;return y.map((_,i)=>{let sum=0,n=0;for(let j=-k;j<=k;j++){const z=i+j;if(z>=0&&z<y.length){sum+=y[z];n++;}}return sum/n;});}
function sg(y,w,d){const k=(w-1)/2,n=y.length;return y.map((_,i)=>{let idx=Array.from({length:w},(_,q)=>clamp(i-k+q,0,n-1)); // shift window at edges, no duplicated values
 if(i<k)idx=Array.from({length:w},(_,q)=>q);else if(i>n-1-k)idx=Array.from({length:w},(_,q)=>n-w+q);
 const x=idx.map(j=>j-i);const A=Array.from({length:d+1},(_,a)=>Array.from({length:d+1},(_,b)=>x.reduce((s,z)=>s+Math.pow(z,a+b),0)));
 const v=Array.from({length:d+1},(_,a)=>idx.reduce((s,j,h)=>s+y[j]*Math.pow(x[h],a),0));return solve(A,v)[0];});}
function curvatureMatrix(n,lam){const A=Array.from({length:n},(_,i)=>Array.from({length:n},(_,j)=>i===j?1:0));
 for(let k=0;k<n-2;k++){const inds=[k,k+1,k+2],co=[1,-2,1];for(let a=0;a<3;a++)for(let b=0;b<3;b++)A[inds[a]][inds[b]]+=lam*co[a]*co[b];}return A;}
function smoothSpline(y,lam){return solve(curvatureMatrix(y.length,lam),y);}
function gcvChoose(y){let best=Infinity,bestLog=-1;const n=y.length;
 for(let log=-4;log<=3.001;log+=.35){const l=Math.pow(10,log),A=curvatureMatrix(n,l),fit=solve(A,y),rss=fit.reduce((s,v,i)=>s+(y[i]-v)**2,0);let tr=0;
 // trace of smoothing matrix obtained exactly via each diagonal basis solve
 for(let i=0;i<n;i++){const e=Array(n).fill(0);e[i]=1;tr+=solve(A,e)[i];}
 const loss=rss/((n-tr)**2+1e-10);if(loss<best){best=loss;bestLog=log;}}
 return bestLog;
}
function renderSmooth(){const svg=$('smoothSvg');if(!svg||!smData.length)return;const method=$('smMethod').value;
 let w=Math.round(numeric('smWindow',7));if(w%2===0)w++;let d=Math.round(numeric('smDegree',3));d=Math.min(d,w-1);
 const log=numeric('smLambda',-1),lam=Math.pow(10,log),y=smData.map(o=>o.y),truth=smData.map(o=>o.truth);
 let fit=method==='mean'?moving(y,w):method==='sg'?sg(y,w,d):smoothSpline(y,lam);
 const L=65,R=850,T=55,B=380,mx=x=>L+x/48*(R-L),my=v=>B-(v+2)/10*(B-T);let h=axes(L,R,T,B,[[0,mx(0)],[12,mx(12)],[24,mx(24)],[36,mx(36)],[48,mx(48)]],[['0',my(0)],['2',my(2)],['4',my(4)],['6',my(6)]],'Signal recovery · blue samples · orange truth · green smooth','Time index');
 h+=path(truth.map((v,i)=>[mx(i),my(v)]),`fill="none" stroke="${C.model}" stroke-width="2" stroke-dasharray="6 4" opacity=".65"`);
 h+=path(fit.map((v,i)=>[mx(i),my(v)]),`fill="none" stroke="${C.est}" stroke-width="3.5"`);
 for(let i=0;i<smData.length;i++)h+=`<circle cx="${mx(i)}" cy="${my(y[i])}" r="3.7" fill="${C.obs}" fill-opacity=".61"/>`;
 svg.innerHTML=h;for(const id of ['smWindow','smDegree','smLambda'])text(id+'V',numeric(id).toFixed(id==='smLambda'?2:0));
 text('smMethodOut',({mean:'Rolling avg',sg:'Savitzky-Golay',spline:'Spline'}[method]));text('smRmseOut',Math.sqrt(fit.reduce((s,v,i)=>s+(v-truth[i])**2,0)/fit.length).toFixed(2));text('smLambdaOut',method==='spline'?lam.toPrecision(2):'—');
 $('smWindow').disabled=method==='spline';$('smDegree').disabled=method!=='sg';$('smLambda').disabled=method!=='spline';$('smGcv').disabled=method!=='spline';
}

// LAB 3: Fourier magnitude, 2 x axis panels, phases never change magnitude spectrum.
function renderFourier(){const svg=$('fourierSvg');if(!svg)return;
  const vals=[1,2].map(i=>({a:numeric('ftA'+i,i===1?2:1.2),f:numeric('ftF'+i,i===1?3:8),p:numeric('ftP'+i,0)}));
  const n=160,signal=Array.from({length:n},(_,i)=>vals.reduce((s,o)=>s+o.a*Math.sin(2*Math.PI*o.f*i/n+o.p),0)),mags=[];
  for(let k=0;k<=17;k++){let re=0,im=0;for(let i=0;i<n;i++){re+=signal[i]*Math.cos(2*Math.PI*k*i/n);im-=signal[i]*Math.sin(2*Math.PI*k*i/n);}mags.push(2*Math.hypot(re,im)/n);}
  const L=75,R=850,T=55,M=225,T2=278,B=404,mx=i=>L+i/(n-1)*(R-L),my=v=>M-(v+5.5)/11*(M-T),mf=k=>L+k/17*(R-L),mg=v=>B-v/5*(B-T2);let h=axes(L,R,T,B,[],[],'Temporal waveform (top) · Fourier magnitude (bottom)');
  h+=line(L,M,R,M,'#98a2b3',1.5)+line(L,T2,L,B,'#98a2b3',1.3)+line(L,B,R,B,'#98a2b3',1.5);
  h+=path(signal.map((v,i)=>[mx(i),my(v)]),`fill="none" stroke="${C.obs}" stroke-width="3"`);
  mags.forEach((v,k)=>{const x=mf(k),yv=mg(v);h+=line(x,B,x,yv,C.unc,4)+`<circle cx="${x}" cy="${yv}" r="3" fill="${C.unc}"/>`;if(k%2===0)h+=label(x,B+21,k);});
  h+=label(L,T2-10,'Magnitude (phase-independent)',C.unc,13,'start');h+=label(R,450,'Frequency (cycles / window)',C.ink,13,'end');svg.innerHTML=h;
  for(const i of [1,2])for(const t of ['A','F','P'])text('ft'+t+i+'V',numeric('ft'+t+i).toFixed(t==='F'?0:1));
  let ix=1;for(let j=2;j<mags.length;j++)if(mags[j]>mags[ix])ix=j;
  text('ftDom',ix+' cycles');text('ftMag',mags[ix].toFixed(2));
}

// LAB 4: Gaussian process posterior for squared exponential kernel and iid observation noise.
let gpData=[],gpSuggested=null;
const gpTrue=x=>.95*Math.sin(1.35*x)+.35*Math.cos(2.8*x)+.08*(x-5);
const kernel=(a,b,len)=>Math.exp(-.5*((a-b)/len)**2);
function gpPredict(x,len){const n=gpData.length;if(!n)return {mean:0,sd:1};
 const A=gpData.map((o,i)=>gpData.map((v,j)=>kernel(o.x,v.x,len)+(i===j?.0009:0)));
 const k=gpData.map(o=>kernel(o.x,x,len)),w=solve(A,gpData.map(o=>o.y));const sol=solve(A,k);
 const mean=k.reduce((s,v,i)=>s+v*w[i],0),variance=clamp(1-k.reduce((s,v,i)=>s+v*sol[i],0),0,1);return{mean,sd:Math.sqrt(variance)};
}
function renderGp(){const svg=$('gpSvg');if(!svg)return;
 const len=numeric('gpLength',1.2),L=65,R=850,T=50,B=390,mx=x=>L+x/10*(R-L),my=y=>B-(y+2.7)/5.4*(B-T);
 let h=axes(L,R,T,B,[[0,mx(0)],[2,mx(2)],[4,mx(4)],[6,mx(6)],[8,mx(8)],[10,mx(10)]],[[-2,my(-2)],[0,my(0)],[2,my(2)]],'GP posterior mean ± 95% interval · click to sample','Experimental condition');
 const xx=Array.from({length:110},(_,i)=>i*10/109),pd=xx.map(x=>gpPredict(x,len));
 const band=pd.map((v,i)=>[mx(xx[i]),my(v.mean+1.96*v.sd)]).concat(pd.map((v,i)=>[mx(xx[i]),my(v.mean-1.96*v.sd)]).reverse());
 h+=path(band,`fill="${C.unc}" fill-opacity=".17" stroke="none"`);
 h+=path(xx.map(x=>[mx(x),my(gpTrue(x))]),`fill="none" stroke="${C.model}" stroke-width="2" opacity=".55" stroke-dasharray="5 5"`);
 h+=path(pd.map((v,i)=>[mx(xx[i]),my(v.mean)]),`fill="none" stroke="${C.est}" stroke-width="3.2"`);
 gpData.forEach(o=>{h+=`<circle cx="${mx(o.x)}" cy="${my(o.y)}" r="6" fill="${C.obs}" stroke="white" stroke-width="2"/>`;});
 if(gpSuggested!==null){h+=line(mx(gpSuggested),T,mx(gpSuggested),B,C.warn,2.3,'6 4')+label(mx(gpSuggested),T+15,'suggested',C.warn,12);}
 svg.innerHTML=h;text('gpLengthV',len.toFixed(1));text('gpN',gpData.length);text('gpLast',gpData.length?gpData[gpData.length-1].x.toFixed(1):'—');text('gpNext',gpSuggested===null?'—':gpSuggested.toFixed(1));
}
function gpAddAt(x){x=clamp(x,0,10);if(gpData.some(v=>Math.abs(v.x-x)<.10))return;
 const r=rand(Math.round(x*100000)+5521),y=gpTrue(x)+.03*gauss(r);gpData.push({x,y});gpSuggested=null;renderGp();}
function gpSuggest(){const len=numeric('gpLength',1.2),mode=$('gpAcq').value;
 let top=-Infinity,best=0;for(let i=0;i<=120;i++){const x=i/12;if(gpData.some(v=>Math.abs(v.x-x)<.15))continue;
 const p=gpPredict(x,len),score=mode==='ucb'?p.mean+1.5*p.sd:p.sd;
 if(score>top){top=score;best=x;}}
 gpSuggested=best;renderGp();}
function gpPointer(e){const svg=$('gpSvg'),ctm=svg?.getScreenCTM();if(!ctm)return;const p=(typeof DOMPoint!=='undefined'?new DOMPoint(e.clientX,e.clientY):(()=>{const q=svg.createSVGPoint();q.x=e.clientX;q.y=e.clientY;return q;})()).matrixTransform(ctm.inverse());
 if(p.x<65||p.x>850||p.y<50||p.y>390)return;gpAddAt((p.x-65)/(850-65)*10);
}

// LAB 5: stochastic Markov patient and exact population distribution
// const P=[[.91,.08,.01],[.06,.78,.16],[.05,.01,.94]],names=['Susceptible','Infected','Recovered'],cols=[C.obs,C.warn,C.est];
// let mkSeed=7799,mkRandom=rand(mkSeed),mkPath=[0];
// function mkDistribution(day){let a=[1,0,0];for(let d=0;d<day;d++){const b=[0,0,0];for(let i=0;i<3;i++)for(let j=0;j<3;j++)b[j]+=a[i]*P[i][j];a=b;}return a;}
// const mkStable=mkDistribution(600);
// function mkTomorrow(days=1){for(let d=0;d<days;d++){const current=mkPath[mkPath.length-1],u=mkRandom(),row=P[current];mkPath.push(u<row[0]?0:u<row[0]+row[1]?1:2);}renderMarkov();}
// function renderMarkov(){const svg=$('markovSvg');if(!svg)return;let day=mkPath.length-1,dist=mkDistribution(day);
//  let h=axes(65,850,50,390,[],[],'Markov patient history and population probabilities');
//  const x0=105,x1=830,tw=230;
//  for(let i=0;i<3;i++){const y=85+i*87;h+=label(x0,y+15,names[i],cols[i],14,'start');h+=`<rect x="${x0+155}" y="${y-5}" width="${tw}" height="28" rx="5" fill="#f3f6fa"/>`+`<rect x="${x0+155}" y="${y-5}" width="${Math.max(0,tw*dist[i])}" height="28" rx="5" fill="${cols[i]}" fill-opacity=".7"/>`;h+=label(x0+165+tw,y+15,(100*dist[i]).toFixed(1)+'%',C.ink,15,'start');}
//  h+=label(65,370,'Sampled patient path (each square = one day)',C.ink,13,'start');
//  const display=mkPath.slice(-32),step=Math.min(23,(x1-x0)/Math.max(1,display.length));
//  display.forEach((v,i)=>h+=`<rect x="${x0+i*step}" y="386" width="${step-2}" height="17" rx="3" fill="${cols[v]}"/>`);
//  svg.innerHTML=h;text('mkDayOut',day);text('mkState',names[mkPath[mkPath.length-1]]);text('mkStable',(100*mkStable[1]).toFixed(1)+'%');
// }

// LAB 5: stochastic Markov patient and exact population distribution
const P=[[.91,.08,.01],[.06,.78,.16],[.05,.01,.94]],names=['Susceptible','Infected','Recovered'],cols=[C.obs,C.warn,C.est];
let mkSeed=7799,mkRandom=rand(mkSeed),mkPath=[0];

function mkDistribution(day){let a=[1,0,0];for(let d=0;d<day;d++){const b=[0,0,0];for(let i=0;i<3;i++)for(let j=0;j<3;j++)b[j]+=a[i]*P[i][j];a=b;}return a;}
const mkStable=mkDistribution(600);

// ------------------------------------------------------------
// Smooth patient-token animation
// ------------------------------------------------------------

let mkAnimating = false;
let mkQueuedDays = 0;

const MK_MOVE_DURATION = 950;  // milliseconds
const MK_STAY_DURATION = 650;


// Animate token along an SVG motion path
function mkAnimateToken(from, to) {

  return new Promise(resolve => {

    const token = document.getElementById('mkToken');
    const path = document.getElementById(
      `mkMotion_${from}_${to}`
    );

    if (!token || !path) {
      resolve();
      return;
    }

    const totalLength = path.getTotalLength();
    const duration = from === to
      ? MK_STAY_DURATION
      : MK_MOVE_DURATION;

    let startTime = null;

    function frame(now) {

      if (!token.isConnected || !path.isConnected) {
        resolve();
        return;
      }

      if (startTime === null) startTime = now;

      const t = Math.min(
        1,
        (now - startTime) / duration
      );

      // Smooth acceleration/deceleration
      const eased = t * t * (3 - 2 * t);

      const point = path.getPointAtLength(
        totalLength * eased
      );

      token.setAttribute('cx', point.x);
      token.setAttribute('cy', point.y);

      if (t < 1) {
        requestAnimationFrame(frame);
      } else {
        resolve();
      }
    }

    requestAnimationFrame(frame);
  });
}


// ------------------------------------------------------------
// Advance Markov chain, animating every transition
// ------------------------------------------------------------

async function mkTomorrow(days = 1) {

  mkQueuedDays += Math.max(
    0,
    Math.floor(days)
  );

  // If an animation is running, new days are queued.
  if (mkAnimating || mkQueuedDays === 0) return;

  mkAnimating = true;

  try {

    while (mkQueuedDays > 0) {

      mkQueuedDays--;

      const current = mkPath[mkPath.length - 1];
      const u = mkRandom();
      const row = P[current];

      const next =
        u < row[0] ? 0 :
        u < row[0] + row[1] ? 1 : 2;

      // Patient moves before the graph updates
      await mkAnimateToken(current, next);

      // Record arrival at the next state
      mkPath.push(next);

      // Update node highlighting, bars, and history
      renderMarkov();
    }

  } finally {
    mkAnimating = false;
  }
}

function renderMarkov(){
  const svg=$('markovSvg');if(!svg)return;
  let day=mkPath.length-1,dist=mkDistribution(day),currState=mkPath[mkPath.length-1];

  let h=label(450, 25, 'Markov patient state graph (left) · population distribution (right)', C.ink, 14, 'middle');

  // Arrow markers
  h += `<defs>
    <marker id="mkArr"
      viewBox="0 0 10 10"
      refX="7" refY="5"
      markerWidth="6" markerHeight="6"
      orient="auto">
      <path d="M 0 1.5 L 10 5 L 0 8.5 z"
        fill="#64748b"/>
    </marker>
  
    ${cols.map((c, i) => `
      <marker id="mkLoopArr${i}"
        viewBox="0 0 10 10"
        refX="7" refY="5"
        markerWidth="6" markerHeight="6"
        orient="auto">
        <path d="M 0 1.5 L 10 5 L 0 8.5 z"
          fill="${c}"/>
      </marker>
    `).join('')}
  </defs>`;
  
  // ------------------------------------------------------------
  // 1. MARKOV GRAPH TOPOLOGY
  //
  // Equilateral triangle, shifted downward.
  // Side length = 200; vertical height ≈ 173.
  // ------------------------------------------------------------
  
  const nodes = [
    {x: 220, y: 132},  // Susceptible
    {x: 120, y: 305},  // Infected
    {x: 320, y: 305}   // Recovered
  ];
  
  const MK_TOKEN_OFFSET = 16;
  
  
  // ------------------------------------------------------------
  // Directed transitions
  //
  // Each edge has TWO paths:
  // 1. Visible arrow between node boundaries
  // 2. Invisible complete path used for token animation
  //
  // The motion path includes travel from/to the node center.
  // ------------------------------------------------------------
  
  const drawEdge = (i, j, p, offset, tx, ty) => {
  
    if (p <= 0) return;
  
    const n1 = nodes[i];
    const n2 = nodes[j];
  
    const dx = n2.x - n1.x;
    const dy = n2.y - n1.y;
    const len = Math.hypot(dx, dy);
  
    const ux = dx / len;
    const uy = dy / len;
  
    const nx = -uy * offset;
    const ny = ux * offset;
  
    const x1 = n1.x + ux * 30 + nx;
    const y1 = n1.y + uy * 30 + ny;
  
    const x2 = n2.x - ux * 32 + nx;
    const y2 = n2.y - uy * 32 + ny;
  
    const cx = (x1 + x2) / 2 + nx * 1.5;
    const cy = (y1 + y2) / 2 + ny * 1.5;
  
    // Visible transition arrow
    const visiblePath = `
      M ${x1} ${y1}
      Q ${cx} ${cy} ${x2} ${y2}
    `;
  
    h += `<path
      d="${visiblePath}"
      fill="none"
      stroke="#94a3b8"
      stroke-width="1.8"
      stroke-linecap="round"
      marker-end="url(#mkArr)"
    />`;
  
    // Invisible path followed by patient token
    const motionPath = `
      M ${n1.x} ${n1.y + MK_TOKEN_OFFSET}
      L ${x1} ${y1}
      Q ${cx} ${cy} ${x2} ${y2}
      L ${n2.x} ${n2.y + MK_TOKEN_OFFSET}
    `;
  
    h += `<path
      id="mkMotion_${i}_${j}"
      d="${motionPath}"
      fill="none"
      stroke="none"
      pointer-events="none"
    />`;
  
    h += label(
      cx + tx,
      cy + ty,
      p.toFixed(2),
      C.ink,
      11
    );
  };
  
  
  // All six directed transitions
  // Adjust tx (+ move right, - move left) and ty (+ move down, - move up) here:
  drawEdge(0, 1, P[0][1], 12, -14, 0);  // S -> I (0.08)
  drawEdge(1, 0, P[1][0], 12,  5, 0);  // I -> S (0.06)
  
  drawEdge(1, 2, P[1][2], 12,   0, 10); // I -> R (0.16)
  drawEdge(2, 1, P[2][1], 12,   0, 0);// R -> I (0.01)
  
  drawEdge(2, 0, P[2][0], 12,  14, 0);  // R -> S (0.05)
  drawEdge(0, 2, P[0][2], 12, -5, 0);  // S -> R (0.01)
  
  
  // ------------------------------------------------------------
  // Self-loops: positioned OUTSIDE the node circles
  //
  // S: above
  // I: left
  // R: right
  //
  // Loops remain visible regardless of current state.
  // ------------------------------------------------------------
  
  const loopSpecs = [
  
    // Susceptible: upward loop
    {
      i: 0,
      start: [-23, -25],
      c1: [-45, -70],
      c2: [ 45, -70],
      end: [23, -25],
      label: [0, -72]
    },
  
    // Infected: leftward loop
    {
      i: 1,
      start: [-26, -23],
      c1: [-83, -66],
      c2: [-83,  66],
      end: [-26, 23],
      label: [-73, -45]
    },
  
    // Recovered: rightward loop
    {
      i: 2,
      start: [26, 23],
      c1: [83, 66],
      c2: [83, -66],
      end: [26, -23],
      label: [73, -45]
    }
  
  ];
  
  
  loopSpecs.forEach(spec => {
  
    const i = spec.i;
    const n = nodes[i];
  
    const abs = p => [
      n.x + p[0],
      n.y + p[1]
    ];
  
    const s = abs(spec.start);
    const c1 = abs(spec.c1);
    const c2 = abs(spec.c2);
    const e = abs(spec.end);
  
    // Visible dashed self-loop
    const visibleLoop = `
      M ${s[0]} ${s[1]}
      C ${c1[0]} ${c1[1]},
        ${c2[0]} ${c2[1]},
        ${e[0]} ${e[1]}
    `;
  
    h += `<path
      d="${visibleLoop}"
      fill="none"
      stroke="${cols[i]}"
      stroke-width="2"
      stroke-dasharray="5 4"
      stroke-linecap="round"
      marker-end="url(#mkLoopArr${i})"
    />`;
  
    // Invisible motion path for a "stay" transition
    const motionLoop = `
      M ${n.x} ${n.y + MK_TOKEN_OFFSET}
      L ${s[0]} ${s[1]}
      C ${c1[0]} ${c1[1]},
        ${c2[0]} ${c2[1]},
        ${e[0]} ${e[1]}
      L ${n.x} ${n.y + MK_TOKEN_OFFSET}
    `;
  
    h += `<path
      id="mkMotion_${i}_${i}"
      d="${motionLoop}"
      fill="none"
      stroke="none"
      pointer-events="none"
    />`;
  
    h += label(
      n.x + spec.label[0],
      n.y + spec.label[1],
      'stay ' + P[i][i].toFixed(2),
      cols[i],
      11
    );
  
  });
  
  // ------------------------------------------------------------
  // Render state nodes
  // ------------------------------------------------------------
  
  nodes.forEach((n, i) => {
  
    const isCurrent = i === currState;
  
    h += `<circle
      cx="${n.x}"
      cy="${n.y}"
      r="32"
      fill="${isCurrent ? cols[i] : '#ffffff'}"
      fill-opacity="${isCurrent ? 0.25 : 0.95}"
      stroke="${cols[i]}"
      stroke-width="${isCurrent ? 3.5 : 2.2}"
    />`;
  
    h += `<circle
      cx="${n.x}"
      cy="${n.y}"
      r="27"
      fill="none"
      stroke="${cols[i]}"
      stroke-width="1.2"
    />`;
  
    // Slightly raised label to leave room for the token
    h += label(
      n.x,
      n.y - 4,
      names[i],
      cols[i],
      12,
      'middle'
    );
  });
  
  
  // ------------------------------------------------------------
  // Animated patient token
  //
  // Positioned slightly below the node label at rest.
  // It travels along the SVG motion paths.
  // ------------------------------------------------------------
  
  const activePos = nodes[currState];
  
  h += `<circle
    id="mkToken"
    cx="${activePos.x}"
    cy="${activePos.y + MK_TOKEN_OFFSET}"
    r="7.5"
    fill="#0f172a"
    stroke="#ffffff"
    stroke-width="2.5"
    pointer-events="none"
  />`;
  
  // 2. POPULATION STATE BARS (Right Side: x in [480, 850])
  const bx0=480,tw=220;
  for(let i=0;i<3;i++){
    const y=90+i*80;
    h+=label(bx0,y+15,names[i],cols[i],14,'start');
    h+=`<rect x="${bx0+110}" y="${y-5}" width="${tw}" height="26" rx="5" fill="#f3f6fa"/>`
      +`<rect x="${bx0+110}" y="${y-5}" width="${Math.max(0,tw*dist[i])}" height="26" rx="5" fill="${cols[i]}" fill-opacity=".75"/>`;
    h+=label(bx0+120+tw,y+15,(100*dist[i]).toFixed(1)+'%',C.ink,14,'start');
  }

  // 3. PATIENT STEP HISTORY (Bottom: y = 386)
  const x0=105,x1=830;
  h+=label(65,368,'Sampled patient path (each square = one day)',C.ink,12,'start');
  const display=mkPath.slice(-32),step=Math.min(23,(x1-x0)/Math.max(1,display.length));
  display.forEach((v,i)=>h+=`<rect x="${x0+i*step}" y="384" width="${step-2}" height="17" rx="3" fill="${cols[v]}"/>`);

  svg.innerHTML=h;
  text('mkDayOut',day);text('mkState',names[currState]);text('mkStable',(100*mkStable[1]).toFixed(1)+'%');
}

// LAB 6: minimal offline Markov word-chain (not corpus-derived)
const toyLines=[
 'the soft night holds the silver stars','the silent river follows the moon',
 'the green river hears the distant rain','the stars rest above the sleeping garden',
 'a soft wind crosses the open field','night draws a curtain over the river',
 'the distant hills remember summer light','soft shadows follow quiet footsteps',
 'river water gathers beneath the moon','the night folds around the quiet stars',
 'stars in the river move with the tide','the wind whispers through the silver trees',
 'soft light returns beyond the hills','the river carries echoes of the night',
 'green leaves sway when the wind wakes','the sleeping garden waits for morning light'
];
const trans={};for(const sentence of toyLines){const tok=sentence.split(' ');for(let i=0;i<tok.length-1;i++){(trans[tok[i]]??=[]).push(tok[i+1]);}}
let wordSeed=11,wordHistory=[];
function generateWords(){const r=rand(++wordSeed);let w=$('wordStart').value;let out=[w];for(let i=0;i<22;i++){
 const options=trans[w]||trans.the;w=options[Math.floor(r()*options.length)];out.push(w);}
 wordHistory=out;renderWord();}
function renderWord(){const svg=$('wordSvg');if(!svg)return;const w=wordHistory[0]||$('wordStart')?.value||'the';const arr=trans[w]||[],counts={};arr.forEach(v=>counts[v]=(counts[v]||0)+1);const sorted=Object.entries(counts).sort((a,b)=>b[1]-a[1]).slice(0,8);
 let h=axes(75,850,45,391,[],[],'Possible next words after “'+w+'”');
 sorted.forEach(([word,n],i)=>{const y=74+i*40;h+=label(95,y+14,word,C.ink,15,'start');h+=`<rect x="295" y="${y}" width="${455*n/arr.length}" height="22" rx="5" fill="${C.unc}" fill-opacity=".7"/>`;h+=label(775,y+15,(100*n/arr.length).toFixed(0)+'%',C.muted,13,'end');});
 svg.innerHTML=h;text('wordTokens',wordHistory.length||0);text('wordUnique',new Set(wordHistory).size);text('wordText',wordHistory.length?wordHistory.join(' ')+'.':'Generate a short synthetic, locally coherent word chain.');
}

const correct={
 '1':['A','Six repeated readings from one patient are not six independent patients.'],
 '2':['B','The patient contributes information while observed, then is right censored at month 6.'],
 '3':['A','An HR is a relative instantaneous hazard under the model, not a risk ratio.'],
 '4':['B','GP uncertainty typically contracts near new observations, depending on the covariance kernel.']
};
function quizAnswer(button){const quiz=button.closest('.w11-quiz'),q=correct[quiz?.dataset.q];if(!q)return;
 const okay=button.dataset.choice===q[0];quiz.querySelectorAll('.w11-choice').forEach(b=>b.classList.remove('correct','wrong'));
 button.classList.add(okay?'correct':'wrong');const f=quiz.querySelector('.w11-feedback');f.className='w11-feedback '+(okay?'correct':'wrong');f.textContent=(okay?'Correct. ':'Not quite. ')+q[1];}
let initialized=false;
function init(){if(initialized||!$('rtmWidget'))return;initialized=true;
 bind('rtmTop','input',rtmPick);bind('rtmResample','click',repeatRtm);bind('rtmNew','click',rtmInitPeople);bind('rtmReset','click',()=>{rtmRepeat=null;renderRtm();});
 for(const id of ['smMethod','smWindow','smDegree','smLambda'])bind(id,id==='smMethod'?'change':'input',renderSmooth);
 bind('smNew','click',smNew);bind('smGcv','click',()=>{if($('smMethod').value!=='spline')return;let best=gcvChoose(smData.map(v=>v.y));$('smLambda').value=best;renderSmooth();});
 for(const id of ['ftA1','ftA2','ftF1','ftF2','ftP1','ftP2'])bind(id,'input',renderFourier);
 bind('gpLength','input',()=>{gpSuggested=null;renderGp();});bind('gpAcq','change',()=>{gpSuggested=null;renderGp();});bind('gpSvg','click',gpPointer);
 bind('gpSuggest','click',gpSuggest);bind('gpReset','click',()=>{gpData=[];gpSuggested=null;renderGp();});
 bind('mkDay','click',()=>mkTomorrow(1));bind('mkTen','click',()=>mkTomorrow(10));bind('mkReset','click',()=>{mkPath=[0];mkRandom=rand(++mkSeed);renderMarkov();});
 bind('wordGenerate','click',generateWords);bind('wordReset','click',()=>{wordHistory=[];renderWord();});bind('wordStart','change',renderWord);
 document.querySelectorAll('.w11-choice').forEach(b=>b.addEventListener('click',()=>quizAnswer(b)));
 rtmInitPeople();smNew();renderFourier();renderGp();renderMarkov();renderWord();
}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',init);else init();
window.addEventListener('load',init);
if(window.Reveal?.on){window.Reveal.on('ready',init);window.Reveal.on('slidechanged',init);}
})();
