# Statistics 101 — Quarto/revealjs course skeleton

This folder is the shared source for a 12-week graduate Pharmaceutical Studies statistics course.

## First build

1. Install current **Quarto** and open `statistics-101.Rproj` in RStudio.
2. Open `week01/week01.qmd`.
3. Click **Render** (or use `quarto render week01/week01.qmd` in the Terminal).
4. The rendered HTML should appear under `_site/week01/`.
5. During presentation:
   - `S` opens speaker view.
   - `M` opens the Reveal menu.
   - `O` opens slide overview.

## Design rules

### Semantic colors

- Blue: observed data / samples
- Orange: population / model / unknown truth
- Green: estimate / effect / learned result
- Red: warning / misconception / error
- Purple: probability / uncertainty

Color should never be the only differentiator; use labels, shapes or line styles as well.

### Slide classes

Use classes on level-2 headings:

```markdown
## A motivating question {.motivation-slide .question-slide}
## Concept {.concept-slide}
## Mathematics {.math-slide}
## Example {.example-slide}
## Case study {.case-slide}
## Checkpoint {.checkpoint-slide}
## Student exercise {.exercise-slide}
```

### Reusable components

Useful CSS classes already defined in `assets/scss/course.scss` include:

- `.concept-line`
- `.example-box`
- `.eyebrow`
- `.big-question`
- `.takeaway`
- `.observed`, `.model`, `.estimate`, `.warning`, `.probability`
- `.compare-grid`, `.metric-card`
- `.flow-row`, `.flow-node`, `.flow-arrow`
- `.life-grid`, `.life-card`

## Speaker notes

Keep lecturer detail in reveal speaker notes rather than on the projected slide:

```markdown
::: {.notes}
What you want to say, questions to ask, timing, and reminders.
:::
```

## R figures

`R/theme.R` defines the shared semantic palette and `theme_statistics101()` for future ggplot2 figures. Week 1 does not require R to render its first seven slides.

## Later interactivity

For browser-side student interactions, prefer small Observable JS (`{ojs}`) cells where possible. Reserve global JavaScript for truly course-wide behavior.


## Week 1 full deck

`week01/week01.qmd` now contains a complete 30-slide Week 1 lecture, including the title slide, speaker notes, two browser-side Observable JS interactive slides, and the extended semantic CSS components used by the deck.

Recommended first render:

```bash
quarto render week01/week01.qmd
```

Interactive slides use Quarto's Observable JS runtime and should work in the rendered HTML without Shiny or an R server.
