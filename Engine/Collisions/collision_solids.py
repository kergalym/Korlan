from panda3d.core import Vec3, LVector3
from panda3d.bullet import ZUp
from panda3d.bullet import BulletSphereShape
from panda3d.bullet import BulletCapsuleShape
from panda3d.bullet import BulletBoxShape
from panda3d.bullet import BulletCylinderShape
from panda3d.bullet import BulletConeShape
from panda3d.bullet import BulletPlaneShape
from panda3d.bullet import BulletTriangleMesh
from panda3d.bullet import BulletTriangleMeshShape
from panda3d.bullet import BulletGhostNode

from direct.showbase.PhysicsManagerGlobal import physicsMgr


class BulletCollisionSolids:

    def __init__(self):
        self.physics_mgr = physicsMgr
        self.base = base
        self.base.actor_hb = {}
        self.base.actor_hb_masks = {}

    def set_bs_hitbox(self, actor, joints, world):
        if (actor and joints and world
                and isinstance(joints, list)):
            if (hasattr(base, 'npcs_actor_refs')
                    and base.npcs_actor_refs
                    and hasattr(base, "player_ref")
                    and base.player_ref):
                for joint in joints:
                    shape = BulletBoxShape(Vec3(1, 1, 1))
                    name_hb = "{0}_{1}:HB".format(actor.get_name(), joint)
                    name = actor.get_name()
                    ghost = BulletGhostNode(name_hb)
                    ghost.add_shape(shape)
                    ghost_np = render.attachNewNode(ghost)

                    if joint == "Hips":
                        ghost_np.set_pos(0, 0, 0)
                        ghost_np.set_scale(15, 15, 15)
                    elif joint == "LeftHand" or joint == "RightHand":
                        ghost_np.set_pos(0, 8.0, 5.2)
                        ghost_np.set_scale(6, 6, 6)

                    mask = actor.get_collide_mask()
                    ghost_np.node().set_into_collide_mask(mask)
                    ghost_np.set_tag(key=name_hb, value=joint)

                    exposed_joint = None
                    if name == "Player":
                        char_joint = base.player_ref.get_part_bundle('modelRoot').get_name()
                        joint = "{0}:{1}".format(char_joint, joint)
                        exposed_joint = base.player_ref.expose_joint(None, "modelRoot", joint)
                    elif name != "Player":
                        char_joint = base.npcs_actor_refs[name].get_part_bundle('modelRoot').get_name()
                        joint = "{0}:{1}".format(char_joint, joint)
                        exposed_joint = base.npcs_actor_refs[name].expose_joint(None, "modelRoot", joint)

                    ghost_np.reparent_to(exposed_joint)
                    world.attach_ghost(ghost)
                    # self.base.actor_hb[name_hb] = ghost_np.node()
                    # self.base.actor_hb_masks[name_hb] = mask

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

    def set_bs_auto(self, obj, type):
        if obj and isinstance(type, str):
            bool_ = False
            geom = obj.node().get_geom(0)
            mesh = BulletTriangleMesh()
            mesh.add_geom(geom)

            if type == 'dynamic':
                bool_ = True
            if type == 'static':
                bool_ = False

            if mesh:
                shape = BulletTriangleMeshShape(mesh, dynamic=bool_)
                return shape

    def set_bs_auto_multi(self, objects, type):
        if objects and isinstance(objects, list) and isinstance(type, str):
            mesh_colliders_dict = {}
            mesh_colliders_cleaned_dict = {}
            objects_cleaned_dict = {}

            colliders = render.find("**/Collisions/lvl*coll")

            if not colliders:
                return

            if hasattr(base, "shaped_objects") and not base.shaped_objects:
                for x, col in zip(objects[1], colliders.get_children()):
                    # Skip already added bullet shapes to prevent duplicating
                    parent_name = ''
                    if not render.find('{0}'.format(x)).get_parent().is_empty():
                        parent_name = render.find('{0}'.format(x)).get_parent().get_name()
                        render.find('{0}'.format(x)).get_parent()

                    if "BS" in parent_name or "BS" in x:
                        continue

                    # Drop unused mesh
                    if "Grass" in x:
                        continue

                    # Has it geom?
                    if hasattr(objects[1][x].node(), "get_geom"):
                        geom = col.node().get_geom(0)
                        mesh = BulletTriangleMesh()
                        mesh.add_geom(geom)

                        if "Box" in x or "Box" in parent_name:
                            type = 'dynamic'

                        if type == 'dynamic':
                            bool_ = True
                            shape = BulletTriangleMeshShape(mesh,
                                                            dynamic=bool_)
                            mesh_colliders_dict[x] = shape
                        if type == 'static':
                            bool_ = False
                            shape = BulletTriangleMeshShape(mesh,
                                                            dynamic=bool_,
                                                            compress=True,
                                                            bvh=True)
                            mesh_colliders_dict[x] = shape

                        # Meshes used to make geom now aren't needed anymore, so remove them
                        col.remove_node()

                # Cleaning from actors by reassembling dict objects
                for key_obj, key_mesh in zip(objects[0], mesh_colliders_dict):
                    if key_mesh != "__Actor_modelRoot":
                        mesh_colliders_cleaned_dict[key_mesh] = mesh_colliders_dict.get(key_mesh)

                    if key_obj != "__Actor_modelRoot":
                        objects_cleaned_dict[key_obj] = objects[0].get(key_obj)

                return [objects_cleaned_dict, mesh_colliders_cleaned_dict]
