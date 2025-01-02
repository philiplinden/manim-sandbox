from manim import *
from manim.typing import Vector3D

from manim_sandbox.common.compound_objects import TwoOpposingWalls, AnalogClock


SPEED_OF_LIGHT = 1  # units per second


class Photon(Dot):
    speed: float = SPEED_OF_LIGHT
    trace: TracedPath

    def __init__(self, position: Vector3D, direction: Vector3D, *args, **kwargs):
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
            np.linalg.norm(points[i] - points[i - 1]) for i in range(1, len(points))
        )

    def clear_trace(self):
        self.trace.clear_points()


class LightClock(VGroup):
    walls: VGroup
    photon: Photon
    label: Text | None = None
    proper_time = ValueTracker(0)
    tick_progress: float = 0
    velocity = ValueTracker(0)
    elements: list[VMobject | VGroup] = []

    def __init__(
        self,
        *args,
        initial_position=ORIGIN,
        height=4,
        wall_width=1,
        hatch_length=0.3,
        title=None,
        color=WHITE,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self.add_updater(self.update_tick_progress)

        position = initial_position
        # Create walls using the provided function
        self.walls = TwoOpposingWalls(
            first_midpoint=position + UP * height / 2,
            second_midpoint=position + DOWN * height / 2,
            wall_width=wall_width,
            hatch_length=hatch_length,
            color=color,
        )

        # Create photon
        self.photon = Photon(position=self.photon_position(), direction=UP, color=YELLOW)

        # Create label
        if title:
            self.label = (
                Text(title, font_size=24)
                .next_to(self.walls, UP)
                .add_updater(lambda m: m.next_to(self.walls, UP))
            )
        else:
            self.label = None

        self.elements = [
            e
            for e in [
                self.walls,
                self.photon,
                self.label,
            ]
            if e is not None
        ]

    def update_tick_progress(self):
        self.tick_progress = self.proper_time.get_value() % 1
        self.photon.move_to(self.photon_position())

    def photon_position(self):
        progress = self.tick_progress
        start = self.walls[1][0].get_center()
        end = self.walls[0][0].get_center()
        if progress < 0.5:
            return interpolate(start, end, progress)
        else:
            return interpolate(end, start, progress)

    def add_to_scene(self, scene: Scene):
        scene.add(self.clock_and_trace())

    def clock_elements(self):
        return VGroup(*self.elements)

    def clock_and_trace(self):
        return VGroup(*self.elements, self.photon.trace)

    def show(self):
        return Create(self.clock_elements())

    def shift(self, shift: Vector3D):
        return ApplyMethod(self.clock_elements().shift, shift)

    def shift_clock_and_trace(self, shift: Vector3D):
        return ApplyMethod(self.clock_and_trace().shift, shift)

    def move_to(self, position: Vector3D):
        return ApplyMethod(self.clock_elements().move_to, position)

    def move_clock_and_trace_to(self, position: Vector3D):
        return ApplyMethod(self.clock_and_trace().move_to, position)


class TimeDilationDemo(Scene):
    def construct(self):
        # Constants
        CLOCK_HEIGHT = 4
        WALL_WIDTH = 1

        # Create stationary clock
        stationary_clock = LightClock(
            initial_position=LEFT * 4,
            height=CLOCK_HEIGHT,
            wall_width=WALL_WIDTH,
            title="Stationary Clock",
            color=BLUE,
        )
        stationary_clock.add_to_scene(self)

        # Create moving clock
        moving_clock = LightClock(
            initial_position=LEFT * 1,
            height=CLOCK_HEIGHT,
            wall_width=WALL_WIDTH,
            title="Moving Clock",
            color=RED,
        )
        moving_clock.add_to_scene(self)

        self.play(
            stationary_clock.show(),
            moving_clock.show(),
        )
        
        
        stationary_analog_clock = AnalogClock(color=BLUE).next_to(
            stationary_clock.walls[1][0], DOWN
        )
        moving_analog_clock = AnalogClock(color=RED).next_to(
            moving_clock.walls[1][0], DOWN
        )
        self.play(
            Create(stationary_analog_clock),
            Create(moving_analog_clock),
        )
        self.wait(1)
        self.play(stationary_analog_clock.accumulated_time.animate.set_value(5), run_time=5, rate_func=linear)

        # moving_diagonal = Line(moving_path[0], moving_stop_point, color=RED)
        # stationary_vertical = Line(
        #     stationary_path[0], stationary_stop_point, color=RED
        # )
        # # Vertical line from bottom to same y as midpoint
        # component_vertical = DashedLine(
        #     moving_path[0],
        #     [moving_path[0][0], moving_stop_point[1], 0],
        #     color=BLUE,
        # )
        # # Horizontal line from that vertical line to the midpoint
        # component_horizontal = DashedLine(
        #     [moving_path[0][0], moving_stop_point[1], 0],
        #     moving_stop_point,
        #     color=BLUE,
        # )

        # # Create them in the scene
        # self.play(
        #     Create(moving_diagonal),
        #     Create(stationary_vertical),
        #     # Start Generation Here
        #     Create(Brace(moving_diagonal, LEFT)),
        #     Write(
        #         MathTex(f"{moving_diagonal.get_length():.2f}").next_to(
        #             Brace(
        #                 moving_diagonal,
        #                 moving_diagonal.copy().rotate(PI / 2).get_unit_vector(),
        #             ),
        #             RIGHT,
        #         )
        #     ),
        #     Create(Brace(stationary_vertical, LEFT)),
        #     Write(
        #         MathTex(f"{stationary_vertical.get_length():.2f}").next_to(
        #             Brace(stationary_vertical, LEFT), LEFT
        #         )
        #     ),
        # )

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
