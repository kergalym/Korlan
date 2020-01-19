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

from Engine.collisions import Collisions
from direct.task.TaskManagerGlobal import taskMgr

from Engine.world import World
from Settings.Input.keyboard import Keyboard
from Settings.Input.mouse import Mouse
from direct.interval.MetaInterval import Sequence


class Actions:

    def __init__(self):
        self.is_moving = False
        self.is_crouching = False
        self.is_jumping = False
        self.is_hitting = False
        self.base = base
        self.render = render
        self.korlan = None
        self.taskMgr = taskMgr
        self.kbd = Keyboard()
        self.mouse = Mouse()
        self.col = Collisions()
        self.world = World()

    """ Prepares actions for scene"""

    def scene_actions_init(self, player, anims):
        if (player
                and anims
                and isinstance(anims, dict)):
            self.kbd.kbd_init()
            self.kbd.kbd_init_released()

            taskMgr.add(self.player_init, "moveTask",
                        extraArgs=[player, anims],
                        appendTask=True)

            # Set up the camera
            self.base.camera.setPos(player.getX(), player.getY() + 40, 2)

            self.col.set_inter_collision(player)

            # Accepts arrow keys to move either the player or the menu cursor,
            # Also deals with grid checking and collision detection

    """ Prepares the player for scene """

    def player_init(self, player, anims, task):
        # Save the player initial position so that we can restore it,
        # in case he falls off the map or runs into something.
        startpos = player.getPos()

        # Here we accept keys
        self.player_movement_action(player, anims)
        self.player_any_action(player, "attack", anims, "Korlan-Boxing.egg", self.is_hitting)
        self.player_any_action(player, "h_attack", anims, "Korlan-Kicking_3.egg", self.is_hitting)
        self.player_any_action(player, "f_attack", anims, "Korlan-Kicking_5.egg", self.is_hitting)
        self.player_crouch_action(player, 'crouch', anims)
        self.player_any_action(player, "jump", anims, "Korlan-Jumping.egg", self.is_jumping)

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
        self.col.cTrav.traverse(self.render)

        # Adjust player's Z coordinate.  If player ray hit terrain,
        # update his Z. If it hit anything else, or didn't hit anything, put
        # him back where he was last frame.
        entries = list(self.col.korlanGroundHandler.getEntries())
        entries.sort(key=lambda x: x.getSurfacePoint(self.render).getZ())

        if len(entries) > 0 and entries[0].getIntoNode().getName() == 'mountain':
            player.setZ(0.0)
        else:
            player.setPos(startpos)

        # Keep the camera at one foot above the terrain,
        # or two feet above player, whichever is greater.

        entries = list(self.col.camGroundHandler.getEntries())
        entries.sort(key=lambda x: x.getSurfacePoint(self.render).getZ())

        if len(entries) > 0 and entries[0].getIntoNode().getName() == 'mountain':
            self.base.camera.setZ(entries[0].getSurfacePoint(self.render).getZ() + 1.0)
        if self.base.camera.getZ() < player.getZ() + 2.0:
            self.base.camera.setZ(player.getZ() + 2.0)

        # The camera should look in Korlan direction,
        # but it should also try to stay horizontal, so look at
        # a floater which hovers above Korlan's head.

        self.base.camera.lookAt(self.mouse.set_floater(player))

        return task.cont

    def player_movement_action(self, player, anims):
        if player and isinstance(anims, dict):
            # Get the time that elapsed since last frame.  We multiply this with
            # the desired speed in order to find out with which distance to move
            # in order to achieve that desired speed.
            dt = globalClock.getDt()
            # If a move-key is pressed, move the player in the specified direction.
            speed = 5

            if self.kbd.keymap["left"]:
                self.set_player_pos(player, player.getY)
                player.setH(player.getH() + 300 * dt)
            if self.kbd.keymap["right"]:
                self.set_player_pos(player, player.getY)
                player.setH(player.getH() - 300 * dt)
            if self.kbd.keymap["forward"]:
                self.set_player_pos(player, player.getY)
                player.setY(player, -speed * dt)
            if self.kbd.keymap["backward"]:
                self.set_player_pos(player, player.getY)
                player.setY(player, speed * dt)

            # If the player does action, loop the animation.
            # If it is standing still, stop the animation.
            if (self.kbd.keymap["forward"]
                    or self.kbd.keymap["backward"]
                    or self.kbd.keymap["left"]
                    or self.kbd.keymap["right"]):
                if self.is_moving is False and self.is_crouching is False:
                    player.loop(anims["Korlan-Walking.egg"])
                    player.setPlayRate(1.0, anims["Korlan-Walking.egg"])
                    self.set_player_pos(player, player.getY)
                    self.is_moving = True
                    self.is_crouching = False
                elif self.is_moving is False and self.is_crouching:
                    player.loop(anims["Korlan-crouch_walking_forward.egg"])
                    player.setPlayRate(1.0, anims["Korlan-crouch_walking_forward.egg"])
                    self.set_player_pos(player, player.getY)
                    self.is_moving = True
                    self.is_crouching = True
            else:
                if self.is_moving and self.is_crouching is False:
                    player.stop()
                    player.pose(anims["Korlan-Walking.egg"], 0)
                    self.set_player_pos(player, player.getY)
                    self.is_moving = False
                    self.is_crouching = False
                elif self.is_moving and self.is_crouching:
                    player.stop()
                    player.pose(anims["Korlan-crouch_walking_forward.egg"], 0)
                    self.set_player_pos(player, player.getY)
                    self.is_moving = False
                    self.is_crouching = False

    def player_crouch_action(self, player, key, anims):
        if (player and isinstance(anims, dict)
                and isinstance(key, str)):

            # Save player position
            self.set_player_pos(player, player.getY)

            # If the player does action, play the animation.
            if self.kbd.keymap[key]:
                crouched_to_standing = player.getAnimControl('Korlan-crouched_to_standing.egg')
                standing_to_crouch = player.getAnimControl('Korlan-standing_to_crouch.egg')

                if crouched_to_standing.isPlaying() is False and self.is_crouching is False:
                    player.play(anims['Korlan-standing_to_crouch.egg'])
                    player.setPlayRate(1.0, anims['Korlan-standing_to_crouch.egg'])
                    self.set_player_pos(player, player.getY)
                    self.is_crouching = True
                if standing_to_crouch.isPlaying() is False and self.is_crouching:
                    player.play(anims['Korlan-crouched_to_standing.egg'])
                    player.setPlayRate(1.0, anims['Korlan-crouched_to_standing.egg'])
                    self.set_player_pos(player, player.getY)
                    self.is_crouching = False

    def player_any_action(self, player, key, anims, action, state):
        if (player and isinstance(anims, dict)
                and isinstance(action, str)
                and isinstance(key, str)
                and isinstance(state, bool)):
            self.set_player_pos(player, player.getY)
            crouched_to_standing = player.getAnimControl('Korlan-crouched_to_standing.egg')
            if self.kbd.keymap[key]:
                if (state is False
                        and crouched_to_standing.isPlaying() is False
                        and self.is_crouching is True):
                    # TODO: Use blending for smooth transition between animations
                    # Do an animation sequence if player is crouched.
                    crouch_to_stand_seq = player.actorInterval(anims['Korlan-crouched_to_standing.egg'],
                                                               playRate=1.0)
                    any_action_seq = player.actorInterval(action, playRate=1.0)
                    Sequence(crouch_to_stand_seq, any_action_seq).start()
                    self.is_crouching = False
                    self.set_player_pos(player, player.getY)
                elif (state is False
                      and crouched_to_standing.isPlaying() is False
                      and self.is_crouching is False):
                    player.play(action)
                    player.setPlayRate(1.0, action)
                    self.set_player_pos(player, player.getY)

    """ Sets current player position after action """

    def set_player_pos(self, player, pos_y):
        if (player and pos_y
                and isinstance(pos_y, float)):
            player.setY(pos_y)

