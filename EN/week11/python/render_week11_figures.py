#!/usr/bin/env python3
"""Recreate synthetic SVG teaching figures for Statistics 101, Week 11.
Run: python python/render_week11_figures.py
All observations simulated; no clinical inference or measured patients.
"""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Polygon, Circle, FancyArrowPatch
from scipy.stats import norm
from scipy.interpolate import make_smoothing_spline

ROOT=Path(__file__).resolve().parents[1]/'week11'/'figures';ROOT.mkdir(parents=True,exist_ok=True)
C={'obs':'#1f6feb','mod':'#c65d09','est':'#18864b','warn':'#c93838','unc':'#7b4ab5','navy':'#101828','muted':'#667085','line':'#d9e1ea','paper':'#fbfcfe'}
rng=np.random.default_rng(202611)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':12,'axes.spines.top':False,'axes.spines.right':False,'axes.edgecolor':'#98a2b3','axes.labelcolor':C['navy'],'text.color':C['navy'],'xtick.color':C['muted'],'ytick.color':C['muted'],'svg.fonttype':'none','savefig.facecolor':'white'})

def save(name,fig):
  fig.savefig(ROOT/f'{name}.svg',bbox_inches='tight',pad_inches=.13,facecolor='white');plt.close(fig)
def styl(ax):
  ax.grid(alpha=.22,color='#98a2b3');ax.set_axisbelow(True)
def labs(ax,x,y,title=None):
  if title:ax.set_title(title,fontweight='bold',pad=10,fontsize=14)
  ax.set_xlabel(x);ax.set_ylabel(y);styl(ax)

# The same-looking XY cloud interpreted as independent units or one time-ordered process
x=np.linspace(0,10,44); y=2.0+4.6*np.exp(-.5*((x-4.4)/1.65)**2)+rng.normal(0,.30,len(x)); y_left=1.5+.62*x+rng.normal(0,.56,len(x))
fig,ax=plt.subplots(1,2,figsize=(12.2,4.1),constrained_layout=True)
ax[0].scatter(x,y_left,s=36,c=C['obs'],alpha=.75);labs(ax[0],'TCR binding affinity (a.u.)','IL-2 response (a.u.)','Independent cells: order is irrelevant')
ax[1].plot(x,y,'-',lw=2,c=C['unc'],alpha=.65);ax[1].scatter(x,y,s=28,c=C['obs']);labs(ax[1],'Hours after infusion','Plasma IL-6 (illustrative)','Repeated measurements: history matters');save('time_vs_independent',fig)

# classes of trajectories
x=np.linspace(0,12,130)
fig,ax=plt.subplots(1,3,figsize=(12,3.7),constrained_layout=True)
forms=[(8+20*(1-np.exp(-x/3)), 'Growth to plateau'), (30*np.exp(-x/3)+3,'Exponential decay'),(3+23*np.exp(-.5*((x-5)/1.55)**2),'Peak and recovery')]
for a,(y,title) in zip(ax,forms):a.plot(x,y,color=C['mod'],lw=3.4);labs(a,'Time','Response',title)
save('trajectory_types',fig)

# PK two group n=10 with jagged observations + mean CI
fig,ax=plt.subplots(figsize=(11.6,4.3));t=np.arange(0,13,.6)
means=[]
for i,(amp,peak,color) in enumerate([(18,3.3,C['obs']),(16,4.4,C['mod'])]):
  curves=[]
  for j in range(10):
    xx=np.maximum(t,0)
    yy=(amp+rng.normal(0,1.9))*np.exp(-.5*((xx-(peak+rng.normal(0,.30)))/1.65)**2)
    yy+=rng.normal(0,1.1,len(t));curves.append(np.clip(yy,0,None));ax.plot(t,curves[-1],lw=.8,alpha=.25,c=color)
  ar=np.array(curves);m=ar.mean(0);se=ar.std(0,ddof=1)/np.sqrt(10)
  ax.plot(t,m,color=color,lw=3,label=['Drug A mean (n=10)','Drug B mean (n=10)'][i]);ax.fill_between(t,m-1.96*se,m+1.96*se,color=color,alpha=.15)
labs(ax,'Hours after dose','Plasma concentration (mg/L)');ax.legend(frameon=False,ncol=2,loc='upper right');save('pk_group_trajectories',fig)

# PK summary annotations
fig, ax = plt.subplots(figsize=(11.8, 4.5))
t = np.linspace(0, 12, 320)
y = 22 * (np.exp(-t / 4) - np.exp(-t / 0.65))
peak = np.argmax(y)
Cmax, tmax = y[peak], t[peak]
threshold = 4.0

# Base PK curve & AUC fill
ax.plot(t, y, color=C['obs'], lw=3.3)
ax.fill_between(t, 0, y, color=C['unc'], alpha=0.12)

# 1. C_max point and t_max drop line + label
ax.plot([tmax, tmax], [0, Cmax], ls='--', c=C['mod'], lw=1.6)
ax.scatter([tmax], [Cmax], s=80, c=C['mod'], zorder=4)
ax.annotate(r'$C_{\mathrm{max}}$', xy=(tmax, Cmax), xytext=(tmax + 0.6, Cmax + 1.8),
            arrowprops=dict(arrowstyle='->', color=C['mod'], lw=1.5),
            color=C['mod'], fontweight='bold', fontsize=12)
# t_max label at bottom of drop line
ax.text(tmax, -1.4, r'$t_{\mathrm{max}}$', color=C['mod'], fontweight='bold', fontsize=12, ha='center', va='top')

# 2. Initial slope of increase (Absorption phase)
t_tang = 0.35
y_tang = 22 * (np.exp(-t_tang / 4) - np.exp(-t_tang / 0.65))
ax.annotate('Initial slope\nof increase', xy=(t_tang, y_tang), xytext=(0.2, 15.5),
            arrowprops=dict(arrowstyle='->', color=C['obs'], lw=1.6, connectionstyle='arc3,rad=0.15'),
            color=C['obs'], fontweight='bold', fontsize=10)

