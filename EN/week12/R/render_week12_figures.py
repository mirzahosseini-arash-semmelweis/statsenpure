"""Generate all deterministic illustrative Week12 SVGs (synthetic data)."""
import numpy as np, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Ellipse, Rectangle, FancyArrowPatch, Circle, Arc
from matplotlib.gridspec import GridSpec
from sklearn.datasets import make_blobs, make_moons, make_circles
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.decomposition import PCA
from sklearn.discriminant_analysis import LinearDiscriminantAnalysis
from sklearn.cluster import KMeans, DBSCAN
from sklearn.mixture import GaussianMixture
from sklearn.manifold import SpectralEmbedding
from sklearn.ensemble import RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier, plot_tree
from scipy.stats import multivariate_normal
from pathlib import Path
import json
P=Path(__file__).resolve().parents[1]
O=P/'week12'/'figures'; O.mkdir(parents=True,exist_ok=True)
D=P/'week12'/'data'; D.mkdir(parents=True,exist_ok=True)
BLUE='#1f6feb'; ORANGE='#c65d09'; GREEN='#18864b'; RED='#c93838'; PURPLE='#7b4ab5'; NAVY='#182230'; GREY='#667085'; BG='#fbfcfe'; LINE='#d9e1ea'

rng=np.random.default_rng(12012)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':12,'axes.spines.top':False,'axes.spines.right':False,'axes.labelcolor':NAVY,'axes.edgecolor':'#98a2b3','xtick.color':GREY,'ytick.color':GREY,'text.color':NAVY,'figure.facecolor':'white','axes.facecolor':'white','svg.fonttype':'none','savefig.pad_inches':.16})
def save(n,fig):
 # fig.savefig(O/f'{n}.svg',format='svg',bbox_inches='tight');plt.close(fig)
 fig.savefig(f'{n}.svg',format='svg',bbox_inches='tight');plt.close(fig)
def figaxes(n=1,w=11,h=4.2):
 f,a=plt.subplots(1,n,figsize=(w,h),layout='constrained');return f,np.atleast_1d(a)
def title(ax,s):
  ax.set_title(s,fontsize=13,fontweight='bold',pad=12)
# matrix, metabolomics
f,aa=figaxes(2,11,4); a,b=aa
M=rng.normal(size=(30,56));M[:,4:15]+=np.linspace(-1.3,1.3,30)[:,None]*.7
a.imshow(M,aspect='auto',cmap='RdBu_r',vmin=-3,vmax=3);title(a,'PAT · production measurements');a.set_xlabel('Sensor + process variables');a.set_ylabel('Manufacturing batches');a.set_xticks([]);a.set_yticks([])
a.text(0,32,'30 batches × 56 signals (illustrative)',fontsize=10,color=GREY)
xx=rng.normal(size=(50,75));cc=rng.integers(0,2,50);xx[cc==1,15:35]+=.9
b.imshow(xx,aspect='auto',cmap='BrBG',vmin=-3,vmax=3);title(b,'Metabolomics · patient × metabolite');b.set_xlabel('Thousands of metabolites →');b.set_ylabel('Patients →');b.set_xticks([]);b.set_yticks([])
save('high_dimensional_matrices',f)
# Gaussian contours
f,aa=figaxes(3,12,3.75)
X,Y=np.meshgrid(np.linspace(-4,4,130),np.linspace(-4,4,130)); pos=np.dstack((X,Y))
for ax,S,name in zip(aa,[np.eye(2),[[2,.8],[.8,.65]],[[1,.85],[.85,1]]],['Equal independent spread','Different marginal variances','Strong positive covariance']):
 z=multivariate_normal(mean=[0,0],cov=S).pdf(pos)
 ax.contourf(X,Y,z,levels=13,cmap='Purples');ax.contour(X,Y,z,levels=6,colors='#6e4da0',linewidths=.5);ax.set_xlim(-4,4);ax.set_ylim(-4,4);ax.set_aspect('equal');title(ax,name);ax.set_xlabel('Variable 1');ax.set_ylabel('Variable 2')
save('gaussian_contours',f)
# pairplot
v=rng.normal(size=160); W=np.stack([v+.12*rng.normal(size=160),.65*v+.8*rng.normal(size=160),-v+.5*rng.normal(size=160),rng.normal(size=160)],axis=1)
labels=['Metabolite A','Metabolite B','Metabolite C','Marker D'];fig,axes=plt.subplots(4,4,figsize=(9,8.5),layout='constrained')
for i in range(4):
 for j in range(4):
  ax=axes[i,j];ax.set_xticks([]);ax.set_yticks([])
  if i==j:ax.hist(W[:,i],bins=19,color=BLUE,alpha=.76)
  elif i>j:ax.scatter(W[:,j],W[:,i],s=6,alpha=.5,color=BLUE)
  else:
    r = np.corrcoef(W[:, i], W[:, j])[0, 1]
    r_str = f'r = {r:+.2f}'.replace('-', '−')
    med = np.median(W[:, j])
    iqr = np.percentile(W[:, j], 75) - np.percentile(W[:, j], 25)
    med_str = f'Median: {med:.2f}'.replace('-', '−')
    iqr_str = f'IQR: {iqr:.2f}'.replace('-', '−')
    ax.text(.5, .72, med_str, ha='center', va='center', transform=ax.transAxes, color=PURPLE, fontsize=17)
    ax.text(.5, .52, iqr_str, ha='center', va='center', transform=ax.transAxes, color=PURPLE, fontsize=17)
    ax.text(.5, .32, r_str, ha='center', va='center', transform=ax.transAxes, color=PURPLE, fontsize=17, fontweight='bold')
  if i==3:ax.set_xlabel(labels[j],fontsize=13,fontweight='bold')
  if j==0:ax.set_ylabel(labels[i],fontsize=13,fontweight='bold')
save('pairplot',fig)
# distances
p1, p2 = [2.0, 0.35], [1.1, 1.4]
f, aa = figaxes(3, 12, 3.7)
for ax, k in zip(aa, ['Euclidean', 'Manhattan', 'Cosine distance']):
    ax.scatter([p1[0], p2[0]], [p1[1], p2[1]], c=[BLUE, ORANGE], s=105, zorder=5)    
    if k == 'Euclidean':
        ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color=PURPLE, lw=3)
    elif k == 'Manhattan':
        ax.plot([p1[0], p1[0], p2[0]], [p1[1], p2[1], p2[1]], color=PURPLE, lw=3)
    else:
        ax.annotate('', xy=p1, xytext=(0, 0), arrowprops=dict(arrowstyle='->,head_width=0.35,head_length=0.5', color=BLUE, lw=2.5))
        ax.annotate('', xy=p2, xytext=(0, 0), arrowprops=dict(arrowstyle='->,head_width=0.35,head_length=0.5', color=ORANGE, lw=2.5))
        a1, a2 = np.degrees([np.arctan2(p1[1], p1[0]), np.arctan2(p2[1], p2[0])])
        ax.add_patch(Arc((0, 0), 1.2, 1.2, theta1=a1, theta2=a2, color=PURPLE, lw=3))
        mid = np.radians((a1 + a2) / 2)
        ax.text(0.8 * np.cos(mid), 0.8 * np.sin(mid), r'$\theta$', color=PURPLE, fontsize=14, ha='center', va='center', fontweight='bold')
    ax.set_xlim(-0.4, 2.5); ax.set_ylim(-0.4, 2.0); ax.set_aspect('equal'); title(ax, k); ax.grid(alpha=.16)
