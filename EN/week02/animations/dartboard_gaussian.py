from manim import *
import numpy as np

# ------------------------------------------------------------
# Course palette
# ------------------------------------------------------------

OBSERVED = "#1f6feb"      # blue: observed data
MODEL = "#c65d09"         # orange: model
INK = "#182230"
MUTED = "#667085"
LINE = "#d9e1ea"
PAPER = "#fbfcfe"

# reproducibility
rng = np.random.default_rng(12)


class DartboardGaussian(ThreeDScene):
    def construct(self):
        self.camera.background_color = PAPER

        # --------------------------------------------------------
        # Camera
        # --------------------------------------------------------
        self.set_camera_orientation(
            phi=68 * DEGREES,
            theta=-45 * DEGREES,
            zoom=0.95
        )

        # --------------------------------------------------------
        # Board plane and axes
        # --------------------------------------------------------
        board = Surface(
            lambda u, v: np.array([u, v, 0]),
            u_range=[-3.2, 3.2],
            v_range=[-3.2, 3.2],
            resolution=(10, 10),
            checkerboard_colors=[GREY_E, GREY_D],
            fill_opacity=0.18,
            stroke_color=LINE,
            stroke_opacity=0.55,
            stroke_width=1.0
        )

        x_axis = Line3D(
            start=np.array([-3.25, 0, 0]),
            end=np.array([ 3.25, 0, 0]),
            color=MUTED,
            thickness=0.02
        )

        y_axis = Line3D(
            start=np.array([0, -3.25, 0]),
            end=np.array([0,  3.25, 0]),
            color=MUTED,
            thickness=0.02
        )

        # Concentric rings for "dartboard" feel
        rings = VGroup()
        for r in [0.6, 1.2, 1.8, 2.4, 3.0]:
            ring = Circle(
                radius=r,
                color=LINE,
                stroke_width=1.8
            ).move_to(ORIGIN)
            rings.add(ring)

        center_dot = Dot3D(point=ORIGIN, radius=0.06, color=INK)

        board_label = Text(
            "Observed outcomes on a measurement surface",
            font_size=28,
            color=MUTED
        ).to_corner(UL)

        self.add_fixed_in_frame_mobjects(board_label)

        self.play(
            FadeIn(board),
            Create(x_axis),
            Create(y_axis),
            LaggedStart(*[Create(r) for r in rings], lag_ratio=0.12),
            FadeIn(center_dot),
            FadeIn(board_label),
            run_time=2.2
        )

        # --------------------------------------------------------
        # Generate Gaussian dart locations
        # --------------------------------------------------------
        # Most points near center, some more distant
        n = 75
        pts = rng.normal(loc=0.0, scale=1.0, size=(n, 2))

        # keep points inside visible region
        pts = np.clip(pts, -3.0, 3.0)

        dart_group = VGroup()
        dart_stems = VGroup()

        for x, y in pts:
            p = np.array([x, y, 0.03])

            dot = Dot3D(
                point=p,
                radius=0.05,
                color=OBSERVED
            )
            dart_group.add(dot)

            # tiny stem above the board for a "dart pin" feel
            stem = Line3D(
                start=np.array([x, y, 0.24]),
                end=np.array([x, y, 0.06]),
                color=OBSERVED,
                thickness=0.012
            )
            dart_stems.add(stem)

        # --------------------------------------------------------
        # Throw darts in batches
        # --------------------------------------------------------
        throw_label = Text(
            "Most observations cluster near the center.\nExtreme outcomes are possible, but rarer.",
            font_size=28,
            color=INK,
            line_spacing=0.9
        ).to_corner(DR)

        self.add_fixed_in_frame_mobjects(throw_label)
        self.play(FadeIn(throw_label), run_time=0.7)

        # Animate in small batches
        batch_size = 8
        for i in range(0, len(dart_group), batch_size):
            dots_batch = dart_group[i:i+batch_size]
            stems_batch = dart_stems[i:i+batch_size]

            self.play(
                LaggedStart(
                    *[
                        AnimationGroup(
                            FadeIn(stem, shift=UP * 0.15),
                            FadeIn(dot, shift=UP * 0.15),
                        )
                        for stem, dot in zip(stems_batch, dots_batch)
                    ],
                    lag_ratio=0.12
                ),
                run_time=0.55
            )

        self.wait(0.5)

        # --------------------------------------------------------
        # Transparent Gaussian surface emerges
        # --------------------------------------------------------
        def gaussian_height(x, y, sigma=1.0):
            return 2.6 * np.exp(-(x**2 + y**2) / (2 * sigma**2))

        surface = Surface(
            lambda u, v: np.array([u, v, gaussian_height(u, v)]),
            u_range=[-3, 3],
            v_range=[-3, 3],
            resolution=(36, 36),
            checkerboard_colors=[MODEL, MODEL],
            fill_opacity=0.22,
            stroke_color=MODEL,
            stroke_opacity=0.38,
            stroke_width=0.7
        )

        wireframe_curves = VGroup()

        # radial slices
        for angle in np.linspace(0, 2*np.pi, 8, endpoint=False):
            curve = ParametricFunction(
                lambda t, a=angle: np.array([
                    t * np.cos(a),
                    t * np.sin(a),
                    gaussian_height(t*np.cos(a), t*np.sin(a))
                ]),
                t_range=np.array([0, 3]),
                color=MODEL,
                stroke_width=1.6
            )
            wireframe_curves.add(curve)

        # cross-sections
        xsec = ParametricFunction(
            lambda t: np.array([t, 0, gaussian_height(t, 0)]),
            t_range=np.array([-3, 3]),
            color=MODEL,
            stroke_width=2.2
        )

        ysec = ParametricFunction(
            lambda t: np.array([0, t, gaussian_height(0, t)]),
            t_range=np.array([-3, 3]),
            color=MODEL,
            stroke_width=2.2
        )

        model_label = Text(
            "A Gaussian model summarizes the pattern:\ncenter + spread",
            font_size=28,
            color=MODEL,
            line_spacing=0.9
        ).to_edge(DOWN)

        self.add_fixed_in_frame_mobjects(model_label)

        self.play(
            FadeOut(throw_label),
            FadeIn(model_label),
            run_time=0.6
        )

        # rise from the board
        self.play(
            FadeIn(surface, shift=UP * 0.2),
            LaggedStart(*[Create(c) for c in wireframe_curves], lag_ratio=0.08),
            Create(xsec),
            Create(ysec),
            run_time=2.5
        )

        self.wait(2.0)
