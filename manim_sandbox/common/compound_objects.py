from manim import *
from manim.typing import Vector3D
from manim.utils.color import ManimColor


class DotWithLocalGrid(VGroup):
    def __init__(
        self,
        color: ManimColor = BLUE,
        grid_size: float = 2,
        grid_spacing: float = 1,
        scale: float = 0.5,
        **kwargs,
    ):
        super().__init__(**kwargs)
        a_dot = Dot(color=color)
        a_grid = NumberPlane(
            x_range=(-grid_size, grid_size, grid_spacing),
            y_range=(-grid_size, grid_size, grid_spacing),
            background_line_style={"stroke_color": GREY, "stroke_width": 1},
        ).scale(scale)
        self.add(a_grid, a_dot)


class WallWithCrossHatching(VGroup):
    def __init__(
        self,
        start: Vector3D,
        end: Vector3D,
        color: ManimColor = WHITE,
        spacing: float = 0.3,
        hatch_length: float = 0.3,
        angle: float = PI / 4,
        **kwargs,
    ):
        super().__init__(**kwargs)
        wall = Line(start=start, end=end, color=color)
        hatch_lines = VGroup()
        wall_vector = np.array(end) - np.array(start)
        wall_length = np.linalg.norm(wall_vector)
        direction = wall_vector / wall_length
        num_hatches = int(wall_length / spacing)
        for i in range(num_hatches + 1):
            point = np.array(start) + direction * spacing * i
            hatch_offset = np.array(
                [
                    hatch_length * np.cos(angle + PI / 2),
                    hatch_length * np.sin(angle + PI / 2),
                    0,
                ]
            )
            hatch_lines.add(
                Line(
                    start=point,
                    end=point + hatch_offset,
                    stroke_width=1,
                    color=color,
                )
            )
        self.add(wall, hatch_lines)


class TwoOpposingWalls(VGroup):
    def __init__(
        self,
        first_midpoint: Vector3D,
        second_midpoint: Vector3D,
        wall_width: float,
        hatch_length: float,
        color: ManimColor = WHITE,
        angle: float = PI / 4,
        **kwargs,
    ):
        super().__init__(**kwargs)
        wall1_to_wall2 = second_midpoint - first_midpoint
        direction = wall1_to_wall2 / np.linalg.norm(wall1_to_wall2)
        perpendicular = np.array([-direction[1], direction[0], 0])
        half_wall = perpendicular * wall_width / 2
        start1 = first_midpoint + half_wall
        end1 = first_midpoint - half_wall
        wall1 = WallWithCrossHatching(
            start1, end1, color=color, hatch_length=hatch_length, angle=angle
        )
        start2 = second_midpoint + half_wall
        end2 = second_midpoint - half_wall
        wall2 = WallWithCrossHatching(
            start2,
            end2,
            color=color,
            hatch_length=hatch_length,
            angle=angle + PI,
        )
        self.add(wall1, wall2)


class AnalogClock(VGroup):
    def __init__(
        self, radius=0.5, color=BLUE, font_size=36, decimal_places=1, **kwargs
    ):
        super().__init__(**kwargs)
        self.radius = radius
        self.color = color
        self.accumulated_time = ValueTracker(0)

        # Circle to represent the clock face
        self.face = Circle(radius=self.radius, color=self.color)

        # Sector to represent the "pie slice"; starts with angle=0
        self.progress_indicator = Sector(
            outer_radius=self.radius,
            inner_radius=self.radius * 0.9,
            angle=0,
            start_angle=PI / 2,
            color=YELLOW,
            fill_opacity=0.7,
        )
        # Use only one updater
        self.add_updater(self.update_progress_indicator)

        # Show current tick progress as a decimal in the center
        self.value_display = DecimalNumber(
            0, num_decimal_places=decimal_places, color=WHITE, font_size=font_size
        ).move_to(self.face.get_center())
        # This updates the text to the current accumulated_time
        self.value_display.add_updater(
            lambda m: m.set_value(self.accumulated_time.get_value())
        )

        # Add components to the AnalogClock
        self.add(self.face, self.progress_indicator, self.value_display)

    def tick_progress(self):
        return self.accumulated_time.get_value() % 1

    def update_progress_indicator(self, clock, dt):
        # Update the sector geometry based on tick progress, ticking clockwise
        angle = -self.tick_progress() * TAU  # negative for clockwise
        new_sector = Sector(
            outer_radius=self.radius,
            inner_radius=self.radius * 0.9,
            angle=angle,
            start_angle=PI / 2,
            color=YELLOW,
            fill_opacity=0.7,
        )
        new_sector.move_arc_center_to(self.get_center())
        # Replace the old sector geometry
        self.progress_indicator.become(new_sector)
