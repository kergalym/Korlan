from direct.task.TaskManagerGlobal import taskMgr
from panda3d.ai import AIWorld
from Engine.FSM.player_fsm import FsmPlayer
from Engine.FSM.npc_ai import FsmNPC


class FsmEnv:
    """ Gameplay logics goes here """

    def __init__(self):
        self.ai_world = None
        self.fsm_player = FsmPlayer()
        self.fsm_npc = FsmNPC()
        self.ai_behaviors = None

    def update_ai_world_task(self, task):
        if self.ai_world:
            self.ai_world.update()
            if base.game_mode is False and base.menu_mode:
                return task.done
        return task.cont

    def set_ai_world(self):
        self.ai_world = AIWorld(render)
        base.ai_world = self.ai_world

        taskMgr.add(self.update_ai_world_task,
                    "update_ai_world",
                    appendTask=True)


class Wind(FsmEnv):
    def __init__(self):

        FsmEnv.__init__(self)


class Rain(FsmEnv):
    def __init__(self):

        FsmEnv.__init__(self)


class Storm(FsmEnv):
    def __init__(self):

        FsmEnv.__init__(self)


class Day(FsmEnv):
    def __init__(self):

        FsmEnv.__init__(self)


class Night(FsmEnv):
    def __init__(self):

        FsmEnv.__init__(self)

