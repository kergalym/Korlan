from direct.task.TaskManagerGlobal import taskMgr
from panda3d.core import BitMask32
from Engine.Collisions.collision_solids import CollisionSolids
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
        self.cs = CollisionSolids()
        self.bs = BulletCollisionSolids()

        self.korlan = None
        self.actor = None

        self.no_mask = BitMask32.allOff()
        self.mask_floor = BitMask32(0x1)
        self.mask_walls = BitMask32(0x2)
        self.mask = BitMask32.allOn()

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
                                    col_name='Korlan:CS',
                                    handler="pusher")

    def set_actor_collider(self, actor, col_name, handler):
        if (actor
                and col_name
                and handler
                and isinstance(col_name, str)
                and isinstance(handler, str)):
            player_bs = self.bs.set_bs_capsule()
            base.bullet_char_contr_node = BulletCharacterControllerNode(player_bs, 0.4, 'Player')
            player_bs_nodepath = self.physics_attr.world_nodepath.attach_new_node(base.bullet_char_contr_node)
            player_bs_nodepath.set_collide_mask(self.mask)
            self.physics_attr.world.attach_character(base.bullet_char_contr_node)
            actor.reparent_to(player_bs_nodepath)
            # Set actor down to make it
            # at the same point as bullet shape
            actor.set_z(-1)
            # Set the bullet shape position same as actor position
            player_bs_nodepath.set_y(actor.get_y())
            # Set actor relative to bullet shape
            actor.set_y(0)

            # TODO: DETACH if base.menu_mode is True

    def set_object_collider(self, col_name, handler, obj):
        if (col_name
                and handler
                and obj
                and isinstance(col_name, str)
                and isinstance(handler, str)):
            object_cs = self.bs.set_bs_cube()
            object_collider_node = BulletRigidBodyNode(col_name)
            object_collider_node.add_solid(object_cs)
            object_collider = obj.attach_new_node(object_collider_node)
