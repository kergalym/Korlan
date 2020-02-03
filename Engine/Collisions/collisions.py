from panda3d.core import CollisionTraverser, CollisionNode
from panda3d.core import CollisionHandlerQueue, CollisionRay
from panda3d.core import CollideMask


class Collisions:

    def __init__(self):
        self.base = base
        self.render = render

        self.korlanGroundRay = None
        self.korlanGroundCol = None
        self.korlanGroundColNp = None
        self.korlanGroundHandler = None

        self.camGroundRay = None
        self.camGroundCol = None
        self.camGroundColNp = None
        self.camGroundHandler = None

        self.actorGroundRay = None
        self.actorGroundCol = None
        self.actorGroundColNp = None
        self.actorGroundHandler = None

        self.cTrav = None
        self.korlan = None
        self.actor = None

    def collision_init(self, player, start_pos):
        if player and start_pos:
            self.korlan = player
            assets = base.asset_nodes_assoc_collector()
            self.actor = assets['NPC']

            # We would have to call traverse() to check for collisions.
            self.cTrav.traverse(self.render)

            # Adjust player's Z coordinate.  If player ray hit terrain,
            # update his Z. If it hit anything else, or didn't hit anything, put
            # him back where he was last frame.

            entries_player = list(self.korlanGroundHandler.getEntries())
            entries_player.sort(key=lambda x: x.getSurfacePoint(self.render).getZ())

            # Player collisions tracking
            # print("1:", entries_player_item, "\n")

            base.collide_item_name = {}
            if (len(entries_player) > 0
                    and entries_player[0].getIntoNode().getName() == 'mountain'):
                base.collide_item_name['name'] = entries_player[0].getIntoNode().getName()
                base.collide_item_name['type'] = base.item_player_access_codes['NOT_USABLE']
                self.korlan.setZ(0.0)
            else:
                self.korlan.setPos(start_pos)

            entries_cam = list(self.camGroundHandler.getEntries())
            entries_cam.sort(key=lambda x: x.getSurfacePoint(self.render).getZ())

            # Keep the camera at one foot above the terrain,
            # or two feet above player, whichever is greater.
            if (len(entries_cam) > 0
                    and entries_cam[0].getIntoNode().getName() == 'mountain'):
                self.base.camera.setZ(entries_cam[0].getSurfacePoint(self.render).getZ() + 1.0)
            if self.base.camera.getZ() < self.korlan.getZ() + 2.0:
                self.base.camera.setZ(self.korlan.getZ() + 2.0)

            elif hasattr(self.actorGroundHandler, 'getEntries'):
                print("actorGroundHandler Entries here")
                entries_actor = list(self.actorGroundHandler.getEntries())
                entries_actor.sort(key=lambda x: x.getSurfacePoint(self.render).getZ())

                # Actor (NPC) collisions tracking
                if len(entries_actor) > 0 and entries_actor[0].getIntoNode().getName() == 'mountain':
                    self.actor.setZ(0.0)
                else:
                    self.actor.setPos(start_pos)

    def set_inter_collision(self, player):
        if player:
            self.korlan = player
            assets = base.asset_nodes_assoc_collector()
            self.actor = assets['NPC']
            # We will detect the height of the terrain by creating a collision
            # ray and casting it downward toward the terrain.  One ray will
            # start above Korlan's head, and the other will start above the camera.
            # A ray may hit the terrain, or it may hit a rock or a tree.  If it
            # hits the terrain, we can detect the height.  If it hits anything
            # else, we rule that the move is illegal.
            self.cTrav = CollisionTraverser()
            self.korlanGroundRay = CollisionRay()
            self.korlanGroundRay.setOrigin(0, 0, 9)
            self.korlanGroundRay.setDirection(0, 0, -1)
            self.korlanGroundCol = CollisionNode('KorlanRay')
            self.korlanGroundCol.addSolid(self.korlanGroundRay)
            self.korlanGroundCol.setFromCollideMask(CollideMask.bit(0))
            self.korlanGroundCol.setIntoCollideMask(CollideMask.allOff())
            self.korlanGroundColNp = self.korlan.attachNewNode(self.korlanGroundCol)
            self.korlanGroundHandler = CollisionHandlerQueue()
            self.cTrav.addCollider(self.korlanGroundColNp, self.korlanGroundHandler)

            self.camGroundRay = CollisionRay()
            self.camGroundRay.setOrigin(0, 0, 9)
            self.camGroundRay.setDirection(0, 0, -1)
            self.camGroundCol = CollisionNode('camRay')
            self.camGroundCol.addSolid(self.camGroundRay)
            self.camGroundCol.setFromCollideMask(CollideMask.bit(0))
            self.camGroundCol.setIntoCollideMask(CollideMask.allOff())
            self.camGroundColNp = self.base.camera.attachNewNode(self.camGroundCol)
            self.camGroundHandler = CollisionHandlerQueue()
            self.cTrav.addCollider(self.camGroundColNp, self.camGroundHandler)

            if self.actor:
                self.actorGroundRay = CollisionRay()
                self.actorGroundRay.setOrigin(0, 0, 9)
                self.actorGroundRay.setDirection(0, 0, -1)
                self.actorGroundCol = CollisionNode('{0}Ray'.format(self.actor))
                self.actorGroundCol.addSolid(self.actorGroundRay)
                self.actorGroundCol.setFromCollideMask(CollideMask.bit(0))
                self.actorGroundCol.setIntoCollideMask(CollideMask.allOff())
                self.actorGroundColNp = self.actor.attachNewNode(self.actorGroundCol)
                self.actorGroundHandler = CollisionHandlerQueue()
                self.cTrav.addCollider(self.actorGroundColNp, self.actorGroundHandler)

                # Uncomment this line to see the collision rays
                # self.actorGroundColNp.show()
                # self.actorItemColNp.show()

                # Uncomment this line to show a visual representation of the
                # collisions occuring
                # self.cTrav.showCollisions(render)

            # Uncomment this line to see the collision rays
            # self.korlanGroundColNp.show()
            # self.camGroundColNp.show()

            # Uncomment this line to show a visual representation of the
            # collisions occuring
            # self.cTrav.showCollisions(render)

