from direct.task.TaskManagerGlobal import taskMgr
from panda3d.core import WindowProperties


class PlayerState:

    def __init__(self):
        self.game_settings = base.game_settings
        self.player_props = {
            'name': 'Korlan',
            'age': 25,
            'sex': 'female',
            'height': "1.7 m",
            'weight': "57 kg",
            'specialty': 'warrior',
            'health': 100,
            'stamina': 100,
            'courage': 100,
        }
        base.player_states = {
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
            "is_attacked": False,
            "is_busy": False,
            "is_turning": False,
            "is_mounted": False,
            "horse_riding": False,
            "horse_is_ready_to_be_used": False
        }
        base.do_key_once = {
            'forward': False,
            'backward': False,
            'left': False,
            'right': False,
            'run': False,
            'crouch': False,
            'jump': False,
            'use': False,
            'attack': False,
            'h_attack': False,
            'f_attack': False,
            'block': False,
            'sword': False,
            'bow': False,
            'tengri': False,
            'umai': False
        }

        base.player_state_unarmed = False
        base.player_state_armed = False
        base.player_state_magic = False
        base.player_state_equipped = False
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

        self.base.game_instance['player_props'] = self.player_props

    def player_view_mode_task(self, assets_dist_vec, task):
        if assets_dist_vec:
            for k in assets_dist_vec:
                digit = int(self.game_settings['Main']['camera_distance'])
                if self.game_settings['Main']['person_look_mode'] == 'first':
                    if assets_dist_vec[k][1] <= -0.0:
                        base.cam.set_y(12)
                        base.first_person_mode = True
                    elif assets_dist_vec[k][1] >= -0.0:
                        base.cam.set_y(digit)
                        base.first_person_mode = False
                elif self.game_settings['Main']['person_look_mode'] == 'third':
                    base.first_person_mode = True
                    base.first_person_mode = False
                    return task.done

        if self.base.game_instance['menu_mode']:
            return task.done

        return task.cont

    def clear_state(self):
        assets = self.base.assets_collector()

        if hasattr(base, "frame_inv") and base.frame_inv:
            base.frame_inv.hide()

        # Remove all lights
        render.clearLight()

        # Remove Bullet World
        if not render.find("**/World").is_empty():
            render.find("**/World").remove_node()

        # Remove all tasks except system
        tasks = ["player_init_task",
                 "anim_state",
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

    def set_do_once_key(self, key, value):
        """ Function    : set_do_once_key

            Description : Set the state of the do once keys

            Input       : String, Boolean

            Output      : None

            Return      : None
        """
        if (key and isinstance(key, str)
                and isinstance(value, bool)):
            base.do_key_once[key] = value

    def set_action_state(self, action, state):
        if (action
                and isinstance(action, str)
                and isinstance(state, bool)):
            if state:
                base.player_states[action] = state
                # use this if action is related to weapon state
                # since we allow only one equipped weapon
                if "has" in action:
                    for key in base.player_states:
                        if key != action:
                            base.player_states[key] = False

            else:
                base.player_states[action] = state
                # use this if action is related to weapon state
                # we don't have any weapon equipped
                if "has" in action:
                    for key in base.player_states:
                        if key != action or "idle" not in action:
                            base.player_states[key] = False
                base.player_states["is_idle"] = True

    """def set_action_state_old(self, action, state):
        # TODO: FIX ME
        if (action
                and isinstance(action, str)
                and isinstance(state, bool)):
            if state:
                base.player_states[action] = state
                for key in base.player_states:
                    print(key, base.player_states[key], action)
                    if (state
                            and key != "is_idle"
                            and key != action
                            and "has" not in action):
                        base.player_states[key] = False

            elif state is False:
                for key in base.player_states:
                    # print(key, base.player_states[key])
                    if "has" not in key:
                        base.player_states[key] = False
                    base.player_states["is_idle"] = True"""

    def set_action_state_crouched(self, action, state):
        if (action
                and isinstance(action, str)
                and isinstance(state, bool)):
            if state:
                for key in base.player_states:
                    if action == "is_crouch_moving":
                        base.player_states[key] = False
                        base.player_states["is_idle"] = False
                        base.player_states["is_crouch_moving"] = True
                    elif action == "is_idle":
                        base.player_states[key] = False
                        base.player_states["is_idle"] = True
            elif not state:
                if action == "is_crouch_moving":
                    base.player_states["is_idle"] = True
                    base.player_states["is_crouch_moving"] = False

    def set_player_equipment(self, actor, bone_name):
        if actor and isinstance(bone_name, str):
            joint = actor.exposeJoint(None, "modelRoot", bone_name)

            weapons = self.base.game_instance["weapons"]
            if weapons:
                for name in weapons:
                    weapon = base.loader.loadModel(base.assets_collector()[name])
                    weapon.set_name(name)
                    weapon.reparent_to(joint)
                    if "bow_kazakh" not in name:
                        weapon.set_pos(10, 20, -8)
                        weapon.set_hpr(325.30, 343.30, 7.13)
                        weapon.set_scale(100)
                    if "bow_kazakh" in name:
                        weapon.set_pos(0, 12, -12)
                        weapon.set_hpr(78.69, 99.46, 108.43)
                        weapon.set_scale(100)

            base.player_state_unarmed = True
            base.player_state_armed = False
            base.player_state_magic = False
            base.player_state_equipped = True

    def get_weapon(self, actor, weapon_name, bone_name):
        if (actor and weapon_name and bone_name
                and isinstance(weapon_name, str)
                and isinstance(bone_name, str)):
            weapons = self.base.game_instance["weapons"]
            if weapons:
                for weapon in weapons:
                    if weapon != weapon_name:
                        self.remove_weapon(actor, weapon, "Korlan:Spine1")

            joint = actor.exposeJoint(None, "modelRoot", bone_name)
            if render.find("**/{0}".format(weapon_name)):
                weapon = render.find("**/{0}".format(weapon_name))
                weapon.reparent_to(joint)
                if "bow_kazakh" not in weapon_name:
                    # rescale weapon because it's scale 100 times smaller than we need
                    weapon.set_scale(100)
                    weapon.set_pos(-11.0, 13.0, -3.0)
                    weapon.set_hpr(212.47, 0.0, 18.43)
                    if weapon.is_hidden():
                        weapon.show()
                elif "bow_kazakh" in weapon_name:
                    # rescale weapon because it's scale 100 times smaller than we need
                    weapon.set_scale(100)
                    weapon.set_pos(0, 2.0, 2.0)
                    weapon.set_hpr(216.57, 293.80, 316.85)
                    if weapon.is_hidden():
                        weapon.show()

                base.player_state_unarmed = False
                base.player_state_armed = True
                base.player_state_magic = False

    def remove_weapon(self, actor, weapon_name, bone_name):
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
                elif "bow_kazakh" in weapon_name:
                    # rescale weapon because it's scale 100 times smaller than we need
                    weapon.set_scale(100)
                    weapon.set_pos(0, 12, -12)
                    weapon.set_hpr(78.69, 99.46, 108.43)

                base.player_state_unarmed = True
                base.player_state_armed = False
                base.player_state_magic = False

    def actor_life(self, task):
        self.has_actor_life()

        if self.base.game_instance['menu_mode']:
            return task.done

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

    # TODO Delete it
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
            player_bs = self.base.get_actor_bullet_shape_node(asset=player.get_name(), type="Player")
            world = render.find('**/World')
            item.reparent_to(world)
            # TODO: Remove temporary scale definition
            item.set_scale(0.1)
            item.set_hpr(0, 0, 0)
            # Put the item near player
            # If player has the bullet shape
            if player_bs:
                item.set_pos(player_bs.get_pos() - (0.20, -0.5, 0))
            item.node().set_kinematic(False)

            base.is_item_in_use = False
            base.is_item_in_use_long = False
            base.is_item_close_to_use = False
            base.is_item_far_to_use = False
            base.in_use_item_name = None

    def pick_up_item(self, player, joint, items_dist_vect):
        if (player
                and items_dist_vect
                and joint
                and isinstance(joint, str)
                and isinstance(items_dist_vect, dict)):
            item = self.get_distance_to(items_dist_vect)
            exposed_joint = player.expose_joint(None, "modelRoot", joint)
            # Get bullet shape node path
            item = self.base.get_static_bullet_shape_node(asset=item.get_name())

            if (item
                    and exposed_joint.find(item.get_name()).is_empty()):
                # We want to keep original scale of the item
                item.wrt_reparent_to(exposed_joint)

                # Set kinematics to make item follow actor joint
                item.node().set_kinematic(True)

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

                """import pdb;
                pdb.set_trace()"""
                base.in_use_item_name = item.get_name()

                add_item_to_inventory = self.base.shared_functions['add_item_to_inventory']
                if add_item_to_inventory:
                    add_item_to_inventory(item=base.in_use_item_name,
                                          count=1,
                                          inventory="INVENTORY_1",
                                          inventory_type="misc")

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
