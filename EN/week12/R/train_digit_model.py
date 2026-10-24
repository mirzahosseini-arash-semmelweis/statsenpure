"""Offline 28×28 pixel classifier trained on sklearn 8×8 digit images resampled to 28×28.
This is not MNIST; original MNIST unavailable in the build environment. All weights are bundled.
"""
from pathlib import Path
import numpy as np, torch, json, time
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split
from PIL import Image, ImageEnhance, ImageFilter
P=Path(__file__).resolve().parents[1];OUT=P/'models';OUT.mkdir(exist_ok=True)
torch.set_num_threads(4);np.random.seed(42);torch.manual_seed(42)
d=load_digits();imgs=d.images; yy=d.target.astype('int64'); ids=np.arange(len(yy));tr,te=train_test_split(ids,test_size=.20,random_state=42,stratify=yy)
tr,va=train_test_split(tr,test_size=.20,random_state=41,stratify=yy[tr])
# generate realistic shifts, rotations, thickened/diluted lines using PIL
rng=np.random.default_rng(2012)
def resample(idx,extra=False):
 a=(imgs[idx]/16*255).astype('uint8');im=Image.fromarray(a,'L').resize((28,28),Image.Resampling.BICUBIC)
 if extra:
  im=im.rotate(float(rng.uniform(-13,13)),resample=Image.Resampling.BICUBIC,translate=(int(rng.integers(-2,3)),int(rng.integers(-2,3))),fillcolor=0)
  if rng.random()<.23: im=im.filter(ImageFilter.GaussianBlur(.45))
  im=ImageEnhance.Contrast(im).enhance(float(rng.uniform(.8,1.3)))
 return np.asarray(im,dtype=np.float32).ravel()/255
Xtr=np.concatenate([np.stack([resample(i,extra=(k>0)) for i in tr]) for k in range(5)]).astype('float32')
ytr=np.tile(yy[tr],5)
Xte=np.stack([resample(i) for i in te]).astype('float32')
Xva=np.stack([resample(i) for i in va]).astype('float32')
model=torch.nn.Sequential(torch.nn.Linear(784,96),torch.nn.ReLU(),torch.nn.Linear(96,48),torch.nn.ReLU(),torch.nn.Linear(48,10))
opt=torch.optim.Adam(model.parameters(),lr=.002,weight_decay=.0002)
loss=torch.nn.CrossEntropyLoss()
X=torch.tensor(Xtr);y=torch.tensor(ytr);Xt=torch.tensor(Xte);Xv=torch.tensor(Xva)
best=0
for ep in range(24):
 perm=torch.randperm(len(X));model.train()
 for ix in perm.split(144):
  opt.zero_grad();z=model(X[ix]);l=loss(z,y[ix]);l.backward();opt.step()
 model.eval()
 with torch.no_grad(): pred=model(Xv).argmax(1).numpy()
 acc=np.mean(pred==yy[va]);
 if ep in (0,4,9,14,19,23):print('epoch',ep+1,'validation accuracy',round(acc,4),flush=True)
 if acc>best:
  best=acc;state={k:v.detach().clone() for k,v in model.state_dict().items()}
model.load_state_dict(state)
with torch.no_grad(): final_acc=float(np.mean(model(Xt).argmax(1).numpy()==yy[te]))
# export matrices neuron-major flattened row first
layers=[]
for i in (0,2,4):
 lin=model[i];layers.append({'in':lin.in_features,'out':lin.out_features,'w':np.round(lin.weight.detach().numpy(),5).ravel().tolist(),'b':np.round(lin.bias.detach().numpy(),5).tolist()})
(OUT/'digit_model.json').write_text(json.dumps({'source':'scikit-learn 8×8 handwritten digits, resampled/augmented to 28×28; NOT MNIST','input':'28×28 grayscale [0,1] row-major','test_accuracy':round(final_acc,4),'validation_accuracy_used_for_checkpoint':round(float(best),4),'architecture':'784–96–48–10 ReLU MLP','layers':layers},separators=(',',':')))
print('Model bytes:',(OUT/'digit_model.json').stat().st_size,'unseen test accuracy',final_acc,flush=True)
