"""Optional Manim Community Edition adaptations of the Week 11 motion concepts.
The shipped MP4s are pre-rendered with python/render_week11_animations.py
so students do not need Manim or a network connection.

Use, if Manim is installed:
  manim -pql manim/week11_animations.py RandomWalkDimensions
  manim -pql manim/week11_animations.py StationaryMarkov

These are source adaptations for further editing, not identical frame-for-frame
copies of the bundled OpenCV MP4s.
"""
import numpy as np
from manim import *
from scipy.signal import savgol_filter
from scipy.interpolate import make_smoothing_spline

OBS="#1f6feb"; EST="#18864b"; UNC="#7b4ab5"; WARN="#c93838"; TEXT_COLOR = "#0f172a"

class RandomWalkDimensions(ThreeDScene):
    def construct(self):
        # 1. Enable Light Mode
        self.camera.background_color = WHITE

        rng = np.random.default_rng(101119)
        num_steps = 3400
        run_time = 34.0

        # 2. Fixed 3D camera perspective (No rotation)
        self.set_camera_orientation(phi=65 * DEGREES, theta=-55 * DEGREES)

        # 3. Fixed 2D overlay headers (Dark text for white background)
        label_2d = Text("2D lattice", font_size=30, weight=BOLD, color=TEXT_COLOR).to_corner(UL).shift(RIGHT * 1.2 + DOWN * 0.2)
        label_3d = Text("3D lattice", font_size=30, weight=BOLD, color=TEXT_COLOR).to_corner(UR).shift(LEFT * 1.2 + DOWN * 0.2)
        self.add_fixed_in_frame_mobjects(label_2d, label_3d)

        # Centers and spatial scaling
        center_2d = LEFT * 3.4
        center_3d = RIGHT * 3.4
        scale = 0.085

        # 4. Create visual bounding wireframes (Soft slate lines for light background)
        bounding_square = Square(side_length=4.2, stroke_color="#cbd5e1", stroke_width=1.5, fill_color="#f8fafc", fill_opacity=0.4)
        bounding_square.move_to(center_2d)

        bounding_cube = Cube(side_length=4.2, stroke_color="#94a3b8", stroke_width=1.5, fill_opacity=0.0)
        bounding_cube.move_to(center_3d)

        self.add(bounding_square, bounding_cube)

        # 5. Generate 2D Random Walk
        steps_2d = np.zeros((num_steps, 3), float)
        for i in range(num_steps):
            dim_idx = rng.integers(2)  # x or y
            steps_2d[i, dim_idx] = rng.choice([-1, 1])
        pos_2d = np.vstack([np.zeros(3), np.cumsum(steps_2d, axis=0)])
        coords_2d = [center_2d + p * scale for p in pos_2d]

        # 6. Generate 3D Random Walk
        steps_3d = np.zeros((num_steps, 3), float)
        for i in range(num_steps):
            dim_idx = rng.integers(3)  # x, y, or z
            steps_3d[i, dim_idx] = rng.choice([-1, 1])
        pos_3d = np.vstack([np.zeros(3), np.cumsum(steps_3d, axis=0)])
        coords_3d = [center_3d + p * scale for p in pos_3d]

        # 7. Build VMobjects and Start Dots
        curve_2d = VMobject(color=OBS, stroke_width=2.5).set_points_as_corners(coords_2d)
        curve_3d = VMobject(color=UNC, stroke_width=2.5).set_points_as_corners(coords_3d)

        start_dot_2d = Dot3D(coords_2d[0], radius=0.07, color=EST)
        start_dot_3d = Dot3D(coords_3d[0], radius=0.07, color=EST)
        self.add(start_dot_2d, start_dot_3d)

        # 8. Animate simultaneous walks
        self.play(
            Create(curve_2d, rate_func=linear),
            Create(curve_3d, rate_func=linear),
            run_time=run_time
        )

        # 9. Highlight endpoints
        end_dot_2d = Dot3D(coords_2d[-1], radius=0.09, color=WARN)
        end_dot_3d = Dot3D(coords_3d[-1], radius=0.09, color=WARN)
        self.play(FadeIn(end_dot_2d), FadeIn(end_dot_3d))

        self.wait(2.5)

# Presentation palette
BLUE_DOTS = "#2563eb"
PURPLE_SMOOTH = "#7c3aed"
ORANGE_FIT = "#ea580c"
RED_CENTER = "#dc2626"
MUTED = "#64748b"
DARK = "#1f2937"