# 3. Time above C_min & C_min threshold line
idx_above = np.where(y >= threshold)[0]
t_start, t_end = t[idx_above[0]], t[idx_above[-1]]

ax.axhline(threshold, color=C['warn'], ls='--', lw=1.6)
# Double-headed arrow spanning time above C_min
ax.annotate('', xy=(t_start, threshold), xytext=(t_end, threshold),
            arrowprops=dict(arrowstyle='<->', color=C['warn'], lw=2.2))
ax.text((t_start + t_end) / 2, threshold + 0.6, r'Time above threshold',
        color=C['warn'], fontweight='bold', fontsize=11, ha='center')
ax.text(0.2, threshold + 0.6, r'$C_{\mathrm{thresh}}$', color=C['warn'], fontweight='bold', fontsize=12)

# 4. C_baseline asymptote line and annotation
ax.axhline(0, color=C['muted'], ls=':', lw=1.5)
ax.annotate(r'$C_{\mathrm{baseline}}$ (asymptote)', xy=(11.2, 0.25), xytext=(7.5, 1.0),
            arrowprops=dict(arrowstyle='->', color=C['muted'], lw=1.5),
            color=C['muted'], fontweight='bold', fontsize=12)

# Area under curve label
ax.text(6.8, 12.5, 'Shaded area = AUC', color=C['unc'], fontweight='bold', fontsize=14,
        bbox=dict(boxstyle='round,pad=0.4,rounding_size=0.3',facecolor='#f0f7ff',edgecolor=C['unc'],linewidth=1.5,alpha=0.92))

labs(ax, 'Time after dose (h)', 'Plasma concentration (mg/L)')
ax.set_ylim(-1.2, 18)
ax.set_xlim(0, 12)

save('pk_anatomy', fig)

# HPLC chromatogram
fig,ax=plt.subplots(figsize=(11.8,3.75));t=np.linspace(0,12,440);y=.07+.22*np.exp(-.5*((t-2)/.25)**2)+1.95*np.exp(-.5*((t-6.6)/.48)**2)+.32*np.exp(-.5*((t-9.4)/.30)**2)
ax.plot(t,y,c=C['obs'],lw=2.9);ax.fill_between(t,0,np.clip(1.95*np.exp(-.5*((t-6.6)/.48)**2),0,None),color=C['est'],alpha=.18);ax.annotate('API retention time',xy=(6.6,2),xytext=(7.5,1.9),arrowprops={'arrowstyle':'->'},fontsize=13,color=C['est']);ax.text(5.92,.65,'Peak area',color=C['est'],fontweight='bold');labs(ax,'Retention time (min)','Detector signal (a.u.)');save('chromatogram',fig)

# BP stabilization repeated within subject
fig,ax=plt.subplots(figsize=(11.5,3.8));t=np.arange(1,7);a=np.array([163,155,146,148,145,147]);b=np.array([151,147,141,139,145,140]);ax.plot(t,a,'o--',c=C['obs'],lw=2.8,label='Patient A');ax.plot(t,b,'o--',c=C['mod'],lw=2.8,label='Patient B');ax.axvspan(2.8,6.2,alpha=.08,color=C['est']);ax.text(4.05,159,'Prespecified stable phase',color=C['est'],fontweight='bold',fontsize=12);labs(ax,'Measurement sequence','Systolic BP (mmHg)');ax.set_xticks(t);ax.legend(frameon=False);save('bp_stabilization',fig)

# temporal fit apparent vs correlation-adjusted uncertainty
fig, ax = plt.subplots(figsize=(11.8, 5))

t = np.linspace(0, 10, 36)
true = 2 + 0.55 * t
eps = np.zeros(36)
for i in range(1, 36):
    eps[i] = 0.80 * eps[i - 1] + rng.normal(0, 0.35)

y = true + eps
p = np.polyfit(t, y, 1)
fit = np.polyval(p, t)

# 1. Calculate realistic hyperbolic regression standard error shape
t_bar = np.mean(t)
se_shape = np.sqrt(1 / len(t) + (t - t_bar) ** 2 / np.sum((t - t_bar) ** 2))

# 2. Scale CIs (Inflation factor accounts for AR(1) autocorrelation)
se_naive = 1.55 * se_shape
se_corr = se_naive * 2.6

# 3. Correlation-aware CI (Outer band, warm tone)
ax.fill_between(
    t,
    fit - se_corr,
    fit + se_corr,
    color=C['unc'],
    alpha=0.18,
    zorder=1,
    label='Correlation-aware CI',
)
ax.plot(t, fit - se_corr, color=C['unc'], ls='--', lw=1.2, alpha=0.7, zorder=1)
ax.plot(t, fit + se_corr, color=C['unc'], ls='--', lw=1.2, alpha=0.7, zorder=1)

# 4. Naive i.i.d. CI (Inner band, cool tone)
ax.fill_between(
    t,
    fit - se_naive,
    fit + se_naive,
    color=C['est'],
    alpha=0.35,
    zorder=2,
    label='Naive i.i.d. CI',
)
ax.plot(t, fit - se_naive, color=C['est'], ls=':', lw=1.2, alpha=0.9, zorder=2)
ax.plot(t, fit + se_naive, color=C['est'], ls=':', lw=1.2, alpha=0.9, zorder=2)

# 5. Fit line and observations
ax.plot(t, fit, color=C['est'], lw=2.5, zorder=3, label='Same fitted trend')
ax.scatter(
    t,
    y,
    s=30,
    c=C['obs'],
    edgecolor='white',
    linewidth=0.6,
    zorder=4,
    label='Repeated readings',
)

labs(ax, 'Time', 'Measurement')
ax.set_xlim(0, 10)
ax.legend(frameon=False, ncol=2, fontsize=12, loc='upper left')

save('temporal_band_warning', fig)

