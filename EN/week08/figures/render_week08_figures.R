# Statistics 101 · Week 08
# Optional native R / ggplot2 SVG regeneration.
# From the course root run: source("R/render_week08_figures.R")
# Assumes this script is in EN/R/ and the slide figures are EN/week08/figures/.
# For standalone package: setwd(".../statistics-101-week08") before sourcing.

required <- c("ggplot2", "gridExtra", "svglite")
missing <- required[!vapply(required, requireNamespace, quietly = TRUE, FUN.VALUE = logical(1))]
if (length(missing)) stop("Install these packages first: ", paste(missing, collapse = ", "))
library(ggplot2)
library(gridExtra)

outdir <- "Rfigures"
if (!dir.exists(outdir)) dir.create(outdir, recursive = TRUE)
col <- list(blue="#1f6feb", orange="#c65d09", green="#18864b",
            purple="#7b4ab5", red="#c93838", navy="#101828", muted="#667085")
base_theme <- theme_bw(base_size = 16) +
  theme(panel.grid.minor=element_blank(), panel.grid.major=element_line(color="#edf1f7"),
        plot.title=element_text(face="bold", color=col$navy),
        axis.title=element_text(color=col$navy), panel.border=element_blank(),
        axis.line=element_line(color="#d9e1ea"))
svg_export <- function(plot, name, width=11, height=5.3) {
  ggplot2::ggsave(filename=file.path(outdir,name), plot=plot,
                  width=width, height=height, units="in", device=svglite::svglite, bg="white")
}
layout2 <- function(a,b, top=NULL) gridExtra::arrangeGrob(a,b,nrow=1,top=top)
layout4 <- function(a,b,c,d, top=NULL) gridExtra::arrangeGrob(a,b,c,d,nrow=2,top=top)
layout6 <- function(a,b,c,d,e,f, top=NULL) gridExtra::arrangeGrob(a,b,c,d,e,f,nrow=2,top=grid::textGrob(top,gp = grid::gpar(fontsize = 20, fontface = "bold")))
set.seed(801)

fmt_num <- function(x, round = 2) {
  res <- sprintf("%.*f", round, x)
  gsub("-", "\u2212", res, fixed = TRUE)
}

# Hook: simulated HPLC chromatogram and calibration standards
# rx <- seq(0,8,length.out=800)
# rt <- data.frame(t=rx, response=.018+.04*exp(-.5*((rx-1.5)/.2)^2)+
#    .87*exp(-.5*((rx-4.2)/.36)^2)+.05*exp(-.5*((rx-6.6)/.23)^2))
# a <- ggplot(rt,aes(t,response))+geom_line(color=col$blue,linewidth=1.5)+
#   geom_vline(xintercept=4.2,linetype=2,color=col$green)+
#   annotate("text",x=5.1,y=.7,label="API peak",colour=col$green,size=5,fontface="bold")+
#   labs(title="1  HPLC separates the API",x="Retention time (min)",y="UV response")+base_theme
# cs <- seq(0,12,length.out=9); calib <- data.frame(x=cs, y=.06+.071*cs+rnorm(length(cs),0,.025))
# b <- ggplot(calib,aes(x,y))+geom_point(size=3,color=col$blue)+
#   geom_abline(intercept=.06,slope=.071,color=col$green,linewidth=1.3)+
#   labs(title="2  Standards establish calibration",x="API (mg/L)",y="Absorbance (AU)")+base_theme
# svg_export(layout2(a,b),"hplc_hook.svg",12,4.6)

# Cell-culture scatter
# set.seed(802)
# cell <- data.frame(x=runif(62,8,25));cell$y <- .28+.031*cell$x+rnorm(nrow(cell),0,.16)
# svg_export(ggplot(cell,aes(x,y))+geom_point(color=col$blue,alpha=.75,size=2.4)+
#   geom_smooth(method="lm",se=FALSE,color=col$green,linewidth=1.3)+
#   labs(title="Cell size and growth rate",x="Cell diameter (µm)",y="Divisions per hour")+base_theme,
#   "cells_scatter.svg",9,4.7)

