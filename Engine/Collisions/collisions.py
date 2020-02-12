from panda3d.core import CollisionTraverser, CollisionHandlerPusher
from panda3d.core import CollisionSphere, CollisionBox
from panda3d.core import CollisionTube, CollisionRay
from panda3d.core import CollideMask, BitMask32
from panda3d.core import CollisionNode, Point3
from direct.showbase.PhysicsManagerGlobal import physicsMgr


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

        self.c_trav = CollisionTraverser()
        self.c_pusher = CollisionHandlerPusher()
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
            box.setTag(key=box.get_name(), value='1')
            # Here we set collider for player-followed camera
            self.set_camera_collider(col_name="CamCS")

            # Here we set collider for our actor
            # self.set_actor_collider_multi_solid()

            self.set_actor_collider_multi_joint(actor=self.korlan,
                                                col_name='Korlan:CS',
                                                axis=(0, 0, 0),
                                                radius=2.2)

            self.c_pusher.add_in_pattern('into-%in')
            # self.event.addAgainPattern('%fn-again-%in')
            self.c_pusher.add_out_pattern('outof-%in')

            self.c_pusher.set_horizontal(True)

            # Show a visual representation of the collisions occuring
            if self.game_settings['Debug']['set_debug_mode'] == "YES":
                self.c_trav.showCollisions(render)

    def set_actor_collider_multi_solid(self):
        actor_head_col = self.set_actor_collider(actor=self.korlan,
                                                 col_name='Korlan:head_CS',
                                                 axis=(0, -0.1, 1.3),
                                                 radius=0.2)

        actor_chest_col = self.set_actor_collider(actor=self.korlan,
                                                  col_name='Korlan:chest_CS',
                                                  axis=(0, 0, 1),
                                                  radius=0.2)

        actor_pelvis_col = self.set_actor_collider(actor=self.korlan,
                                                   col_name='Korlan:pelvis_CS',
                                                   axis=(0, 0, 0.7),
                                                   radius=0.2)

        actor_r_leg_col = self.set_actor_collider(actor=self.korlan,
                                                  col_name='Korlan:r_leg_CS',
                                                  axis=(0.1, -0.1, 0.4),
                                                  radius=0.2)
        actor_r_foot_col = self.set_actor_collider(actor=self.korlan,
                                                   col_name='Korlan:r_foot_CS',
                                                   axis=(0.1, -0.1, 0.2),
                                                   radius=0.2)

        actor_l_leg_col = self.set_actor_collider(actor=self.korlan,
                                                  col_name='Korlan:l_leg_CS',
                                                  axis=(-0.1, -0.1, 0.4),
                                                  radius=0.2)
        actor_l_foot_col = self.set_actor_collider(actor=self.korlan,
                                                   col_name='Korlan:l_foot_CS',
                                                   axis=(-0.1, -0.1, 0.2),
                                                   radius=0.2)

        # Here we set collider handler for our actor
        self.set_actor_collider_handler(actor=self.korlan,
                                        player_collider=actor_head_col)

        self.set_actor_collider_handler(actor=self.korlan,
                                        player_collider=actor_chest_col)

        self.set_actor_collider_handler(actor=self.korlan,
                                        player_collider=actor_pelvis_col)

        self.set_actor_collider_handler(actor=self.korlan,
                                        player_collider=actor_r_leg_col)

        self.set_actor_collider_handler(actor=self.korlan,
                                        player_collider=actor_r_foot_col)

        self.set_actor_collider_handler(actor=self.korlan,
                                        player_collider=actor_l_leg_col)

        self.set_actor_collider_handler(actor=self.korlan,
                                        player_collider=actor_l_foot_col)

    def set_actor_collider_multi_joint(self, actor, col_name, axis, radius):
        if (actor
                and col_name
                and isinstance(col_name, str)
                and isinstance(axis, tuple)
                and isinstance(radius, float)
                or isinstance(radius, int)):
            player_collider_node = CollisionNode(col_name)
            player_cs = CollisionSphere(axis, radius)
            player_collider_node.add_solid(player_cs)

            # Make self.korlanCollider a list including all joint collision solids
            korlan = {}
            player_collider = {}

            for joint in self.korlan.get_joints():
                if joint.get_name():
                    # import pdb;pdb.set_trace()
                    korlan[joint.get_name()] = self.korlan.expose_joint(None, "modelRoot", joint.get_name())
                    player_collider[joint.get_name()] = korlan[joint.get_name()].attach_new_node(
                        player_collider_node)

            # Add only parent player collider because we have child colliders on it
            for key in player_collider:
                self.c_pusher.addCollider(player_collider[key],
                                          self.korlan)

                self.c_trav.addCollider(player_collider[key],
                                        self.c_pusher)

            # Show the collision solids
            if self.game_settings['Debug']['set_debug_mode'] == "YES":
                for key in player_collider:
                    player_collider[key].show()
            else:
                for key in player_collider:
                    player_collider[key].show()

    def set_actor_collider(self, actor, col_name, axis, radius):
        if (actor
                and col_name
                and isinstance(col_name, str)
                and isinstance(axis, tuple)
                and isinstance(radius, float)
                or isinstance(radius, int)):
            player_collider_node = CollisionNode(col_name)
            player_cs = CollisionSphere(axis, radius)
            player_collider_node.add_solid(player_cs)
            player_collider = actor.attach_new_node(player_collider_node)

            return player_collider

    def set_actor_collider_handler(self, actor, player_collider):
        if player_collider and actor:
            self.c_pusher.add_collider(player_collider,
                                       actor)

            self.c_trav.add_collider(player_collider,
                                     self.c_pusher)

            if self.game_settings['Debug']['set_debug_mode'] == "YES":
                player_collider.show()

    def set_camera_collider(self, col_name):
        if col_name and isinstance(col_name, str):
            self.cam_cs = CollisionRay()
            self.cam_cs.set_origin(0, 0, 9)
            self.cam_cs.set_direction(0, 0, -1)
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
