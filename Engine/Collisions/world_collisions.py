from panda3d.core import CollisionTraverser, CollisionNode, CollisionHandlerPusher
from panda3d.core import CollisionSphere, CollisionBox
from panda3d.core import CollisionTube, CollisionCapsule
from panda3d.core import CollideMask, BitMask32


class WorldCollisions:

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

        self.envCS = None
        self.envColliderNode = None
        self.envCollider = None

        # We will detect the height of the terrain by creating a collision
        # solid and casting it downward toward the terrain.  One solid will
        # start above env head, and the other will start above the camera.
        # A solid may hit the terrain, or it may hit a rock or a tree.  If it
        # hits the terrain, we can detect the height.  If it hits anything
        # else, we rule that the move is illegal.
        self.cTrav = CollisionTraverser()
        self.pusher = CollisionHandlerPusher()
        self.env = None

        self.goodMask = BitMask32(0x1)
        self.badMask = BitMask32(0x2)
        self.floorMask = BitMask32(0x4)

    def set_env_collider(self, col_name, scene):
        if (col_name
                and isinstance(col_name, str) and scene):
            # Tubes are defined by their start-points, end-points, and radius.
            # In this first case, the tube goes from (-8, 0, 0) to (8, 0, 0),
            # and has a radius of 0.2.
            self.envCS = CollisionSphere(0, 0, 0, 2.25)
            self.envColliderNode = CollisionNode(str(scene))
            self.envColliderNode.addSolid(self.envCS)
            self.envColliderNode.setFromCollideMask(CollideMask.allOff())
            self.envColliderNode.setIntoCollideMask(self.badMask)

            self.envCollider = scene.attachNewNode(self.envColliderNode)
            
            # Show the collision solid
            if self.game_settings['Debug']['set_debug_mode'] == "YES":
                self.envCollider.show()
