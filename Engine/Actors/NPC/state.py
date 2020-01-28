
class NpcState:

    def __init__(self):
        base.actor_unarmed = False
        base.actor_armed = False
        base.actor_magic = False
        base.creature_unarmed = False
        base.creature_magic = False

    def set_actor_state(self, task):
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
        return task.cont

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
