# ============================================================
# Synthetic clinical data + SVG visualizations for RevealJS
# ============================================================
#
# Required packages:
# install.packages(c(
#   "ggplot2", "dplyr", "gridExtra",
#   "patchwork", "svglite", "scales"
# ))
#
# Output: 15 SVG files in ./figures/
# ============================================================

# ------------------------------------------------------------
# 1. Load libraries
# ------------------------------------------------------------

library(ggplot2)
library(dplyr)
library(gridExtra)
library(patchwork)
library(svglite)
library(scales)
library(ggExtra)

# ------------------------------------------------------------
# 2. Shared visual design
# ------------------------------------------------------------

COL_TEXT  <- "#1F2937"
COL_GRID  <- "#E5E7EB"

COL_CONT  <- "#2563EB"

SEX_COLORS <- c(
  "Female" = "#2563EB",
  "Male"   = "#DC2626"
)

STAGE_COLORS <- c(
  "Stage 1" = "#0F766E",
  "Stage 2" = "#B45309",
  "Stage 3" = "#7C3AED"
)

STAGE_SHAPES <- c(
  "Stage 1" = 16,
  "Stage 2" = 17,
  "Stage 3" = 15
)


theme_slide <- function(base_size = 17) {
  theme_minimal(
    base_size = base_size,
    base_family = "sans"
  ) +
    theme(
      text = element_text(color = COL_TEXT),
      
      axis.title = element_text(
        size = base_size,
        face = "bold",
        color = COL_TEXT
      ),
      
      axis.text = element_text(
        size = base_size - 2,
        color = COL_TEXT
      ),
      
      legend.title = element_text(
        size = base_size - 1,
        face = "bold"
      ),
      
      legend.text = element_text(
        size = base_size - 2
      ),
      
      legend.position = "bottom",
      
      strip.text = element_text(
        size = base_size - 1,
        face = "bold",
        color = COL_TEXT
      ),
      
      strip.background = element_rect(
        fill = "#F3F4F6",
        color = NA
      ),
      
      panel.grid.minor = element_blank(),
      
      panel.grid.major.x = element_blank(),
      
      panel.grid.major.y = element_line(
        color = COL_GRID,
        linewidth = 0.45
      ),
      
      plot.margin = margin(10, 12, 10, 10)
    )
}


theme_scatter <- function(base_size = 17) {
  theme_slide(base_size) +
    theme(
      panel.grid.major.x = element_line(
        color = COL_GRID,
        linewidth = 0.45
      )
    )
}


# ------------------------------------------------------------
# 3. Generate synthetic data
# ------------------------------------------------------------

set.seed(20260929)

n <- 180


# Sex
sex <- sample(
  c("Female", "Male"),
  size = n,
  replace = TRUE,
  prob = c(0.53, 0.47)
)

sex <- factor(
  sex,
  levels = c("Female", "Male")
)


# Disease stage
#
# A small sex-stage association is intentionally included so
# that the contingency table and stacked bar plot are not flat.

stage_num <- integer(n)

stage_num[sex == "Female"] <- sample(
  1:3,
  size = sum(sex == "Female"),
  replace = TRUE,
  prob = c(0.50, 0.34, 0.16)
)

stage_num[sex == "Male"] <- sample(
  1:3,
  size = sum(sex == "Male"),
  replace = TRUE,
  prob = c(0.38, 0.38, 0.24)
)

stage <- factor(
  stage_num,
  levels = 1:3,
  labels = c("Stage 1", "Stage 2", "Stage 3"),
  ordered = TRUE
)


# Systolic blood pressure
#
# Slightly higher on average in men and progressively higher
# across disease stages.

bp_mean <-
  116 +
  ifelse(sex == "Male", 5, 0) +
  c(0, 8, 16)[stage_num]

bp <- round(
  rnorm(
    n,
    mean = bp_mean,
    sd = 10.5
  )
)

# Avoid implausible extreme simulated values
bp <- pmin(pmax(bp, 88), 185)


# Body temperature
#
# Temperature rises with disease stage and contains a small
# within-stage relationship with systolic BP.

temp_mean <-
  36.65 +
  c(0, 0.30, 0.80)[stage_num] +
  ifelse(sex == "Female", 0.06, 0) +
  0.006 * (bp - bp_mean)

