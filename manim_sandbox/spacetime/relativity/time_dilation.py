from manim import *
from manim.typing import Vector3D

from manim_sandbox.common.compound_objects import TwoOpposingWalls, AnalogClock


class Photon(Dot):
    def __init__(
        self, position: Vector3D, direction: Vector3D, *args, **kwargs
    ):
        super().__init__(*args, **kwargs)
        self.move_to(position)
        self.direction = direction
        # Create path tracker
        self.trace = TracedPath(
            self.get_center,
            stroke_width=2,
            stroke_color=YELLOW,
            stroke_opacity=0.7,
        )

    def get_distance_traveled(self):
        points = self.trace.get_points()
        return sum(
            np.linalg.norm(points[i] - points[i - 1])
            for i in range(1, len(points))
        )

    def clear_trace(self):
        self.trace.clear_points()


class LightClock(VGroup):
    def __init__(
        self,
        *args,
        initial_position=ORIGIN,
        height=4,
        wall_width=1,
        hatch_length=0.3,
        color=WHITE,
        symbol="\\tau",
        use_symbol_for_value=True,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.proper_time = ValueTracker(0)
        self.initial_position = initial_position
        position = initial_position
        # Create walls using the provided function
        self.walls = TwoOpposingWalls(
            first_midpoint=position + UP * height / 2,
            second_midpoint=position + DOWN * height / 2,
            wall_width=wall_width,
            hatch_length=hatch_length,
            color=color,
        )
        self.wall_separation_distance = np.linalg.norm(
            x=self.walls[0][0].get_bottom() - self.walls[1][0].get_top()
        )
        self.photon = Photon(
            position=self.photon_position(0), direction=UP, color=YELLOW
        ).add_updater(
            update_function=lambda m: m.move_to(
                self.photon_position(self.proper_time.get_value())
            )
        )
        self.indicator = (
            AnalogClock(color=color, decimal_places=2, symbol=symbol, use_symbol_for_value=use_symbol_for_value)
            .next_to(self.walls[1][0], DOWN)
            .add_updater(self.update_indicator)
        )

        # Include the walls, photon, indicator, and trace in self.elements
        self.add(
            *[
                e
                for e in [
                    self.walls,
                    self.indicator,
                    self.photon,
                    self.photon.trace,
                ]
                if e is not None
            ]
        )

    def photon_position(self, proper_time: float):
        # Use a repeating bounce rather than resetting at each integer time:
        period = 0.5
        cycles = int(proper_time // period)
        remainder = (proper_time % period) / period
        start = self.walls[1][0].get_center()
        end = self.walls[0][0].get_center()

        if cycles % 2 == 0:
            return interpolate(start, end, remainder)
        else:
            return interpolate(end, start, remainder)

    def update_indicator(self, mobj):
        proper_time = self.proper_time.get_value()
        mobj.accumulated_time.set_value(proper_time)
        mobj.next_to(self.walls[1][0], DOWN)


class TimeDilationDemo(Scene):
    def construct(self):
        CLOCK_HEIGHT = 4
        WALL_WIDTH = 1
        ASTRONAUT_SPEED = 0.5

        # Make a grid for each reference frame
        astronaut_grid = NumberPlane(
            x_range=[-1, 1, 1],
            x_axis_config={"stroke_color": RED},
            y_range=[0, config.frame_height / 2, 1],
            y_axis_config={"stroke_color": RED},
            background_line_style={
                "stroke_color": RED_D,
                "stroke_width": 1,
                "stroke_opacity": 0.5,
            },
        ).shift(LEFT * 5)
        astronaut_pov_label = Text(
            "Astronaut's POV", color=RED, font_size=24
        ).next_to(astronaut_grid, UP, buff=0.5)

        astronomer_grid = NumberPlane(
            x_range=[0, 6, 1],
            x_axis_config={"stroke_color": BLUE},
            y_range=[0, config.frame_height / 2, 1],
            y_axis_config={"stroke_color": BLUE},
            background_line_style={
                "stroke_color": BLUE_D,
                "stroke_width": 1,
                "stroke_opacity": 0.5,
            },
        )
        astronomer_pov_label = Text(
            "Astronomer's POV", color=BLUE, font_size=24
        ).next_to(astronomer_grid, UP, buff=0.5)

        self.play(
            Create(astronaut_grid),
            Write(astronaut_pov_label),
            Create(astronomer_grid),
            Write(astronomer_pov_label),
        )

        # Create astronaut POV clock
        astronaut_clock = LightClock(
            initial_position=LEFT * 5,
            height=CLOCK_HEIGHT,
            wall_width=WALL_WIDTH,
            color=RED,
            symbol="\\Delta \\tau",
            use_symbol_for_value=True,
        )

        # Create astronomer-view clock
        astronomer_view_clock = LightClock(
            initial_position=LEFT * 3,
            height=CLOCK_HEIGHT,
            wall_width=WALL_WIDTH,
            color=BLUE,
            symbol="\\Delta t",
            use_symbol_for_value=True,
        )

        self.add(astronaut_clock, astronomer_view_clock)
        self.play(
            Create(astronomer_view_clock),
            Create(astronaut_clock),
        )

        # stash some geometry for later
        a1 = astronaut_clock.walls[1][0].get_center()
        a2 = astronaut_clock.walls[0][0].get_center()
        b1 = astronomer_view_clock.walls[0][0].get_center()
        c1 = astronomer_view_clock.walls[1][0].get_center()

        # Play the tick progress in segments to ensure we don't skip any frames
        # and end up dropping points in the photon path trace
        play_time = 2.0
        left_right_displacement = ASTRONAUT_SPEED * play_time

        astronaut_delta_t = 0.25
        light_speed = (astronaut_delta_t * CLOCK_HEIGHT * 2) / play_time
        lorentz_factor = np.sqrt(1 - (ASTRONAUT_SPEED**2) / (light_speed**2))
        astronomer_delta_t = astronaut_delta_t * lorentz_factor
        self.play(
            astronaut_clock.proper_time.animate.set_value(astronaut_delta_t),
            astronomer_view_clock.proper_time.animate.set_value(
                astronomer_delta_t
            ),
            astronomer_view_clock.walls.animate.shift(
                RIGHT * left_right_displacement
            ),
            run_time=play_time,
            rate_func=linear,
        )

        # Point out that the speed of the photon in the moving clock is the
        # same, but the clock has "ticked" slower because the photon had to move
        # more distance in this reference frame.
        # Create braces for each photon's traced path
        astronaut_brace = Brace(astronaut_clock.photon.trace, LEFT)
        astronaut_length = MathTex("c \\Delta \\tau").next_to(astronaut_brace, LEFT)

        path_vector = LEFT * left_right_displacement + UP * (astronomer_delta_t)
        path_vector = path_vector / np.linalg.norm(path_vector)
        astronomer_brace = BraceBetweenPoints(
            astronomer_view_clock.photon.trace.get_points()[0],
            astronomer_view_clock.photon.trace.get_points()[-1],
        )
        astronomer_length = (
            MathTex("c \\Delta t")
            .next_to(astronomer_view_clock.photon.trace, RIGHT)
            .shift(DOWN * 0.3 + LEFT * 0.1)
        )
        v_brace = Brace(astronomer_view_clock.photon.trace, UP)
        v_component_label = MathTex("v \\Delta t").next_to(
            v_brace, UP, buff=0.1
        )

        self.play(
            Create(astronaut_brace),
            FadeIn(astronaut_length),
            Create(astronomer_brace),
            FadeIn(astronomer_length),
            Create(v_brace),
            FadeIn(v_component_label),
        )
        self.wait(1)

        # fade out the components and the braces
        self.play(
            FadeOut(astronaut_brace),
            FadeOut(astronaut_length),
            FadeOut(astronomer_brace),
            FadeOut(astronomer_length),
            FadeOut(v_brace),
            FadeOut(v_component_label),
        )

        # animate until the astronaut sees the bounce
        play_time = 2.0
        left_right_displacement = ASTRONAUT_SPEED * play_time

        astronaut_delta_t = 0.5
        astronomer_delta_t = astronaut_delta_t * lorentz_factor
        time_difference = astronomer_delta_t - astronaut_delta_t
        # Animate astronaut tick progress from ~1/4 to 1/2
        self.play(
            astronaut_clock.proper_time.animate.set_value(astronaut_delta_t),
            astronomer_view_clock.proper_time.animate.set_value(
                astronomer_delta_t
            ),
            astronomer_view_clock.walls.animate.shift(
                RIGHT * left_right_displacement
            ),
            rate_func=linear,
            run_time=play_time,
        )

        # Animate until the astronomer sees the bounce to make sure we capture
        # that point in the path trace too
        play_time = 0.5 - time_difference
        astronomer_delta_t = 0.5
        astronaut_delta_t = astronomer_delta_t / lorentz_factor
        time_difference = astronomer_delta_t - astronaut_delta_t
        left_right_displacement = ASTRONAUT_SPEED * play_time
        self.play(
            astronaut_clock.proper_time.animate.set_value(astronaut_delta_t),
            astronomer_view_clock.proper_time.animate.set_value(
                astronomer_delta_t
            ),
            astronomer_view_clock.walls.animate.shift(
                RIGHT * left_right_displacement
            ),
            rate_func=linear,
            run_time=play_time,
        )
        b2 = astronomer_view_clock.photon.get_center()
        c2 = b2.copy()

        # Now continue from 1/2 to 1.0
        play_time = 4.0 - time_difference
        left_right_displacement = ASTRONAUT_SPEED * play_time

        astronaut_delta_t = 1.0
        astronomer_delta_t = astronaut_delta_t * np.sqrt(
            1 - (ASTRONAUT_SPEED**2) / (light_speed**2)
        )

        self.play(
            astronaut_clock.proper_time.animate.set_value(astronaut_delta_t),
            astronomer_view_clock.proper_time.animate.set_value(
                astronomer_delta_t
            ),
            astronomer_view_clock.walls.animate.shift(
                RIGHT * left_right_displacement
            ),
            rate_func=linear,
            run_time=play_time,
        )
        self.wait(1)
        self.play(
            FadeOut(astronaut_pov_label),
            FadeOut(astronomer_pov_label),
        )

        # fade out clock and walls and make it a trig/geometry problem
        # derive lorentz factor from the geometry
        side_a = Line(a1, a2, color=RED)
        side_a_label = MathTex("c \\Delta \\tau").next_to(side_a, LEFT)
        side_b = Line(b1, b2, color=GREEN)
        side_b_label = MathTex("v \\Delta t").next_to(side_b, UP)
        side_c = Line(c1, c2, color=BLUE)
        side_c_label = (
            MathTex("c \\Delta t").next_to(side_c, RIGHT).shift(LEFT)
        )
        self.play(
            Create(side_a),
            Write(side_a_label),
            Create(side_b),
            Write(side_b_label),
            Create(side_c),
            Write(side_c_label),
        )
        self.play(
            FadeOut(
                VGroup(
                    astronaut_grid,
                    astronomer_grid,
                    astronaut_clock.walls,
                    astronomer_view_clock.walls,
                    astronaut_clock.photon,
                    astronomer_view_clock.photon,
                    astronaut_clock.indicator,
                    astronomer_view_clock.indicator,
                    astronaut_clock.indicator.progress_indicator,
                    astronomer_view_clock.indicator.progress_indicator,
                    astronaut_clock.photon.trace,
                    astronomer_view_clock.photon.trace,
                )
            ),
        )
        self.play(VGroup(side_a, side_a_label).animate.shift(RIGHT * 2))

        pythagorean_theorem = MathTex(
            "(c \\Delta \\tau)^2 = (v \\Delta t)^2 + (c \\Delta t)^2",
            tex_to_color_map={
                "c \\Delta \\tau": BLUE,
                "v \\Delta t": GREEN,
                "c \\Delta t": RED,
            },
        ).to_edge(UP)

        self.play(
            TransformMatchingTex(side_a_label, pythagorean_theorem),
            TransformMatchingTex(side_b_label, pythagorean_theorem),
            TransformMatchingTex(side_c_label, pythagorean_theorem),
        )

        # Fade everything out except the derivation
        self.play(
            FadeOut(side_a),
            FadeOut(side_b),
            FadeOut(side_c),
            pythagorean_theorem.animate.set_color(WHITE),
        )
        self.wait(1)

        # remind the audience what's what
        derivation_step_1a = MathTex(
            "(c \\Delta t)^2 = (v \\Delta t)^2 + (c \\Delta \\tau)^2",
            tex_to_color_map={"\\Delta \\tau": RED},
        ).to_edge(UP)
        explanation1 = (
            VGroup(
                MathTex("\\Delta \\tau", color=RED),
                Text("Elapsed clock time in Astronaut's reference frame").scale(
                    0.5
                ),
            )
            .arrange(RIGHT)
            .next_to(derivation_step_1a, DOWN)
        )

        derivation_step_1b = MathTex(
            "(c \\Delta t)^2 = (v \\Delta t)^2 + (c \\Delta \\tau)^2",
            tex_to_color_map={"\\Delta \\tau": RED, "\\Delta t": BLUE, },
        ).to_edge(UP)
        explanation2 = (
            VGroup(
                MathTex("\\Delta t", color=BLUE),
                Text(
                    "Elapsed clock time in Astronomer's reference frame"
                ).scale(0.5),
            )
            .arrange(RIGHT)
            .next_to(derivation_step_1b, DOWN)
        )

        derivation_step_1c = MathTex(
            "(c \\Delta t)^2 = (v \\Delta t)^2 + (c \\Delta \\tau)^2",
            tex_to_color_map={
                "\\Delta \\tau": RED,
                "\\Delta t": BLUE,
                "v": GREEN,
            },
        ).to_edge(UP)
        explanation3 = (
            VGroup(
                MathTex("v", color=GREEN),
                Text(
                    "Speed of the clock in the Astronomer's reference frame"
                ).scale(0.5),
            )
            .arrange(RIGHT)
            .next_to(derivation_step_1c, DOWN)
        )

        derivation_step_1d = MathTex(
            "(c \\Delta t)^2 = (v \\Delta t)^2 + (c \\Delta \\tau)^2",
            tex_to_color_map={
                "\\Delta \\tau": RED,
                "\\Delta t": BLUE,
                "v": GREEN,
                "c": YELLOW,
            },
        ).to_edge(UP)
        explanation4 = (
            VGroup(
                MathTex("c", color=YELLOW),
                Text("Speed of light in all reference frames").scale(
                    0.5
                ),
            )
            .arrange(RIGHT)
            .next_to(derivation_step_1c, DOWN)
        )

        self.play(
            TransformMatchingTex(pythagorean_theorem, derivation_step_1a),
            Write(explanation1),
        )
        self.play(explanation1.animate.shift(DOWN))
        self.play(
            TransformMatchingTex(derivation_step_1a, derivation_step_1b),
            Write(explanation2),
        )
        self.play(explanation2.animate.next_to(explanation1, DOWN))
        self.play(
            TransformMatchingTex(derivation_step_1b, derivation_step_1c),
            Write(explanation3),
        )
        self.play(explanation3.animate.next_to(explanation2, DOWN))
        self.play(
            TransformMatchingTex(derivation_step_1c, derivation_step_1d),
            Write(explanation4),
        )
        self.play(explanation4.animate.next_to(explanation3, DOWN))
        self.wait(1)
        self.play(
            FadeOut(explanation1),
            FadeOut(explanation2),
            FadeOut(explanation3),
            FadeOut(explanation4),
        )

        # go through the derivation step by step
        derivation_step_2 = MathTex(
            r"(c^2 \Delta t)^2 - (v \Delta t)^2 = (c \Delta \tau)^2",
            tex_to_color_map={
                "\\Delta \\tau": RED,
                "\\Delta t": BLUE,
                "v": GREEN,
                "c": YELLOW,
            },
        ).next_to(derivation_step_1d, DOWN)
        self.play(
            TransformMatchingTex(derivation_step_1d.copy(), derivation_step_2),
        )
        derivation_step_3 = MathTex(
            r"\\Delta t^2 (c^2 - v^2) = c^2 \\Delta \\tau^2",
            tex_to_color_map={
                "\\Delta \\tau": RED,
                "\\Delta t": BLUE,
                "v": GREEN,
                "c": YELLOW,
            },
        ).next_to(derivation_step_2, DOWN)
        self.play(
            TransformMatchingTex(derivation_step_2.copy(), derivation_step_3),
        )
        derivation_step_4 = MathTex(
            r"\Delta t^2 = (c^2 \Delta \\tau^2) / (c^2 - v^2)",
            tex_to_color_map={
                "\\Delta \\tau": RED,
                "\\Delta t": BLUE,
                "v": GREEN,
                "c": YELLOW,
            },
        ).next_to(derivation_step_3, DOWN)
        self.play(
            TransformMatchingTex(derivation_step_3.copy(), derivation_step_4),
        )
        derivation_step_5 = MathTex(
            r"\Delta t^2 = (c^2 \Delta \\tau^2) / c^2 (1 - (v/c)^2)",
            tex_to_color_map={
                "\\Delta \\tau": RED,
                "\\Delta t": BLUE,
                "v": GREEN,
                "c": YELLOW,
            },
        ).next_to(derivation_step_4, DOWN)
        self.play(
            TransformMatchingTex(derivation_step_4.copy(), derivation_step_5),
        )
        derivation_step_6 = MathTex(
            r"\Delta t = \Delta \\tau / \sqrt{1 - (v/c)^2}",
            tex_to_color_map={
                "\\Delta \\tau": RED,
                "\\Delta t": BLUE,
                "v": GREEN,
                "c": YELLOW,
            },
        ).next_to(derivation_step_5, DOWN)
        self.play(
            TransformMatchingTex(derivation_step_5.copy(), derivation_step_6),
        )
        self.wait(1)

        lorentz_factor_eq = MathTex(
            r"\Delta t = \gamma \Delta \\tau \quad \gamma = (\sqrt{1 - (v/c)^2})^{-1}",
            tex_to_color_map={
                "\\Delta \\tau": RED,
                "\\Delta t": BLUE,
                "v": GREEN,
                "c": YELLOW,
                "\\gamma": LIGHT_PINK,
            },
        ).next_to(derivation_step_6, DOWN, buff=SMALL_BUFF)
        self.play(TransformMatchingTex(derivation_step_6, lorentz_factor_eq))
        self.wait(1)
        explanation_lorentz_factor = Tex(
            "The Lorentz factor, $\\gamma$, quantifies time dilation due to relative motion",
            font_size=32,
        ).next_to(lorentz_factor_eq, DOWN, buff=LARGE_BUFF)
        self.play(Write(explanation_lorentz_factor))
        self.wait(1)

        self.play(
            FadeOut(derivation_step_1d),
            FadeOut(derivation_step_2),
            FadeOut(derivation_step_3),
            FadeOut(derivation_step_4),
            FadeOut(derivation_step_5),
            FadeOut(explanation_lorentz_factor),
            lorentz_factor_eq.animate.to_edge(UP),
        )
        explanation_text = Tex(
            "In the astronomer's reference frame, the photon moves across more space over the course of one ``tick'' of the clock. The only way the speed of the photon, $c$, can be the same in all reference frames and yet travel across more distance in one reference frame than in another is if the elapsed time experienced by a moving object, $\\Delta \\tau$, ``dilates'' when observed from a reference frame at rest compared to the reference frame's proper time, $\Delta t$.",
            font_size=32,
            
        ).next_to(lorentz_factor_eq, DOWN, buff=LARGE_BUFF)

        self.play(Write(explanation_text), run_time=4)
        self.wait(2)
        self.play(FadeOut(lorentz_factor_eq), FadeOut(explanation_text))
