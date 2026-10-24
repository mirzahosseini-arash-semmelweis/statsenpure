#!/usr/bin/env python3
"""Deterministic, synthetic teaching SVG figures for Week 10.
Figures are not measured clinical evidence or validated diagnostic tests.
"""
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy.stats import norm, lognorm
from pathlib import Path

OUT=Path(__file__).resolve().parents[1]/'week10'/'figures'
OUT.mkdir(parents=True, exist_ok=True)
BLUE='#1f6feb'; ORANGE='#c65d09'; GREEN='#18864b'; RED='#c93838'; PURPLE='#7b4ab5'; NAVY='#182230'; MUTED='#667085'; LINE='#d9e1ea'
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':12,'svg.fonttype':'none','axes.spines.right':False,'axes.spines.top':False,'axes.labelcolor':NAVY,'text.color':NAVY,'xtick.color':MUTED,'ytick.color':MUTED,'axes.edgecolor':LINE,'grid.color':'#e7ecf2','figure.facecolor':'white','savefig.facecolor':'white'})
rng=np.random.default_rng(80410)

def save(fig,name):
    fig.savefig(OUT/name,format='svg',bbox_inches='tight',pad_inches=.14)
    plt.close(fig)

def labelbars(ax, bars, fmt='{:.0f}%'):
    for b in bars:
        ax.text(b.get_x()+b.get_width()/2,b.get_height()+1.4,fmt.format(b.get_height()),ha='center',fontsize=12,fontweight='bold')

# Confounding: association appears when pooled

fig, axs = plt.subplots(
    1, 3,
    figsize=(13, 4),
    sharey=True
)

for ax, values, title, note in zip(
    axs,
    [[10, 10], [50, 50], [17, 43]],
    ['Low rent', 'High rent', 'Aggregated'],
    ['10/100 vs 2/20', '10/20 vs 50/100', '20/120 vs 52/120']
):
    bars = ax.bar(
        ['Few drinks', 'Many drinks'],
        values,
        color=[BLUE, ORANGE],
        width=.63
    )

    labelbars(ax, bars)

    ax.set_ylim(0, 99)
    ax.set_title(title, fontsize=17, weight='bold', pad=15)

    ax.text(
        .5, 1.01, note,
        transform=ax.transAxes,
        ha='center',
        fontsize=10,
        color=MUTED
    )

    ax.grid(axis='y', alpha=.6)
    ax.set_axisbelow(True)

axs[0].set_ylabel('Bad scholastic outcome (%)')

fig.suptitle(
    'No association in strata; appearing when pooled',
    fontsize=17,
    y=0.97
)

# Explicit margins so everything fits within the fixed canvas
fig.subplots_adjust(
    left=0.08,
    right=0.98,
    bottom=0.18,
    top=0.73,
    wspace=0.25
)

# 1. Save the complete figure
fig.savefig(
    'confounding_strata.svg',
    format='svg',
    bbox_inches=None,
    transparent=True
)

# 2. Hide the third subplot completely
axs[2].set_visible(False)

# 3. Save the masked version with IDENTICAL canvas dimensions
fig.savefig(
    'confounding_strata_masked.svg',
    format='svg',
    bbox_inches=None,
    transparent=True
)

plt.close(fig)

# Simpson hospital case drug better in each hospital yet pooled lower.
fig,axs=plt.subplots(1,2,figsize=(12.5,4.2)); x=np.arange(3);w=.35
T=np.array([30,60,90]);C=np.array([20,50,80]);nt=[180,80,40];nc=[40,80,180]
for ax in axs:
    ax.grid(axis='y',alpha=.6);ax.set_axisbelow(True)
axs[0].bar(x-w/2,T,w,label='Drug',color=GREEN);axs[0].bar(x+w/2,C,w,label='Control',color=BLUE)
axs[0].set_xticks(x,['Hospital A','Hospital B','Hospital C']);axs[0].set_ylim(0,105);axs[0].set_ylabel('Favorable outcome (%)');axs[0].legend(frameon=False,ncol=2,loc='upper left',bbox_to_anchor=(0.02, 0.88))
axs[0].set_title('Each hospital: drug better',fontweight='bold')
for i in range(3): axs[0].text(i,100,f'n: {nt[i]} / {nc[i]}',ha='center',fontsize=10,color=MUTED)
bs=axs[1].bar(['Drug','Control'],[46,64],color=[GREEN,BLUE],width=.48)
labelbars(axs[1],bs);axs[1].set_ylim(0,105);axs[1].set_title('Pooled: apparent reversal',fontweight='bold');axs[1].set_ylabel('Favorable outcome (%)')
fig.tight_layout();save(fig,'hospital_simpson.svg')

