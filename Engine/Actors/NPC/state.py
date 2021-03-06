

class NpcState:

    def __init__(self):
        self.base = base
        base.actor_unarmed = False
        base.actor_armed = False
        base.actor_magic = False
        base.creature_unarmed = False
        base.creature_magic = False
        base.item_npc_access_codes = {'NOT_USABLE': 0,
                                      'USABLE': 1,
                                      'DEFORMED': 2
                                      }

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