# Nine patterns: note that constant y has undefined Pearson correlation.
set.seed(803)
names9 <- c("Steep positive / tight","Gentle positive / tight","Positive / loose",
            "Unrelated","Constant response","Curved, symmetric",
            "Steep negative / tight","Gentle negative / tight","Negative / loose")
slopes <- c(2.4,.28,.62,0,0,NA,-2.1,-.26,-.55)
noise <- c(.12,.015,.85,1.1,0,.2,.14,.018,.85)
plots <- lapply(seq_len(9),function(i){
 x <- seq(-2.5,2.5,length.out=58)+rnorm(58,sd=.08)
 y <- if(i==5) rep(.8,length(x)) else if(i==6) .55*x^2+rnorm(length(x),sd=noise[i])
      else slopes[i]*x+rnorm(length(x),sd=noise[i])
 r <- if(sd(y)<1e-10) "undefined" else fmt_num(cor(x,y))
 ggplot(data.frame(x,y),aes(x,y))+geom_point(size=1.6,color=col$blue,alpha=.8)+
   annotate("text",x=Inf,y=-Inf,label=paste("r =",r),hjust=1.1,vjust=-.6,
            colour=col$purple,fontface="bold",size=8.6)+
   labs(title=names9[i])+base_theme+theme(axis.text=element_blank(),axis.ticks=element_blank(),
      axis.title=element_blank(),panel.grid=element_blank(),plot.title=element_text(size=12))
})
plots[[2]] <- plots[[2]] + scale_y_continuous(limits= c(-2, 2))
plots[[8]] <- plots[[8]] + scale_y_continuous(limits= c(-2, 2))
svg_export(do.call(gridExtra::arrangeGrob,c(plots,list(ncol=3))),"correlation_gallery.svg",12,10)

# Category association heatmap
# ct <- matrix(c(18,4,1,7,13,5,2,7,21),nrow=3,byrow=TRUE)
# chi2 <- chisq.test(ct, correct = FALSE)$statistic
# n <- sum(ct)
# k <- min(nrow(ct), ncol(ct))
# cramer_v <- sqrt(chi2 / (n * (k - 1)))
# cramer_v
# ord <- expand.grid(Size=c("small","medium","large"),Growth=c("slow","medium","fast"))
# ord$n <- as.vector(t(ct))
# p <- ggplot(ord,aes(Growth,Size,fill=n))+geom_tile(color="white",linewidth=1)+
#   geom_text(aes(label=n),size=6,fontface="bold")+
#   scale_fill_gradient(low="#eef4fd",high=col$blue)+
#   labs(title="Contingency table: cell size × growth",x="Growth category",y="Cell-size category")+base_theme+
#   theme(panel.grid=element_blank())
# svg_export(p,"ordinal_table.svg",7.5,5)

# Six diagnostic grids
set.seed(804)
diag_kinds <- c(good_tight="Well-behaved / strong positive",
                good_loose="Well-behaved / weak negative",
                nonnormal="Skewed errors",curvature="Unmodeled nonlinear trend",
                outliers="Outliers and influence",hetero="Heteroscedastic errors")