temp <- round(
  rnorm(
    n,
    mean = temp_mean,
    sd = 0.26
  ),
  digits = 1
)

temp <- pmin(pmax(temp, 35.8), 39.6)


dat <- data.frame(
  id = seq_len(n),
  sex = sex,
  stage = stage,
  bp = bp,
  temp = temp
)


# Inspect if desired
summary(dat)


# ------------------------------------------------------------
# 4. Helper functions
# ------------------------------------------------------------

save_svg <- function(plot, filename, width = 8, height = 5) {
  
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


make_frequency_table <- function(x, variable_name) {
  
  tab <- table(x)
  
  out <- data.frame(
    Category = names(tab),
    Frequency = as.integer(tab),
    Percent = percent(
      as.integer(tab) / sum(tab),
      accuracy = 1
    )
  )
  
  names(out)[1] <- variable_name
  
  out
}


table_theme <- ttheme_minimal(
  base_size = 15,
  
  core = list(
    fg_params = list(
      col = COL_TEXT,
      hjust = 0.5,
      x = 0.5
    ),
    
    bg_params = list(
      fill = "white",
      col = NA
    )
  ),
  
  colhead = list(
    fg_params = list(
      col = "white",
      fontface = "bold",
      hjust = 0.5,
      x = 0.5
    ),
    
    bg_params = list(
      fill = COL_TEXT,
      col = NA
    )
  )
)


make_table_grob <- function(x, variable_name) {
  
  tab <- make_frequency_table(
    x,
    variable_name
  )
  
  tableGrob(
    tab,
    rows = NULL,
    theme = table_theme
  )
}


# Histogram with horizontal boxplot below it
make_hist_box <- function(
    data,
    variable,
    x_label,
    binwidth,
    fill = COL_CONT) {
  
  x <- data[[variable]]
  
  lower <- floor(min(x) / binwidth) * binwidth
  upper <- ceiling(max(x) / binwidth) * binwidth
  
  axis_breaks <- pretty(
    c(lower, upper),
    n = 6
  )
  
  
  p_hist <- ggplot(
    data,
    aes(x = .data[[variable]])
  ) +
    geom_histogram(
      binwidth = binwidth,
      boundary = lower,
      closed = "left",
      fill = fill,
      color = "white",
      linewidth = 0.5
    ) +
    scale_x_continuous(
      limits = c(lower, upper),
      breaks = axis_breaks,
      expand = expansion(mult = c(0.01, 0.01))
    ) +
    labs(
      x = NULL,
      y = "Number of participants"
    ) +
    theme_slide() +
    theme(
      axis.text.x = element_blank(),
      axis.ticks.x = element_blank(),
      plot.margin = margin(8, 10, 1, 10)
    )
  
  
  p_box <- ggplot(
    data,
    aes(
      x = .data[[variable]],
      y = factor(1)
    )
  ) +
    geom_boxplot(
      orientation = "y",
      width = 0.52,
      fill = fill,
      alpha = 0.35,
      color = COL_TEXT,
      linewidth = 0.8,
      outlier.shape = 21,
      outlier.size = 2.4,
      outlier.stroke = 0.6,
      outlier.fill = fill,
      outlier.color = COL_TEXT
    ) +
    scale_x_continuous(
      limits = c(lower, upper),
      breaks = axis_breaks,
      expand = expansion(mult = c(0.01, 0.01))
    ) +
    labs(
      x = x_label,
      y = NULL
    ) +
    theme_slide() +
    theme(
      axis.text.y = element_blank(),
      axis.ticks.y = element_blank(),
      panel.grid = element_blank(),
      plot.margin = margin(0, 10, 8, 10)
    )
  
  
  p_hist / p_box +
    plot_layout(
      heights = c(3.1, 1)
    )
}

add_plain_marginals <- function(p) {
  ggExtra::ggMarginal(
    p,
    type = "density",
    margins = "both",
    size = 5,
    colour = COL_CONT,
    fill = COL_CONT,
    alpha = 0.22
  )
}


add_grouped_marginals <- function(p) {
  ggExtra::ggMarginal(
    p,
    type = "density",
    margins = "both",
    size = 5,
    groupColour = TRUE,
    groupFill = TRUE,
    alpha = 0.18
  )
}


# More reliable than ggsave() for ggExtraPlot objects
save_marginal_svg <- function(
    plot,
    filename,
    width = 8,
    height = 6) {
  
  svglite::svglite(
    filename,
    width = width,
    height = height,
    bg = "transparent"
  )
  
  print(plot)
  dev.off()
}


make_mean_heatmap <- function(
    data,
    variable,
    legend_title,
    digits = 1) {
  
  heat_dat <- data |>
    group_by(sex, stage) |>
    summarise(
      mean_value = mean(.data[[variable]]),
      .groups = "drop"
    ) |>
    mutate(
      label = format(
        round(mean_value, digits),
        nsmall = digits
      ),
      light_text = mean_value > median(mean_value)
    )
  
  ggplot(
    heat_dat,
    aes(
      x = sex,
      y = stage,
      fill = mean_value
    )
  ) +
    geom_tile(
      color = "white",
      linewidth = 1.5
    ) +
    geom_text(
      aes(
        label = label,
        color = light_text
      ),
      size = 5.2,
      fontface = "bold"
    ) +
    scale_color_manual(
      values = c(
        "FALSE" = COL_TEXT,
        "TRUE" = "white"
      ),
      guide = "none"
    ) +
    scale_fill_gradient(
      low = "#DBEAFE",
      high = "#1D4ED8"
    ) +
    guides(
      fill = guide_colorbar(
        direction = "horizontal",
        title.position = "top"
      )
    ) +
    labs(
      x = "Sex",
      y = "Disease stage",
      fill = legend_title
    ) +
    theme_slide(base_size = 15) +
    theme(
      panel.grid = element_blank(),
      legend.position = "bottom",
      legend.key.width = grid::unit(2.6, "cm"),
      axis.text.x = element_text(size = 13),
      axis.text.y = element_text(size = 13)
    )
}

# ------------------------------------------------------------
# 5. SEX: frequency table + frequency bar plot
# ------------------------------------------------------------

sex_table <- make_table_grob(
  dat$sex,
  "Sex"
)


p_sex <- ggplot(
  dat,
  aes(
    x = sex,
    fill = sex
  )
) +
  geom_bar(
    width = 0.68,
    color = "white",
    linewidth = 0.6
  ) +
  geom_text(
    stat = "count",
    aes(label = after_stat(count)),
    vjust = -0.45,
    size = 5.2,
    fontface = "bold",
    color = COL_TEXT
  ) +
  scale_fill_manual(
    values = SEX_COLORS,
    guide = "none"
  ) +
  scale_y_continuous(
    expand = expansion(
      mult = c(0, 0.13)
    )
  ) +
  labs(
    x = "Sex",
    y = "Number of participants"
  ) +
  theme_slide()


viz_sex <- arrangeGrob(
  sex_table,
  p_sex,
  ncol = 2,
  widths = c(1.05, 1.55)
)


save_svg(
  viz_sex,
  "viz_sex.svg",
  width = 9.5,
  height = 4.8
)


# ------------------------------------------------------------
# 6. DISEASE STAGE: frequency table + frequency bar plot
# ------------------------------------------------------------

stage_table <- make_table_grob(
  dat$stage,
  "Disease stage"
)


p_stage <- ggplot(
  dat,
  aes(
    x = stage,
    fill = stage
  )
) +
  geom_bar(
    width = 0.68,
    color = "white",
    linewidth = 0.6
  ) +
  geom_text(
    stat = "count",
    aes(label = after_stat(count)),
    vjust = -0.45,
    size = 5.2,
    fontface = "bold",
    color = COL_TEXT
  ) +
  scale_fill_manual(
    values = STAGE_COLORS,
    guide = "none"
  ) +
  scale_y_continuous(
    expand = expansion(
      mult = c(0, 0.13)
    )
  ) +
  labs(
    x = "Disease stage",
    y = "Number of participants"
  ) +
  theme_slide()


viz_stage <- arrangeGrob(
  stage_table,
  p_stage,
  ncol = 2,
  widths = c(1.05, 1.55)
)


save_svg(
  viz_stage,
  "viz_stage.svg",
  width = 9.5,
  height = 4.8
)


# ------------------------------------------------------------
# 7. SYSTOLIC BP: histogram + boxplot
# ------------------------------------------------------------

viz_bp <- make_hist_box(
  data = dat,
  variable = "bp",
  x_label = "Systolic blood pressure (mmHg)",
  binwidth = 5
)


save_svg(
  viz_bp,
  "viz_bp.svg",
  width = 8.4,
  height = 5.6
)


# ------------------------------------------------------------
# 8. TEMPERATURE: histogram + boxplot
# ------------------------------------------------------------

viz_temp <- make_hist_box(
  data = dat,
  variable = "temp",
  x_label = "Body temperature (°C)",
  binwidth = 0.25
)


save_svg(
  viz_temp,
  "viz_temp.svg",
  width = 8.4,
  height = 5.6
)


# ------------------------------------------------------------
# 9. SEX x STAGE: contingency table + stacked bar plot
# ------------------------------------------------------------

ct <- addmargins(
  table(
    dat$sex,
    dat$stage
  )
)

ct_df <- as.data.frame.matrix(ct)

ct_df <- cbind(
  Sex = rownames(ct_df),
  ct_df
)

rownames(ct_df) <- NULL

ct_df$Sex[ct_df$Sex == "Sum"] <- "Total"

names(ct_df)[
  names(ct_df) == "Sum"
] <- "Total"


sex_stage_table <- tableGrob(
  ct_df,
  rows = NULL,
  theme = table_theme
)


sex_stage_counts <- dat |>
  count(
    sex,
    stage,
    name = "Frequency"
  )


p_sex_stage <- ggplot(
  sex_stage_counts,
  aes(
    x = sex,
    y = Frequency,
    fill = stage
  )
) +
  geom_col(
    width = 0.68,
    color = "white",
    linewidth = 0.6
  ) +
  geom_text(
    aes(label = Frequency),
    position = position_stack(vjust = 0.5),
    color = "white",
    fontface = "bold",
    size = 4.5
  ) +
  scale_fill_manual(
    values = STAGE_COLORS,
    labels = c("1", "2", "3")
  ) +
  labs(
    x = "Sex",
    y = "Number of participants",
    fill = "Disease stage"
  ) +
  theme_slide()


viz_sex_stage <- arrangeGrob(
  sex_stage_table,
  p_sex_stage,
  ncol = 2,
  widths = c(1.25, 1.55)
)


save_svg(
  viz_sex_stage,
  "viz_sex_stage.svg",
  width = 10,
  height = 5
)


# ------------------------------------------------------------
# 10. BP x TEMPERATURE: scatter plot
# ------------------------------------------------------------

p_bp_temp <- ggplot(
  dat,
  aes(
    x = bp,
    y = temp
  )
) +
  geom_point(
    size = 2.8,
    alpha = 0.72,
    color = COL_CONT
  ) +
  labs(
    x = "Systolic blood pressure (mmHg)",
    y = "Body temperature (°C)"
  ) +
  theme_scatter()

viz_bp_temp <- add_plain_marginals(
  p_bp_temp
)

save_marginal_svg(
  viz_bp_temp,
  "viz_bp_temp.svg",
  width = 8.2,
  height = 6.0
)

# ------------------------------------------------------------
# 11. SEX x BP: boxplot
# ------------------------------------------------------------

p_sex_bp <- ggplot(
  dat,
  aes(
    x = sex,
    y = bp,
    fill = sex
  )
) +
  geom_boxplot(
    width = 0.58,
    linewidth = 0.8,
    alpha = 0.85,
    outlier.size = 2.3
  ) +
  scale_fill_manual(
    values = SEX_COLORS,
    guide = "none"
  ) +
  labs(
    x = "Sex",
    y = "Systolic blood pressure (mmHg)"
  ) +
  theme_slide()


save_svg(
  p_sex_bp,
  "viz_sex_bp.svg",
  width = 7.2,
  height = 5.2
)


# ------------------------------------------------------------
# 12. SEX x TEMPERATURE: boxplot
# ------------------------------------------------------------

p_sex_temp <- ggplot(
  dat,
  aes(
    x = sex,
    y = temp,
    fill = sex
  )
) +
  geom_boxplot(
    width = 0.58,
    linewidth = 0.8,
    alpha = 0.85,
    outlier.size = 2.3
  ) +
  scale_fill_manual(
    values = SEX_COLORS,
    guide = "none"
  ) +
  labs(
    x = "Sex",
    y = "Body temperature (°C)"
  ) +
  theme_slide()


save_svg(
  p_sex_temp,
  "viz_sex_temp.svg",
  width = 7.2,
  height = 5.2
)


# ------------------------------------------------------------
# 13. STAGE x BP: boxplot
# ------------------------------------------------------------

p_stage_bp <- ggplot(
  dat,
  aes(
    x = stage,
    y = bp,
    fill = stage
  )
) +
  geom_boxplot(
    width = 0.58,
    linewidth = 0.8,
    alpha = 0.85,
    outlier.size = 2.3
  ) +
  scale_fill_manual(
    values = STAGE_COLORS,
    guide = "none"
  ) +
  labs(
    x = "Disease stage",
    y = "Systolic blood pressure (mmHg)"
  ) +
  theme_slide()


save_svg(
  p_stage_bp,
  "viz_stage_bp.svg",
  width = 7.5,
  height = 5.2
)


# ------------------------------------------------------------
# 14. STAGE x TEMPERATURE: boxplot
# ------------------------------------------------------------

p_stage_temp <- ggplot(
  dat,
  aes(
    x = stage,
    y = temp,
    fill = stage
  )
) +
  geom_boxplot(
    width = 0.58,
    linewidth = 0.8,
    alpha = 0.85,
    outlier.size = 2.3
  ) +
  scale_fill_manual(
    values = STAGE_COLORS,
    guide = "none"
  ) +
  labs(
    x = "Disease stage",
    y = "Body temperature (°C)"
  ) +
  theme_slide()


save_svg(
  p_stage_temp,
  "viz_stage_temp.svg",
  width = 7.5,
  height = 5.2
)


# ------------------------------------------------------------
# 15. SEX x STAGE x BP: faceted boxplot
# ------------------------------------------------------------

p_sex_stage_bp <- ggplot(
  dat,
  aes(
    x = sex,
    y = bp,
    fill = sex
  )
) +
  geom_boxplot(
    width = 0.58,
    linewidth = 0.8,
    alpha = 0.85,
    outlier.size = 2
  ) +
  facet_wrap(
    ~ stage,
    nrow = 1
  ) +
  scale_fill_manual(
    values = SEX_COLORS,
    guide = "none"
  ) +
  labs(
    x = "Sex",
    y = "Systolic blood pressure (mmHg)"
  ) +
  theme_slide()

p_heat_bp <- make_mean_heatmap(
  data = dat,
  variable = "bp",
  legend_title = "Mean systolic BP (mmHg)",
  digits = 0
)


viz_sex_stage_bp <- p_sex_stage_bp | p_heat_bp

viz_sex_stage_bp <- viz_sex_stage_bp +
  plot_layout(
    widths = c(3.2, 1.25)
  )


save_svg(
  viz_sex_stage_bp,
  "viz_sex_stage_bp.svg",
  width = 11.5,
  height = 5.4
)


# ------------------------------------------------------------
# 16. SEX x STAGE x TEMPERATURE: faceted boxplot
# ------------------------------------------------------------

p_sex_stage_temp <- ggplot(
  dat,
  aes(
    x = sex,
    y = temp,
    fill = sex
  )
) +
  geom_boxplot(
    width = 0.58,
    linewidth = 0.8,
    alpha = 0.85,
    outlier.size = 2
  ) +
  facet_wrap(
    ~ stage,
    nrow = 1
  ) +
  scale_fill_manual(
    values = SEX_COLORS,
    guide = "none"
  ) +
  labs(
    x = "Sex",
    y = "Body temperature (°C)"
  ) +
  theme_slide()

p_heat_temp <- make_mean_heatmap(
  data = dat,
  variable = "temp",
  legend_title = "Mean temperature (°C)",
  digits = 1
)


viz_sex_stage_temp <- p_sex_stage_temp | p_heat_temp

viz_sex_stage_temp <- viz_sex_stage_temp +
  plot_layout(
    widths = c(3.2, 1.25)
  )


save_svg(
  viz_sex_stage_temp,
  "viz_sex_stage_temp.svg",
  width = 11.5,
  height = 5.4
)

# ------------------------------------------------------------
# 17. SEX x BP x TEMPERATURE: color-coded scatter plot
# ------------------------------------------------------------

p_sex_bp_temp <- ggplot(
  dat,
  aes(
    x = bp,
    y = temp,
    color = sex
  )
) +
  geom_point(
    size = 3,
    alpha = 0.78
  ) +
  scale_color_manual(
    values = SEX_COLORS
  ) +
  labs(
    x = "Systolic blood pressure (mmHg)",
    y = "Body temperature (°C)",
    color = "Sex"
  ) +
  theme_scatter()

viz_sex_bp_temp <- add_grouped_marginals(
  p_sex_bp_temp
)

save_marginal_svg(
  viz_sex_bp_temp,
  "viz_sex_bp_temp.svg",
  width = 8.4,
  height = 6.1
)

# ------------------------------------------------------------
# 18. STAGE x BP x TEMPERATURE: color-coded scatter plot
# ------------------------------------------------------------

p_stage_bp_temp <- ggplot(
  dat,
  aes(
    x = bp,
    y = temp,
    color = stage
  )
) +
  geom_point(
    size = 3,
    alpha = 0.78
  ) +
  scale_color_manual(
    values = STAGE_COLORS
  ) +
  labs(
    x = "Systolic blood pressure (mmHg)",
    y = "Body temperature (°C)",
    color = "Disease stage"
  ) +
  theme_scatter()

viz_stage_bp_temp <- add_grouped_marginals(
  p_stage_bp_temp
)

save_marginal_svg(
  viz_stage_bp_temp,
  "viz_stage_bp_temp.svg",
  width = 8.4,
  height = 6.1
)

# ------------------------------------------------------------
# 19. SEX x STAGE x BP x TEMPERATURE:
#     color + shape encoded scatter plot
# ------------------------------------------------------------

p_sex_stage_bp_temp <- ggplot(
  dat,
  aes(
    x = bp,
    y = temp,
    color = sex,
    size = stage
  )
) +
  geom_point(
    alpha = 0.8,
    stroke = 0.8
  ) +
  scale_color_manual(
    values = SEX_COLORS
  ) +
  scale_size_manual(
    values = c(`Stage 1` = 2, `Stage 2` = 4, `Stage 3` = 8),
    labels = c("1", "2", "3")
  ) +
  labs(
    x = "Systolic blood pressure (mmHg)",
    y = "Body temperature (°C)",
    color = "Sex",
    size = "Disease stage"
  ) +
  theme_scatter() +
  theme(
    legend.box = "horizontal"
  )


save_svg(
  p_sex_stage_bp_temp,
  "viz_sex_stage_bp_temp.svg",
  width = 8.5,
  height = 5.7
)

# ------------------------------------------------------------
# 20. Standalone defective plots
# ------------------------------------------------------------

# ============================================================
# Faulty / misleading visualization examples
# ============================================================

TRAP_RED  <- "#DC2626"
TRAP_FILL <- "#64748B"
TRAP_DARK <- "#334155"


# ------------------------------------------------------------
# 1. Zero baseline vs truncated baseline
# ------------------------------------------------------------

trap_axis_dat <- data.frame(
  Group = factor(
    c("Treatment A", "Treatment B"),
    levels = c("Treatment A", "Treatment B")
  ),
  Rate = c(72, 78)
)


# Correct version: zero baseline
p_trap_zero_axis <- ggplot(
  trap_axis_dat,
  aes(
    x = Group,
    y = Rate
  )
) +
  geom_col(
    width = 0.62,
    fill = TRAP_FILL
  ) +
  geom_text(
    aes(label = paste0(Rate, "%")),
    vjust = -0.5,
    size = 5,
    fontface = "bold",
    color = COL_TEXT
  ) +
  scale_y_continuous(
    limits = c(0, 85),
    breaks = seq(0, 80, 20),
    expand = expansion(mult = c(0, 0.04))
  ) +
  labs(
    x = NULL,
    y = "Response rate (%)"
  ) +
  theme_slide() +
  theme(
    legend.position = "none"
  )


save_svg(
  p_trap_zero_axis,
  "trap_zero_axis.svg",
  width = 5,
  height = 4.2
)


# Misleading version: truncated baseline
p_trap_truncated_axis <- ggplot(
  trap_axis_dat,
  aes(
    x = Group,
    y = Rate
  )
) +
  geom_col(
    width = 0.62,
    fill = TRAP_RED
  ) +
  geom_text(
    aes(label = paste0(Rate, "%")),
    vjust = -0.5,
    size = 5,
    fontface = "bold",
    color = COL_TEXT
  ) +
  coord_cartesian(
    ylim = c(68, 81)
  ) +
  scale_y_continuous(
    breaks = seq(68, 80, 2),
    expand = expansion(mult = c(0, 0.04))
  ) +
  labs(
    x = NULL,
    y = "Response rate (%)"
  ) +
  theme_slide() +
  theme(
    legend.position = "none"
  )


save_svg(
  p_trap_truncated_axis,
  "trap_truncated_axis.svg",
  width = 5,
  height = 4.2
)

# ------------------------------------------------------------
# 2. Too many pie slices
# ------------------------------------------------------------

set.seed(14)

pie_dat <- data.frame(
  Category = paste0("Category ", LETTERS[1:18]),
  Value = sample(3:12, 18, replace = TRUE)
)


p_trap_many_pie <- ggplot(
  pie_dat,
  aes(
    x = "",
    y = Value,
    fill = Category
  )
) +
  geom_col(
    width = 1,
    color = "white",
    linewidth = 0.5
  ) +
  coord_polar(
    theta = "y"
  ) +
  labs(
    x = NULL,
    y = NULL,
    fill = "Category"
  ) +
  theme_void(
    base_size = 16
  ) +
  theme(
    legend.position = "right",
    legend.text = element_text(size = 9),
    legend.title = element_text(
      size = 11,
      face = "bold"
    )
  )


save_svg(
  p_trap_many_pie,
  "trap_many_pie.svg",
  width = 5,
  height = 4.2
)

# ------------------------------------------------------------
# 3. Line plot for unordered categories
# ------------------------------------------------------------

unordered_dat <- data.frame(
  Department = factor(
    c("Cardiology", "Neurology", "Surgery", "Oncology", "Pediatrics"),
    levels = c(
      "Cardiology",
      "Neurology",
      "Surgery",
      "Oncology",
      "Pediatrics"
    )
  ),
  Patients = c(42, 68, 51, 79, 46)
)


p_trap_unordered_line <- ggplot(
  unordered_dat,
  aes(
    x = Department,
    y = Patients,
    group = 1
  )
) +
  geom_line(
    linewidth = 1.3,
    color = TRAP_RED
  ) +
  geom_point(
    size = 4,
    color = TRAP_RED
  ) +
  labs(
    x = "Hospital department",
    y = "Number of patients"
  ) +
  theme_slide() +
  theme(
    axis.text.x = element_text(
      angle = 25,
      hjust = 1
    )
  )


save_svg(
  p_trap_unordered_line,
  "trap_unordered_line.svg",
  width = 5,
  height = 4.2
)

# ------------------------------------------------------------
# 4. 3D bars / perspective distortion
#    (with a second categorical dimension and occlusion)
# ------------------------------------------------------------

library(plot3D)
library(viridis)

set.seed(123)
x <- seq(0, 10, length.out = 10)
y <- seq(0, 10, length.out = 10)
z <- matrix(runif(100, min = 0, max = 1.25), nrow = 10, ncol = 10)

color_palette <- viridis(100)


svg(
  filename = "trap_3d_bars.svg",
  width = 6,
  height = 5,
  bg = "transparent",
  pointsize = 14
)

par(
  mar = c(0.75,0,0,0)
)

hist3D(
  x = x, y = y, z = z,
  xlab = "x", ylab = "y", zlab = "",
  col = color_palette,
  border = "black",
  space = 0.1,
  theta = -35, phi = 20,
  ticktype = "detailed",
  bty = "b2",
  colkey = FALSE,
  lighting = TRUE
)

dev.off()