class MovingAverageWindow(Scene):
    def construct(self):

        self.camera.background_color = WHITE

        # --------------------------------------------------
        # 1. Generate exactly the same synthetic signal
        # --------------------------------------------------

        rng = np.random.default_rng(101)

        n = 120
        x_data = np.linspace(0, 10, n)

        y_true = (
            np.sin(x_data)
            + 0.5 * np.cos(2 * x_data)
            + 0.3 * x_data
        )

        y_noisy = y_true + rng.normal(
            0, 0.25, size=n
        )

        window_len = 31
        half_win = window_len // 2

        first_idx = half_win
        last_idx = n - half_win - 1

        # --------------------------------------------------
        # 2. Calculate centered moving average
        #
        # Each smoothed observation is the arithmetic mean
        # of the 31 observations in its local window.
        #
        # Calculate only where a full window is available.
        # --------------------------------------------------

        kernel = np.ones(window_len) / window_len

        ma_valid = np.convolve(
            y_noisy,
            kernel,
            mode="valid"
        )

        y_moving_avg = np.full(n, np.nan)

        y_moving_avg[
            first_idx : last_idx + 1
        ] = ma_valid

        # --------------------------------------------------
        # 3. Axes and labels
        # --------------------------------------------------

        title = Text(
            "Moving average smoothing: moving constant fit",
            font_size=30,
            color=DARK,
            weight=BOLD
        ).to_edge(UP, buff=0.25)

        axes = Axes(
            x_range=[0, 10, 2],
            y_range=[-0.8, 4.2, 1],
            x_length=11.2,
            y_length=5.1,
            tips=False,
            axis_config={
                "color": MUTED,
                "stroke_width": 2
            }
        ).shift(DOWN * 0.35)

        x_label = Text(
            "Time / position (x)",
            font_size=23,
            color=MUTED
        ).next_to(
            axes, DOWN, buff=0.25
        )

        y_label = Text(
            "Amplitude",
            font_size=23,
            color=MUTED
        ).rotate(PI / 2).next_to(
            axes, LEFT, buff=0.30
        )

        self.add(title, axes, x_label, y_label)

        # --------------------------------------------------
        # 4. Static noisy observations
        #
        # Ordinary Dot objects rather than DotCloud.
        # --------------------------------------------------

        dots = VGroup(
            *[
                Dot(
                    point=axes.c2p(x, y),
                    radius=0.035,
                    color=BLUE_DOTS,
                    fill_opacity=0.65,
                    stroke_width=0
                )
                for x, y in zip(x_data, y_noisy)
            ]
        ).set_z_index(3)

        self.play(
            FadeIn(dots),
            run_time=1.5
        )

        self.wait(0.8)

        # --------------------------------------------------
        # 5. Moving window tracker
        # --------------------------------------------------

        progress = ValueTracker(float(first_idx))

        def current_idx():
            return int(
                np.clip(
                    np.rint(progress.get_value()),
                    first_idx,
                    last_idx
                )
            )

        window_width = (
            axes.x_length
            * (x_data[2 * half_win] - x_data[0])
            / (x_data[-1] - x_data[0])
        )

        y_middle = (-0.8 + 4.2) / 2

        # --------------------------------------------------
        # 6. Shaded moving window
        # --------------------------------------------------

        def make_window():

            i = current_idx()

            return Rectangle(
                width=window_width,
                height=axes.y_length,
                fill_color=MUTED,
                fill_opacity=0.12,
                stroke_color=MUTED,
                stroke_width=1.5,
                stroke_opacity=0.65
            ).move_to(
                axes.c2p(x_data[i], y_middle)
            ).set_z_index(0)

        moving_window = always_redraw(make_window)

        # --------------------------------------------------
        # 7. Orange local constant fit
        #
        # Unlike Savitzky-Golay, this is a horizontal
        # line at the mean of the observations inside
        # the current window.
        # --------------------------------------------------

        def make_local_fit():

            i = current_idx()

            x_left = x_data[i - half_win]
            x_right = x_data[i + half_win]

            local_mean = y_moving_avg[i]

            return Line(
                axes.c2p(x_left, local_mean),
                axes.c2p(x_right, local_mean),
                color=ORANGE_FIT,
                stroke_width=4
            ).set_z_index(4)

        local_fit = always_redraw(make_local_fit)

        # --------------------------------------------------
        # 8. Purple moving-average trail
        #
        # Reveal the calculated window means from left
        # to right. No accumulation of duplicate points.
        # --------------------------------------------------

        def make_smooth_trail():

            i = current_idx()

            points = [
                axes.c2p(
                    x_data[j],
                    y_moving_avg[j]
                )
                for j in range(first_idx, i + 1)
            ]

            if len(points) == 1:
                points.append(points[0].copy())

            return VMobject(
                color=PURPLE_SMOOTH,
                stroke_width=4.5
            ).set_points_as_corners(
                points
            ).set_z_index(5)

        smooth_trail = always_redraw(make_smooth_trail)

        # --------------------------------------------------
        # 9. Red center marker
        #
        # The center estimate is exactly the mean
        # of the observations in the current window.
        # --------------------------------------------------

        marker = VGroup(
            Line(
                0.11 * (DOWN + LEFT),
                0.11 * (UP + RIGHT),
                color=RED_CENTER,
                stroke_width=4
            ),
            Line(
                0.11 * (UP + LEFT),
                0.11 * (DOWN + RIGHT),
                color=RED_CENTER,
                stroke_width=4
            )
        ).set_z_index(6)

        marker.move_to(
            axes.c2p(
                x_data[first_idx],
                y_moving_avg[first_idx]
            )
        )

        marker.add_updater(
            lambda m: m.move_to(
                axes.c2p(
                    x_data[current_idx()],
                    y_moving_avg[current_idx()]
                )
            )
        )

        # --------------------------------------------------
        # 10. Animate from left to right
        # --------------------------------------------------

        self.add(
            moving_window,
            local_fit,
            smooth_trail,
            marker
        )

        self.play(
            progress.animate.set_value(last_idx),
            run_time=18,
            rate_func=linear
        )

        marker.clear_updaters()

        self.wait(1)

        # --------------------------------------------------
        # 11. Final label
        # --------------------------------------------------

        final_label = Text(
            "Centered moving average (31 points)",
            font_size=23,
            color=PURPLE_SMOOTH,
            weight=BOLD
        ).next_to(
            axes, UP, buff=0.08
        ).align_to(axes, RIGHT)

        self.play(
            FadeIn(final_label),
            run_time=0.8
        )

        self.wait(2)

