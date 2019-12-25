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

from panda3d.core import *


class Collisions:

    def __init__(self):
        self.cTrav = CollisionTraverser()
        self.player = None
        self.npc = None
        self.animals = None
        self.terrain = None
        self.ground = None
        self.notifier = CollisionHandlerEvent()
        self.notifier.addInPattern(" % fn - in - % in")

    def player_col(self, player):
        if player:
            self.player = player
            player_cs = CollisionSphere(0, 0, 1, 1.1)
            col = player.attachNewNode(CollisionNode('Korlan'))
            col.node().addSolid(player_cs)
            col.show()
            self.cTrav.addCollider(col, self.notifier)

    def ground_col(self, ground):
        if ground:
            self.ground = ground
            ground_cs = CollisionPlane(Plane(Vec3(0, 0, 1), Point3(0, 0, 0)))
            col = ground.attachNewNode(CollisionNode('Ground'))
            col.node().addSolid(ground_cs)
            col.show()
            self.cTrav.addCollider(col, self.notifier)

