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
f=lambda x:.4*x-.65*x*x+.9*x*x*x
cases=[]
for seed in [5,31]:
 g=np.random.default_rng(seed);n=14;xt=np.sort(g.uniform(-1,1,n));xv=np.linspace(-1,1,140);yt=f(xt)+g.normal(0,.03,n);yv=f(xv)
 sims=[]
 for deg in range(1,45):
  V=legvander(xt,deg);coef=np.linalg.pinv(V,rcond=1e-9)@yt;ft=V@coef;fv=legvander(xv,deg)@coef
  sims.append({'degree':deg,'curve':np.round(fv,4).tolist(),'train':round(float(np.mean((ft-yt)**2)),5),'valid':round(float(np.mean((fv-yv)**2)),5)})
 cases.append({'trainX':np.round(xt,4).tolist(),'trainY':np.round(yt,4).tolist(),'testX':np.round(xv,4).tolist(),'testY':np.round(yv,4).tolist(),'sims':sims})
# expose in script with models
out={'pca':{'points':np.round(scaled,4).tolist(),'axes':np.round(pca.components_,4).tolist(),'variance':np.round(pca.explained_variance_ratio_,4).tolist(),'labels':['Hemoglobin','Age','Weight']},'complexity':cases}
for name in ['clusters','tree','nonlinear_embeddings']:
 out[name]=json.loads((D/(name+'.json')).read_text())
# raw JavaScript variables; no fetch, works on static Quarto pages offline
(R/'week12'/'data.js').write_text('window.W12_DATA='+json.dumps(out,separators=(',',':'))+';\n')
model=json.loads((R/'models'/'digit_model.json').read_text())
(R/'week12'/'digit_model.js').write_text('window.W12_DIGIT_MODEL='+json.dumps(model,separators=(',',':'))+';\n')
print('data JS bytes',(R/'week12'/'data.js').stat().st_size, 'model JS bytes',(R/'week12'/'digit_model.js').stat().st_size)
