from panda3d.core import CollisionTraverser, CollisionNode, CollisionHandlerPusher, Point3
from panda3d.core import CollisionSphere, CollisionBox
from panda3d.core import CollisionTube, CollisionRay
from panda3d.core import CollideMask, BitMask32
from direct.showbase.PhysicsManagerGlobal import physicsMgr


class FromCollisions:

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

        self.camCS = None
        self.camColliderNode = None
        self.camCollider = None

        self.cTrav = CollisionTraverser()
        self.pusher = CollisionHandlerPusher()
        self.korlan = None
        self.actor = None

        self.no_mask = BitMask32.bit(0)
        self.mask_floor = BitMask32.bit(1)
        self.mask_walls = BitMask32.bit(2)

    def set_inter_collision(self, player):
        if player:
            self.korlan = player

            # Octree-optimised "into" objects defined here
            assets = base.asset_nodes_assoc_collector()
            mountains = assets.get('Mountains')
            mountains.setCollideMask(self.mask_walls)

            # Here we set collider for player-followed camera
            self.set_camera_collider(col_name="CamCS")

            # Here we set collider for our actor
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

            self.pusher.setHorizontal(True)

            # Show a visual representation of the collisions occuring
            if self.game_settings['Debug']['set_debug_mode'] == "YES":
                self.cTrav.showCollisions(render)

    def set_actor_collider(self, actor, col_name, axis, radius):
        if (actor
                and col_name
                and isinstance(col_name, str)
                and isinstance(axis, tuple)
                and isinstance(radius, float)
                or isinstance(radius, int)):
            playerColliderNode = CollisionNode(col_name)
            playerCS = CollisionSphere(axis, radius)
            playerColliderNode.addSolid(playerCS)
            playerCollider = actor.attachNewNode(playerColliderNode)

            return playerCollider

    def set_actor_collider_handler(self, actor, player_collider):
        if player_collider and actor:
            self.pusher.addCollider(player_collider,
                                    actor)

            self.cTrav.addCollider(player_collider,
                                   self.pusher)

            if self.game_settings['Debug']['set_debug_mode'] == "YES":
                player_collider.show()

    def set_camera_collider(self, col_name):
        if col_name and isinstance(col_name, str):
            self.camCS = CollisionRay()
            self.camCS.setOrigin(0, 0, 9)
            self.camCS.setDirection(0, 0, -1)
            self.camColliderNode = CollisionNode(col_name)
            self.camColliderNode.addSolid(self.camCS)
            self.camColliderNode.setFromCollideMask(CollideMask.bit(0))
            self.camColliderNode.setIntoCollideMask(CollideMask.allOff())

            self.camCollider = self.base.camera.attachNewNode(self.camColliderNode)

            self.pusher.addCollider(self.camCollider,
                                    self.korlan)

            self.cTrav.addCollider(self.camCollider,
                                   self.pusher)
            # Show the collision solid
            if self.game_settings['Debug']['set_debug_mode'] == "YES":
                self.camCollider.show()
