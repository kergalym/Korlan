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

from Engine.Collisions import Collisions
from direct.task.TaskManagerGlobal import taskMgr

from Engine.World import World
from Settings.Input.keyboard import Keyboard
from Settings.Input.mouse import Mouse


class Movement:

    def __init__(self):
        self.isMoving = False
        self.base = base
        self.korlan = None
        self.taskMgr = taskMgr
        self.kbd = Keyboard()
        self.mouse = Mouse()
        self.col = Collisions()
        self.world = World()

    def movement_init(self, player, anim):
        if (player
                and anim
                and isinstance(anim, str)):

            # self.mouse.set_floater(self.korlan)

            self.kbd.kbd_init()

            taskMgr.add(self.player_movement, "moveTask",
                        extraArgs=[player, anim],
                        appendTask=True)

            # Set up the camera
            self.base.camera.setPos(player.getX(), player.getY() + 10, 2)

            self.col.set_inter_collision(player)

            # Accepts arrow keys to move either the player or the menu cursor,
            # Also deals with grid checking and collision detection

    def player_movement(self, player, anim, task):
        # Get the time that elapsed since last frame.  We multiply this with
        # the desired speed in order to find out with which distance to move
        # in order to achieve that desired speed.
        dt = globalClock.getDt()

        # If the camera-left key is pressed, move camera left.
        # If the camera-right key is pressed, move camera right.

        if self.kbd.keymap["cam-left"]:
            self.base.camera.setX(self.base.camera, -20 * dt)
        if self.kbd.keymap["cam-right"]:
            self.base.camera.setX(self.base.camera, +20 * dt)

        # Save the player initial position so that we can restore it,
        # in case he falls off the map or runs into something.

        startpos = player.getPos()

        # If a move-key is pressed, move the player in the specified direction.

        speed = 25

        if self.kbd.keymap["left"]:
            player.setH(player.getH() + 180 * dt)
            player.setX(player, speed * dt)
        if self.kbd.keymap["right"]:
            player.setH(player.getH() - 180 * dt)
            player.setX(player, -speed * dt)
        if self.kbd.keymap["forward"]:
            player.setY(player, -speed * dt)
        if self.kbd.keymap["backward"]:
            player.setY(player, speed * dt)

        # If the player is moving, loop the run animation.
        # If it is standing still, stop the animation.

        if (self.kbd.keymap["forward"]
                or self.kbd.keymap["backward"]
                or self.kbd.keymap["left"]
                or self.kbd.keymap["right"]):
            if self.isMoving is False:
                player.loop(anim)
                player.setPlayRate(8.0, anim)
                self.isMoving = True
        else:
            if self.isMoving:
                player.stop()
                player.pose(anim, 0)
                self.isMoving = False

        # If the camera is too far from player, move it closer.
        # If the camera is too close to player, move it farther.

        camvec = player.getPos() - self.base.camera.getPos()
        camvec.setZ(0)
        camdist = camvec.length()
        camvec.normalize()
        if camdist > 10.0:
            self.base.camera.setPos(self.base.camera.getPos() + camvec * (camdist - 10))
            camdist = 10.0
        if camdist < 5.0:
            self.base.camera.setPos(self.base.camera.getPos() - camvec * (5 - camdist))
            camdist = 5.0

        # We would have to call traverse() to check for collisions.
        self.col.cTrav.traverse(render)

        # Adjust player's Z coordinate.  If player ray hit terrain,
        # update his Z. If it hit anything else, or didn't hit anything, put
        # him back where he was last frame.
        entries = list(self.col.korlanGroundHandler.getEntries())
        entries.sort(key=lambda x: x.getSurfacePoint(render).getZ())

        if len(entries) > 0 and entries[0].getIntoNode().getName() == 'mountain':
            player.setZ(entries[0].getSurfacePoint(render).getZ())
        else:
            player.setPos(startpos)

        # Keep the camera at one foot above the terrain,
        # or two feet above player, whichever is greater.

        entries = list(self.col.camGroundHandler.getEntries())
        entries.sort(key=lambda x: x.getSurfacePoint(render).getZ())

        if len(entries) > 0 and entries[0].getIntoNode().getName() == 'mountain':
            self.base.camera.setZ(entries[0].getSurfacePoint(render).getZ() + 1.0)
        if self.base.camera.getZ() < player.getZ() + 2.0:
            self.base.camera.setZ(player.getZ() + 2.0)

        # The camera should look in Korlan direction,
        # but it should also try to stay horizontal, so look at
        # a floater which hovers above Korlan's head.

        self.base.camera.lookAt(self.mouse.set_floater(player))

        return task.cont