# Risk: RR=0.5 but RD different by baseline risk.
fig,axs=plt.subplots(1,2,figsize=(11,4),sharey=True)
for ax,vals,title,txt in zip(axs,[[2,1],[40,20]],['Low baseline risk','High baseline risk'],['RR = 0.50, RD = 1 pp','RR = 0.50, RD = 20 pp']):
    bars=ax.bar(['Control','Treatment'],vals,color=[ORANGE,GREEN],width=.5)
    labelbars(ax,bars);ax.set_ylim(0,49);ax.set_title(title,fontweight='bold');ax.text(.5,.88,txt,transform=ax.transAxes,ha='center',color=PURPLE,weight='bold',fontsize=12);ax.grid(axis='y',alpha=.5);ax.set_axisbelow(True)
axs[0].set_ylabel('Event risk (%)');fig.tight_layout();save(fig,'relative_absolute_risk.svg')

# Population incidence schematic
fig,ax=plt.subplots(figsize=(12,3.3));ax.set_xlim(0,1000);ax.set_ylim(-.6,3.8);ax.axis('off')
for y,title,beg,end,color in [(2.9,'Population at baseline',0,1000,BLUE),(1.65,'Already ill / prevalent',0,50,ORANGE),(0.4,'New cases during follow-up',50,90,RED)]:
    ax.text(0,y+.52,title,fontsize=14,fontweight='bold')
    ax.add_patch(plt.Rectangle((0,y),1000,.35,facecolor='#edf2f8',edgecolor=LINE))
    ax.add_patch(plt.Rectangle((beg,y),max(end-beg,4),.35,facecolor=color))
ax.text(1000,3.42,'N = 1,000',ha='right',fontsize=12,color=MUTED);ax.text(1000,2.16,'50 cases at baseline = 5% prevalence',ha='right',fontsize=12,color=ORANGE)
ax.text(1000,.92,'40 incident cases among 950 at risk = 4.2% cumulative incidence',ha='right',fontsize=11,color=RED)
save(fig,'incidence_prevalence.svg')

# Confusion matrix illustrator
fig,ax=plt.subplots(figsize=(10,4.5));ax.axis('off')
from matplotlib.patches import Rectangle
for row in range(2):
    for col in range(2):
        x=.22+col*.38;y=.17+(1-row)*.37
        text=[['True positive (TP)','False negative (FN)'],['False positive (FP)','True negative (TN)']][row][col]
        val=[[38,8],[12,142]][row][col]
        ax.add_patch(Rectangle((x,y),.34,.3,facecolor=('#e8f7ec' if row==col else '#fceeed'),edgecolor=(GREEN if row==col else RED),lw=1.8,transform=ax.transAxes))
        ax.text(x+.17,y+.2,text,ha='center',transform=ax.transAxes,color=NAVY,fontweight='bold',fontsize=12)
        ax.text(x+.17,y+.08,str(val),ha='center',transform=ax.transAxes,color=GREEN if row==col else RED,fontweight='bold',fontsize=22)
ax.text(.59,.97,'Test says',ha='center',transform=ax.transAxes,fontsize=18,fontweight='bold')
ax.text(.39,.87,'Positive',ha='center',transform=ax.transAxes,fontsize=12,color=MUTED)
ax.text(.77,.87,'Negative',ha='center',transform=ax.transAxes,fontsize=12,color=MUTED)
ax.text(.08,.67,'Sick',va='center',transform=ax.transAxes,fontsize=12,fontweight='bold')
ax.text(.08,.3,'Healthy',va='center',transform=ax.transAxes,fontsize=12,fontweight='bold')
save(fig,'confusion_matrix.svg')

# Trial study flow
fig,ax=plt.subplots(figsize=(13,3.5));ax.axis('off')
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
boxes=[(.015,.36,.2,.28,'Eligible patients',BLUE),(.31,.36,.2,.28,'Random allocation',PURPLE),(.64,.62,.25,.24,'Treatment arm',GREEN),(.64,.18,.25,.24,'Comparator arm',ORANGE)]
for x,y,w,h,name,color in boxes:
 ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=.014,rounding_size=.025',transform=ax.transAxes,facecolor='#f8fafc',edgecolor=color,lw=2.3))
 ax.text(x+w/2,y+h/2,name,ha='center',va='center',transform=ax.transAxes,fontsize=13,fontweight='bold')
