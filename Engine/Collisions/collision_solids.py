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
            colliders_dict = base.assets_collider_collector()
            colliders = base.loader.load_model(colliders_dict["level_one_coll"])
            if hasattr(base, "shaped_objects") and not base.shaped_objects:
                for x, col in zip(objects[1], colliders.get_children()):

                    # Skip already added bullet shapes to prevent duplicating
                    parent_name = render.find('**/{0}'.format(x)).get_parent().get_name()
                    if "BS" in parent_name or "BS" in x:
                        continue

                    # Drop unused mesh
                    if "Grass" in x:
                        continue

                    # Has it  geom?
                    if hasattr(objects[1][x].node(), "get_geom"):
                        # TODO Use col.node().get_geom(0) when colliders will be ready
                        # geom = col.node().get_geom(0)
                        geom = objects[1][x].node().get_geom(0)
                        mesh = BulletTriangleMesh()
                        mesh.add_geom(geom)

                        if type == 'dynamic':
                            bool_ = True
                            shape = BulletTriangleMeshShape(mesh, dynamic=bool_, compress=False, bvh=False)
                            mesh_colliders_dict[x] = shape
                        if type == 'static':
                            bool_ = False
                            shape = BulletTriangleMeshShape(mesh, dynamic=bool_, compress=True, bvh=True)
                            mesh_colliders_dict[x] = shape

                        # Meshes used to make geom now aren't needed anymore, so remove them
                        col.remove_node()

                return [objects[0], mesh_colliders_dict]