for(kind in names(diag_kinds)){
 n <- 55; x <- seq(.6,9.4,length.out=n)+rnorm(n,sd=.10)
 y <- switch(kind,
   good_tight=1+.95*x+rnorm(n,sd=.42),
   good_loose=7.4-.38*x+rnorm(n,sd=1.35),
   nonnormal=1+.8*x+pmin(1.7*(rexp(n)-1), 50),
   curvature=3+.18*x+.08*(x-5)^3+rnorm(n,sd=.4),
   outliers={y0 <- 1+.72*x+rnorm(n,sd=.42); y0[n]<-y0[n]+6;y0[3]<-y0[3]-4;y0},
   hetero=1+.7*x+pmax(pmin(rnorm(n,sd=.16+.14*exp(x/2)), 10), -10))
 model <- lm(y~x); f <- fitted(model); e <- resid(model); z <- rstandard(model); R2 <- summary(model)$adj.r.squared
 d <- data.frame(x,y,f,e,z,leverage=hatvalues(model),scale=sqrt(abs(z)))
 p1 <- ggplot(d, aes(x, y)) +
   geom_point(color = col$blue, alpha = .7) +
   geom_abline(intercept = coef(model)[1], slope = coef(model)[2], color = col$green) +
   labs(title = paste0("Fit (R² = ", round(R2, 3), ")"), x = "Predictor", y = "Response") +
   scale_x_continuous(labels = signs::signs_format()) +
   scale_y_continuous(labels = signs::signs_format()) +
   base_theme
 p2<-ggplot(d,aes(f,e))+geom_point(color=col$blue,alpha=.7)+
    geom_hline(yintercept=0,linetype=2,color=col$red)+
    labs(title="Residual vs fitted",x="Fitted",y="Residual")+
    scale_x_continuous(labels = signs::signs_format()) +
    scale_y_continuous(labels = signs::signs_format()) +
    base_theme
 zord<-sort(z);q<-qnorm((seq_len(n)-.5)/n)
 p3<-ggplot(data.frame(q,zord),aes(q,zord))+geom_point(color=col$blue,alpha=.7)+
    geom_abline(intercept=0,slope=1,linetype=2,color=col$green)+
    labs(title="Normal QQ",x="Theoretical quantile",y="Std residual")+
    scale_x_continuous(labels = signs::signs_format()) +
    scale_y_continuous(labels = signs::signs_format()) +
    base_theme
 header <- grid::textGrob(
   "Diagnostic checklist:",
   gp = grid::gpar(fontsize = 15, fontface = "bold", col = col$navy),
   x = 0.1, y = 0.5, just = c("left", "bottom")
 )
 body <- grid::textGrob(
   "• Curvature in residuals?\n• Non-normal error tails?\n• Unequal scatter/variance?\n• High-leverage outliers?",
   gp = grid::gpar(fontsize = 15, col = col$navy),
   x = grid::unit(20, "pt"),
   y = 1, 
   just = c("left", "top")
 )
 p4 <- gridExtra::arrangeGrob(
   header, body,
   ncol = 1,
   heights = c(1, 2)
 )
 p5<-ggplot(d,aes(f,scale))+geom_point(color=col$blue,alpha=.7)+
    labs(title="Scale–location",x="Fitted",y="sqrt(|std residual|)")+
    scale_x_continuous(labels = signs::signs_format()) +
    scale_y_continuous(labels = signs::signs_format()) +
    base_theme
 p6<-ggplot(d,aes(leverage,z))+geom_point(color=col$blue,alpha=.7)+
   geom_hline(yintercept=0,linetype=2,color=col$red)+
   labs(title="Residual vs leverage",x="Leverage",y="Std residual")+
   scale_x_continuous(labels = signs::signs_format()) +
   scale_y_continuous(labels = signs::signs_format()) +
   base_theme
 svg_export(layout6(p1,p2,p3,p4,p5,p6,top=diag_kinds[kind]),paste0("diagnostic_",kind,".svg"),12,7.0)
}

