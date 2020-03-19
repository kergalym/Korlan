from panda3d.core import BitMask32
from Engine.Collisions.bullet_collision_solids import BulletCollisionSolids
from Engine.Physics.physics import PhysicsAttr
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

        self.korlan = None

        self.no_mask = BitMask32.allOff()
        self.mask = BitMask32.allOn()
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

    def set_inter_collision(self, player):
        if player:
            self.korlan = player
            self.korlan.setTag(key=player.get_name(), value='1')
            # Octree-optimised "into" objects defined here
            assets_nodes = base.asset_nodes_assoc_collector()
            box = assets_nodes.get('Box')
            box.set_tag(key=box.get_name(), value='1')
            self.physics_attr.set_physics()
            self.set_actor_collider(actor=self.korlan,
                                    col_name='{0}:BS'.format(self.korlan.get_name()),
                                    shape="capsule")
            self.set_object_collider(obj=box,
                                     col_name='{0}:BS'.format(box.get_name()),
                                     shape="cube")

    def set_actor_collider(self, actor, col_name, shape):
        if (actor
                and col_name
                and shape
                and isinstance(col_name, str)
                and isinstance(shape, str)):
            if base.menu_mode is False and base.game_mode:
                base.bullet_char_contr_node = None
                actor_bs = None
                if shape == 'capsule':
                    actor_bs = self.bs.set_bs_capsule()
                if shape == 'sphere':
                    actor_bs = self.bs.set_bs_sphere()
                base.actor_bs = actor_bs
                base.bullet_char_contr_node = BulletCharacterControllerNode(actor_bs,
                                                                            0.4,
                                                                            '{0}:BS'.format(actor.get_name()))
                player_bs_np = self.physics_attr.world_nodepath.attach_new_node(base.bullet_char_contr_node)
                player_bs_np.set_collide_mask(self.mask)
                self.physics_attr.world.attach(base.bullet_char_contr_node)
                actor.reparent_to(player_bs_np)
                # Set actor down to make it
                # at the same point as bullet shape
                actor.set_z(-1)
                # Set the bullet shape position same as actor position
                player_bs_np.set_y(actor.get_y())
                # Set actor relative to bullet shape
                actor.set_y(0)

    def set_object_collider(self, obj, col_name, shape):
        if (obj
                and col_name
                and shape
                and isinstance(col_name, str)
                and isinstance(shape, str)):
            if base.menu_mode is False and base.game_mode:
                object_bs = None
                if shape == 'cube':
                    object_bs = self.bs.set_bs_cube()
                obj_bs_np = self.physics_attr.world_nodepath.attach_new_node(BulletRigidBodyNode(col_name))
                obj_bs_np.node().set_mass(1.0)
                obj_bs_np.node().add_shape(object_bs)
                obj_bs_np.set_collide_mask(self.mask)
                self.physics_attr.world.attach(obj_bs_np.node())
                obj.clearModelNodes()
                obj.reparent_to(obj_bs_np)
                obj_bs_np.set_pos(obj.get_pos())
                obj_bs_np.set_scale(0.20, 0.20, 0.20)
                obj.set_pos(0.0, 3.70, -0.50)
                obj.set_hpr(0, 0, 0)
                obj.set_scale(6.25, 6.25, 6.25)
