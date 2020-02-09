from direct.showbase.DirectObject import DirectObject
from configparser import ConfigParser
from direct.fsm.FSM import FSM
from direct.task.TaskManagerGlobal import taskMgr

from Engine.Collisions.collisions import FromCollisions


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
        self.is_h_kicking = base.korlan_is_h_kicking
        self.is_f_kicking = base.korlan_is_f_kicking
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
        self.col = FromCollisions()
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
                self.avatar.setPlayRate(self.base.actor_play_rate, action)


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

