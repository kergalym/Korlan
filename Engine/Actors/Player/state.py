

class PlayerState:

    def __init__(self):
        base.player_state_unarmed = False
        base.player_state_armed = False
        base.player_state_magic = False

    def get_matched_objects_pos(self):
        pass

    def set_player_state(self, task):
        base.player_state_unarmed = True
        if base.player_state_armed:
            base.player_state_unarmed = False
            base.player_state_magic = False
        elif base.player_state_magic:
            base.player_state_unarmed = False
            base.player_state_armed = False
        elif base.player_state_unarmed:
            base.player_state_armed = False
            base.player_state_magic = False
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

    def has_actor_item(self):
        # TODO: Check if item or weapon assigned to an actor arm joint
        #   and return True
        pass