# ACF panels AR1, CS, white noise, random walk (difference vs level)
fig,ax=plt.subplots(1,3,figsize=(12.4,3.8),constrained_layout=True);lags=np.arange(0,13)
for a,y,title,color in zip(ax,[.72**lags,np.r_[1,np.full(12,.45)],np.r_[1,np.zeros(12)]],['AR(1): decaying memory','Compound symmetry','White noise: no lag memory'],[C['obs'],C['unc'],C['mod']]):
 a.vlines(lags,0,y,colors=color,lw=3);a.scatter(lags,y,color=color);a.set_ylim(-.12,1.14);labs(a,'Lag','Correlation',title)
save('acf_structures',fig)

# random walk 2d/3d trajectory still
steps=np.random.default_rng(101).choice([-1,1],size=(800,3))*np.random.default_rng(1018).integers(0,2,size=(800,3));arr=np.cumsum(np.vstack(([0,0,0],steps)),axis=0)
fig=plt.figure(figsize=(12.5,4.3));a=fig.add_subplot(121);b=fig.add_subplot(122,projection='3d');a.plot(arr[:,0],arr[:,1],color=C['unc'],lw=1.3);a.scatter([0],[0],c=C['est'],s=60);a.scatter([arr[-1,0]],[arr[-1,1]],c=C['warn'],s=60);a.set_title('2D lattice walk · example realization',fontweight='bold');a.set_xlabel('x');a.set_ylabel('y');a.grid(alpha=.2)
b.plot(arr[:,0],arr[:,1],arr[:,2],color=C['unc'],lw=1.1);b.scatter([0],[0],[0],c=C['est'],s=40);b.scatter([arr[-1,0]],[arr[-1,1]],[arr[-1,2]],c=C['warn'],s=40);b.set_title('3D lattice walk · example realization',fontweight='bold');save('randomwalk_still',fig)

# decomposition
n=180;t=np.arange(n);trend=2+.018*t+.00003*t*t;season=.95*np.sin(t*2*np.pi/30);cycle=.42*np.sin(t*2*np.pi/105);noise=rng.normal(0,.32,n);obs=trend+season+cycle+noise
fig,ax=plt.subplots(4,1,figsize=(11.8,8.4),sharex=True,gridspec_kw={'hspace':.29});arrs=[(obs,'Observed = all components',C['obs']),(trend,'Smooth trend',C['est']),(season+cycle,'Seasonal + slower cycle',C['unc']),(noise,'Irregular component',C['mod'])]
for a,(y,txt,color) in zip(ax,arrs):a.plot(t,y,color=color,lw=1.8);a.set_ylabel(txt,rotation=0,labelpad=90,fontsize=14,va='center');a.grid(alpha=.16)
ax[-1].set_xlabel('Time index');save('decomposition',fig)

# Fourier filtering
n=512;t=np.linspace(0,12,n,endpoint=False);trend=.18*t;slow=2.2*np.sin(2*np.pi*t/6);signal=.8*np.sin(2*np.pi*t/.9);noise=rng.normal(0,.65,n);y=trend+slow+signal+noise
F=np.fft.rfft(y);freq=np.fft.rfftfreq(n,d=t[1]-t[0]);keep=(freq>=.14)&(freq<=1.5);filtered=np.fft.irfft(F*keep,n=n)
fig,ax=plt.subplots(2,1,figsize=(11.8,5),gridspec_kw={'hspace':.48})
ax[0].plot(t,y,c=C['obs'],lw=1.1,alpha=.6,label='Observed noisy signal');ax[0].plot(t,filtered,c=C['est'],lw=2.3,label='Band-pass reconstruction');ax[0].legend(frameon=False,ncol=2,fontsize=10);labs(ax[0],'Time','Signal')
ax[1].plot(freq,np.abs(F)/n*2,c=C['unc'],lw=1.5);ax[1].axvspan(.14,1.5,alpha=.1,color=C['est']);ax[1].set_xlim(0,4);labs(ax[1],'Frequency (cycles / time)','Magnitude','Keep a frequency band · discard others');save('fourier_filter',fig)

# deconvolution cartoon - truth spikes H kernel blurred + recovered illustrative
x=np.arange(0,220);sp=np.zeros(220);sp[[25,61,109,151,182]]=[1,1.3,.8,1.15,.9];h=np.arange(55);kernel=(h/7)**5*np.exp(-h/7);kernel/=kernel.sum();blur=np.convolve(sp,kernel,mode='full')[:220];noisy=blur+rng.normal(0,.005,len(blur));fftY=np.fft.rfft(noisy);fftH=np.fft.rfft(np.r_[kernel,np.zeros(len(x)-len(kernel))]);recover=np.fft.irfft(fftY*np.conj(fftH)/(np.abs(fftH)**2+.055),n=len(x));
fig,ax=plt.subplots(3,1,figsize=(12,5.5),sharex=True,gridspec_kw={'hspace':.25})
for a,y,c,lab in zip(ax,[sp,noisy,recover],[C['obs'],C['mod'],C['est']],[r"""Latent spikes
$x(t)$""",r"""Blurred observed response
$y(t)$""",r"""Regularized estimate
$\hat{x}(t)$"""]):a.plot(x,y,color=c,lw=1.9);a.set_ylabel(lab,rotation=0,labelpad=95,fontsize=12,va='center');a.grid(alpha=.15)
ax[-1].set_xlabel('Sample index');save('deconvolution',fig)

# censor and truncation diagram timeline
fig, ax = plt.subplots(figsize=(11.5, 5.2))

# Color palette definition
C = {
    'obs': '#1d4ed8',   # Blue: Still alive / under observation
    'warn': '#dc2626',  # Red: Event occurred ('X')
    'unc': '#64748b',   # Grey: Post-event exposure / interval bounds
    'muted': '#94a3b8'  # Light grey: Study start & end vertical lines
}

