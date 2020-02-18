from panda3d.core import CollisionSphere
from panda3d.core import CollisionCapsule
from panda3d.core import CollisionInvSphere
from panda3d.core import CollisionPlane
from panda3d.core import CollisionPolygon
from panda3d.core import CollisionRay
from panda3d.core import CollisionLine
from panda3d.core import CollisionSegment
from panda3d.core import CollisionParabola
from panda3d.core import CollisionBox
from panda3d.core import CollisionTube


class CollisionSolids:

    def __init__(self):
        self.base = base
        self.render = render

    def set_cs_sphere(self, axis, radius):
        if (isinstance(axis, tuple)
                and isinstance(radius, float)
                or isinstance(radius, int)):
            cs = CollisionSphere(axis, radius)
            return cs

    def set_cs_capsule(self):
        pass

    def set_cs_invsphere(self):
        pass

    def set_cs_plane(self):
        pass

    def set_cs_polygon(self):
        pass

    def set_cs_ray(self, origin, direction):
        if (isinstance(origin, tuple)
                and isinstance(direction, tuple)):
            cs = CollisionRay()
            cs.set_origin(origin)
            cs.set_direction(direction)
            return cs

    def set_cs_line(self):
        pass

    def set_cs_segment(self):
        pass

    def set_cs_parabola(self):
        pass

    def set_cs_cube(self):
        pass

    def set_cs_tube(self):
        pass
