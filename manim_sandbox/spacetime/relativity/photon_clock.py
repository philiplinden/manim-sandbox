from manim import *
from manim_sandbox.common.compound_objects import two_opposing_walls


class PhotonClock(Scene):
    def construct(self):
        # Define top and bottom walls
        TOP_WALL = UP
        BOTTOM_WALL = DOWN

        # Create the walls and add them to the scene
        walls = two_opposing_walls(TOP_WALL, BOTTOM_WALL, wall_width=1.5, hatch_length=0.3)
        self.add(walls)

        photon = Dot(color=YELLOW).move_to(BOTTOM_WALL)
        trace = TracedPath(photon.get_center, stroke_width=2, stroke_color=YELLOW, stroke_opacity=0.7)

        clock = VGroup(walls, photon, trace)
        
        self.play(FadeIn(clock))
        
        # Define the path for the photon to move along
        path_points = [BOTTOM_WALL, TOP_WALL, BOTTOM_WALL]
        photon_path = VMobject().set_points_as_corners(path_points)

        # Animate the photon along the path while waiting simultaneously
        self.play(
            MoveAlongPath(photon, photon_path),
            rate_func=linear
        )
        self.wait(1)

        self.play(
            clock.animate.shift(LEFT * 6)
        )
        self.wait(2)

        moving_path_points = [BOTTOM_WALL + LEFT * 6, TOP_WALL, BOTTOM_WALL + RIGHT * 6]
        moving_photon_path = VMobject().set_points_as_corners(moving_path_points)
        self.play(
            AnimationGroup(
                walls.animate(rate_func=linear, run_time=2).shift(RIGHT * 12),
                MoveAlongPath(photon, moving_photon_path, rate_func=linear, run_time=2),
            )
        )
        self.wait(2)
        self.play(FadeOut(clock))
