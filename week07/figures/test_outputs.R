# ============================================================
# SYNTHETIC CLINICAL DATA — STATISTICS SLIDE DECK
# ============================================================

library(ggplot2)
library(dplyr)
library(tidyr)
library(gridExtra)
library(cowplot)
library(svglite)
library(scales)
library(signs)
library(PairedData)

# ------------------------------------------------------------
# Consistent slide palette
# ------------------------------------------------------------

COL_TEXT <- "#1F2937"
COL_GRID <- "#E5E7EB"
COL_REF  <- "#DC2626"
COL_MAIN <- "#2563EB"

DISEASE_COLORS <- c(
  "Healthy" = "#2563EB",
  "Sick"    = "#DC2626"
)

HAEM_COLORS <- c(
  "Non-haemophilic" = "#64748B",
  "Haemophilic"     = "#7C3AED"
)

AGE_COLORS <- c(
  "Young"       = "#a5d6a7",
  "Middle-aged" = "#e0a96d",
  "Old"         = "#9c6644"
)

TIME_COLORS <- c(
  "Pre-treatment"  = "#64748B",
  "Post-treatment" = "#2563EB"
)


# ------------------------------------------------------------
# Slide-friendly theme
# ------------------------------------------------------------

theme_deck <- function(base_size = 17) {
  
  theme_bw(
    base_size = base_size,
    base_family = "sans"
  ) +
    theme(
      text = element_text(color = COL_TEXT),
      
      axis.title = element_text(
        face = "bold",
        size = base_size
      ),
      
      axis.text = element_text(
        size = base_size - 2,
        color = COL_TEXT
      ),
      
      legend.title = element_text(
        face = "bold",
        size = base_size - 1
      ),
      
      legend.text = element_text(
        size = base_size - 2
      ),
      
      legend.position = "bottom",
      
      panel.grid.minor = element_blank(),
      
      panel.grid.major = element_line(
        color = COL_GRID,
        linewidth = 0.4
      ),
      
      strip.background = element_rect(
        fill = "#F3F4F6",
        color = "#D1D5DB"
      ),
      
      strip.text = element_text(
        face = "bold",
        size = base_size - 1
      ),
      
      plot.margin = margin(8, 10, 8, 10)
    )
}


# ------------------------------------------------------------
# Export helper
# ------------------------------------------------------------

save_svg <- function(
    plot,
    filename,
    width = 10,
    height = 6) {
  
  ggsave(
    filename = filename,
    plot = plot,
    device = svglite::svglite,
    width = width,
    height = height,
    units = "in",
    bg = "transparent"
  )
}


# ------------------------------------------------------------
# Formatting helpers
# ------------------------------------------------------------

fmt_p <- function(p) {
  
  if (p < 0.001) {
    "p < 0.001"
  } else {
    sprintf("p = %.3f", p)
  }
}

fmt_num <- function(x, round = 2) {
  res <- sprintf("%.*f", round, x)
  gsub("-", "\u2212", res, fixed = TRUE)
}

fmt_pct <- function(x) {
  res <- sprintf("%.1f%%", 100 * x)
  gsub("-", "\u2212", res, fixed = TRUE)
}

# ------------------------------------------------------------
# Wilson CI for proportions
# ------------------------------------------------------------

wilson_ci <- function(x, n, conf.level = 0.95) {
  
  z <- qnorm(1 - (1 - conf.level) / 2)
  
  p <- x / n
  
  denom <- 1 + z^2 / n
  
  centre <- (
    p + z^2 / (2 * n)
  ) / denom
  
  half <- (
    z *
      sqrt(
        p * (1 - p) / n +
          z^2 / (4 * n^2)
      )
  ) / denom
  
  c(
    max(0, centre - half),
    min(1, centre + half)
  )
}


add_wilson_ci <- function(df) {
  
  cis <- t(
    vapply(
      seq_len(nrow(df)),
      function(i) {
        wilson_ci(
          df$count[i],
          df$total[i]
        )
      },
      numeric(2)
    )
  )
  
  df$lo <- cis[, 1]
  df$hi <- cis[, 2]
  
  df
}


# ------------------------------------------------------------
# Exact binomial CI
# ------------------------------------------------------------

add_exact_binom_ci <- function(df) {
  
  cis <- t(
    vapply(
      seq_len(nrow(df)),
      function(i) {
        binom.test(
          df$count[i],
          df$total[i]
        )$conf.int
      },
      numeric(2)
    )
  )
  
  df$lo <- cis[, 1]
  df$hi <- cis[, 2]
  
  df
}


# ------------------------------------------------------------
# Generic horizontal CI / number-line plot
# ------------------------------------------------------------

ci_numberline <- function(
    estimate,
    lower,
    upper,
    null,
    xlab,
    formatter = fmt_num,
    null_label = "Null value",
    color = COL_MAIN) {
  
  rr <- range(
    c(lower, upper, null),
    finite = TRUE
  )
  
  span <- diff(rr)
  
  if (span == 0) {
    span <- max(abs(rr), 1)
  }
  
  lim <- c(
    rr[1] - 0.18 * span,
    rr[2] + 0.18 * span
  )
  
  label <- paste0(
    "Estimate = ", formatter(estimate),
    "    95% CI: ",
    formatter(lower), " to ", formatter(upper)
  )
  
  
  ggplot() +
    
    geom_segment(
      aes(
        x = lower,
        xend = upper,
        y = 1,
        yend = 1
      ),
      linewidth = 3,
      color = color,
      lineend = "round"
    ) +
    
    geom_point(
      aes(
        x = estimate,
        y = 1
      ),
      size = 5,
      color = color
    ) +
    
    geom_segment(
      aes(
        x = null,
        xend = null,
        y = 0.84,
        yend = 1.17
      ),
      linewidth = 1.1,
      linetype = "dashed",
      color = COL_REF
    ) +
    
    annotate(
      "text",
      x = mean(lim),
      y = 1.28,
      label = label,
      fontface = "bold",
      size = 5,
      color = COL_TEXT
    ) +
    
    annotate(
      "text",
      x = null,
      y = 0.78,
      label = null_label,
      vjust = 1,
      size = 4.2,
      color = COL_REF
    ) +
    
    scale_x_continuous(
      limits = lim,
      labels = signs_format()
    ) +
    
    coord_cartesian(
      ylim = c(0.58, 1.38),
      clip = "off"
    ) +
    
    labs(
      x = xlab,
      y = NULL
    ) +
    
    theme_deck() +
    
    theme(
      axis.text.y = element_blank(),
      axis.ticks.y = element_blank(),
      panel.grid.major.y = element_blank()
    )
}


