# Statistics 101 — Statistics for Pharmacists

**A 12-week graduate-level statistics course for Pharmaceutical Studies**, delivered as interactive [Quarto](https://quarto.org/) / [RevealJS](https://revealjs.com/) slide decks.

The course develops statistical reasoning from probability and study design through inference, regression, pharmaceutical applications, time-dependent data, multivariate analysis, and machine learning. It emphasizes **what the data support, what remains uncertain, and how to evaluate statistical claims** rather than memorizing procedures.

## Course outline

|Week|Topic|
|-|-|
|01|Reasoning with data under uncertainty|
|02|Probability distributions|
|03|From probability to data|
|04|Understanding data|
|05|Sampling distributions|
|06|Statistical inference|
|07|Comparing groups|
|08|Relationships and regression|
|09|Beyond classical linear methods|
|10|Pharmaceutical and clinical statistics|
|11|Time, survival, and smoothing|
|12|Multivariate statistics and machine learning|

## Getting started

**To present an existing lecture**, you need Quarto and a modern browser. RStudio is convenient but not required. The figures, videos, and most widget data are already generated; **R, Python, and Manim are not required to render or present the finished decks**.

1. Install [Quarto](https://quarto.org/docs/get-started/) and, optionally, [RStudio](https://posit.co/download/rstudio-desktop/).
2. Open `statistics-101.Rproj` in RStudio, or open a terminal at the repository root.
3. Render any lecture, for example:

```bash
   quarto render week01/week01.qmd
   quarto render week12/week12.qmd
   ```

4. Open the generated HTML in a modern browser. The output directory depends on the Quarto project configuration (commonly `\_site/` for a website project).
5. For editing and interactive checks, use `quarto preview week12/week12.qmd` or the **Render** button in RStudio.

To render all twelve decks individually in **PowerShell**:

```powershell
for ($i = 1; $i -le 12; $i++) {
    $week = "week{0:D2}" -f $i
    quarto render "$week/$week.qmd"
}
```

### Presenting with RevealJS

* **S** — speaker view / notes
* **O** — slide overview
* **M** — RevealJS menu (where enabled)
* **Arrow keys / Space** — navigate slides and fragments

Several slides contain draggable diagrams, sliders, prediction buttons, and quizzes. Interact with these directly in the rendered presentation.

## Repository organization

The principal files follow this pattern (some weeks use only a subset of the optional assets):

```text
statistics-101.Rproj
assets/
  scss/
    course.scss            # Shared colors, typography, and slide components
    week01.scss            # Week-specific styling, where needed
    ...
    week12.scss
week01/
  week01.qmd
...
week12/
  week12.qmd
  widgets.js               # Custom interactive labs
  data.js                  # Precomputed data used by the labs
  mammoth\_umap\_data.js     # Precomputed UMAP mammoth example
  digit\_model.js           # Local digit-recognition model weights
  figures/                 # Pre-rendered SVG illustrations
  media/                   # Pre-rendered teaching animations
R/                         # Source and regeneration scripts, where supplied
manim/                     # Animation source, where supplied
```

Every lecture's `weekXX.qmd` is the **source of truth for that week's slides**. Week-specific SCSS extends, rather than replaces, the shared stylesheet in `assets/scss/course.scss`. Local figure, data, JavaScript, and video paths are referenced by the relevant QMD.

## Interactive labs and generated assets

The course uses a mix of **Observable JavaScript** (in some earlier lectures), **plain browser-side JavaScript/SVG** (including the later labs), and **pre-rendered SVG or MP4 assets**. Interactive activities run in the browser; no Shiny application or R server is needed to present them.

Examples include probability and sampling experiments, regression and inference visualizations, smoothing and Gaussian-process labs, Markov chains, PCA, UMAP, clustering, decision-tree traversal, polynomial double descent, and handwritten-digit recognition.

The later Week 12 labs use local precomputed data and models. In particular:

* The **UMAP mammoth** displays a rotatable 3D point cloud and 2D embeddings for `n\_neighbors = 15, 50, 200` with `min\_dist = 0.25`. Anatomical coloring is illustrative; it is not a validated segmentation of the specimen.
* The **decision-tree lab** demonstrates decisions made from three *synthetic* standardized predictors. Its displayed leaf proportions are not clinically calibrated risk estimates.
* The **digit recognizer** uses a locally trained demonstration model based on resized handwritten-digit examples from scikit-learn. It is **not an officially MNIST-trained model** and does not establish any medical diagnostic performance.
* The **double-descent lab** uses selected synthetic examples to demonstrate a possible validation-error pattern; double descent is not guaranteed for every dataset.

The animations explain concepts; they should not be interpreted as recordings of model training or inference unless explicitly identified as such.

### Regenerating material

Most lectures can be rendered without running any generation scripts. When editing underlying figures, datasets, or animations, inspect the relevant scripts under `R/`, `manim/`, or the corresponding week folder. Depending on the asset, regeneration may require R packages, Python packages, and/or Manim Community Edition. Keep regenerated files alongside the QMD so presentations remain reproducible without recomputation at lecture time.

## Visual and authoring conventions

The shared design uses a **semantic color vocabulary**:

|Color|Intended role|
|-|-|
|Blue|Observed data / samples|
|Orange|Population / model / unknown truth|
|Green|Estimates / effects / learned results|
|Red|Warnings / errors / misconceptions|
|Purple|Probability / uncertainty|

Never rely on color alone: use labels, shapes, line styles, or annotations as well.

Common slide classes include `.motivation-slide`, `.question-slide`, `.concept-slide`, `.math-slide`, `.example-slide`, `.case-slide`, `.checkpoint-slide`, and `.exercise-slide`. Reusable components in `course.scss` include `.concept-line`, `.example-box`, `.eyebrow`, `.big-question`, `.takeaway`, `.compare-grid`, `.metric-card`, `.flow-row`, and `.life-card`.

Place detailed teaching cues in RevealJS speaker notes:

```markdown
::: {.notes}
Talking points, discussion prompts, timing, and reminders.
:::
```

For custom HTML inside QMD files, keep nested markup **shallow and minimally indented**: overly indented raw HTML can be parsed as unintended paragraphs and disrupt the slide layout. Test both the rendered slide and its interactions after modifying a widget.

## Scientific scope and attribution

Many datasets, scenarios, risk labels, and model outputs are **synthetic instructional examples**. Unless a slide explicitly states otherwise, they are not real patient records, validated diagnostic procedures, or clinical recommendations.

The Week 12 mammoth example uses data adapted from [Google PAIR's *Understanding UMAP*](https://github.com/PAIR-code/understanding-umap) (Copyright 2019 Google LLC, **Apache License 2.0**) and acknowledges the [Smithsonian 3D mammoth project](https://3d.si.edu/). The classroom widget uses a modified point-cloud sample and independently computed example embeddings. Preserve the applicable license, source notices, and modification/attribution documentation when redistributing these assets.

\---

**Statistics 101 · Graduate Pharmaceutical Studies**  
*From probability to evidence, inference, modeling, and generalization.*