for a,b in [((.23,.5),(.30,.5)),((.525,.5),(.63,.74)),((.525,.5),(.63,.3))]:
 ax.add_patch(FancyArrowPatch(a,b,arrowstyle='-|>',mutation_scale=21,lw=2,color=MUTED,transform=ax.transAxes))
ax.text(.775,.91,'Same endpoint and planned follow-up in both arms',ha='center',transform=ax.transAxes,fontsize=12,color=MUTED)
ax.text(.5,.02,'Conceal the allocation sequence; mask participants/assessors when feasible.',ha='center',transform=ax.transAxes,fontsize=11,color=MUTED)
save(fig,'trial_design_flow.svg')

# Dose response Emax, logit on log dose
fig,axs=plt.subplots(1,2,figsize=(11.8,4.3));x=np.logspace(-2,2,260); lx=np.log10(x)
for ec,color,lbl in [(0.3,BLUE,'Higher potency'),(1.0,GREEN,'Reference'),(3.0,ORANGE,'Lower potency')]:
 y=100*x**1.5/(ec**1.5+x**1.5)
 axs[0].semilogx(x,y,color=color,lw=2.8,label=lbl)
axs[0].axhline(50,color=PURPLE,ls='--',alpha=.7);axs[0].axvline(1,color=PURPLE,ls='--',alpha=.7)
axs[0].set(xlabel='Dose / concentration (log scale)',ylabel='Response (%)',ylim=(-2,106));axs[0].set_title('Potency and EC50',fontweight='bold');axs[0].legend(frameon=False,fontsize=10,loc='lower right')
for slope,color in [(.7,BLUE),(1.8,GREEN),(4,ORANGE)]:
 axs[1].plot(lx,100/(1+np.exp(-slope*lx)),lw=2.8,color=color,label=f'Steepness {slope:g}')
axs[1].set(xlabel='Log10 dose',ylabel='Response (%)',ylim=(-2,106));axs[1].set_title('Slope changes the transition',fontweight='bold');axs[1].legend(frameon=False,fontsize=10)
for ax in axs: ax.grid(alpha=.35)
fig.tight_layout();save(fig,'dose_response_families.svg')

# toxicity NOAEL LOAEL + benchmark dose illustrative curve
fig,ax=plt.subplots(figsize=(11.5,4.2)); x=np.linspace(0,100,500)
y=0.04+0.90/(1+np.exp(-(x-54)/11)); doses=np.array([0,12,25,38,55,75,95]);observed=0.04+0.90/(1+np.exp(-(doses-54)/11))+np.array([0,-.005,.005,.01,.0,-.02,.01]);
ax.plot(x,y,color=PURPLE,lw=3,label='Fitted adverse-response model');ax.scatter(doses,observed,color=BLUE,s=85,zorder=5,label='Observed dose groups')
for d,color,text in [(25,GREEN,'NOAEL'),(38,RED,'LOAEL')]:
 ax.axvline(d,color=color,ls='--',lw=2);ax.text(d+1,.79 if d==25 else .72,text,color=color,fontsize=12,weight='bold')
bmd = 31.0  # illustrative benchmark dose (x-axis)
ax.axvline(bmd, color=ORANGE, ls=':', lw=2)
ax.text(bmd + 1, .61, 'BMD', color=ORANGE, fontsize=11, weight='bold')
# Benchmark response level (y-axis: baseline 0.04 + 10% extra risk = 0.14)
bmr = 0.04 + 0.90 / (1 + np.exp(-(bmd - 54) / 11))
ax.axhline(bmr, color=ORANGE, ls=':', lw=2)
ax.text(2, bmr + 0.03, 'Benchmark response (14% extra risk)', color=ORANGE, fontsize=11)
ax.set(xlabel='Dose (arbitrary units)',ylabel='Observed adverse-response probability',ylim=(0,1),xlim=(0,100));ax.set_title('Observed study levels ≠ modeled dose estimate',fontweight='bold');ax.grid(alpha=.3);ax.legend(loc='upper left',frameon=False,fontsize=10)
save(fig,'toxicology_bmd.svg')