save('distance_metrics', f)
# linkage
f, aa = figaxes(4, 12, 3.4)
g1 = np.array([[-1.1, -0.2], [-0.7, 1.1], [-0.5, 0.4], [0.0, 1.2], [0.4, 0.2]])
g2 = np.array([[2.7, 0.0], [3.1, 1.3], [3.5, 0.5], [4.0, 1.1], [4.2, -0.3]])
for ax, t in zip(aa, ['Single · closest', 'Complete · farthest', 'Average · all pairs', 'Centroid · centers']):
    ax.scatter(*g1.T, s=45, color=BLUE, zorder=4)
    ax.scatter(*g2.T, s=45, color=ORANGE, zorder=4)
    if t.startswith('Single'):
        dists = np.linalg.norm(g1[:, None, :] - g2[None, :, :], axis=-1)
        i, j = np.unravel_index(np.argmin(dists), dists.shape)
        ax.plot([g1[i, 0], g2[j, 0]], [g1[i, 1], g2[j, 1]], color=PURPLE, lw=3, ls='--', zorder=3)
    elif t.startswith('Complete'):
        dists = np.linalg.norm(g1[:, None, :] - g2[None, :, :], axis=-1)
        i, j = np.unravel_index(np.argmax(dists), dists.shape)
        ax.plot([g1[i, 0], g2[j, 0]], [g1[i, 1], g2[j, 1]], color=PURPLE, lw=3, ls='--', zorder=3)
    elif t.startswith('Average'):
        for p1 in g1:
            for p2 in g2:
                ax.plot([p1[0], p2[0]], [p1[1], p2[1]], color=PURPLE, lw=1.2, ls='--', alpha=0.45, zorder=3)
    else:
        m1, m2 = g1.mean(0), g2.mean(0)
        ax.plot([m1[0], m2[0]], [m1[1], m2[1]], color=PURPLE, lw=3, ls='--', zorder=3)
        ax.scatter([m1[0], m2[0]], [m1[1], m2[1]], color=PURPLE, marker='X', s=90, zorder=5)
    title(ax, t)
    ax.set_xlim(-1.6, 4.7)
    ax.set_ylim(-0.6, 1.8)
    ax.set_xticks([])
    ax.set_yticks([])
save('cluster_linkage', f)
# mahalanobis
f, aa = figaxes(2, 11, 4.2)
S = np.array([[3, 2.4], [2.4, 2.6]])
A = rng.multivariate_normal([0, 0], S, 300)
u = np.array([2.0, 2.0])
v = np.array([-1.6, 1.9])
inv = np.linalg.inv(S)
for i, (ax, typ) in enumerate(zip(aa, ['Ordinary Euclidean distance', 'Mahalanobis · covariance-adjusted'])):
    ax.scatter(*A.T, s=11, c=BLUE, alpha=.25)
    ax.scatter([0], [0], s=80, color=NAVY, marker='+')
    ax.scatter([u[0], v[0]], [u[1], v[1]], s=95, c=[GREEN, RED], edgecolor='white', zorder=5)
    for p, col in [(u, GREEN), (v, RED)]:
        ax.plot([0, p[0]], [0, p[1]], color=col, lw=2, zorder=4)
        d = np.linalg.norm(p) if i == 0 else np.sqrt(p.T @ inv @ p)
        lbl = f'$d_E = {d:.2f}$' if i == 0 else f'$d_M = {d:.2f}$'        
        ha = 'left' if p[0] > 0 else 'right'
        offset = 0.35 if p[0] > 0 else -0.35
        ax.text(p[0] + offset, p[1] + 0.1, lbl, color=col, fontweight='bold', fontsize=13, ha=ha)
    if i == 0:
        for r in (np.linalg.norm(v), np.linalg.norm(u)):
            ax.add_patch(Circle((0, 0), r, fill=False, color=PURPLE, lw=1.3, ls='--'))
    else:
        eig, Q = np.linalg.eigh(S)
        ang = np.degrees(np.arctan2(Q[1, 1], Q[0, 1]))
        for k in (1, 2):
            ax.add_patch(Ellipse((0, 0), 2*k*np.sqrt(eig[1]), 2*k*np.sqrt(eig[0]), angle=ang, fill=False, color=PURPLE, lw=1.3, ls='--'))
    title(ax, typ)
    ax.set_xlim(-5, 5); ax.set_ylim(-5, 5); ax.set_aspect('equal')
    ax.set_xlabel('Marker 1'); ax.set_ylabel('Marker 2')
save('mahalanobis', f)
# IR spectra match
f,aa=figaxes(2,11,3.8);x=np.linspace(600,3600,550)
def spec(peaks):
    return 1.0 - sum(a*np.exp(-.5*((x-m)/w)**2) for m,w,a in peaks)
ref=spec([(1050,70,.65),(1700,50,1.0),(2300,75,.3),(3000,80,.5)])
y1=spec([(1050,70,.65),(1700,50,1.0),(2300,75,.3),(3000,80,.5)])+.032*rng.normal(size=x.size)
y2=spec([(1040,80,.65),(1560,60,.83),(2100,30,.15),(2300,80,.25),(2600,40,.2),(2970,70,.55),(3200,35,.1)])+.04*rng.normal(size=x.size)
color_sample = '#1d4ed8' # BLUE
color_ref = '#ea580c' # ORANGE
for ax,yy,ttl in [(aa[0],y1,'Sample A · closely aligned'),(aa[1],y2,'Sample B · meaningful mismatch')]:
    ax.plot(x,yy,lw=1.4,color=color_sample,zorder=4,label='Measured sample') # BLUE is behind
    ax.plot(x,ref,lw=2.2,color=color_ref,zorder=5,label='Reference standard') # ORANGE is in front
    title(ax,ttl)
    ax.set_xlabel('Wavenumber (cm⁻¹)')
    ax.set_ylabel('Relative transmittance') # Updates label to transmittance
    ax.invert_xaxis() # Wavenumber goes from high to low for IR
    ax.legend(frameon=False,fontsize=9,loc='lower left')
