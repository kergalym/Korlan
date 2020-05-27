from panda3d.core import Vec3
from panda3d.bullet import ZUp
from panda3d.bullet import BulletSphereShape
from panda3d.bullet import BulletCapsuleShape
from panda3d.bullet import BulletBoxShape
from panda3d.bullet import BulletCylinderShape
from panda3d.bullet import BulletConeShape
from panda3d.bullet import BulletPlaneShape
from panda3d.bullet import BulletTriangleMesh
from panda3d.bullet import BulletTriangleMeshShape
from panda3d.bullet import BulletConvexHullShape

from direct.showbase.PhysicsManagerGlobal import physicsMgr


class BulletCollisionSolids:

    def __init__(self):
        self.physics_mgr = physicsMgr

    def set_bs_sphere(self):
        radius = 0.6
        sphere = BulletSphereShape(radius)
        return sphere

    def set_bs_capsule(self):
        height = 1.75
        width = 0.3
        radius = height - 2 * width
        capsule = BulletCapsuleShape(width, radius, ZUp)
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
        axis = Vec3(0.5, 0.5, 0.5)
        box = BulletBoxShape(axis)
        return box

    def set_bs_auto_multi(self, objects, type):
        if objects and isinstance(objects, list) and isinstance(type, str):
            mesh_colliders_dict = {}
            if hasattr(base, "shaped_objects") and not base.shaped_objects:
                for x in objects[1]:
                    # Don't use actors
                    if x != '__Actor_modelRoot':
                        # If it's geom?
                        if hasattr(objects[1][x].node(), "get_geom"):
                            geom = objects[1][x].node().get_geom(0)
                            mesh = BulletTriangleMesh()
                            mesh.add_geom(geom)
                            bool_ = None
                            if type == 'dynamic':
                                bool_ = True
                            if type == 'static':
                                bool_ = False
                            shape = BulletTriangleMeshShape(mesh, dynamic=bool_)
                            mesh_colliders_dict[x] = shape

                return [objects[0], mesh_colliders_dict]

