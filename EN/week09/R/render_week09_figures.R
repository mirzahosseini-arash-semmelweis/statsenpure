# Week 09 synthetic teaching figures (native R + ggplot2 SVG workflow)
# Install, if needed: install.packages(c("ggplot2", "patchwork", "svglite"))
# Run from the course's EN directory: Rscript R/render_week09_figures.R
# All outputs are synthetic educational examples. No clinical data are loaded.
suppressPackageStartupMessages({
  library(ggplot2)
  library(patchwork)
  library(svglite)
})

out <- "week09/figures"
dir.create(out, recursive = TRUE, showWarnings = FALSE)
set.seed(901)
C <- list(blue="#1f6feb", orange="#c65d09", green="#18864b",
          red="#c93838", purple="#7b4ab5", ink="#182230",
          muted="#667085", line="#d9e1ea")

th <- function() {
  theme_bw(base_size=16) +
    theme(plot.title=element_text(face="bold", color=C$ink, size=18),
          axis.title=element_text(color=C$ink, size=15),
          axis.text=element_text(color=C$muted, size=13),
          panel.grid.minor=element_blank(),
          panel.grid.major=element_line(color="#edf1f6", linewidth=.35),
          panel.border=element_blank(),
          legend.position="top", legend.title=element_blank(),
          legend.text=element_text(color=C$ink),
          plot.margin=margin(12,15,12,12))
}
export <- function(p, stem, width=11.8, height=5.6) {
  ggsave(file.path(out, paste0(stem,".svg")), p,
         device=svglite::svglite, width=width, height=height, units="in")
}
invlogit <- function(z) plogis(z)

# 1. Why ordinary least squares is unsuitable for a binary response.
x <- seq(4.1, 10.1, length.out=105) + rnorm(105, 0, .12)
y <- rbinom(length(x), 1, invlogit(-.35+1.55*(x-6.5)))
dat <- data.frame(hba1c=x, diabetes=y, jittered=y+runif(length(y),-.055,.055))
xs <- seq(3.5,10.5,length.out=300)
lines <- data.frame(hba1c=xs,
                    ordinary=unname(coef(lm(diabetes~hba1c,dat))[1] + coef(lm(diabetes~hba1c,dat))[2]*xs),
                    logistic=invlogit(-.35+1.55*(xs-6.5)))
p <- ggplot(dat,aes(hba1c,jittered)) +
  annotate("rect", xmin=-Inf,xmax=Inf,ymin=0,ymax=1,fill="#eef5ff",alpha=.8) +
  geom_point(color=C$blue,alpha=.55,size=2.4) +
  geom_line(data=lines,aes(hba1c,ordinary),inherit.aes=FALSE,color=C$red,linewidth=1.1) +
  geom_line(data=lines,aes(hba1c,logistic),inherit.aes=FALSE,color=C$green,linewidth=1.1,linetype=2) +
  coord_cartesian(xlim=c(3.5,10.5),ylim=c(-.33,1.38)) +
  scale_y_continuous(breaks=c(0,1),labels=c("0  no diabetes", "1  diabetes")) +
  labs(title="An ordinary line can predict below 0 or above 1",
       x="HbA1c (%)",y="Recorded outcome / modeled probability") + th()
export(p,"binary_linear_failure")

# 2. Same binary regression viewed on logit and response scales.
x <- seq(4.1,9.5,length.out=300);eta <- -.35+1.55*(x-6.5)
a <- ggplot(data.frame(x,eta),aes(x,eta)) + geom_line(color=C$purple,linewidth=1.2) +
  geom_hline(yintercept=0,linetype=3,color="#9aa6b5") +
  labs(title="Log-odds scale: a straight line",x="HbA1c (%)",y="logit(p)") + th()
b <- ggplot(data.frame(x,p=invlogit(eta)),aes(x,p)) +
  geom_line(color=C$green,linewidth=1.2) + coord_cartesian(ylim=c(0,1)) +
  labs(title="Probability scale: an S-shaped curve",x="HbA1c (%)",y="P(diabetes = 1 | HbA1c)") + th()