# Inter/extrapolation
set.seed(801)
x_cal <- seq(2, 10, by = 1)
y_cal <- 2.5 + 1.8 * x_cal + rnorm(length(x_cal), mean = 0, sd = 0.7)
cal_data <- data.frame(x = x_cal, y = y_cal)
fit <- lm(y ~ x, data = cal_data)
b0 <- coef(fit)[1]
b1 <- coef(fit)[2]
calc_x <- function(y_meas) (y_meas - b0) / b1
y_interp <- 11.5                  # Falls within calibration range
x_interp <- calc_x(y_interp)      # Reverse calculated x
y_extrap <- 24.5                  # Falls outside calibration range
x_extrap <- calc_x(y_extrap)      # Reverse calculated x
build_cal_plot <- function(x_new, y_new, title, mode = c("interpolation", "extrapolation")) {
  mode <- match.arg(mode)
  accent_col <- if (mode == "interpolation") col$green else col$red
  
  x_min <- min(cal_data$x)
  x_max <- max(cal_data$x)
  
  # Trend line segments
  line_in        <- data.frame(x = c(x_min, x_max), y = b0 + b1 * c(x_min, x_max))
  line_out_left  <- data.frame(x = c(0, x_min),     y = b0 + b1 * c(0, x_min))
  line_out_right <- data.frame(x = c(x_max, 15),    y = b0 + b1 * c(x_max, 15))
  
  ggplot() +
    # Highlight calibration region
    annotate("rect", xmin = x_min, xmax = x_max, ymin = -Inf, ymax = Inf,
             fill = col$muted, alpha = 0.12) +
    annotate("text", x = mean(cal_data$x), y = 25.5, label = "Calibration Range",
             color = col$muted, fontface = "italic", size = 3.8) +
    
    # 1. Solid trend line inside calibration range
    geom_line(data = line_in, aes(x, y), color = col$navy, linewidth = 0.9, linetype = "solid") +
    
    # 2. Dashed trend lines outside calibration range
    geom_line(data = line_out_left, aes(x, y), color = col$navy, linewidth = 0.9, linetype = "dashed") +
    geom_line(data = line_out_right, aes(x, y), color = col$navy, linewidth = 0.9, linetype = "dashed") +
    
    # Calibration data points
    geom_point(data = cal_data, aes(x, y), color = col$blue, size = 3, alpha = 0.8) +
    
    # Reverse-calculation projection lines (dotted)
    geom_segment(aes(x = 0, xend = x_new, y = y_new, yend = y_new),
                 linetype = "dotted", color = accent_col, linewidth = 0.8) +
    geom_segment(aes(x = x_new, xend = x_new, y = 0, yend = y_new),
                 linetype = "dotted", color = accent_col, linewidth = 0.8) +
    
    # Target point
    geom_point(aes(x = x_new, y = y_new), color = accent_col, size = 4.5) +
    
    # Value labels
    annotate("text", x = x_new + 0.4, y = 1.5, 
             label = as.expression(bquote(hat(x) == .(fmt_num(x_new)))),
             color = accent_col, fontface = "bold", hjust = 0, size = 4) +
    annotate("text", x = 0.4, y = y_new + 1.2, 
             label = as.expression(bquote(y[meas] == .(fmt_num(y_new)))),
             color = accent_col, fontface = "bold", hjust = 0, size = 4) +
    
    # Status Badge / Label
    annotate("label", x = ifelse(mode == "interpolation", 3.2, 12.8), y = 21.5,
             label = title, fill = accent_col, color = "white",
             fontface = "bold", size = 4.5, label.padding = unit(0.4, "lines")) +
    
    scale_x_continuous(breaks = seq(0, 14, 2)) +
    # Use coord_cartesian for zooming/clipping without discarding data
    coord_cartesian(xlim = c(0, 15), ylim = c(0, 27), expand = FALSE) +
    labs(
      title = NULL,
      x = "Concentration / Predictor (x)",
      y = "Measured Signal (y)"
    ) +
    base_theme
}
p_left <- build_cal_plot(x_interp, y_interp, "Interpolation", mode = "interpolation")
p_right <- build_cal_plot(x_extrap, y_extrap, "Extrapolation", mode = "extrapolation")
svg_export(p_left,"interpolation.svg",5,5)
svg_export(p_right,"extrapolation.svg",5,5)

