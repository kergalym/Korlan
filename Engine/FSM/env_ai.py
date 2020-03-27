from direct.task.TaskManagerGlobal import taskMgr
from panda3d.ai import AIWorld
from Engine.FSM.player_fsm import FsmPlayer
from Engine.FSM.npc_ai import NpcAI


class EnvAI:
    def __init__(self):
        self.ai_world = None
        self.fsm_player = FsmPlayer()
        self.fsm_npc = NpcAI()
        self.ai_behaviors = None

    def update_ai_world_task(self, task):
        if self.ai_world:
            self.ai_world.update()
            if base.game_mode is False and base.menu_mode:
                return task.done
        return task.cont

    def set_ai_world(self):
        self.ai_world = AIWorld(render)
        if self.ai_world:
            base.ai_world = self.ai_world

        taskMgr.add(self.update_ai_world_task,
                    "update_ai_world",
                    appendTask=True)

    def set_weather(self, weather):
        if weather and isinstance(weather, str):
            if weather == "wind":
                pass
            elif weather == "rain":
                pass
            elif weather == "storm":
                pass
            elif weather == "day":
                pass
            elif weather == "night":
                pass