save('ir_similarity',f)
# scaling plot
COLOR_RAW = '#1d4ed8'        # OBS Blue for raw observations
COLOR_MINMAX = '#7c3aed'     # UNC Purple for Min-Max normalization
COLOR_ZSCORE = '#16a34a'     # EST Green for Z-score standardization
COLOR_GREY = '#64748b'       # Neutral grey for axes and ticks
COLOR_PROJ = '#cbd5e1'       # Light grey for projection lines
COLOR_WARN = '#dc2626'       # WARN Red for outlier emphasis
raw_clean = np.array([-10.0, -8.2, -6.5, -4.8, -3.1, -1.2, 0.5, 2.0, 3.8, 5.2, 7.0, 8.8, 10.5, 12.1, 13.6, 15.0])
raw_outlier = np.append(raw_clean, 100.0)
min_c, max_c = raw_clean.min(), raw_clean.max()
minmax_clean = (raw_clean - min_c) / (max_c - min_c)
zscore_clean = (raw_clean - raw_clean.mean()) / raw_clean.std()
min_o, max_o = raw_outlier.min(), raw_outlier.max()
minmax_outlier = (raw_outlier - min_o) / (max_o - min_o)
zscore_outlier = (raw_outlier - raw_outlier.mean()) / raw_outlier.std()
def map_to_disp(val, v_min, v_max, disp_min=-10.0, disp_max=15.0):
    return disp_min + (val - v_min) / (v_max - v_min) * (disp_max - disp_min)
fig = plt.figure(figsize=(11.5, 7.2))
gs = GridSpec(2, 2, height_ratios=[1, 1], hspace=0.48, wspace=0.25)
ax_tl = fig.add_subplot(gs[0, 0])  # Top Left: Min-Max (Clean)
ax_tr = fig.add_subplot(gs[0, 1])  # Top Right: Z-Score (Clean)
ax_bl = fig.add_subplot(gs[1, 0])  # Bottom Left: Min-Max (Outlier)
ax_br = fig.add_subplot(gs[1, 1])  # Bottom Right: Z-Score (Outlier)
ax_tl.set_title('Min-Max Normalization', fontsize=16, fontweight='bold', pad=22, color='#0f172a')
ax_tr.set_title('Z-score Standardization', fontsize=16, fontweight='bold', pad=22, color='#0f172a')
# =========================================================================
# ROW 1: WITHOUT OUTLIER
# =========================================================================
ax_tl.text(-17.5, 0.5, 'Without\nOutlier', fontsize=11, fontweight='bold', color='#334155', ha='right', va='center')
ax_tl.plot([-12, 16], [1, 1], color=COLOR_GREY, lw=1.2, zorder=1)
ax_tl.scatter(raw_clean, np.ones_like(raw_clean), color=COLOR_RAW, s=36, zorder=4)
for val in [-10, -5, 0, 5, 10, 15]:
    ax_tl.plot([val, val], [0.94, 1.06], color=COLOR_GREY, lw=1.0)
    ax_tl.text(val, 1.18, f'{val}', ha='center', va='bottom', fontsize=10, color=COLOR_GREY)
disp_mm_clean = map_to_disp(minmax_clean, 0.0, 1.0, -10.0, 15.0)
ax_tl.plot([-10, 15], [0, 0], color=COLOR_MINMAX, lw=1.8, zorder=1)
ax_tl.scatter(disp_mm_clean, np.zeros_like(disp_mm_clean), color=COLOR_MINMAX, s=36, zorder=4)
for r_x, m_x in zip(raw_clean, disp_mm_clean):
    ax_tl.plot([r_x, m_x], [1, 0], color=COLOR_PROJ, ls='--', lw=1.0, zorder=2)
for n_val in [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]:
    d_x = map_to_disp(n_val, 0.0, 1.0, -10.0, 15.0)
    is_b = n_val in [0.0, 1.0]
    ax_tl.plot([d_x, d_x], [-0.06, 0.06], color=COLOR_MINMAX, lw=1.6 if is_b else 1.0)
    ax_tl.text(d_x, -0.22, f'{n_val:.1f}', ha='center', va='top', fontsize=10, fontweight='bold' if is_b else 'normal', color=COLOR_MINMAX)
ax_tl.text(-12.8, 1.0, 'Raw data', ha='right', va='center', fontsize=11, fontweight='bold', color=COLOR_RAW)
ax_tl.text(-12.8, 0.0, 'Transformed', ha='right', va='center', fontsize=11, fontweight='bold', color=COLOR_MINMAX)
ax_tl.set_xlim(-16, 17); ax_tl.set_ylim(-0.5, 1.5); ax_tl.axis('off')
ax_tr.plot([-12, 16], [1, 1], color=COLOR_GREY, lw=1.2, zorder=1)
ax_tr.scatter(raw_clean, np.ones_like(raw_clean), color=COLOR_RAW, s=36, zorder=4)
for val in [-10, -5, 0, 5, 10, 15]:
    ax_tr.plot([val, val], [0.94, 1.06], color=COLOR_GREY, lw=1.0)
    ax_tr.text(val, 1.18, f'{val}', ha='center', va='bottom', fontsize=10, color=COLOR_GREY)
z_clean_disp = map_to_disp(zscore_clean, -2.5, 2.5, -10.0, 15.0)
ax_tr.plot([map_to_disp(-2.2, -2.5, 2.5), map_to_disp(2.2, -2.5, 2.5)], [0, 0], color=COLOR_ZSCORE, lw=1.8, zorder=1)
ax_tr.scatter(z_clean_disp, np.zeros_like(z_clean_disp), color=COLOR_ZSCORE, s=36, zorder=4)
for r_x, z_x in zip(raw_clean, z_clean_disp):
    ax_tr.plot([r_x, z_x], [1, 0], color=COLOR_PROJ, ls='--', lw=1.0, zorder=2)
for z_val in [-2.0, -1.0, 0.0, 1.0, 2.0]:
    d_z = map_to_disp(z_val, -2.5, 2.5, -10.0, 15.0)
    is_c = z_val == 0.0
    ax_tr.plot([d_z, d_z], [-0.06, 0.06], color=COLOR_ZSCORE, lw=1.6 if is_c else 1.0)
    lbl = '0 (μ)' if is_c else f'{z_val:+.0f}σ'
    ax_tr.text(d_z, -0.22, lbl, ha='center', va='top', fontsize=10, fontweight='bold' if is_c else 'normal', color=COLOR_ZSCORE)