export(a+b+plot_annotation(title="One model viewed on two scales"),"logistic_two_scales",12,5.5)

# 3. Two smoking strata, different modeled SBP slopes.
sbp <- seq(90,180,length.out=300);z <- (sbp-120)/10
curves <- rbind(data.frame(sbp=sbp,p=invlogit(-2.3+.34*z),group="Non-smoker"),
                data.frame(sbp=sbp,p=invlogit(-1.62+.60*z),group="Smoker"))
p <- ggplot(curves,aes(sbp,p,color=group)) + geom_line(linewidth=1.3) +
  geom_vline(xintercept=120,linetype=2,color=C$purple) +
  scale_color_manual(values=c("Non-smoker"=C$blue,"Smoker"=C$orange)) +
  coord_cartesian(ylim=c(0,1)) +
  labs(title="Smoking changes both baseline log-odds and SBP slope",
       x="Systolic blood pressure (mmHg)",y="Illustrative P(ACS = 1)") + th()
export(p,"sbp_smoking_curves")

# 4. Multinomial softmax: three mutually exclusive probabilities that sum to 1.
age <- seq(40,90,length.out=250)
h <- -.5 + .031*(age-65);t <- .1 - .029*(age-65)
D <- 1+exp(h)+exp(t)
mat <- data.frame(age=rep(age,3),
                  p=c(1/D,exp(h)/D,exp(t)/D),
                  diagnosis=factor(rep(c("Ischemic","Hemorrhagic","TIA"),each=length(age)),
                    levels=c("TIA","Hemorrhagic","Ischemic")))
p <- ggplot(mat,aes(age,p,fill=diagnosis)) + geom_area(position="stack",alpha=.86) +
  scale_fill_manual(values=c("Ischemic"=C$blue,"Hemorrhagic"=C$red,"TIA"=C$purple)) +
  scale_y_continuous(limits=c(0,1),breaks=seq(0,1,.2),expand=c(0,0)) +
  labs(title="Three probabilities must add to 1 for every patient profile",
       x="Age (years), other predictors held fixed",y="Predicted category probability") + th()
export(p,"multinomial_probs")

# 5. Poisson versus NB, same mean but different variance.
k <- 0:12; mu <- 2.8; shape <- 1.3
counts <- data.frame(k=rep(k,2),
                     prob=c(dpois(k,mu),dnbinom(k,size=shape,mu=mu)),
                     family=rep(c("Poisson: variance = mean","Neg. binomial: variance > mean"),each=length(k)))
p <- ggplot(counts,aes(k,prob,fill=family)) +
  geom_col(position=position_dodge(width=.78),width=.38) +
  scale_fill_manual(values=c("Poisson: variance = mean"=C$blue,
                             "Neg. binomial: variance > mean"=C$purple)) +
  scale_x_continuous(breaks=k) +
  labs(title="Same mean, different dispersion",x="Episodes per patient",y="Probability") + th()
export(p,"poisson_vs_nb")

# 6. Ordered factor levels are not event counts.
a <- ggplot(data.frame(level=factor(c("mild","moderate","severe"),levels=c("mild","moderate","severe")),
                       p=c(.45,.35,.2)),aes(level,p,fill=level)) +
  geom_col(width=.7) + scale_fill_manual(values=c(C$blue,C$purple,C$orange)) +
  guides(fill="none") + coord_cartesian(ylim=c(0,.55)) +
  labs(title="Ordered categories → ordinal model",x=NULL,y="Proportion") + th()
b <- ggplot(data.frame(episodes=0:6,p=c(.18,.27,.21,.14,.10,.06,.04)),
            aes(factor(episodes),p)) + geom_col(fill=C$green,width=.7) +
  coord_cartesian(ylim=c(0,.32)) +
  labs(title="Integer counts → count model",x="Number of episodes",y="Proportion") + th()
export(a+b,"ordinal_vs_count",12,5.2)
message("Wrote six teaching SVGs to ", out)
