from manim import *
from manim_sandbox.common.compound_objects import two_opposing_walls


class PhotonClock(Scene):
    def construct(self):
        # Constants
        CLOCK_HEIGHT = 4
        WALL_WIDTH = 1

        PHOTON_SPEED = 1
        BASE_TIME = (CLOCK_HEIGHT * 2) / PHOTON_SPEED
        CLOCK_DISPLACEMENT = 4

        def create_clock(position=ORIGIN, label="Clock"):
            # Create walls using the provided function
            walls = two_opposing_walls(
                first_midpoint=position + UP * CLOCK_HEIGHT / 2,
                second_midpoint=position + DOWN * CLOCK_HEIGHT / 2,
                wall_width=WALL_WIDTH,
                hatch_length=0.3,
                color=WHITE,
            )

            # Create photon
            photon = Dot(color=YELLOW).move_to(
                position + DOWN * CLOCK_HEIGHT / 2
            )

            # Create path tracker
            trace = TracedPath(
                photon.get_center,
                stroke_width=2,
                stroke_color=YELLOW,
                stroke_opacity=0.7,
            )

            # Create label
            title = (
                Text(label, font_size=24)
                .next_to(walls, UP)
                .add_updater(lambda m: m.next_to(walls, UP))
            )
            return VGroup(walls, photon, title), trace

        # Create stationary clock
        stationary_clock, stationary_trace = create_clock(
            LEFT * 4, "Stationary Clock"
        )
        self.add(stationary_clock, stationary_trace)

        # Create moving clock
        moving_clock, moving_trace = create_clock(LEFT * 0, "Moving Clock")
        self.add(moving_clock, moving_trace)

        # Get references to photons
        stationary_photon = stationary_clock[1]
        moving_photon = moving_clock[1]

        # Create paths
        stationary_path = [
            stationary_photon.get_center(),
            stationary_photon.get_center() + UP * CLOCK_HEIGHT,
            stationary_photon.get_center(),
        ]

        # Calculate diagonal path for moving clock
        moving_start = moving_photon.get_center()
        moving_end = moving_start + (RIGHT * CLOCK_DISPLACEMENT)
        moving_top = moving_start + (RIGHT * CLOCK_DISPLACEMENT) + (UP * CLOCK_HEIGHT)

        moving_path = [moving_start, moving_top, moving_end]

        # Create path visualizations (shown later)
        path_demonstration = VGroup(
            Line(stationary_path[0], stationary_path[1], color=RED),
            Line(moving_start, moving_top, color=RED),
        )

        # Animation sequence
        self.wait(1)

        # Show one complete cycle with proper timing
        # 1) Move each photon to the midpoint in the same time
        #    This shows the stationary clock goes directly up L/2,
        #    while the moving clock goes diagonally the same distance.

        # Animate both photons to the midpoint in the same run_time
        stop_time = BASE_TIME / 4

        # Define midpoint for the stationary clock (bottom -> halfway up)
        stationary_stop_point = (
            stationary_path[0] + stop_time * PHOTON_SPEED * UP
        )
        stationary_stop_path = VMobject().set_points_as_corners(
            [stationary_path[0], stationary_stop_point]
        )

        # Define midpoint for the moving clock (bottom -> halfway up diagonally)
        moving_direction = CLOCK_HEIGHT * UP + CLOCK_SPEED * RIGHT
        moving_direction_unit = moving_direction / np.linalg.norm(
            moving_direction
        )
        moving_stop_point = moving_path[0] + (
            stop_time * PHOTON_SPEED * moving_direction_unit
        )
        moving_stop_path = VMobject().set_points_as_corners(
            [moving_path[0], moving_stop_point]
        )

        self.play(
            AnimationGroup(
                MoveAlongPath(
                    stationary_photon,
                    stationary_stop_path,
                    rate_func=linear,
                    run_time=stop_time,
                ),
                AnimationGroup(
                    MoveAlongPath(
                        moving_photon,
                        moving_stop_path,
                        rate_func=linear,
                        run_time=stop_time,
                    ),
                    moving_clock[0]
                    .animate(run_time=stop_time, rate_func=linear)
                    .shift(CLOCK_SPEED * RIGHT * stop_time),
                ),
            )
        )
        # Pause to emphasize they've both traveled the same total distance
        self.wait(2)

        moving_diagonal = Line(moving_path[0], moving_stop_point, color=RED)
        stationary_vertical = Line(
            stationary_path[0], stationary_stop_point, color=RED
        )
        # Vertical line from bottom to same y as midpoint
        component_vertical = DashedLine(
            moving_path[0],
            [moving_path[0][0], moving_stop_point[1], 0],
            color=BLUE,
        )
        # Horizontal line from that vertical line to the midpoint
        component_horizontal = DashedLine(
            [moving_path[0][0], moving_stop_point[1], 0],
            moving_stop_point,
            color=BLUE,
        )

        # Create them in the scene
        self.play(
            Create(moving_diagonal),
            Create(stationary_vertical),
            # Start Generation Here
            Create(Brace(moving_diagonal, LEFT)),
            Write(
                MathTex(f"{moving_diagonal.get_length():.2f}").next_to(
                    Brace(
                        moving_diagonal,
                        moving_diagonal.copy().rotate(PI / 2).get_unit_vector(),
                    ),
                    RIGHT,
                )
            ),
            Create(Brace(stationary_vertical, LEFT)),
            Write(
                MathTex(f"{stationary_vertical.get_length():.2f}").next_to(
                    Brace(stationary_vertical, LEFT), LEFT
                )
            ),
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

        self.wait(2)
