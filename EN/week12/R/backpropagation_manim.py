"""Light-theme Manim Community Edition: backpropagation, 5-10-10-10-1.

Two patients arrive sequentially. A *real* four-layer sigmoid network is
trained using binary cross-entropy and five full-batch-size-one gradient
descent (SGD) steps per patient. The gradients and shown probabilities are
computed from the same weights, not hand-authored animation values.

Render:
    manim -pqh backpropagation_manim.py BackpropagationLight
    manim -p -r 1920,1080 backpropagation_manim.py BackpropagationLight

No external images, 3b1b library, or pretrained models required.
"""

from manim import *
import numpy as np

# ------ Match the light Statistics 101 course theme ------
BG       = "#FBFCFE"
INK      = "#182230"
MUTED    = "#667085"
LINE     = "#D9E1EA"
PANEL    = "#F3F6FA"
BLUE     = "#1F6FEB"       # observations / input
ORANGE   = "#C65D09"       # model / hidden neurons
GREEN    = "#18864B"       # improved estimate / correct class
RED      = "#C93838"       # error / negative weights
PURPLE   = "#7B4AB5"       # backpropagating gradients

STRUCTURE = [5, 10, 10, 10, 1]
LEARNING_RATE = 0.6
UPDATES_PER_PATIENT = 5

# Synthetic normalized measurements for two patients. Illustrative only.
PATIENTS = [
    {"name": "Patient 1  ·  sick", "x": np.array([.86, .22, .79, .44, .12]), "y": 1},
    {"name": "Patient 2  ·  healthy", "x": np.array([.16, .81, .28, .71, .92]), "y": 0},
]


def logistic(z):
    return 1.0 / (1.0 + np.exp(-np.clip(z, -40, 40)))


def bce(prob, target):
    """Binary cross-entropy on one observation."""
    p = float(np.clip(prob, 1.e-10, 1 - 1.e-10))
    return -(target * np.log(p) + (1 - target) * np.log(1 - p))


def initial_model():
    """Actual random (but reproducibly seeded) initial weights."""
    rng = np.random.default_rng(9)
    W = [rng.normal(0, 1.0 / np.sqrt(n_in), size=(n_out, n_in))
         for n_in, n_out in zip(STRUCTURE[:-1], STRUCTURE[1:])]
    B = [rng.normal(0, .10, size=n_out) for n_out in STRUCTURE[1:]]
    return W, B


def forward(W, B, x):
    activations = [np.asarray(x, dtype=float)]
    for w, b in zip(W, B):
        activations.append(logistic(w @ activations[-1] + b))
    return activations


def gradients(W, B, x, truth):
    """Chain-rule backpropagation for sigmoid hidden and sigmoid+BCE output.

    dL/dz_out = p-y. All four matrices get gradients from the *same*
    pre-update forward pass; parameter updates are simultaneous SGD.
    """
    A = forward(W, B, x)
    delta = A[-1] - float(truth)
    grad_W = [None] * 4
    grad_B = [None] * 4
    for k in (3, 2, 1, 0):
        grad_W[k] = np.outer(delta, A[k])
        grad_B[k] = delta.copy()
        if k:
            delta = (W[k].T @ delta) * A[k] * (1 - A[k])
    return grad_W, grad_B


def make_training_story():
    """Return all numerical states and true gradient updates for the scene."""
    W, B = initial_model()
    story = []
    for patient in PATIENTS:
        x, y = patient["x"], patient["y"]
        start_a = forward(W, B, x)
        steps = []
        for _ in range(UPDATES_PER_PATIENT):
            dW, dB = gradients(W, B, x, y)
            W = [w - LEARNING_RATE * gw for w, gw in zip(W, dW)]
            B = [b - LEARNING_RATE * gb for b, gb in zip(B, dB)]
            a = forward(W, B, x)
            steps.append({
                "W": [w.copy() for w in W],
                "B": [b.copy() for b in B],
                "gradW": [g.copy() for g in dW],
                "activations": a,
                "p": float(a[-1][0]),
                "loss": bce(a[-1][0], y),
            })
        story.append({
            "patient": patient,
            "start": start_a,
            "initial_p": float(start_a[-1][0]),
            "initial_loss": bce(start_a[-1][0], y),
            "steps": steps,
        })
    return story