# ------------------------------------------------------------
# Text statistics panel
# ------------------------------------------------------------

stats_panel <- function(lines, text_size = 8) {
  
  y_positions <- seq(
    0.82,
    0.18,
    length.out = length(lines)
  )
  
  ggplot() +
    
    annotate(
      "text",
      x = 0,
      y = y_positions,
      label = lines,
      hjust = 0,
      vjust = 0.5,
      size = text_size,
      color = COL_TEXT
    ) +
    
    coord_cartesian(
      xlim = c(0, 1),
      ylim = c(0, 1),
      clip = "off"
    ) +
    
    theme_void()
}


# ------------------------------------------------------------
# Tables as ggplot-compatible objects
# ------------------------------------------------------------

table_theme <- ttheme_minimal(
  base_size = 16,
  
  core = list(
    fg_params = list(
      col = COL_TEXT
    ),
    bg_params = list(
      fill = "white",
      col = "#E5E7EB"
    )
  ),
  
  colhead = list(
    fg_params = list(
      col = "white",
      fontface = "bold"
    ),
    bg_params = list(
      fill = COL_TEXT,
      col = "white"
    )
  )
)


table_panel <- function(df) {
  
  g <- tableGrob(
    df,
    rows = NULL,
    theme = table_theme
  )
  
  ggdraw() +
    draw_grob(
      g,
      x = 0,
      y = 0,
      width = 1,
      height = 1
    )
}


# ------------------------------------------------------------
# Bootstrap CI for paired difference in proportions
# ------------------------------------------------------------

paired_prop_boot_ci <- function(
    pre,
    post,
    B = 5000,
    seed = 1001) {
  
  set.seed(seed)
  
  n <- length(pre)
  
  diffs <- replicate(
    B,
    {
      ii <- sample.int(
        n,
        size = n,
        replace = TRUE
      )
      
      mean(post[ii]) -
        mean(pre[ii])
    }
  )
  
  c(
    estimate = mean(post) - mean(pre),
    quantile(
      diffs,
      probs = c(0.025, 0.975),
      names = FALSE
    )
  )
}


# ============================================================
# MAIN COHORT SIMULATION
# ============================================================

set.seed(20261006)

n <- 420


# ------------------------------------------------------------
# Disease group
# ------------------------------------------------------------

disease_num <- rbinom(
  n,
  size = 1,
  prob = 0.55
)

disease <- factor(
  ifelse(
    disease_num == 1,
    "Sick",
    "Healthy"
  ),
  levels = c("Healthy", "Sick")
)


# ------------------------------------------------------------
# Age group
# ------------------------------------------------------------

age_num <- integer(n)

for (i in seq_len(n)) {
  
  if (disease_num[i] == 0) {
    
    age_num[i] <- sample(
      0:2,
      size = 1,
      prob = c(0.42, 0.38, 0.20)
    )
    
  } else {
    
    age_num[i] <- sample(
      0:2,
      size = 1,
      prob = c(0.20, 0.38, 0.42)
    )
  }
}


age_group <- factor(
  age_num,
  levels = 0:2,
  labels = c(
    "Young",
    "Middle-aged",
    "Old"
  ),
  ordered = TRUE
)


# ------------------------------------------------------------
# Haemophilia
# ------------------------------------------------------------

logit_p_haem <-
  qlogis(0.27) +
  1.25 * disease_num +
  0.18 * age_num

p_haem <- plogis(
  logit_p_haem
)

haem_num <- rbinom(
  n,
  size = 1,
  prob = p_haem
)

haemophilia <- factor(
  ifelse(
    haem_num == 1,
    "Haemophilic",
    "Non-haemophilic"
  ),
  levels = c(
    "Non-haemophilic",
    "Haemophilic"
  )
)


# ------------------------------------------------------------
# Hemoglobin
# ------------------------------------------------------------

hgb_mean <-
  146 -
  17 * disease_num -
  3.5 * age_num -
  2.0 * haem_num

hgb_sd <- ifelse(
  disease_num == 1,
  13.5,
  8.5
)

hemoglobin <- rnorm(
  n,
  mean = hgb_mean,
  sd = hgb_sd
)

hemoglobin <- round(
  pmin(
    pmax(hemoglobin, 80),
    175
  ),
  1
)


# ------------------------------------------------------------
# Final main dataset
# ------------------------------------------------------------

patients <- data.frame(
  id = seq_len(n),
  disease = disease,
  haemophilia = haemophilia,
  age_group = age_group,
  hemoglobin = hemoglobin
)


# ============================================================
# TREATMENT SUBSTUDY
#
# Old patients with disease D receive treatment T.
# ============================================================

treatment <- patients |>
  filter(
    disease == "Sick",
    age_group == "Old"
  ) |>
  transmute(
    id,
    haem_pre = haemophilia,
    hemoglobin_pre = hemoglobin
  )


# Binary outcome after treatment
#
# Haemophilic -> non-haemophilic transitions are intentionally
# more frequent than the reverse transition for teaching McNemar.

p_haem_post <- ifelse(
  treatment$haem_pre == "Haemophilic",
  0.60,
  0.08
)

haem_post_num <- rbinom(
  nrow(treatment),
  size = 1,
  prob = p_haem_post
)

treatment$haem_post <- factor(
  ifelse(
    haem_post_num == 1,
    "Haemophilic",
    "Non-haemophilic"
  ),
  levels = c(
    "Non-haemophilic",
    "Haemophilic"
  )
)


# Hemoglobin treatment effect
#
# Mean rises, while higher baseline observations improve somewhat
# less strongly. This also reduces post-treatment variance.

pre_centered <-
  treatment$hemoglobin_pre -
  mean(treatment$hemoglobin_pre)

change <-
  8 -
  0.30 * pre_centered +
  rnorm(
    nrow(treatment),
    mean = 0,
    sd = 3.5
  )

treatment$hemoglobin_post <- round(
  treatment$hemoglobin_pre + change,
  1
)

treatment$hemoglobin_change <-
  treatment$hemoglobin_post -
  treatment$hemoglobin_pre

# ============================================================
# CATEGORICAL ANALYSIS
# ============================================================


# ************************************************************
# cat_binomial.svg
#
# Exact binomial test:
# Is haemophilia prevalence in sick patients different from 0.5?
# ************************************************************

