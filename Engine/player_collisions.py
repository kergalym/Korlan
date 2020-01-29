from panda3d.core import CollisionTraverser, CollisionNode
from panda3d.core import CollisionHandlerQueue, CollisionRay
from panda3d.core import CollideMask


class PlayerCollisions:

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
        self.cTrav = None
        self.korlan = None
        self.npc = None
        self.animals = None
        self.terrain = None

    def collision_init(self, player, start_pos):
        if player and start_pos:
            # We would have to call traverse() to check for collisions.
            self.cTrav.traverse(self.render)

            # Adjust player's Z coordinate.  If player ray hit terrain,
            # update his Z. If it hit anything else, or didn't hit anything, put
            # him back where he was last frame.
            entries = list(self.korlanGroundHandler.getEntries())
            entries.sort(key=lambda x: x.getSurfacePoint(self.render).getZ())

            if len(entries) > 0 and entries[0].getIntoNode().getName() == 'mountain':
                player.setZ(0.0)
            else:
                player.setPos(start_pos)

            # Keep the camera at one foot above the terrain,
            # or two feet above player, whichever is greater.

            entries = list(self.camGroundHandler.getEntries())
            entries.sort(key=lambda x: x.getSurfacePoint(self.render).getZ())

            if len(entries) > 0 and entries[0].getIntoNode().getName() == 'mountain':
                self.base.camera.setZ(entries[0].getSurfacePoint(self.render).getZ() + 1.0)
            if self.base.camera.getZ() < player.getZ() + 2.0:
                self.base.camera.setZ(player.getZ() + 2.0)

    def set_inter_collision(self, korlan):
        if korlan:
            self.korlan = korlan
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

            # Uncomment this line to see the collision rays
            # self.korlanGroundColNp.show()
            # self.camGroundColNp.show()

            # Uncomment this line to show a visual representation of the
            # collisions occuring
            # self.cTrav.showCollisions(render)
