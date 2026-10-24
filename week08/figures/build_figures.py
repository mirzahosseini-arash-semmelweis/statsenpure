"""Generate ready-to-use Week 08 SVG figures (run: python R/build_figures.py).
An optional native ggplot2 regeneration script is provided separately.
"""
import pathlib
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from scipy import stats
from scipy.optimize import least_squares
from scipy.special import expit
from mpl_toolkits.mplot3d import Axes3D  # noqa

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / 'week08' / 'figures'
OUT.mkdir(parents=True,exist_ok=True)
C={'blue':'#1f6feb','orange':'#c65d09','green':'#18864b','red':'#c93838','purple':'#7b4ab5','navy':'#101828','muted':'#667085','line':'#d9e1ea','panel':'#f3f6fa'}
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'axes.labelcolor':C['navy'],'axes.edgecolor':C['line'],'xtick.color':C['muted'],'ytick.color':C['muted'],'text.color':C['navy'],'axes.titleweight':'bold','axes.titlesize':12,'axes.grid':True,'grid.color':'#edf1f7','grid.linewidth':.7,'svg.fonttype':'none','figure.facecolor':'white','axes.facecolor':'white'})
def save(fig,name):
    fig.savefig(OUT/name,format='svg',bbox_inches='tight',facecolor='white')
    plt.close(fig)
def prep(ax):ax.set_axisbelow(True)

# HPLC: chromatographic signal and absorbance calibration
rng=np.random.default_rng(801)
fig,(a,b)=plt.subplots(1,2,figsize=(11.2,3.8),gridspec_kw={'wspace':.27})
x=np.linspace(0,8,800)
y=.018+.04*np.exp(-.5*((x-1.5)/.2)**2)+.87*np.exp(-.5*((x-4.2)/.36)**2)+.05*np.exp(-.5*((x-6.6)/.23)**2)
a.plot(x,y,color=C['blue'],lw=2.8);a.fill_between(x,0,y,color=C['blue'],alpha=.09);a.axvline(4.2,color=C['green'],lw=1.5,ls='--');a.text(4.28,.74,'API peak',color=C['green'],weight='bold');a.set(xlabel='Retention time (min)',ylabel='UV detector response',title='1  HPLC separates the API');prep(a)
c=np.linspace(0,12,9);absorb=.06+.071*c+rng.normal(0,.025,len(c));xx=np.linspace(0,12,100);b.scatter(c,absorb,color=C['blue'],s=43,zorder=3);b.plot(xx,.06+.071*xx,color=C['green'],lw=2.5);b.set(xlabel='Known API concentration (mg/L)',ylabel='Absorbance (AU)',title='2  Standards establish calibration');prep(b);save(fig,'hplc_hook.svg')

# scatter cell culture
rng=np.random.default_rng(802); x=rng.uniform(8,25,62); y=.28+.031*x+rng.normal(0,.16,len(x))
fig,ax=plt.subplots(figsize=(8.2,4.7));ax.scatter(x,y,s=38,color=C['blue'],alpha=.72);fit=np.polyfit(x,y,1);ax.plot([8,25],np.polyval(fit,[8,25]),color=C['green'],lw=2.8);ax.set(xlabel='Cell diameter (µm)',ylabel='Growth rate (divisions/h)',title='Cell size and growth rate: two continuous measurements');prep(ax);save(fig,'cells_scatter.svg')

# correlation gallery 3x3
"""
rng=np.random.default_rng(803);fig,axes=plt.subplots(3,3,figsize=(10.7,8.9));titles=[('Steep + / tight',2.4,.12),('Gentle + / tight',.28,.015),('Positive / loose',.62,.85),('Unrelated',0,1.1),('Constant response',0,0),('Curved, symmetric',None,.2),('Steep − / tight',-2.1,.14),('Gentle − / tight',-.26,.018),('Negative / loose',-.55,.85)]
for k,(name,slope,noise) in enumerate(titles):
 ax=axes.flat[k]; x=np.linspace(-2.5,2.5,58)+rng.normal(0,.08,58)
 if k==5:y=.55*x*x+rng.normal(0,noise,len(x))
 elif k==4:y=np.ones_like(x)*.8
 else:y=slope*x+rng.normal(0,noise,len(x))
 r=np.corrcoef(x,y)[0,1] if np.std(y)>1e-10 else np.nan
 ax.scatter(x,y,s=13,alpha=.78,c=C['blue']);ax.set_title(name,fontsize=10,loc='left');ax.text(.97,.05,f'r = {r:+.2f}' if np.isfinite(r) else 'r undefined',transform=ax.transAxes,ha='right',va='bottom',color=C['purple'],fontweight='bold',fontsize=10);ax.set_xticks([]);ax.set_yticks([]);ax.grid(False)
fig.suptitle('Pearson correlation: strength of linear co-movement, not slope',fontsize=14,weight='bold',y=1.005);fig.tight_layout(pad=1.1);save(fig,'correlation_gallery.svg')
"""