sick <- patients |>
  filter(disease == "Sick")

n_sick <- nrow(sick)

x_sick_haem <- sum(
  sick$haemophilia == "Haemophilic"
)


binom_result <- binom.test(
  x = x_sick_haem,
  n = n_sick,
  p = 0.50
)


bin_df <- sick |>
  count(
    haemophilia,
    .drop = FALSE,
    name = "count"
  ) |>
  mutate(
    total = sum(count),
    proportion = count / total
  )

bin_df <- add_exact_binom_ci(
  bin_df
)


p_bin_bar <- ggplot(
  bin_df,
  aes(
    x = haemophilia,
    y = proportion,
    fill = haemophilia
  )
) +
  
  geom_col(
    width = 0.62
  ) +
  
  geom_errorbar(
    aes(
      ymin = lo,
      ymax = hi
    ),
    width = 0.16,
    linewidth = 0.9
  ) +
  
  geom_hline(
    yintercept = 0.50,
    linetype = "dashed",
    linewidth = 1.1,
    color = COL_REF
  ) +
  
  annotate(
    "text",
    x = 1.5,
    y = 0.52,
    label = "Reference proportion = 50%",
    color = COL_REF,
    vjust = 0,
    size = 5.0
  ) +
  
  scale_fill_manual(
    values = HAEM_COLORS,
    guide = "none"
  ) +
  
  scale_y_continuous(
    labels = percent_format(accuracy = 1),
    limits = c(0, 1),
    expand = expansion(mult = c(0, 0.02))
  ) +
  
  labs(
    x = "Haemophilia status",
    y = "Proportion of sick patients"
  ) +
  
  theme_deck()


p_bin_ci <- ci_numberline(
  estimate = unname(binom_result$estimate),
  lower = binom_result$conf.int[1],
  upper = binom_result$conf.int[2],
  null = 0.50,
  xlab = "Proportion haemophilic",
  formatter = fmt_pct,
  null_label = "Reference = 50%",
  color = HAEM_COLORS["Haemophilic"]
)


p_bin_stats <- stats_panel(
  c(
    "Exact binomial test",
    paste0(
      x_sick_haem,
      " / ",
      n_sick,
      " sick patients haemophilic"
    ),
    fmt_p(binom_result$p.value)
  )
)


viz_cat_binomial <- plot_grid(
  p_bin_bar,
  
  plot_grid(
    p_bin_ci,
    p_bin_stats,
    ncol = 2,
    rel_widths = c(2.2, 1)
  ),
  
  ncol = 1,
  rel_heights = c(1.8, 1)
)


save_svg(
  viz_cat_binomial,
  "cat_binomial.svg",
  width = 10.5,
  height = 6.5
)



# ************************************************************
# cat_gof.svg
#
# Chi-squared goodness-of-fit:
# Is age-group distribution in sick patients different from
# equal thirds?
# ************************************************************

age_obs <- table(
  sick$age_group
)

gof_result <- chisq.test(
  age_obs,
  p = rep(1 / 3, 3)
)


gof_df <- sick |>
  count(
    age_group,
    .drop = FALSE,
    name = "count"
  ) |>
  mutate(
    total = sum(count),
    proportion = count / total
  )

gof_df <- add_wilson_ci(
  gof_df
)


p_gof_bar <- ggplot(
  gof_df,
  aes(
    x = age_group,
    y = proportion,
    fill = age_group
  )
) +
  
  geom_col(
    width = 0.64
  ) +
  
  geom_errorbar(
    aes(
      ymin = lo,
      ymax = hi
    ),
    width = 0.15,
    linewidth = 0.9
  ) +
  
  geom_point(
    aes(y = 1 / 3),
    shape = 21,
    size = 4.5,
    stroke = 1.2,
    fill = "white",
    color = COL_REF
  ) +
  
  scale_fill_manual(
    values = AGE_COLORS,
    guide = "none"
  ) +
  
  scale_y_continuous(
    labels = percent_format(accuracy = 1),
    limits = c(0, 0.60),
    expand = expansion(mult = c(0, 0.03))
  ) +
  
  labs(
    x = "Age group",
    y = "Proportion of sick patients"
  ) +
  
  theme_deck()


gof_table_df <- data.frame(
  `Age group` = levels(sick$age_group),
  Observed = as.integer(age_obs),
  Expected = round(
    rep(n_sick / 3, 3),
    1
  ),
  `Observed %` = sprintf(
    "%.1f",
    100 * as.integer(age_obs) / n_sick
  ),
  `Expected %` = "33.3",
  check.names = FALSE
)


p_gof_table <- table_panel(
  gof_table_df
)


p_gof_stats <- stats_panel(
  c(
    "Goodness-of-fit",
    sprintf(
      "χ2 = %.2f",
      unname(gof_result$statistic)
    ),
    sprintf(
      "df = %d",
      unname(gof_result$parameter)
    ),
    fmt_p(gof_result$p.value)
  )
)


viz_cat_gof <- plot_grid(
  p_gof_bar,
  
  plot_grid(
    p_gof_table,
    p_gof_stats,
    ncol = 2,
    rel_widths = c(2, 1)
  ),
  
  ncol = 1,
  rel_heights = c(1.8, 1)
)


save_svg(
  viz_cat_gof,
  "cat_gof.svg",
  width = 11,
  height = 6.5
)



# ************************************************************
# cat_two_groups.svg
#
# Chi-squared test of homogeneity:
# Is haemophilia prevalence different in healthy vs sick?
# ************************************************************

hom_tab <- table(
  patients$disease,
  patients$haemophilia
)

hom_result <- chisq.test(
  hom_tab,
  correct = FALSE
)


hom_df <- patients |>
  count(
    disease,
    haemophilia,
    .drop = FALSE,
    name = "count"
  ) |>
  group_by(disease) |>
  mutate(
    total = sum(count),
    proportion = count / total
  ) |>
  ungroup()

hom_df <- add_wilson_ci(
  hom_df
)


p_hom_bar <- ggplot(
  hom_df,
  aes(
    x = haemophilia,
    y = proportion,
    fill = disease
  )
) +
  
  geom_col(
    position = position_dodge(width = 0.78),
    width = 0.68
  ) +
  
  geom_errorbar(
    aes(
      ymin = lo,
      ymax = hi
    ),
    position = position_dodge(width = 0.78),
    width = 0.14,
    linewidth = 0.85
  ) +
  
  scale_fill_manual(
    values = DISEASE_COLORS
  ) +
  
  scale_y_continuous(
    labels = percent_format(accuracy = 1),
    limits = c(0, 1),
    expand = expansion(mult = c(0, 0.02))
  ) +
  
  labs(
    x = "Haemophilia status",
    y = "Proportion within\ndisease group",
    fill = "Disease status"
  ) +
  
  theme_deck()


