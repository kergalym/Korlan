class PlayerState:

    def __init__(self):
        base.states = {
            "is_idle": True,
            "is_moving": False,
            "is_crouch_moving": False,
            "is_crouching": False,
            "is_standing": False,
            "is_jumping": False,
            "is_hitting": False,
            "is_h_kicking": False,
            "is_f_kicking": False,
            "is_using": False,
            "is_blocking": False,
            "has_sword": False,
            "has_bow": False,
            "has_tengri": False,
            "has_umai": False,
        }
        base.player_state_unarmed = False
        base.player_state_armed = False
        base.player_state_magic = False
        base.item_player_access_codes = {'NOT_USABLE': 0,
                                         'USABLE': 1,
                                         'DEFORMED': 2
                                         }

    def set_player_idle_state(self, state):
        if state is False:
            base.states['is_idle'] = False
        else:
            base.states['is_idle'] = True

    def set_action_state(self, state, boolean):
        if (state
                and isinstance(state, str)
                and isinstance(boolean, bool)):
            if state:
                base.states[state] = boolean

            for key in base.states:
                if state is False and key == "is_idle":
                    base.states[key] = True
                elif state and key != state:
                    base.states[key] = False

    def set_player_equip_state(self, task):
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

    def has_actor_any_item(self, item, exposed_joint):
        if item and exposed_joint:
            if (exposed_joint.get_num_children() == 1
                    and item.get_name() == exposed_joint.get_child(0).get_name()):
                return True
            else:
                return False

    def pick_up_item(self, player, joint, entry):
        if (player
                and entry
                and joint
                and isinstance(joint, str)):
            assets = base.asset_nodes_assoc_collector()
            item = assets.get(entry.get_into_node().get_name())
            exposed_joint = player.expose_joint(None, "modelRoot", joint)
            if self.has_actor_any_item(item, exposed_joint) is False:
                item.reparent_to(exposed_joint)
                item_np = exposed_joint.find(item.get_name())
                # After reparenting to joint the item inherits joint coordinates,
                # so we find it in given joint and then do rotate and rescale the item
                if not item_np.is_empty():
                    item_np.set_scale(8.0)
                    item_np.set_h(205.0)
                print("Info from PlayerState class: ", item, type(item))
            elif self.has_actor_any_item(item, exposed_joint) is True:
                item.detachNode()

    def pass_item(self, player, joint, item):
        if (player
                and isinstance(joint, str)
                and item):
            exposed_joint = player.expose_joint(None, "modelRoot", joint)
            item.reparent_to(exposed_joint)

    def drop_item(self, object, item):
        if object and item:
            item.reparent_to(object)
            item.set_pos(object.get_pos())