cases = [
    ("Complete observation", [
        ('alive', -2.5, 6.5),
        ('event', 6.5, None),
        ('exposed', 6.5, 10.0)
    ]),
    ("Left censored", [
        ('alive', -2.5, -1.5),
        ('event', -1.5, None),
        ('exposed', -1.5, 0.0)
    ]),
    ("Right censored (fixed cutoff)", [
        ('alive', -2.5, 10.0),
        ('censor_tick', 10.0, None)
    ]),
    ("Right censored (ongoing)", [
        ('alive_arrow', -2.5, 11.5)
    ]),
    ("Right censored (dropout)", [
        ('alive', -2.5, 8.0),
        ('question', 8.0, None)
    ]),
    ("Interval censored", [
        ('alive', -2.5, 4.0),
        ('interval', 4.0, 7.0),
        ('exposed', 7.0, 10.0)
    ]),
    ("Left truncated (unobserved)", [
        ('alive', -2.5, -0.5),
        ('event', -0.5, None)
    ]),
    ("Right truncated (selected entry)", [
        ('alive', -2.5, 0.0),
        ('alive', 10.0, 11.5),
        ('event', 11.5, None)
    ])
]

y_positions = range(len(cases) - 1, -1, -1)

for y, (label, elements) in zip(y_positions, cases):
    # Right-aligned scenario label
    ax.text(12.3, y, label, va='center', ha='left', fontsize=11, fontweight='bold', color='#0f172a')
    
    for elem in elements:
        kind = elem[0]
        if kind == 'alive':
            ax.plot([elem[1], elem[2]], [y, y], color=C['obs'], lw=3.8, solid_capstyle='round', zorder=3)
        elif kind == 'alive_arrow':
            ax.add_patch(FancyArrowPatch((elem[1], y), (elem[2], y), arrowstyle='-|>', mutation_scale=14, color=C['obs'], lw=3.2, zorder=3))
        elif kind == 'exposed':
            ax.plot([elem[1], elem[2]], [y, y], color=C['unc'], lw=2, ls='--', zorder=2)
        elif kind == 'event':
            ax.scatter([elem[1]], [y], color=C['warn'], s=85, marker='X', zorder=5)
        elif kind == 'censor_tick':
            ax.plot([elem[1], elem[1]], [y - 0.22, y + 0.22], color=C['obs'], lw=3, zorder=5)
        elif kind == 'question':
            ax.text(elem[1], y, '?', color=C['unc'], ha='center', va='center', fontweight='bold', fontsize=11, bbox=dict(boxstyle='square,pad=0.12', facecolor='white', edgecolor='none'))
        elif kind == 'interval':
            a, b = elem[1], elem[2]
            ax.plot([a, b], [y, y], color=C['unc'], lw=2, ls=':', zorder=2)
            ax.text(a, y, '?', color=C['unc'], ha='center', va='center', fontweight='bold', fontsize=11, bbox=dict(boxstyle='square,pad=0.12', facecolor='white', edgecolor='none'))
            ax.text(b, y, '?', color=C['unc'], ha='center', va='center', fontweight='bold', fontsize=11, bbox=dict(boxstyle='square,pad=0.12', facecolor='white', edgecolor='none'))
            ax.scatter([(a + b) / 2], [y], color=C['warn'], s=65, marker='X', zorder=5, alpha=0.75)

# Study Start (t = 0) and End (t = 10) boundaries
ax.axvline(0, color=C['muted'], lw=1.5, ls='--', zorder=1)
ax.axvline(10, color=C['muted'], lw=1.5, ls='--', zorder=1)

# Time axis along the bottom
y_axis = -0.8
ax.plot([-3, 13], [y_axis, y_axis], color='#334155', lw=1.2, zorder=3)
for x_t in range(-3, 14):
    ax.plot([x_t, x_t], [y_axis - 0.08, y_axis + 0.08], color='#334155', lw=1.0)
    if x_t in [0, 10]:
        ax.text(x_t, y_axis - 0.35, str(x_t), ha='center', va='top', fontsize=10, fontweight='bold', color='#0f172a')
    else:
        ax.text(x_t, y_axis - 0.35, str(x_t), ha='center', va='top', fontsize=9, color='#64748b')

ax.text(4.5, y_axis - 0.85, 'Time', ha='center', va='top', fontsize=11, fontweight='bold', color='#0f172a')

# Header annotations for study limits
ax.text(0, 7.7, 'Start of study', ha='center', va='bottom', fontsize=10, color='#334155', fontweight='bold')
ax.text(10, 7.7, 'End of study', ha='center', va='bottom', fontsize=10, color='#334155', fontweight='bold')

ax.set_xlim(-3.6, 17.5)
ax.set_ylim(-2.0, 8.3)
ax.axis('off')

save('censoring_truncation', fig)

# survival Kaplan meier group n ~ 65; deterministic generation
rng=np.random.default_rng(99)
def km(times,events):
 uniq=np.unique(times[events]);ss=[1.];tt=[0.];risk=[];censors=[]
 for t in uniq:
  at=(times>=t).sum();d=((times==t)&events).sum();ss.append(ss[-1]*(1-d/at));tt.append(t);risk.append((t,at,d))
 censors=list(times[~events]);return np.array(tt),np.array(ss),risk,censors
fig,ax=plt.subplots(figsize=(11.8,4.4))
for color,scale,name in [(C['obs'],9,'Standard therapy'),(C['est'],15,'Investigational therapy')]:
 n=76;event=rng.exponential(scale,n);cens=rng.uniform(8,23,n);obs=np.minimum(event,cens);status=event<=cens;tt,ss,risk,censor=km(obs,status)
 ax.step(np.r_[tt,25],np.r_[ss,ss[-1]],where='post',color=color,lw=2.8,label=name)
 for ct in censor:
  v=ss[np.searchsorted(tt,ct,side='right')-1];ax.scatter([ct],[v],marker='+',color=color,s=20,lw=.8)
 ax.fill_between(tt,np.clip(ss-.065,0,1),np.clip(ss+.065,0,1),step='post',color=color,alpha=.08)
ax.set_xlim(0,25);ax.set_ylim(0,1.04);labs(ax,'Months from enrollment','Estimated event-free survival S(t)');ax.legend(frameon=False,fontsize=11);ax.text(16,.88,'+ = right censored\nBands illustrative',fontsize=10,color=C['muted']);save('km_two_groups',fig)

