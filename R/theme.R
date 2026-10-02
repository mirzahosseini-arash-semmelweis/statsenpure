# Statistics 101 figure grammar ------------------------------------------------
# This file is intentionally not sourced by Week 1 yet. It is a shared foundation
# for later R-generated figures.

stat_palette <- c(
  observed    = "#1F6FEB",
  model       = "#C65D09",
  estimate    = "#18864B",
  warning     = "#C93838",
  uncertainty = "#7B4AB5",
  ink         = "#182230",
  muted       = "#667085"
)

theme_statistics101 <- function(base_size = 15, base_family = "sans") {
  ggplot2::theme_minimal(base_size = base_size, base_family = base_family) +
    ggplot2::theme(
      plot.title.position = "plot",
      plot.title = ggplot2::element_text(face = "bold", color = stat_palette[["ink"]]),
      plot.subtitle = ggplot2::element_text(color = stat_palette[["muted"]]),
      axis.title = ggplot2::element_text(color = stat_palette[["ink"]]),
      axis.text = ggplot2::element_text(color = stat_palette[["muted"]]),
      panel.grid.minor = ggplot2::element_blank(),
      panel.grid.major = ggplot2::element_line(linewidth = 0.35, color = "#E4E7EC"),
      legend.position = "top",
      legend.title = ggplot2::element_blank(),
      plot.margin = ggplot2::margin(12, 12, 12, 12)
    )
}
