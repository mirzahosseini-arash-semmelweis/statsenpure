# Week 10 SVG figures — native R/ggplot2 regeneration option.
# Input data are SYNTHETIC examples, not measured clinical findings.
# Run from course root: source('R/render_week10_figures.R')
# Requires: ggplot2, svglite, gridExtra.
stopifnot(requireNamespace('ggplot2', quietly=TRUE),
          requireNamespace('svglite', quietly=TRUE),
          requireNamespace('gridExtra', quietly=TRUE))
library(ggplot2)

# Infer output directory whether script is sourced from EN/ or run directly.
fig_dir <- if (dir.exists('week10/figures')) 'week10/figures' else
  file.path('..', 'week10', 'figures')
dir.create(fig_dir, showWarnings=FALSE, recursive=TRUE)
blue <- '#1f6feb'; orange <- '#c65d09'; green <- '#18864b'
red <- '#c93838'; purple <- '#7b4ab5'; ink <- '#182230'; muted <- '#667085'
base_theme <- theme_bw(base_size=15) +
  theme(panel.grid.minor=element_blank(), strip.background=element_rect(fill='#f3f6fa'),
        strip.text=element_text(face='bold'), plot.title=element_text(face='bold',size=16),
        axis.title=element_text(color=ink), legend.position='bottom')
sv <- function(p, name, w=11.5, h=4.5) {
  ggplot2::ggsave(file.path(fig_dir,name),plot=p,width=w,height=h,units='in',device=svglite::svglite,bg='white')
}

# 1. confounding: within-stratum risks differ; pooled risks coincide.
a <- data.frame(stratum=rep(c('Low rent','High rent','Pooled'),each=2),
                drinks=rep(c('Few','Many'),3),
                bad=c(10,20,60,80,40,40),
                count=c('4/40','12/60','36/60','24/30','40/100','36/90'))
p <- ggplot(a,aes(drinks,bad,fill=drinks))+geom_col(width=.65)+
  geom_text(aes(label=paste0(count,' = ',bad,'%')),vjust=-.6,size=4)+
  facet_wrap(~stratum,nrow=1)+scale_fill_manual(values=c(Few=blue,Many=orange))+
  coord_cartesian(ylim=c(0,100))+labs(title='Stratified versus pooled association',x='',y='Bad school outcome (%)')+base_theme
sv(p,'confounding_strata.svg',13,4.5)

# 2. synthetic hospital Simpson case
h <- data.frame(hospital=rep(c('A','B','C'),each=2),arm=rep(c('Drug','Control'),3),
                rate=c(30,20,60,50,90,80),n=c(180,40,80,80,40,180))
p1 <- ggplot(h,aes(hospital,rate,fill=arm))+geom_col(position='dodge',width=.67)+
  scale_fill_manual(values=c(Drug=green,Control=blue))+coord_cartesian(ylim=c(0,100))+
  labs(title='Within every hospital: drug better',x='Hospital',y='Favorable outcome (%)')+base_theme
p2 <- ggplot(data.frame(arm=c('Drug','Control'),rate=c(46,64)),aes(arm,rate,fill=arm))+
  geom_col(width=.6)+geom_text(aes(label=paste0(rate,'%')),vjust=-.4,size=5)+
  scale_fill_manual(values=c(Drug=green,Control=blue))+coord_cartesian(ylim=c(0,100))+
  labs(title='Aggregated: apparent reversal',x='',y='Favorable outcome (%)')+base_theme+theme(legend.position='none')
sv(gridExtra::arrangeGrob(p1,p2,ncol=2),'hospital_simpson.svg',13,4.5)

# 3. prevalence & incidence schematic
pop <- data.frame(stage=c('Population','Already affected','New cases during follow-up'),
                  count=c(1000,50,40))
p <- ggplot(pop,aes(stage,count,fill=stage))+geom_col(width=.52)+
  geom_text(aes(label=count),vjust=-.4,size=4.4)+
  scale_fill_manual(values=c('Population'=blue,'Already affected'=orange,
                             'New cases during follow-up'=red))+
  scale_y_continuous(limits=c(0,1100))+coord_flip()+
  labs(title='Prevalent cases versus new cases during follow-up',x='',y='People')+
  base_theme+theme(legend.position='none')
sv(p,'incidence_prevalence.svg',12,3.8)

# 4. Confounding DAG (geometrically schematic, not a fitted model)
nodes <- data.frame(label=c('Sugary drinks X','Household resources Z','School performance Y'),x=c(1,2.5,4),y=c(0,1.2,0))
links <- data.frame(x=c(2.35,2.7,1.35),y=c(1.08,1.08,0),xend=c(1.17,3.85,3.65),yend=c(.1,.1,0))
p <- ggplot()+geom_segment(data=links,aes(x,y,xend=xend,yend=yend),arrow=grid::arrow(length=grid::unit(.22,'cm')),linewidth=1,color=muted)+
  geom_label(data=nodes,aes(x,y,label=label),fill='white',color=ink,size=4.3,label.size=.75)+
  scale_x_continuous(limits=c(.3,4.8))+scale_y_continuous(limits=c(-.65,1.8))+
  labs(title='A common cause of exposure and outcome')+theme_void(base_size=15)+
  theme(plot.title=element_text(face='bold',color=ink))