# hazard shapes
fig,ax=plt.subplots(figsize=(11.8,3.9));t=np.linspace(0,10,200);ax.plot(t,.045+.018*t,c=C['warn'],lw=3,label='Increasing · wear-out');ax.plot(t,.28*np.exp(-t/2.5)+.018,c=C['est'],lw=3,label='Decreasing · early vulnerability');ax.plot(t,np.full_like(t,.12),c=C['unc'],lw=3,label='Constant · exponential survival');labs(ax,'Time','Instantaneous hazard (per time)');ax.legend(frameon=False,ncol=3,fontsize=10);ax.set_ylim(0,.37);save('hazard_shapes',fig)

# Cox proportional hazards curves
fig,ax=plt.subplots(1,2,figsize=(12,4),constrained_layout=True);t=np.linspace(0,12,260);h0=.045+.015*t
for mult,label,col in [(1,'Baseline',C['obs']),(1.8,'HR = 1.8',C['warn']),(.60,'HR = 0.6',C['est'])]:
 ax[0].plot(t,mult*h0,c=col,lw=2.6,label=label);S=np.exp(-mult*(.045*t+.0075*t*t));ax[1].plot(t,S,c=col,lw=2.6,label=label)
labs(ax[0],'Time','Instantaneous hazard','Hazard changes with time');labs(ax[1],'Time','Survival S(t)','Relative hazards are proportional');ax[0].legend(frameon=False);save('cox_profiles',fig)

# parametric survival distribution
fig,ax=plt.subplots(figsize=(11,3.6));t=np.linspace(0,16,280)
ax.plot(t,np.exp(-t/7),c=C['obs'],lw=2.5,label='Exponential');ax.plot(t,np.exp(-(t/8)**1.8),c=C['mod'],lw=2.5,label='Weibull');ax.plot(t,1-norm.cdf((np.log(np.maximum(t,.001))-np.log(7))/.5),c=C['unc'],lw=2.5,label='Lognormal');labs(ax,'Time','Survival probability');ax.set_ylim(0,1.04);ax.legend(frameon=False,ncol=3);save('survival_families',fig)

# missing data modeling
fig,ax=plt.subplots(figsize=(11.4,4));x=np.linspace(0,12,70);y=2+1.1*np.sin(x/2)+rng.normal(0,.22,len(x));missing=np.array([10,11,12,27,28,46,47,48,49,63]);keep=np.ones(len(x),bool);keep[missing]=False;ax.scatter(x[keep],y[keep],c=C['obs'],s=35,label='Observed',zorder=3);ax.scatter(x[~keep],(2+1.1*np.sin(x/2))[~keep],c=C['est'],marker='D',s=50,label='Imputed estimate',zorder=4);ax.plot(x,2+1.1*np.sin(x/2),color=C['mod'],lw=2.4,label='Illustrative fitted mean');ax.fill_between(x,2+1.1*np.sin(x/2)-.38,2+1.1*np.sin(x/2)+.38,color=C['unc'],alpha=.10);labs(ax,'Visit time','Biomarker');ax.legend(frameon=False,ncol=3);save('model_imputation',fig)

# Prior GP conceptual
fig,ax=plt.subplots(figsize=(11.2,3.8));x=np.linspace(0,10,200);f=np.sin(1.3*x)+.27*x-1;ax.plot(x,f,color=C['mod'],lw=2.1,ls='--',label='Unknown truth (illustration)');ax.fill_between(x,-1.96,1.96,color=C['unc'],alpha=.13,label='Uninformed prior range');ax.axhline(0,c=C['est'],lw=2,label='Prior mean');labs(ax,'Experimental condition','Output response');ax.legend(frameon=False,ncol=3,fontsize=10);save('gp_prior',fig)

# Markov diagram n states with arrows - optional guide slide
# ------------------------------------------------------------
# Clean Markov state diagram: 3 states on an equilateral triangle
# ------------------------------------------------------------

fig, ax = plt.subplots(figsize=(7.2, 6.2))
ax.set_xlim(0, 10)
ax.set_ylim(0, 8.7)
ax.set_aspect('equal')
ax.axis('off')

# ------------------------------------------------------------
# Geometry: equilateral triangle
# ------------------------------------------------------------

cx, cy = 5.0, 4.3          # triangle center
side = 5.0
h = np.sqrt(3) / 2 * side

# Corners of an equilateral triangle
pos = {
    "Susceptible": (cx, cy + 2*h/3),
    "Infected":    (cx - side/2, cy - h/3),
    "Recovered":   (cx + side/2, cy - h/3),
}

# ------------------------------------------------------------
# Colors
# (assumes you already have C defined; otherwise use fallback)
# ------------------------------------------------------------

try:
    col_S = C['obs']
    col_I = C['warn']
    col_R = C['est']
    col_back = C['unc']
except NameError:
    col_S = "#2563eb"   # blue
    col_I = "#dc2626"   # red/orange
    col_R = "#059669"   # green
    col_back = "#7c3aed"  # purple

node_colors = {
    "Susceptible": col_S,
    "Infected": col_I,
    "Recovered": col_R,
}

# ------------------------------------------------------------
# Helpers
# ------------------------------------------------------------

node_r = 0.78

def draw_state(x, y, label, color):
    # soft halo
    ax.add_patch(
        Circle((x, y), node_r, facecolor=color, edgecolor="none", alpha=0.13, zorder=1)
    )
    # crisp outline
    ax.add_patch(
        Circle((x, y), node_r, facecolor="white", edgecolor=color, linewidth=2.2, zorder=2)
    )
    # label
    ax.text(
        x, y, label,
        ha='center', va='center',
        fontsize=10.5, fontweight='bold',
        color=color, zorder=3
    )

def shrink_segment(p1, p2, shrink=node_r * 0.92):
    p1 = np.array(p1, dtype=float)
    p2 = np.array(p2, dtype=float)
    v = p2 - p1
    u = v / np.linalg.norm(v)
    return p1 + shrink*u, p2 - shrink*u

