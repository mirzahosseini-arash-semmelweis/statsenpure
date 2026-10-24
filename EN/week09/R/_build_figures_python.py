"""Pre-render the Week 09 vector figures. SVG text remains editable."""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator
from math import gamma, factorial
from pathlib import Path
out=Path(__file__).resolve().parents[1]/'week09'/'figures'
out.mkdir(parents=True,exist_ok=True)
BLUE='#1f6feb'; ORANGE='#c65d09'; GREEN='#18864b'; RED='#c93838'; PURPLE='#7b4ab5'; INK='#182230'; MUTED='#667085'; PANEL='#f3f6fa'; LINE='#d9e1ea'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':13,'axes.titlesize':16,'axes.titleweight':'bold','axes.labelsize':14,'axes.labelcolor':INK,'axes.edgecolor':'#a4afbc','axes.spines.right':False,'axes.spines.top':False,'text.color':INK,'xtick.color':MUTED,'ytick.color':MUTED,'svg.fonttype':'none','figure.facecolor':'white','axes.facecolor':'white','savefig.facecolor':'white'})
def save(fig,filename):
    fig.savefig(out/filename,format='svg',bbox_inches='tight',pad_inches=.18)
    plt.close(fig)
def sigmoid(v):
    return 1/(1+np.exp(-np.clip(v,-40,40)))
def dress(ax):
    ax.grid(color='#e3e9f1',lw=.8,zorder=0);ax.set_axisbelow(True)
