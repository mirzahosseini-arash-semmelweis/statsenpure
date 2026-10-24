# Statistics 101 — Week 11
# Rebuild the 20 pre-rendered SVG assets from RStudio.
# The canonical figure generator is Python/matplotlib, shipped alongside this
# course. Run this R wrapper from the week11 package root. The outputs are
# static SVG files; the lecture contains no runtime Python dependency.
package_root <- normalizePath(getwd(), winslash = "/", mustWork = TRUE)
script <- file.path(package_root, "python", "render_week11_figures.py")
if (!file.exists(script)) stop("Run from the extracted statistics-101-week11/ directory")
python <- Sys.which("python")
if (!nzchar(python)) python <- Sys.which("python3")
if (!nzchar(python)) stop("Python not found. Install Python with numpy, scipy and matplotlib.")
status <- system2(python, script, stdout = TRUE, stderr = TRUE)
cat(paste(status, collapse = "\n"), "\n")
if (!is.null(attr(status, "status")) && attr(status, "status") != 0) stop("Figure generation failed")
