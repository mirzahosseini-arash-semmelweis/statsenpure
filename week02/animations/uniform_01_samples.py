from manim import *
import numpy as np

OBSERVED = "#1f6feb"
MODEL = "#c65d09"
INK = "#182230"
MUTED = "#667085"
LINE = "#d9e1ea"
PAPER = "#fbfcfe"

class Uniform01Samples(Scene):
    def construct(self):
        self.camera.background_color = PAPER

        # ------------------------------------------------------------------
        # Large number line
        # ------------------------------------------------------------------
        line = NumberLine(
            x_range=[0, 1, 0.1],
            length=10.5,
            include_ticks=False,
            include_numbers=False,
            color=INK
        ).shift(UP * 0.15)

        title = MathTex(
            r"\text{sample from }\mathcal{U}(0,1)",
            font_size=40,
            color=MODEL
        ).next_to(line, UP, buff=0.55)

        left_label = Text(
            "0",
            font_size=34,
            color=MUTED
        ).next_to(line.n2p(0), DOWN, buff=0.28)

        right_label = Text(
            "1",
            font_size=34,
            color=MUTED
        ).next_to(line.n2p(1), DOWN, buff=0.28)

        self.add(line, title, left_label, right_label)

        # ------------------------------------------------------------------
        # Value tracker controls current x-position
        # ------------------------------------------------------------------
        x_tracker = ValueTracker(0.20)

        # Sliding dot just below the number line
        dot = always_redraw(
            lambda: Dot(
                point=line.n2p(x_tracker.get_value()) + DOWN * 0.23,
                radius=0.13,
                color=OBSERVED
            )
        )

        # Small vertical guide from line to dot
        guide = always_redraw(
            lambda: Line(
                start=line.n2p(x_tracker.get_value()),
                end=line.n2p(x_tracker.get_value()) + DOWN * 0.18,
                color=OBSERVED,
                stroke_width=4
            )
        )

        # Continuously updating value label below the line
        value_display = always_redraw(
            lambda: VGroup(
                MathTex("X =", color=OBSERVED).scale(1.0),
                DecimalNumber(
                    x_tracker.get_value(),
                    num_decimal_places=2,
                    color=OBSERVED
                ).scale(1.0)
            )
            .arrange(RIGHT, buff=0.15)
            .next_to(dot, DOWN, buff=0.35)
        )

        subtitle = Text(
            "any point in the interval is possible",
            font_size=30,
            color=MUTED
        ).next_to(line, DOWN, buff=1.35)

        self.play(FadeIn(dot), FadeIn(guide), FadeIn(value_display), run_time=0.8)

        # ------------------------------------------------------------------
        # Smoothly move between random values
        # ------------------------------------------------------------------
        targets = [0.18, 0.74, 0.31, 0.92, 0.46, 0.08, 0.63, 0.27, 0.20]

        for t in targets:
            self.play(
                x_tracker.animate.set_value(float(t)),
                run_time=1.0,
                rate_func=smooth
            )

        self.play(FadeIn(subtitle), run_time=0.6)
        self.wait(1.2)