# ordinal category heatmap
arr=np.array([[18,4,1],[7,13,5],[2,7,21]])
fig,ax=plt.subplots(figsize=(6.4,3.8));ax.imshow(arr,cmap='Blues',vmin=0,vmax=24);ax.set_xticks(range(3),['slow','medium','fast']);ax.set_yticks(range(3),['small','medium','large']);ax.set(xlabel='Growth rate (ordinal)',ylabel='Cell size (ordinal)',title='A 3 × 3 contingency table');
for i in range(3):
 for j in range(3):ax.text(j,i,str(arr[i,j]),ha='center',va='center',fontsize=14,weight='bold',color='white' if arr[i,j]>13 else C['navy'])
ax.grid(False);save(fig,'ordinal_table.svg')

# Diagnostics 6 cases 2x2, 6x output
"""
rng=np.random.default_rng(804)
for key,title in [('good_tight','Well-behaved / strong positive'),('good_loose','Well-behaved / weak negative'),('nonnormal','Skewed errors'),('curvature','Unmodeled nonlinear trend'),('outliers','Outliers and influence'),('hetero','Heteroscedastic errors')]:
 n=55;xx=np.linspace(0.6,9.4,n)+rng.normal(0,.10,n)
 e=rng.normal(0,.42,n)
 if key=='good_tight':yy=1.0+.95*xx+e
 if key=='good_loose':yy=7.4-.38*xx+rng.normal(0,1.35,n)
 if key=='nonnormal':yy=1+.8*xx+.7*(rng.exponential(1,n)-1)
 if key=='curvature':yy=3+.18*xx+.08*(xx-5)**3+rng.normal(0,.6,n)
 if key=='outliers':
  yy=1+.72*xx+e;yy[-1]+=6;yy[2]-=4
 if key=='hetero':yy=1+.7*xx+rng.normal(0,.16+.14*xx,n)
 slope,intercept=np.polyfit(xx,yy,1);fit=intercept+slope*xx;res=yy-fit
 sse=np.sum(res*res);s=np.sqrt(sse/(n-2));z=res/s
 leverage=1/n+(xx-np.mean(xx))**2/np.sum((xx-np.mean(xx))**2)
 qqx=stats.norm.ppf((np.arange(n)+.5)/n);qqy=np.sort(z)
 fig,axs=plt.subplots(2,3,figsize=(12.5,6.5));a,b,c,d,e,f=axs.flat
 a.scatter(xx,yy,s=24,color=C['blue'],alpha=.78);a.plot(xx,fit,color=C['green'],lw=2.1);a.set(xlabel='Predictor x',ylabel='Response y',title='Data + fitted line')
 b.scatter(fit,res,s=22,color=C['blue'],alpha=.78);b.axhline(0,color=C['red'],ls='--');b.set(xlabel='Fitted value',ylabel='Residual',title='Residual vs fitted')
 c.scatter(qqx,qqy,s=22,color=C['blue'],alpha=.78);qfit=np.polyfit(qqx,qqy,1);c.plot(qqx,np.polyval(qfit,qqx),color=C['green'],lw=1.8,ls='--');c.set(xlabel='Theoretical normal quantiles',ylabel='Standardized residual',title='Normal QQ')
 d.scatter(fit,np.sqrt(np.abs(z)),s=22,color=C['blue'],alpha=.78);d.set(xlabel='Fitted value',ylabel='sqrt(|std. residual|)',title='Scale–location')
 e.scatter(leverage,z,s=25,color=C['blue'],alpha=.78);e.axhline(0,color=C['red'],ls='--');e.set(xlabel='Leverage',ylabel='Standardized residual',title='Residual vs leverage')
 f.axis('off');f.text(.04,.90,'Diagnostic checklist',transform=f.transAxes,weight='bold',fontsize=12,color=C['navy']);f.text(.05,.69,'• Curvature in residuals?\n• Unequal scatter/variance?\n• Non-normal error tails?\n• High-leverage outliers?',transform=f.transAxes,fontsize=11,color=C['muted'],va='top',linespacing=1.9)
 for aa in axs.flat[:5]:prep(aa)
 fig.suptitle(title,fontsize=14,weight='bold');fig.tight_layout();save(fig,f'diagnostic_{key}.svg')
"""