healthy_n <- sum(
  patients$disease == "Healthy"
)

sick_n <- sum(
  patients$disease == "Sick"
)

healthy_haem <- sum(
  patients$disease == "Healthy" &
    patients$haemophilia == "Haemophilic"
)

sick_haem <- sum(
  patients$disease == "Sick" &
    patients$haemophilia == "Haemophilic"
)


prop_diff_result <- prop.test(
  x = c(
    healthy_haem,
    sick_haem
  ),
  n = c(
    healthy_n,
    sick_n
  ),
  correct = FALSE
)


prop_diff_est <-
  healthy_haem / healthy_n -
  sick_haem / sick_n


p_hom_ci <- ci_numberline(
  estimate = prop_diff_est,
  lower = prop_diff_result$conf.int[1],
  upper = prop_diff_result$conf.int[2],
  null = 0,
  xlab = "Difference in haemophilia proportions: Healthy − Sick",
  formatter = fmt_pct,
  null_label = "No difference",
  color = COL_MAIN
)


hom_table_df <- as.data.frame.matrix(
  hom_tab
)

hom_table_df <- data.frame(
  `Disease status` = rownames(hom_table_df),
  hom_table_df,
  check.names = FALSE,
  row.names = NULL
)


p_hom_table <- table_panel(
  hom_table_df
)


p_hom_stats <- stats_panel(
  c(
    paste0(
      "Homogeneity    ",
      sprintf(
        "χ2 = %.2f",
        unname(hom_result$statistic)
      )
    ),
    paste0(
      sprintf(
        "df = %d",
        unname(hom_result$parameter)
      ),
      "                ",
      fmt_p(hom_result$p.value)
    )
  )
)


viz_cat_two_groups <- plot_grid(
  p_hom_bar,
  
  plot_grid(
    p_hom_ci,
    
    plot_grid(
      p_hom_table,
      p_hom_stats,
      ncol = 1,
      rel_heights = c(1, 1)
    ),
    
    ncol = 2,
    rel_widths = c(1.6, 1)
  ),
  
  ncol = 1,
  rel_heights = c(1.65, 1)
)


save_svg(
  viz_cat_two_groups,
  "cat_two_groups.svg",
  width = 13,
  height = 6.5
)



# ************************************************************
# cat_mcnemar.svg
#
# McNemar test:
# Did binary haemophilia status change after treatment?
# ************************************************************

haem_long <- treatment |>
  select(
    id,
    haem_pre,
    haem_post
  ) |>
  pivot_longer(
    cols = c(
      haem_pre,
      haem_post
    ),
    names_to = "time",
    values_to = "haemophilia"
  ) |>
  mutate(
    time = factor(
      time,
      levels = c(
        "haem_pre",
        "haem_post"
      ),
      labels = c(
        "Pre-treatment",
        "Post-treatment"
      )
    )
  )


mc_df <- haem_long |>
  count(
    time,
    haemophilia,
    .drop = FALSE,
    name = "count"
  ) |>
  group_by(time) |>
  mutate(
    total = sum(count),
    proportion = count / total
  ) |>
  ungroup()

mc_df <- add_wilson_ci(
  mc_df
)


p_mc_bar <- ggplot(
  mc_df,
  aes(
    x = haemophilia,
    y = proportion,
    fill = time
  )
) +
  
  geom_col(
    position = position_dodge(width = 0.78),
    width = 0.68
  ) +
  
  geom_errorbar(
    aes(
      ymin = lo,
      ymax = hi
    ),
    position = position_dodge(width = 0.78),
    width = 0.14,
    linewidth = 0.85
  ) +
  
  scale_fill_manual(
    values = TIME_COLORS
  ) +
  
  scale_y_continuous(
    labels = percent_format(accuracy = 1),
    limits = c(0, 1)
  ) +
  
  labs(
    x = "Haemophilia status",
    y = "Proportion of\ntreated patients",
    fill = "Measurement"
  ) +
  
  theme_deck()


pre_num <- as.integer(
  treatment$haem_pre == "Haemophilic"
)

post_num <- as.integer(
  treatment$haem_post == "Haemophilic"
)


paired_prop_ci <- paired_prop_boot_ci(
  pre = pre_num,
  post = post_num
)


p_mc_ci <- ci_numberline(
  estimate = paired_prop_ci[1],
  lower = paired_prop_ci[2],
  upper = paired_prop_ci[3],
  null = 0,
  xlab = "Paired change in haemophilia proportion: Post − Pre",
  formatter = fmt_pct,
  null_label = "No change",
  color = COL_MAIN
)


mc_tab <- table(
  Pre = treatment$haem_pre,
  Post = treatment$haem_post
)


mc_result <- mcnemar.test(
  mc_tab,
  correct = FALSE
)


n_non_to_haem <-
  mc_tab[
    "Non-haemophilic",
    "Haemophilic"
  ]

n_haem_to_non <-
  mc_tab[
    "Haemophilic",
    "Non-haemophilic"
  ]


mc_transition_df <- data.frame(
  Transition = c(
    "Non-haemophilic → Haemophilic",
    "Haemophilic → Non-haemophilic"
  ),
  Count = c(
    n_non_to_haem,
    n_haem_to_non
  )
)


p_mc_table <- table_panel(
  mc_transition_df
)


p_mc_stats <- stats_panel(
  c(
    "McNemar test",
    sprintf(
      "Discordant pairs = %d",
      n_non_to_haem + n_haem_to_non
    ),
    sprintf(
      "χ2 = %.2f",
      unname(mc_result$statistic)
    ),
    fmt_p(mc_result$p.value)
  ),
  text_size = 6
)


viz_cat_mcnemar <- plot_grid(
  p_mc_bar,
  
  plot_grid(
    p_mc_ci,
    
    plot_grid(
      p_mc_table,
      p_mc_stats,
      ncol = 1,
      rel_heights = c(1, 1.2)
    ),
    
    ncol = 2,
    rel_widths = c(2.1, 1.25)
  ),
  
  ncol = 1,
  rel_heights = c(1.65, 1)
)


