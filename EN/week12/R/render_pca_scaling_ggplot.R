# Week 12 supplemental R/ggplot2 implementation of the dedicated PCA scaling slide.
# All data are synthetic. Run from the package root; requires ggplot2 and svglite.
set.seed(12012)
n <- 190
z <- rnorm(n)
d <- data.frame(
  hemoglobin = 13.5 - 0.7*z + rnorm(n, sd=0.5),
  age = 65 + 12*z + rnorm(n, sd=3),
  weight = 73 + 18*z + rnorm(n, sd=9),
  synthetic_group = factor(ifelse(z > 0.25, "B", "A"))
)
X <- as.matrix(d[, 1:3]); labels <- c("Raw variables", "Min–max normalization", "Z-score standardization")
Xs <- list(X,
           apply(X, 2, function(x) (x-min(x))/(max(x)-min(x))),
           scale(X))
comps <- lapply(seq_along(Xs), function(i) {
  pca <- prcomp(Xs[[i]], center=TRUE, scale.=FALSE)
  out <- data.frame(PC1=pca$x[,1], PC2=pca$x[,2],
                    group=d$synthetic_group, scaling=labels[i])
  out
})
long <- do.call(rbind, comps)
plt <- ggplot2::ggplot(long, ggplot2::aes(PC1, PC2, color=group)) +
  ggplot2::geom_point(size=1.45, alpha=.7) +
  ggplot2::facet_wrap(~ scaling, scales="free", nrow=1) +
  ggplot2::scale_color_manual(values=c(A="#1f6feb", B="#c65d09")) +
  ggplot2::labs(title="Same data, different scaling → different PCA",
                subtitle="Raw measurements, 0–1 min–max, and z-scores", color="Synthetic group") +
  ggplot2::theme_minimal(base_size=15) +
  ggplot2::theme(panel.grid.minor=ggplot2::element_blank(),
                 strip.text=ggplot2::element_text(face="bold"),
                 plot.title=ggplot2::element_text(face="bold"))
dir.create("week12/figures", recursive=TRUE, showWarnings=FALSE)
ggplot2::ggsave("week12/figures/pca_scaling_from_R.svg", plt,
                device=svglite::svglite, width=12.5, height=4.8)
