"""Reproducible self-contained UMAP-core preprocessing for the Week 12 mammoth lab.

Data: 1 in 8 points from PAIR-code/understanding-umap raw_data/mammoth_3d.json
quantized to uint8 per axis; Apache 2.0. See ATTRIBUTION.md.

UMAP objective: kNN local fuzzy graph, probabilistic union, spectral embedding,
and SGD cross-entropy with negative sampling. UMAP's min_dist curve is fit to
its low-dimensional attraction kernel. For larger datasets prefer umap-learn.
"""
import base64
import json
from pathlib import Path
import numpy as np
from scipy.optimize import curve_fit
from scipy.linalg import orthogonal_procrustes
from scipy.sparse import coo_matrix, diags, eye
from scipy.sparse.csgraph import connected_components
from scipy.sparse.linalg import eigsh
from sklearn.neighbors import NearestNeighbors
from numba import njit

HERE=Path(__file__).resolve().parent
nbit=np.frombuffer(base64.urlsafe_b64decode((HERE/'mammoth1250.b64').read_text().strip()),dtype=np.uint8).reshape(-1,3)
LO=np.array([61.108,-171.933,-22.085]);HI=np.array([568.899,172.019,169.582]);orig=LO+(nbit/255.0)*(HI-LO)
# Preserve the source geometry by using a single scale for all 3 dimensions.
raw=(orig-orig.mean(axis=0))/((HI-LO).max()/3.0)
# For reproducible visual color mapping, color depends on original mammoth z coordinate.
color=(orig[:,2]-orig[:,2].min())/np.ptp(orig[:,2])

def find_ab(spread=1.0,min_dist=0.25):
  x=np.linspace(0,spread*3,300)
  y=np.where(x<min_dist,1,np.exp(-(x-min_dist)/spread))
  def fun(x,a,b):return 1.0/(1.0+a*x**(2*b))
  return curve_fit(fun,x,y,p0=[1.5,1],maxfev=10000)[0]

def fuzzy_graph(x,k):
 n=x.shape[0]
 # sklearn returns the query point itself as the zeroth neighbour
 distances,indices=NearestNeighbors(n_neighbors=k+1,algorithm='auto',n_jobs=-1).fit(x).kneighbors(x)
 distances,indices=distances[:,1:],indices[:,1:]
 rhos=np.zeros(n)
 sigmas=np.zeros(n)
 target=np.log2(k)
 for i in range(n):
  nonzero=distances[i][distances[i]>1e-9]
  rhos[i]=nonzero[0] if len(nonzero) else 0.0
  lo=0.0;hi=np.inf;mid=1.0
  for _ in range(65):
   psum=np.exp(-np.maximum(0.0,distances[i]-rhos[i])/mid).sum()
   if abs(psum-target)<1e-5:break
   if psum>target:hi=mid;mid=(lo+hi)/2
   else:lo=mid;mid=2*mid if np.isinf(hi) else (lo+hi)/2
  sigmas[i]=max(mid,1e-5)
 rows=np.repeat(np.arange(n),k)
 cols=indices.ravel()
 vals=np.exp(-np.maximum(0,distances-rhos[:,None])/sigmas[:,None]).ravel()
 directed=coo_matrix((vals,(rows,cols)),shape=(n,n)).tocsr()
 directed.setdiag(0);directed.eliminate_zeros()
 trans=directed.transpose()
 both=directed.multiply(trans)
 union=directed+trans-both
 union.data=np.maximum(0,np.minimum(union.data,1))
 union.setdiag(0);union.eliminate_zeros()
 return union

def spectral_init(graph, seed):
 n=graph.shape[0]
 ncomp,labels=connected_components(graph)
 print('components',ncomp)
 degree=np.asarray(graph.sum(axis=1)).ravel()
 lap=eye(n)-diags(1/np.sqrt(np.maximum(degree,1e-8)))@graph@diags(1/np.sqrt(np.maximum(degree,1e-8)))
 if ncomp!=1:
  # fuzzy graph disconnected at small k: PCA initialisation is stable
  from sklearn.decomposition import PCA
  return PCA(2).fit_transform(raw).astype(np.float64)
 try:
  values,vectors=eigsh(lap,k=3,which='SM',tol=1e-4,random_state=np.random.default_rng(seed))
  ids=np.argsort(values)
  vec=vectors[:,ids[1:3]]
  vec=vec/np.maximum(1e-9,vec.std(axis=0))
  return np.asarray(vec,dtype=np.float64)
 except Exception:
  from sklearn.decomposition import PCA
  return PCA(2).fit_transform(raw).astype(np.float64)