def draw_transition(p1, p2, label, color, rad=0.0, dx=0.0, dy=0.0):
    a, b = shrink_segment(p1, p2)
    patch = FancyArrowPatch(
        a, b,
        arrowstyle='-|>',
        mutation_scale=16,
        linewidth=2.2,
        color=color,
        connectionstyle=f"arc3,rad={rad}",
        zorder=4
    )
    ax.add_patch(patch)

    mx, my = (a + b) / 2
    ax.text(
        mx + dx, my + dy, label,
        ha='center', va='center',
        fontsize=13.5,
        color=color,
        fontweight='bold',
        zorder=5
    )

def draw_self_loop(x, y, label, color, where="top"):
    if where == "top":
        start = (x - 0.42, y + 0.68)
        end   = (x + 0.42, y + 0.68)
        textx, texty = x, y + 1.45
        rad = -1.25

    elif where == "left":
        start = (x - 0.62, y - 0.48)
        end   = (x - 0.72, y + 0.28)
        textx, texty = x - 2.05, y
        rad = -1.85

    elif where == "right":
        start = (x + 0.72, y + 0.28)
        end   = (x + 0.62, y - 0.48)
        textx, texty = x + 2.08, y
        rad = -1.85

    patch = FancyArrowPatch(
        start, end,
        arrowstyle='-|>',
        mutation_scale=14,
        linewidth=2.0,
        color=color,
        connectionstyle=f"arc3,rad={rad}",
        zorder=4
    )
    ax.add_patch(patch)

    ax.text(
        textx, texty, f"stay {label}",
        ha='center', va='center',
        fontsize=10.8,
        fontweight='bold',
        color=color,
        zorder=5
    )

# ------------------------------------------------------------
# Draw nodes
# ------------------------------------------------------------

for state, (x, y) in pos.items():
    draw_state(x, y, state, node_colors[state])

# ------------------------------------------------------------
# Draw edge transitions around the triangle
# ------------------------------------------------------------

S = pos["Susceptible"]
I = pos["Infected"]
R = pos["Recovered"]

# Susceptible -> Infected
draw_transition(S, I, "0.08", col_I, rad=0.20, dx=-0.8, dy=0.30)
draw_transition(I, S, "0.06", col_S, rad=0.20, dx=0.9, dy=0.10)

# Infected -> Recovered
draw_transition(I, R, "0.16", col_R, rad=0.20, dx=0.00, dy=-0.60)
draw_transition(R, I, "0.01", col_I, rad=0.20, dx=0.00, dy=0.55)

# Recovered -> Susceptible
draw_transition(R, S, "0.05", col_S, rad=0.20, dx=0.8, dy=0.30)
draw_transition(S, R, "0.01", col_R, rad=0.20, dx=-0.7, dy=-0.30)

# ------------------------------------------------------------
# Self-loops
# ------------------------------------------------------------

draw_self_loop(*S, "0.91", col_S, where="top")
draw_self_loop(*I, "0.78", col_I, where="left")
draw_self_loop(*R, "0.94", col_R, where="right")

# Optional title
ax.set_title("Three-state Markov model", fontsize=16, weight='bold', pad=8)

plt.tight_layout()
save('markov_states', fig)

# Fourier transform
# Color palette matching the artwork
COLOR_DARK_BLUE = '#01527d'     # Primary signal & 3D component curves
COLOR_MID_BLUE = '#006699'      # FT arrow & label text
COLOR_LIGHT_BLUE = '#7a9eb3'    # Component curves on Time Domain plane
PLANE_FILL = '#d2e1ed'          # Translucent plane fill
PLANE_BORDER = '#8baec6'        # Edge borders for planes
AXIS_COLOR = '#111111'          # 3D Coordinate axes
DOTTED_COLOR = '#333333'        # Projection guidelines

fig, ax = plt.subplots(figsize=(11, 6))
ax.axis('off')
ax.set_xlim(-0.02, 1.08)
ax.set_ylim(-0.28, 0.72)

# -------------------------------------------------------------
# 3D ISOMETRIC PROJECTION MATRIX
# -------------------------------------------------------------
O_x, O_y = 0.28, 0.18  # Origin in 2D display space

v_t = np.array([0.20, -0.10])  # Time axis vector (down-right)
v_f = np.array([0.28, 0.20])   # Frequency axis vector (up-right)
v_a = np.array([0.0, 0.44])    # Amplitude axis vector (up)

def P(t, f, a):
    """Maps 3D coordinates (time, freq, amp) into 2D display space."""
    pt = np.array([O_x, O_y]) + t * v_t + f * v_f + a * v_a
    return pt[0], pt[1]

# -------------------------------------------------------------
# 1. TIME DOMAIN PLANE (Left)
# -------------------------------------------------------------
# Plane quad in display coordinates
td_p1 = P(0, -0.62, -0.22)  # bottom-left
td_p2 = P(0, -0.62, 0.82)   # top-left
td_p3 = P(0.85, -0.62, 0.82) # top-right
td_p4 = P(0.85, -0.62, -0.22)# bottom-right

poly_td = Polygon([td_p1, td_p2, td_p3, td_p4],
                  facecolor=PLANE_FILL, edgecolor=PLANE_BORDER, lw=1.5, zorder=1)
ax.add_patch(poly_td)

# Signals inside Left Plane (straight across the plane)
t_arr = np.linspace(0, 0.85, 300)
c1_val = 0.10 * np.sin(2 * np.pi * 2.2 * (t_arr / 0.85))
c2_val = 0.05 * np.sin(2 * np.pi * 5.5 * (t_arr / 0.85))
c_sum = c1_val + c2_val

# Points mapped straight along the plane baseline (f = -0.32, a = 0.30)
pts_td_c1 = [P(t, -0.62, 0.30 + a1) for t, a1 in zip(t_arr, c1_val)]
pts_td_c2 = [P(t, -0.62, 0.30 + a2) for t, a2 in zip(t_arr, c2_val)]
pts_td_sum = [P(t, -0.62, 0.30 + a) for t, a in zip(t_arr, c_sum)]

