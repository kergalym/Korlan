from panda3d.core import CollisionTraverser, CollisionHandlerPusher
from panda3d.core import CollisionHandlerEvent, CollisionHandlerQueue
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
        self.c_event = CollisionHandlerEvent()
        self.c_queue = CollisionHandlerQueue()
        self.korlan = None
        self.actor = None

        self.no_mask = BitMask32.bit(0)
        self.mask_floor = BitMask32.bit(1)
        self.mask_walls = BitMask32.bit(2)

    def get_queue_event(self, player):
        if player:
            entries_y = list(self.c_queue.get_entries())
            entries_z = list(self.c_queue.get_entries())
            entries_y.sort(key=lambda x: x.getSurfacePoint(render).getY())
            entries_z.sort(key=lambda x: x.getSurfacePoint(render).getZ())

            for event_y, event_z in zip(entries_y, entries_z):
                if event_y.get_into_node().get_name() == 'Box':
                    base.event_item = event_y.get_into_node().get_name()
                    player.set_y(entries_y[0].getSurfacePoint(render).getY())

                elif event_y.get_into_node().get_name() == "mountain":
                    player.set_y(entries_y[0].getSurfacePoint(render).getY())

                elif event_y.get_into_node().get_name() == "Ground":
                    player.set_z(entries_z[0].getSurfacePoint(render).getZ())

    def get_event(self, player, entry):
        if player and entry:
            print(1)
            if entry.get_into_node().get_name():
                player.set_y(0.0)

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

            # TODO: Debug & Fix
            if self.game_settings['Debug']['set_debug_mode'] == "YES":  # YES

                # TODO: Uncomment after debug & fix item attaching

                self.set_actor_collider(actor=self.korlan,
                                        col_name='Korlan:CS',
                                        axis=(0, 0, 0.5),
                                        radius=20.2,
                                        handler='queue')

            else:
                self.set_actor_collider(actor=self.korlan,
                                        col_name='Korlan:CS',
                                        axis=(0, 0, 0),
                                        radius=20.2,
                                        handler='pusher')

                self.c_pusher.add_in_pattern('into-%in')
                # self.event.addAgainPattern('%fn-again-%in')
                self.c_pusher.add_out_pattern('outof-%in')

                self.c_pusher.set_horizontal(True)

            # Show a visual representation of the collisions occuring
            if self.game_settings['Debug']['set_debug_mode'] == "YES":
                self.c_trav.show_collisions(render)

    def set_actor_collider(self, actor, col_name, axis, radius, handler):
        if (actor
                and col_name
                and handler
                and isinstance(col_name, str)
                and isinstance(handler, str)
                and isinstance(axis, tuple)
                and isinstance(radius, float)
                or isinstance(radius, int)):
            player_collider_node = CollisionNode(col_name)
            player_cs = CollisionSphere(axis, radius)
            player_collider_node.add_solid(player_cs)

            # Make player_collider a list including all joint collision solids
            actor_dict = {}
            player_collider_dict = {}
            if handler == "pusher":
                for joint in actor.get_joints():
                    if (joint.get_name() != "Korlan:LeftToe_End"
                            and joint.get_name() != "Korlan:RightToe_End"
                            and joint.get_name() != "Korlan:LeftFoot"
                            and joint.get_name() != "Korlan:RightFoot"
                            and joint.get_name() != "Korlan:LeftToeBase"
                            and joint.get_name() != "Korlan:RightToeBase"):
                        actor_dict[joint.get_name()] = actor.expose_joint(None, "modelRoot", joint.get_name())
                        player_collider_dict[joint.get_name()] = actor_dict[joint.get_name()].attach_new_node(
                            player_collider_node)

            if handler == "queue":
                for joint in actor.get_joints():
                    actor_dict[joint.get_name()] = actor.expose_joint(None, "modelRoot", joint.get_name())
                    player_collider_dict[joint.get_name()] = actor_dict[joint.get_name()].attach_new_node(
                        player_collider_node)

            # Add only parent player collider because we have child colliders on it
            for key in player_collider_dict:
                if handler == "pusher":
                    self.c_pusher.add_collider(player_collider_dict[key],
                                               actor)

                    self.c_trav.add_collider(player_collider_dict[key],
                                             self.c_pusher)
                elif handler == "queue":
                    self.c_trav.add_collider(player_collider_dict[key],
                                             self.c_queue)

            # Show the collision solids
            if self.game_settings['Debug']['set_debug_mode'] == "YES":
                for key in player_collider_dict:
                    player_collider_dict[key].show()
            else:
                for key in player_collider_dict:
                    player_collider_dict[key].show()

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
