from pathlib import Path
import numpy as np,json
from numpy.polynomial.legendre import legvander
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
R=Path(__file__).resolve().parents[1];D=R/'week12'/'data'; D.mkdir(exist_ok=True)
rng=np.random.default_rng(122)
cloud=[]
for m in [[-1.7,0.5,.6],[1.2,1.3,-.5],[.8,-1.3,1.3]]:
 c=rng.normal(loc=m,scale=[.55,.43,.47],size=(80,3));cloud.extend(c.tolist())
cloud=np.array(cloud);scaled=StandardScaler().fit_transform(cloud);pca=PCA().fit(scaled)
# A deliberately constructed, reproducible *non-cubic* signal.
# With 14 observations a cubic alone is already captured too well by low degrees,
# leaving little room for a genuinely better second descent. The oscillatory
# component makes this a richer function-approximation example, not a generic result.
f=lambda x:.40*x-.65*x*x+.90*x*x*x + 1.0*np.sin(4*np.pi*x+.47)
cases=[]
for seed in (8,5):
 g=np.random.default_rng(seed)
 n=14
 xt=np.sort(np.clip(np.linspace(-.96,.96,n)+g.normal(0,.025,n),-.99,.99))
 yt=f(xt)+g.normal(0,.05,n)
 plotX=np.linspace(-1,1,181)
 plotY=f(plotX)
 # Independent held-out sample; fixed across every polynomial degree.
 valrng=np.random.default_rng(1000+seed)
 xv=np.sort(valrng.uniform(-1,1,120))
 yv=f(xv)+valrng.normal(0,.05,len(xv))
 sims=[]
 V=legvander(xt,44)
 DV=legvander(xv,44)
 G=legvander(plotX,44)
 for deg in range(1,45):
  # Exactly the same minimum-L2-coefficient-norm fit in the Legendre basis.
  # This is a Moore–Penrose solution; for degree > n-1 it picks one of
  # infinitely many interpolating polynomials, *not* the smoothest in general.
  coef=np.linalg.pinv(V[:,:deg+1],rcond=1e-9)@yt
  ft=V[:,:deg+1]@coef
  fv=DV[:,:deg+1]@coef
  fp=G[:,:deg+1]@coef
  sims.append({'degree':deg,'curve':np.round(fp,5).tolist(),
               'trainFit':np.round(ft,5).tolist(),
               'valFit':np.round(fv,5).tolist(),
               'train':round(float(np.mean((ft-yt)**2)),10),
               'valid':round(float(np.mean((fv-yv)**2)),10)})
 yrange=np.r_[plotY,yt,yv]
 pad=.11*(yrange.max()-yrange.min())
 cases.append({'seed':seed,'trainX':np.round(xt,5).tolist(),
               'trainY':np.round(yt,5).tolist(),
               'valX':np.round(xv,5).tolist(),
               'valY':np.round(yv,5).tolist(),
               'plotX':np.round(plotX,5).tolist(),
               'plotY':np.round(plotY,5).tolist(),
               'yMin':round(float(yrange.min()-pad),3),
               'yMax':round(float(yrange.max()+pad),3),
               'sims':sims})
# expose in script with models
out={'pca':{'points':np.round(scaled,4).tolist(),'axes':np.round(pca.components_,4).tolist(),'variance':np.round(pca.explained_variance_ratio_,4).tolist(),'labels':['Hemoglobin','Age','Weight']},'complexity':cases}
for name in ['clusters','tree','nonlinear_embeddings']:
 out[name]=json.loads((D/(name+'.json')).read_text())
# raw JavaScript variables; no fetch, works on static Quarto pages offline
(R/'week12'/'data.js').write_text('window.W12_DATA='+json.dumps(out,separators=(',',':'))+';\n')
model=json.loads((R/'models'/'digit_model.json').read_text())
(R/'week12'/'digit_model.js').write_text('window.W12_DIGIT_MODEL='+json.dumps(model,separators=(',',':'))+';\n')
print('data JS bytes',(R/'week12'/'data.js').stat().st_size, 'model JS bytes',(R/'week12'/'digit_model.js').stat().st_size)
