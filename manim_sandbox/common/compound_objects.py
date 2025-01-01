from manim import *
from manim.typing import Vector3D
from manim.utils.color import ManimColor


def dot_with_local_grid(
    color: ManimColor = BLUE,
    grid_size: float = 2,
    grid_spacing: float = 1,
    scale: float = 0.5,
):
    a_dot = Dot(color=color)
    a_grid = NumberPlane(
        x_range=(-grid_size, grid_size, grid_spacing),
        y_range=(-grid_size, grid_size, grid_spacing),
        background_line_style={"stroke_color": GREY, "stroke_width": 1},
    ).scale(scale)
    return Group(a_grid, a_dot)


def wall_with_cross_hatching(
    start: Vector3D,
    end: Vector3D,
    color: ManimColor = WHITE,
    spacing: float = 0.3,
    hatch_length: float = 0.3,
    angle: float = PI / 4,
):
    # Create the main wall line
    wall = Line(start=start, end=end, color=color)

    # Create hatching lines
    hatch_lines = VGroup()
    wall_vector = np.array(end) - np.array(start)
    wall_length = np.linalg.norm(wall_vector)
    direction = wall_vector / wall_length

    num_hatches = int(wall_length / spacing)
    for i in range(num_hatches+1):
        point = np.array(start) + direction * spacing * i
        hatch_offset = np.array([
            hatch_length * np.cos(angle + PI / 2),
            hatch_length * np.sin(angle + PI / 2),
            0
        ])
        hatch_lines.add(
            Line(
                start=point,
                end=point + hatch_offset,
                stroke_width=1,
                color=color,
            )
        )
    return VGroup(wall, hatch_lines)


def two_opposing_walls(
    first_midpoint: Vector3D,
    second_midpoint: Vector3D,
    wall_width: float,
    hatch_length: float,
    color: ManimColor = WHITE,
    angle: float = PI / 4,
):
    # Calculate direction vector from first to second midpoint
    wall1_to_wall2 = second_midpoint - first_midpoint
    direction = wall1_to_wall2 / np.linalg.norm(wall1_to_wall2)
    perpendicular = np.array([-direction[1], direction[0], 0])
    half_wall = perpendicular * wall_width / 2

    start1 = first_midpoint + half_wall
    end1 = first_midpoint - half_wall
    wall1 = wall_with_cross_hatching(
        start1, end1, color=color, hatch_length=hatch_length, angle=angle
    )

    start2 = second_midpoint + half_wall
    end2 = second_midpoint - half_wall
    wall2 = wall_with_cross_hatching(
        start2, end2, color=color, hatch_length=hatch_length, angle=angle + PI
    )

    return VGroup(wall1, wall2)
