from panda3d.core import CollisionTraverser, CollisionHandlerPusher
from panda3d.core import CollideMask, BitMask32
from panda3d.core import CollisionNode, Point3
from Engine.Collisions.collision_solids import CollisionSolids
from Engine.Collisions.collision_physics import CollisionPhysics

class Collisions:

    def __init__(self):
        self.base = base
        self.render = render
        self.game_settings = base.game_settings
        self.game_dir = base.game_dir
        self.game_cfg = base.game_cfg
        self.game_cfg_dir = base.game_cfg_dir
        self.game_settings_filename = base.game_settings_filename
        self.cfg_path = {"game_config_path":
                         "{0}/{1}".format(self.game_cfg_dir, self.game_settings_filename)}

        self.cam_cs = None
        self.cam_collider_node = None
        self.cam_collider = None

        self.cs = CollisionSolids()
        self.c_trav = CollisionTraverser()
        self.c_pusher = CollisionHandlerPusher()
        self.c_physx = CollisionPhysics()

        self.korlan = None
        self.actor = None

        self.no_mask = BitMask32.bit(0)
        self.mask_floor = BitMask32.bit(1)
        self.mask_walls = BitMask32.bit(2)

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
            # Here we set collider for player-followed camera
            self.set_camera_collider(col_name="CamCS")

            self.set_actor_collider(actor=self.korlan,
                                    col_name='Korlan:CS',
                                    axis=(0, 0, 0.8),
                                    radius=0.6)

            self.c_pusher.add_in_pattern('into-%in')
            # self.c_pusher.addAgainPattern('%fn-again-%in')
            self.c_pusher.add_out_pattern('outof-%in')

            self.c_pusher.set_horizontal(True)

            # Show a visual representation of the collisions occuring
            if self.game_settings['Debug']['set_debug_mode'] == "YES":
                self.c_trav.show_collisions(render)

    def set_actor_collider(self, actor, col_name, axis, radius):
        if (actor
                and col_name
                and isinstance(col_name, str)
                and isinstance(axis, tuple)
                and isinstance(radius, float)
                or isinstance(radius, int)):
            player_collider_node = CollisionNode(col_name)
            player_cs = self.cs.set_cs_sphere(axis, radius)
            player_collider_node.add_solid(player_cs)

            # Make player_collider a dict including collision solid
            player_collider_dict = {
                actor.get_name(): actor.attach_new_node(player_collider_node)
            }
            # Add the pusher and traverser
            self.c_pusher.add_collider(player_collider_dict[actor.get_name()],
                                       actor)

            self.c_trav.add_collider(player_collider_dict[actor.get_name()],
                                     self.c_pusher)

            # Show the collision solids
            if self.game_settings['Debug']['set_debug_mode'] == "YES":
                player_collider_dict[actor.get_name()].show()
            else:
                player_collider_dict[actor.get_name()].show()

    def set_camera_collider(self, col_name):
        if col_name and isinstance(col_name, str):
            self.cam_cs = self.cs.set_cs_ray(origin=(0, 0, 9),
                                             direction=(0, 0, -1))
            self.cam_collider_node = CollisionNode(col_name)
            self.cam_collider_node.add_solid(self.cam_cs)
            self.cam_collider_node.set_from_collide_mask(CollideMask.bit(0))
            self.cam_collider_node.set_into_collide_mask(CollideMask.allOff())

            self.cam_collider = self.base.camera.attach_new_node(self.cam_collider_node)

            self.c_pusher.add_collider(self.cam_collider,
                                       self.korlan)

            self.c_trav.add_collider(self.cam_collider,
                                     self.c_pusher)

            # Show the collision solid
            if self.game_settings['Debug']['set_debug_mode'] == "YES":
                self.cam_collider.show()