ax_tr.text(-12.8, 1.0, 'Raw data', ha='right', va='center', fontsize=11, fontweight='bold', color=COLOR_RAW)
ax_tr.text(-12.8, 0.0, 'Transformed', ha='right', va='center', fontsize=11, fontweight='bold', color=COLOR_ZSCORE)
ax_tr.set_xlim(-16, 17); ax_tr.set_ylim(-0.5, 1.5); ax_tr.axis('off')
# =========================================================================
# ROW 2: WITH OUTLIER (100.0)
# =========================================================================
ax_bl.text(-17.5, 0.5, 'With Outlier\n(100.0)', fontsize=11, fontweight='bold', color=COLOR_WARN, ha='right', va='center')
ax_bl.plot([-15, 105], [1, 1], color=COLOR_GREY, lw=1.2, zorder=1)
ax_bl.scatter(raw_outlier, np.ones_like(raw_outlier), color=COLOR_RAW, s=36, zorder=4)
for val in [0, 25, 50, 75, 100]:
    is_o = val == 100
    ax_bl.plot([val, val], [0.94, 1.06], color=COLOR_WARN if is_o else COLOR_GREY, lw=1.8 if is_o else 1.0)
    ax_bl.text(val, 1.18, f'{val}', ha='center', va='bottom', fontsize=10, fontweight='bold' if is_o else 'normal', color=COLOR_WARN if is_o else COLOR_GREY)
disp_mm_out = map_to_disp(minmax_outlier, 0.0, 1.0, -10.0, 100.0)
ax_bl.plot([-10, 100], [0, 0], color=COLOR_MINMAX, lw=1.8, zorder=1)
ax_bl.scatter(disp_mm_out, np.zeros_like(disp_mm_out), color=COLOR_MINMAX, s=36, zorder=4)
for r_x, m_x in zip(raw_outlier, disp_mm_out):
    ax_bl.plot([r_x, m_x], [1, 0], color=COLOR_PROJ, ls='--', lw=1.0, zorder=2)
for n_val in [0.0, 0.2, 0.4, 0.6, 0.8, 1.0]:
    d_x = map_to_disp(n_val, 0.0, 1.0, -10.0, 100.0)
    is_b = n_val in [0.0, 1.0]
    ax_bl.plot([d_x, d_x], [-0.06, 0.06], color=COLOR_MINMAX, lw=1.6 if is_b else 1.0)
    ax_bl.text(d_x, -0.22, f'{n_val:.1f}', ha='center', va='top', fontsize=10, fontweight='bold' if is_b else 'normal', color=COLOR_MINMAX)
ax_bl.text(-12.8, 1.0, 'Raw data', ha='right', va='center', fontsize=11, fontweight='bold', color=COLOR_RAW)
ax_bl.text(-12.8, 0.0, 'Transformed', ha='right', va='center', fontsize=11, fontweight='bold', color=COLOR_MINMAX)
ax_bl.set_xlim(-16, 110); ax_bl.set_ylim(-0.5, 1.5); ax_bl.axis('off')
ax_br.plot([-15, 105], [1, 1], color=COLOR_GREY, lw=1.2, zorder=1)
ax_br.scatter(raw_outlier, np.ones_like(raw_outlier), color=COLOR_RAW, s=36, zorder=4)
for val in [0, 25, 50, 75, 100]:
    is_o = val == 100
    ax_br.plot([val, val], [0.94, 1.06], color=COLOR_WARN if is_o else COLOR_GREY, lw=1.8 if is_o else 1.0)
    ax_br.text(val, 1.18, f'{val}', ha='center', va='bottom', fontsize=10, fontweight='bold' if is_o else 'normal', color=COLOR_WARN if is_o else COLOR_GREY)
z_vis_min, z_vis_max = -2.5, 16.0
disp_z_out = map_to_disp(zscore_outlier, z_vis_min, z_vis_max, -10.0, 100.0)
ax_br.plot([map_to_disp(-2.2, z_vis_min, z_vis_max, -10.0, 100.0), map_to_disp(15.5, z_vis_min, z_vis_max, -10.0, 100.0)], [0, 0], color=COLOR_ZSCORE, lw=1.8, zorder=1)
ax_br.scatter(disp_z_out, np.zeros_like(disp_z_out), color=COLOR_ZSCORE, s=36, zorder=4)
for r_x, z_x in zip(raw_outlier, disp_z_out):
    ax_br.plot([r_x, z_x], [1, 0], color=COLOR_PROJ, ls='--', lw=1.0, zorder=2)
for z_val, label in [(0, '0 (μ)'), (5, '+5σ'), (10, '+10σ'), (15, '+15σ')]:
    d_z = map_to_disp(z_val, z_vis_min, z_vis_max, -10.0, 100.0)
    is_c = z_val == 0
    ax_br.plot([d_z, d_z], [-0.06, 0.06], color=COLOR_ZSCORE, lw=1.6 if is_c else 1.0)
    ax_br.text(d_z, -0.22, label, ha='center', va='top', fontsize=10, fontweight='bold' if is_c else 'normal', color=COLOR_ZSCORE)
ax_br.text(-12.8, 1.0, 'Raw data', ha='right', va='center', fontsize=11, fontweight='bold', color=COLOR_RAW)
ax_br.text(-12.8, 0.0, 'Transformed', ha='right', va='center', fontsize=11, fontweight='bold', color=COLOR_ZSCORE)
ax_br.set_xlim(-16, 110); ax_br.set_ylim(-0.5, 1.5); ax_br.axis('off')
plt.savefig('pca_scaling.svg', format='svg', bbox_inches='tight')
# PCA loading biplot/scree
W=StandardScaler().fit_transform(V);pca=PCA(n_components=3).fit(W);proj=pca.transform(W)
f,aa=figaxes(2,10.9,4.1);a,b=aa;a.scatter(*proj[:,:2].T,c=C,s=17,alpha=.55)
for i,l in enumerate(['Hemoglobin','Age','Weight']):
 vx,vy=pca.components_[0,i]*2.8,pca.components_[1,i]*2.8;a.arrow(0,0,vx,vy,color=PURPLE,width=.025,head_width=.15,length_includes_head=True);a.text(vx*1.13,vy*1.13,l,fontsize=10,color=PURPLE,fontweight='bold')
