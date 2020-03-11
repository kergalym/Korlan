from Engine.Collisions.collisions import Collisions
from Engine.Actors.Player.inventory import Inventory


class PlayerState:

    def __init__(self):
        base.states = {
            "is_idle": True,
            "is_moving": False,
            "is_running": False,
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
        base.is_item_close_to_use = False
        base.is_item_far_to_use = False
        base.is_item_in_use = False
        base.is_item_in_use_long = False
        base.in_use_item_name = None

        self.render = render
        self.col = Collisions()
        self.inventory = Inventory()

    def set_action_state(self, action, state):
        if (action
                and isinstance(action, str)
                and isinstance(state, bool)):
            if state:
                base.states[action] = state
                for key in base.states:
                    if (state
                            and key != "is_idle"
                            and key != action):
                        base.states[key] = False

            elif state is False:
                for key in base.states:
                    base.states[key] = False
                    base.states["is_idle"] = True

    def set_action_state_crouched(self, action, state):
        if (action
                and isinstance(action, str)
                and isinstance(state, bool)):
            if state:
                for key in base.states:
                    if action == "is_crouch_moving":
                        base.states[key] = False
                        base.states["is_idle"] = False
                        base.states["is_crouch_moving"] = True
                    elif action == "is_idle":
                        base.states[key] = False
                        base.states["is_idle"] = True
            elif state is False:
                if action == "is_crouch_moving":
                    base.states["is_idle"] = True
                    base.states["is_crouch_moving"] = False

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

    def pick_up_item(self, player, joint, items_dist_vect):
        if (player
                and items_dist_vect
                and joint
                and isinstance(joint, str)
                and isinstance(items_dist_vect, dict)):
            assets = base.asset_nodes_assoc_collector()
            item = None

            for key in items_dist_vect:
                if key and assets.get(key):
                    if key == assets[key].get_name():
                        # noinspection PyChainedComparisons
                        if (items_dist_vect[key][0] > 0.0
                                and items_dist_vect[key][0] < 0.7
                                or items_dist_vect[key][1] > 0.0
                                and items_dist_vect[key][1] < 0.7):
                            if base.is_item_in_use is False:
                                base.is_item_close_to_use = True
                                base.is_item_far_to_use = False
                                item = assets[key]
                            elif base.is_item_in_use:
                                base.is_item_close_to_use = False
                                base.is_item_far_to_use = True
                        else:
                            base.is_item_close_to_use = False
                            base.is_item_far_to_use = True

            exposed_joint = player.expose_joint(None, "modelRoot", joint)

            if (base.is_item_close_to_use
                    and base.is_item_in_use is False
                    and base.is_item_in_use_long is False):
                if exposed_joint.find(item.get_name()).is_empty():
                    # Get bullet shape node path
                    item = item.get_parent()
                    # Disable collide mask before attaching
                    # because we don't want colliding
                    # between character and item.
                    item.set_collide_mask(self.col.no_mask)
                    item.reparent_to(exposed_joint)
                    base.in_use_item_name = item.get_name()
                    base.in_use_item_mass_orig = item.node().get_mass()
                    base.in_use_item_loc_orig = item.get_parent()
                    item.set_scale(7.0)

                    # Set mass to 0 to make item follow actor joint
                    item.node().set_mass(0)

                    item.set_h(205.0)
                    item.set_x(0.4)
                    item.set_y(8.0)
                    item.set_z(5.2)

                    self.inventory.get_item(item)

                    # Set item state
                    base.is_item_in_use = True
                    base.is_item_in_use_long = True
                    base.is_item_close_to_use = False
                    base.is_item_far_to_use = False

            elif (base.is_item_close_to_use is False
                  and base.is_item_in_use is True
                  and base.is_item_in_use_long is True):
                if not render.find('**/World').is_empty():
                    world = render.find('**/World')
                    item = self.render.find("**/{0}".format(base.in_use_item_name))
                    item.reparent_to(world)
                    item.set_scale(0.2)
                    item.set_hpr(0, 0, 0)
                    item.node().set_mass(base.in_use_item_mass_orig)
                    item.set_collide_mask(self.col.mask)

                    # Put the item near player
                    # If player has the bullet shape
                    if "BS" in player.get_parent().get_name():
                        player = player.get_parent()

                    item.set_pos(player.get_pos() - (0.20, -0.5, 0))

                    # Set the item Z coordinate to 0 to prevent high jumping
                    item.set_z(0)

                    # Set item state
                    base.is_item_in_use = False
                    base.is_item_in_use_long = False
                    base.is_item_close_to_use = False
                    base.is_item_far_to_use = False

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
