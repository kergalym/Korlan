class Equip:
    """ Equip class implements weapon and clothes (e.g. armor) equipping
        for Inventory
    """

    def toggle_cloth_visibility(self, item):
        """ Switch player clothes visibility
        """
        if item and isinstance(item, str):
            player_bs = render.find("**/Player:BS")
            if player_bs:
                player = player_bs.find("**/Player")
                if player:
                    item_np = player.find("**/__Actor_{0}".format(item))
                    if item_np:
                        if item_np.is_hidden():
                            item_np.show()
                        else:
                            item_np.hide()

    def _get_weapon(self, actor, weapon_name, bone_name):
        if (actor and weapon_name and bone_name
                and isinstance(weapon_name, str)
                and isinstance(bone_name, str)):

            if weapon_name == "sword":
                if actor.find("bow"):
                    self._remove_weapon(actor, "bow", bone_name)
            elif weapon_name == "bow":
                if actor.find("sword"):
                    self._remove_weapon(actor, "sword", bone_name)

            joint = actor.exposeJoint(None, "modelRoot", bone_name)
            if render.find("**/{0}".format(weapon_name)):
                weapon = render.find("**/{0}".format(weapon_name))
                weapon.reparent_to(joint)
                if weapon_name == "sword":
                    # rescale weapon because it's scale 100 times smaller than we need
                    weapon.set_scale(100)
                    weapon.set_pos(-11.0, 13.0, -3.0)
                    weapon.set_hpr(212.47, 0.0, 18.43)
                    weapon.show()
                elif weapon_name == "bow_kazakh":
                    # rescale weapon because it's scale 100 times smaller than we need
                    weapon.set_scale(100)
                    weapon.set_pos(0, 2.0, 2.0)
                    weapon.set_hpr(216.57, 293.80, 316.85)
                    weapon.show()
                    arrow = render.find("**/bow_arrow_kazakh")
                    arrow.reparent_to(weapon)
                    # rescale weapon because it's scale 100 times smaller than we need
                    arrow.set_scale(1)
                    arrow.set_pos(0.04, 0.01, -0.01)
                    arrow.set_hpr(0, 2.86, 0)
                    arrow.show()

                base.player_state_unarmed = False
                base.player_state_armed = True
                base.player_state_magic = False

    def _remove_weapon(self, actor, weapon_name, bone_name):
        if (actor and weapon_name and bone_name
                and isinstance(weapon_name, str)
                and isinstance(bone_name, str)):

            if weapon_name == "sword":
                if actor.find("bow"):
                    self._remove_weapon(actor, "bow", bone_name)
            elif weapon_name == "bow":
                if actor.find("sword"):
                    self._remove_weapon(actor, "sword", bone_name)

            joint = actor.exposeJoint(None, "modelRoot", bone_name)
            if render.find("**/{0}".format(weapon_name)):
                weapon = render.find("**/{0}".format(weapon_name))
                weapon.reparent_to(render)
                if weapon_name == "sword":
                    # rescale weapon because it's scale 100 times smaller than we need
                    weapon.set_scale(100)
                    weapon.set_pos(10, 20, -8)
                    weapon.set_hpr(325.30, 343.30, 7.13)
                    weapon.hide()
                elif weapon_name == "bow_kazakh":
                    # rescale weapon because it's scale 100 times smaller than we need
                    weapon.set_scale(100)
                    weapon.set_pos(0, 12, -12)
                    weapon.set_hpr(78.69, 99.46, 108.43)
                    weapon.hide()
                    arrow = render.find("**/bow_arrow_kazakh")
                    if arrow:
                        arrow.reparent_to(render)
                        # rescale weapon because it's scale 100 times smaller than we need
                        arrow.set_scale(1)
                        arrow.set_pos(-10, 7, -12)
                        arrow.set_hpr(91.55, 0, 0)
                        arrow.hide()

                base.player_state_unarmed = True
                base.player_state_armed = False
                base.player_state_magic = False

    def _get_player(self):
        """player_bs = render.find("**/Player:BS")
        if player_bs:
            player = player_bs.find("**/Player")
            if player:
                return player"""
        return base.player_ref

    def toggle_weapon(self, item, bone):
        if item and bone:
            player = self._get_player()
            if player:
                if hasattr(base, "player_state_armed"):
                    if base.player_state_unarmed:
                        self._get_weapon(actor=player, weapon_name=item, bone_name=bone)
                    else:
                        self._remove_weapon(actor=player, weapon_name=item, bone_name=bone)