# effect forest
studies=['Trial A','Trial B','Trial C','Trial D','Trial E','Trial F','Trial G']; est=np.array([.78,.89,1.04,.84,.70,.93,.82]);se=np.array([.115,.088,.155,.10,.185,.092,.132]);ll=np.exp(np.log(est)-1.96*se);ul=np.exp(np.log(est)+1.96*se);w=1/se**2;w/=sum(w); pooled=np.exp(np.sum(w*np.log(est))); pooledse=1/np.sqrt(sum(1/se**2));pl=np.exp(np.log(pooled)-1.96*pooledse);pu=np.exp(np.log(pooled)+1.96*pooledse)
fig,ax=plt.subplots(figsize=(12.5,5)); y=np.arange(len(studies),0,-1)
ax.axvline(1,color=RED,linestyle='--',lw=1.7,label='No effect (RR = 1)')
for i,z in enumerate(y):
 ax.plot([ll[i],ul[i]],[z,z],color=NAVY,lw=1.6)
 ax.scatter([est[i]],[z],s=55+w[i]*540,marker='s',color=BLUE,zorder=4)
 ax.text(1.39,z,f'{est[i]:.2f} [{ll[i]:.2f}, {ul[i]:.2f}]',va='center',fontsize=11)
ax.fill([pl,pooled,pu,pooled],[0,0.35,0,-.35],color=GREEN,alpha=.9)
ax.text(1.39,0,f'{pooled:.2f} [{pl:.2f}, {pu:.2f}]',va='center',fontsize=11,fontweight='bold',color=GREEN)
ax.set_yticks(list(y)+[0],studies+['Pooled']);ax.set_xlim(.3,1.77);ax.set_ylim(-.8,8.1)
ax.set(xlabel='Risk ratio (log scale)');ax.set_xscale('log');ax.set_xticks([.4,.6,.8,1,1.2,1.5],['0.4','0.6','0.8','1.0','1.2','1.5'])
ax.set_title('Common-effect meta-analysis · synthetic trials',fontweight='bold');ax.grid(axis='x',alpha=.4)
save(fig,'forest_anatomy.svg')

# funnel side by side
fig,axs=plt.subplots(1,2,figsize=(11.7,4.2)); rng=np.random.default_rng(44)
for ax,skew,title in zip(axs,[False,True],['Approximately symmetric','Illustrative asymmetry']):
 se=rng.uniform(.045,.35,75)
 eff=-.18+rng.normal(size=75)*se
 if skew:
  keep=(se<.15)|(eff<-.06)
  se,eff=se[keep],eff[keep]
 ax.scatter(eff,se,s=27,color=BLUE,alpha=.68)
 for q in (-1.96,1.96): ax.plot(-.18+q*np.array([0,.36]),[0,.36],color=PURPLE,linestyle='--',alpha=.6)
 ax.axvline(-.18,color=GREEN,lw=2);ax.invert_yaxis();ax.set(xlim=(-1,.65),ylim=(.36,0),xlabel='Estimated log risk ratio',ylabel='Standard error')
 ax.set_title(title,fontweight='bold');ax.grid(alpha=.3)
fig.tight_layout();save(fig,'funnel_anatomy.svg')

# group testing
fig,ax=plt.subplots(figsize=(12,3.6));ax.axis('off');from matplotlib.patches import FancyBboxPatch
for x,y,w,h,t,c in [(.04,.32,.22,.36,'Pool 8 samples',BLUE),(.38,.32,.24,.36,'Test pooled material',PURPLE),(.74,.58,.2,.22,'Negative: done',GREEN),(.74,.19,.2,.22,'Positive: retest',ORANGE)]:
 ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=.015,rounding_size=.025',facecolor='#f8fafc',edgecolor=c,lw=2,transform=ax.transAxes));ax.text(x+w/2,y+h/2,t,ha='center',va='center',transform=ax.transAxes,fontsize=12,weight='bold')
for a,b in [((.275,.5),(.37,.5)),((.635,.5),(.73,.69)),((.635,.5),(.73,.3))]:ax.add_patch(FancyArrowPatch(a,b,arrowstyle='-|>',mutation_scale=20,color=MUTED,lw=2,transform=ax.transAxes))
ax.text(.5,.04,'Best for low prevalence with validated assay sensitivity at the pooled dilution.',ha='center',transform=ax.transAxes,fontsize=12,color=MUTED)
save(fig,'pooled_testing.svg')