# Binary data and dubious OLS line
r=np.random.default_rng(901)
x=r.lognormal(mean=3.5, sigma=0.55, size=105)
p=sigmoid(-1.2+1.8*(x-30)/10)
y=r.binomial(1,p)
ols=np.polyfit(x,y,1)
xx=np.linspace(1.0,150.0,400)
fig,ax=plt.subplots(figsize=(11.8,5.6));dress(ax)
ax.scatter(x,y+r.uniform(-0.01,0.01,len(y)),s=30,c=BLUE,alpha=.62,edgecolor='white',linewidth=.6,zorder=4,label='Patient observations (0/1)')
ax.plot(xx,np.polyval(ols,xx),c=RED,lw=3,label='Ordinary least-squares line')
ax.plot(xx,sigmoid(-1.2+1.8*(xx-30)/10),c=GREEN,lw=3,ls='--',label='Logistic probability curve')
ax.axhspan(0,1,color='#eef5ff',zorder=-1);ax.axhline(0,c=INK,lw=.8);ax.axhline(1,c=INK,lw=.8)
ax.set(xlim=(0.0,80.0),ylim=(-.33,1.38),xlabel='Fasting insulin level (pmol/L)',ylabel='Recorded outcome / modeled probability',title='An ordinary line can predict below 0 or above 1')
ax.set_yticks([0,1]);ax.set_yticklabels(['0  no diabetes','1  diabetes']);ax.legend(loc='upper left',fontsize=10,ncol=2,frameon=False);save(fig,'binary_linear_failure.svg')
# scales
fig,axs=plt.subplots(1,2,figsize=(12,5.5),sharex=True)
z=-1.2+1.8*(xx-30)/10
for ax in axs:dress(ax);ax.set(xlim=(5.0,80.0),xlabel='Insulin (pmol/L)')
axs[0].plot(xx,z,color=PURPLE,lw=3.4);axs[0].axhline(0,color='#8e9bae',ls=':');axs[0].set(title='Log-odds scale: a straight line',ylabel='logit(p)',ylim=(-4.5,5.2))
axs[1].plot(xx,sigmoid(z),color=GREEN,lw=3.4);axs[1].set(title='Probability scale: an S-shaped curve',ylabel = r'$\mathbb{P}(\mathrm{diabetes} = 1 \mid \mathrm{insulin})$',ylim=(-.05,1.05))
fig.suptitle('One model viewed on two scales',fontweight='bold',fontsize=17);fig.tight_layout();save(fig,'logistic_two_scales.svg')
# SBP
xx_sbp=np.linspace(90,180,320);xs=(xx_sbp-120)/10
no=sigmoid(-2.3+.34*xs);sm=sigmoid(-1.62+(.34+.26)*xs)
fig,ax=plt.subplots(figsize=(11.8,5.5));dress(ax)
ax.plot(xx_sbp,no,color=BLUE,lw=3.4,label='Non-smoker')
ax.plot(xx_sbp,sm,color=ORANGE,lw=3.4,label='Smoker')
ax.axvline(120,color=PURPLE,ls='--',lw=1.5,alpha=.8);ax.text(122,.92,'SBP centered at 120 mmHg',color=PURPLE,fontsize=11)
ax.set(xlim=(90,180),ylim=(0,1.02),xlabel='Systolic blood pressure (mmHg)',ylabel='Illustrative P(ACS = 1)',title='Smoking changes both baseline log-odds and SBP slope')
ax.legend(loc='upper left',frameon=False,ncol=2);save(fig,'sbp_smoking_curves.svg')
# multinomial softmax over age
ages = np.linspace(20, 90, 250)
lh = -.50 + .031 * (ages - 65)
lt = .10 - .029 * (ages - 65)
D = 1 + np.exp(lh) + np.exp(lt)
prob_is = 1 / D
prob_he = np.exp(lh) / D
prob_tia = np.exp(lt) / D
fig, ax = plt.subplots(figsize=(11.8, 5.7))
dress(ax)
ax.plot(ages, prob_is, color=BLUE, lw=3, label='Ischemic')
ax.plot(ages, prob_he, color=RED, lw=3, label='Hemorrhagic')
ax.plot(ages, prob_tia, color=PURPLE, lw=3, label='TIA')
ax.set(
    xlim=(20, 90),
    ylim=(0, 1),
    xlabel='Age (years), other predictors held fixed',
    ylabel='Predicted category probability',
    title='Three probabilities must add to 1 for every patient profile'
)
ax.legend(loc='upper right', ncol=3, fontsize=11, frameon=False)
save(fig, 'multinomial_probs.svg')
# counts same mean
from scipy.stats import nbinom,poisson
ks=np.arange(0,13);mu=2.8;size=1.3
pmf_po=poisson.pmf(ks,mu);pmf_nb=nbinom.pmf(ks,size,size/(size+mu))
fig,ax=plt.subplots(figsize=(11.8,5.7));dress(ax)
ax.bar(ks-.2,pmf_po,width=.38,color=BLUE,alpha=.92,label=f'Poisson: mean = variance = {mu:.1f}')
ax.bar(ks+.2,pmf_nb,width=.38,color=PURPLE,alpha=.78,label=f'Negative binomial: mean = {mu:.1f}, variance > mean')
ax.set(xlim=(-.7,12.7),ylim=(0,.29),xlabel='Episodes per patient',ylabel='Probability',title='Same mean, different dispersion')
ax.xaxis.set_major_locator(MaxNLocator(integer=True));ax.legend(frameon=False,fontsize=10);save(fig,'poisson_vs_nb.svg')
# ordinal vs counts side by side
fig,axes=plt.subplots(1,2,figsize=(11.8,5.1));
for ax in axes:dress(ax)
axes[0].bar(['mild','moderate','severe'],[.45,.35,.20],color=[BLUE,PURPLE,ORANGE]);axes[0].set(ylabel='Proportion',ylim=(0,.52),title='Ordered categories → ordinal model')
axes[1].bar(list(range(7)),[.18,.27,.21,.14,.10,.06,.04],color=GREEN);axes[1].set(xlabel='Number of episodes',ylabel='Proportion',ylim=(0,.32),title='Integer counts → count model')
fig.tight_layout();save(fig,'ordinal_vs_count.svg')
print('created',*[f.name for f in sorted(out.glob('*.svg'))],sep='\n')
