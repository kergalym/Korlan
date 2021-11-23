

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

    def set_npc_equipment(self, actor, bone):
        if actor and isinstance(bone, str):
            hips_joint = actor.exposeJoint(None, "modelRoot", bone)

            sword = base.loader.loadModel(base.assets_collector()["sword"])
            sword.set_name("sword")
            sword.reparent_to(hips_joint)
            bow = base.loader.loadModel(base.assets_collector()["bow"])
            bow.set_name("bow")
            bow.reparent_to(hips_joint)
            arrow = base.loader.loadModel(base.assets_collector()["bow_arrow"])
            arrow.set_name("bow_arrow")
            arrow.reparent_to(hips_joint)

            # positioning and scaling
            sword.set_pos(10, 20, -8)
            sword.set_hpr(325.30, 343.30, 7.13)
            sword.set_scale(100)
            bow.set_pos(0, 12, -12)
            bow.set_hpr(78.69, 99.46, 108.43)
            bow.set_scale(100)
            arrow.set_pos(-10, 7, -12)
            arrow.set_hpr(91.55, 0, 0)
            arrow.set_scale(100)

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
