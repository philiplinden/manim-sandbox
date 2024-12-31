from manim import *

class InertialReferenceFrames(ZoomedScene):
    """
    An **inertial reference frame** is a frame of reference in which a body at
    rest remains at rest and a body in motion moves at a constant speed in a
    straight line unless acted upon by an outside force.

    ([source](https://openstax.org/books/university-physics-volume-3/pages/5-1-invariance-of-physical-laws))
    """
    def __init__(self, **kwargs):   #HEREFROM
        ZoomedScene.__init__(
            self,
            zoom_factor=0.5,
            zoomed_display_height=4,
            zoomed_display_width=4,
            image_frame_stroke_width=1,
            zoomed_camera_config={
                'default_frame_stroke_width': 1,
            },
            **kwargs
        )
    def construct(self):
        zoomed_camera = self.zoomed_camera
        zoomed_display = self.zoomed_display
        frame = zoomed_camera.frame
        
        dot1 = Dot(color=BLUE)
        dot2 = Dot(color=RED).shift(RIGHT)
        frame.move_to(dot2)

        circle_path = Circle(radius=1)
        self.add(dot1, dot2)
        
        zd_rect = BackgroundRectangle(zoomed_display, fill_opacity=0, buff=MED_SMALL_BUFF)
        self.add_foreground_mobject(zd_rect)

        self.activate_zooming()

        self.play(
            MoveAlongPath(Group(dot2, frame), circle_path, rate_func=linear, run_time=5),
        )