save_svg(
  viz_cat_mcnemar,
  "cat_mcnemar.svg",
  width = 12,
  height = 7
)

# ============================================================
# CONTINUOUS ANALYSIS
# ============================================================


# ************************************************************
# cont_one_mean.svg
#
# One-sample t test:
# Is mean hemoglobin in sick patients different from 130 g/L?
# ************************************************************

hgb_sick <- sick$hemoglobin

one_mean <- t.test(
  hgb_sick,
  mu = 130
)


one_mean_df <- data.frame(
  Group = "Sick",
  Hemoglobin = hgb_sick
)


p_one_mean_box <- ggplot(
  one_mean_df,
  aes(
    x = Group,
    y = Hemoglobin
  )
) +
  
  geom_boxplot(
    width = 0.42,
    fill = DISEASE_COLORS["Sick"],
    alpha = 0.65,
    outlier.shape = NA
  ) +
  
  geom_jitter(
    width = 0.10,
    alpha = 0.30,
    size = 1.7,
    color = COL_TEXT
  ) +
  
  geom_hline(
    yintercept = 130,
    color = COL_REF,
    linewidth = 1.1,
    linetype = "dashed"
  ) +
  
  annotate(
    "text",
    x = 1.18,
    y = 131,
    label = "Reference = 130 g/L",
    hjust = 0,
    color = COL_REF,
    size = 4.5
  ) +
  
  labs(
    x = NULL,
    y = "Hemoglobin (g/L)"
  ) +
  
  theme_deck()


p_one_mean_ci <- ci_numberline(
  estimate = mean(hgb_sick),
  lower = one_mean$conf.int[1],
  upper = one_mean$conf.int[2],
  null = 130,
  xlab = "Mean hemoglobin (g/L)",
  formatter = function(x) sprintf("%.1f", x),
  null_label = "Reference = 130 g/L"
)


p_one_mean_stats <- stats_panel(
  c(
    "One-sample Student's t test",
    paste0(
      "t = ", gsub("-", "\u2212", round(unname(one_mean$statistic), 2), fixed = TRUE),
      " df = ", unname(one_mean$parameter)
    ),
    fmt_p(one_mean$p.value)
  )
)


viz_cont_one_mean <- plot_grid(
  p_one_mean_box,
  
  plot_grid(
    p_one_mean_ci,
    p_one_mean_stats,
    ncol = 2,
    rel_widths = c(2, 1)
  ),
  
  ncol = 1,
  rel_heights = c(1.7, 1)
)


save_svg(
  viz_cont_one_mean,
  "cont_one_mean.svg",
  width = 10.5,
  height = 6.5
)



# ************************************************************
# cont_one_variance.svg
#
# One-sample chi-squared test for variance:
# Is SD different from 10 g/L?
# ************************************************************

reference_sd <- 10
reference_var <- reference_sd^2

n_var <- length(hgb_sick)
df_var <- n_var - 1

sample_var <- var(hgb_sick)
sample_sd <- sd(hgb_sick)

var_stat <-
  df_var *
  sample_var /
  reference_var

p_lower <- pchisq(
  var_stat,
  df = df_var
)

p_upper <- pchisq(
  var_stat,
  df = df_var,
  lower.tail = FALSE
)

var_p <- min(
  1,
  2 * min(
    p_lower,
    p_upper
  )
)

var_ratio <-
  sample_var /
  reference_var

alpha <- 0.05

var_ratio_ci <- c(
  df_var * sample_var /
    (
      qchisq(
        1 - alpha / 2,
        df_var
      ) *
        reference_var
    ),
  
  df_var * sample_var /
    (
      qchisq(
        alpha / 2,
        df_var
      ) *
        reference_var
    )
)


reference_low <-
  mean(hgb_sick) -
  reference_sd

reference_high <-
  mean(hgb_sick) +
  reference_sd


p_one_var_spread <- ggplot(
  data.frame(
    Hemoglobin = hgb_sick
  ),
  aes(x = Hemoglobin)
) +
  
  annotate(
    "rect",
    xmin = reference_low,
    xmax = reference_high,
    ymin = -Inf,
    ymax = Inf,
    fill = COL_REF,
    alpha = 0.20
  ) +
  
  geom_dotplot(
    binwidth = 1.5,
    stackratio = 1,
    dotsize = 0.65,
    fill = COL_MAIN,
    color = "white"
  ) +
  
  geom_vline(
    xintercept = mean(hgb_sick),
    linewidth = 1,
    color = COL_TEXT
  ) +
  
  labs(
    x = "Hemoglobin (g/L)",
    y = NULL,
    subtitle = paste0(
      "Shaded width = +/− reference SD of ",
      reference_sd,
      " g/L around the sample mean"
    )
  ) +
  
  theme_deck() +
  
  theme(
    axis.text.y = element_blank(),
    axis.ticks.y = element_blank(),
    panel.grid.major.y = element_blank()
  )


p_one_var_ci <- ci_numberline(
  estimate = var_ratio,
  lower = var_ratio_ci[1],
  upper = var_ratio_ci[2],
  null = 1,
  xlab = "Variance ratio: observed variance / reference variance",
  formatter = function(x) sprintf("%.2f", x),
  null_label = "Reference ratio = 1"
)


p_one_var_stats <- stats_panel(
  c(
    "One-sample χ2 variance test",
    sprintf(
      "Observed SD = %.1f g/L",
      sample_sd
    ),
    sprintf(
      "Reference SD = %.1f g/L",
      reference_sd
    ),
    sprintf(
      "χ2 = %.2f, df = %d",
      var_stat,
      df_var
    ),
    fmt_p(var_p)
  ),
  text_size = 7
)


viz_cont_one_variance <- plot_grid(
  p_one_var_spread,
  
  plot_grid(
    p_one_var_ci,
    p_one_var_stats,
    ncol = 2,
    rel_widths = c(1.9, 1)
  ),
  
  ncol = 1,
  rel_heights = c(1.65, 1)
)


save_svg(
  viz_cont_one_variance,
  "cont_one_variance.svg",
  width = 11,
  height = 6.5
)



# ************************************************************
# cont_welch.svg
#
# Welch two-sample t test:
# Healthy vs sick mean hemoglobin
# ************************************************************

hgb_healthy <- patients$hemoglobin[
  patients$disease == "Healthy"
]

hgb_sick <- patients$hemoglobin[
  patients$disease == "Sick"
]


