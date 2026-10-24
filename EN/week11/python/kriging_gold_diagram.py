"""Create a standalone, valid SVG illustration of measured and inferred gold concentration.

This is a conceptual Kriging schematic; the interpolated curve is illustrative,
not the output of a fitted spatial covariance / Kriging model.
"""
from pathlib import Path
from random import Random
import xml.etree.ElementTree as ET

WIDTH, HEIGHT = 1000, 650
SOIL_TOP, GOLD_DEPTH = 350, 548

COL_BG = "#ffffff"
COL_CURVE = "#38b6ff"
COL_GOLD_BRIGHT = "#ffcc00"
COL_GOLD_SOFT = "#e9cc64"
COL_GROUND_TOP = "#f0e0c0"
COL_GROUND_BOT = "#d0c0a0"
COL_GROUND_UNDER = "#a0a0b0"
COL_TEXT_DARK = "#333333"
COL_MEASURED = "#ff6b6b"
COL_INFERRED = "#64748b"

RNG = Random(123)


def circle(cx, cy, radius, fill, stroke="none", stroke_width=0, extra=""):
    return (
        f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{radius:.2f}" '
        f'fill="{fill}" stroke="{stroke}" stroke-width="{stroke_width}" {extra}/>'
    )


def draw_clump(cx, cy, count, radius_range=(2, 5.5)):
    pieces = []
    for _ in range(count):
        x = cx + RNG.uniform(-39, 39)
        y = cy + RNG.uniform(-17, 17)
        r = RNG.uniform(*radius_range)
        pieces.append(circle(x, y, r, COL_GOLD_SOFT, extra='opacity="0.93"'))
    return "\n".join(pieces)


def draw_drill(x, depth=GOLD_DEPTH):
    """Draw a drill only where the concentration was actually measured."""
    pieces = [
        f'<g stroke="{COL_TEXT_DARK}" stroke-linejoin="round">',
        f'<path d="M{x},302 L{x-16},342 L{x+16},342 Z" fill="none" stroke-width="1.8"/>',
        f'<line x1="{x}" y1="315" x2="{x}" y2="{depth}" stroke-width="2.5"/>',
        f'<line x1="{x-20}" y1="342" x2="{x+20}" y2="342" stroke-width="2"/>',
        '</g>',
    ]
    for _ in range(4):
        pieces.append(circle(
            x + RNG.uniform(-12, 12), depth + RNG.uniform(-8, 8),
            4.2, COL_GOLD_BRIGHT, stroke="#b38a00", stroke_width=0.45
        ))
    return "\n".join(pieces)


def callout(x, y, w, word, measured):
    icon = (
        circle(24, 23, 8, COL_MEASURED, COL_TEXT_DARK, 1.2)
        if measured else
        circle(24, 23, 8, "white", COL_INFERRED, 2.3)
    )
    return f'''<g transform="translate({x},{y})">
    <rect x="0" y="0" width="{w}" height="46" rx="11" fill="#ffffff" stroke="#64748b" stroke-width="1.5"/>
    {icon}
    <text x="{w/2+12:.1f}" y="30" text-anchor="middle" font-family="sans-serif"
          font-size="19" font-weight="700" fill="{COL_TEXT_DARK}">{word}</text>
    </g>'''


