"""Light-theme animated 5-input binary perceptron (Manim Community Edition).

Inspired by the explanatory visual language of 3Blue1Brown's neural-network
series (original scene implementation; does not import 3b1b/manimlib).

Render:
    manim -pqh perceptron_manim.py PerceptronLight
    manim -p -r 1920,1080 perceptron_manim.py PerceptronLight

The illustrative example is a logistic output neuron, not a hard-threshold
historical perceptron: p = sigmoid(w dot x + b), predict 1 if p >= 0.5.
"""

from manim import *
import numpy as np

# Course palette (white/light RevealJS visual system)
BG      = "#FBFCFE"
INK     = "#182230"
MUTED   = "#667085"
LINE    = "#D9E1EA"
BLUE    = "#1F6FEB"       # observed predictors
ORANGE  = "#C65D09"       # model/neuron
GREEN   = "#18864B"       # result/prediction
RED     = "#C93838"       # negative weights
PURPLE  = "#7B4AB5"       # uncertainty
PANEL   = "#F3F6FA"


class PerceptronLight(Scene):
    def construct(self):
        self.camera.background_color = BG

        # Synthetic normalized biomarker inputs, model weights and intercept.
        target = np.array([0.75, 0.20, 0.85, 0.65, 0.30])
        weights = np.array([0.90, -1.10, 0.60, 1.30, -0.70])
        bias = -0.35
        logit = float(np.dot(target, weights) + bias)
        probability = 1 / (1 + np.exp(-logit))
        predicted = int(probability >= .5)

        # Typography and heading
        title = Text("From five biomarkers to one prediction", font_size=38,
                     color=INK, weight=BOLD).to_edge(UP, buff=.38)
        subtitle = Text("A single logistic neuron  |  illustrative values",
                        font_size=22, color=MUTED).next_to(title, DOWN, buff=.12)
        accent = Line(LEFT*6.25, RIGHT*6.25, color=BLUE, stroke_width=4)
        accent.next_to(subtitle, DOWN, buff=.27)
        self.add(title, subtitle, accent)

        # Reserve a clear title/subtitle band above the three column headings.
        # Slightly compress/lower the nodes so labels and panels still fit.
        ys = [1.30, .40, -.50, -1.40, -2.30]
        x_input = -4.55
        input_centers = [np.array([x_input,y,0]) for y in ys]
        hidden_at = np.array([.1,-.50,0])
        output_at = np.array([4.25,-.50,0])

        # Faint panels, drawn before the nodes/edges.
        left_panel = RoundedRectangle(corner_radius=.23, width=2.35, height=5.30,
                                      stroke_color=LINE, stroke_width=1.5,
                                      fill_color=WHITE, fill_opacity=1).move_to([-4.75,-.35,0])
        right_panel = RoundedRectangle(corner_radius=.24, width=2.30, height=5.30,
                                       stroke_color=LINE, stroke_width=1.5,
                                       fill_color=WHITE, fill_opacity=1).move_to([4.25,-.35,0])
        self.play(FadeIn(left_panel), FadeIn(right_panel), run_time=.5)
        
        in_header = Text("INPUTS  x", font_size=22, color=BLUE, weight=BOLD)
        in_header.move_to([-4.55,2.02,0])
        mid_header = Text("WEIGHTED SUM", font_size=21, color=ORANGE, weight=BOLD)
        mid_header.move_to([.15,2.02,0])
        out_header = Text("OUTPUT  p", font_size=22, color=GREEN, weight=BOLD)
        out_header.move_to([4.25,2.02,0])
        self.play(FadeIn(in_header), FadeIn(mid_header), FadeIn(out_header), run_time=.6)

        initial = [.21,.79,.42,.93,.54]
        trackers = [ValueTracker(v) for v in initial]
        input_nodes = VGroup()
        input_readouts = VGroup()
        labels = VGroup()
        for i, center in enumerate(input_centers):
            node = Circle(radius=.34, color=BLUE, stroke_width=2.6,
                          fill_color="#EAF2FF", fill_opacity=1).move_to(center)
            input_nodes.add(node)
            number = DecimalNumber(initial[i], num_decimal_places=2, font_size=22,
                                   color=INK)
            number.add_updater(lambda m, tr=trackers[i], p=center:
                               m.set_value(tr.get_value()).move_to(p))
            input_readouts.add(number)
            label = Text(f"x{i+1}", font_size=21, color=MUTED)
            label.move_to(center + LEFT*.77)
            labels.add(label)

        self.play(LaggedStart(*[Create(c) for c in input_nodes], lag_ratio=.13),
                  FadeIn(labels), FadeIn(input_readouts), run_time=1.15)
        # The input numbers flicker through measurement scenarios, then settle.
        self.play(*[tr.animate.set_value(v) for tr,v in zip(trackers,[.91,.31,.72,.41,.88])],
                  run_time=.65, rate_func=smooth)
        self.play(*[tr.animate.set_value(v) for tr,v in zip(trackers,[.37,.62,.29,.72,.18])],
                  run_time=.55, rate_func=smooth)
        self.play(*[tr.animate.set_value(v) for tr,v in zip(trackers,target)],
                  run_time=.85, rate_func=smooth)
        self.wait(.15)

        # The sign and absolute magnitude of weights determine line color/width.
        base_edges = VGroup()
        heavy_edges = VGroup()
        weight_numbers = VGroup()
        for i, (center, w) in enumerate(zip(input_centers, weights)):
            start = center + RIGHT*.38
            end = hidden_at + LEFT*.57 + UP*(.11 if i==0 else (-.11 if i==4 else 0))
            base = Line(start, end, stroke_width=1.8, color=LINE)
            active = Line(start, end, stroke_width=1.6+4.0*abs(w),
                          color=BLUE if w>0 else RED)
            base_edges.add(base)
            heavy_edges.add(active)
            # Labels positioned at individual edges, near the input rather than the convergence.
            pos = base.point_from_proportion(.31) + (UP*.15 if i < 2 else DOWN*.15)
            wn = Text(f"{w:+.2f}", font_size=18,
                      color=BLUE if w>0 else RED, weight=BOLD)
            wn.move_to(pos)
            weight_numbers.add(wn)

        neuron = Circle(radius=.58, stroke_color=ORANGE, stroke_width=4,
                        fill_color="#FFF2E9", fill_opacity=1).move_to(hidden_at)
        sigma = Text("Σ", font_size=44, color=ORANGE, weight=BOLD).move_to(hidden_at)
        neuron_label = Text("z = w·x + b", font_size=22, color=INK)
        neuron_label.next_to(neuron, DOWN, buff=.40)

        self.play(LaggedStart(*[Create(edge) for edge in base_edges], lag_ratio=.13),
                  Create(neuron), FadeIn(sigma), run_time=1.05)
        self.play(FadeIn(neuron_label), run_time=.35)
        self.play(LaggedStart(*[
            AnimationGroup(TransformFromCopy(base_edges[i], heavy_edges[i]),
                           FadeIn(weight_numbers[i]))
            for i in range(5)], lag_ratio=.17), run_time=1.65)
        # Persist the thick lines and ensure beams are underneath the neuron.
        self.add(heavy_edges)
        self.bring_to_front(neuron,sigma)
        self.play(*[ShowPassingFlash(edge.copy().set_stroke(color=PURPLE,
                          width=edge.get_stroke_width()+2.5), time_width=.35)
                    for edge in heavy_edges], run_time=1.5)

        # Numeric aggregation, genuinely matching the illustrated inputs/weights.
        z_note = Text(f"z = {logit:+.2f}", font_size=24, color=ORANGE, weight=BOLD)
        z_note.next_to(neuron_label, DOWN, buff=.16)
        self.play(FadeIn(z_note), Indicate(neuron, color=ORANGE), run_time=.75)

        # Propagate through the sigmoid to the probability node.
        outgoing = Arrow(neuron.get_right()+RIGHT*.04,
                         output_at+LEFT*.59, buff=.07,
                         stroke_width=4, color=GREEN, max_tip_length_to_length_ratio=.09)
        activation_text = Text("sigmoid", font_size=20, color=MUTED)
        activation_text.next_to(outgoing, UP, buff=.22)
        output_circle = Circle(radius=.58, stroke_color=GREEN,
                               stroke_width=3.5, fill_color="#E9F6ED",
                               fill_opacity=1).move_to(output_at)
        p_tracker = ValueTracker(.5)
        p_text = DecimalNumber(.5, num_decimal_places=2, font_size=30,
                               color=GREEN)
        p_text.add_updater(lambda m: m.set_value(p_tracker.get_value()).move_to(output_at))
        self.play(GrowArrow(outgoing), FadeIn(activation_text),
                  Create(output_circle), FadeIn(p_text), run_time=1.0)
        self.play(p_tracker.animate.set_value(.66), run_time=.45)
        self.play(p_tracker.animate.set_value(.59), run_time=.40)
        self.play(p_tracker.animate.set_value(probability), run_time=.85)

        # Binary classification is a separate step after probability estimation.
        threshold = Text("threshold = 0.50", font_size=19, color=MUTED)
        threshold.move_to([4.25,-1.46,0])
        label0 = Text("0   healthy", font_size=21, color=MUTED)
        label1 = Text("1   sick", font_size=21, color=MUTED)
        label0.move_to([4.25,-1.99,0])
        label1.move_to([4.25,-2.52,0])
        self.play(FadeIn(threshold), FadeIn(label0), FadeIn(label1), run_time=.55)
        winner = label1 if predicted == 1 else label0
        winner_bg = SurroundingRectangle(winner, buff=.13, corner_radius=.14,
                                         color=GREEN, stroke_width=2.5)
        winner_bg.set_fill("#E7F6ED", opacity=.9)
        # Keep the selected label *above* the box fill, not washed out by it.
        winner_bg.set_z_index(1)
        winner.set_z_index(2)
        self.play(Create(winner_bg), winner.animate.set_color(INK).scale(1.09),
                  output_circle.animate.set_fill(GREEN,opacity=.22),
                  Flash(output_circle, color=GREEN, flash_radius=.9), run_time=1.0)
        verdict = Text("Predicted class: 1 (sick)" if predicted else
                       "Predicted class: 0 (healthy)", font_size=25,
                       color=GREEN, weight=BOLD).to_edge(DOWN,buff=.38)
        self.play(FadeIn(verdict, shift=UP*.16), run_time=.6)
        self.wait(1.6)

        for m in input_readouts:
            m.clear_updaters()
        p_text.clear_updaters()