a.set_xlim(-4.7,4.7);a.set_ylim(-4.2,4.2);a.axhline(0,color=LINE);a.axvline(0,color=LINE);a.set_xlabel('PC1');a.set_ylabel('PC2');title(a,'PCA scores + original-variable loading arrows')
b.bar(range(1,4),pca.explained_variance_ratio_*100,color=[PURPLE,BLUE,GREEN]);b.set_ylim(0,100);b.set_xticks([1,2,3]);b.set_xlabel('Component');b.set_ylabel('% variance explained');title(b,'How much information each PC keeps')
save('pca_loadings_scree',f)
# clustering and precomputed dataset
X1,y1=make_moons(n_samples=300,noise=.085,random_state=12);X2,y2=make_blobs(n_samples=300,centers=[[-1.5,0.], [1.5,0.]],cluster_std=[.75,.9],random_state=21)
def clrecs(X):
 res={}
 for k in (2,3,4,5):
  res[f'kmeans{k}']=KMeans(n_clusters=k,random_state=21,n_init=8).fit_predict(X).tolist()
  res[f'gmm{k}']=GaussianMixture(n_components=k,random_state=21).fit_predict(X).tolist()
 for eps in (.14,.21,.29,.38):res[f'dbscan{eps}']=DBSCAN(eps=eps,min_samples=5).fit_predict(X).tolist()
 return res
DATA={'moons':{'points':X1.round(4).tolist(),'true':y1.tolist(),'labels':clrecs(X1)},'blobs':{'points':X2.round(4).tolist(),'true':y2.tolist(),'labels':clrecs(X2)}}
(D/'clusters.json').write_text(json.dumps(DATA,separators=(',',':')))
f,aa=figaxes(3,11.7,3.7)
for ax,cls,lbl in zip(aa,[KMeans(n_clusters=2,random_state=4,n_init=8).fit_predict(X1),GaussianMixture(n_components=2,random_state=4).fit_predict(X1),DBSCAN(eps=.21,min_samples=5).fit_predict(X1)],['K-means','Gaussian mixture','DBSCAN']):
 ax.scatter(*X1.T,c=np.asarray([BLUE,ORANGE,PURPLE,GREEN])[np.maximum(0,cls)],s=12,alpha=.72);title(ax,lbl);ax.set_xticks([]);ax.set_yticks([])
save('clustering_methods',f)
# nonlinear embeddings: transparent illustration using Isomap/Spectral, not UMAP exact
from sklearn.manifold import Isomap
S=np.column_stack([rng.normal(size=300),rng.normal(size=300)])
t=np.linspace(0,3*np.pi,300);roll=np.c_[t*np.cos(t),t*np.sin(t),.4*t]+.15*rng.normal(size=(300,3)); order=np.argsort(t)
embeds=[]
for neighbor in [7,16,35]:
 try: e=Isomap(n_neighbors=neighbor,n_components=2).fit_transform(roll)
 except Exception:e=PCA(n_components=2).fit_transform(roll)
 embeds.append(e)
f,aa=figaxes(3,12,4.0)
for ax,e,k in zip(aa,embeds,[7,16,35]):
 ax.scatter(*e.T,c=t,cmap='viridis',s=13,alpha=.8);title(ax,f'Neighborhood size = {k}');ax.set_xlabel('Embedding 1');ax.set_ylabel('Embedding 2')
f.suptitle('Neighborhood-based nonlinear embedding · Isomap illustration (not UMAP)',fontsize=15,fontweight='bold')
save('neighborhood_embedding',f)
(D/'nonlinear_embeddings.json').write_text(json.dumps({'points':roll.round(3).tolist(),'projections':{str(k):e.round(4).tolist() for k,e in zip([7,16,35],embeds)},'method':'Isomap conceptual counterpart, not UMAP'},separators=(',',':')))
# LDA vs PCA
Xc,yc=make_blobs(n_samples=200,centers=[[0,0],[2,1]],cluster_std=2.2,random_state=31);Xc[:,0]*=3
pc=PCA(n_components=1).fit_transform(Xc);lda=LinearDiscriminantAnalysis(n_components=1).fit_transform(Xc,yc)
f,aa=figaxes(2,11.5,3.65)
for ax,proj,lab in zip(aa,[pc,lda],['PCA · label-blind variance','LDA · label-aware separation']):
 jitter=.06*rng.normal(size=len(proj));ax.scatter(proj[:,0],jitter,c=np.array([BLUE,ORANGE])[yc],s=21,alpha=.6);title(ax,lab);ax.set_yticks([]);ax.set_xlabel('Projection coordinate')
save('pca_vs_lda',f)
# decision tree trained on biologically illustrative synthetic 5 biomarkers
rr=np.random.default_rng(12);aa=rr.normal(size=(800,5));logit=1.2*aa[:,0]-.85*aa[:,1]+.65*(aa[:,2]>.7)-.35*aa[:,3]*aa[:,4];yy=(rr.random(800)<1/(1+np.exp(-logit))).astype(int)
tree=DecisionTreeClassifier(max_depth=3,min_samples_leaf=50,random_state=4).fit(aa,yy)
f,axs=plt.subplots(figsize=(14,5.1));plot_tree(tree,filled=True,feature_names=['Amino acid A','Lipid B','Metabolite C','Amino acid D','Peptide E'],class_names=['Low','Higher'],rounded=True,fontsize=8,ax=axs);save('decision_tree',f)
T={'features':['Amino acid A','Lipid B','Metabolite C','Amino acid D','Peptide E'],'children_left':tree.tree_.children_left.tolist(),'children_right':tree.tree_.children_right.tolist(),'feature':tree.tree_.feature.tolist(),'threshold':tree.tree_.threshold.round(4).tolist(),'value':tree.tree_.value[:,0,:].round(4).tolist()}
(D/'tree.json').write_text(json.dumps(T,separators=(',',':')))
# RF concept
def draw_mini_tree(ax, cx, cy, col=BLUE):
    nodes = {
        'root': (cx, cy),
        'L': (cx - 0.38, cy - 0.32),
        'R': (cx + 0.38, cy - 0.32),
        'LL': (cx - 0.52, cy - 0.64),
        'LR': (cx - 0.22, cy - 0.64),
        'RL': (cx + 0.22, cy - 0.64),
        'RR': (cx + 0.52, cy - 0.64),
    }
    edges = [
        ('root', 'L'), ('root', 'R'),
        ('L', 'LL'), ('L', 'LR'),
        ('R', 'RL'), ('R', 'RR')
    ]
    for n1, n2 in edges:
        x1, y1 = nodes[n1]
        x2, y2 = nodes[n2]
        ax.plot([x1, x2], [y1, y2], color=col, lw=1.6, zorder=3)
    for key, (nx, ny) in nodes.items():
        if len(key) == 2:  # Leaf nodes
            ax.scatter(nx, ny, s=40, color=col, zorder=4)
        else:  # Internal / Root nodes
            ax.scatter(nx, ny, s=40, color='white', edgecolor=col, linewidth=1.5, zorder=4)