sv(p,'confounding_dag.svg',11,4)

# 5. Risk ratios versus absolute changes
rr <- data.frame(scenario=rep(c('Low baseline risk','High baseline risk'),each=2),
  arm=rep(c('Control','Treatment'),2),risk=c(2,1,40,20))
p <- ggplot(rr,aes(arm,risk,fill=arm))+geom_col(width=.55)+
  geom_text(aes(label=paste0(risk,'%')),vjust=-.5,size=4.5)+
  facet_wrap(~scenario)+scale_fill_manual(values=c(Control=orange,Treatment=green))+
  coord_cartesian(ylim=c(0,48))+labs(title='Both have RR = 0.5; different risk differences',x='',y='Event risk (%)')+base_theme
sv(p,'relative_absolute_risk.svg',12,4.4)

# 6. Confusion matrix geometry
cm <- data.frame(reference=rep(c('Sick','Healthy'),each=2),test=rep(c('Positive','Negative'),2),
                 n=c(38,8,12,142),kind=c('TP','FN','FP','TN'))
p <- ggplot(cm,aes(test,reference,fill=kind))+geom_tile(color='#d9e1ea',linewidth=2)+
  geom_text(aes(label=paste0(kind,'\n',n)),fontface='bold',size=7,color=ink)+
  scale_fill_manual(values=c(TP='#e8f7ec',TN='#e8f7ec',FP='#fceeed',FN='#fceeed'))+
  labs(title='Observed versus reference-standard status',x='Test result',y='Reference status')+base_theme+
  theme(legend.position='none',panel.grid=element_blank())
sv(p,'confusion_matrix.svg',10,4.8)

# 7–9. Diagram helper, in native ggplot2; arrows point between blocks.
diagram <- function(boxes, arrows, title, name, w=12, h=3.3) {
  boxes <- transform(boxes,xmin=x-.45,xmax=x+.45,ymin=y-.19,ymax=y+.19)
  p <- ggplot()+geom_rect(data=boxes,aes(xmin=xmin,xmax=xmax,ymin=ymin,ymax=ymax),
                          fill='#f8fafc',color=purple,linewidth=1.3)+
    geom_text(data=boxes,aes(x,y,label=label),color=ink,fontface='bold',size=4.3)+
    geom_segment(data=arrows,aes(x=x,y=y,xend=xend,yend=yend),
                 arrow=grid::arrow(length=grid::unit(.18,'cm')),color=muted,linewidth=1)+
    coord_equal(xlim=c(-.5,5),ylim=c(-.1,2.45),expand=FALSE)+
    labs(title=title)+theme_void(base_size=15)+theme(plot.title=element_text(face='bold',color=ink))
  sv(p,name,w,h)
}
diagram(data.frame(x=c(.5,2.25,4,4),y=c(1.1,1.1,1.75,.55),label=c('Pool samples','Assay pool','Negative: stop','Positive: retest')),
  data.frame(x=c(1,2.75,2.75),y=c(1.1,1.14,1.05),xend=c(1.8,3.55,3.55),yend=c(1.1,1.75,.55)),
  'Group testing at low prevalence','pooled_testing.svg')
diagram(data.frame(x=c(.5,2.25,4,4),y=c(1.1,1.1,1.75,.55),label=c('Eligible patients','Randomization','Treatment','Comparator')),
  data.frame(x=c(1,2.75,2.75),y=c(1.1,1.14,1.05),xend=c(1.8,3.55,3.55),yend=c(1.1,1.75,.55)),
  'Two-arm randomized comparison','trial_design_flow.svg')
ends <- data.frame(x=1:4,y=1,label=c('Primary\nendpoint','Secondary:\nweight','Secondary:\nlipids','Safety:\nadverse events'))
p <- ggplot(ends,aes(x,y,label=label))+geom_label(fill='#f3f6fa',color=ink,size=5,label.size=1.3)+
  xlim(.3,4.7)+ylim(.3,1.7)+labs(title='Prespecify endpoints and multiplicity controls')+
  theme_void(base_size=15)+theme(plot.title=element_text(face='bold',color=ink))
sv(p,'trial_endpoints.svg',12,3.5)

