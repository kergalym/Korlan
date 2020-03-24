from direct.showbase.DirectObject import DirectObject
from configparser import ConfigParser
from direct.fsm.FSM import FSM
from direct.task.TaskManagerGlobal import taskMgr
from panda3d.ai import AICharacter
from Engine.Collisions.collisions import Collisions
# from Engine.FSM.env_ai import FsmEnv


class FsmNPC:
    """ Gameplay logics goes here """

    def __init__(self):
        self.d_object = DirectObject()
        self.cfg_parser = ConfigParser()
        self.is_idle = True
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
        self.taskMgr = taskMgr
        self.col = Collisions()

    def get_npc(self, actor):
        if actor and isinstance(actor, str):
            if not render.find("**/{}".format(actor)).is_empty():
                avatar = render.find("**/{}".format(actor))
                return avatar

    def set_npc_ai(self, actor, behavior):
        if (actor
                and behavior):
            if hasattr(base, "ai_world") and base.ai_world:
                if behavior == "seek":
                    ai_char = AICharacter(behavior, actor, 100, 0.05, 5)
                    base.ai_world.add_ai_char(ai_char)
                    ai_behaviors = ai_char.get_ai_behaviors()
                    if not render.find("**/Korlan:BS").is_empty():
                        player = render.find("**/Korlan:BS")
                        ai_behaviors.seek(player)
                    actor.loop("Walking")


class Walking(FsmNPC):
    def __init__(self):

        FsmNPC.__init__(self)

    def enterWalk(self):
        self.avatar.loop('walk')
        # self.snd.footstepsSound.play()
        # self.col.enableDoorCollisions()

    def exitWalk(self):
        self.avatar.stop()
        # self.snd.footstepsSound.stop()


class Idle(FsmNPC):
    def __init__(self):

        FsmNPC.__init__(self)

    def enter_idle(self, actor, action):
        if actor and action:
            self.avatar = actor

            any_action = self.avatar.getAnimControl(action)

            if (any_action.isPlaying() is False
                    and self.is_idle
                    and self.is_moving is False):
                self.avatar.play(action)
                self.avatar.setPlayRate(1.0, action)


class Swimming(FsmNPC):
    def __init__(self):

        FsmNPC.__init__(self)


class Staying(FsmNPC):
    def __init__(self):

        FsmNPC.__init__(self)


class Jumping(FsmNPC):
    def __init__(self):

        FsmNPC.__init__(self)


class Laying(FsmNPC):
    def __init__(self):

        FsmNPC.__init__(self)


class Sitting(FsmNPC):
    def __init__(self):

        FsmNPC.__init__(self)


class Interacting(FsmNPC):
    def __init__(self):

        FsmNPC.__init__(self)


class Life(FsmNPC):
    def __init__(self):
        FsmNPC.__init__(self)


class Dying(FsmNPC):
    def __init__(self):

        FsmNPC.__init__(self)


class MartialActions(FsmNPC):
    def __init__(self):

        FsmNPC.__init__(self)


class MiscActions(FsmNPC):
    def __init__(self):

        FsmNPC.__init__(self)

