from direct.task.TaskManagerGlobal import taskMgr
from Engine.FSM.npc_ai import NpcAI


class NpcState:

    def __init__(self):
        base.actor_unarmed = False
        base.actor_armed = False
        base.actor_magic = False
        base.creature_unarmed = False
        base.creature_magic = False
        base.item_npc_access_codes = {'NOT_USABLE': 0,
                                      'USABLE': 1,
                                      'DEFORMED': 2
                                      }
        self.fsm_npc = NpcAI()

    def actor_behavior_task(self, actor, animation, task):
        if actor and animation and isinstance(animation, str):
            if hasattr(base, "npc_distance_calculate"):
                if (not render.find("**/Korlan:BS").is_empty()
                        and not render.find("**/{0}:BS".format(actor.get_name())).is_empty()):
                    player_bs = render.find("**/Korlan:BS")
                    actor_bs = render.find("**/{0}:BS".format(actor.get_name()))
                    vect = base.npc_distance_calculate(player_bs, actor_bs)
                    if vect:
                        if vect['vector'][1] > 0.2:
                            self.fsm_npc.request("Walk", actor, animation, "loop")
                        if vect['vector'][1] > -0.2:
                            self.fsm_npc.request("Walk", actor, animation, "loop")
                        elif vect['vector'][1] < 0.2:
                            self.fsm_npc.request("Walk", actor, animation, "loop")
                        elif vect['vector'][1] < -0.2:
                            self.fsm_npc.request("Walk", actor, animation, "loop")

            return task.cont

    """def set_actor_state(self, task):
        base.actor_state_unarmed = True
        if base.actor_state_armed:
            base.actor_state_unarmed = False
            base.actor_state_magic = False
        elif base.actor_state_magic:
            base.actor_state_unarmed = False
            base.actor_state_armed = False
        elif base.actor_state_unarmed:
            base.actor_state_armed = False
            base.actor_state_magic = False
        return task.cont"""

    def set_actor_state(self, actor):
        if actor:
            taskMgr.add(self.actor_behavior_task,
                        'actor_behavior',
                        extraArgs=[actor, 'Walking'],
                        appendTask=True)

    def set_creature_state(self, task):
        if base.creature_unarmed:
            base.creature_magic = False
        elif base.creature_magic:
            base.creature_unarmed = False
        return task.cont

    def actor_life(self, task):
        self.has_actor_life()
        return task.cont

    def has_actor_life(self):
        if (base.actor_is_dead is False
                and base.actor_is_alive is False):
            base.actor_life_perc = 100
            base.actor_is_alive = True
        else:
            return False

    def creature_life(self, task):
        self.has_actor_life()
        return task.cont

    def has_creature_life(self):
        if (base.actor_is_dead is False
                and base.actor_is_alive is False):
            base.actor_life_perc = 100
            base.actor_is_alive = True
        else:
            return False