# transformation choices 4 figs
"""
rng=np.random.default_rng(811)
transforms=[('exponential','Exponential: ln(y) vs x','log(response)','y = a · exp(bx)',lambda x:np.exp(.3+.48*x),lambda y:np.log(y)),('power','Power: ln(y) vs ln(x)','log(response)','y = a · xᵇ',lambda x:1.25*x**1.6,lambda y:np.log(y)),('hyperbolic','Hyperbolic: 1/y vs 1/x','1/response','y = Vmax·x / (Km+x)',lambda x:2.8*x/(2.1+x),lambda y:1/y),('logarithmic','Logarithmic: y vs ln(x)','response','y = a + b·ln(x)',lambda x:1.2+.9*np.log(x),lambda y:y)]
for name,title,yl,eq,f,t in transforms:
 x=np.linspace(.6,6,33);y=f(x)*(1+rng.normal(0,.032,len(x))) if name!='logarithmic' else f(x)+rng.normal(0,.075,len(x))
 tx=np.log(x) if name in ('power','logarithmic') else 1/x if name=='hyperbolic' else x
 ty=t(y)
 fit=np.polyfit(tx,ty,1)
 fig,(a,b)=plt.subplots(1,2,figsize=(10,3.8));a.scatter(x,y,s=30,color=C['blue']);a.plot(x,f(x),color=C['orange'],lw=2.2);a.set(xlabel='x',ylabel='y',title=f'Original: {eq}');
 b.scatter(tx,ty,s=30,color=C['blue']);b.plot(tx,np.polyval(fit,tx),color=C['green'],lw=2.2);b.set(xlabel='ln(x)' if name in ('power','logarithmic') else '1/x' if name=='hyperbolic' else 'x',ylabel=yl,title='Transformed coordinates: straight line');prep(a);prep(b);fig.suptitle(title,weight='bold');fig.tight_layout();save(fig,f'transform_{name}.svg')
"""

# vertical/horizontal/orthogonal residual fits
"""
rng=np.random.default_rng(814);x=np.linspace(0,6,20)+rng.normal(0,.35,20);y=.9+1.15*x+rng.normal(0,.8,len(x));b1,a1=np.polyfit(x,y,1);bx,ax=np.polyfit(y,x,1);bs=1/bx;ass=-ax/bx;z=np.stack([x,y],axis=1);zcenter=np.mean(z,axis=0);ev,V=np.linalg.eigh(np.cov(z.T));v=V[:,-1];borth=v[1]/v[0];aorth=zcenter[1]-borth*zcenter[0]
fig,axs=plt.subplots(1,3,figsize=(11,3.65));
for ax,(label,slope,inter,col) in zip(axs,[('Vertical: regress y on x',b1,a1,C['green']),('Horizontal: regress x on y',bs,ass,C['purple']),('Orthogonal: symmetric TLS',borth,aorth,C['orange'])]):
 ax.scatter(x,y,s=34,c=C['blue'],alpha=.78);xx=np.array([-.3,6.7]);ax.plot(xx,inter+slope*xx,color=col,lw=2.4);ax.set(xlim=(-.4,6.8),ylim=(-1,9),xlabel='x',ylabel='y',title=label);prep(ax)
fig.tight_layout();save(fig,'residual_directions.svg')
"""

# Multiple regression plane + pairs
rng = np.random.default_rng(815)
n = 85
h = rng.normal(171, 9, n)
w = 0.85 * (h - 171) + 73 + rng.normal(0, 7, n)
sbp = 118 + .45 * (w - 73) + .22 * (h - 171) + rng.normal(0, 7, n)
# 1. Compute fitted plane values for individual data points
sbp_fit = 118 + .45 * (w - 73) + .22 * (h - 171)
fig = plt.figure(figsize=(11, 4.4))
ax = fig.add_subplot(121, projection='3d')
# 2. Add faint red vertical residual lines
for wi, hi, sbpi, fiti in zip(w, h, sbp, sbp_fit):
    ax.plot([wi, wi], [hi, hi], [sbpi, fiti], color=C['red'], alpha=0.35, linewidth=0.8)
# 3. Data points & fitted surface
ax.scatter(w, h, sbp, c=C['blue'], s=16, alpha=.6)
gW, gH = np.meshgrid(np.linspace(w.min(), w.max(), 12), np.linspace(h.min(), h.max(), 12))
gP = 118 + .45 * (gW - 73) + .22 * (gH - 171)
ax.plot_surface(gW, gH, gP, color=C['green'], alpha=.24, edgecolor='none')
ax.set(xlabel='Weight (kg)', ylabel='Height (cm)', zlabel='SBP (mmHg)')
ax.set_title('Two predictors → fitted plane', fontsize=11)
# Right subplot
ax2 = fig.add_subplot(122)
ax2.scatter(h, w, c=C['blue'], s=25, alpha=.7)
ax2.set(xlabel='Height (cm)', ylabel='Weight (kg)', title='Predictors correlated: collinearity')
prep(ax2)
fig.tight_layout()
save(fig, 'multiple_regression.svg')

