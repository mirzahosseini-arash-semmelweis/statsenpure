from manim import *
import numpy as np

# ---------------------------------------------------------------------
# Course semantic colors
# ---------------------------------------------------------------------

OBSERVED = "#1f6feb"     # observed outcome
MODEL = "#c65d09"        # theoretical model
ESTIMATE = "#18864b"
WARNING = "#c93838"
PROBABILITY = "#7b4ab5"  # uncertainty / random angle

INK = "#182230"
MUTED = "#667085"
LINE = "#d9e1ea"
PAPER = "#fbfcfe"


class CauchyGeometry(Scene):

    def construct(self):

        self.camera.background_color = PAPER

        # -------------------------------------------------------------
        # Geometry:
        #
        # source = (0, 1)
        # target line y = 2
        #
        # theta is measured from vertical.
        #
        # Therefore:
        #       x = tan(theta)
        #
        # when the ray reaches y = 2.
        # -------------------------------------------------------------

        source = np.array([0.0, 1.0, 0.0])
        target_y = 2.0

        target_line = Line(
            [-6.3, target_y, 0],
            [6.3, target_y, 0],
            color=MUTED,
            stroke_width=3,
        )

        target_label = Text(
            "possible intersection location",
            font_size=22,
            color=MUTED,
        ).next_to(target_line, UP, buff=0.10).align_to(target_line, RIGHT)

        source_dot = Dot(
            source,
            radius=0.09,
            color=INK,
        )

        source_label = Text(
            "source",
            font_size=22,
            color=MUTED,
        ).next_to(source_dot, DOWN, buff=0.12)

        # Uniform random angle
        angle_label = Text(
            "uniform uncertainty in angle",
            font_size=27,
            color=PROBABILITY,
        ).to_edge(UL).shift(DOWN * 0.25)

        relation = Text(
            "intersection:  x = tan(theta)",
            font_size=25,
            color=INK,
        ).next_to(angle_label, DOWN, aligned_edge=LEFT, buff=0.16)

        self.play(
            FadeIn(target_line),
            FadeIn(target_label),
            FadeIn(source_dot),
            FadeIn(source_label),
        )

        self.play(
            FadeIn(angle_label),
            FadeIn(relation),
        )

        # -------------------------------------------------------------
        # Moving angle
        # -------------------------------------------------------------

        theta = ValueTracker(0)

        def intersection():
            x = np.tan(theta.get_value())
            return np.array([x, target_y, 0])

        ray = always_redraw(
            lambda: Line(
                source,
                intersection(),
                color=PROBABILITY,
                stroke_width=5,
            )
        )

        hit = always_redraw(
            lambda: Dot(
                intersection(),
                radius=0.085,
                color=OBSERVED,
            )
        )

        vertical_reference = DashedLine(
            source,
            [0, target_y, 0],
            color=LINE,
            stroke_width=2,
        )

        theta_value = always_redraw(
            lambda: VGroup(
                Text(
                    "theta =",
                    font_size=23,
                    color=MUTED,
                ),
                DecimalNumber(
                    theta.get_value() * 180 / PI,
                    num_decimal_places=1,
                    font_size=25,
                    color=PROBABILITY,
                ),
                Text(
                    "deg",
                    font_size=20,
                    color=MUTED,
                ),
            )
            .arrange(RIGHT, buff=0.10)
            .move_to([4.6, 1.15, 0])
        )

        x_value = always_redraw(
            lambda: VGroup(
                Text(
                    "x =",
                    font_size=23,
                    color=MUTED,
                ),
                DecimalNumber(
                    np.tan(theta.get_value()),
                    num_decimal_places=2,
                    font_size=25,
                    color=OBSERVED,
                ),
            )
            .arrange(RIGHT, buff=0.10)
            .next_to(theta_value, DOWN, buff=0.12)
        )

        self.play(
            Create(vertical_reference),
            Create(ray),
            FadeIn(hit),
            FadeIn(theta_value),
            FadeIn(x_value),
        )

        # Trace emphasizes how much faster x moves near ±90 degrees.
        trace = TracedPath(
            hit.get_center,
            dissipating_time=0.35,
            stroke_color=OBSERVED,
            stroke_width=5,
        )

        self.add(trace)

        # Equal angular motion -> dramatically unequal linear motion.
        self.play(
            theta.animate.set_value(1.40),
            run_time=3.0,
            rate_func=linear,
        )

        self.play(
            theta.animate.set_value(-1.40),
            run_time=5.0,
            rate_func=linear,
        )

        self.play(
            theta.animate.set_value(0),
            run_time=2.0,
            rate_func=smooth,
        )

        # -------------------------------------------------------------
        # Cauchy density
        # -------------------------------------------------------------

        axes = Axes(
            x_range=[-6, 6, 2],
            y_range=[0, 0.35, 0.1],
            x_length=10.5,
            y_length=1.7,
            tips=False,
            axis_config={
                "color": MUTED,
                "stroke_width": 2,
            },
        ).shift(DOWN * 2.05)

        density = axes.plot(
            lambda x: 1 / (np.pi * (1 + x**2)),
            x_range=[-6, 6],
            color=MODEL,
            stroke_width=5,
        )

        density_label = Text(
            "Cauchy density",
            font_size=24,
            color=MODEL,
        ).next_to(axes, UP, buff=0.08).shift(RIGHT * 4)

        transformation = VGroup(
            Text(
                "uniform angle",
                font_size=24,
                color=PROBABILITY,
            ),
            Text(
                "   →   ",
                font_size=24,
                color=MUTED,
            ),
            Text(
                "Cauchy-distributed position",
                font_size=24,
                color=MODEL,
            ),
        ).arrange(RIGHT, buff=0.08).next_to(
            axes,
            DOWN,
            buff=0.18,
        )

        self.play(
            Create(axes),
            Create(density),
            FadeIn(density_label),
            run_time=1.5,
        )

        self.play(
            FadeIn(transformation),
        )

        self.wait(1.5)