# study bias causal graph
fig, ax = plt.subplots(figsize=(10, 3.3))
ax.axis('off')

w, h = 0.24, 0.20
nodes = [
    (0.17, 0.25, 'Sugary drinks\nX', BLUE),
    (0.50, 0.73, 'Household resources\nZ', PURPLE),
    (0.83, 0.25, 'School performance\nY', ORANGE),
]

for x, y, t, c in nodes:
    ax.add_patch(
        FancyBboxPatch(
            (x - w / 2, y - h / 2),
            w,
            h,
            boxstyle='round,pad=.015,rounding_size=.03',
            facecolor='white',
            edgecolor=c,
            lw=2.5,
            transform=ax.transAxes,
        )
    )
    ax.text(
        x,
        y,
        t,
        ha='center',
        va='center',
        fontsize=12,
        weight='bold',
        transform=ax.transAxes,
    )

arrows = [
    ((0.30, 0.25), (0.70, 0.25)),  # X -> Y
]

for a, b in arrows:
    ax.add_patch(
        FancyArrowPatch(
            a,
            b,
            arrowstyle='-|> ',
            mutation_scale=22,
            color=MUTED,
            lw=2,
            transform=ax.transAxes,
        )
    )

# Question mark above the X -> Y arrow
ax.text(
    0.50,
    0.25,
    '?',
    ha='center',
    va='center',
    fontsize=14,
    fontweight='bold',
    color=MUTED,
    transform=ax.transAxes,
    bbox=dict(boxstyle='round,pad=0.2', facecolor='white', edgecolor='none'),
)

save(fig, 'confounding_dag1.svg')

fig, ax = plt.subplots(figsize=(10, 3.3))
ax.axis('off')

w, h = 0.24, 0.20
nodes = [
    (0.17, 0.25, 'Sugary drinks\nX', BLUE),
    (0.50, 0.73, 'Household resources\nZ', PURPLE),
    (0.83, 0.25, 'School performance\nY', ORANGE),
]

for x, y, t, c in nodes:
    ax.add_patch(
        FancyBboxPatch(
            (x - w / 2, y - h / 2),
            w,
            h,
            boxstyle='round,pad=.015,rounding_size=.03',
            facecolor='white',
            edgecolor=c,
            lw=2.5,
            transform=ax.transAxes,
        )
    )
    ax.text(
        x,
        y,
        t,
        ha='center',
        va='center',
        fontsize=12,
        weight='bold',
        transform=ax.transAxes,
    )

arrows = [
    ((0.43, 0.62), (0.23, 0.36)),  # Z -> X
    ((0.57, 0.62), (0.77, 0.36)),  # Z -> Y
]

for a, b in arrows:
    ax.add_patch(
        FancyArrowPatch(
            a,
            b,
            arrowstyle='-|> ',
            mutation_scale=22,
            color=MUTED,
            lw=2,
            transform=ax.transAxes,
        )
    )

save(fig, 'confounding_dag2.svg')

# additional small: endpoint multiplicity
fig,ax=plt.subplots(figsize=(11,3.4)); ax.set_axis_off()
for k,txt in enumerate(['Primary:\nSBP week 12','Secondary:\nweight','Secondary:\nlipids','Safety:\nadverse events']):
 x=.03+k*.242; color=GREEN if k==0 else MUTED
 ax.add_patch(FancyBboxPatch((x,.22),.225,.54,boxstyle='round,pad=.01',facecolor='#f7fbf8' if k==0 else '#f8fafc',edgecolor=color,lw=2 if k==0 else 1.2,transform=ax.transAxes))
 ax.text(x+.1125,.52,txt,ha='center',va='center',transform=ax.transAxes,fontsize=11.6,weight='bold' if k==0 else 'normal',wrap=True)
 ax.text(x+.1125,.32,'PRESPECIFIED' if k==0 else 'SUPPORTIVE',ha='center',fontsize=9,transform=ax.transAxes,color=color)
ax.text(.5,.06,'Every additional confirmatory claim requires a multiplicity strategy.',ha='center',transform=ax.transAxes,fontsize=12,color=RED)
save(fig,'trial_endpoints.svg')

print('Generated',len(list(OUT.glob('*.svg'))),'SVGs')
