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
            joint = actor.exposeJoint(None, "modelRoot", bone_name)
            if render.find("**/{0}".format(weapon_name)):
                weapon = render.find("**/{0}".format(weapon_name))
                weapon.reparent_to(joint)
                if "bow_kazakh" not in weapon_name:
                    # rescale weapon because it's scale 100 times smaller than we need
                    weapon.set_scale(100)
                    weapon.set_pos(10, 20, -8)
                    weapon.set_hpr(325.30, 343.30, 7.13)
                    if weapon.is_hidden():
                        weapon.show()
                elif "bow_kazakh" in weapon_name:
                    # rescale weapon because it's scale 100 times smaller than we need
                    weapon.set_scale(100)
                    weapon.set_pos(0, 12, -12)
                    weapon.set_hpr(78.69, 99.46, 108.43)
                    if weapon.is_hidden():
                        weapon.show()
                    arrow = render.find("**/bow_arrow_kazakh")
                    if arrow:
                        arrow.reparent_to(weapon)
                        # rescale weapon because it's scale 100 times smaller than we need
                        arrow.set_scale(100)
                        arrow.set_pos(-10, 7, -12)
                        arrow.set_hpr(91.55, 0, 0)
                        if arrow.is_hidden():
                            arrow.show()

                base.player_state_equipped = True

    def _remove_weapon(self, actor, weapon_name):
        if (actor and weapon_name
                and isinstance(weapon_name, str)):
            if render.find("**/{0}".format(weapon_name)):
                weapon = render.find("**/{0}".format(weapon_name))
                weapon.reparent_to(render)
                if "bow_kazakh" not in weapon_name:
                    # rescale weapon because it's scale 100 times smaller than we need
                    weapon.set_scale(100)
                    weapon.set_pos(10, 20, -8)
                    weapon.set_hpr(325.30, 343.30, 7.13)
                    weapon.hide()
                elif "bow_kazakh" in weapon_name:
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

                base.player_state_equipped = False

    def _get_player(self):
        """player_bs = render.find("**/Player:BS")
        if player_bs:
            player = player_bs.find("**/Player")
            if player:
                return player"""
        if hasattr(base, "player_ref"):
            return base.player_ref

    def toggle_weapon(self, item, bone):
        if item and bone:
            player = self._get_player()
            if player:
                if hasattr(base, "player_state_equipped"):
                    if base.player_state_equipped:
                        self._remove_weapon(actor=player, weapon_name=item)
                    else:
                        self._get_weapon(actor=player, weapon_name=item, bone_name=bone)