f, aa = figaxes(1, 11.4, 3.2)
ax = aa[0]
ax.set_axis_off()
ax.set_xlim(0, 10)
ax.set_ylim(-0.1, 3.0)
tree_centers = [1.8, 5.0, 8.2]
for i, x0 in enumerate(tree_centers):
    card = patches.FancyBboxPatch((x0 - 1.1, 1.15), 2.2, 1.4, boxstyle="round,pad=0.03,rounding_size=0.15",
                                 fc='#f8fafc', ec=BLUE, lw=1.8, zorder=2)
    ax.add_patch(card)
    ax.text(x0, 2.32, f'Tree {i+1}', ha='center', va='center', fontsize=13, fontweight='bold', color=BLUE, zorder=4)
    draw_mini_tree(ax, x0, 2.0, col=BLUE)
    ax.annotate('', xy=(5.0, 0.8), xytext=(x0, 1.12),
                arrowprops=dict(arrowstyle='->,head_width=0.3,head_length=0.4', lw=1.8, color=GREY))
agg_card = patches.FancyBboxPatch((3.5, 0.15), 3.0, 0.65, boxstyle="round,pad=0.03,rounding_size=0.12",
                                  fc='#f0fdf4', ec=GREEN, lw=2.2, zorder=2)
ax.add_patch(agg_card)
ax.text(5.0, 0.48, 'Aggregate votes / Ensembling', ha='center', va='center', color=GREEN, fontsize=13, fontweight='bold', zorder=4)
title(ax, 'Many diverse trees → one more stable prediction')
save('random_forest', f)
# learning process schematic
# Color palette matching library standards
f, aa = figaxes(1, 11, 4.2)
a = aa[0]
a.axis('off')
a.set_xlim(0, 11)
a.set_ylim(-0.2, 3.4)
w_box, h_box = 2.0, 1.15
gx, gy = 0.8, 1.95    # Generator coordinates
sx, sy = 5.0, 1.95    # Supervisor coordinates
lmx, lmy = 5.0, 0.25  # Learning Machine coordinates
# 1. Generator (G)
a.add_patch(patches.Rectangle((gx, gy), w_box, h_box, fc='white', ec=BLUE, lw=2.5, zorder=3))
a.text(gx + w_box/2, gy + h_box/2 + 0.15, 'G', ha='center', va='center', fontsize=20, fontweight='bold', color=BLUE)
a.text(gx + w_box/2, gy + h_box/2 - 0.22, 'Data Generator', ha='center', va='center', fontsize=11, color=BLUE)
# 2. Supervisor (S)
a.add_patch(patches.Rectangle((sx, sy), w_box, h_box, fc='white', ec=ORANGE, lw=2.5, zorder=3))
a.text(sx + w_box/2, sy + h_box/2 + 0.15, 'S', ha='center', va='center', fontsize=20, fontweight='bold', color=ORANGE)
a.text(sx + w_box/2, sy + h_box/2 - 0.22, 'Supervisor', ha='center', va='center', fontsize=11, color=ORANGE)
# 3. Learning Machine (LM)
a.add_patch(patches.Rectangle((lmx, lmy), w_box, h_box, fc='white', ec=PURPLE, lw=2.5, zorder=3))
a.text(lmx + w_box/2, lmy + h_box/2 + 0.15, 'L M', ha='center', va='center', fontsize=18, fontweight='bold', color=PURPLE)
a.text(lmx + w_box/2, lmy + h_box/2 - 0.22, 'Learning Machine', ha='center', va='center', fontsize=10.5, color=PURPLE)
# --- Routing & Branching Connections ---
# 1. Output vector x from G
split1_x = 3.9
y_line_x = gy + h_box/2
a.plot([gx + w_box, split1_x], [y_line_x, y_line_x], color=BLUE, lw=2.2)
a.text((gx + w_box + split1_x)/2 + 0.2, y_line_x + 0.15, r'$X$ (data)', color=BLUE, fontsize=16, fontweight='bold', ha='center', va='bottom')
# Branch 1a: Into Supervisor (S)
a.annotate('', xy=(sx, y_line_x), xytext=(split1_x, y_line_x),
           arrowprops=dict(arrowstyle='->,head_width=0.35,head_length=0.45', color=BLUE, lw=2.2))
# Branch 1b: Down and into Learning Machine (LM)
lm_in_y = lmy + 0.72
a.plot([split1_x, split1_x], [y_line_x, lm_in_y], color=BLUE, lw=2.2)
a.annotate('', xy=(lmx, lm_in_y), xytext=(split1_x, lm_in_y),
           arrowprops=dict(arrowstyle='->,head_width=0.35,head_length=0.45', color=BLUE, lw=2.2))
# 2. Output target y from Supervisor (S)
y_out_y = sy + h_box/2
a.annotate('', xy=(9.2, y_out_y), xytext=(sx + w_box, y_out_y),
           arrowprops=dict(arrowstyle='->,head_width=0.35,head_length=0.45', color=ORANGE, lw=2.2))
a.text(9.4, y_out_y, r'$y$ (labels)', color=ORANGE, fontsize=17, fontweight='bold', ha='left', va='center')
# Branch 2: Supervisor output y fed back down into Learning Machine (LM)
split2_x = 7.8
lm_sup_in_y = lmy + 0.52
a.plot([split2_x, split2_x], [y_out_y, lm_sup_in_y], color=ORANGE, lw=2.2)
a.annotate('', xy=(lmx + w_box, lm_sup_in_y), xytext=(split2_x, lm_sup_in_y),
           arrowprops=dict(arrowstyle='->,head_width=0.35,head_length=0.45', color=ORANGE, lw=2.2))
# 3. Output prediction \hat{y} from Learning Machine (LM)
lm_out_y = lmy + 0.22
a.annotate('', xy=(9.2, lm_out_y), xytext=(lmx + w_box, lm_out_y),
           arrowprops=dict(arrowstyle='->,head_width=0.35,head_length=0.45', color=PURPLE, lw=2.2))
a.text(9.4, lm_out_y, r'$\hat{y}$ (predictions)', color=PURPLE, fontsize=17, fontweight='bold', ha='left', va='center')
title(a, "General Model of Statistical Learning")
save('training_workflow', f)
# ML process schematic
fig, ax = plt.subplots(figsize=(14.5, 5.2))
ax.axis('off')
ax.set_xlim(-0.5, 15.0)
ax.set_ylim(-0.6, 5.2)
# Helper function for drawing styled card components
def draw_card(ax, x, y, w, h, title, subtext=None, ec=BLUE, fc='white', lw=2.2, title_size=10.5, sub_size=9.5):
    box = patches.FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.03,rounding_size=0.15",
                                fc=fc, ec=ec, lw=lw, zorder=3)
    ax.add_patch(box)
    if subtext:
        ax.text(x + w/2, y + h*0.64, title, ha='center', va='center', fontsize=title_size, fontweight='bold', color=ec, zorder=4)
        ax.text(x + w/2, y + h*0.28, subtext, ha='center', va='center', fontsize=sub_size, color=GREY, zorder=4)
    else:
        ax.text(x + w/2, y + h/2, title, ha='center', va='center', fontsize=title_size, fontweight='bold', color=ec, zorder=4)
