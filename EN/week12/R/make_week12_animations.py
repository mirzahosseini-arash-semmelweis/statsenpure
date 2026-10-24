"""Create self-contained schematic MP4 animations for Week 12 (not Manim)."""
from PIL import Image,ImageDraw,ImageFont
import math,subprocess,numpy as np
from pathlib import Path
O=Path(__file__).resolve().parents[1]/'week12'/'media';O.mkdir(parents=True,exist_ok=True)
W,H=960,540;S=1
C={'navy':'#182230','blue':'#1f6feb','green':'#18864b','purple':'#7b4ab5','orange':'#c65d09','red':'#c93838','light':'#f4f7fb','muted':'#667085'}
try:
 B='/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf'; R='/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
 fbig=ImageFont.truetype(B,28);ftitle=ImageFont.truetype(B,22);ftext=ImageFont.truetype(R,17);fsm=ImageFont.truetype(R,14)
except: fbig=ftitle=ftext=fsm=ImageFont.load_default()
def text(d,pt,s,font=ftext,color='navy',anchor=None):d.text(pt,s,font=font,fill=C.get(color,color),anchor=anchor)
def line(d,a,b,col='muted',width=2):d.line([a,b],fill=C.get(col,col),width=width)
def circ(d,p,r=13,col='blue',outline=None):d.ellipse((p[0]-r,p[1]-r,p[0]+r,p[1]+r),fill=C[col] if col else '#fff',outline=C.get(outline,outline) if outline else None,width=3)
def base(s,title,subtitle):
 im=Image.new('RGB',(W,H),'white');d=ImageDraw.Draw(im)
 d.rectangle((0,0,W,9),fill=C['purple']);text(d,(40,29),title,fbig);text(d,(40,72),subtitle,ftext,'muted');return im,d
def network(d,layers,phase=0,back=False,small=False):
 xs=np.linspace(160,790,len(layers));pts=[]
 for j,(x,n) in enumerate(zip(xs,layers)):
  ys=np.linspace(180,415,n);pts.append([(int(x),int(y)) for y in ys])
 for j in range(len(pts)-1):
  for u in pts[j]:
   for v in pts[j+1]:
    active= (j<=phase if not back else j>=phase)
    line(d,u,v,'purple' if active else 'muted',2 if active else 1)
 for j,arr in enumerate(pts):
  for p in arr:
   circ(d,p,11,'green' if (j<=phase if not back else j>=phase) else 'blue')
 return pts
fps=12;frames=66
def save(name,func):
 cmd=['ffmpeg','-hide_banner','-loglevel','error','-y','-f','rawvideo','-vcodec','rawvideo','-s',f'{W}x{H}','-pix_fmt','rgb24','-r',str(fps),'-i','-','-c:v','libx264','-preset','ultrafast','-crf','25','-pix_fmt','yuv420p',str(O/name)]
 p=subprocess.Popen(cmd,stdin=subprocess.PIPE)
 for i in range(frames):
  im=func(i/frames);p.stdin.write(im.tobytes())
 p.stdin.close();p.wait();print(name,(O/name).stat().st_size)
def perceptron(t):
 im,d=base(t,'A single artificial neuron','Five measured metabolites  →  weighted sum  →  probability')
 xs=[140]*5;ys=[170,225,280,335,390]
 for i,(x,y) in enumerate(zip(xs,ys)):
  circ(d,(x,y),16,'blue');text(d,(95,y),f'x{i+1}',fsm,anchor='rm')
  line(d,(x+18,y),(460,280),'purple' if t>.2 else 'muted',2)
 circ(d,(480,280),52,'purple');text(d,(480,270),'Σ wx+b',ftext,'#ffffff',anchor='mm');text(d,(480,300),'activation',fsm,'#ffffff',anchor='mm')
 line(d,(535,280),(720,280),'purple' if t>.4 else 'muted',4);circ(d,(750,280),36,'green' if t>.55 else 'blue')
 prob=.19+.6*min(1,max(0,(t-.55)/.28));text(d,(750,280),f'{prob:.2f}',ftext,'#ffffff',anchor='mm')
 text(d,(500,460),'One neuron is a small model; the weights determine its response.',ftitle,anchor='mm')
 return im
def multi(t):
 im,d=base(t,'Forward propagation through hidden layers','Input vector  →  nonlinear transformations  →  disease probability')
 pts=network(d,[5,9,9,9,2],phase=int(t*5))
 for xx,s in zip([160,318,475,632,790],['5 features','Hidden 1','Hidden 2','Hidden 3','Output']):text(d,(xx,445),s,fsm,anchor='mm')
 text(d,(480,496),'Each neuron transforms a weighted sum; many layers create flexible functions.',ftext,anchor='mm');return im
def backward(t):
 im,d=base(t,'Learning by backpropagation','A labeled example produces loss; gradients update weights')
 phase=max(0,3-int(t*4));network(d,[5,8,8,8,2],phase=phase,back=True)
 text(d,(760,137),f'Loss: {(.73-.56*t):.2f}',ftitle,'red')
 text(d,(480,480),'Gradient information moves backward; parameter updates reduce training loss.',ftext,anchor='mm');return im
def cnn(t):
 im,d=base(t,'Convolutional neural network · conceptual flow','This visual is illustrative, not the internal activation map of the digit predictor.')
 r=(170,176,318,333);d.rectangle(r,outline=C['blue'],width=3)
 for i in range(14):
  for j in range(14):
   x=172+j*10;y=180+i*10
   v=math.exp(-((i-7)**2+(j-7)**2)/18) *(.5+.5*math.sin(j*.6+i*.7))
   g=int(255-195*v);d.rectangle((x,y,x+9,y+9),fill=(g,g,255))
 text(d,(245,370),'28 × 28 pixels',ftext,anchor='mm');
 for k in range(4):
  x=415+k*63;y=185+(k%2)*19
  cc='purple' if t>(.15+.12*k) else 'muted'
  d.rectangle((x,y,x+45,y+115),fill=C['light'],outline=C[cc],width=4)
  d.line((x+9,y+45,x+36,y+45),fill=C[cc],width=3)
 text(d,(528,370),'Feature maps',ftext,anchor='mm')
 for k in range(10):
  x=742+k*13;y=300-140*(.12+(k==3)*.8)*(min(1,max(0,(t-.5)*3)))
  d.rectangle((x,y,x+10,300),fill=C['green'] if k==3 else C['blue'])
 text(d,(810,370),'Class scores',ftext,anchor='mm')
 d.line((320,260,398,260),fill=C['muted'],width=3);d.line((705,260,735,260),fill=C['muted'],width=3)
 text(d,(480,470),'Spatial filters learn useful local features before final classification.',ftext,anchor='mm');return im
for name,fn in [('perceptron.mp4',perceptron),('feedforward.mp4',multi),('backpropagation.mp4',backward),('cnn_concept.mp4',cnn)]:save(name,fn)
