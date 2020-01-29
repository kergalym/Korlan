from panda3d.core import CollisionTraverser, CollisionNode
from panda3d.core import CollisionHandlerQueue, CollisionRay
from panda3d.core import CollideMask


class AnimalCollisions:

    def __init__(self):
        self.base = base
        self.animalGroundRay = None
        self.animalGroundCol = None
        self.animalGroundColNp = None
        self.animalGroundHandler = None
        self.camGroundRay = None
        self.camGroundCol = None
        self.camGroundColNp = None
        self.camGroundHandler = None
        self.cTrav = None
        self.animal = None
        self.npc = None
        self.animals = None
        self.terrain = None

    def set_inter_collision(self, animal):
        if animal:
            self.animal = animal
            # We will detect the height of the terrain by creating a collision
            # ray and casting it downward toward the terrain.  One ray will
            # start above Korlan's head, and the other will start above the camera.
            # A ray may hit the terrain, or it may hit a rock or a tree.  If it
            # hits the terrain, we can detect the height.  If it hits anything
            # else, we rule that the move is illegal.
            self.cTrav = CollisionTraverser()
            self.animalGroundRay = CollisionRay()
            self.animalGroundRay.setOrigin(0, 0, 9)
            self.animalGroundRay.setDirection(0, 0, -1)
            self.animalGroundCol = CollisionNode('KorlanRay')
            self.animalGroundCol.addSolid(self.animalGroundRay)
            self.animalGroundCol.setFromCollideMask(CollideMask.bit(0))
            self.animalGroundCol.setIntoCollideMask(CollideMask.allOff())
            self.animalGroundColNp = self.animal.attachNewNode(self.animalGroundCol)
            self.animalGroundHandler = CollisionHandlerQueue()
            self.cTrav.addCollider(self.animalGroundColNp, self.animalGroundHandler)

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
            # self.animalGroundColNp.show()
            # self.camGroundColNp.show()

            # Uncomment this line to show a visual representation of the
            # collisions occuring
            # self.cTrav.showCollisions(render)
