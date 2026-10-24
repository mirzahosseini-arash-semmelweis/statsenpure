#!/usr/bin/env python3
"""Render two compact teaching animations to H.264 MP4 without Manim dependency.
Manim equivalents are provided separately for instructors who prefer them.
"""
from pathlib import Path
import numpy as np,cv2
ROOT=Path(__file__).resolve().parents[1]/'week11'/'media';ROOT.mkdir(parents=True,exist_ok=True)
W,H=1280,720
WHITE=(255,255,255);BLUE=(235,111,31);PURPLE=(181,74,123);GREEN=(75,134,24);RED=(56,56,201);GRAY=(133,117,102);INK=(40,24,16);LIGHT=(242,238,230)
font=cv2.FONT_HERSHEY_SIMPLEX

def put(im,s,xy,scale=.78,color=INK,weight=2):cv2.putText(im,s,xy,font,scale,color,weight,cv2.LINE_AA)
def writer(name):
 out=cv2.VideoWriter(str(ROOT/name),cv2.VideoWriter_fourcc(*'mp4v'),24,(W,H))
 if not out.isOpened():raise RuntimeError('video writer failed')
 return out

def convert_h264(path):
 # convert to browser-compatible H.264/yuv420p via ffmpeg if available
 import subprocess
 temp=path.with_name(path.stem+'_h264.mp4')
 subprocess.run(['ffmpeg','-y','-hide_banner','-loglevel','error','-i',str(path),'-c:v','libx264','-pix_fmt','yuv420p','-crf','23','-movflags','+faststart',str(temp)],check=True)
 temp.replace(path)

def panel(im,x0,y0,x1,y1):cv2.rectangle(im,(x0,y0),(x1,y1),(227,224,219),2,cv2.LINE_AA)
def drawtraj(im,pt,color,rect,width=2):
 if len(pt)<2:return
 x0,y0,x1,y1=rect
 arr=np.asarray(pt,np.float64);span=max(np.ptp(arr[:,0]),np.ptp(arr[:,1]),10.)
 # Fixed scaling based on full walk; panels will not 'zoom' between frames.
 origin=np.array([(x0+x1)/2,(y0+y1)/2])
 arrpix=np.stack([origin[0]+arr[:,0]*3.45,origin[1]-arr[:,1]*3.45],axis=1).astype('int32')
 cv2.polylines(im,[arrpix],False,color,width,cv2.LINE_AA)
 cv2.circle(im,tuple(arrpix[0]),6,GREEN,-1,cv2.LINE_AA)
 cv2.circle(im,tuple(arrpix[-1]),6,RED,-1,cv2.LINE_AA)

r=np.random.default_rng(101119)
length=950
walk2=np.zeros((length+1,2),dtype=np.int32);walk3=np.zeros((length+1,3),dtype=np.int32)
for i in range(1,length+1):
 walk2[i]=walk2[i-1];walk3[i]=walk3[i-1]
 walk2[i,r.integers(0,2)]+=r.choice([-1,1]);walk3[i,r.integers(0,3)]+=r.choice([-1,1])
iso=np.stack([walk3[:,0]+.65*walk3[:,1],.35*walk3[:,1]-.9*walk3[:,2]],axis=1)
w=writer('random_walk_2d_3d.mp4')
for frame in range(110):
 idx=min(length,int(length*frame/109));im=np.full((H,W,3),255,np.uint8)
 put(im,'RANDOM WALK: STEP BY STEP', (48,55),1.08,INK,3)
 put(im,'Independent increments; dependent accumulated positions', (50,94),.63,GRAY,2)
 panel(im,48,125,625,624);panel(im,658,125,1233,624)
 put(im,'2D lattice', (80,170),.92,BLUE,2);put(im,'3D lattice (projected view)',(691,170),.92,PURPLE,2)
 cv2.line(im,(337,175),(337,594),(231,227,221),1,cv2.LINE_AA);cv2.line(im,(78,395),(597,395),(231,227,221),1,cv2.LINE_AA)
 cv2.line(im,(945,175),(945,594),(231,227,221),1,cv2.LINE_AA);cv2.line(im,(685,395),(1209,395),(231,227,221),1,cv2.LINE_AA)
 drawtraj(im,walk2[:idx+1],BLUE,(48,125,625,624))
 # center 3d iso projection at 945,395 rather than initial drawing center x945.5 y374.5
 xy=iso[:idx+1];pix=np.stack([945+xy[:,0]*3.45,395-xy[:,1]*3.45],axis=1).astype(np.int32)
 if len(pix)>1:cv2.polylines(im,[pix],False,PURPLE,2,cv2.LINE_AA)
 cv2.circle(im,tuple(pix[0]),6,GREEN,-1,cv2.LINE_AA);cv2.circle(im,tuple(pix[-1]),6,RED,-1,cv2.LINE_AA)
 put(im,f'Step: {idx} / {length}',(52,671),.76,INK,2)
 put(im,'Green = origin     Red = current position', (650,670),.66,GRAY,2)
 w.write(im)
w.release();convert_h264(ROOT/'random_walk_2d_3d.mp4')

P=np.array([[.91,.08,.01],[.06,.78,.16],[.05,.01,.94]])
steady=np.array([1.,0,0]);
for i in range(1000):steady=steady@P
w=writer('markov_stationary.mp4')
for frame in range(110):
 step=min(frame//2,54);pi=np.array([1.,0,0]);
 for i in range(step):pi=pi@P
 im=np.full((H,W,3),255,np.uint8)
 put(im,'MARKOV CHAIN: APPROACH TO STATIONARITY',(43,58),1.00,INK,3)
 put(im,'One illustrative hospital transition matrix (rows sum to 1)',(45,94),.65,GRAY,2)
 panel(im,45,130,1235,600)
 put(im,f'Day {step}',(78,198),.91,INK,2)
 cols=[BLUE,RED,GREEN];names=['Susceptible','Infected','Recovered'];
 for i in range(3):
  yy=260+i*112;put(im,names[i],(90,yy),.75,cols[i],2)
  cv2.rectangle(im,(340,yy-28),(1050,yy+10),LIGHT,-1)
  cv2.rectangle(im,(340,yy-28),(340+int(pi[i]*710),yy+10),cols[i],-1)
  put(im,f'{pi[i]*100:5.1f}%',(1070,yy),.72,cols[i],2)
 put(im,'Converges to a stable distribution for this ergodic transition matrix.',(62,651),.66,INK,2)
 put(im,'Long-run infected share: '+f'{steady[1]*100:.1f}%',(700,686),.62,GRAY,2)
 w.write(im)
w.release();convert_h264(ROOT/'markov_stationary.mp4')
print('Rendered mp4 animations to',ROOT)