# Four transformations; two-panel original -> transformed
set.seed(811)
for(kind in c("exponential", "power", "hyperbolic", "logarithmic")){
  x <- seq(.6, 6, length.out = 33)
  
  theory <- switch(kind,
                   exponential = exp(.3 + .48 * x),
                   power       = 1.25 * x^1.6,
                   hyperbolic  = 2.8 * x / (2.1 + x),
                   logarithmic = 1.2 + .9 * log(x)
  )
  
  y <- if(kind == "logarithmic") theory + rnorm(length(x), sd = .075)
  else theory * (1 + rnorm(length(x), sd = .032))
  
  tx <- switch(kind, power = log(x), logarithmic = log(x), hyperbolic = 1/x, x)
  ty <- switch(kind, exponential = log(y), power = log(y), hyperbolic = 1/y, y)
  
  # Equations for titles
  title_left <- switch(kind,
                       exponential = bquote("Original: " ~ y == 1.35 * e^{0.48*x}),
                       power       = bquote("Original: " ~ y == 1.25 * x^1.6),
                       hyperbolic  = bquote("Original: " ~ y == frac(2.8*x, 2.1 + x)),
                       logarithmic = bquote("Original: " ~ y == 1.2 + 0.9 * log(x))
  )
  
  title_right <- switch(kind,
                        exponential = bquote("Transformed: " ~ log(y) == 0.3 + 0.48*x),
                        power       = bquote("Transformed: " ~ log(y) == 0.223 + 1.6 * log(x)),
                        hyperbolic  = bquote("Transformed: " ~ frac(1, y) == 0.357 + 0.75 * frac(1, x)),
                        logarithmic = bquote("Transformed: " ~ y == 1.2 + 0.9 * log(x))
  )
  
  left <- ggplot(data.frame(x, y), aes(x, y)) +
    geom_point(color = col$blue, size = 2) +
    geom_line(data = data.frame(x, y = theory), colour = col$orange, linewidth = 1.2) +
    labs(title = title_left, x = "x", y = "y") +
    base_theme +
    theme(plot.title = element_text(hjust = 0.5))
  
  right <- ggplot(data.frame(tx, ty), aes(tx, ty)) +
    geom_point(color = col$blue, size = 2) +
    geom_smooth(method = "lm", se = FALSE, color = col$green, linewidth = 1.2) +
    labs(
      title = title_right,
      x = if(kind %in% c("power", "logarithmic")) "log(x)" else if(kind == "hyperbolic") "1/x" else "x",
      y = if(kind %in% c("exponential", "power")) "log(y)" else if(kind == "hyperbolic") "1/y" else "y"
    ) +
    base_theme +
    theme(plot.title = element_text(hjust = 0.5))
  
  svg_export(layout2(left, right), paste0("transform_", kind, ".svg"), 11.5, 4.7)
}

# Vertical, horizontal and orthogonal regression target different loss functions
set.seed(814)
x <- seq(0, 6, length.out = 20) + rnorm(20, sd = .35)
y <- 0.0 + 1.0 * x + rnorm(20, sd = .8)
ols <- coef(lm(y ~ x))
reverse <- coef(lm(x ~ y))
horizontal <- c(-reverse[1] / reverse[2], 1 / reverse[2])
center <- colMeans(cbind(x, y))
ee <- eigen(cov(cbind(x, y)))$vectors[, 1]
orth <- c(center[2] - ee[2] / ee[1] * center[1], ee[2] / ee[1])
fits <- list(ols, horizontal, orth)
labs <- c("Vertical: regress y on x", "Horizontal: regress x on y", "Orthogonal: symmetric TLS")
cols <- c(col$green, col$purple, col$orange)
regPlots <- lapply(1:3, function(i) {
  a <- fits[[i]][1]
  b <- fits[[i]][2]
  
  df <- data.frame(x = x, y = y)
  if (i == 1) {
    df$xend <- df$x
    df$yend <- a + b * df$x
  } else if (i == 2) {
    df$xend <- (df$y - a) / b
    df$yend <- df$y
  } else if (i == 3) {
    df$xend <- (df$x + b * (df$y - a)) / (1 + b^2)
    df$yend <- a + b * df$xend
  }
  p <- ggplot(df, aes(x, y)) +
    geom_segment(aes(xend = xend, yend = yend), 
                 color = col$red, alpha = 0.4, linewidth = 0.6)
  for (j in setdiff(1:3, i)) {
    p <- p + geom_abline(intercept = fits[[j]][1], slope = fits[[j]][2], 
                         color = cols[j], linetype = "dashed", alpha = 0.35, linewidth = 0.8)
  }
  p + 
    geom_abline(intercept = a, slope = b, color = cols[i], linewidth = 1.2) +
    geom_point(color = col$blue, alpha = 0.85, size = 2.5) +
    coord_fixed(ratio = 1, xlim = c(-.4, 6.8), ylim = c(-1, 9), expand = FALSE) +
    labs(title = labs[i], x = "x", y = "y") +
    base_theme +
    theme(plot.title = element_text(hjust = 0.5),
          plot.margin = margin(0, 2, 0, 2, unit = "pt"))
})
svg_export(
  do.call(gridExtra::arrangeGrob, c(regPlots, list(ncol = 3, padding = grid::unit(0, "line")))), 
  "residual_directions.svg", 13, 4.8
)

