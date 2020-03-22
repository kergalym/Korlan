from direct.task.TaskManagerGlobal import taskMgr
from panda3d.core import WindowProperties

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

        self.base = base
        self.render = render
        self.loader = base.loader

        self.render = render
        self.inventory = Inventory()

    def clear_state(self):
        assets = self.base.assets_collector()

        if hasattr(base, "frame_inv"):
            base.frame_inv.hide()

        # Remove all lights
        render.clearLight()

        # Remove Bullet World
        if not render.find("**/World").is_empty():
            render.find("**/World").remove_node()

        # Remove all tasks except system
        tasks = ["player_init",
                 "player_state",
                 "actor_life",
                 "mouse_look"]
        for t in tasks:
            taskMgr.remove(t)

        # make pattern list from assets dict
        pattern = [key for key in assets]
        # use pattern to remove nodes corresponding to asset names
        for node in pattern:
            if render.find("**/{0}".format(node)).is_empty() is False:
                render.find("**/{0}".format(node)).remove_node()

        for key in assets:
            self.loader.unload_model(assets[key])

        wp = WindowProperties()
        wp.set_cursor_hidden(False)
        self.base.win.request_properties(wp)

        # Disable the camera trackball controls.
        self.base.disable_mouse()

        # Disable mouse camera
        self.base.mouse_magnitude = 0
        self.base.rotate_x = 0
        self.base.last_mouse_x = None
        self.base.hide_mouse = False
        self.base.manual_recenter_Mouse = False
        self.base.camera.set_pos(0, 0, 0)
        self.base.camera.set_hpr(0, 0, 0)
        self.base.cam.set_pos(0, 0, 0)
        self.base.cam.set_hpr(0, 0, 0)
        self.base.load_menu_scene()
        self.base.frame.show()

        if hasattr(base, "is_item_in_use"):
            base.is_item_in_use = False
        if hasattr(base, "is_item_in_use_long"):
            base.is_item_in_use_long = False

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

    def get_distance_to(self, items_dist_vect):
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
                    # noinspection PyChainedComparisons
                    elif (items_dist_vect[key][0] < -0.0
                          and items_dist_vect[key][0] > -0.7
                          or items_dist_vect[key][1] < -0.0
                          and items_dist_vect[key][1] > -0.7):
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
        if item:
            return item

    def drop_item(self, player):
        if player and not render.find('**/World').is_empty():
            item = self.render.find("**/{0}".format(base.in_use_item_name))
            world = render.find('**/World')
            item.reparent_to(world)
            item.set_scale(0.1)
            item.set_hpr(0, 0, 0)
            # Put the item near player
            # If player has the bullet shape
            if "BS" in player.get_parent().get_name():
                player = player.get_parent()
            item.set_pos(player.get_pos() - (0.20, -0.5, 0))
            item.node().set_kinematic(False)

            base.is_item_in_use = False
            base.is_item_in_use_long = False
            base.is_item_close_to_use = False
            base.is_item_far_to_use = False

    def pick_up_item(self, player, joint, items_dist_vect):
        if (player
                and items_dist_vect
                and joint
                and isinstance(joint, str)
                and isinstance(items_dist_vect, dict)):
            item = self.get_distance_to(items_dist_vect)
            exposed_joint = player.expose_joint(None, "modelRoot", joint)

            if (item
                    and exposed_joint.find(item.get_name()).is_empty()):
                # Get bullet shape node path
                if "BS" in item.get_parent().get_name():
                    item = item.get_parent()
                # we want to keep original scale of the item
                item.wrt_reparent_to(exposed_joint)
                # Set kinematics to make item follow actor joint
                item.node().set_kinematic(True)
                base.in_use_item_name = item.get_name()

                item.set_h(205.0)
                item.set_pos(0.4, 8.0, 5.2)
                # Prevent fast moving objects from passing through thin obstacles.
                item.node().set_ccd_motion_threshold(1e-7)
                item.node().set_ccd_swept_sphere_radius(0.50)

                # Set item state
                base.is_item_in_use = True
                base.is_item_in_use_long = True
                base.is_item_close_to_use = False
                base.is_item_far_to_use = False
                self.inventory.get_item(item)

    def take_item(self, player, joint, items_dist_vect):
        if (player
                and items_dist_vect
                and joint
                and isinstance(joint, str)
                and isinstance(items_dist_vect, dict)):
            if (base.is_item_close_to_use
                    and base.is_item_in_use is False
                    and base.is_item_in_use_long is False):
                self.pick_up_item(player, joint, items_dist_vect)
            elif (base.is_item_close_to_use is False
                  and base.is_item_in_use is True
                  and base.is_item_in_use_long is True):
                self.drop_item(player)
