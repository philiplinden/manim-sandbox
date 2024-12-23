# Example: Introduction figure
from manim import *

class Intro(Scene):
    def construct(self):
        # Create mirrors (horizontal lines)
        mirror_top = Line(start=[-2, 2, 0], end=[2, 2, 0], color=BLUE)
        mirror_bottom = Line(start=[-2, -2, 0], end=[2, -2, 0], color=BLUE)

        # Create photon (dot)
        photon = Dot(color=YELLOW)
        
        # Add elements to scene
        self.add(mirror_top, mirror_bottom)
        self.add(photon)

        # Create distance and time counters
        distance = 0
        mirror_spacing = 4  # Distance between mirrors
        
        distance_text = Text("Distance: ", font_size=24).move_to([-3, 3, 0])
        distance_number = DecimalNumber(
            0,
            num_decimal_places=1,
            font_size=24
        ).next_to(distance_text, RIGHT)
        
        time_text = Text("Time: ", font_size=24).move_to([-3, 2.5, 0])
        time_number = DecimalNumber(
            0,
            num_decimal_places=2,
            font_size=24
        ).next_to(time_text, RIGHT)
        
        self.add(distance_text, distance_number, time_text, time_number)

        # Create the bouncing animation
        bounce_time = 1.0  # Time for one bounce (up or down)
        num_bounces = 4    # Number of complete bounces

        # Initial position at bottom mirror
        photon.move_to([-0.5, -2, 0])

        # Create the bouncing animations
        for i in range(num_bounces * 2):
            distance += mirror_spacing
            if i % 2 == 0:
                # Moving up
                self.play(
                    photon.animate.move_to([-0.5, 2, 0]),
                    distance_number.animate.set_value(distance),
                    time_number.animate.set_value(distance/3e8),
                    run_time=bounce_time,
                    rate_func=linear
                )
            else:
                # Moving down
                self.play(
                    photon.animate.move_to([-0.5, -2, 0]),
                    distance_number.animate.set_value(distance),
                    time_number.animate.set_value(distance/3e8),
                    run_time=bounce_time,
                    rate_func=linear
                )

        # Pause briefly at the end
        self.wait(0.5)