def generate_gold_diagram(filename):
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{HEIGHT}" viewBox="0 0 {WIDTH} {HEIGHT}" role="img" aria-labelledby="title desc">',
        '<title id="title">Measured and inferred gold concentration schematic</title>',
        '<desc id="desc">Drilling observations, subsurface gold deposits, and an illustrative interpolated concentration curve. A hollow marker denotes an unmeasured prediction location.</desc>',
        f'''<defs>
        <linearGradient id="ground_gradient" x1="0%" y1="0%" x2="0%" y2="100%">
          <stop offset="0%" stop-color="{COL_GROUND_TOP}"/>
          <stop offset="60%" stop-color="{COL_GROUND_BOT}"/>
          <stop offset="100%" stop-color="{COL_GROUND_UNDER}"/>
        </linearGradient>
        </defs>''',
        f'<rect width="{WIDTH}" height="{HEIGHT}" fill="{COL_BG}"/>',
        # Soil and subtle strata
        f'<rect x="0" y="{SOIL_TOP}" width="{WIDTH}" height="{HEIGHT-SOIL_TOP}" fill="url(#ground_gradient)"/>',
        '<path d="M0 350 Q250 348 500 350 T1000 350" fill="none" stroke="#978a74" stroke-width="2"/>',
        '<path d="M0 433 Q250 419 505 438 T1000 427" fill="none" stroke="#b7aa91" stroke-width="1.4" opacity="0.48"/>',
        '<path d="M0 593 Q260 574 505 593 T1000 590" fill="none" stroke="#8f8c96" stroke-width="1.7" opacity="0.35"/>',
    ]

    # Yellow deposits near a subsurface mineralized horizon.
    for x, n in [(200, 10), (400, 25), (600, 12), (800, 18), (940, 10)]:
        parts.append(draw_clump(x, GOLD_DEPTH, n))

    # Vertical projections. 800 is a prediction, not a drilling site.
    observations = [(200, 250), (400, 150), (600, 310), (940, 327)]
    for x, y in observations:
        parts.append(
            f'<line x1="{x}" y1="{y+9}" x2="{x}" y2="{SOIL_TOP}" '
            f'stroke="{COL_TEXT_DARK}" stroke-width="1.5" stroke-dasharray="5 5" opacity="0.5"/>'
        )

    parts.append(
        f'<line x1="800" y1="282" x2="800" y2="{GOLD_DEPTH}" '
        f'stroke="{COL_INFERRED}" stroke-width="2" stroke-dasharray="7 7" opacity="0.75"/>'
    )
    parts.append(circle(800, GOLD_DEPTH, 15, "none", COL_INFERRED, 2, extra='stroke-dasharray="4 5" opacity="0.9"'))

    for x, _ in observations:
        parts.append(draw_drill(x))

    # Cyan interpolated concentration schematic, drawn over projections and boreholes.
    parts.append(
        f'<path d="M100 280 C130 270 170 260 200 250 '
        f'C260 230 340 170 400 150 '
        f'C460 130 540 290 600 310 '
        f'C660 330 740 290 800 270 '
        f'C860 250 910 310 950 330 '
        f'C970 340 980 310 1000 300" '
        f'fill="none" stroke="{COL_CURVE}" stroke-width="5" '
        f'stroke-linecap="round" stroke-linejoin="round"/>'
    )

    # Sample points; one emphasized as MEASURED, one hollow as INFERRED.
    for x, y in [(200, 250), (600, 310), (950, 330)]:
        parts.append(circle(x, y, 7, COL_GOLD_SOFT, COL_TEXT_DARK, 1.4))
    parts.append(circle(400, 150, 12, COL_MEASURED, COL_TEXT_DARK, 2.0))
    parts.append(circle(800, 270, 11, "white", COL_INFERRED, 3))

    # Concentration direction indicator in the air above the soil.
    parts += [
        f'<path d="M90 310 L90 88 L78 108 M90 88 L102 108" fill="none" stroke="{COL_GOLD_BRIGHT}" stroke-width="6" stroke-linecap="round" stroke-linejoin="round"/>',
        f'<text x="60" y="198" transform="rotate(-90 60 198)" font-family="sans-serif" font-size="21" font-weight="bold" text-anchor="middle" fill="{COL_TEXT_DARK}">GOLD CONCENTRATION</text>',
        f'<text x="90" y="72" text-anchor="middle" font-family="sans-serif" font-size="17" fill="#b38a00">MORE</text>',
        f'<text x="90" y="337" text-anchor="middle" font-family="sans-serif" font-size="17" fill="#b38a00">LESS</text>',
    ]

    # Callout panels and short leaders.
    parts += [
        callout(320, 22, 165, "MEASURED", measured=True),
        f'<line x1="400" y1="68" x2="400" y2="134" stroke="{COL_TEXT_DARK}" stroke-width="1.4" stroke-dasharray="4 4"/>',
        callout(722, 168, 158, "INFERRED", measured=False),
        f'<line x1="800" y1="214" x2="800" y2="254" stroke="{COL_TEXT_DARK}" stroke-width="1.4" stroke-dasharray="4 4"/>',
        f'<text x="980" y="631" font-family="sans-serif" font-size="13" text-anchor="end" fill="#555a65">Conceptual interpolation schematic</text>',
        '</svg>',
    ]

    output = Path(filename)
    # output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text("\n".join(parts), encoding="utf-8")
    # Fail immediately if the exported markup is invalid XML.
    ET.parse(output)
    print(f"SVG created and XML validated: {output.resolve()}")


if __name__ == "__main__":
    generate_gold_diagram("kriging_Gold_diagram_light.svg")
