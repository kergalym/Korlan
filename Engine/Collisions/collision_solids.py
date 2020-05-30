from panda3d.core import Vec3, Point3
from panda3d.core import BoundingVolume
from panda3d.core import Geom
from panda3d.core import GeomVertexFormat, GeomVertexData
from panda3d.core import GeomEnums
from panda3d.core import GeomTriangles
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
                    if x == '__Actor_modelRoot':
                        continue

                    # Drop unused or heavy meshes
                    if ("Grass" in x
                            # or "tosagash" in x  # false
                            # or "chest" in x  # false
                            # or 'kebeje' in x  # false
                            # or 'besik' in x  # false
                            # or 'stones.hi' in x  # false
                            # or 'mountain' in x  # false
                            # or 'kul' in x  # false
                            # or 'otyn_jer' in x  # false
                            # or 'tosek' in x  # false
                            # or 'saddle' in x  # false
                            # or 'stand_for_weapons' in x  # false
                            # or 'sandyk' in x  # false
                            # or 'tosenish' in x  # false
                            # or 'korpe' in x  # false
                            # or 'jastyk' in x  # false
                            # or 'oshaq' in x  # false
                            # or 'qazan' in x  # false
                            # or 'round_table' in x  # false
                       ):
                        continue

                    name = render.find('**/{0}'.format(x)).get_parent().get_name()
                    if "BS" in name:
                        continue

                    # If it's geom?
                    if hasattr(objects[1][x].node(), "get_geom"):
                        objects[1][x].show_tight_bounds()
                        bounds = objects[1][x].get_bounds()

                        format = GeomVertexFormat()
                        vdata = GeomVertexData('abc', format, GeomEnums.UH_static)
                        tris = GeomTriangles(GeomEnums.UH_static)

                        geom = Geom(vdata)
                        # geom = objects[1][x].node().get_geom(0)
                        geom.add_primitive(tris)
                        geom.set_bounds(bounds)

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

                return [objects[0], mesh_colliders_dict]