# 1. Raw Dataset
draw_card(ax, 0.2, 2.2, 1.5, 1.1, '1. Raw Data', 'Full Dataset', ec=BLUE)
# Arrow to Train/Test Split
ax.annotate('', xy=(2.2, 2.75), xytext=(1.7, 2.75),
            arrowprops=dict(arrowstyle='->,head_width=0.3,head_length=0.4', color=GREY, lw=2))
# 2. Train / Test Split
draw_card(ax, 2.2, 2.2, 1.6, 1.1, '2. Initial Split', 'Train / Test', ec=BLUE)
# Split Branches
# Branch to Training Set (Up)
ax.annotate('', xy=(4.3, 3.8), xytext=(3.8, 2.9),
            arrowprops=dict(arrowstyle='->,head_width=0.3,head_length=0.4', color=ORANGE, lw=2))
# Branch to Held-out Test Set (Down)
ax.annotate('', xy=(4.3, 0.9), xytext=(3.8, 2.6),
            arrowprops=dict(arrowstyle='->,head_width=0.3,head_length=0.4', color=RED, lw=2, ls='--'))
# 3. Training Data
draw_card(ax, 4.3, 3.25, 1.6, 1.1, '3. Train Set', '80% Data', ec=ORANGE)
# Arrow into Iterative Tuning Loop
ax.annotate('', xy=(6.4, 3.8), xytext=(5.9, 3.8),
            arrowprops=dict(arrowstyle='->,head_width=0.3,head_length=0.4', color=ORANGE, lw=2))
# --- 4. HYPERPARAMETER TUNING & MODEL SELECTION CONTAINER ---
container = patches.FancyBboxPatch((6.4, 2.3), 3.5, 2.5, boxstyle="round,pad=0.05,rounding_size=0.2",
                                   fc='#f8f5ff', ec=PURPLE, lw=1.5, ls='--', zorder=1)
ax.add_patch(container)
ax.text(8.15, 4.55, '4. Model Selection & Tuning Loop', ha='center', va='center', fontsize=10, fontweight='bold', color=PURPLE)
# Sub-components inside container
draw_card(ax, 6.6, 3.5, 1.4, 0.8, 'Train Sub-set', 'Minimize Loss', ec=ORANGE, title_size=9.5, sub_size=7.5)
draw_card(ax, 8.3, 3.5, 1.4, 0.8, 'Validation Set', 'Measure Error', ec=PURPLE, title_size=9.5, sub_size=7.5)
# Forward evaluation arrow: Train -> Validation
ax.annotate('', xy=(8.3, 3.9), xytext=(8.0, 3.9),
            arrowprops=dict(arrowstyle='->,head_width=0.25,head_length=0.35', color=PURPLE, lw=1.8))
# Feedback loop arrow: Validation -> Hyperparameter Tuning -> Train
ax.annotate('', xy=(7.3, 3.5), xytext=(9.0, 3.5),
            arrowprops=dict(arrowstyle='->,head_width=0.25,head_length=0.35', color=PURPLE, lw=1.8, connectionstyle="arc3,rad=-0.75"))
ax.text(8.15, 2.62, 'Tune Hyperparameters\n(Iterate)', ha='center', va='top', fontsize=8.5, fontweight='bold', color=PURPLE)
# Arrow out of Tuning Loop to Final Model
ax.annotate('', xy=(10.4, 3.8), xytext=(9.9, 3.8),
            arrowprops=dict(arrowstyle='->,head_width=0.3,head_length=0.4', color=PURPLE, lw=2))
# 5. Final Optimized Model
draw_card(ax, 10.4, 3.25, 1.7, 1.1, '5. Final Model', 'Optimized Params', ec=PURPLE)
# --- 6. HELD-OUT TEST SET & EVALUATION ---
draw_card(ax, 4.3, 0.35, 1.6, 1.1, 'Test Set', 'Held-out (20%)', ec=RED)
# Pathway from Test Set across bottom to Evaluation
ax.plot([5.9, 11.25], [0.9, 0.9], color=RED, lw=2, ls='--')
ax.annotate('', xy=(11.25, 1.8), xytext=(11.25, 0.9),
            arrowprops=dict(arrowstyle='->,head_width=0.3,head_length=0.4', color=RED, lw=2, ls='--'))
# Pathway from Final Model down to Evaluation
ax.annotate('', xy=(11.25, 1.8), xytext=(11.25, 3.25),
            arrowprops=dict(arrowstyle='->,head_width=0.3,head_length=0.4', color=PURPLE, lw=2))
# 6. Final Evaluation Node
draw_card(ax, 10.4, 1.25, 1.7, 1.1, '6. Test Evaluation', 'Unseen Performance', ec=RED)
# Arrow to Deployment
ax.annotate('', xy=(12.6, 1.8), xytext=(12.1, 1.8),
            arrowprops=dict(arrowstyle='->,head_width=0.35,head_length=0.45', color=GREEN, lw=2.4))
# 7. Deployment
draw_card(ax, 12.6, 1.25, 1.5, 1.1, '7. Deployment', 'Production', ec=GREEN, lw=2.5)
ax.set_title('Canonical Machine Learning Training & Evaluation Pipeline', fontsize=14, fontweight='bold', pad=15, color='#0f172a')
plt.tight_layout()
plt.savefig('ml_workflow.svg', format='svg', bbox_inches='tight')
# bias variance styles
f,aa=figaxes(3,12,3.6);x=np.linspace(-1,1,180);truth=np.sin(3*x)+.7*x;obs=truth[::12]+rng.normal(0,.18,len(truth[::12]));xs=x[::12]
for ax,d,lab in zip(aa,[1,3,12],['Underfitting','Useful flexibility','Overfitting']):
 coef=np.polyfit(xs,obs,d);ax.plot(x,truth,c=ORANGE,ls='--',lw=2,label='Underlying function');ax.plot(x,np.polyval(coef,x),c=GREEN,lw=2,label='Fit');ax.scatter(xs,obs,c=BLUE,s=32);title(ax,lab);ax.set_ylim(-2,2);ax.set_xticks([]);ax.set_yticks([])
