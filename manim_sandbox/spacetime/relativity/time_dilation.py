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
            AnalogClock(color=color, decimal_places=2)
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
        tick_progress = proper_time % 1
        bottom_to_top_progress = tick_progress / 0.5
        top_to_bottom_progress = (tick_progress - 0.5) / 0.5
        start = self.walls[1][0].get_center()
        end = self.walls[0][0].get_center()
        if tick_progress < 0.5:
            return interpolate(start, end, bottom_to_top_progress)
        else:
            return interpolate(end, start, top_to_bottom_progress)

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
        label1 = Text("Astronaut's POV", color=RED, font_size=24).next_to(
            astronaut_grid, UP, buff=0.5
        )

        astronomer_grid = NumberPlane(
            x_range=[0, 4, 1],
            x_axis_config={"stroke_color": BLUE},
            y_range=[0, config.frame_height / 2, 1],
            y_axis_config={"stroke_color": BLUE},
            background_line_style={
                "stroke_color": BLUE_D,
                "stroke_width": 1,
                "stroke_opacity": 0.5,
            },
        ).shift(LEFT)
        label2 = Text("Astronomer's POV", color=BLUE, font_size=24).next_to(
            astronomer_grid, UP, buff=0.5
        )

        self.play(
            Create(astronaut_grid),
            Write(label1),
            Create(astronomer_grid),
            Write(label2),
        )

        # Create astronaut POV clock
        astronaut_clock = LightClock(
            initial_position=LEFT * 5,
            height=CLOCK_HEIGHT,
            wall_width=WALL_WIDTH,
        )

        # Create astronomer-view clock
        astronomer_view_clock = LightClock(
            initial_position=LEFT * 3,
            height=CLOCK_HEIGHT,
            wall_width=WALL_WIDTH,
        )

        self.add(astronaut_clock, astronomer_view_clock)
        self.play(
            Create(astronomer_view_clock),
            Create(astronaut_clock),
        )

        # Progress coordinate time by 1/4 tick then pause
        tick_progress = 1 / 4

        play_time = 2.0
        left_right_displacement = ASTRONAUT_SPEED * play_time

        astronaut_delta_t = tick_progress
        light_speed = (tick_progress * CLOCK_HEIGHT * 2) / play_time
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
            run_time=play_time,
            rate_func=linear,
        )
        self.wait(1)

        # Point out that the speed of the photon in the moving clock is the
        # same, but the clock has "ticked" slower because the photon had to move
        # more distance in this reference frame.
        # Create braces for each photon's traced path
        astronaut_brace = Brace(astronaut_clock.photon.trace, LEFT)
        astronaut_length = MathTex("c \\Delta t").next_to(astronaut_brace, LEFT)

        path_vector = (
            LEFT * left_right_displacement + UP * (astronomer_delta_t)
        )
        path_vector = path_vector / np.linalg.norm(path_vector)
        astronomer_brace = BraceBetweenPoints(
            astronomer_view_clock.photon.trace.get_points()[0],
            astronomer_view_clock.photon.trace.get_points()[-1],
        )
        astronomer_length = MathTex("c \\Delta \\tau").next_to(astronomer_view_clock.photon.trace, RIGHT).shift(DOWN * 0.3 + LEFT * 0.1)
        v_brace = Brace(astronomer_view_clock.photon.trace, UP)
        v_component_label = MathTex("v \\Delta \\tau").next_to(v_brace, UP, buff=0.1)

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
        # play the rest of the animation until astronaut pov reaches 1.0
        
        # Progress coordinate time by 1/4 tick then pause
        tick_progress = 1

        play_time = 6.0
        left_right_displacement = ASTRONAUT_SPEED * play_time

        astronaut_delta_t = tick_progress
        light_speed = (tick_progress * CLOCK_HEIGHT * 2) / play_time
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
            run_time=play_time,
            rate_func=linear,
        )
        self.wait(1)

        # fade out clock and walls and make it a trig/geometry problem
        self.play(
            FadeOut(astronaut_clock.walls),
            FadeOut(astronomer_view_clock.walls),
            FadeOut(astronaut_clock.photon),
            FadeOut(astronomer_view_clock.photon),
            FadeOut(astronaut_clock.indicator),
            FadeOut(astronomer_view_clock.indicator),
            FadeOut(astronaut_clock.indicator.progress_indicator),
            FadeOut(astronomer_view_clock.indicator.progress_indicator),
        )
        
        # derive lorentz factor from the geometry
        
        # Fade everything out to reset the scene for a loop
        self.wait(1)
        self.play(
            FadeOut(astronaut_grid),
            FadeOut(astronomer_grid),
            FadeOut(label1),
            FadeOut(label2),
            FadeOut(astronaut_clock.photon.trace),
            FadeOut(astronomer_view_clock.photon.trace),
        )
