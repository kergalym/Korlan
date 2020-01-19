"""
BSD 3-Clause License

Copyright (c) 2019, Galym Kerimbekov
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its
   contributors may be used to endorse or promote products derived from
   this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

from panda3d.core import CollisionTraverser, CollisionNode
from panda3d.core import CollisionHandlerQueue, CollisionRay
from panda3d.core import CollideMask


class Collisions:

    def __init__(self):
        self.base = base
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