class SavitzkyGolayMovingWindow(Scene):
    def construct(self):

        self.camera.background_color = WHITE

        # --------------------------------------------------
        # 1. Generate synthetic signal
        # --------------------------------------------------

        rng = np.random.default_rng(101)

        n = 120
        x_data = np.linspace(0, 10, n)

        y_true = (
            np.sin(x_data)
            + 0.5 * np.cos(2 * x_data)
            + 0.3 * x_data
        )

        y_noisy = y_true + rng.normal(
            0, 0.25, size=n
        )

        window_len = 31
        half_win = window_len // 2
        poly_order = 3

        # Savitzky-Golay smoothed values
        y_smooth = savgol_filter(
            y_noisy,
            window_length=window_len,
            polyorder=poly_order,
            mode="interp"
        )

        # Only show centers with a complete symmetric window
        first_idx = half_win
        last_idx = n - half_win - 1

        # Precompute local polynomial coefficients
        # Center the x coordinates for numerical stability
        coefficients = {}

        for i in range(first_idx, last_idx + 1):

            xw = x_data[
                i - half_win : i + half_win + 1
            ] - x_data[i]

            yw = y_noisy[
                i - half_win : i + half_win + 1
            ]

            coefficients[i] = np.polyfit(
                xw, yw, deg=poly_order
            )

        # Confirm local cubic estimates match SG values
        assert all(
            np.isclose(
                np.polyval(coefficients[i], 0),
                y_smooth[i],
                atol=1e-9
            )
            for i in range(first_idx, last_idx + 1)
        )

        # --------------------------------------------------
        # 2. Axes and labels
        # --------------------------------------------------

        title = Text(
            "Savitzky-Golay smoothing: moving cubic fit",
            font_size=30,
            color=DARK,
            weight=BOLD
        ).to_edge(UP, buff=0.25)

        axes = Axes(
            x_range=[0, 10, 2],
            y_range=[-0.8, 4.2, 1],
            x_length=11.2,
            y_length=5.1,
            tips=False,
            axis_config={
                "color": MUTED,
                "stroke_width": 2
            }
        ).shift(DOWN * 0.35)

        x_label = Text(
            "Time / position (x)",
            font_size=23,
            color=MUTED
        ).next_to(axes, DOWN, buff=0.25)

        y_label = Text(
            "Amplitude",
            font_size=23,
            color=MUTED
        ).rotate(PI / 2).next_to(
            axes, LEFT, buff=0.30
        )

        self.add(title, axes, x_label, y_label)

        # --------------------------------------------------
        # 3. Noisy observations
        #
        # Use VGroup(Dot) instead of DotCloud.
        # Compatible with standard Cairo rendering.
        # --------------------------------------------------

        dots = VGroup(
            *[
                Dot(
                    point=axes.c2p(x, y),
                    radius=0.035,
                    color=BLUE_DOTS,
                    fill_opacity=0.65,
                    stroke_width=0
                )
                for x, y in zip(x_data, y_noisy)
            ]
        ).set_z_index(3)

        self.play(
            FadeIn(dots),
            run_time=1.5
        )
        self.wait(0.8)

        # --------------------------------------------------
        # 4. Moving window tracker
        # --------------------------------------------------

        progress = ValueTracker(float(first_idx))

        def current_idx():
            return int(
                np.clip(
                    np.rint(progress.get_value()),
                    first_idx,
                    last_idx
                )
            )

        # Window spans exactly 31 sample positions
        window_width = (
            axes.x_length
            * (x_data[2 * half_win] - x_data[0])
            / (x_data[-1] - x_data[0])
        )

        y_middle = (-0.8 + 4.2) / 2

        # --------------------------------------------------
        # 5. Shaded moving window
        # --------------------------------------------------

        def make_window():

            i = current_idx()

            return Rectangle(
                width=window_width,
                height=axes.y_length,
                fill_color=MUTED,
                fill_opacity=0.12,
                stroke_color=MUTED,
                stroke_width=1.5,
                stroke_opacity=0.65
            ).move_to(
                axes.c2p(x_data[i], y_middle)
            ).set_z_index(0)

        moving_window = always_redraw(make_window)

        # --------------------------------------------------
        # 6. Orange local cubic regression
        # --------------------------------------------------

        def make_local_fit():

            i = current_idx()

            x_local = np.linspace(
                x_data[i - half_win],
                x_data[i + half_win],
                80
            )

            # Evaluate cubic in centered coordinates
            y_local = np.polyval(
                coefficients[i],
                x_local - x_data[i]
            )

            points = [
                axes.c2p(x, y)
                for x, y in zip(x_local, y_local)
            ]

            return VMobject(
                color=ORANGE_FIT,
                stroke_width=3.5
            ).set_points_as_corners(
                points
            ).set_z_index(4)

        local_fit = always_redraw(make_local_fit)

        # --------------------------------------------------
        # 7. Purple permanent smoothing trail
        #
        # Reveal all calculated SG estimates up to
        # the current center, without adding duplicate
        # points on each rendered frame.
        # --------------------------------------------------

        def make_smooth_trail():

            i = current_idx()

            points = [
                axes.c2p(x_data[j], y_smooth[j])
                for j in range(first_idx, i + 1)
            ]

            # VMobject needs at least two points
            if len(points) == 1:
                points.append(points[0].copy())

            return VMobject(
                color=PURPLE_SMOOTH,
                stroke_width=4.5
            ).set_points_as_corners(
                points
            ).set_z_index(5)

        smooth_trail = always_redraw(make_smooth_trail)

        # --------------------------------------------------
        # 8. Red center marker (X)
        #
        # Small geometric cross: avoids recreating Text
        # or MathTex on every animation frame.
        # --------------------------------------------------

        marker = VGroup(
            Line(
                0.11 * (DOWN + LEFT),
                0.11 * (UP + RIGHT),
                color=RED_CENTER,
                stroke_width=4
            ),
            Line(
                0.11 * (UP + LEFT),
                0.11 * (DOWN + RIGHT),
                color=RED_CENTER,
                stroke_width=4
            )
        ).set_z_index(6)

        marker.move_to(
            axes.c2p(
                x_data[first_idx],
                y_smooth[first_idx]
            )
        )

        marker.add_updater(
            lambda m: m.move_to(
                axes.c2p(
                    x_data[current_idx()],
                    y_smooth[current_idx()]
                )
            )
        )

        # --------------------------------------------------
        # 9. Animate left to right
        # --------------------------------------------------

        self.add(
            moving_window,
            local_fit,
            smooth_trail,
            marker
        )

        self.play(
            progress.animate.set_value(last_idx),
            run_time=18,
            rate_func=linear
        )

        marker.clear_updaters()

        self.wait(1)

        # --------------------------------------------------
        # 10. Final label
        # --------------------------------------------------

        final_label = Text(
            "Savitzky-Golay smoothed signal",
            font_size=23,
            color=PURPLE_SMOOTH,
            weight=BOLD
        ).next_to(
            axes, UP, buff=0.08
        ).align_to(axes, RIGHT)

        self.play(
            FadeIn(final_label),
            run_time=0.8
        )

        self.wait(2)

