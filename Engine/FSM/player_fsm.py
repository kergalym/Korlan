from direct.showbase.DirectObject import DirectObject
from configparser import ConfigParser
from direct.fsm.FSM import FSM
from direct.task.TaskManagerGlobal import taskMgr
from panda3d.ai import AICharacter
from Engine.Collisions.collisions import Collisions


class FsmPlayer(FSM):
    """ Gameplay logics goes here """

    def __init__(self):
        self.d_object = DirectObject()
        self.cfg_parser = ConfigParser()
        self.is_moving = False
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
        self.col = Collisions()
        FSM.__init__(self, 'FsmPlayer')

    def get_player(self, actor):
        if actor and isinstance(actor, str):
            if not render.find("**/{}:BS").is_empty():
                self.avatar = render.find("**/{}:BS")
                return self.avatar


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