@njit
def sgd(y, heads, tails, weights, a, b, epochs, seed):
 # Reproduces the UMAP edge-sampling objective with negative samples.
 # Deterministic RNG for reproducibility.
 np.random.seed(seed)
 n=len(y)
 maxw=np.max(weights)
 periods=maxw/np.maximum(weights,1e-12)
 nextpos=periods.copy()
 nextneg=periods/5.0
 negperiod=periods/5.0
 for epoch in range(epochs):
  alpha=1.0-epoch/epochs
  for e in range(len(weights)):
   if nextpos[e]>epoch:continue
   i=heads[e];j=tails[e]
   dx=y[i,0]-y[j,0];dy=y[i,1]-y[j,1]
   dist2=dx*dx+dy*dy
   if dist2>0:
    coeff=-2.0*a*b*(dist2**(b-1.0))/(1.0+a*(dist2**b))
    gx=max(-4.0,min(4.0,coeff*dx))*alpha
    gy=max(-4.0,min(4.0,coeff*dy))*alpha
    y[i,0]+=gx;y[i,1]+=gy
    y[j,0]-=gx;y[j,1]-=gy
   nextpos[e]+=periods[e]
   nneg=int((epoch-nextneg[e])/negperiod[e])
   if nneg>0:
    for _ in range(nneg):
     other=np.random.randint(0,n)
     if other==i:continue
     dx=y[i,0]-y[other,0];dy=y[i,1]-y[other,1]
     dist2=dx*dx+dy*dy
     if dist2>0:
      coeff=(2.0*b)/((0.001+dist2)*(1.0+a*(dist2**b)))
      y[i,0]+=max(-4.0,min(4.0,coeff*dx))*alpha
      y[i,1]+=max(-4.0,min(4.0,coeff*dy))*alpha
    nextneg[e]+=nneg*negperiod[e]
 return y

result={'source':'PAIR-code/understanding-umap raw_data/mammoth_3d.json; 1-in-8 deterministic subset','params':{'min_dist':0.25,'n_neighbors':[15,50,200],'seed':42},'xyz':np.round(raw,4).tolist(),'shade':np.round(color,3).tolist(),'umap':{}}
a,b=find_ab()
print('a,b',a,b,'N=',len(raw),'xyz ranges',raw.min(axis=0),raw.max(axis=0))
for k in [15,50,200]:
 print('computing',k,flush=True)
 graph=fuzzy_graph(raw,k)
 print('graph edges',graph.nnz,flush=True)
 y=spectral_init(graph,42)
 y=y/np.maximum(y.std(axis=0),1e-6)*2.0
 rng=np.random.default_rng(42);y+=rng.normal(0,.0001,size=y.shape)
 coo=graph.tocoo()
 order=np.argsort(coo.row)
 epochs=230 if k<=50 else 170
 yy=sgd(y.copy(),coo.row.astype(np.int32)[order],coo.col.astype(np.int32)[order],coo.data.astype(np.float64)[order],a,b,epochs,42)
 yy=(yy-yy.mean(0)).astype(float)
 # Align the otherwise arbitrary rotation/reflection to the raw XY view.
 # This preserves every pairwise distance of the learned UMAP embedding.
 rotation,_=orthogonal_procrustes(yy,raw[:,:2]-raw[:,:2].mean(axis=0))
 yy=yy@rotation
 result['umap'][str(k)]=np.round(yy,4).tolist()
 print('range',yy.min(0),yy.max(0), 'std', yy.std(0),flush=True)

(HERE/'mammoth_umap_data.js').write_text('/* Precomputed 2D UMAP embeddings; see ATTRIBUTION.md and build_mammoth_umap.py */\nwindow.W12_MAMMOTH='+json.dumps(result,separators=(',',':'))+';\n')
(HERE/'mammoth_umap_data.json').write_text(json.dumps(result,separators=(',',':')))
print('Wrote',HERE/'mammoth_umap_data.js')