ax.plot([p[0] for p in pts_td_c1], [p[1] for p in pts_td_c1], color=COLOR_LIGHT_BLUE, lw=1.3, zorder=2)
ax.plot([p[0] for p in pts_td_c2], [p[1] for p in pts_td_c2], color=COLOR_LIGHT_BLUE, lw=1.3, zorder=2)
ax.plot([p[0] for p in pts_td_sum], [p[1] for p in pts_td_sum], color=COLOR_DARK_BLUE, lw=3.0, zorder=3)

# -------------------------------------------------------------
# 2. 3D COORDINATE AXES
# -------------------------------------------------------------
p_O = P(0, 0, 0)
p_tmax = P(1.05, 0, 0)
p_amax = P(0, 0, 1.05)

ax.annotate('', xy=p_amax, xytext=p_O,
            arrowprops=dict(arrowstyle='->', color=AXIS_COLOR, lw=1.5, mutation_scale=12))
ax.annotate('', xy=p_tmax, xytext=p_O,
            arrowprops=dict(arrowstyle='->', color=AXIS_COLOR, lw=1.5, mutation_scale=12))

# -------------------------------------------------------------
# 3. 3D DECOMPOSED SINE WAVES
# -------------------------------------------------------------
f1_pos = 0.18
f2_pos = 0.72
t_wave = np.linspace(0, 0.85, 300)
a_base = 0.30

# Component 1 (Low Frequency, High Amplitude)
w1_amp = 0.32 * np.sin(2 * np.pi * 2.2 * (t_wave / 0.85))
pts_w1 = [P(t, f1_pos, a_base + a) for t, a in zip(t_wave, w1_amp)]
ax.plot([p[0] for p in pts_w1], [p[1] for p in pts_w1], color=COLOR_DARK_BLUE, lw=2.6, zorder=4)

# Component 2 (High Frequency, Low Amplitude)
w2_amp = 0.16 * np.sin(2 * np.pi * 5.5 * (t_wave / 0.85))
pts_w2 = [P(t, f2_pos, a_base + a) for t, a in zip(t_wave, w2_amp)]
ax.plot([p[0] for p in pts_w2], [p[1] for p in pts_w2], color=COLOR_DARK_BLUE, lw=2.6, zorder=4)

# -------------------------------------------------------------
# 4. FREQUENCY DOMAIN PLANE (Right - Positioned farther away at t = 1.45)
# -------------------------------------------------------------
fd_t = 1.45
fd_p1 = P(fd_t, -0.08, -0.08)  # bottom-left
fd_p2 = P(fd_t, -0.08, 0.95)   # top-left
fd_p3 = P(fd_t, 0.95, 0.95)    # top-right
fd_p4 = P(fd_t, 0.95, -0.08)   # bottom-right

poly_fd = Polygon([fd_p1, fd_p2, fd_p3, fd_p4],
                  facecolor=PLANE_FILL, edgecolor=PLANE_BORDER, lw=1.5, zorder=1)
ax.add_patch(poly_fd)

# Spectrum curve on Frequency Domain plane
f_grid = np.linspace(-0.05, 0.90, 500)
spec_pts = []

for f in f_grid:
    h1 = 0.32 * max(0, 1 - abs(f - f1_pos) / 0.012)
    h2 = 0.16 * max(0, 1 - abs(f - f2_pos) / 0.012)
    amp = a_base + max(h1, h2)
    spec_pts.append(P(fd_t, f, amp))

ax.plot([p[0] for p in spec_pts], [p[1] for p in spec_pts], color='black', lw=2.2, zorder=5)

# -------------------------------------------------------------
# 5. CORRECTED GUIDELINES (Connecting 3D waves parallel to Time axis)
# -------------------------------------------------------------
"""
# Guideline 1: Component 1 Baseline -> Spectrum Baseline at f1
p_w1_base_start = P(0.85, f1_pos, a_base)
p_w1_base_end = P(fd_t, f1_pos, a_base)
ax.plot([p_w1_base_start[0], p_w1_base_end[0]], [p_w1_base_start[1], p_w1_base_end[1]],
        color=DOTTED_COLOR, ls=':', lw=1.3, zorder=2)
"""
# Guideline 2: Component 1 Peak -> Spectrum Peak 1 at f1
t_pk1 = 0.85 * (1.0 / 4.0) / 2.2 + 0.01  # first peak location of wave 1
p_w1_peak_start = P(t_pk1, f1_pos, a_base + 0.32)
p_w1_peak_end = P(fd_t, f1_pos, a_base + 0.32)
ax.plot([p_w1_peak_start[0], p_w1_peak_end[0]], [p_w1_peak_start[1], p_w1_peak_end[1]],
        color=DOTTED_COLOR, ls=':', lw=1.3, zorder=2)
"""
# Guideline 3: Component 2 Baseline -> Spectrum Baseline at f2
p_w2_base_start = P(0.85, f2_pos, a_base)
p_w2_base_end = P(fd_t, f2_pos, a_base)
ax.plot([p_w2_base_start[0], p_w2_base_end[0]], [p_w2_base_start[1], p_w2_base_end[1]],
        color=DOTTED_COLOR, ls=':', lw=1.3, zorder=2)
"""
# Guideline 4: Component 2 Peak -> Spectrum Peak 2 at f2
t_pk2 = 0.85 * (1.0 / 4.0) / 5.5 + 0.01  # first peak location of wave 2
p_w2_peak_start = P(t_pk2, f2_pos, a_base + 0.16)
p_w2_peak_end = P(fd_t, f2_pos, a_base + 0.16)
ax.plot([p_w2_peak_start[0], p_w2_peak_end[0]], [p_w2_peak_start[1], p_w2_peak_end[1]],
        color=DOTTED_COLOR, ls=':', lw=1.3, zorder=2)

