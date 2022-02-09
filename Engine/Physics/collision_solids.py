from panda3d.core import Vec3, BitMask32
from panda3d.bullet import ZUp, BulletRigidBodyNode
from panda3d.bullet import BulletSphereShape
from panda3d.bullet import BulletCapsuleShape
from panda3d.bullet import BulletBoxShape
from panda3d.bullet import BulletCylinderShape
from panda3d.bullet import BulletConeShape
from panda3d.bullet import BulletPlaneShape
from panda3d.bullet import BulletTriangleMesh
from panda3d.bullet import BulletTriangleMeshShape
from panda3d.bullet import BulletGhostNode


class BulletCollisionSolids:

    def __init__(self):
        self.base = base

    def get_bs_hitbox(self, actor, joints, mask, world):
        if (actor and joints and mask and world
                and isinstance(joints, list)):

            for joint in joints:
                shape = BulletBoxShape(Vec3(1, 1, 1))
                name_hb = "{0}_{1}:HB".format(actor.get_name(), joint)
                name = actor.get_name()
                ghost = BulletGhostNode(name_hb)
                ghost.add_shape(shape)
                ghost_np = render.attach_new_node(ghost)

                if joint == "Hips":
                    ghost_np.set_pos(0, 0, 0)
                    ghost_np.set_scale(15, 15, 15)
                    # Actor and its hitboxes won't collide with each other
                    ghost_np.node().set_into_collide_mask(mask)
                elif (joint == "LeftHand"
                      or joint == "RightHand"):
                    ghost_np.set_pos(0, 8.0, 5.2)
                    ghost_np.set_scale(6, 6, 6)
                    # Actor and its hitboxes won't collide with each other
                    ghost_np.set_collide_mask(BitMask32.allOff())

                ghost_np.set_tag(key=name_hb, value=joint)

                if "Player" in name and self.base.game_instance['player_ref']:
                    char_joint = self.base.game_instance['player_ref'].get_part_bundle('modelRoot').get_name()
                    joint = "{0}:{1}".format(char_joint, joint)
                    exp_joint = self.base.game_instance['player_ref'].expose_joint(None, "modelRoot", joint)
                    ghost_np.reparent_to(exp_joint)
                    world.attach_ghost(ghost)
                elif "NPC" in name and self.base.game_instance['actors_ref']:
                    char_joint = self.base.game_instance['actors_ref'][name].get_part_bundle('modelRoot').get_name()
                    joint = "{0}:{1}".format(char_joint, joint)
                    exp_joint = self.base.game_instance['actors_ref'][name].expose_joint(None, "modelRoot", joint)
                    ghost_np.reparent_to(exp_joint)
                    world.attach_ghost(ghost)

    def get_bs_sphere(self):
        radius = 0.6
        sphere = BulletSphereShape(radius)
        return sphere

    def get_bs_capsule(self):
        height = 1.75
        width = 0.3
        radius = height - 2 * width
        capsule = BulletCapsuleShape(width, radius, ZUp)
        return capsule

    def get_bs_cylinder(self):
        radius = 0.5
        height = 1.4
        cylinder = BulletCylinderShape(radius, height, ZUp)
        return cylinder

    def get_bs_cone(self):
        radius = 0.6
        height = 1.0
        cone = BulletConeShape(radius, height, ZUp)
        return cone

    def get_bs_plane(self):
        norm_vec = Vec3(0, 0, 1)
        distance = 0
        plane = BulletPlaneShape(norm_vec, distance)
        return plane

    def get_bs_cube(self):
        axis = Vec3(0.5, 0.5, 0.5)
        box = BulletBoxShape(axis)
        return box

    def get_bs_auto(self, obj, type_):
        if obj and isinstance(type_, str):
            bool_ = False
            if hasattr(obj.node(), "get_geom"):
                geom = obj.node().get_geom(0)
                mesh = BulletTriangleMesh()
                mesh.add_geom(geom)

                if type_ == 'dynamic':
                    bool_ = True
                if type_ == 'static':
                    bool_ = False

                if mesh:
                    shape = BulletTriangleMeshShape(mesh, dynamic=bool_)
                    return shape

    def get_bs_predefined(self, obj, type_):
        if obj and isinstance(type_, str):
            bool_ = False
            collection = render.find("**/Collisions/lvl*coll")
            if collection:
                for child in collection.get_children():
                    if child and obj.get_name() == child.get_name():
                        if hasattr(obj.node(), "get_geom"):
                            geom = child.node().get_geom(0)
                            mesh = BulletTriangleMesh()
                            mesh.add_geom(geom)

                            if type_ == 'dynamic':
                                bool_ = True
                            if type_ == 'static':
                                bool_ = False

                            if mesh:
                                shape = BulletTriangleMeshShape(mesh, dynamic=bool_)
                                return shape
