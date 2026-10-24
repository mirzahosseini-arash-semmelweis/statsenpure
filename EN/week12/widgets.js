/* Week 12 · fully offline, dependency-free classroom widgets.
 * Statistical examples synthetic except the locally trained digit model.
 */
(()=>{'use strict';
const $=id=>document.getElementById(id), DATA=window.W12_DATA||{};
const C={blue:'#1f6feb',orange:'#c65d09',green:'#18864b',red:'#c93838',purple:'#7b4ab5',grey:'#667085',navy:'#182230',line:'#d9e1ea'};
const svgTxt=(x,y,t,cls='w12-tick',anchor='middle')=>`<text x="${x}" y="${y}" text-anchor="${anchor}" class="${cls}">${t}</text>`;
const axis=(x1,y1,x2,y2,cls='w12-axis')=>`<line x1="${x1}" y1="${y1}" x2="${x2}" y2="${y2}" class="${cls}"/>`;
const dot=(x,y,r,col,opacity=1)=>`<circle cx="${x.toFixed(1)}" cy="${y.toFixed(1)}" r="${r}" fill="${col}" opacity="${opacity}"/>`;
const esc=s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;');
const clamp=(x,a,b)=>Math.max(a,Math.min(b,x));
function once(id,ev,fn){const el=$(id);if(!el)return;const key=`w12${ev}`;if(el.dataset[key])return;el.dataset[key]='1';el.addEventListener(ev,fn)}
function val(id,d=0){const x=Number($(id)?.value);return Number.isFinite(x)?x:d}
function upd(id,v){if($(id))$(id).textContent=String(v)}
function fmt(x,d=2){return Number(x).toFixed(d)}
function bounds(v){let a=Math.min(...v),b=Math.max(...v);const g=Math.max(.05,(b-a)*.10);return[a-g,b+g]}
function coords(svg,e){const mat=svg.getScreenCTM();if(!mat)return null;const p=svg.createSVGPoint();p.x=e.clientX;p.y=e.clientY;return p.matrixTransform(mat.inverse())}
const normalize=(x,lo,hi,L,R)=>L+(x-lo)/(hi-lo)*(R-L);

// ------------ Rotatable bivariate density -----------------
let gaussYaw=.63,gaussPitch=.56,gaussPointer=null;
function g3(x,y,z){const a=gaussYaw,b=gaussPitch;const xx=Math.cos(a)*x-Math.sin(a)*y, yy=Math.sin(a)*x+Math.cos(a)*y;
 return [460+xx*80,320+yy*45*Math.sin(b)-z*170*Math.cos(b)]}
function gaussianDens(x,y,mode){if(mode==='mixture')return .53*Math.exp(-.5*((x+1.1)**2/.65**2+(y+.5)**2/.7**2))+.43*Math.exp(-.5*((x-1.25)**2/.75**2+(y-1.)**2/.57**2));
 const sx=val('gaussSx',1.3),sy=val('gaussSy',.9),rho=val('gaussRho',.45),u=x/sx,v=y/sy;return Math.exp(-.5*(u*u-2*rho*u*v+v*v)/(1-rho*rho));}
function gaussian(){const svg=$('gaussSvg');if(!svg)return;const mode=$('gaussMode').value;for(const id of ['gaussSx','gaussSy','gaussRho'])$(id).disabled=mode==='mixture';
 ['gaussSx','gaussSy','gaussRho'].forEach((id,i)=>upd(id+'Val',fmt(val(id,[1.3,.9,.45][i]),2)));
 const n=29,grid=[],faces=[];for(let j=0;j<=n;j++){const row=[];for(let i=0;i<=n;i++){const x=-3.2+i*6.4/n,y=-3.2+j*6.4/n,z=gaussianDens(x,y,mode)*2.6;row.push(g3(x,y,z));}grid.push(row)}
 for(let j=0;j<n;j++)for(let i=0;i<n;i++){const v=[grid[j][i],grid[j][i+1],grid[j+1][i+1],grid[j+1][i]];const depth=(i+j)*Math.sin(gaussYaw)+j*Math.cos(gaussYaw);const xx=-3.2+(i+.5)*6.4/n,yy=-3.2+(j+.5)*6.4/n;const d=gaussianDens(xx,yy,mode);faces.push({depth,s:`<polygon points="${v.map(p=>p.map(x=>x.toFixed(1)).join(',')).join(' ')}" fill="hsl(${258-35*Math.min(1,d)}, 55%, ${91-42*Math.min(1,d)}%)" stroke="rgba(110,70,155,.24)" stroke-width=".65"/>`})}
 faces.sort((a,b)=>a.depth-b.depth);let h=faces.map(f=>f.s).join('');
 for(const [a,b] of [[[-3.2,-3.2,0],[3.2,-3.2,0]],[[-3.2,-3.2,0],[-3.2,3.2,0]],[[-3.2,-3.2,0],[-3.2,-3.2,2.6]]]){const u=g3(...a),v=g3(...b);h+=axis(u[0],u[1],v[0],v[1])}
 h+=svgTxt(480,30,mode==='mixture'?'Two latent groups · Gaussian mixture':'One correlated bivariate Normal', 'w12-title');h+=svgTxt(470,460,'Drag the surface to rotate · variation and covariance reshape the density');svg.innerHTML=h;drawGaussScatter()}
function initGauss(){if(!$('gaussSvg'))return;for(const id of ['gaussSx','gaussSy','gaussRho','gaussMode'])once(id,id==='gaussMode'?'change':'input',gaussian);
 once('gaussSvg','pointerdown',e=>{e.preventDefault();gaussPointer=[e.clientX,e.clientY];$('gaussSvg').setPointerCapture(e.pointerId)});
 once('gaussSvg','pointermove',e=>{if(!gaussPointer)return;gaussYaw+=.009*(e.clientX-gaussPointer[0]);gaussPitch=clamp(gaussPitch-.006*(e.clientY-gaussPointer[1]),.05,1.3);gaussPointer=[e.clientX,e.clientY];gaussian()});
 once('gaussSvg','pointerup',()=>gaussPointer=null);once('gaussSvg','pointercancel',()=>gaussPointer=null);once('gaussSvg','lostpointercapture',()=>gaussPointer=null);gaussian()}


// 200 persistent standard-Normal draws, seeded once: sliders change the SAME sample.
const gaussSamples=(()=>{
 let seed=12931;
 const unif=()=>{seed=(1664525*seed+1013904223)>>>0;return(seed+.5)/4294967296};
 return Array.from({length:200},()=>{
  const r=Math.sqrt(-2*Math.log(Math.max(1e-12,unif()))),a=2*Math.PI*unif();
  return {z1:r*Math.cos(a),z2:r*Math.sin(a),first:unif()<.53/(.53+.43)};
 });
})();

// Contours and sampled points use the SAME bivariate model as the surface.
// Azimuth rotates both views; pitch affects only the 3D view.
function drawGaussScatter(){
 const svg=$('gaussScatterSvg');if(!svg)return;
 const mode=$('gaussMode').value;
 const sx=val('gaussSx',1.3),sy=val('gaussSy',.9),rho=val('gaussRho',.45);
 const co=Math.cos(gaussYaw),si=Math.sin(gaussYaw);
 const xy=(x,y)=>[450+37*(co*x-si*y),145-37*(si*x+co*y)];
 const project=p=>`${p[0].toFixed(1)},${p[1].toFixed(1)}`;

 let html=`<defs><clipPath id="w12GaussMapClip"><rect x="175" y="10" width="550" height="270"/></clipPath></defs>`;
 // Keep axes and density/data together in the camera-aligned plan view.
 html+='<g clip-path="url(#w12GaussMapClip)">';
 const x0=xy(-3.4,0),x1=xy(3.4,0),y0=xy(0,-3.4),y1=xy(0,3.4);
 html+=axis(...x0,...x1,'w12-gauss-map-axis')+axis(...y0,...y1,'w12-gauss-map-axis');

 // Actual iso-density curves (marching squares), including for the mixture.
 const n=52,min=-3.35,max=3.35,step=(max-min)/n;
 const xvals=Array.from({length:n+1},(_,i)=>min+i*step);
 const dens=xvals.map(y=>xvals.map(x=>gaussianDens(x,y,mode)));
 const levels=mode==='mixture'?[.10,.19,.29,.40]:[.16,.32,.52,.73];
 for(let k=0;k<levels.length;k++){
  const lev=levels[k];let path='';
  for(let j=0;j<n;j++)for(let i=0;i<n;i++){
   const x=xvals[i],y=xvals[j];
   const v=[
    [x,y,dens[j][i]],
    [x+step,y,dens[j][i+1]],
    [x+step,y+step,dens[j+1][i+1]],
    [x,y+step,dens[j+1][i]]
   ];
   const hits=[];
   for(let e=0;e<4;e++){
    const a=v[e],b=v[(e+1)%4];
    if((a[2]<lev)!==(b[2]<lev)){
     const t=(lev-a[2])/(b[2]-a[2]);
     hits.push(xy(a[0]+t*(b[0]-a[0]),a[1]+t*(b[1]-a[1])));
    }
   }
   for(let h=0;h+1<hits.length;h+=2){
    path+=`M${project(hits[h])} L${project(hits[h+1])} `;
   }
  }
  html+=`<path d="${path}" fill="none" stroke="${C.purple}" stroke-width="${1.5+k*.35}" stroke-opacity="${.42+k*.13}"/>`;
 }

 // Use the fixed latent draws so camera drags do not randomly regenerate dots.
 const qr=Math.sqrt(1-rho*rho);
 for(const z of gaussSamples){
  let x,y;
  if(mode==='mixture'){
   if(z.first){x=-1.1+.65*z.z1;y=-.5+.70*z.z2;}
   else{x=1.25+.75*z.z1;y=1.0+.57*z.z2;}
  }else{
   x=sx*z.z1;
   y=sy*(rho*z.z1+qr*z.z2);
  }
  const p=xy(x,y);
  html+=dot(p[0],p[1],3.1,C.blue,.56);
 }
 html+='</g>';
 const xl=xy(3.7,0),yl=xy(0,3.7);
 html+=svgTxt(xl[0],xl[1],'X','w12-gauss-map-axislabel');
 html+=svgTxt(yl[0],yl[1],'Y','w12-gauss-map-axislabel');
 html+=svgTxt(22,38,`n = ${gaussSamples.length}`,'w12-gauss-map-note','start');
 html+=svgTxt(22,60,mode==='mixture'?'Two latent groups':'Correlated Normal','w12-gauss-map-note','start');
 html+=svgTxt(877,38,'Purple: contours','w12-gauss-map-note','end');
 html+=svgTxt(877,60,'Blue: sample','w12-gauss-map-note','end');
 svg.innerHTML=html;
}

// ------------ PCA 3D projection lab (replacement block) -----------
let pcaYaw = .65, pcaPitch = .5, pcaActive = false, pcaDrag = null;

// Coordinates are expressed in the true PC1, PC2, PC3 basis.
// This preserves the cloud's position when switching from PCA view to dragging.
function pcaXY(p) {
  const ca = Math.cos(pcaYaw), sa = Math.sin(pcaYaw);
  const projectedX = ca*p[0] - sa*p[1];
  const projectedY = Math.sin(pcaPitch)*(sa*p[0] + ca*p[1]) - Math.cos(pcaPitch)*p[2];
  return [450 + projectedX*80, 255 - projectedY*80];
}

// Fraction of the sample's total 3D variance retained by this screen plane.
function pcaRetainedVariance(points) {
  const mean = [0, 0, 0];
  for (const p of points) for (let k=0; k<3; k++) mean[k] += p[k]/points.length;
  const ca=Math.cos(pcaYaw), sa=Math.sin(pcaYaw), sb=Math.sin(pcaPitch), cb=Math.cos(pcaPitch);
  let retained=0, total=0;
  for (const p of points) {
    const x=p[0]-mean[0], y=p[1]-mean[1], z=p[2]-mean[2];
    const u=ca*x-sa*y;
    const v=sb*(sa*x+ca*y)-cb*z;
    retained += u*u+v*v;
    total += x*x+y*y+z*z;
  }
  return total > 0 ? retained / total : 0;
}

function pcRender() {
  const svg=$('pcaSvg');
  if (!svg || !DATA.pca) return;
  const dat=DATA.pca;

  // Principal-component coordinates are used in BOTH modes.
  // No point-cloud jump when leaving PCA view to drag the scene.
  const pcPoints=dat.points.map(p => dat.axes.map(a =>
    a[0]*p[0]+a[1]*p[1]+a[2]*p[2]));
  const retained=pcaRetainedVariance(pcPoints);

  let h=`<defs><clipPath id="w12PcaClip"><rect x="30" y="63" width="840" height="380"/></clipPath></defs>`;
  h+=svgTxt(450,35,
    pcaActive?'PCA plane · optimal two-dimensional projection':'Drag to rotate · seek maximum retained variance',
    'w12-title');

  // The grid lives on the *actual* PC1-PC2 plane (PC3 = 0),
  // not on the camera's arbitrary 2D screen plane.
  h+='<g clip-path="url(#w12PcaClip)">';
  for (let j=-5;j<=5;j++) {
    const c=j*.5;
    const a=pcaXY([c,-2.5,0]), b=pcaXY([c,2.5,0]);
    const d=pcaXY([-2.5,c,0]), e=pcaXY([2.5,c,0]);
    h+=`<line x1="${a[0]}" y1="${a[1]}" x2="${b[0]}" y2="${b[1]}" class="w12-pca-grid"/>`;
    h+=`<line x1="${d[0]}" y1="${d[1]}" x2="${e[0]}" y2="${e[1]}" class="w12-pca-grid"/>`;
  }
  const origin=pcaXY([0,0,0]);
  const pc1=pcaXY([2.5,0,0]), pc2=pcaXY([0,2.5,0]);
  h+=axis(...pcaXY([-2.5,0,0]),...pc1,'w12-pca-axis');
  h+=axis(...pcaXY([0,-2.5,0]),...pc2,'w12-pca-axis');

  // Variable axes: a one-unit original variable axis (Hb, age, weight)
  // expressed in PC coordinates. All three rotate together with the cloud.
  const colors=[C.orange,C.purple,C.green];
  dat.labels.forEach((name,j)=>{
    const v=dat.axes.map(a=>a[j]*2.35);
    const tip=pcaXY(v);
    const dx=tip[0]-origin[0], dy=tip[1]-origin[1];
    const len=Math.hypot(dx,dy)||1;
    const nx=dx/len, ny=dy/len, px=-ny, py=nx;
    const arrowEnd=[tip[0]-10*nx,tip[1]-10*ny];
    h+=`<line x1="${origin[0]}" y1="${origin[1]}" x2="${arrowEnd[0]}" y2="${arrowEnd[1]}" stroke="${colors[j]}" stroke-width="3.6" stroke-linecap="round"/>`;
    h+=`<polygon points="${tip[0]},${tip[1]} ${tip[0]-14*nx+5*px},${tip[1]-14*ny+5*py} ${tip[0]-14*nx-5*px},${tip[1]-14*ny-5*py}" fill="${colors[j]}"/>`;
  });

  // Points are plotted after the grid so their blue color stays readable.
  pcPoints.forEach(p=>{const q=pcaXY(p);h+=dot(q[0],q[1],3.7,C.blue,.57)});
  h+='</g>';

  // Axis labels outside clipped grid; colored variable labels on top.
  h+=svgTxt(clamp(pc1[0]+11,45,856),clamp(pc1[1]-9,69,434),'PC1','w12-pca-pc','start');
  h+=svgTxt(clamp(pc2[0]+46,45,856),clamp(pc2[1]-9,69,434),'PC2','w12-pca-pc','start');

  dat.labels.forEach((name,j)=>{
    const v=dat.axes.map(a=>a[j]*2.35), tip=pcaXY(v);
    const dx=tip[0]-origin[0],dy=tip[1]-origin[1],len=Math.hypot(dx,dy)||1;
    const x=clamp(tip[0]+14*dx/len,58,842);
    const y=clamp(tip[1]+14*dy/len,75,432);
    const color=colors[j];
    h+=`<text x="${x.toFixed(1)}" y="${y.toFixed(1)}" text-anchor="middle" class="w12-pca-variable" fill="${color}">${name}</text>`;
  });

  h+=svgTxt(450,467,
    pcaActive?'PC1 + PC2 plane · maximum retained variance':'The projected variance changes as you rotate the cloud',
    'w12-small');
  svg.innerHTML=h;
  upd('pcaVar',fmt(100*(pcaActive?dat.variance[0]+dat.variance[1]:retained),1)+'%');
  upd('pcaPlane',pcaActive?'PCA principal plane':'Custom viewpoint');
}

function initPCA() {
  const svg=$('pcaSvg');if(!svg)return;
  once('pcaShow','click',()=>{
    pcaActive=true;
    pcaYaw=0;
    pcaPitch=Math.PI/2;  // look straight down onto PC1 and PC2
    pcRender();
  });
  once('pcaReset','click',()=>{
    pcaActive=false;
    pcaYaw=.65;
    pcaPitch=.5;
    pcRender();
  });
  once('pcaSvg','pointerdown',e=>{
    e.preventDefault();   // prevent selection of text while dragging
    pcaDrag=[e.clientX,e.clientY];
    svg.setPointerCapture(e.pointerId);
  });
  once('pcaSvg','pointermove',e=>{
    if(!pcaDrag)return;
    const dx=e.clientX-pcaDrag[0],dy=e.clientY-pcaDrag[1];
    if(dx!==0||dy!==0) {
      pcaActive=false;
      pcaYaw+=.009*dx;
      pcaPitch=clamp(pcaPitch-.007*dy,.05,Math.PI/2);
      pcRender();
    }
    pcaDrag=[e.clientX,e.clientY];
  });
  once('pcaSvg','pointerup',e=>{
    pcaDrag=null;
    if(svg.hasPointerCapture?.(e.pointerId))svg.releasePointerCapture(e.pointerId);
  });
  once('pcaSvg','pointercancel',()=>{pcaDrag=null});
  pcRender();
}

// ------------ Rotatable PAIR mammoth + offline UMAP embeddings ------------
// Replaces ONLY the old nonlinear() and initNonlin() functions.
// Data: mammoth_umap_data.js, bundled alongside data.js and widgets.js.
// This fragment belongs INSIDE the existing Week 12 widgets.js IIFE.
let mammothYaw = -0.07;
let mammothPitch = 0.16;
let mammothPointer = null;
let mammothColors = null;
let mammothFrame = 0;

function mammothRamp(v) {
  // A color-blind-conscious gradient: same original 3D point, same color in 2D.
  const ramp = ['#414487', '#2a788e', '#22a884', '#7ad151', '#dce319'];
  let p = Math.max(0, Math.min(.999999, v)) * (ramp.length - 1);
  let i = Math.floor(p), f = p - i;
  const aa = ramp[i].slice(1), bb = ramp[i + 1].slice(1);
  const rgb = [0, 2, 4].map(j => {
    const a = parseInt(aa.slice(j, j + 2), 16);
    const b = parseInt(bb.slice(j, j + 2), 16);
    return Math.round(a + (b - a) * f).toString(16).padStart(2, '0');
  });
  return '#' + rgb.join('');
}

function mammothProject(p) {
  const ca = Math.cos(mammothYaw), sa = Math.sin(mammothYaw);
  const cb = Math.cos(mammothPitch), sb = Math.sin(mammothPitch);
  const xr = ca * p[0] - sa * p[1];
  const yr = sa * p[0] + ca * p[1];
  return [228 + 110 * xr,
          245 - 110 * (cb * yr - sb * p[2]),
          sb * yr + cb * p[2]];
}

const MAMMOTH_PART_COLORS = [
  '#E98F30', // 0 Tusks — orange
  '#CE5F7D', // 1 Head — pink
  '#4595C2', // 2 Torso — blue
  '#7B4AB5', // 3 Front legs — purple
  '#1A927F', // 4 Hind legs — teal
  '#89A33C'  // 5 Pelvis — olive
];

function mammothPart(p) {
  const [x, y, z] = p;

  if (x < -1.04)
    return 0; // Tusks

  if (x < -0.57 && y >= -0.55)
    return 1; // Head

  if (y < -0.70)
    return x < 0.30 ? 3 : 4; // Front / hind legs

  if (x > 0.60)
    return 5; // Pelvis

  return 2; // Torso
}

function mammothRender3D() {
  const data = window.W12_MAMMOTH;
  const group = $('mammoth3DPoints');
  if (!group || !data) return;
  const pts = data.xyz.map((v, i) => ({q: mammothProject(v), i}));
  // Orthographic depth-sort: draw distant points behind near ones.
  pts.sort((a, b) => a.q[2] - b.q[2]);
  group.innerHTML = pts.map(({q, i}) =>
    `<circle cx="${q[0].toFixed(2)}" cy="${q[1].toFixed(2)}" r="2.75" fill="${mammothColors[i]}" fill-opacity=".88"/>`
  ).join('');
}

function mammothRenderUMAP() {
  const data = window.W12_MAMMOTH;
  const group = $('mammothUMAPPoints');
  if (!data || !group) return;
  const k = $('nonlinK').value;
  const points = data.umap[k];
  if (!points) return;

  const xa = points.map(p => p[0]), ya = points.map(p => p[1]);
  const cx = (Math.min(...xa) + Math.max(...xa)) / 2;
  const cy = (Math.min(...ya) + Math.max(...ya)) / 2;
  // One common scale for horizontal and vertical = no distorted geometries.
  const scale = Math.min(371 / Math.max(...xa.map(x=>Math.abs(x-cx)))/2,
                         300 / Math.max(...ya.map(y=>Math.abs(y-cy)))/2);

  group.innerHTML = points.map((v, i) => {
    const x = 675 + scale * (v[0] - cx);
    const y = 242 - scale * (v[1] - cy);
    return `<circle cx="${x.toFixed(2)}" cy="${y.toFixed(2)}" r="2.75" fill="${mammothColors[i]}" fill-opacity=".91"/>`;
  }).join('');

  const title = $('mammothUMAPTitle');
  if (title) title.textContent = `UMAP projection · neighbors = ${k}`;
  upd('nonlinKVal', k); // harmless if no optional readout exists
}

function nonlinear() {
  const svg = $('nonlinearSvg'), data = window.W12_MAMMOTH;
  if (!svg || !data) return;
  if (!mammothColors)
    mammothColors = data.xyz.map(
      p => MAMMOTH_PART_COLORS[mammothPart(p)]
    );

  // Rebuild only when a missing panel must be added. On rotation,
  // only the left <g> is repainted; on dropdown changes, only the right.
  if (!$('mammoth3DPoints')) {
    svg.innerHTML = `
      <defs>
        <clipPath id="mammoth3DClip"><rect x="25" y="61" width="415" height="348" rx="14"/></clipPath>
        <clipPath id="mammothUMAPClip"><rect x="463" y="61" width="410" height="348" rx="14"/></clipPath>
      </defs>
      <rect x="20" y="58" width="425" height="354" rx="15" fill="#fbfcfe" stroke="#d9e1ea" stroke-width="1.6"/>
      <rect x="457" y="58" width="423" height="354" rx="15" fill="#fbfcfe" stroke="#d9e1ea" stroke-width="1.6"/>
      <text x="228" y="32" text-anchor="middle" class="w12-title">3D mammoth · drag to rotate</text>
      <text id="mammothUMAPTitle" x="670" y="32" text-anchor="middle" class="w12-title">UMAP projection</text>
      <g clip-path="url(#mammoth3DClip)" id="mammoth3DPoints"></g>
      <g clip-path="url(#mammothUMAPClip)" id="mammothUMAPPoints"></g>
      <text x="228" y="445" text-anchor="middle" class="w12-small">Original 3D coordinates</text>
      <text x="670" y="445" text-anchor="middle" class="w12-small">Same 1,250 points · min_dist = 0.25</text>
    `;
  }
  mammothRender3D();
  mammothRenderUMAP();
}

function initNonlin() {
  const svg = $('nonlinearSvg');
  if (!svg || !window.W12_MAMMOTH) return;
  nonlinear();

  once('nonlinK', 'change', mammothRenderUMAP);
  once('nonlinearSvg', 'pointerdown', e => {
    if (e.pointerType === 'mouse' && e.button !== 0) return;
    const p = coords(svg, e); // existing SVG-accurate pointer helper
    if (!p || p.x < 24 || p.x > 445 || p.y < 58 || p.y > 413) return;
    e.preventDefault();
    mammothPointer = [e.clientX, e.clientY];
    svg.setPointerCapture(e.pointerId);
  });
  once('nonlinearSvg', 'pointermove', e => {
    if (!mammothPointer) return;
    e.preventDefault();
    const dx = e.clientX - mammothPointer[0];
    const dy = e.clientY - mammothPointer[1];
    mammothPointer = [e.clientX, e.clientY];
    mammothYaw += .008 * dx;
    mammothPitch = clamp(mammothPitch + .007 * dy, -1.37, 1.37);
    if (!mammothFrame) {
      mammothFrame = requestAnimationFrame(() => {
        mammothFrame = 0;
        mammothRender3D();
      });
    }
  });
  const end = () => { mammothPointer = null; };
  once('nonlinearSvg', 'pointerup', end);
  once('nonlinearSvg', 'pointercancel', end);
  once('nonlinearSvg', 'lostpointercapture', end);
}

// ------------ Cluster visualizer --------------------------
function clust(){const svg=$('clusterSvg');if(!svg||!DATA.clusters)return;const shape=$('clusterShape').value,m=$('clusterMethod').value,k=+$('clusterK').value,eps=$('clusterEps').value;const dat=DATA.clusters[shape];const labs=dat.labels[m==='dbscan'?'dbscan'+eps:m+k],col=[C.blue,C.orange,C.green,C.purple,C.red,'#18a0a6'];let h=axis(75,410,850,410)+axis(75,55,75,410);const X=dat.points;let Xmin=Math.min(...X.map(p=>p[0])),Xmax=Math.max(...X.map(p=>p[0])),Ymin=Math.min(...X.map(p=>p[1])),Ymax=Math.max(...X.map(p=>p[1]));const xb=bounds([Xmin,Xmax]),yb=bounds([Ymin,Ymax]);const xy=X.map(p=>[normalize(p[0],...xb,88,837),normalize(p[1],...yb,392,78)]);
 let uniq=[...new Set(labs)].filter(q=>q>=0);for(const id of uniq){const gp=xy.filter((_,i)=>labs[i]===id);if(gp.length<3)continue;const minx=Math.min(...gp.map(p=>p[0])),maxx=Math.max(...gp.map(p=>p[0])),miny=Math.min(...gp.map(p=>p[1])),maxy=Math.max(...gp.map(p=>p[1]));h+=`<ellipse cx="${(minx+maxx)/2}" cy="${(miny+maxy)/2}" rx="${(maxx-minx)/2+9}" ry="${(maxy-miny)/2+8}" fill="none" stroke="${col[id%col.length]}" stroke-width="2" stroke-opacity=".4"/>`}
 xy.forEach((p,i)=>h+=dot(...p,4,labs[i]<0?C.grey:col[labs[i]%col.length],labs[i]<0?.35:.73));h+=svgTxt(450,35,`${m.toUpperCase()} · ${uniq.length} clusters${labs.includes(-1)?' · noise marked gray':''}`,'w12-title');svg.innerHTML=h;upd('clusterNum',uniq.length);upd('clusterNoise',labs.filter(q=>q<0).length);$('clusterK').disabled=m==='dbscan';$('clusterEps').disabled=m!=='dbscan';upd('clusterKVal',k)}
function initClust(){if(!$('clusterSvg'))return;for(const id of ['clusterShape','clusterMethod','clusterK','clusterEps'])once(id,id==='clusterK'||id==='clusterEps'?'input':'change',clust);clust()}

// ------------ PCA vs LDA · shared 3D point cloud ----------------------
// Educational labels, NOT medical diagnoses: class 1 = PC3 score >= 0.
// Fit a genuine two-class Fisher LDA on these synthetic labels.
// For two classes LDA supplies only LD1; the second displayed axis is
// an orthogonal, unsupervised companion direction (roughly PC1).
let pcaldaState = null;
const pcaldaDot=(a,b)=>a.reduce((s,x,i)=>s+x*b[i],0);
const pcaldaCross=(a,b)=>[a[1]*b[2]-a[2]*b[1],a[2]*b[0]-a[0]*b[2],a[0]*b[1]-a[1]*b[0]];
const pcaldaUnit=a=>{const n=Math.hypot(...a)||1;return a.map(x=>x/n)};
const pcaldaLerp=(a,b,t)=>a.map((x,i)=>x*(1-t)+b[i]*t);
const pcaldaSubtract=(a,b)=>a.map((x,i)=>x-b[i]);
function pcaldaSolve(A,b) { // three-by-three, with pivoting and tiny regularization
  const rows=A.map((row,i)=>[...row.map((v,j)=>v+(i===j?1e-8:0)), b[i]]);
  for(let k=0;k<3;k++){
    let m=k;
    for(let i=k+1;i<3;i++)if(Math.abs(rows[i][k])>Math.abs(rows[m][k]))m=i;
    [rows[k],rows[m]]=[rows[m],rows[k]];
    const v=rows[k][k];if(Math.abs(v)<1e-12)return [0,0,1];
    for(let j=k;j<4;j++)rows[k][j]/=v;
    for(let i=0;i<3;i++)if(i!==k){const f=rows[i][k];for(let j=k;j<4;j++)rows[i][j]-=f*rows[k][j]}
  }
  return rows.map(r=>r[3]);
}
function pcaldaFit(points,groups){
  const means=[[0,0,0],[0,0,0]],cnt=[0,0],pooled=Array.from({length:3},()=>[0,0,0]);
  points.forEach((p,i)=>{const k=groups[i];cnt[k]++;for(let j=0;j<3;j++)means[k][j]+=p[j]});
  for(let k=0;k<2;k++)for(let j=0;j<3;j++)means[k][j]/=cnt[k];
  points.forEach((p,i)=>{const d=pcaldaSubtract(p,means[groups[i]]);for(let a=0;a<3;a++)for(let b=0;b<3;b++)pooled[a][b]+=d[a]*d[b]/(points.length-2)});
  const delta=pcaldaSubtract(means[1],means[0]);
  let ld1=pcaldaUnit(pcaldaSolve(pooled,delta));
  if(pcaldaDot(ld1,delta)<0)ld1=ld1.map(v=>-v);
  const pc1=[1,0,0];
  let secondary=pcaldaSubtract(pc1,ld1.map(v=>v*pcaldaDot(pc1,ld1)));
  if(Math.hypot(...secondary)<1e-5){const pc2=[0,1,0];secondary=pcaldaSubtract(pc2,ld1.map(v=>v*pcaldaDot(pc2,ld1)))}
  return {ld1,secondary:pcaldaUnit(secondary),counts:cnt};
}
function pcaldaFrame(){
  const s=pcaldaState;if(s.override)return s.override;
  // Turn relative to the selected reference plane. Both screen directions remain orthonormal.
  const v0=s.baseV, n0=pcaldaUnit(pcaldaCross(s.baseU,v0));
  const cy=Math.cos(s.yaw), sy=Math.sin(s.yaw);
  const u=pcaldaUnit(s.baseU.map((x,i)=>cy*x-sy*n0[i]));
  const n=pcaldaUnit(pcaldaCross(u,v0));
  const cp=Math.cos(s.pitch), sp=Math.sin(s.pitch);
  const v=pcaldaUnit(v0.map((x,i)=>cp*x+sp*n[i]));
  return {u,v};
}
function pcaldaFisherDistance(points,groups,frame){
  const m=[[0,0],[0,0]],counts=[0,0],cov=[0,0,0];
  const proj=points.map(p=>[pcaldaDot(p,frame.u),pcaldaDot(p,frame.v)]);
  proj.forEach((p,i)=>{const k=groups[i];counts[k]++;m[k][0]+=p[0];m[k][1]+=p[1]});
  for(let k=0;k<2;k++){m[k][0]/=counts[k];m[k][1]/=counts[k]}
  proj.forEach((p,i)=>{const d=[p[0]-m[groups[i]][0],p[1]-m[groups[i]][1]];cov[0]+=d[0]*d[0];cov[1]+=d[0]*d[1];cov[2]+=d[1]*d[1]});
  cov[0]/=points.length-2;cov[1]/=points.length-2;cov[2]/=points.length-2;
  const du=m[1][0]-m[0][0],dv=m[1][1]-m[0][1],det=cov[0]*cov[2]-cov[1]*cov[1];
  if(det<1e-10)return 0;
  return Math.sqrt(Math.max(0,(cov[2]*du*du-2*cov[1]*du*dv+cov[0]*dv*dv)/det));
}
function pcaldaVariance(points,frame){
  const means=[0,0,0];points.forEach(p=>{for(let j=0;j<3;j++)means[j]+=p[j]/points.length});
  let visible=0,total=0;
  points.forEach(p=>{const d=pcaldaSubtract(p,means);visible+=pcaldaDot(d,frame.u)**2+pcaldaDot(d,frame.v)**2;total+=pcaldaDot(d,d)});
  return total?100*visible/total:0;
}
function pcaldaRender(){
  const svg=$('pcaLdaSvg'),s=pcaldaState;if(!svg||!s)return;
  const fr=pcaldaFrame(), pr=p=>[450+80*pcaldaDot(p,fr.u),252-80*pcaldaDot(p,fr.v)];
  const mode=s.mode==='pca'?'PCA: most variance':s.mode==='lda'?'LDA: most class separation':'Rotate · same data, different projection';
  let h='<defs><clipPath id="w12PcaLdaClip"><rect x="28" y="58" width="844" height="374"/></clipPath></defs>';
  h+=svgTxt(450,34,mode,'w12-title');
  h+='<g clip-path="url(#w12PcaLdaClip)">';
  const a=s.baseU,b=s.baseV; // reference grid: PCA plane or (LD1, orthogonal PC1)
  for(let j=-5;j<=5;j++){
    const q=j*.5, pts=[pr(a.map((x,i)=>q*x-2.5*b[i])),pr(a.map((x,i)=>q*x+2.5*b[i])),pr(a.map((x,i)=>-2.5*x+q*b[i])),pr(a.map((x,i)=>2.5*x+q*b[i]))];
    h+=`<line x1="${pts[0][0]}" y1="${pts[0][1]}" x2="${pts[1][0]}" y2="${pts[1][1]}" class="w12-pcalda-grid"/>`;
    h+=`<line x1="${pts[2][0]}" y1="${pts[2][1]}" x2="${pts[3][0]}" y2="${pts[3][1]}" class="w12-pcalda-grid"/>`;
  }
  const endA=pr(a.map(v=>2.5*v)),endB=pr(b.map(v=>2.5*v)),startA=pr(a.map(v=>-2.5*v)),startB=pr(b.map(v=>-2.5*v));
  h+=axis(...startA,...endA,'w12-pcalda-axis')+axis(...startB,...endB,'w12-pcalda-axis');
  const origin=pr([0,0,0]);
  const colors=[C.orange,C.purple,C.green];
  s.data.labels.forEach((name,j)=>{
    const v=s.data.axes.map(ax=>ax[j]*2.25),tip=pr(v);
    const delta=[tip[0]-origin[0],tip[1]-origin[1]],len=Math.hypot(...delta)||1,n=delta.map(q=>q/len),perp=[-n[1],n[0]];
    h+=`<line x1="${origin[0]}" y1="${origin[1]}" x2="${tip[0]-n[0]*9}" y2="${tip[1]-n[1]*9}" stroke="${colors[j]}" stroke-width="3.1" stroke-linecap="round"/>`;
    h+=`<polygon points="${tip[0]},${tip[1]} ${tip[0]-n[0]*13+perp[0]*4},${tip[1]-n[1]*13+perp[1]*4} ${tip[0]-n[0]*13-perp[0]*4},${tip[1]-n[1]*13-perp[1]*4}" fill="${colors[j]}"/>`;
  });
  // Depth-order points for a readable pseudo-3D view.
  const depth=pcaldaCross(fr.u,fr.v);
  s.points.map((p,i)=>({p,i,z:pcaldaDot(p,depth)})).sort((a,b)=>a.z-b.z).forEach(({p,i})=>{
    const [x,y]=pr(p),color=s.groups[i]?C.red:C.blue;
    h+=`<circle cx="${x.toFixed(2)}" cy="${y.toFixed(2)}" r="4.2" fill="${color}" fill-opacity=".77" stroke="white" stroke-opacity=".68" stroke-width=".75"/>`;
  });
  h+='</g>';
  const axisNames=s.baseMode==='lda'?['LD1','PC1*']:['PC1','PC2'];
  h+=svgTxt(clamp(endA[0]+18,50,853),clamp(endA[1]-8,73,420),axisNames[0],'w12-pcalda-label');
  h+=svgTxt(clamp(endB[0]+58,50,853),clamp(endB[1]-8,73,420),axisNames[1],'w12-pcalda-label');
  s.data.labels.forEach((name,j)=>{
    const v=s.data.axes.map(ax=>ax[j]*2.25),tip=pr(v),dx=tip[0]-origin[0],dy=tip[1]-origin[1],len=Math.hypot(dx,dy)||1;
    h+=`<text x="${clamp(tip[0]+14*dx/len,62,840).toFixed(1)}" y="${clamp(tip[1]+14*dy/len,75,425).toFixed(1)}" text-anchor="middle" class="w12-pcalda-variable" fill="${colors[j]}">${name}</text>`;
  });
  h+=`<circle cx="270" cy="464" r="6" fill="${C.blue}"/><text x="283" y="470" class="w12-pcalda-legend">Healthy</text>`;
  h+=`<circle cx="527" cy="464" r="6" fill="${C.red}"/><text x="540" y="470" class="w12-pcalda-legend">Sick</text>`;
  svg.innerHTML=h;
  upd('pcaLdaView',s.mode==='pca'?'PC1 + PC2':s.mode==='lda'?'LD1 + PC1*':'Custom view');
  upd('pcaLdaVariance',fmt(pcaldaVariance(s.points,fr),1)+'%');
  upd('pcaLdaSeparation',fmt(pcaldaFisherDistance(s.points,s.groups,fr),2));
}
function pcaldaChange(mode){
  const s=pcaldaState;if(!s)return;
  if(s.anim)cancelAnimationFrame(s.anim);
  const start=pcaldaFrame(),target=mode==='pca'?
    {u:[1,0,0],v:[0,1,0]}:{u:s.fit.ld1,v:s.fit.secondary};
  s.baseMode=mode;s.baseU=target.u;s.baseV=target.v;s.yaw=0;s.pitch=0;s.mode=mode;
  const t0=performance.now();
  function tick(t){
    const progress=clamp((t-t0)/650,0,1),e=progress*progress*(3-2*progress);
    let u=pcaldaUnit(pcaldaLerp(start.u,target.u,e));
    let v=pcaldaLerp(start.v,target.v,e);
    v=pcaldaUnit(pcaldaSubtract(v,u.map(x=>x*pcaldaDot(v,u))));
    s.override=progress<1?{u,v}:null;
    pcaldaRender();
    s.anim=progress<1?requestAnimationFrame(tick):null;
  }
  s.anim=requestAnimationFrame(tick);
}
function initPcaLda(){
  const svg=$('pcaLdaSvg'),dat=DATA.pca;if(!svg||!dat)return;
  if(!pcaldaState){
    const points=dat.points.map(p=>dat.axes.map(a=>pcaldaDot(p,a)));
    const groups=points.map(p=>p[2]>=0?1:0); // each blob cut by low-variance PC3
    pcaldaState={data:dat,points,groups,fit:pcaldaFit(points,groups),
      baseMode:'pca',baseU:[1,0,0],baseV:[0,1,0],yaw:.63,pitch:.52,
      mode:'custom',drag:null,anim:null,override:null};
  }
  once('pcaLdaShowPCA','click',()=>pcaldaChange('pca'));
  once('pcaLdaShowLDA','click',()=>pcaldaChange('lda'));
  once('pcaLdaSvg','pointerdown',e=>{
    e.preventDefault();const s=pcaldaState;
    if(s.anim){cancelAnimationFrame(s.anim);s.anim=null;const f=pcaldaFrame();s.baseU=f.u;s.baseV=f.v;s.override=null;s.yaw=0;s.pitch=0}
    s.drag=[e.clientX,e.clientY];svg.setPointerCapture(e.pointerId);
  });
  once('pcaLdaSvg','pointermove',e=>{
    const s=pcaldaState;if(!s?.drag)return;
    const dx=e.clientX-s.drag[0],dy=e.clientY-s.drag[1];
    if(dx||dy){s.yaw=clamp(s.yaw+.009*dx,-1.50,1.50);s.pitch=clamp(s.pitch-.007*dy,-1.42,1.42);s.mode='custom';pcaldaRender()}
    s.drag=[e.clientX,e.clientY];
  });
  for(const eventName of ['pointerup','pointercancel'])once('pcaLdaSvg',eventName,e=>{
    pcaldaState.drag=null;
    if(svg.hasPointerCapture?.(e.pointerId))svg.releasePointerCapture(e.pointerId);
  });
  pcaldaRender();
}

// ------------ Seven-leaf, three-biomarker decision tree walkthrough --------
// Replaces the previous "Supervised tree browser" block (treeRender + initTree).
// Model trained offline on 900 synthetic observations; standalone and independent
// of W12_DATA.tree (which splits on only two of the original five biomarkers).
const TREE_WALK_MODEL = {"features":["Amino acid A","Lipid B","Metabolite C"],"children_left":[1,3,9,-1,5,-1,7,-1,-1,-1,11,-1,-1],"children_right":[2,4,10,-1,6,-1,8,-1,-1,-1,12,-1,-1],"feature":[0,1,1,-2,2,-2,0,-2,-2,-2,0,-2,-2],"threshold":[0.2904,-0.6141,0.8281,-2.0,0.5536,-2.0,-0.1039,-2.0,-2.0,-2.0,0.746,-2.0,-2.0],"value":[[0.464444,0.535556],[0.62963,0.37037],[0.216667,0.783333],[0.40411,0.59589],[0.713198,0.286802],[0.785455,0.214545],[0.546218,0.453782],[0.662921,0.337079],[0.2,0.8],[0.159722,0.840278],[0.444444,0.555556],[0.666667,0.333333],[0.285714,0.714286]],"samples":[900,540,360,146,394,275,119,89,30,288,72,30,42]};
let treeStepTimer = null, treeRunVersion = 0;
let treeCoords = null;

function treeMakeLayout(model) {
  const coords = Array(model.feature.length), dy=90, y0=66;
  let nleaf=0;
  function place(node,depth) {
    const left=model.children_left[node], right=model.children_right[node];
    let x;
    if(left<0) x=83+(nleaf++)*122.3;
    else x=(place(left,depth+1)+place(right,depth+1))/2;
    coords[node]={x:x,y:y0+dy*depth,depth};
    return x;
  }
  place(0,0);
  return coords;
}
function treeRender() {
  const svg=$('treeSvg');if(!svg)return;
  const m=TREE_WALK_MODEL, pts=treeCoords=treeMakeLayout(m);
  const N=m.feature.length;
  let h=`<text x="450" y="24" text-anchor="middle" class="w12-title">Follow the patient through the entire decision tree</text>`;
  // All branches are visible even before a prediction is requested.
  for(let node=0;node<N;node++){
    const left=m.children_left[node],right=m.children_right[node];
    if(left<0)continue;
    for(const [child,isLeft] of [[left,true],[right,false]]){
      const a=pts[node],b=pts[child];
      const x1=a.x,y1=a.y+23,x2=b.x,y2=b.y-24;
      const c=(y1+y2)*.5;
      h+=`<path class="w12-tree-edge" data-from="${node}" data-to="${child}" d="M ${x1.toFixed(2)} ${y1} C ${x1.toFixed(2)} ${c.toFixed(1)}, ${x2.toFixed(2)} ${c.toFixed(1)}, ${x2.toFixed(2)} ${y2}"/>`;
      const lx=x1*.43+x2*.57, ly=y1*.43+y2*.57;
      h+=`<text x="${lx.toFixed(1)}" y="${(ly-5).toFixed(1)}" class="w12-tree-edge-tag" text-anchor="middle">${isLeft?'YES':'NO'}</text>`;
    }
  }
  for(let node=0;node<N;node++){
    const p=pts[node],fi=m.feature[node],leaf=fi<0;
    const prob=m.value[node][1] / Math.max(1e-8,m.value[node][0]+m.value[node][1]);
    const risk=prob>=.5?'high':'low', w=leaf?104:136, ht=48;
    h+=`<g class="w12-tree-node ${leaf?'w12-tree-leaf':''}" data-node="${node}" ${leaf?`data-risk="${risk}"`:''}>`;
    h+=`<rect class="w12-tree-box" x="${(p.x-w/2).toFixed(1)}" y="${(p.y-ht/2).toFixed(1)}" width="${w}" height="${ht}" rx="12"/>`;
    if(leaf){
      h+=`<text class="w12-tree-node-text" x="${p.x.toFixed(1)}" y="${(p.y-2).toFixed(1)}">${risk==='high'?'Higher risk':'Lower risk'}</text>`;
      h+=`<text class="w12-tree-node-rule" x="${p.x.toFixed(1)}" y="${(p.y+14).toFixed(1)}">${(prob*100).toFixed(0)}% higher</text>`;
    } else {
      h+=`<text class="w12-tree-node-text" x="${p.x.toFixed(1)}" y="${(p.y-3).toFixed(1)}">${esc(m.features[fi])}</text>`;
      h+=`<text class="w12-tree-node-rule" x="${p.x.toFixed(1)}" y="${(p.y+14).toFixed(1)}">≤ ${fmt(m.threshold[node],2)}?</text>`;
    }
    h+='</g>';
  }
  h+=`<circle cx="285" cy="492" r="7" fill="#eaf7ef" stroke="#18864b" stroke-width="1.5"/>`;
  h+=`<text x="299" y="497" class="w12-tree-footer">Lower risk</text>`;
  h+=`<circle cx="491" cy="492" r="7" fill="#fff0e5" stroke="#c65d09" stroke-width="1.5"/>`;
  h+=`<text x="505" y="497" class="w12-tree-footer">Higher risk</text>`;
  svg.innerHTML=h;
}
function treeResetPath() {
  treeRunVersion++;
  if(treeStepTimer !== null){clearTimeout(treeStepTimer);treeStepTimer=null;}
  const svg=$('treeSvg');
  if(svg)svg.querySelectorAll('.w12-tree-node,.w12-tree-edge').forEach(el=>el.classList.remove('is-active','is-done'));
  upd('treePred','—');upd('treeProb','—');upd('treeDepth','—');
  upd('treeStatus','Set values and press Predict.');
}
function treePredict() {
  const svg=$('treeSvg');if(!svg)return;
  treeResetPath();
  const m=TREE_WALK_MODEL, values=[0,1,2].map(i=>val('treeF'+i));
  let node=0, nodes=[0], answers=[];
  while(m.feature[node]>=0 && nodes.length<=5){
    const fi=m.feature[node],yes=values[fi]<=m.threshold[node];
    answers.push({id:node,feature:fi,yes});
    node=yes?m.children_left[node]:m.children_right[node];
    nodes.push(node);
  }
  const token=treeRunVersion;
  const locate=id=>svg.querySelector(`[data-node="${id}"]`);
  function highlightStep(i){
    if(token!==treeRunVersion || !svg.isConnected)return;
    if(i>0){
      locate(nodes[i-1])?.classList.replace('is-active','is-done');
      svg.querySelector(`[data-from="${nodes[i-1]}"][data-to="${nodes[i]}"]`)?.classList.add('is-active');
    }
    locate(nodes[i])?.classList.add('is-active');
    if(i<answers.length){
      const a=answers[i],sign=a.yes?'≤':'>';
      upd('treeStatus',`Rule ${i+1} of ${answers.length}: ${m.features[a.feature]} = ${fmt(values[a.feature],1)} ${sign} ${fmt(m.threshold[a.id],2)} · ${a.yes?'YES':'NO'}`);
      treeStepTimer=setTimeout(()=>highlightStep(i+1),690);
    }else{
      const p=m.value[node][1]/Math.max(1e-8,m.value[node][0]+m.value[node][1]);
      treeStepTimer=setTimeout(()=>{
        if(token!==treeRunVersion)return;
        upd('treePred',p>=.5?'Higher-risk':'Lower-risk');
        upd('treeProb',`${(100*p).toFixed(1)}%`);
        upd('treeDepth',String(answers.length));
        upd('treeStatus',`Reached a ${p>=.5?'higher':'lower'}-risk leaf after ${answers.length} ${answers.length===1?'rule':'rules'}. Prediction complete.`);
        treeStepTimer=null;
      },360);
    }
  }
  highlightStep(0);
}
function initTree() {
  if(!$('treeSvg'))return;
  treeRender();
  for(let i=0;i<3;i++){
    const update=()=>{upd('treeV'+i,fmt(val('treeF'+i),1));treeResetPath();};
    once('treeF'+i,'input',update);
    upd('treeV'+i,fmt(val('treeF'+i),1));
  }
  once('treePredict','click',treePredict);
  treeResetPath();
}

// ------------ Reproducible polynomial double descent ------------
// Both datasets have a cubic + oscillating signal, Gaussian measurement noise,
// and a separate held-out validation sample. The displayed descent is particular
// to these constructed examples; it is not a universal property of high degree.
let ddCase=0;
function ddRender(){
 const svg=$('complexitySvg'); if(!svg||!DATA.complexity)return;
 const dat=DATA.complexity[ddCase];
 const deg=clamp(Math.round(val('degree',4)),1,dat.sims.length);
 const mode=$('complexMode').value, split=mode==='split';
 const sim=dat.sims[deg-1],L=65,R=455,T=65,B=420;
 const yMin=dat.yMin,yMax=dat.yMax;
 const X=x=>normalize(x,-1,1,L,R);
 // Do not artificially flatten polynomial excursions at the plot boundaries.
 // Instead use a clip path, keeping the true residual lengths available.
 const Y=y=>normalize(y,yMin,yMax,B,T);
 const xPath=(xs,ys)=>xs.map((x,i)=>(i?'L':'M')+X(x).toFixed(1)+' '+Y(ys[i]).toFixed(1)).join(' ');
 let h='<defs><clipPath id="ddDataClip"><rect x="65" y="65" width="390" height="355"/></clipPath></defs>';
 h+=axis(L,B,R,B)+axis(L,T,L,B);
 h+=svgTxt(260,35,`Degree ${deg} · fitted polynomial`,'w12-title');
 h+=`<g clip-path="url(#ddDataClip)">`;
 // Residuals are observed-minus-fitted, vertical because this is OLS.
 dat.trainX.forEach((x,i)=>{
  h+=`<line x1="${X(x).toFixed(1)}" y1="${Y(dat.trainY[i]).toFixed(1)}" x2="${X(x).toFixed(1)}" y2="${Y(sim.trainFit[i]).toFixed(1)}" stroke="${C.blue}" stroke-width="1.55" stroke-opacity=".52"/>`;
 });
 // Draw only a readable subset of validation residuals, but compute MSE
 // using every one of the 120 held-out observations.
 const valStep=Math.ceil(dat.valX.length/20);
 if(split)for(let i=0;i<dat.valX.length;i+=valStep){
  const x=dat.valX[i];
  h+=`<line x1="${X(x).toFixed(1)}" y1="${Y(dat.valY[i]).toFixed(1)}" x2="${X(x).toFixed(1)}" y2="${Y(sim.valFit[i]).toFixed(1)}" stroke="${C.purple}" stroke-width="1.7" stroke-opacity=".60" stroke-dasharray="3 3"/>`;
 }
 h+=`<path d="${xPath(dat.plotX,dat.plotY)}" fill="none" stroke="${C.orange}" stroke-width="2.2" stroke-dasharray="5 5"/>`;
 h+=`<path d="${xPath(dat.plotX,sim.curve)}" fill="none" stroke="${C.green}" stroke-width="3.4"/>`;
 dat.trainX.forEach((x,i)=>h+=`<circle cx="${X(x).toFixed(1)}" cy="${Y(dat.trainY[i]).toFixed(1)}" r="5.3" fill="${C.blue}" stroke="white" stroke-width="1.2"/>`);
 if(split)for(let i=0;i<dat.valX.length;i+=valStep){
  h+=`<circle cx="${X(dat.valX[i]).toFixed(1)}" cy="${Y(dat.valY[i]).toFixed(1)}" r="5" fill="${C.purple}" stroke="white" stroke-width="1.5"/>`;
 }
 h+='</g>';
 for(const v of [-1,-.5,0,.5,1])h+=svgTxt(X(v),B+22,String(v),'w12-small');
 h+=`<circle cx="85" cy="454" r="4.5" fill="${C.blue}"/>`+svgTxt(96,459,'train','w12-small','start');
 if(split)h+=`<circle cx="172" cy="454" r="4.5" fill="${C.purple}"/>`+svgTxt(183,459,'validation','w12-small','start');
 h+=`<line x1="${split?288:205}" y1="454" x2="${split?314:231}" y2="454" stroke="${C.green}" stroke-width="3"/>`+svgTxt(split?320:237,459,'fit','w12-small','start');
 h+=`<line x1="365" y1="454" x2="386" y2="454" stroke="${C.orange}" stroke-width="2" stroke-dasharray="4 3"/>`+svgTxt(392,459,'truth','w12-small','start');

 // Right: train and independent validation MSE, on a common log scale.
 const lo=570,ro=865,to=65,bo=420;
 h+=axis(lo,bo,ro,bo)+axis(lo,to,lo,bo);
 const xx=d=>normalize(d,1,44,lo,ro);
 const logLoss=loss=>Math.log10(Math.max(1e-9,loss));
 const yy=v=>normalize(clamp(logLoss(v),-6,2),-6,2,bo,to);
 function lineFor(prop,color){return `<path d="${dat.sims.map((v,i)=>(i?'L':'M')+xx(v.degree).toFixed(1)+' '+yy(v[prop]).toFixed(1)).join(' ')}" fill="none" stroke="${color}" stroke-width="2.8"/>`}
 h+=lineFor('train',C.blue);if(split)h+=lineFor('valid',C.red);
 h+=axis(xx(13),to,xx(13),bo,'w12-grid');
 h+=svgTxt(xx(13),to-9,'interpolation','w12-small');
 h+=axis(xx(deg),to,xx(deg),bo,'w12-select-line');
 h+=dot(xx(deg),yy(sim.train),6,C.blue);
 if(split)h+=dot(xx(deg),yy(sim.valid),6,C.red);
 [1,10,20,30,40].forEach(v=>h+=svgTxt(xx(v),bo+23,v));
 [-6,-4,-2,0,2].forEach(v=>h+=svgTxt(lo-8,yy(10**v)+4,'10^'+v,'w12-small','end'));
 h+=svgTxt(717,35,split?'Train vs validation MSE (log scale)':'Training MSE only (log scale)','w12-title');
 h+=svgTxt(715,470,'Polynomial degree →');
 svg.innerHTML=h;
 const showMSE=x=>x<1e-5?'<0.00001':fmt(x,5);
 upd('degreeVal',deg);
 upd('complexTrain',showMSE(sim.train));
 upd('complexVal',split?showMSE(sim.valid):'hidden');
}
function initDouble(){
 if(!$('complexitySvg'))return;
 for(const id of ['degree','complexMode'])once(id,id==='degree'?'input':'change',ddRender);
 once('complexResplit','click',()=>{ddCase=(ddCase+1)%DATA.complexity.length;ddRender()});
 ddRender();
}

// ------------ Truly offline pretrained digit network -------
let digitDragging=false,digitReady=false;
function digitClear(){const cv=$('digitCanvas');if(!cv)return;const ctx=cv.getContext('2d');ctx.fillStyle='#000';ctx.fillRect(0,0,280,280);upd('digitResult','Draw a digit');$('digitProbs').innerHTML='';const pv=$('digitPixels');if(pv)pv.getContext('2d').clearRect(0,0,112,112)}
function drawXY(e){const cv=$('digitCanvas'),b=cv.getBoundingClientRect();return[(e.clientX-b.left)*280/b.width,(e.clientY-b.top)*280/b.height]}
function digitStart(e){const cv=$('digitCanvas');cv.setPointerCapture(e.pointerId);digitDragging=true;const p=drawXY(e),ctx=cv.getContext('2d');ctx.beginPath();ctx.moveTo(...p);ctx.lineCap='round';ctx.lineJoin='round';ctx.strokeStyle='#fff';ctx.lineWidth=21;ctx.lineTo(p[0]+.2,p[1]+.2);ctx.stroke()}
function digitMove(e){if(!digitDragging)return;const ctx=$('digitCanvas').getContext('2d'),p=drawXY(e);ctx.lineTo(...p);ctx.stroke()}
function digitPrepare(){const src=$('digitCanvas'),orig=src.getContext('2d').getImageData(0,0,280,280).data;let minx=280,miny=280,maxx=-1,maxy=-1;
 for(let y=0;y<280;y++)for(let x=0;x<280;x++){const p=orig[(y*280+x)*4];if(p>28){minx=Math.min(minx,x);miny=Math.min(miny,y);maxx=Math.max(maxx,x);maxy=Math.max(maxy,y)}}
 if(maxx<0)return null;let wid=maxx-minx+1,hei=maxy-miny+1;const scale=23/Math.max(wid,hei),ww=Math.max(1,Math.round(wid*scale)),hh=Math.max(1,Math.round(hei*scale));const crop=document.createElement('canvas');crop.width=28;crop.height=28;let ctx=crop.getContext('2d',{willReadFrequently:true});ctx.fillStyle='#000';ctx.fillRect(0,0,28,28);ctx.imageSmoothingEnabled=true;ctx.imageSmoothingQuality='high';ctx.drawImage(src,minx,miny,wid,hei,Math.round((28-ww)/2),Math.round((28-hh)/2),ww,hh);
 const arr=ctx.getImageData(0,0,28,28).data,out=[];for(let i=0;i<784;i++)out.push(arr[4*i]/255);
 const preview=$('digitPixels');if(preview){const pctx=preview.getContext('2d');pctx.imageSmoothingEnabled=false;pctx.clearRect(0,0,112,112);pctx.drawImage(crop,0,0,112,112)}return out}
function modelPredict(input){const mdl=window.W12_DIGIT_MODEL;if(!mdl)return null;let u=input;
 for(let l=0;l<mdl.layers.length;l++){const layer=mdl.layers[l],w=layer.w,b=layer.b,nu=new Float32Array(layer.out);for(let j=0;j<layer.out;j++){let s=b[j],k=j*layer.in;for(let i=0;i<layer.in;i++)s+=w[k+i]*u[i];nu[j]=l<mdl.layers.length-1?Math.max(0,s):s}u=nu}
 const peak=Math.max(...u),exp=Array.from(u,z=>Math.exp(z-peak)),sum=exp.reduce((a,b)=>a+b,0);return exp.map(z=>z/sum)}
function digitPredict(){const x=digitPrepare();if(!x){upd('digitResult','Draw first');return}const p=modelPredict(x);if(!p){upd('digitResult','Weights unavailable');return}const ix=p.indexOf(Math.max(...p));upd('digitResult',`Prediction: ${ix}`);$('digitProbs').innerHTML=p.map((q,i)=>`<div class="w12-digit-prob"><b>${i}</b><div><span style="width:${(100*q).toFixed(1)}%;background:${i===ix?C.green:C.blue}"></span></div><small>${(100*q).toFixed(1)}%</small></div>`).join('')}
function initDigit(){if(!$('digitCanvas')||digitReady)return;digitReady=true;const cv=$('digitCanvas');cv.addEventListener('pointerdown',digitStart,{passive:false});cv.addEventListener('pointermove',digitMove,{passive:false});cv.addEventListener('pointerup',()=>digitDragging=false);cv.addEventListener('pointercancel',()=>digitDragging=false);once('digitClear','click',digitClear);once('digitPredict','click',digitPredict);digitClear()}

// ------------ Review questions -------------------------------
const ANSWERS={1:['B','PCA maximizes retained variance; it does not read outcome labels.'],2:['C','Scaling changes which variables dominate the covariance and principal components.'],3:['B','Clustering gives a partition, not proof of biological classes.'],4:['A','A separate test set is evaluated only after model selection.'],5:['C','A large gap between training and validation error flags overfitting.'],6:['B','The digit network is a predictive tool, not evidence of medical validity.']};
function initQuiz(){document.querySelectorAll('.w12-quiz').forEach(box=>{if(box.dataset.bound)return;box.dataset.bound='1';box.querySelectorAll('button[data-choice]').forEach(btn=>btn.addEventListener('click',()=>{const [correct,why]=ANSWERS[box.dataset.q],ok=btn.dataset.choice===correct;box.querySelectorAll('button[data-choice]').forEach(b=>{b.classList.toggle('correct',b.dataset.choice===correct);b.classList.toggle('wrong',b===btn&&!ok)});const f=box.querySelector('.w12-quiz-feedback');f.textContent=(ok?'Correct. ':'Not quite. ')+why;f.className='w12-quiz-feedback '+(ok?'correct':'wrong')}))})}

function initAll(){initGauss();initPCA();initNonlin();initClust();initPcaLda();initTree();initDouble();initDigit();initQuiz()}
if(document.readyState==='loading')document.addEventListener('DOMContentLoaded',initAll,{once:true});else initAll();
window.addEventListener('load',initAll,{once:true});
if(window.Reveal){try{window.Reveal.on('ready',initAll)}catch(e){}}
})();
