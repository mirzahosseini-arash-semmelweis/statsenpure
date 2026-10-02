from manim import *

# ------------------------------------------------------------
# Course palette
# ------------------------------------------------------------
OBSERVED = "#1f6feb"      # treatment A / observed data
MODEL = "#c65d09"         # treatment B / comparator
ESTIMATE = "#18864b"      # within-stratum result
WARNING = "#c93838"       # reversal / caution
UNCERTAINTY = "#7b4ab5"   # confounder / stratification
INK = "#182230"
MUTED = "#667085"
PAPER = "#fbfcfe"
PANEL = "#f3f6fa"
LINE = "#d9e1ea"
NAVY = "#101828"


class SimpsonsParadox(Scene):
    """Four-stage Simpson's paradox animation for Week 3.

    1. Show the aggregate comparison.
    2. Reveal the hidden risk strata / unequal case mix.
    3. Reorganize the data by stratum.
    4. Expose the reversal: A > B in each stratum, but B > A overall.
    """

    def construct(self):
        self.camera.background_color = PAPER

        # --------------------------------------------------------
        # Helpers
        # --------------------------------------------------------
        def make_bar(x, rate, group, count, color,
                     base_y=-1.45, max_height=3.15, width=1.12,
                     label_scale=1.0):
            height = max_height * rate

            rect = Rectangle(
                width=width,
                height=height,
                stroke_width=0,
                fill_color=color,
                fill_opacity=0.86,
            )
            rect.move_to([x, base_y + height / 2, 0])

            pct = Text(
                f"{100 * rate:.0f}%",
                font_size=31 * label_scale,
                weight=BOLD,
                color=INK,
            ).next_to(rect, UP, buff=0.12)

            group_label = Text(
                group,
                font_size=27 * label_scale,
                weight=BOLD,
                color=color,
            ).move_to([x, base_y - 0.34, 0])

            count_label = Text(
                count,
                font_size=19 * label_scale,
                color=MUTED,
            ).move_to([x, base_y - 0.72, 0])

            return VGroup(rect, pct, group_label, count_label)

        def make_badge(text, color, width=2.7):
            box = RoundedRectangle(
                corner_radius=0.16,
                width=width,
                height=0.62,
                stroke_color=color,
                stroke_width=2,
                fill_color=color,
                fill_opacity=0.08,
            )
            label = Text(text, font_size=24, weight=BOLD, color=color)
            return VGroup(box, label)

        def make_mix_bar(x, lower_n, higher_n, total, width=2.5):
            lower_w = width * lower_n / total
            higher_w = width * higher_n / total

            lower = Rectangle(
                width=lower_w,
                height=0.28,
                stroke_width=0,
                fill_color=LINE,
                fill_opacity=1,
            )
            higher = Rectangle(
                width=higher_w,
                height=0.28,
                stroke_width=0,
                fill_color=UNCERTAINTY,
                fill_opacity=0.78,
            )

            lower.move_to([x - width / 2 + lower_w / 2, -2.70, 0])
            higher.move_to([x - width / 2 + lower_w + higher_w / 2, -2.70, 0])

            lower_txt = Text(
                f"{lower_n} lower-risk",
                font_size=15,
                color=MUTED,
            ).next_to(lower, DOWN, buff=0.10)

            higher_txt = Text(
                f"{higher_n} higher-risk",
                font_size=15,
                color=UNCERTAINTY,
            ).next_to(higher, DOWN, buff=0.10)

            return VGroup(lower, higher, lower_txt, higher_txt)

        # --------------------------------------------------------
        # Persistent title
        # --------------------------------------------------------
        title = Text(
            "Simpson's paradox",
            font_size=42,
            weight=BOLD,
            color=NAVY,
        ).to_edge(UP, buff=0.24)

        subtitle = Text(
            "Aggregation can reverse the comparison",
            font_size=25,
            color=MUTED,
        ).next_to(title, DOWN, buff=0.10)

        self.play(FadeIn(title), FadeIn(subtitle), run_time=0.8)

        # --------------------------------------------------------
        # STAGE 1 — OVERALL
        # --------------------------------------------------------
        stage1 = Text(
            "1  Look at the overall response rates",
            font_size=25,
            color=INK,
        ).to_edge(LEFT, buff=0.55).shift(UP * 1.65)

        baseline = Line(
            start=[-3.35, -1.45, 0],
            end=[3.35, -1.45, 0],
            stroke_color=LINE,
            stroke_width=2,
        )

        overall_a = make_bar(
            x=-1.35,
            rate=273 / 350,
            group="Treatment A",
            count="273 / 350",
            color=OBSERVED,
        )

        overall_b = make_bar(
            x=1.35,
            rate=289 / 350,
            group="Treatment B",
            count="289 / 350",
            color=MODEL,
        )

        overall_badge = make_badge("Overall: B > A", WARNING, width=2.85)
        overall_badge.to_edge(RIGHT, buff=0.48).shift(UP * 1.56)

        self.play(FadeIn(stage1), Create(baseline), run_time=0.6)
        self.play(
            GrowFromEdge(overall_a[0], DOWN),
            GrowFromEdge(overall_b[0], DOWN),
            FadeIn(overall_a[1:]),
            FadeIn(overall_b[1:]),
            run_time=1.6,
        )
        self.play(FadeIn(overall_badge, shift=UP * 0.12), run_time=0.6)
        self.wait(1.0)

        # --------------------------------------------------------
        # STAGE 2 — REVEAL STRATA / CASE MIX
        # --------------------------------------------------------
        stage2 = Text(
            "2  Reveal a hidden variable: disease severity",
            font_size=25,
            color=INK,
        ).move_to(stage1)

        confounder = RoundedRectangle(
            corner_radius=0.18,
            width=3.15,
            height=0.66,
            stroke_color=UNCERTAINTY,
            stroke_width=2.2,
            fill_color=UNCERTAINTY,
            fill_opacity=0.08,
        )
        confounder.move_to([0, -2.06, 0])

        confounder_label = Text(
            "Disease severity / risk mix",
            font_size=23,
            weight=BOLD,
            color=UNCERTAINTY,
        ).move_to(confounder)

        mix_a = make_mix_bar(-2.15, lower_n=87, higher_n=263, total=350)
        mix_b = make_mix_bar(2.15, lower_n=270, higher_n=80, total=350)

        mix_a_title = Text("Treatment A", font_size=17, color=OBSERVED)
        mix_a_title.next_to(mix_a, UP, buff=0.06)
        mix_b_title = Text("Treatment B", font_size=17, color=MODEL)
        mix_b_title.next_to(mix_b, UP, buff=0.06)

        mix_note = Text(
            "The groups contain very different proportions of lower- and higher-risk patients.",
            font_size=20,
            color=MUTED,
        ).to_edge(DOWN, buff=0.18)

        self.play(Transform(stage1, stage2), run_time=0.6)
        self.play(
            FadeIn(confounder),
            FadeIn(confounder_label),
            run_time=0.7,
        )
        self.play(
            overall_a.animate.set_opacity(0.30),
            overall_b.animate.set_opacity(0.30),
            baseline.animate.set_opacity(0.30),
            overall_badge.animate.set_opacity(0.38),
            FadeIn(mix_a),
            FadeIn(mix_b),
            FadeIn(mix_a_title),
            FadeIn(mix_b_title),
            FadeIn(mix_note),
            run_time=1.3,
        )
        self.wait(1.1)

        # --------------------------------------------------------
        # STAGE 3 — REORDER BY STRATUM
        # --------------------------------------------------------
        stage3 = Text(
            "3  Compare like with like",
            font_size=25,
            color=INK,
        ).move_to(stage1)

        lower_title = Text(
            "Lower-risk patients",
            font_size=27,
            weight=BOLD,
            color=NAVY,
        ).move_to([-3.1, 1.35, 0])

        higher_title = Text(
            "Higher-risk patients",
            font_size=27,
            weight=BOLD,
            color=NAVY,
        ).move_to([3.1, 1.35, 0])

        separator = DashedLine(
            start=[0, -2.95, 0],
            end=[0, 1.70, 0],
            dash_length=0.12,
            stroke_color=LINE,
            stroke_width=2,
        )

        # New stratum-specific bars
        low_a = make_bar(
            x=-4.05,
            rate=81 / 87,
            group="A",
            count="81 / 87",
            color=OBSERVED,
            base_y=-1.40,
            max_height=2.75,
            width=0.92,
            label_scale=0.86,
        )
        low_b = make_bar(
            x=-2.15,
            rate=234 / 270,
            group="B",
            count="234 / 270",
            color=MODEL,
            base_y=-1.40,
            max_height=2.75,
            width=0.92,
            label_scale=0.86,
        )

        high_a = make_bar(
            x=2.15,
            rate=192 / 263,
            group="A",
            count="192 / 263",
            color=OBSERVED,
            base_y=-1.40,
            max_height=2.75,
            width=0.92,
            label_scale=0.86,
        )
        high_b = make_bar(
            x=4.05,
            rate=55 / 80,
            group="B",
            count="55 / 80",
            color=MODEL,
            base_y=-1.40,
            max_height=2.75,
            width=0.92,
            label_scale=0.86,
        )

        stratum_baseline_left = Line(
            [-4.85, -1.40, 0], [-1.35, -1.40, 0],
            stroke_color=LINE, stroke_width=2,
        )
        stratum_baseline_right = Line(
            [1.35, -1.40, 0], [4.85, -1.40, 0],
            stroke_color=LINE, stroke_width=2,
        )

        self.play(Transform(stage1, stage3), run_time=0.55)

        self.play(
            FadeOut(confounder),
            FadeOut(confounder_label),
            FadeOut(mix_note),
            FadeOut(mix_a_title),
            FadeOut(mix_b_title),
            FadeOut(overall_badge),
            FadeOut(baseline),
            FadeOut(overall_a),
            FadeOut(overall_b),
            FadeIn(separator),
            FadeIn(lower_title),
            FadeIn(higher_title),
            FadeIn(stratum_baseline_left),
            FadeIn(stratum_baseline_right),
            run_time=0.9,
        )

        # Animate the case-mix strips splitting into the two strata.
        self.play(
            TransformFromCopy(mix_a, low_a),
            TransformFromCopy(mix_b, low_b),
            TransformFromCopy(mix_a, high_a),
            TransformFromCopy(mix_b, high_b),
            run_time=1.8,
        )
        self.play(FadeOut(mix_a), FadeOut(mix_b), run_time=0.45)
        self.wait(0.8)

        # --------------------------------------------------------
        # STAGE 4 — EXPOSE THE REVERSAL
        # --------------------------------------------------------
        stage4 = Text(
            "4  The comparison reverses after stratification",
            font_size=25,
            color=INK,
        ).move_to(stage1)

        low_badge = make_badge("A > B   (93% vs 87%)", ESTIMATE, width=3.45)
        low_badge.move_to([-3.1, -2.52, 0])

        high_badge = make_badge("A > B   (73% vs 69%)", ESTIMATE, width=3.45)
        high_badge.move_to([3.1, -2.52, 0])

        overall_small = make_badge("But overall: B > A   (83% vs 78%)", WARNING, width=4.55)
        overall_small.move_to([0, 2.03, 0])

        reversal_note = Text(
            "Different case mix created the aggregate reversal.",
            font_size=22,
            weight=BOLD,
            color=WARNING,
        ).to_edge(DOWN, buff=0.12)

        self.play(Transform(stage1, stage4), run_time=0.55)
        self.play(
            FadeIn(low_badge, shift=UP * 0.12),
            FadeIn(high_badge, shift=UP * 0.12),
            run_time=0.8,
        )
        self.play(
            FadeIn(overall_small, shift=DOWN * 0.10),
            run_time=0.65,
        )
        self.play(
            Circumscribe(low_badge, color=ESTIMATE, time_width=0.7),
            Circumscribe(high_badge, color=ESTIMATE, time_width=0.7),
            run_time=1.1,
        )
        self.play(
            Indicate(overall_small, color=WARNING, scale_factor=1.04),
            FadeIn(reversal_note),
            run_time=0.9,
        )

        self.wait(2.0)