save('bias_variance',f)
# mathematical baseline vs nonlinear neuron
f,aa=figaxes(1,10.8,2.7);a=aa[0];a.axis('off');a.set_xlim(0,12);a.set_ylim(0,3)
for xi,lab in [(1,'x₁'),(1.9,'x₂'),(2.8,'x₃'),(3.7,'x₄'),(4.6,'x₅')]:
 a.text(xi,1.8,lab,ha='center',fontsize=16,color=BLUE,fontweight='bold');a.annotate('',xy=(6.1,1.45),xytext=(xi,1.68),arrowprops={'arrowstyle':'->','lw':1.2,'color':'#98a2b3'})
a.add_patch(Circle((6.5,1.4),.65,fc='#f2ebfc',ec=PURPLE,lw=2));a.text(6.5,1.4,'Σwᵢxᵢ+b',ha='center',va='center',fontsize=12,color=PURPLE)
a.annotate('',xy=(8.4,1.4),xytext=(7.2,1.4),arrowprops={'arrowstyle':'->','color':GREY,'lw':2});a.text(8.9,1.4,'activation',fontsize=13,color=PURPLE,va='center');a.annotate('',xy=(11.25,1.4),xytext=(10.45,1.4),arrowprops={'arrowstyle':'->','color':GREY,'lw':2});a.text(11.7,1.4,'p',color=GREEN,fontsize=20,va='center',fontweight='bold');save('single_neuron',f)

# Jaccard / Tanimoto similarity for binary molecular fingerprints
f, aa = figaxes(1, 12.6, 4.1)
ax = aa[0]
ax.set_axis_off()
ax.set_xlim(-0.9, 13.2)
ax.set_ylim(-1.2, 4.4)

fingerA = np.array([1, 1, 0, 1, 0, 1, 1, 0, 1, 0, 0, 1])
fingerB = np.array([1, 0, 1, 1, 1, 0, 1, 0, 0, 1, 0, 1])

common = int(np.sum(fingerA & fingerB))
union  = int(np.sum(fingerA | fingerB))

# Compact functional-group / substructure labels for each bit
bit_labels = [
    "OH", "NH$_2$", "Cl", "C=O", "COOH", "Ar",
    "C=C", "S", "OCH$_3$", "F", "Br", "N"
]

# Geometry
cell_w = 0.86
cell_h = 0.70
yA = 2.10
yB = 0.92
yFeat = 3.28
yInterp = 0.08

# Column headers showing what each fingerprint bit stands for
for j, lab in enumerate(bit_labels):
    ax.text(
        j + cell_w/2, 3.35, lab,
        ha='center', va='center',
        fontsize=10.5,
        color=GREY,
        fontweight='bold'
    )
    # optional faint guide line
    ax.plot(
        [j + cell_w/2, j + cell_w/2],
        [3.05, 2.90],
        color='#d8dee8', lw=0.8
    )

ax.text(
    5.5, 3.72,
    'Fingerprint bits record presence or absence of structural features',
    ha='center', va='center',
    fontsize=11,
    color=GREY
)

# Main fingerprint boxes
for j in range(len(fingerA)):
    a = fingerA[j]
    b = fingerB[j]

    # Optional subtle highlighting of shared 1-bits
    both_one = (a == 1 and b == 1)

    for yy, v, col in [(yA, a, BLUE), (yB, b, ORANGE)]:
        ax.add_patch(Rectangle(
            (j, yy), cell_w, cell_h,
            fc=col if v else '#eef2f8',
            ec=PURPLE if both_one else LINE,
            lw=1.8 if both_one else 1
        ))
        ax.text(
            j + cell_w/2, yy + cell_h/2, str(int(v)),
            ha='center', va='center',
            fontsize=13,
            fontweight='bold',
            color='white' if v else GREY
        )

# Row labels
ax.text(-0.28, yA + cell_h/2, 'A', fontsize=13, fontweight='bold',
        ha='right', va='center', color=BLUE)
ax.text(-0.28, yB + cell_h/2, 'B', fontsize=13, fontweight='bold',
        ha='right', va='center', color=ORANGE)

# ------------------------------------------------------------
# Larger and clearer Venn-style ratio icon
# ------------------------------------------------------------
def draw_venn_ratio(ax, x, y, r=0.28, d=0.18, color=PURPLE):
    """
    Draw a fraction-like Venn diagram:
    top = overlap only
    bottom = union
    """

    # numerator: overlap only
    y_top = y + 0.34
    left_top  = Circle((x - d, y_top), r, fc='white', ec=color, lw=1.6, zorder=2)
    right_top = Circle((x + d, y_top), r, fc='white', ec=color, lw=1.6, zorder=2)
    ax.add_patch(left_top)
    ax.add_patch(right_top)

    clip_c = Circle((x - d, y_top), r, transform=ax.transData)
    fill_overlap = Circle((x + d, y_top), r, fc=color, ec='none', zorder=3)
    fill_overlap.set_clip_path(clip_c)
    ax.add_patch(fill_overlap)

    ax.add_patch(Circle((x - d, y_top), r, fc='none', ec=color, lw=1.6, zorder=4))
    ax.add_patch(Circle((x + d, y_top), r, fc='none', ec=color, lw=1.6, zorder=4))

    # fraction bar
    ax.plot([x - 0.56, x + 0.56], [y, y], color=color, lw=2.2, zorder=5)

    # denominator: union
    y_bot = y - 0.34
    left_bot  = Circle((x - d, y_bot), r, fc=color, ec=color, lw=1.6, zorder=2)
    right_bot = Circle((x + d, y_bot), r, fc=color, ec=color, lw=1.6, zorder=2)
    ax.add_patch(left_bot)
    ax.add_patch(right_bot)

# Equation row
y_eq = -0.45
ax.text(
    2.95, y_eq,
    'Tanimoto similarity =',
    ha='right', va='center',
    fontsize=12.8,
    color=PURPLE,
    fontweight='bold'
)

draw_venn_ratio(ax, 4.05, y_eq, r=0.28, d=0.18, color=PURPLE)

ax.text(
    5.10, y_eq,
    f'=   shared 1-bits / union of 1-bits   =   {common} / {union}   =   {common/union:.2f}',
    ha='left', va='center',
    fontsize=12.5,
    color=PURPLE,
    fontweight='bold'
)

# Optional explanatory note
ax.text(
    5.9, -1.5,
    'Only present features contribute: matching 0/0 bits do not increase similarity.',
    ha='center', va='center',
    fontsize=10.5,
    color=GREY
)

ax.set_title(
    'Tanimoto similarity for sparse binary chemical fingerprints',
    fontsize=15,
    fontweight='bold'
)

save('tanimoto_fingerprints', f)
