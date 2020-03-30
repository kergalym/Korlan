from panda3d.core import BitMask32
from Engine.Collisions.collision_solids import BulletCollisionSolids
from Engine.Physics.physics import PhysicsAttr
from Engine.FSM.npc_ai import NpcAI
from panda3d.bullet import BulletCharacterControllerNode
from panda3d.bullet import BulletRigidBodyNode


class Collisions:

    def __init__(self):
        self.base = base
        self.render = render

        self.cam_cs = None
        self.cam_bs_nodepath = None
        self.cam_collider = None

        self.physics_attr = PhysicsAttr()
        self.bs = BulletCollisionSolids()
        self.fsm_npc = NpcAI()

        self.korlan = None

        self.no_mask = BitMask32.allOff()
        self.mask = BitMask32.allOn()
        self.mask0 = BitMask32.bit(0)
        self.mask1 = BitMask32.bit(1)
        self.mask2 = BitMask32.bit(2)
        self.mask3 = BitMask32.bit(3)
        self.mask5 = BitMask32.bit(5)

    def collision_info(self, player, item):
        if player and item and hasattr(base, "bullet_world"):

            query_all = base.bullet_world.ray_test_all(player.get_pos(),
                                                       item.get_pos())

            collision_info = {"hits": query_all.has_hits(),
                              "fraction": query_all.get_closest_hit_fraction(),
                              "num_hits": query_all.get_num_hits()}

            for query in query_all.get_hits():
                collision_info["hit_pos"] = query.get_hit_pos()
                collision_info["hit_normal"] = query.get_hit_normal()
                collision_info["hit_fraction"] = query.get_hit_fraction()
                collision_info["node"] = query.get_node()

            return collision_info

    def set_collision(self, obj, type, shape):
        # Physics World must be enabled only one time before adding collider.
        self.physics_attr.set_physics_world()

        if (obj and type and shape
                and isinstance(type, str)
                and isinstance(shape, str)):
            if type == "player":
                self.korlan = obj
                self.korlan.setTag(key=obj.get_name(), value='1')
                self.set_actor_collider(actor=self.korlan,
                                        col_name='{0}:BS'.format(self.korlan.get_name()),
                                        shape=shape,
                                        mask=self.mask0,
                                        type="player")
            if type == "actor":
                obj.set_tag(key=obj.get_name(), value='1')
                self.set_actor_collider(actor=obj,
                                        col_name='{0}:BS'.format(obj.get_name()),
                                        shape=shape,
                                        mask=self.mask1,
                                        type="actor")
            if type == "item":
                obj.set_tag(key=obj.get_name(), value='1')
                self.set_object_collider(obj=obj,
                                         col_name='{0}:BS'.format(obj.get_name()),
                                         shape=shape,
                                         mask=self.mask0)

    def set_actor_collider(self, actor, col_name, shape, mask, type):
        if (actor
                and col_name
                and shape
                and mask
                and type
                and isinstance(col_name, str)
                and isinstance(shape, str)
                and isinstance(type, str)):
            if base.menu_mode is False and base.game_mode:
                actor_bs = None
                actor_bs_np = None
                if shape == 'capsule':
                    actor_bs = self.bs.set_bs_capsule()
                if shape == 'sphere':
                    actor_bs = self.bs.set_bs_sphere()
                if type == 'player':
                    if self.physics_attr.world_nodepath:
                        base.bullet_char_contr_node = BulletCharacterControllerNode(actor_bs,
                                                                                    0.4,
                                                                                    col_name)
                        actor_bs_np = self.physics_attr.world_nodepath.attach_new_node(base.bullet_char_contr_node)
                        actor_bs_np.set_collide_mask(mask)
                        self.physics_attr.world.attach(base.bullet_char_contr_node)
                        actor.reparent_to(actor_bs_np)
                elif type == 'actor':
                    if self.physics_attr.world_nodepath:
                        actor_contr_node = BulletCharacterControllerNode(actor_bs,
                                                                         0.4,
                                                                         col_name)
                        actor_bs_np = self.physics_attr.world_nodepath.attach_new_node(actor_contr_node)
                        actor_bs_np.set_collide_mask(mask)
                        self.physics_attr.world.attach(actor_contr_node)
                        actor.reparent_to(actor_bs_np)
                # Set actor down to make it
                # at the same point as bullet shape
                actor.set_z(-1)
                # Set the bullet shape position same as actor position
                if actor_bs_np:
                    actor_bs_np.set_x(actor.get_x())
                    actor_bs_np.set_y(actor.get_y())
                # Set actor position to zero
                # after actor becomes a child of bullet shape.
                # It should not get own position values.
                actor.set_y(0)
                actor.set_x(0)

    def set_object_collider(self, obj, col_name, shape, mask):
        if (obj
                and col_name
                and shape
                and mask
                and isinstance(col_name, str)
                and isinstance(shape, str)):
            if base.menu_mode is False and base.game_mode:
                object_bs = None
                if shape == 'cube':
                    object_bs = self.bs.set_bs_cube()
                    if self.physics_attr.world_nodepath:
                        obj_bs_np = self.physics_attr.world_nodepath.attach_new_node(BulletRigidBodyNode(col_name))
                        obj_bs_np.node().set_mass(1.0)
                        obj_bs_np.node().add_shape(object_bs)
                        obj_bs_np.set_collide_mask(mask)
                        self.physics_attr.world.attach(obj_bs_np.node())
                        obj.reparent_to(obj_bs_np)
                        obj_bs_np.set_pos(obj.get_pos())
                        obj_bs_np.set_scale(0.20, 0.20, 0.20)
                        obj.set_pos(0.0, 3.70, -0.50)
                        obj.set_hpr(0, 0, 0)
                        obj.set_scale(6.25, 6.25, 6.25)