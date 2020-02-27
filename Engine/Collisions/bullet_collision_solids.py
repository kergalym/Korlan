from panda3d.core import Vec3
from panda3d.bullet import ZUp
from panda3d.bullet import BulletSphereShape
from panda3d.bullet import BulletCapsuleShape
from panda3d.bullet import BulletBoxShape
from panda3d.bullet import BulletCylinderShape
from panda3d.bullet import BulletConeShape
from panda3d.bullet import BulletPlaneShape
from direct.showbase.PhysicsManagerGlobal import physicsMgr


class BulletCollisionSolids:

    def __init__(self):
        self.physics_mgr = physicsMgr

    def set_bs_sphere(self):
        radius = 0.6
        sphere = BulletSphereShape(radius)
        return sphere

    def set_bs_capsule(self):
        radius = 0.5
        height = 0.75
        capsule = BulletCapsuleShape(radius, height, ZUp)
        return capsule

    def set_bs_cylinder(self):
        radius = 0.5
        height = 1.4
        cylinder = BulletCylinderShape(radius, height, ZUp)
        return cylinder

    def set_bs_cone(self):
        radius = 0.6
        height = 1.0
        cone = BulletConeShape(radius, height, ZUp)
        return cone

    def set_bs_plane(self):
        norm_vec = Vec3(0, 0, 1)
        distance = 0
        plane = BulletPlaneShape(norm_vec, distance)
        return plane

    def set_bs_cube(self):
        axis = Vec3(0.5, 0.5, 1.0)
        box = BulletBoxShape(axis)
        return box