BLUE_DOTS = "#2563eb"
PURPLE_SMOOTH = "#7c3aed"
MUTED = "#64748b"
DARK = "#1f2937"

class SmoothingSplineRegularization(Scene):
    def construct(self):

        self.camera.background_color = WHITE

        # --------------------------------------------------
        # 1. Same synthetic signal as the previous animations
        # --------------------------------------------------

        rng = np.random.default_rng(101)

        n = 120
        x_data = np.linspace(0, 10, n)

        y_true = (
            np.sin(x_data)
            + 0.5 * np.cos(2 * x_data)
            + 0.3 * x_data
        )

        y_noisy = y_true + rng.normal(
            0, 0.25, size=n
        )

        # --------------------------------------------------
        # 2. Precompute smoothing splines
        #
        # Animate log10(lambda) from -5 to +2.
        # The fits are natural cubic smoothing splines.
        # --------------------------------------------------

        x_dense = np.linspace(0, 10, 450)

        log_lambdas = np.linspace(-5, 2, 85)

        curves = np.array([
            make_smoothing_spline(
                x_data,
                y_noisy,
                lam=10.0 ** loglam
            )(x_dense)
            for loglam in log_lambdas
        ])

        # --------------------------------------------------
        # 3. Axes and labels
        # --------------------------------------------------

        title = Text(
            "Smoothing spline: balancing fit and smoothness",
            font_size=30,
            color=DARK,
            weight=BOLD
        ).to_edge(UP, buff=0.25)

        axes = Axes(
            x_range=[0, 10, 2],
            y_range=[-0.8, 4.2, 1],
            x_length=11.2,
            y_length=5.1,
            tips=False,
            axis_config={
                "color": MUTED,
                "stroke_width": 2
            }
        ).shift(DOWN * 0.35)

        x_label = Text(
            "Time / position (x)",
            font_size=23,
            color=MUTED
        ).next_to(axes, DOWN, buff=0.25)

        y_label = Text(
            "Amplitude",
            font_size=23,
            color=MUTED
        ).rotate(PI / 2).next_to(
            axes, LEFT, buff=0.30
        )

        self.add(title, axes, x_label, y_label)

        # --------------------------------------------------
        # 4. Show noisy data
        # --------------------------------------------------

        dots = VGroup(*[
            Dot(
                point=axes.c2p(x, y),
                radius=0.035,
                color=BLUE_DOTS,
                fill_opacity=0.65,
                stroke_width=0
            )
            for x, y in zip(x_data, y_noisy)
        ]).set_z_index(3)

        self.play(
            FadeIn(dots),
            run_time=1.5
        )

        self.wait(0.8)

        # --------------------------------------------------
        # 5. Lambda tracker
        # --------------------------------------------------

        log_lambda = ValueTracker(-5.0)

        def current_curve():

            s = np.clip(
                log_lambda.get_value(),
                log_lambdas[0],
                log_lambdas[-1]
            )

            # Find adjacent precomputed splines
            j = np.searchsorted(
                log_lambdas, s, side="right"
            ) - 1

            j = int(np.clip(
                j, 0, len(log_lambdas) - 2
            ))

            # Interpolate between fits for smooth animation
            weight = (
                (s - log_lambdas[j]) /
                (log_lambdas[j + 1] - log_lambdas[j])
            )

            return (
                (1 - weight) * curves[j] +
                weight * curves[j + 1]
            )

        # --------------------------------------------------
        # 6. Fitted spline: globally changing purple curve
        # --------------------------------------------------

        def make_spline_curve():

            y_fit = current_curve()

            points = [
                axes.c2p(x, y)
                for x, y in zip(x_dense, y_fit)
            ]

            return VMobject(
                color=PURPLE_SMOOTH,
                stroke_width=4.5
            ).set_points_as_corners(
                points
            ).set_z_index(5)

        spline_curve = always_redraw(make_spline_curve)

        # --------------------------------------------------
        # 7. Display smoothing parameter
        # --------------------------------------------------

        lambda_text = Text(
            "log10(λ) =",
            font_size=23,
            color=PURPLE_SMOOTH,
            weight=BOLD
        ).next_to(
            axes, UP, buff=0.16
        ).align_to(axes, RIGHT).shift(LEFT * 0.8)

        lambda_number = DecimalNumber(
            -5.0,
            num_decimal_places=1,
            font_size=23,
            color=PURPLE_SMOOTH
        )

        lambda_number.add_updater(
            lambda m: m.set_value(
                log_lambda.get_value()
            ).next_to(
                lambda_text, RIGHT, buff=0.08
            )
        )

        def stage_label(message):
            return Text(
                message,
                font_size=20,
                color=MUTED
            ).next_to(
                axes, UP, buff=0.16
            ).align_to(axes, LEFT)

        status = stage_label(
            "Small λ: follows the noise"
        )

        self.add(
            lambda_text,
            lambda_number,
            status
        )

        self.play(
            FadeIn(spline_curve),
            run_time=1
        )

        self.wait(1)

        # --------------------------------------------------
        # 8. Increase lambda: flexible -> moderately smooth
        # --------------------------------------------------

        self.play(
            log_lambda.animate.set_value(-2),
            Transform(
                status,
                stage_label(
                    "Moderate λ: balanced smoothing"
                )
            ),
            run_time=5.5,
            rate_func=linear
        )

        self.wait(1.2)

        # --------------------------------------------------
        # 9. Increase lambda further: nearly linear
        # --------------------------------------------------

        self.play(
            log_lambda.animate.set_value(2),
            Transform(
                status,
                stage_label(
                    "Large λ: curvature strongly penalized"
                )
            ),
            run_time=6,
            rate_func=linear
        )

        self.wait(1.2)

        # --------------------------------------------------
        # 10. Return to moderately smoothed estimate
        # --------------------------------------------------

        self.play(
            log_lambda.animate.set_value(-2),
            Transform(
                status,
                stage_label(
                    "Balance between fidelity and smoothness"
                )
            ),
            run_time=4,
            rate_func=smooth
        )

        self.wait(2)

        lambda_number.clear_updaters()