# Multiple regression and pairs plot
# set.seed(815); n<-85
# height<-rnorm(n,171,9);weight<-.85*(height-171)+73+rnorm(n,0,7)
# sbp<-118+.45*(weight-73)+.22*(height-171)+rnorm(n,0,7)
# d<-data.frame(height,weight,sbp)
# # 2D slice visualization of a fitted plane: color encodes height
# pa<-ggplot(d,aes(weight,sbp,colour=height))+geom_point(size=2.2)+
#   scale_color_gradient(low=col$blue,high=col$orange)+
#   geom_smooth(aes(group=1),method="lm",se=FALSE,colour=col$green,linewidth=1.3)+
#   labs(title="SBP from two predictors",x="Weight (kg)",y="SBP (mmHg)")+base_theme
# pb<-ggplot(d,aes(height,weight))+geom_point(colour=col$blue,alpha=.75,size=2)+
#   geom_smooth(method="lm",se=FALSE,colour=col$green)+
#   labs(title="Predictors are correlated",x="Height (cm)",y="Weight (kg)")+base_theme
# svg_export(layout2(pa,pb),"multiple_regression.svg",11.5,4.7)
# # Base graphics pairs is appropriate for this straightforward diagnostic matrix, still exported as SVG.
# svglite::svglite(file.path(outdir,"pairs_plot.svg"),width=8,height=8)
# pairs(d,col=grDevices::adjustcolor(col$blue,.55),pch=19,
#       main="Predictor/response pairs: shared variation")
# grDevices::dev.off()

# Factorial concentration × wavelength × solvent
set.seed(816)
for(kind in c("additive", "wavelength_interaction", "full_interaction")){
  combos <- expand.grid(conc = seq(0, 10, length.out = 12), 
                        wl = factor(c(250, 280, 320)), 
                        solvent = c("MeOH", "Water"))
  j  <- as.integer(combos$wl) - 1
  si <- as.numeric(combos$solvent == "Water")
  ints   <- .07 + .055 * si + .08 * j
  slopes <- if(kind == "additive") rep(.065, nrow(combos)) else c(.046, .094, .071)[j + 1]
  if(kind == "full_interaction") slopes <- slopes + si * c(.025, -.02, .03)[j + 1]
  combos$mu  <- ints + slopes * combos$conc
  combos$abs <- combos$mu + rnorm(nrow(combos), 0, .024)
  sub_eq <- switch(kind,
                   additive = as.expression(bquote(
                     Abs == italic("\u03B2")[0] + italic("\u03B2")[1]*italic(c) + italic("\u03B2")[2]*italic(I)[water] +
                       italic("\u03B2")[3]*italic(I)[280] + italic("\u03B2")[4]*italic(I)[320]
                   )),
                   wavelength_interaction = as.expression(bquote(
                     Abs == italic("\u03B2")[0] + italic("\u03B2")[1]*italic(c) + italic("\u03B2")[2]*italic(I)[water] +
                       italic("\u03B2")[3]*italic(I)[280] + italic("\u03B2")[4]*italic(I)[320] +
                       italic("\u03B2")[5]*italic(c)*italic(I)[280] + italic("\u03B2")[6]*italic(c)*italic(I)[320]
                   )),
                   full_interaction = ""
  )
  p <- ggplot(combos, aes(conc, abs, colour = wl, group = wl)) +
    geom_point(alpha = .65, size = 1.8) +
    geom_line(aes(y = mu), linewidth = 1.1) +
    facet_wrap(~solvent, nrow = 1) +
    scale_color_manual(values = c(col$blue, col$green, col$purple)) +
    labs(
      title = switch(kind, 
                     additive = "Additive model: parallel slopes",
                     wavelength_interaction = "Concentration × wavelength: slopes differ with wavelength",
                     full_interaction = "Full interaction mode: wavelength dependence differs by solvent"
      ),
      subtitle = sub_eq,
      x = "Concentration (mg/L)", 
      y = "Absorbance (AU)", 
      colour = "λ (nm)"
    ) +
    base_theme +
    theme(
      strip.background = element_blank(),
      strip.text = element_text(face = "bold", color = col$navy, size = 13),
      plot.title = element_text(hjust = 0.5),
      plot.subtitle = element_text(hjust = 0.5)
    )
  
  svg_export(p, paste0("factor_", kind, ".svg"), 11.5, 5)
}

