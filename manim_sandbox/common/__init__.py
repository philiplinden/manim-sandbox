from manim import *

def dot_with_local_grid(
        color=BLUE, grid_size=2, grid_spacing=1, scale=0.5
    ):
        a_dot = Dot(color=color)
        a_grid = NumberPlane(
            x_range=(-grid_size, grid_size, grid_spacing),
            y_range=(-grid_size, grid_size, grid_spacing),
            background_line_style={"stroke_color": GREY, "stroke_width": 1},
        ).scale(scale)
        return Group(a_grid, a_dot)