# -------------------------------------------------------------
# 6. LABELS AND FT ARROW AT BOTTOM
# -------------------------------------------------------------
ax.text(0.12, -0.15, 'Time Domain', ha='center', va='center', fontsize=12, fontstyle='italic', fontweight='bold')
ax.text(0.12, -0.22, 's(t)', ha='center', va='center', fontsize=12, fontstyle='italic')

ax.text(0.66, -0.15, 'Frequency Domain', ha='center', va='center', fontsize=12, fontstyle='italic', fontweight='bold')
ax.text(0.66, -0.22, 'S(ω)', ha='center', va='center', fontsize=12, fontstyle='italic')

# Big FT Arrow
ax.annotate('', xy=(0.48, -0.18), xytext=(0.32, -0.18),
            arrowprops=dict(arrowstyle='->,head_width=0.45,head_length=0.6', color=COLOR_MID_BLUE, lw=3.8))
ax.text(0.40, -0.11, 'FT', ha='center', va='center', fontsize=22, color=COLOR_MID_BLUE, fontweight='bold', fontstyle='italic')

# Save vector graphic SVG
plt.savefig('fourier_transform.svg', format='svg', bbox_inches='tight')

# Spline
# ------------------------------------------------------------
# Presentation palette
# ------------------------------------------------------------

BLUE_DOTS = "#2563eb"       # noisy data
PURPLE_SMOOTH = "#7c3aed"   # full smoothing spline
MUTED = "#64748b"
DARK = "#1f2937"
LIGHT_GRID = "#e5e7eb"

# alternating purple shades so adjoining pieces are visible
PIECE_COLORS = [
    "#6d28d9",
    "#a78bfa",
    "#6d28d9",
    "#a78bfa",
    "#6d28d9",
    "#a78bfa",
    "#6d28d9",
]

# ------------------------------------------------------------
# 1. Generate the same synthetic data as in the animations
# ------------------------------------------------------------

rng = np.random.default_rng(101)

x_start, x_end = 0, 10
n = 120
x_data = np.linspace(x_start, x_end, n)

y_true = np.sin(x_data) + 0.5 * np.cos(2 * x_data) + 0.3 * x_data
y_noisy = y_true + rng.normal(0, 0.25, size=n)

# ------------------------------------------------------------
# 2. Fit smoothing spline
#    Set lambda manually for desired smoothness
# ------------------------------------------------------------

LAMBDA = 0.02

spline = make_smoothing_spline(
    x_data,
    y_noisy,
    lam=LAMBDA
)

x_dense = np.linspace(x_start, x_end, 900)
y_dense = spline(x_dense)

# ------------------------------------------------------------
# 3. Choose 6 illustrative knot locations
#
# These are illustrative only. A classical smoothing spline
# is constructed globally; we are selecting a small number of
# visible knot positions so the adjoining pieces can be seen.
# ------------------------------------------------------------

n_knots = 6
knot_x = np.linspace(1.2, 8.8, n_knots)
knot_y = spline(knot_x)

# include boundaries so the entire curve is split into pieces
breaks = np.concatenate([[x_start], knot_x, [x_end]])

# ------------------------------------------------------------
# 4. Figure setup
# ------------------------------------------------------------

fig, ax = plt.subplots(figsize=(10.5, 5.6))

# noisy points
ax.scatter(
    x_data,
    y_noisy,
    s=22,
    color=BLUE_DOTS,
    alpha=0.55,
    edgecolors="none",
    zorder=2,
)

# ------------------------------------------------------------
# 5. Draw adjoining cubic pieces as segmented spline pieces
# ------------------------------------------------------------

for i in range(len(breaks) - 1):
    left = breaks[i]
    right = breaks[i + 1]

    mask = (x_dense >= left) & (x_dense <= right)

    ax.plot(
        x_dense[mask],
        y_dense[mask],
        color=PIECE_COLORS[i % len(PIECE_COLORS)],
        linewidth=4.4,
        solid_capstyle="round",
        zorder=4,
    )

# ------------------------------------------------------------
# 6. Mark illustrative knots
# ------------------------------------------------------------

# vertical guides
for j, xk in enumerate(knot_x, start=1):
    ax.axvline(
        xk,
        color=MUTED,
        linewidth=1.0,
        linestyle=(0, (2, 3)),
        alpha=0.45,
        zorder=1,
    )

# knot points on the spline
ax.scatter(
    knot_x,
    knot_y,
    s=92,
    facecolor="white",
    edgecolor=DARK,
    linewidth=1.8,
    zorder=6,
)

ax.scatter(
    knot_x,
    knot_y,
    s=28,
    facecolor=PURPLE_SMOOTH,
    edgecolor="none",
    zorder=7,
)

# minimal labels
y_offset = 0.18
for j, (xk, yk) in enumerate(zip(knot_x, knot_y), start=1):
    ax.text(
        xk,
        yk + y_offset,
        f"K{j}",
        ha="center",
        va="bottom",
        fontsize=10,
        color=MUTED,
        zorder=6,
    )

# ------------------------------------------------------------
# 7. Styling
# ------------------------------------------------------------

ax.set_title(
    "Smoothing spline shown as adjoining cubic pieces",
    fontsize=18,
    fontweight="bold",
    color=DARK,
    pad=14,
)

ax.set_xlabel(
    "Time / position",
    fontsize=14,
    fontweight="bold",
    color=DARK,
)

ax.set_ylabel(
    "Amplitude",
    fontsize=14,
    fontweight="bold",
    color=DARK,
)

ax.tick_params(labelsize=12, colors=DARK)

ax.grid(axis="y", color=LIGHT_GRID, linewidth=1.0)
ax.set_axisbelow(True)

ax.spines["top"].set_visible(False)
ax.spines["right"].set_visible(False)

ax.set_xlim(x_start, x_end)
ax.set_ylim(-0.8, 4.2)

plt.tight_layout()

# ------------------------------------------------------------
# 8. Save SVG
# ------------------------------------------------------------

plt.savefig(
    "smoothing_spline_static.svg",
    format="svg",
    bbox_inches="tight",
    transparent=True,
)