# 10. Dose-response families
doses <- exp(seq(log(.01),log(100),length.out=300))
xy <- expand.grid(dose=doses,ec50=c(.3,1,3))
xy$response <- 100*xy$dose^1.5/(xy$ec50^1.5+xy$dose^1.5)
xy$ec50 <- factor(xy$ec50,levels=c(.3,1,3),labels=c('EC50 0.3','EC50 1','EC50 3'))
p1 <- ggplot(xy,aes(dose,response,color=ec50))+geom_line(linewidth=1.3)+scale_x_log10()+
  scale_color_manual(values=c(blue,green,orange))+labs(title='Potency changes EC50',x='Dose, log axis',y='Response (%)')+base_theme
xz <- expand.grid(logdose=seq(-2,2,length.out=300),slope=c(.7,1.8,4))
xz$response <- 100/(1+exp(-xz$slope*xz$logdose))
xz$slope <- factor(xz$slope)
p2 <- ggplot(xz,aes(logdose,response,color=slope))+geom_line(linewidth=1.3)+
  scale_color_manual(values=c(blue,green,orange))+labs(title='Hill slope changes the transition',x='Log10 dose',y='Response (%)')+base_theme
sv(gridExtra::arrangeGrob(p1,p2,ncol=2),'dose_response_families.svg',13,4.7)

# 11. NOAEL/LOAEL/BMD
x <- seq(0,100,length.out=400)
risk <- function(d) .04+.9/(1+exp(-(d-54)/11))
dose <- c(0,12,25,38,55,75,95)
base <- risk(0);rstar <- base+.10
bmd <- 54+11*log(((rstar-.04)/.9)/(1-(rstar-.04)/.9))
p <- ggplot(data.frame(x,risk=risk(x)),aes(x,risk))+geom_line(color=purple,linewidth=1.6)+
  geom_point(data=data.frame(x=dose,risk=risk(dose)),aes(x,risk),color=blue,size=3)+
  geom_vline(xintercept=25,color=green,linetype=2)+geom_vline(xintercept=38,color=red,linetype=2)+
  geom_vline(xintercept=bmd,color=orange,linetype=3)+
  annotate('text',x=25,y=.78,label='NOAEL',color=green,hjust=0,size=4)+
  annotate('text',x=38,y=.68,label='LOAEL',color=red,hjust=0,size=4)+
  annotate('text',x=bmd,y=.55,label='BMD',color=orange,hjust=0,size=4)+
  labs(title='Observed levels versus modeled benchmark dose',x='Dose (arbitrary units)',y='Adverse response probability')+base_theme
sv(p,'toxicology_bmd.svg',12,4.5)

# 12. Forest plot: inverse-variance pooled log risk ratio.
study <- data.frame(study=paste('Study',LETTERS[1:7]),rr=c(.78,.89,1.04,.84,.70,.93,.82),
                    se=c(.115,.088,.155,.10,.185,.092,.132))
study$low <- exp(log(study$rr)-1.96*study$se)
study$high<- exp(log(study$rr)+1.96*study$se)
weight <- 1/study$se^2
pooled <- sum(weight*log(study$rr))/sum(weight)
pse <- sqrt(1/sum(weight))
study$position <- 7:1
p <- ggplot(study,aes(x=rr,y=position))+
  geom_vline(xintercept=1,color=red,linetype=2)+
  geom_segment(aes(x=low,xend=high,y=position,yend=position),linewidth=.8,color=ink)+
  geom_point(aes(size=1/se^2),color=blue,shape=15)+
  annotate('point',x=exp(pooled),y=0,shape=23,size=6,fill=green,color=green)+
  scale_y_continuous(breaks=0:7,labels=c('Pooled',study$study[7:1]),limits=c(-.8,8))+
  scale_x_log10(breaks=c(.4,.6,.8,1,1.2,1.5),limits=c(.35,1.65))+
  scale_size_continuous(range=c(3,7),guide='none')+
  labs(title=sprintf('Synthetic common-effect forest plot · pooled RR %.2f',exp(pooled)),x='Risk ratio (95% CI)',y='Study')+base_theme
sv(p,'forest_anatomy.svg',12.5,5.0)

# 13. Funnel plots
set.seed(310)
a <- data.frame(se=runif(70,.04,.35),example='Approximately symmetric')
set.seed(310)
a$effect <- -.18+rnorm(nrow(a))*a$se
b <- data.frame(se=runif(90,.04,.35),example='Illustrative asymmetry')
b$effect <- -.18+rnorm(nrow(b))*b$se
b <- subset(b,se<.15 | effect<-.06)
fun <- rbind(a,b)
p <- ggplot(fun,aes(effect,se))+geom_point(color=blue,alpha=.65,size=2)+
  geom_vline(xintercept=-.18,color=green)+
  facet_wrap(~example)+scale_y_reverse()+labs(title='Funnel asymmetry has multiple possible causes',x='Estimated log risk ratio',y='Standard error')+base_theme
sv(p,'funnel_anatomy.svg',13,4.6)

message('Week 10 SVG regeneration complete in ',normalizePath(fig_dir))
