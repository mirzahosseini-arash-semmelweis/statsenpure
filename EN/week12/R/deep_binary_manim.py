from manim import *
import numpy as np

# ------------------------------------------------------------
# Light-theme binary neural network animation
# 5 inputs -> 10 -> 10 -> 10 -> 1 output
# Manim Community Edition
# ------------------------------------------------------------

# ---------- palette ----------
BG = "#F7F9FC"
INK = "#182230"
MUTED = "#667085"
LINE = "#D0D7E2"

OBSERVED = "#2F6FED"      # blue
MODEL = "#C65D09"         # orange
ESTIMATE = "#18864B"      # green
WARNING = "#C93838"       # red
UNCERTAINTY = "#7B4AB5"   # purple

POS_W = "#4F83F1"         # positive-weight flash
NEG_W = "#D97777"         # negative-weight flash
PANEL = "#FFFFFF"


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


class DeepBinaryClassifier(Scene):
    def construct(self):
        self.camera.background_color = BG
        np.random.seed(7)

        # ---------------- Title area ----------------
        title = Text(
            "Binary classifier with hidden layers",
            font_size=30,
            color=INK,
            weight=BOLD
        ).to_edge(UP, buff=0.22)

        subtitle = Text(
            "Input biomarkers activate successive hidden representations before a final healthy/sick decision",
            font_size=16,
            color=MUTED
        ).next_to(title, DOWN, buff=0.10)

        self.play(FadeIn(title, shift=DOWN * 0.15), FadeIn(subtitle, shift=DOWN * 0.15))
        self.wait(0.2)

        # ---------------- Network architecture ----------------
        layer_sizes = [5, 10, 10, 10, 1]
        layer_x = [-5.8, -2.8, 0.2, 3.2, 6.05]
        layer_radius = [0.28, 0.19, 0.19, 0.19, 0.31]
        y_top = 1.45
        y_bottom = -2.15

        headers = [
            ("INPUTS x", OBSERVED),
            ("HIDDEN 1", MODEL),
            ("HIDDEN 2", MODEL),
            ("HIDDEN 3", MODEL),
            ("OUTPUT p", ESTIMATE),
        ]

        header_mobs = VGroup()
        for (txt, col), x in zip(headers, layer_x):
            h = Text(txt, font_size=17, color=col, weight=BOLD)
            h.move_to([x, 2.18, 0])
            header_mobs.add(h)

        # Background column panels (subtle)
        panels = VGroup()
        panel_widths = [1.4, 1.55, 1.55, 1.55, 1.45]
        for x, w in zip(layer_x, panel_widths):
            r = RoundedRectangle(
                corner_radius=0.16,
                width=w,
                height=4.95,
                stroke_color=LINE,
                stroke_width=1.2,
                fill_color=PANEL,
                fill_opacity=1.0,
            ).move_to([x, -0.08, 0])
            panels.add(r)

        self.play(FadeIn(panels, lag_ratio=0.05), FadeIn(header_mobs, lag_ratio=0.05))
        self.wait(0.1)

        # Create node layers
        layers = []
        for idx, (n, x, r) in enumerate(zip(layer_sizes, layer_x, layer_radius)):
            ys = (
                np.array([-0.08])
                if n == 1
                else np.linspace(y_top, y_bottom, n)
            )
            circles = []
            labels = []
            layer_group = VGroup()
            for y in ys:
                c = Circle(
                    radius=r,
                    stroke_color=LINE,
                    stroke_width=1.8,
                    fill_color="#FFFFFF",
                    fill_opacity=1.0,
                ).move_to([x, y, 0])

                placeholder = Text(
                    "",
                    font_size=12,
                    color=INK,
                ).move_to(c.get_center())

                circles.append(c)
                labels.append(placeholder)
                layer_group.add(c, placeholder)

            layers.append(
                {
                    "circles": circles,
                    "labels": labels,
                    "group": layer_group,
                }
            )

        # Connections
        connection_groups = []
        all_connections = VGroup()
        for li in range(len(layers) - 1):
            left = layers[li]["circles"]
            right = layers[li + 1]["circles"]
            mat = []
            group = VGroup()

            for i, c1 in enumerate(left):
                row = []
                for j, c2 in enumerate(right):
                    line = Line(
                        c1.get_right(),
                        c2.get_left(),
                        buff=0.02,
                        stroke_color="#BFC8D8",
                        stroke_width=0.85,
                        stroke_opacity=0.22,
                    )
                    row.append(line)
                    group.add(line)
                mat.append(row)

            connection_groups.append(mat)
            all_connections.add(group)

        # Add connections behind nodes
        self.play(FadeIn(all_connections, lag_ratio=0.02), FadeIn(VGroup(*[L["group"] for L in layers])))
        self.wait(0.25)

        # ---------------- Generate one internally consistent network ----------------
        x_final = np.array([0.82, 0.31, 0.67, 0.21, 0.54])
        W1, b1, W2, b2, W3, b3, W4, b4, a1, a2, a3, out = self.make_consistent_network(x_final)

        # ---------------- Input jitter then settle ----------------
        rng = np.random.default_rng(123)
        for _ in range(4):
            temp = rng.uniform(0.05, 0.95, size=5)
            anims = self.set_node_values(
                layer=layers[0],
                values=temp,
                fill_color=OBSERVED,
                decimals=2,
                stroke_color=OBSERVED
            )
            self.play(*anims, run_time=0.22)

        # Final input vector
        self.play(
            *self.set_node_values(
                layer=layers[0],
                values=x_final,
                fill_color=OBSERVED,
                decimals=2,
                stroke_color=OBSERVED,
            ),
            run_time=0.55
        )
        self.wait(0.25)

        # ---------------- Layer transitions ----------------
        self.animate_transition(
            layers[0], layers[1], connection_groups[0],
            W1, a1, fill_color=MODEL, layer_name="hidden 1", decimals=2
        )
        self.wait(0.18)

        self.animate_transition(
            layers[1], layers[2], connection_groups[1],
            W2, a2, fill_color=MODEL, layer_name="hidden 2", decimals=2
        )
        self.wait(0.18)

        self.animate_transition(
            layers[2], layers[3], connection_groups[2],
            W3, a3, fill_color=MODEL, layer_name="hidden 3", decimals=2
        )
        self.wait(0.18)

        # Output transition
        self.animate_transition(
            layers[3], layers[4], connection_groups[3],
            W4, np.array([out]), fill_color=ESTIMATE, layer_name="output", decimals=3
        )

        # ---------------- Final classification ----------------
        out_circle = layers[4]["circles"][0]
        out_value = out

        threshold_note = Text(
            "Decision threshold = 0.50",
            font_size=15,
            color=MUTED
        ).move_to([5.5, -2.78, 0])

        self.play(FadeIn(threshold_note, shift=UP * 0.15), run_time=0.5)

        healthy = Text("0  healthy", font_size=21, color=MUTED, weight=MEDIUM)
        sick = Text("1  sick", font_size=21, color=MUTED, weight=MEDIUM)

        class_group = VGroup(healthy, sick).arrange(DOWN, aligned_edge=LEFT, buff=0.18)
        class_group.move_to([6.0, -3.55, 0])

        self.play(FadeIn(class_group, lag_ratio=0.15), run_time=0.55)

        predicted_idx = 1 if out_value >= 0.5 else 0
        winner = class_group[predicted_idx]

        winner_bg = SurroundingRectangle(
            winner,
            color=ESTIMATE,
            stroke_width=2.2,
            buff=0.14,
            corner_radius=0.10
        )
        winner_bg.set_fill(ESTIMATE, opacity=0.10)
        winner_bg.set_z_index(1)
        winner.set_z_index(2)

        self.play(
            Create(winner_bg),
            winner.animate.set_color(INK).scale(1.08),
            out_circle.animate.set_fill(ESTIMATE, opacity=0.25).set_stroke(ESTIMATE, width=2.6),
            Flash(out_circle, color=ESTIMATE, flash_radius=0.95),
            run_time=1.0
        )

        # Optional concluding annotation
        pred_text = Text(
            f"Predicted probability of illness: {out_value:.3f}",
            font_size=18,
            color=INK,
            weight=MEDIUM
        ).move_to([0.0, -3.48, 0])

        self.play(FadeIn(pred_text, shift=UP * 0.15), run_time=0.6)
        self.wait(1.8)

    # ------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------
    def make_consistent_network(self, x_final):
        """
        Build one fixed reproducible network and keep trying seeds
        until the final output lands in a nice didactic range.
        """
        for seed in range(1, 200):
            rng = np.random.default_rng(seed)

            W1 = rng.normal(0, 0.9, size=(10, 5))
            b1 = rng.normal(0, 0.25, size=(10,))

            W2 = rng.normal(0, 0.8, size=(10, 10))
            b2 = rng.normal(0, 0.22, size=(10,))

            W3 = rng.normal(0, 0.8, size=(10, 10))
            b3 = rng.normal(0, 0.22, size=(10,))

            W4 = rng.normal(0, 0.8, size=(1, 10))
            b4 = np.array([0.12])

            a1 = sigmoid(W1 @ x_final + b1)
            a2 = sigmoid(W2 @ a1 + b2)
            a3 = sigmoid(W3 @ a2 + b3)
            out = float(sigmoid(W4 @ a3 + b4)[0])

            # Want a reasonably decisive binary probability
            if 0.66 <= out <= 0.88:
                return W1, b1, W2, b2, W3, b3, W4, b4, a1, a2, a3, out

        # fallback (very unlikely to be used)
        W1 = np.full((10, 5), 0.3)
        b1 = np.linspace(-0.2, 0.2, 10)
        W2 = np.eye(10) * 0.9
        b2 = np.zeros(10)
        W3 = np.eye(10) * 0.8
        b3 = np.zeros(10)
        W4 = np.full((1, 10), 0.18)
        b4 = np.array([0.05])
        a1 = sigmoid(W1 @ x_final + b1)
        a2 = sigmoid(W2 @ a1 + b2)
        a3 = sigmoid(W3 @ a2 + b3)
        out = float(sigmoid(W4 @ a3 + b4)[0])
        return W1, b1, W2, b2, W3, b3, W4, b4, a1, a2, a3, out

    def set_node_values(self, layer, values, fill_color, decimals=2, stroke_color=None):
        anims = []
        stroke_col = stroke_color if stroke_color is not None else fill_color

        for i, (circle, label, v) in enumerate(
            zip(layer["circles"], layer["labels"], values)
        ):
            opacity = 0.10 + 0.55 * float(np.clip(v, 0, 1))
            anims.append(
                circle.animate.set_fill(fill_color, opacity=opacity).set_stroke(stroke_col, width=2.2)
            )

            new_lab = DecimalNumber(
                float(v),
                num_decimal_places=decimals,
                font_size=self.font_for_circle(circle),
                color=INK
            ).move_to(circle.get_center())

            anims.append(FadeOut(label))
            anims.append(FadeIn(new_lab))
            layer["labels"][i] = new_lab

        return anims

    def font_for_circle(self, circle):
        r = circle.radius
        if r >= 0.30:
            return 22
        elif r >= 0.25:
            return 16
        else:
            return 12

    def animate_transition(self, layer_from, layer_to, connection_matrix, W, activations, fill_color, layer_name="", decimals=2):
        # incoming weighted flashes
        max_abs = np.max(np.abs(W)) if np.max(np.abs(W)) > 0 else 1.0
        flashes = []

        for i in range(len(layer_from["circles"])):
            for j in range(len(layer_to["circles"])):
                line = connection_matrix[i][j]
                w = W[j, i]  # W is (n_to, n_from)

                color = POS_W if w >= 0 else NEG_W
                width = 0.7 + 2.7 * abs(w) / max_abs

                flashes.append(
                    ShowPassingFlash(
                        line.copy().set_stroke(color=color, width=width, opacity=0.95),
                        time_width=0.65
                    )
                )

        self.play(LaggedStart(*flashes, lag_ratio=0.003), run_time=1.25)

        # target nodes settle to activation values
        node_anims = self.set_node_values(
            layer=layer_to,
            values=np.array(activations).flatten(),
            fill_color=fill_color,
            decimals=decimals,
            stroke_color=fill_color
        )

        self.play(*node_anims, run_time=0.75)

        # small pulse on target layer
        self.play(
            *[
                Indicate(c, color=fill_color, scale_factor=1.06)
                for c in layer_to["circles"]
            ],
            run_time=0.5
        )