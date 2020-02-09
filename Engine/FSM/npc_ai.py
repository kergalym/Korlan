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
        self.is_idle = True
        self.is_moving = base.korlan_is_moving
        self.is_crouching = False
        self.is_jumping = False
        self.is_hitting = False
        self.is_using = False
        self.is_blocking = False
        self.is_has_sword = False
        self.is_has_bow = False
        self.is_has_tengri = False
        self.is_has_umai = False
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

    def enter_idle(self, player, action):
        if player and action:
            self.avatar = player

            any_action = self.avatar.getAnimControl(action)

            if (any_action.isPlaying() is False
                    and self.is_idle
                    and self.is_moving is False):
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

