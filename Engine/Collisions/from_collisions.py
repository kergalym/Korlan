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

    def set_inter_collision(self, player):
        if player:
            self.korlan = player
            assets = base.asset_nodes_assoc_collector()
            self.actor = assets.get('NPC')

            # Here we set collider for player-followed camera
            self.set_camera_collider(col_name="CamCS")

            # Here we set collider for our actor
            actor_head_col = self.set_actor_collider(actor=self.korlan,
                                                     col_name='Korlan:head_CS',
                                                     axis=(0, 0, 2),
                                                     radius=0.5)

            actor_hips_col = self.set_actor_collider(actor=self.korlan,
                                                     col_name='Korlan:hips_CS',
                                                     axis=(0, 0, 1),
                                                     radius=1.0)

            # Here we set collider handler for our actor
            self.set_actor_collider_handler(actor=self.korlan,
                                            player_collider=actor_head_col)

            self.set_actor_collider_handler(actor=self.korlan,
                                            player_collider=actor_hips_col)

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