lam <- seq(210, 360, length.out = 350)
gband <- function(x, pos, amp, width) amp * exp(-0.5 * ((x - pos) / width)^2)
abs_meoh <- 0.04 + 
  0.015 * (360 / lam)^3.5 +          # Rayleigh scattering drift
  gband(lam, 215, 1.15,  9) +         # High-energy / E-band tail
  gband(lam, 268, 0.78, 16) +         # Primary pi -> pi* band
  gband(lam, 276, 0.38,  7) +         # Vibronic shoulder (resolved in MeOH)
  gband(lam, 312, 0.42, 15)          # Secondary n -> pi* band
abs_water <- 0.05 + 
  0.020 * (360 / lam)^3.5 +          # Baseline drift
  gband(lam, 218, 1.30, 11) +         # E-band shift + hyperchromism
  gband(lam, 274, 0.88, 22) +         # Red-shifted pi -> pi* (merged shoulder)
  gband(lam, 306, 0.32, 18)          # Blue-shifted n -> pi* (H-bonding stabilization)
spec <- data.frame(
  wavelength = rep(lam, 2),
  solvent = factor(rep(c("MeOH", "Water"), each = length(lam)), levels = c("MeOH", "Water")),
  absorbance = c(abs_meoh, abs_water)
)
p<-ggplot(spec,aes(wavelength,absorbance,colour=solvent))+geom_line(linewidth=1.4)+
 scale_colour_manual(values=c(col$blue,col$orange))+
 labs(title="Synthetic spectra: solvent affects spectral shape",x="Wavelength (nm)",y="Absorbance (AU)")+base_theme
svg_export(p,"spectra.svg",9,4.6)

# Cubic response plus hormone factor shift
# set.seed(817)
# size<-seq(1,5,length.out=50)
# cc<-expand.grid(size=size,hormone=c("No hormone","Hormone present"))
# cc$mu<-.06+.033*cc$size^3+.55*as.numeric(cc$hormone=="Hormone present")
# cc$growth<-cc$mu+rnorm(nrow(cc),sd=.25)
# p<-ggplot(cc,aes(size,growth,colour=hormone,group=hormone))+
#  geom_point(alpha=.65,size=1.8)+geom_line(aes(y=mu),linewidth=1.2)+
#  scale_colour_manual(values=c(col$blue,col$orange))+
#  labs(title="Polynomial size response + categorical hormone effect",
#       x="Cell size (arbitrary units)",y="Growth rate (divisions/h)")+base_theme
# svg_export(p,"cubic_hormone.svg",9,4.8)