welch_result <- t.test(
  hgb_healthy,
  hgb_sick,
  var.equal = FALSE
)


mean_diff <-
  mean(hgb_healthy) -
  mean(hgb_sick)


p_welch_box <- ggplot(
  patients,
  aes(
    x = disease,
    y = hemoglobin,
    fill = disease
  )
) +
  
  geom_boxplot(
    width = 0.55,
    alpha = 0.72,
    outlier.shape = NA
  ) +
  
  geom_jitter(
    width = 0.12,
    alpha = 0.20,
    size = 1.3
  ) +
  
  scale_fill_manual(
    values = DISEASE_COLORS,
    guide = "none"
  ) +
  
  labs(
    x = "Disease status",
    y = "Hemoglobin (g/L)"
  ) +
  
  theme_deck()


p_welch_ci <- ci_numberline(
  estimate = mean_diff,
  lower = welch_result$conf.int[1],
  upper = welch_result$conf.int[2],
  null = 0,
  xlab = "Difference in means: Healthy − Sick (g/L)",
  formatter = function(x) sprintf("%.1f", x),
  null_label = "No difference"
)


p_welch_stats <- stats_panel(
  c(
    "Welch two-sample t test",
    sprintf(
      "t = %.2f",
      unname(welch_result$statistic)
    ),
    sprintf(
      "df = %.1f",
      unname(welch_result$parameter)
    ),
    fmt_p(welch_result$p.value)
  )
)


viz_cont_welch <- plot_grid(
  p_welch_box,
  
  plot_grid(
    p_welch_ci,
    p_welch_stats,
    ncol = 2,
    rel_widths = c(2, 1)
  ),
  
  ncol = 1,
  rel_heights = c(1.7, 1)
)


save_svg(
  viz_cont_welch,
  "cont_welch.svg",
  width = 10.8,
  height = 6.5
)



# ************************************************************
# cont_f_variance.svg
#
# F test:
# Healthy vs sick hemoglobin variance
# ************************************************************

f_result <- var.test(
  hgb_healthy,
  hgb_sick
)

f_ratio <-
  var(hgb_healthy) /
  var(hgb_sick)


p_f_spread <- ggplot(
  patients,
  aes(
    x = disease,
    y = hemoglobin,
    fill = disease,
    color = disease
  )
) +
  
  geom_violin(
    width = 0.78,
    alpha = 0.25,
    linewidth = 0.9
  ) +
  
  geom_boxplot(
    width = 0.18,
    alpha = 0.75,
    color = COL_TEXT,
    outlier.shape = NA
  ) +
  
  geom_jitter(
    width = 0.10,
    alpha = 0.25,
    size = 1.2
  ) +
  
  scale_fill_manual(
    values = DISEASE_COLORS,
    guide = "none"
  ) +
  
  scale_color_manual(
    values = DISEASE_COLORS,
    guide = "none"
  ) +
  
  labs(
    x = "Disease status",
    y = "Hemoglobin (g/L)"
  ) +
  
  theme_deck()


p_f_ci <- ci_numberline(
  estimate = f_ratio,
  lower = f_result$conf.int[1],
  upper = f_result$conf.int[2],
  null = 1,
  xlab = "Variance ratio: Healthy / Sick",
  formatter = function(x) sprintf("%.2f", x),
  null_label = "Equal variances"
)


p_f_stats <- stats_panel(
  c(
    "Variance ratio F test",
    sprintf(
      "F = %.2f",
      unname(f_result$statistic)
    ),
    sprintf(
      "df = %d, %d",
      unname(f_result$parameter[1]),
      unname(f_result$parameter[2])
    ),
    fmt_p(f_result$p.value)
  )
)


viz_cont_f_variance <- plot_grid(
  p_f_spread,
  
  plot_grid(
    p_f_ci,
    p_f_stats,
    ncol = 2,
    rel_widths = c(2.1, 1)
  ),
  
  ncol = 1,
  rel_heights = c(1.7, 1)
)


save_svg(
  viz_cont_f_variance,
  "cont_f_variance.svg",
  width = 10.8,
  height = 6.5
)



# ************************************************************
# cont_paired_t.svg
#
# Paired t test:
# Mean hemoglobin change pre/post treatment
# ************************************************************

paired_t <- t.test(
  treatment$hemoglobin_post,
  treatment$hemoglobin_pre,
  paired = TRUE
)


paired_long <- treatment |>
  select(
    id,
    hemoglobin_pre,
    hemoglobin_post
  ) |>
  pivot_longer(
    cols = c(
      hemoglobin_pre,
      hemoglobin_post
    ),
    names_to = "time",
    values_to = "hemoglobin"
  ) |>
  mutate(
    time = factor(
      time,
      levels = c(
        "hemoglobin_pre",
        "hemoglobin_post"
      ),
      labels = c(
        "Pre-treatment",
        "Post-treatment"
      )
    )
  )


p_pair_traj <- ggplot(
  paired_long,
  aes(
    x = time,
    y = hemoglobin,
    group = id
  )
) +
  
  geom_line(
    alpha = 0.22,
    linewidth = 0.6,
    color = COL_TEXT
  ) +
  
  geom_point(
    aes(color = time),
    size = 2,
    alpha = 0.70
  ) +
  
  scale_color_manual(
    values = TIME_COLORS,
    guide = "none"
  ) +
  
  labs(
    x = NULL,
    y = "Hemoglobin (g/L)",
    title = "Paired trajectories"
  ) +
  
  theme_deck()


p_pair_box <- ggplot(
  paired_long,
  aes(
    x = time,
    y = hemoglobin,
    fill = time
  )
) +
  
  geom_boxplot(
    width = 0.52,
    alpha = 0.72
  ) +
  
  scale_fill_manual(
    values = TIME_COLORS,
    guide = "none"
  ) +
  
  labs(
    x = NULL,
    y = "Hemoglobin (g/L)",
    title = "Pre- and post-treatment distributions"
  ) +
  
  theme_deck()


p_pair_diff <- ggplot(
  treatment,
  aes(x = hemoglobin_change)
) +
  
  geom_histogram(
    binwidth = 2,
    fill = COL_MAIN,
    color = "white",
    alpha = 0.8
  ) +
  
  geom_vline(
    xintercept = 0,
    linetype = "dashed",
    color = COL_REF,
    linewidth = 1
  ) +
  
  labs(
    x = "Within-patient change: Post − Pre (g/L)",
    y = "Number of patients",
    title = "Distribution of paired differences"
  ) +
  
  scale_x_continuous(labels = signs_format()) +
  
  theme_deck()