class StationaryMarkov(Scene):
    def construct(self):
        P=np.array([[.91,.08,.01],[.06,.78,.16],[.05,.01,.94]])
        names=["Susceptible","Infected","Recovered"]
        colors=[OBS,WARN,EST]
        title=Text("Markov probabilities converge for this chain",font_size=32).to_edge(UP)
        self.add(title)
        vals=np.array([1.0,0,0]);rects=VGroup();numbers=VGroup()
        for j in range(3):
            lab=Text(names[j],font_size=24,color=colors[j]).move_to(LEFT*5+UP*(1.4-j*1.3))
            r=Rectangle(width=max(.002,vals[j]*5),height=.42,fill_color=colors[j],fill_opacity=.8,stroke_width=0).align_to(LEFT*2.1,LEFT).move_to(RIGHT*0.5+UP*(1.4-j*1.3),aligned_edge=LEFT)
            num=DecimalNumber(vals[j],num_decimal_places=3,font_size=25).move_to(RIGHT*5+UP*(1.4-j*1.3))
            self.add(lab);rects.add(r);numbers.add(num)
        self.add(rects,numbers)
        for step in range(1,26):
            vals=vals@P
            newR=VGroup();newN=VGroup()
            for j in range(3):
                newR.add(Rectangle(width=max(.002,vals[j]*5),height=.42,fill_color=colors[j],fill_opacity=.8,stroke_width=0).move_to(RIGHT*0.5+UP*(1.4-j*1.3),aligned_edge=LEFT))
                newN.add(DecimalNumber(vals[j],num_decimal_places=3,font_size=25).move_to(RIGHT*5+UP*(1.4-j*1.3)))
            self.play(Transform(rects,newR),Transform(numbers,newN),run_time=.20)
        self.wait(1)
