from panda3d.core import CollisionSphere, Plane, Vec3, Point3, CollisionNode
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
        pass

    def set_cs_sphere(self):
        axis = (0, 0, 0.8)
        radius = 0.6
        sphere = CollisionSphere(axis, radius)
        return sphere

    def set_cs_capsule(self):
        dimensions = (0, 0, 1.3)
        axis = (0, 0, 0.4)
        radius = 0.2
        capsule = CollisionCapsule(dimensions, axis, radius)
        return capsule

    def set_cs_invsphere(self):
        axis = (0, 0, 0.8)
        radius = 0.6
        inv_sphere = CollisionInvSphere(axis, radius)
        return inv_sphere

    def set_cs_plane(self):
        plane = CollisionPlane(Plane(Vec3(0, 0, 1), Point3(0, 0, 0)))
        return plane

    def set_cs_polygon(self):
        quad = CollisionPolygon(Point3(0, 0, 0), Point3(0, 0, 1),
                                Point3(0, 1, 1), Point3(0, 1, 0))
        return quad

    def set_cs_ray(self):
        origin = (0, 0, 9)
        direction = (0, 0, -1)
        ray = CollisionRay(origin, direction)
        return ray

    def set_cs_line(self):
        origin = (0, 0, 9)
        direction = (0, 0, -1)
        line = CollisionLine(origin, direction)
        return line

    def set_cs_segment(self):
        axis_a = (0, 0, 9)
        axis_b = (1, 0, 1)
        segment = CollisionSegment(axis_a, axis_b)
        return segment

    def set_cs_parabola(self):
        origin = (0, 0, 9)
        direction = (0, 0, -1)
        parabola = CollisionParabola(origin, direction)
        return parabola

    def set_cs_cube(self):
        center = (0, 0, 0.2)
        axis = (-1, 0.5, 1)
        box = CollisionBox(center, axis)
        return box