class BackpropagationLight(Scene):
    # Keep animation design / numerical model distinct.
    # Coordinates assume Manim's default 16:9 frame (about 14.22 x 8 units).
    X = [-5.65, -2.98, -.28, 2.43, 5.03]
    Y_CENTER = -.09
    TARGET_X = 6.35

    def construct(self):
        self.camera.background_color = BG
        self.story = make_training_story()
        self.W, self.B = initial_model()

        # Helps catch accidental model changes before producing a video.
        assert .20 < self.story[0]["initial_p"] < .32
        assert self.story[0]["steps"][-1]["p"] > .85
        assert self.story[1]["initial_p"] > .78
        assert self.story[1]["steps"][-1]["p"] < .18

        self.build_frame()
        self.build_network()
        self.build_readouts()

        # -------------------------------------------------------
        # FIRST PATIENT: truth=1, initial predicted p near 0.25.
        # -------------------------------------------------------
        first = self.story[0]
        self.show_patient(first, first_patient=True)
        self.show_forward(first["start"], first["initial_loss"], first["patient"]["y"])
        self.wait(.35)
        self.show_direction(up=True)
        self.train_one_patient(first)
        self.wait(.60)

        # -------------------------------------------------------
        # SECOND PATIENT: truth=0; previous fit predicts p near 0.92.
        # The same gradients / update mechanism now corrects this error.
        # -------------------------------------------------------
        second = self.story[1]
        self.hide_direction()
        self.show_patient(second, first_patient=False)
        self.show_forward(second["start"], second["initial_loss"], second["patient"]["y"])
        self.wait(.35)
        self.show_direction(up=False)
        self.train_one_patient(second)
        self.hide_direction()

        closing = Text(
            "One update helps one patient; reliable prediction needs many patients and validation.",
            font_size=18, color=INK,
        ).move_to([0, -3.78, 0])
        self.play(FadeIn(closing), run_time=.6)
        self.wait(1.8)

        # DecimalNumber updaters are no longer needed once rendering is over.
        for number in self.input_numbers:
            number.clear_updaters()
        self.output_number.clear_updaters()
        self.loss_number.clear_updaters()

    def build_frame(self):
        title = Text("How does backpropagation learn?", font_size=37,
                     color=INK, weight=BOLD).move_to([0, 3.55, 0])
        subtitle = Text(
            "Forward prediction  ·  cross-entropy error  ·  backward gradients  ·  weight update",
            font_size=19, color=MUTED,
        ).move_to([0, 3.05, 0])
        accent = Line([-6.42, 2.73, 0], [6.42, 2.73, 0],
                      color=BLUE, stroke_width=3.3)
        self.play(FadeIn(title), FadeIn(subtitle), Create(accent), run_time=.85)

        # IMPORTANT: draw the panels first, headers afterward, so no panels
        # can obscure header text (the issue from animation 1).
        widths = [1.48, 1.55, 1.55, 1.55, 1.16]
        panels = VGroup(*[
            RoundedRectangle(corner_radius=.15, width=w, height=4.50,
                             stroke_color=LINE, stroke_width=1.2,
                             fill_color=WHITE, fill_opacity=.93)
            .move_to([x, -.17, 0])
            for x, w in zip(self.X, widths)
        ])
        panels.set_z_index(0)
        self.play(FadeIn(panels), run_time=.5)

        labels = ["INPUT x", "HIDDEN 1", "HIDDEN 2", "HIDDEN 3", "OUTPUT p", "TRUTH y"]
        xs = self.X + [self.TARGET_X]
        cols = [BLUE, ORANGE, ORANGE, ORANGE, GREEN, INK]
        headers = VGroup()
        for name, x, color in zip(labels, xs, cols):
            txt = Text(name, font_size=14.5, color=color, weight=BOLD)
            txt.move_to([x, 2.37, 0]).set_z_index(8)
            headers.add(txt)
        self.play(LaggedStart(*[FadeIn(t) for t in headers], lag_ratio=.1), run_time=.6)

    def build_network(self):
        self.nodes = []
        self.node_groups = []
        for li, (n, x) in enumerate(zip(STRUCTURE, self.X)):
            ys = (np.array([self.Y_CENTER]) if n == 1
                  else np.linspace(1.66 if n == 10 else 1.43,
                                   -1.89 if n == 10 else -1.64, n))
            radius = .33 if li == 0 else (.39 if li == 4 else .153)
            circles = VGroup()
            for y in ys:
                c = Circle(radius=radius, stroke_color=BLUE if li == 0 else LINE,
                           stroke_width=2.0 if li in (0, 4) else 1.3,
                           fill_color="#FFFFFF", fill_opacity=1)
                c.move_to([x, y, 0]).set_z_index(4)
                circles.add(c)
            self.nodes.append(circles)
            self.node_groups.append(circles)

        # Matrix entry W[layer][destination, source] maps to one visible line.
        self.edges = []
        self.edge_groups = VGroup()
        for li in range(4):
            edge_mat = []
            edge_group = VGroup()
            for j, dest in enumerate(self.nodes[li + 1]):
                row = []
                for i, source in enumerate(self.nodes[li]):
                    w = float(self.W[li][j, i])
                    edge = Line(source.get_right() + RIGHT*.025,
                                dest.get_left() + LEFT*.025,
                                color=self.weight_color(w),
                                stroke_width=self.weight_width(w),
                                stroke_opacity=self.weight_opacity(w))
                    edge.set_z_index(1)
                    row.append(edge)
                    edge_group.add(edge)
                edge_mat.append(row)
            self.edges.append(edge_mat)
            self.edge_groups.add(edge_group)

        self.play(FadeIn(self.edge_groups),
                  LaggedStart(*[FadeIn(layer) for layer in self.node_groups], lag_ratio=.11),
                  run_time=1.0)

        self.input_trackers = [ValueTracker(0) for _ in range(5)]
        self.input_numbers = VGroup()
        for node, t in zip(self.nodes[0], self.input_trackers):
            p = node.get_center().copy()
            m = DecimalNumber(0, num_decimal_places=2, font_size=18, color=INK)
            m.move_to(p)
            m.add_updater(lambda obj, tr=t, pt=p:
                          obj.set_value(tr.get_value()).move_to(pt))
            m.set_z_index(6)
            self.input_numbers.add(m)
        self.play(FadeIn(self.input_numbers), run_time=.35)

        self.p_tracker = ValueTracker(.5)
        self.output_number = DecimalNumber(.5, num_decimal_places=3,
                                           font_size=21, color=INK)
        p_center = self.nodes[4][0].get_center().copy()
        self.output_number.move_to(p_center)
        self.output_number.add_updater(
            lambda obj: obj.set_value(self.p_tracker.get_value()).move_to(p_center))
        self.output_number.set_z_index(8)
        self.add(self.output_number)

        p_label = Text("p(sick)", font_size=16, color=MUTED)
        p_label.move_to([self.X[4], .66, 0])
        self.play(FadeIn(p_label), run_time=.3)

        # Persistent truth node; its number changes on patient 2.
        self.truth_node = Circle(radius=.38, stroke_color=GREEN, stroke_width=2.8,
                                 fill_color="#EAF7EF", fill_opacity=1)
        self.truth_node.move_to([self.TARGET_X, self.Y_CENTER, 0]).set_z_index(5)
        self.truth_number = Text("1", font_size=28, color=INK, weight=BOLD)
        self.truth_number.move_to(self.truth_node).set_z_index(6)
        self.patient_tag = Text("Patient 1 · sick", font_size=15.5,
                                color=GREEN, weight=BOLD).move_to([5.96, 1.40, 0])

    def build_readouts(self):
        loss_panel = RoundedRectangle(
            corner_radius=.18, width=3.2, height=.78,
            stroke_color=LINE, stroke_width=1.3,
            fill_color="#FFFFFF", fill_opacity=1,
        ).move_to([3.22, -3.20, 0])
        loss_panel.set_z_index(0)

        loss_label = Text("Loss", font_size=20, color=RED, weight=BOLD)
        loss_label.move_to([2.67, -3.20, 0]).set_z_index(4)
        self.loss_tracker = ValueTracker(0.0)
        self.loss_number = DecimalNumber(0, num_decimal_places=3,
                                          font_size=28, color=RED)
        self.loss_number.move_to([3.77, -3.20, 0]).set_z_index(5)
        self.loss_number.add_updater(
            lambda obj: obj.set_value(self.loss_tracker.get_value())
                           .move_to([3.77, -3.20, 0]))
        self.add(loss_panel, loss_label, self.loss_number)

        # The status stays clear of the big loss panel and all network panels.
        self.status = Text("Randomly initialized weights", font_size=17,
                           color=MUTED, weight=MEDIUM)
        self.status.move_to([-3.6, -2.68, 0]).set_z_index(5)
        self.add(self.status)

        self.direction_group = None

    @staticmethod
    def weight_color(w):
        return BLUE if w >= 0 else RED

    @staticmethod
    def weight_width(w):
        return .60 + 2.10 * min(abs(float(w)) / 1.3, 1)

    @staticmethod
    def weight_opacity(w):
        return .17 + .19 * min(abs(float(w)) / 1.3, 1)

    def set_status(self, message, color=MUTED):
        nxt = Text(message, font_size=17, color=color, weight=MEDIUM)
        nxt.move_to(self.status)
        self.play(Transform(self.status, nxt), run_time=.35)

    def show_patient(self, entry, first_patient=False):
        patient = entry["patient"]
        x, y = patient["x"], patient["y"]

        if first_patient:
            self.play(FadeIn(self.truth_node), FadeIn(self.truth_number),
                      FadeIn(self.patient_tag), run_time=.6)
            # The inputs flicker through numerical readings locally, with no
            # Transform from the canvas center.
            for vec in [np.array([.29,.71,.54,.18,.90]),
                        np.array([.63,.11,.86,.75,.26]), x]:
                self.play(*[tr.animate.set_value(float(v))
                            for tr,v in zip(self.input_trackers, vec)],
                          run_time=.40 if not np.array_equal(vec, x) else .65)
        else:
            self.set_status("A different patient arrives", BLUE)
            nxt = Text(patient["name"], font_size=15.5,
                       color=BLUE, weight=BOLD).move_to(self.patient_tag)
            self.play(
                Transform(self.patient_tag, nxt),
                Transform(self.truth_number,
                          Text(str(y), font_size=28, color=INK, weight=BOLD)
                          .move_to(self.truth_node)),
                self.truth_node.animate.set_stroke(BLUE, width=2.8)
                     .set_fill("#EAF2FF", opacity=1),
                *[tr.animate.set_value(float(v))
                  for tr, v in zip(self.input_trackers, x)],
                run_time=1.1,
            )

        self.set_status("Forward pass: compute p(sick)", BLUE)

    def layer_fill_anims(self, acts, truth):
        animations = []
        for li in (1,2,3):
            for circle, a in zip(self.nodes[li], acts[li]):
                animations.append(circle.animate.set_stroke(ORANGE, width=1.8)
                                  .set_fill(ORANGE, opacity=.08 + .80*float(a)))
        p = float(acts[-1][0])
        good = (int(p >= .5) == int(truth))
        col = GREEN if good else RED
        animations.append(self.nodes[4][0].animate.set_stroke(col, width=2.8)
                          .set_fill(col, opacity=.12 if good else .08))
        return animations

    def forward_pulses(self, slow=False):
        """A small representative selection of signals travels left to right."""
        for li in range(4):
            chosen = self.top_edges(li, self.W[li], limit=7)
            pulses = [
                ShowPassingFlash(
                    Line(e.get_start(), e.get_end(), color=BLUE,
                         stroke_width=2.8, stroke_opacity=.9),
                    time_width=.52,
                ) for e in chosen
            ]
            self.play(LaggedStart(*pulses, lag_ratio=.05),
                      run_time=.52 if slow else .27)

    def show_forward(self, activations, loss, truth):
        self.forward_pulses(slow=True)
        self.play(
            self.p_tracker.animate.set_value(float(activations[-1][0])),
            self.loss_tracker.animate.set_value(float(loss)),
            *self.layer_fill_anims(activations, truth),
            run_time=.75,
        )
        self.set_status("Prediction disagrees with the known label", RED)

    def show_direction(self, up):
        # Arrow directly beside the output circle, not outside the frame.
        x = 5.76
        if up:
            start, end, msg = [x,-.87,0], [x,.43,0], "raise p"
        else:
            start, end, msg = [x,.43,0], [x,-.87,0], "lower p"
        arrow = Arrow(start, end, buff=0, stroke_width=4.0,
                      max_tip_length_to_length_ratio=.21, color=GREEN)
        desc = Text(msg, font_size=15.5, color=GREEN, weight=BOLD)
        desc.move_to([5.84, -1.18, 0])
        self.direction_group = VGroup(arrow, desc).set_z_index(6)
        self.play(GrowArrow(arrow), FadeIn(desc), run_time=.55)
        self.set_status("Backward pass: use the loss gradient", PURPLE)

    def hide_direction(self):
        if self.direction_group is not None:
            self.play(FadeOut(self.direction_group), run_time=.35)
            self.direction_group = None

    def top_edges(self, layer_i, scores, limit=8):
        scores_flat = np.abs(np.asarray(scores)).flatten()
        indices = np.argsort(scores_flat)[-min(limit,len(scores_flat)):]
        edges = self.edges[layer_i]
        n_input = scores.shape[1]
        return [edges[int(k // n_input)][int(k % n_input)] for k in indices]

    def backward_one_layer(self, li, W_new, dW, slow):
        # Show real signed weights changing as the gradient travels right -> left.
        flashes = []
        for edge in self.top_edges(li, dW, limit=9):
            # Opposite direction of the forward-pass flash.
            beam = Line(edge.get_end(), edge.get_start(), color=PURPLE,
                        stroke_width=3.6, stroke_opacity=.96)
            flashes.append(ShowPassingFlash(beam, time_width=.52))

        animations = []
        for j, row in enumerate(self.edges[li]):
            for i, edge in enumerate(row):
                w = float(W_new[j,i])
                animations.append(
                    edge.animate.set_stroke(
                        color=self.weight_color(w),
                        width=self.weight_width(w),
                        opacity=self.weight_opacity(w),
                    )
                )
        self.play(
            *animations,
            LaggedStart(*flashes, lag_ratio=.06),
            run_time=.56 if slow else .22,
        )

    def train_one_patient(self, entry):
        y = entry["patient"]["y"]
        for iteration, step in enumerate(entry["steps"]):
            slow = iteration == 0
            # Each step is an honest SGD update, computed using gradients from
            # the preceding weights; the visualization traverses layers 4 -> 1.
            for li in (3, 2, 1, 0):
                self.backward_one_layer(li, step["W"][li],
                                        step["gradW"][li], slow)
            self.W = [w.copy() for w in step["W"]]
            self.B = [b.copy() for b in step["B"]]
            # Re-evaluate the updated model: probability and BCE must match.
            self.play(
                self.p_tracker.animate.set_value(step["p"]),
                self.loss_tracker.animate.set_value(step["loss"]),
                *self.layer_fill_anims(step["activations"], y),
                run_time=.65 if slow else .33,
            )
            if slow:
                self.set_status("Gradient descent lowers binary cross-entropy", GREEN)
        self.set_status("Five SGD updates completed", GREEN)
        self.play(Flash(self.nodes[4][0], color=GREEN, flash_radius=.82),
                  run_time=.50)


if __name__ == "__main__":
    # Numerical self-check: usable without importing/running Manim's renderer
    # by extracting the pure NumPy portion, if desired.
    s = make_training_story()
    for entry in s:
        p = entry["patient"]
        print(p["name"],
              "initial", round(entry["initial_p"],3),
              "loss", round(entry["initial_loss"],3),
              "final", round(entry["steps"][-1]["p"],3),
              "loss", round(entry["steps"][-1]["loss"],3))
