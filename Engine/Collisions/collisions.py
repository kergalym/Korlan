from panda3d.core import CollisionTraverser, CollisionNode, CollisionSphere, CollisionBox, BitMask32, \
    CollisionHandlerPusher
from panda3d.core import CollisionHandlerQueue, CollisionRay
from panda3d.core import CollideMask


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

        self.korlanCS = None
        self.korlanCol = None
        self.korlanColNp = None
        self.korlanColHandler = None

        self.camCS = None
        self.camCol = None
        self.camColNp = None
        self.camColHandler = None

        self.actorCS = None
        self.actorCol = None
        self.actorColNp = None
        self.actorColHandler = None

        self.cTrav = None
        self.pusher = CollisionHandlerPusher()
        self.korlan = None
        self.actor = None

        self.goodMask = BitMask32(0x1)
        self.badMask = BitMask32(0x2)
        self.floorMask = BitMask32(0x4)

    def collision_init(self, player, start_pos):
        if player and start_pos:
            self.korlan = player
            assets = base.asset_nodes_assoc_collector()
            self.actor = assets['NPC']

            # We would have to call traverse() to check for collisions.
            self.cTrav.traverse(self.render)

            # TODO: fixme!
            if self.game_settings['Debug']['set_debug_mode'] == "NO":
                self.detect_player_in(start_pos=start_pos)

            self.detect_camera_in()

            self.detect_actor_in(start_pos=start_pos)

    def set_inter_collision(self, player):
        if player:
            self.korlan = player
            assets = base.asset_nodes_assoc_collector()
            self.actor = assets.get('NPC')

            # We will detect the height of the terrain by creating a collision
            # solid and casting it downward toward the terrain.  One solid will
            # start above actor head, and the other will start above the camera.
            # A solid may hit the terrain, or it may hit a rock or a tree.  If it
            # hits the terrain, we can detect the height.  If it hits anything
            # else, we rule that the move is illegal.
            self.cTrav = CollisionTraverser()

            self.set_player_collider(col_name='KorlanCS')
            # TODO: fixme!
            if self.game_settings['Debug']['set_debug_mode'] == "YES":
                self.set_player_collider_multi_test(col_name='KorlanCS')

            self.set_camera_collider(col_name="CamCS")

            # TODO: fixme!
            # self.set_actor_collider(col_name="{0}CS".format(self.actor.getName()))
            if self.game_settings['Debug']['set_debug_mode'] == "YES":
                self.pusher.setHorizontal(True)

            # Show a visual representation of the collisions occuring
            if self.game_settings['Debug']['set_debug_mode'] == "YES":
                self.cTrav.showCollisions(render)

    """ Detects colliding with "in" (inactive) objects for player
        and moves the player.  
    """

    def detect_player_in(self, start_pos):
        if start_pos:
            # Adjust player Z coordinate.  If player ray hit terrain,
            # update his Z. If it hit anything else, or didn't hit anything, put
            # him back where he was last frame.
            entries = list(self.korlanColHandler.getEntries())
            entries.sort(key=lambda x: x.getSurfacePoint(self.render).getZ())

            base.collide_item_name = {}
            if (len(entries) > 0
                    and entries[0].getIntoNode().getName() == 'mountain'):
                base.collide_item_name['name'] = entries[0].getIntoNode()
                base.collide_item_name['type'] = base.item_player_access_codes['NOT_USABLE']
                self.korlan.setZ(0.0)
            elif (len(entries) > 0
                  and entries[0].getIntoNode().getName() == 'Box'):
                print(entries[0].getIntoNode())
                base.collide_itema_name['name'] = entries[0].getIntoNode()
                base.collide_item_name['type'] = base.item_player_access_codes['USABLE']
                self.korlan.setZ(0.0)
            else:
                self.korlan.setPos(start_pos)

    """ Detects colliding with "in" (inactive) objects for player
        and moves camera to follow the player.  
    """

    def detect_camera_in(self):
        entries = list(self.camColHandler.getEntries())
        entries.sort(key=lambda x: x.getSurfacePoint(self.render).getZ())

        # Keep the camera at one foot above the terrain,
        # or two feet above player, whichever is greater.
        if (len(entries) > 0
                and entries[0].getIntoNode().getName() == 'mountain'):
            self.base.camera.setZ(entries[0].getSurfacePoint(self.render).getZ() + 1.0)
        if self.base.camera.getZ() < self.korlan.getZ() + 2.0:
            self.base.camera.setZ(self.korlan.getZ() + 2.0)

    def detect_actor_in(self, start_pos):
        if start_pos:
            if hasattr(self.actorColHandler, 'getEntries'):
                entries = list(self.actorColHandler.getEntries())
                entries.sort(key=lambda x: x.getSurfacePoint(self.render).getZ())

                if len(entries) > 0 and entries[0].getIntoNode().getName() == 'mountain':
                    self.actor.setZ(0.0)
                else:
                    self.actor.setPos(start_pos)

    def set_player_collider(self, col_name):
        if col_name and isinstance(col_name, str):
            self.korlanCS = CollisionRay()
            self.korlanCS.setOrigin(0, 0, 9)
            self.korlanCS.setDirection(0, 0, -1)
            self.korlanCol = CollisionNode(col_name)
            self.korlanCol.addSolid(self.korlanCS)
            self.korlanCol.setFromCollideMask(CollideMask.bit(0))
            self.korlanCol.setIntoCollideMask(CollideMask.allOff())

            self.korlanColNp = self.korlan.attachNewNode(self.korlanCol)
            self.korlanColHandler = CollisionHandlerQueue()

            self.cTrav.addCollider(self.korlanColNp,
                                   self.korlanColHandler)

            if self.game_settings['Debug']['set_debug_mode'] == "YES":
                self.korlanColNp.show()

    def set_player_collider_multi_test(self, col_name):
        if col_name and isinstance(col_name, str):
            self.korlanCS = CollisionSphere(0, 0, 0, 1)
            self.korlanCol = CollisionNode(col_name)
            self.korlanCol.addSolid(self.korlanCS)
            self.korlanCol.setFromCollideMask(CollideMask.bit(0))
            self.korlanCol.setIntoCollideMask(CollideMask.allOff())
            # Make self.korlanColNp a list including all joint collision solids

            korlan = {}
            self.korlanColNp = {}

            for joint in self.korlan.getJoints():
                if joint.getName():
                    korlan[joint.getName()] = self.korlan.exposeJoint(None, "modelRoot", joint.getName())
                    self.korlanColNp[joint.getName()] = korlan[joint.getName()].attachNewNode(self.korlanCol)

            # Add only parent player collider because we have child colliders on it
            self.cTrav.addCollider(self.korlanColNp['Korlan:Hips'],
                                   self.pusher)

            # Show the collision solids
            if self.game_settings['Debug']['set_debug_mode'] == "YES":
                for key in self.korlanColNp:
                    self.korlanColNp[key].show()

    def set_camera_collider(self, col_name):
        if col_name and isinstance(col_name, str):
            self.camCS = CollisionRay()
            self.camCS.setOrigin(0, 0, 9)
            self.camCS.setDirection(0, 0, -1)
            self.camCol = CollisionNode(col_name)
            self.camCol.addSolid(self.camCS)
            self.camCol.setFromCollideMask(CollideMask.bit(0))
            self.camCol.setIntoCollideMask(CollideMask.allOff())
            self.camColNp = self.base.camera.attachNewNode(self.camCol)
            self.camColHandler = CollisionHandlerQueue()
            self.cTrav.addCollider(self.camColNp, self.camColHandler)

            # Show the collision solid
            if self.game_settings['Debug']['set_debug_mode'] == "YES":
                self.camColNp.show()

    def set_actor_collider(self, col_name):
        if col_name and isinstance(col_name, str):
            self.actorCS = CollisionRay()
            self.actorCS.setOrigin(0, 0, 9)
            self.actorCS.setDirection(0, 0, -1)
            self.actorCol = CollisionNode(col_name)
            self.actorCol.addSolid(self.actorCS)
            self.actorCol.setFromCollideMask(CollideMask.bit(0))
            self.actorCol.setIntoCollideMask(CollideMask.allOff())
            self.actorColNp = self.actor.attachNewNode(self.actorCol)
            self.actorColHandler = CollisionHandlerQueue()
            self.cTrav.addCollider(self.actorColNp, self.actorColHandler)

            # Show the collision solid
            if self.game_settings['Debug']['set_debug_mode'] == "YES":
                self.actorColNp.show()