p_pair_ci <- ci_numberline(
  estimate = mean(
    treatment$hemoglobin_change
  ),
  lower = paired_t$conf.int[1],
  upper = paired_t$conf.int[2],
  null = 0,
  xlab = "Mean paired change in hemoglobin (g/L)",
  formatter = function(x) sprintf("%.1f", x),
  null_label = "No mean change"
) +
  
  labs(
    subtitle = paste0(
      "Paired Student's t test: ",
      fmt_p(paired_t$p.value)
    )
  )


viz_cont_paired_t <- plot_grid(
  p_pair_traj,
  p_pair_box,
  p_pair_diff,
  p_pair_ci,
  ncol = 2,
  rel_heights = c(1, 1)
)


save_svg(
  viz_cont_paired_t,
  "cont_paired_t.svg",
  width = 12.5,
  height = 8
)



# ************************************************************
# cont_pitman_morgan.svg
#
# Pitman-Morgan test:
# Has hemoglobin variance changed pre/post treatment?
# ************************************************************


paired_hemoglobin <- paired(treatment$hemoglobin_pre, treatment$hemoglobin_post)
pm_result <- Var.test(paired_hemoglobin)


centered_pair <- treatment |>
  transmute(
    id,
    `Pre-treatment` =
      hemoglobin_pre -
      mean(hemoglobin_pre),
    
    `Post-treatment` =
      hemoglobin_post -
      mean(hemoglobin_post)
  ) |>
  pivot_longer(
    cols = -id,
    names_to = "time",
    values_to = "centered_hgb"
  ) |>
  mutate(
    time = factor(
      time,
      levels = c(
        "Pre-treatment",
        "Post-treatment"
      )
    )
  )


p_pm_spread <- ggplot(
  centered_pair,
  aes(
    x = time,
    y = centered_hgb,
    group = id
  )
) +
  
  geom_hline(
    yintercept = 0,
    color = COL_TEXT,
    linewidth = 0.7
  ) +
  
  geom_line(
    alpha = 0.20,
    linewidth = 0.55
  ) +
  
  geom_point(
    aes(color = time),
    size = 1.8,
    alpha = 0.65
  ) +
  
  scale_color_manual(
    values = TIME_COLORS,
    guide = "none"
  ) +
  
  scale_y_continuous(labels = signs_format()) +
  
  labs(
    x = NULL,
    y = "Deviation from time-specific mean (g/L)",
    title = "Paired spread around each mean"
  ) +
  
  theme_deck()


variance_df <- data.frame(
  Time = factor(
    c(
      "Pre-treatment",
      "Post-treatment"
    ),
    levels = c(
      "Pre-treatment",
      "Post-treatment"
    )
  ),
  
  Variance = c(
    var(treatment$hemoglobin_pre),
    var(treatment$hemoglobin_post)
  )
)


p_pm_variance <- ggplot(
  variance_df,
  aes(
    x = Time,
    y = Variance,
    fill = Time
  )
) +
  
  geom_col(
    width = 0.58
  ) +
  
  geom_text(
    aes(
      label = sprintf(
        "%.1f",
        Variance
      )
    ),
    vjust = -0.5,
    fontface = "bold",
    size = 5
  ) +
  
  scale_fill_manual(
    values = TIME_COLORS,
    guide = "none"
  ) +
  
  labs(
    x = NULL,
    y = expression(
      paste(
        "Sample variance ((g/L)",
        {}^2,
        ")"
      )
    ),
    title = "Variances"
  ) +
  
  scale_y_continuous(
    expand = expansion(
      mult = c(0, 0.15)
    )
  ) +
  scale_x_discrete(
    labels = c(
      "Pre-treatment" = "Pre-",
      "Post-treatment" = "Post-"
    )
  ) +
  
  theme_deck()


pm_ratio <-
  var(treatment$hemoglobin_pre) /
  var(treatment$hemoglobin_post)


p_pm_ci <- ci_numberline(
  estimate = pm_ratio,
  lower = pm_result$conf.int[1],
  upper = pm_result$conf.int[2],
  null = 1,
  xlab = "Variance ratio: Pre-treatment / Post-treatment",
  formatter = function(x) sprintf("%.2f", x),
  null_label = "Equal variances"
)


p_pm_stats <- stats_panel(
  c(
    "Pitman-Morgan test",
    sprintf(
      "Pre SD = %.1f g/L",
      sd(treatment$hemoglobin_pre)
    ),
    sprintf(
      "Post SD = %.1f g/L",
      sd(treatment$hemoglobin_post)
    ),
    sprintf(
      "Test statistic = %.2f",
      unname(pm_result$statistic)
    ),
    fmt_p(pm_result$p.value)
  ),
  text_size = 8
)


viz_cont_pm <- plot_grid(
  p_pm_spread,
  p_pm_variance,
  
  plot_grid(
    p_pm_ci,
    p_pm_stats,
    ncol = 1,
    rel_heights = c(1.3, 1)
  ),
  
  ncol = 3,
  rel_widths = c(1.5, 1, 1.6)
)


save_svg(
  viz_cont_pm,
  "cont_pitman_morgan.svg",
  width = 14,
  height = 6
)

# ============================================================
# BLAND-ALTMAN EXAMPLES
# ============================================================

BA_THRESHOLD <- 8


# ------------------------------------------------------------
# Simulate method-comparison data
# ------------------------------------------------------------

simulate_ba <- function(
    type = c(
      "good",
      "bias",
      "hetero",
      "wide"
    ),
    n = 140,
    seed = 1) {
  
  type <- match.arg(type)
  
  set.seed(seed)
  
  measurement_mean <- rnorm(
    n,
    mean = 140,
    sd = 18
  )
  
  
  if (type == "good") {
    
    difference <- rnorm(
      n,
      mean = 0,
      sd = 1.8
    )
    
    # Make the example visually exactly unbiased
    difference <-
      difference -
      mean(difference)
  }
  
  
  if (type == "bias") {
    
    difference <- rnorm(
      n,
      mean = 4,
      sd = 1.5
    )
    
    difference <-
      difference -
      mean(difference) +
      4
  }
  
  
  if (type == "hetero") {
    
    norm_mean <- scales::rescale(measurement_mean, to = c(0, 1))
    
    local_sd <- 0.2 + 4.5 * (norm_mean ^ 2.5)
    
    difference <- rnorm(
      n,
      mean = 0,
      sd = local_sd
    )
    
    difference <-
      difference -
      mean(difference)
  }
  
  
  if (type == "wide") {
    
    difference <- rnorm(
      n,
      mean = 0,
      sd = 5.2
    )
    
    difference <-
      difference -
      mean(difference)
  }
  
  
  method_A <-
    measurement_mean -
    difference / 2
  
  method_B <-
    measurement_mean +
    difference / 2
  
  
  data.frame(
    method_A = method_A,
    method_B = method_B,
    average = (
      method_A +
        method_B
    ) / 2,
    difference = (
      method_B -
        method_A
    )
  )
}


