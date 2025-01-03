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
        label1 = Text("Astronaut's POV", color=RED, font_size=24).next_to(astronaut_grid, UP, buff=0.5)
        self.play(
            Create(astronaut_grid),
            Write(label1),
        )

        astronomer_grid = NumberPlane(
            x_range=[0, 10, 1],
            x_axis_config={"stroke_color": BLUE},
            y_range=[0, config.frame_height / 2, 1],
            y_axis_config={"stroke_color": BLUE},
            background_line_style={
                "stroke_color": BLUE_D,
                "stroke_width": 1,
                "stroke_opacity": 0.5,
            },
        ).shift(RIGHT * 2)
        label2 = Text("Astronomer's POV", color=BLUE, font_size=24).next_to(astronomer_grid, UP, buff=0.5)
        self.play(
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
        left_right_displacement = 1.0
        clock_speed = left_right_displacement / play_time

        astronaut_delta_t = tick_progress
        light_speed = (tick_progress * CLOCK_HEIGHT * 2) / play_time
        astronomer_delta_t = astronaut_delta_t * np.sqrt(
            1 - (clock_speed**2) / (light_speed**2)
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
        self.wait(2)

        # Point out that the speed of the photon in the moving clock is the
        # same, but the clock has "ticked" slower because the photon had to move
        # more distance in this reference frame.

        # Fade everything out to reset the scene for a loop
        self.play(
            FadeOut(astronaut_grid),
            FadeOut(astronomer_grid),
            FadeOut(label1),
            FadeOut(label2),
            FadeOut(astronaut_clock.walls),
            FadeOut(astronomer_view_clock.walls),
            FadeOut(astronaut_clock.photon),
            FadeOut(astronomer_view_clock.photon),
            FadeOut(astronaut_clock.indicator),
            FadeOut(astronomer_view_clock.indicator),
            FadeOut(astronaut_clock.indicator.progress_indicator),
            FadeOut(astronomer_view_clock.indicator.progress_indicator),
            FadeOut(astronaut_clock.photon.trace),
            FadeOut(astronomer_view_clock.photon.trace),
        )
        # # Briefly highlight that the diagonal is the same length
        # # as the stationary clock's vertical half.
        # # (Optionally add a small label)
        # label_hypo = Text("Same length!", font_size=24).next_to(
        #     moving_diagonal, UR
        # )
        # self.play(
        #     Write(label_hypo),
        #     Wait(1),
        #     FadeOut(label_hypo),
        # )
        # self.play(Create(component_vertical), Create(component_horizontal))
        # self.wait(2)

        # # Remove these component lines before proceeding
        # self.play(
        #     FadeOut(moving_diagonal),
        #     FadeOut(stationary_vertical),
        #     FadeOut(component_vertical),
        #     FadeOut(component_horizontal),
        #     FadeOut(label_hypo),
        # )

        # # 2) Continue from midpoint to complete the cycle (the second half)
        # stationary_second_half = VMobject().set_points_as_corners(
        #     [stationary_midpoint, stationary_path[1], stationary_path[2]]
        # )
        # moving_second_half = VMobject().set_points_as_corners(
        #     [moving_midpoint, moving_path[1], moving_path[2]]
        # )

        # # The second half reuses the remaining run times
        # self.play(
        #     AnimationGroup(
        #         MoveAlongPath(
        #             stationary_photon,
        #             stationary_second_half,
        #             rate_func=linear,
        #             run_time=BASE_TIME - half_time,
        #         ),
        #         AnimationGroup(
        #             MoveAlongPath(
        #                 moving_photon,
        #                 moving_second_half,
        #                 rate_func=linear,
        #                 run_time=moving_time - half_time,
        #             ),
        #             moving_clock[0]
        #             .animate(rate_func=linear, run_time=moving_time - half_time)
        #             .shift(displacement),
        #         ),
        #     )
        # )

        # # Add length labels
        # length_labels = VGroup(
        #     MathTex("ct").next_to(path_demonstration[0], LEFT),
        #     MathTex("ct'").next_to(path_demonstration[1], LEFT),
        # )

        # # Show path length comparison
        # self.play(Create(path_demonstration), Write(length_labels))