fig,axs=plt.subplots(3,3,figsize=(7.5,7.5));arr=[('Height',h),('Weight',w),('SBP',sbp)]
for i,(name1,da) in enumerate(arr):
 for j,(name2,db) in enumerate(arr):
  ax=axs[i,j];
  if i==j:ax.hist(da,bins=13,color=C['blue'],alpha=.68)
  else:ax.scatter(db,da,s=9,color=C['blue'],alpha=.5)
  ax.grid(False)
  if i==2:ax.set_xlabel(name2,fontsize=9)
  else:ax.set_xticklabels([])
  if j==0:ax.set_ylabel(name1,fontsize=9)
  else:ax.set_yticklabels([])
fig.suptitle('Pairs plot: covariation among predictors and response',fontsize=12,weight='bold');fig.tight_layout();save(fig,'pairs_plot.svg')

# Solvent and wavelength factor models. Dose slopes wavelength-dependent variants
"""
rng=np.random.default_rng(816);lam=[250,280,320];conc=np.linspace(0,10,12);cols=[C['blue'],C['green'],C['purple']]
for kind in ['additive','wavelength_interaction','full_interaction']:
 fig,axs=plt.subplots(1,2,figsize=(10.8,3.9),sharey=True)
 for si,(ax,solvent) in enumerate(zip(axs,['MeOH','Water'])):
  for j,(wl,col) in enumerate(zip(lam,cols)):
   intercept=.07+.055*si+.08*j
   slope=(.065 if kind=='additive' else [.046,.094,.071][j])
   if kind=='full_interaction':slope+=si*[.025,-.02,.03][j]
   y=intercept+slope*conc+rng.normal(0,.024,len(conc))
   ax.scatter(conc,y,color=col,s=21,alpha=.70);ax.plot(conc,intercept+slope*conc,color=col,lw=2,label=f'{wl} nm')
  ax.set(xlabel='Concentration (mg/L)',title=f'{solvent}');prep(ax)
 axs[0].set_ylabel('Absorbance (AU)');axs[1].legend(frameon=False,title='Wavelength',loc='upper left',fontsize=9)
 kindtitle={'additive':'Additive model: parallel concentration slopes','wavelength_interaction':'Concentration × wavelength: slopes differ with λ','full_interaction':'Three-way interaction: wavelength dependence differs by solvent'}[kind]
 fig.suptitle(kindtitle,fontsize=13,weight='bold');fig.tight_layout();save(fig,f'factor_{kind}.svg')

fig,ax=plt.subplots(figsize=(8.6,4));lam=np.linspace(210,360,350)
meoh=.14+.85*np.exp(-.5*((lam-263)/24)**2)+.36*np.exp(-.5*((lam-307)/19)**2)
water=.12+.70*np.exp(-.5*((lam-275)/26)**2)+.42*np.exp(-.5*((lam-319)/18)**2)
ax.plot(lam,meoh,color=C['blue'],lw=2.8,label='MeOH');ax.plot(lam,water,color=C['orange'],lw=2.8,label='Water');ax.set(xlabel='Wavelength (nm)',ylabel='Absorbance (AU)',title='Synthetic API spectra: solvent can change spectral shape');ax.legend(frameon=False);prep(ax);save(fig,'spectra.svg')
"""

# cubic growth and hormone, calibrated polynomial visual
rng=np.random.default_rng(817);size=np.linspace(1,5,50);base=.06+.033*size**3
fig,ax=plt.subplots(figsize=(8.8,4.6));
for shift,color,label in [(0,C['blue'],'No hormone'),(.55,C['orange'],'Hormone present')]:
 y=base+shift+rng.normal(0,.25,len(size));ax.scatter(size,y,color=color,s=22,alpha=.6,label=label);ax.plot(size,base+shift,color=color,lw=2.5)
ax.set(xlabel='Cell size (arbitrary units)',ylabel='Growth rate (divisions/h)',title='Polynomial term captures curvature; factor shifts the response');ax.legend(frameon=False);prep(ax);save(fig,'cubic_hormone.svg')

# titration reference
rng=np.random.default_rng(818);x=np.linspace(1,7,40);y=0+1/(1+10.0**(4-x))+rng.normal(0,0.01,len(x));xx=np.linspace(1,7,400)
fig,ax=plt.subplots(figsize=(8.6,4.5));ax.scatter(x,y,color=C['blue'],s=29,alpha=.75,label='Potentiometric observations');ax.plot(xx,0+1/(1+10.0**(4-xx)),color=C['green'],lw=2.8,label='Theoretical sigmoid');ax.axvline(4.0,color=C['purple'],ls='--',lw=1.8);ax.set(xlabel='pH',ylabel='Titrant volume difference (mL)',title='Illustrative potentiometric titration');ax.legend(frameon=False);prep(ax);save(fig,'titration.svg')

print('Generated', len(list(OUT.glob('*.svg'))),'SVGs:', ', '.join(p.name for p in sorted(OUT.glob('*.svg'))))
