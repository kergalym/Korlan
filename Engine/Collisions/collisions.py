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
        self.actor = None

        self.no_mask = BitMask32.allOff()
        self.mask_floor = BitMask32(0x1)
        self.mask_walls = BitMask32(0x2)
        self.mask = BitMask32.allOn()
        self.mask2 = BitMask32.bit(2)
        self.mask5 = BitMask32.bit(5)
        self.mask3 = BitMask32(0x3)

    def set_inter_collision(self, player):
        if player:
            self.korlan = player
            self.korlan.setTag(key=player.get_name(), value='1')
            # Octree-optimised "into" objects defined here
            assets_nodes = base.asset_nodes_assoc_collector()
            mountains = assets_nodes.get('Mountains')
            mountains.set_collide_mask(self.mask_walls)
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
                base.bullet_char_contr_node = BulletCharacterControllerNode(actor_bs,
                                                                            0.4,
                                                                            '{0}:BS'.format(actor.get_name()))
                player_bs_nodepath = self.physics_attr.world_nodepath.attach_new_node(base.bullet_char_contr_node)
                player_bs_nodepath.set_collide_mask(self.mask)
                self.physics_attr.world.attach(base.bullet_char_contr_node)
                actor.reparent_to(player_bs_nodepath)
                # Set actor down to make it
                # at the same point as bullet shape
                actor.set_z(-1)
                # Set the bullet shape position same as actor position
                player_bs_nodepath.set_y(actor.get_y())
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
                object_bs_nodepath = self.physics_attr.world_nodepath.attach_new_node(BulletRigidBodyNode(col_name))
                object_bs_nodepath.node().set_mass(10.0)
                object_bs_nodepath.node().add_shape(object_bs)
                object_bs_nodepath.set_collide_mask(self.mask)
                self.physics_attr.world.attach(object_bs_nodepath.node())
                obj.clearModelNodes()
                obj.reparent_to(object_bs_nodepath)
                object_bs_nodepath.set_pos(obj.get_pos())
                object_bs_nodepath.set_scale(0.20, 0.20, 0.20)
                obj.set_pos(0.0, 3.70, -0.50)
                obj.set_hpr(0, 0, 0)
                obj.set_scale(6.25, 6.25, 6.25)
