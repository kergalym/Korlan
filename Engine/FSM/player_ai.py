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
from time import sleep

from direct.showbase.DirectObject import DirectObject
from configparser import ConfigParser
from direct.fsm.FSM import FSM
from direct.task.TaskManagerGlobal import taskMgr

from Engine.collisions import Collisions


class FsmPlayer(FSM):
    """ Gameplay logics goes here """

    def __init__(self):
        self.d_object = DirectObject()
        self.cfg_parser = ConfigParser()
        self.is_idle = base.korlan_is_idle
        self.is_moving = base.korlan_is_moving
        self.is_crouching = base.korlan_is_crouching
        self.is_jumping = base.korlan_is_jumping
        self.is_hitting = base.korlan_is_hitting
        self.is_using = base.korlan_is_using
        self.is_blocking = base.korlan_is_blocking
        self.has_sword = base.korlan_has_sword
        self.has_bow = base.korlan_has_bow
        self.has_tengri = base.korlan_has_tengri
        self.has_umai = base.korlan_has_umai
        self.base = base
        self.render = render
        self.korlan = None
        self.avatar = None
        self.taskMgr = taskMgr
        self.col = Collisions()
        FSM.__init__(self, 'FsmPlayer')

    def get_player(self, player):
        if player:
            self.avatar = player


class Walking(FsmPlayer):
    def __init__(self):

        FsmPlayer.__init__(self)

    def enterWalk(self):
        self.avatar.loop('walk')
        # self.snd.footstepsSound.play()
        # self.col.enableDoorCollisions()

    def exitWalk(self):
        self.avatar.stop()
        # self.snd.footstepsSound.stop()


class Idle(FsmPlayer):
    def __init__(self):

        FsmPlayer.__init__(self)

    def enter_idle(self, player, action, state):
        if player and action:
            if state:
                self.avatar = player
                self.avatar.play(action)
                self.avatar.setPlayRate(1.0, action)


class Swimming(FsmPlayer):
    def __init__(self):

        FsmPlayer.__init__(self)


class Staying(FsmPlayer):
    def __init__(self):

        FsmPlayer.__init__(self)


class Jumping(FsmPlayer):
    def __init__(self):

        FsmPlayer.__init__(self)


class Laying(FsmPlayer):
    def __init__(self):

        FsmPlayer.__init__(self)


class Sitting(FsmPlayer):
    def __init__(self):

        FsmPlayer.__init__(self)


class Interacting(FsmPlayer):
    def __init__(self):

        FsmPlayer.__init__(self)


class Life(FsmPlayer):
    def __init__(self):
        FsmPlayer.__init__(self)


class Dying(FsmPlayer):
    def __init__(self):

        FsmPlayer.__init__(self)


class MartialActions(FsmPlayer):
    def __init__(self):

        FsmPlayer.__init__(self)


class MiscActions(FsmPlayer):
    def __init__(self):

        FsmPlayer.__init__(self)

