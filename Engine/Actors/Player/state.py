from direct.task.TaskManagerGlobal import taskMgr
from panda3d.bullet import BulletBoxShape, BulletRigidBodyNode, BulletGhostNode
from panda3d.core import WindowProperties, NodePath, BitMask32, Vec3


class PlayerState:

    def __init__(self):
        self.base = base
        self.render = render
        self.loader = base.loader
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
        self.damage_weapons = ['LeftHand', 'RightHand', 'sword', 'arrow', 'spear', 'fireballs']
        base.player_states = {
            "is_alive": True,
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

        self.base.game_instance['player_state_cls'] = self
        self.base.game_instance['player_props'] = self.player_props

    def set_state(self, actor):
        if actor:
            actor.set_python_tag("health", 100)
            actor.set_python_tag("stamina", 100)
            actor.set_python_tag("courage", 100)
            actor.set_python_tag("damage_level", 1)
            actor.set_python_tag("is_on_horse", False)
            actor.set_python_tag("damage_weapons", self.damage_weapons)

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

        self.base.win_props.set_cursor_hidden(False)
        self.base.win.request_properties(self.base.win_props)

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
                        if key != action and key != "is_alive":
                            base.player_states[key] = False

            else:
                base.player_states[action] = state
                # use this if action is related to weapon state
                # we don't have any weapon equipped
                if "has" in action:
                    for key in base.player_states:
                        if key != action and key != "is_alive":
                            base.player_states[key] = False
                        if "idle" not in action:
                            base.player_states[key] = False

                base.player_states["is_idle"] = True

    def set_horse_riding_weapon_state(self, action, state):
        if (action
                and isinstance(action, str)
                and isinstance(state, bool)):
            for key in base.player_states:
                if "has" in key and key != "is_alive":
                   base.player_states[key] = False

            base.player_states[action] = state

    def set_action_state_crouched(self, action, state):
        if (action
                and isinstance(action, str)
                and isinstance(state, bool)):
            if state:
                for key in base.player_states:
                    if (action == "is_crouch_moving"
                            and key != "is_alive"
                            and "has" not in key):
                        base.player_states[key] = False
                        base.player_states["is_idle"] = False
                        base.player_states["is_crouch_moving"] = True
                    elif action == "is_idle" and key != "is_alive":
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
                    weapon = base.loader.load_model(base.assets_collector()[name])
                    weapon.set_name(name)
                    if "bow_kazakh" not in name:
                        weapon.reparent_to(joint)
                        weapon.set_pos(10, 20, -8)
                        weapon.set_hpr(325.30, 343.30, 7.13)
                        weapon.set_scale(100)
                        self.set_weapon_collider(weapon=weapon, joint=joint)
                    if "bow_kazakh" in name:
                        weapon.reparent_to(joint)
                        weapon.set_pos(0, 12, -12)
                        weapon.set_hpr(78.69, 99.46, 108.43)
                        weapon.set_scale(100)

            base.player_state_unarmed = True
            base.player_state_armed = False
            base.player_state_magic = False
            base.player_state_equipped = True

    def set_weapon_collider(self, weapon, joint):
        if weapon and joint:
            # Create weapon collider
            name = weapon.get_name()
            # min_, max_ = weapon.get_tight_bounds()
            # size = max_ - min_
            shape = BulletBoxShape(Vec3(0.05, 0.55, 0.05))
            body = BulletGhostNode('{0}_BGN'.format(name))
            weapon_rb_np = NodePath(body)
            weapon_rb_np.wrt_reparent_to(joint)
            weapon_rb_np.set_pos(10, -14.90, -8)
            weapon_rb_np.set_hpr(0, 0, 0)
            weapon_rb_np.set_scale(weapon.get_scale())
            weapon.wrt_reparent_to(weapon_rb_np)
            weapon.set_hpr(325, 343, 0)
            weapon.set_pos(0, 0.3, 0)
            weapon_rb_np.node().add_shape(shape)
            # weapon_rb_np.node().set_kinematic(True)

            # Player and its owning arrow won't collide with each other
            weapon_rb_np.set_collide_mask(BitMask32.allOff())

            self.base.game_instance['physics_world_np'].attach_ghost(weapon_rb_np.node())

    def clear_weapon_collider(self, weapon, joint):
        if weapon and joint:
            if "BRB" in weapon.get_parent().get_name():
                weapon_rb_np = weapon.get_parent()
                weapon.reparent_to(joint)
                self.base.game_instance['physics_world_np'].remove_ghost(weapon_rb_np.node())

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
            if actor.find("**/{0}".format(weapon_name)):
                if "bow_kazakh" not in weapon_name:
                    # get weapon collider
                    weapon = actor.find("**/{0}_BGN".format(weapon_name))
                    weapon.reparent_to(joint)
                    # rescale weapon because it's scale 100 times smaller than we need
                    weapon.set_scale(100)
                    weapon.set_pos(-20.0, 40.0, 1.0)
                    weapon.set_hpr(212.47, 0.0, 18.43)
                    if weapon.is_hidden():
                        weapon.show()

                elif "bow_kazakh" in weapon_name:
                    weapon = actor.find("**/{0}".format(weapon_name))
                    weapon.reparent_to(joint)
                    # rescale weapon because it's scale 100 times smaller than we need
                    weapon.set_scale(100)
                    weapon.set_pos(0, 5.0, 4.0)
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
            if actor.find("**/{0}".format(weapon_name)):
                if "bow_kazakh" not in weapon_name:
                    # get weapon collider
                    weapon = actor.find("**/{0}_BGN".format(weapon_name))
                    weapon.reparent_to(joint)
                    # self.clear_weapon_collider(weapon=weapon, joint=joint)
                    # rescale weapon because it's scale 100 times smaller than we need
                    weapon.set_scale(100)
                    weapon.set_pos(10, -14.90, -8)
                    weapon.set_hpr(0, 0, 0)
                elif "bow_kazakh" in weapon_name:
                    weapon = actor.find("**/{0}".format(weapon_name))
                    weapon.reparent_to(joint)
                    # rescale weapon because it's scale 100 times smaller than we need
                    weapon.set_scale(100)
                    weapon.set_pos(0, 12, -12)
                    weapon.set_hpr(78.69, 99.46, 108.43)

                base.player_state_unarmed = True
                base.player_state_armed = False
                base.player_state_magic = False

    def pick_up_item(self, player, joint):
        if (player
                and joint
                and isinstance(joint, str)):
            item = player.get_python_tag("used_item_np")
            exposed_joint = player.expose_joint(None, "modelRoot", joint)
            # Get bullet shape node path
            if (item
                    and exposed_joint.find(item.get_name()).is_empty()):
                # We want to keep original scale of the item
                if hasattr(item, "set_python_tag"):
                    item.set_python_tag("orig_scale", item.get_scale())

                # Hide txt cap while item is in use
                item_trigger = item.find("**/{0}_trigger".format(item.get_name()))
                txt_cap = item_trigger.find("**/txt_use")
                if txt_cap:
                    txt_cap.hide()

                item.wrt_reparent_to(exposed_joint)

                # Set kinematics to make item follow actor joint
                if hasattr(item.node(), "set_kinematic"):
                    item.node().set_kinematic(True)

                # Set item position and rotation
                for name, pos, hpr in zip(player.get_python_tag("usable_item_list")["name"],
                                          player.get_python_tag("usable_item_list")["pos"],
                                          player.get_python_tag("usable_item_list")["hpr"]):
                    if name in item.get_name():
                        item.set_hpr(hpr)
                        item.set_pos(pos)

                # Prevent fast moving objects from passing through thin obstacles.
                if hasattr(item.node(), "set_ccd_motion_threshold"):
                    item.node().set_ccd_motion_threshold(1e-7)
                if hasattr(item.node(), "set_ccd_swept_sphere_radius"):
                    item.node().set_ccd_swept_sphere_radius(0.50)

                player.set_python_tag("is_item_using", True)
                player.set_python_tag("is_item_ready", False)

                item_prop = player.get_python_tag("current_item_prop")
                if item_prop:
                    item_prop['in-use'] = True

                # Set hands icon to busy
                if self.base.game_instance['hud_np']:
                    self.base.game_instance['hud_np'].toggle_weapon_state(weapon_name="busy_hands")

                # Update usable items current count
                if self.base.game_instance["is_indoor"]:
                    name = item.get_name()
                    for _name in player.get_python_tag("usable_item_list")["name"]:
                        if _name == name:
                            player.get_python_tag("usable_item_list")["name"].remove(name)

                # TODO: Uncomment after pick_up_item() is debugged
                """
                add_item_to_inventory = self.base.shared_functions['add_item_to_inventory']
                if add_item_to_inventory:
                    item_prop = player.get_python_tag("current_item_prop")
                    item_prop['in-use'] = False
                    add_item_to_inventory(item=item.get_name(),
                                          count=1,
                                          inventory="INVENTORY_1",
                                          inventory_type="misc")
                    player.set_python_tag("is_item_using", False)
                    player.set_python_tag("used_item_np", None)
                    player.set_python_tag("is_item_ready", False)
                    player.set_python_tag("current_item_prop", None)
                """

    def drop_item(self, player):
        if player and not render.find('**/World').is_empty():
            item = player.get_python_tag("used_item_np")
            if item:
                player_bs = self.base.get_actor_bullet_shape_node(asset=player.get_name(), type="Player")
                world = render.find('**/World')
                item.reparent_to(world)

                # Show txt cap while item is not in use
                item_trigger = item.find("**/{0}_trigger".format(item.get_name()))
                txt_cap = item_trigger.find("**/txt_use")
                txt_cap.show()

                if hasattr(item, "get_python_tag"):
                    scale = item.get_python_tag("orig_scale")
                    item.set_scale(1)
                    item.set_hpr(0, 0, 0)

                # Put the item near player
                # If player has the bullet shape
                if player_bs:
                    pos = Vec3(player_bs.get_x(), player_bs.get_y(), 0.2)
                    item.set_pos(pos)

                if hasattr(item.node(), "set_kinematic"):
                    item.node().set_kinematic(False)

                player.set_python_tag("is_item_using", False)
                player.set_python_tag("used_item_np", None)
                player.set_python_tag("is_item_ready", False)
                self.base.game_instance['item_state'].clear()

                # Set hands icon to free back
                if self.base.game_instance['hud_np']:
                    self.base.game_instance['hud_np'].toggle_weapon_state(weapon_name="hands")

                # Update usable items current count
                # TODO:Uncomment this after "return item back" is implemented in the item menu
                """if self.base.game_instance["is_indoor"]:
                    name = item.get_name()
                    player.get_python_tag("usable_item_list")["name"].append(name)"""

