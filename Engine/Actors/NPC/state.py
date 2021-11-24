

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

    def get_weapon(self, actor, weapon_name, bone_name):
        if (actor and weapon_name and bone_name
                and isinstance(weapon_name, str)
                and isinstance(bone_name, str)):
            joint = actor.exposeJoint(None, "modelRoot", bone_name)
            if render.find("**/{0}".format(weapon_name)):
                weapon = render.find("**/{0}".format(weapon_name))
                weapon.reparent_to(joint)
                if weapon_name == "sword":
                    # rescale weapon because it's scale 100 times smaller than we need
                    weapon.set_scale(100)
                    weapon.set_pos(-11.0, 13.0, -3.0)
                    weapon.set_hpr(212.47, 0.0, 18.43)
                elif weapon_name == "bow_kazakh":
                    # rescale weapon because it's scale 100 times smaller than we need
                    weapon.set_scale(100)
                    weapon.set_pos(0, 2.0, 2.0)
                    weapon.set_hpr(216.57, 293.80, 316.85)
                    arrow = render.find("**/bow_arrow_kazakh")
                    arrow.reparent_to(weapon)
                    # rescale weapon because it's scale 100 times smaller than we need
                    arrow.set_scale(1)
                    arrow.set_pos(0.04, 0.01, -0.01)
                    arrow.set_hpr(0, 2.86, 0)

    def remove_weapon(self, actor, weapon_name, bone_name):
        if (actor and weapon_name and bone_name
                and isinstance(weapon_name, str)
                and isinstance(bone_name, str)):
            if weapon_name == "sword":
                self.remove_weapon(actor, "bow", bone_name)
            elif weapon_name == "bow":
                self.remove_weapon(actor, "sword", bone_name)

            joint = actor.exposeJoint(None, "modelRoot", bone_name)
            if render.find("**/{0}".format(weapon_name)):
                weapon = render.find("**/{0}".format(weapon_name))
                weapon.reparent_to(joint)
                if weapon_name == "sword":
                    # rescale weapon because it's scale 100 times smaller than we need
                    weapon.set_scale(100)
                    weapon.set_pos(10, 20, -8)
                    weapon.set_hpr(325.30, 343.30, 7.13)
                elif weapon_name == "bow":
                    # rescale weapon because it's scale 100 times smaller than we need
                    weapon.set_scale(100)
                    weapon.set_pos(0, 12, -12)
                    weapon.set_hpr(78.69, 99.46, 108.43)
                    arrow = render.find("**/bow_arrow")
                    if arrow:
                        arrow.reparent_to(weapon)
                        # rescale weapon because it's scale 100 times smaller than we need
                        arrow.set_scale(1)
                        arrow.set_pos(-10, 7, -12)
                        arrow.set_hpr(91.55, 0, 0)

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