# ------------------------------------------------------------
# Bland-Altman plotting helper
# ------------------------------------------------------------

make_ba_plot <- function(
    dat,
    title,
    threshold = BA_THRESHOLD) {
  
  bias <- mean(
    dat$difference
  )
  
  difference_sd <- sd(
    dat$difference
  )
  
  loa_lower <-
    bias -
    1.96 * difference_sd
  
  loa_upper <-
    bias +
    1.96 * difference_sd
  
  
  bias_test <- t.test(
    dat$difference,
    mu = 0
  )
  
  bias_ci <- bias_test$conf.int
  
  
  horizontal_lines <- data.frame(
    y = c(
      0,
      bias,
      loa_lower,
      loa_upper,
      -threshold,
      threshold
    ),
    
    type = factor(
      c(
        "Zero",
        "Bias",
        "95% limits of agreement",
        "95% limits of agreement",
        "Interchangeability threshold",
        "Interchangeability threshold"
      ),
      levels = c(
        "Zero",
        "Bias",
        "95% limits of agreement",
        "Interchangeability threshold"
      )
    )
  )
  
  ggplot(
    dat,
    aes(
      x = average,
      y = difference
    )
  ) +
    
    annotate(
      "rect",
      xmin = -Inf,
      xmax = Inf,
      ymin = bias_ci[1],
      ymax = bias_ci[2],
      fill = COL_MAIN,
      alpha = 0.12
    ) +
    
    geom_hline(
      data = horizontal_lines,
      aes(
        yintercept = y,
        color = type,
        linetype = type
      ),
      linewidth = 1
    ) +
    
    geom_point(
      size = 2.3,
      alpha = 0.55,
      color = COL_TEXT
    ) +
    
    scale_color_manual(
      values = c(
        "Zero" = "#64748B",
        "Bias" = "#2563EB",
        "95% limits of agreement" = "#7C3AED",
        "Interchangeability threshold" = "#DC2626"
      )
    ) +
    
    scale_linetype_manual(
      values = c(
        "Zero" = "dotted",
        "Bias" = "solid",
        "95% limits of agreement" = "dashed",
        "Interchangeability threshold" = "longdash"
      )
    ) +
    
    scale_x_continuous(labels = signs_format()) +
    scale_y_continuous(labels = signs_format()) +
    
    # guides(
    #   color = guide_legend(
    #     title = NULL,
    #     nrow = 2,
    #     byrow = TRUE
    #   ),
    #   linetype = "none"
    # ) +
    
    labs(
      x = "Mean of the two measurements (g/L)",
      y = "Difference of measurements (g/L)",
      title = title,
      
      # subtitle = paste0(
      #   "Bias = ", fmt_num(bias), " g/L",
      #   "    |    ",
      #   "95% limits of agreement: ", fmt_num(loa_lower), " to ", fmt_num(loa_upper), " g/L"
      # )
      subtitle = paste0(
        "<span style='color:#2563EB;'>Bias</span>: ", fmt_num(bias, 0), " g/L",
        " &nbsp;|&nbsp; ",
        "<span style='color:#7C3AED;'>95% limits of agreement</span>: ", fmt_num(loa_lower, 0), " to ", fmt_num(loa_upper, 0), " g/L",
        " &nbsp;|&nbsp; ",
        "<span style='color:#DC2626;'>a priori threshold</span>: ±", threshold, " g/L"
      )
    ) +
    
    theme_deck() +
    
    theme(
      legend.position = "none",
      plot.title = element_text(
        face = "bold",
        size = 19,
        hjust = 0.5
      ),
      plot.subtitle = ggtext::element_markdown(
        size = 14,
        hjust = 0.5
      )
    )
}


# ------------------------------------------------------------
# Example 1:
# No bias + narrow agreement
# ------------------------------------------------------------

ba_good_dat <- simulate_ba(
  type = "good",
  seed = 101
)

p_ba_good <- make_ba_plot(
  ba_good_dat,
  title = "No bias and acceptable agreement"
)

save_svg(
  p_ba_good,
  "ba_good.svg",
  width = 7.5,
  height = 5.5
)


# ------------------------------------------------------------
# Example 2:
# Systematic bias, but LoA still inside threshold
# ------------------------------------------------------------

ba_bias_dat <- simulate_ba(
  type = "bias",
  seed = 102
)

p_ba_bias <- make_ba_plot(
  ba_bias_dat,
  title = "Systematic bias, but acceptable agreement width"
)

save_svg(
  p_ba_bias,
  "ba_bias.svg",
  width = 8.5,
  height = 6
)


# ------------------------------------------------------------
# Example 3:
# Heteroscedastic / funnel-shaped differences
# ------------------------------------------------------------

ba_hetero_dat <- simulate_ba(
  type = "hetero",
  seed = 103
)

p_ba_hetero <- make_ba_plot(
  ba_hetero_dat,
  title = "Heteroscedastic agreement"
)

save_svg(
  p_ba_hetero,
  "ba_hetero.svg",
  width = 8.5,
  height = 6
)


# ------------------------------------------------------------
# Example 4:
# No bias but LoA too wide for interchangeability
# ------------------------------------------------------------

ba_wide_dat <- simulate_ba(
  type = "wide",
  seed = 104
)

p_ba_wide <- make_ba_plot(
  ba_wide_dat,
  title = "No bias, but agreement is too wide"
)

save_svg(
  p_ba_wide,
  "ba_wide.svg",
  width = 8.5,
  height = 6
)


# ============================================================
# Optional: save simulated datasets
# ============================================================

write.csv(
  patients,
  "synthetic_patients.csv",
  row.names = FALSE
)

write.csv(
  treatment,
  "synthetic_treatment_study.csv",
  row.names = FALSE
)