# Simple sigmoid titration model
# set.seed(818)
# V<-seq(1,13,length.out=40)
# E<-35+170/(1+exp(-(V-7.1)/.7))+rnorm(length(V),sd=4)
# xx<-seq(1,13,length.out=400)
# p<-ggplot(data.frame(V,E),aes(V,E))+geom_point(colour=col$blue,alpha=.76,size=2)+
#  geom_line(data=data.frame(V=xx,E=35+170/(1+exp(-(xx-7.1)/.7))),colour=col$green,linewidth=1.3)+
#  geom_vline(xintercept=7.1,linetype=2,colour=col$purple)+
#  labs(title="Illustrative potentiometric sigmoid",x="Titrant volume (mL)",y="Potential (mV)")+base_theme
# svg_export(p,"titration.svg",9,4.8)

# R2 decomposition figure
set.seed(801)
x <- seq(1, 10, length.out = 16)
y <- 2.2 + 1.15 * x + rnorm(length(x), mean = 0, sd = 1.6)
df <- data.frame(x = x, y = y)
fit <- lm(y ~ x, data = df)
df$y_hat <- predict(fit)
y_bar <- mean(df$y)
rss <- sum((df$y - df$y_hat)^2)
tss <- sum((df$y - y_bar)^2)
r2  <- 1 - (rss / tss)

# Horizontal offset for visual separation of segment pairs
dx <- 0.03

p_r2 <- ggplot(df, aes(x, y)) +
  # TSS: Total deviation from mean y (Green, offset left)
  geom_segment(aes(x = x - dx, xend = x - dx, y = y, yend = y_bar),
               color = col$green, alpha = 0.55, linewidth = 1.2) +
  
  # RSS: Residual deviation from fitted line (Red, offset right)
  geom_segment(aes(x = x + dx, xend = x + dx, y = y, yend = y_hat),
               color = col$red, alpha = 0.55, linewidth = 1.2) +
  
  # Mean response line y_bar (Dotted Navy)
  geom_hline(yintercept = y_bar, linetype = "dotted", color = col$navy, linewidth = 0.9) +
  
  # Fitted OLS regression line (Solid Blue)
  geom_line(aes(y = y_hat), color = col$blue, linewidth = 1.1) +
  
  # Data points
  geom_point(color = col$navy, size = 3) +
  
  # Mean line label
  annotate("text", x = 0.7, y = y_bar + 0.45, 
           label = as.expression(bquote(bar(y) == .(fmt_num(y_bar)))),
           color = col$navy, fontface = "bold", hjust = 0, size = 4.8) +
  
  # Formulas and Color Keys
  annotate("label", x = 1.0, y = 13.8, 
           label = as.expression(bquote(
             italic(R)^2 == 1 - frac(RSS, TSS) ~ "=" ~ frac(ESS, TSS)
           )),
           fill = "#f8f9fa", color = col$navy, fontface = "bold", size = 6.2, 
           hjust = 0, label.padding = unit(0.5, "lines")) +
  
  annotate("text", x = 6.0, y = 4.6, 
           label = as.expression(bquote(TSS == sum((y - bar(y))^2) ~ bold("(Total Deviations)"))),
           color = col$green, hjust = 0, size = 4.8) +
  
  annotate("text", x = 6.0, y = 3.2, 
           label = as.expression(bquote(RSS == sum((y - hat(y))^2) ~ bold("(Residual Errors)"))),
           color = col$red, hjust = 0, size = 4.8) +
  
  annotate("text", x = 6.0, y = 1.8, 
           label = as.expression(bquote(ESS == TSS - RSS ~ bold("(Explained variance)"))),
           color = col$purple, hjust = 0, size = 4.8) +
  
  coord_cartesian(xlim = c(0.5, 10.5), ylim = c(0.5, 15.5), expand = FALSE) +
  labs(
    title = "Partitioning Variance",
    x = "Predictor (x)",
    y = "Response (y)"
  ) +
  base_theme +
  theme(plot.title = element_text(hjust = 0.5))

# Save output
svg_export(p_r2, "r_squared_decomposition.svg", 8.5, 5.2)

message("Saved 23 conceptual SVG figures to ",outdir)
