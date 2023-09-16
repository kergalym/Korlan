from Engine.Actors.Player.state import PlayerState
from Engine.FSM.player_fsm import PlayerFSM
from direct.task.TaskManagerGlobal import taskMgr
from Settings.Input.keyboard import Keyboard
from Settings.Input.mouse import Mouse
from Engine.Inventory.sheet import Sheet
from Engine.Actors.Player.player_archery import PlayerArchery
from Engine.Actors.Player.player_movement import PlayerMovement
from Engine.Actors.Player.player_actions import PlayerActions

""" ANIMATIONS"""
from Engine import anim_names


class PlayerController:

    def __init__(self):
        self.game_settings = base.game_settings
        self.base = base
        self.render = render

        self.korlan = None
        self.player = None
        self.floater = None
        self.taskMgr = taskMgr
        self.kbd = Keyboard()
        self.mouse = Mouse()
        self.fsm_player = PlayerFSM()
        self.base.game_instance["player_fsm_cls"] = self.fsm_player
        self.sheet = None
        self.state = PlayerState()
        self.archery = PlayerArchery()
        self.mov_actions = None
        self.actions = None
        self.base.is_cutscene_active = False

    """ Player Anim States Tracking """
    def _regular_anim_state_tracker(self, player, anims):
        any_action = player.get_anim_control(anims[anim_names.a_anim_idle_player])
        if (any_action.is_playing() is False
                # and base.player_states['is_idle']
                and base.player_states['is_attacked'] is False
                and base.player_states["is_blocking"] is False
                and base.player_states['is_busy'] is False
                and base.player_states['is_using'] is False
                and base.player_states['is_turning'] is False
                and base.player_states['is_moving'] is False
                and base.player_states['is_running'] is False
                and base.player_states['is_crouch_moving'] is False
                and base.player_states['is_crouching'] is False
                and base.player_states['is_mounted'] is False
                and base.player_states['horse_riding'] is False):

            self.fsm_player.request("Idle", player,
                                    anims[anim_names.a_anim_idle_player],
                                    "play")
            if self.base.game_instance['player_props']['stamina'] < 100:
                self.base.game_instance['player_props']['stamina'] += 5

            if (self.base.game_instance['hud_np']
                    and self.base.game_instance['hud_np'].player_bar_ui_stamina):
                if self.base.game_instance['hud_np'].player_bar_ui_stamina['value'] < 100:
                    self.base.game_instance['hud_np'].player_bar_ui_stamina['value'] += 5
                    stamina = self.base.game_instance['hud_np'].player_bar_ui_stamina['value']
                    player.set_python_tag("stamina", stamina)

    def _regular_actions_set(self, player, anims):
        if base.player_state_unarmed:
            self._regular_movement(player, anims)
            self._regular_actions(player, anims)
            self._regular_equip_actions(player, anims)

            if not self.base.game_instance["is_indoor"]:
                self._battle_actions(player, anims)

        if base.player_state_armed:
            self._regular_movement(player, anims)
            self._regular_actions(player, anims)
            self._regular_equip_actions(player, anims)

            if not self.base.game_instance["is_indoor"]:
                self._battle_actions(player, anims)

        if base.player_state_magic:
            self._regular_movement(player, anims)
            self._regular_actions(player, anims)
            self._regular_equip_actions(player, anims)

            if not self.base.game_instance["is_indoor"]:
                self._battle_actions(player, anims)
                self._battle_magic_actions(player, anims)

    """ Rider Anim States Tracking """
    def _rider_anim_state_tracker(self, player, anims):
        any_action = player.get_anim_control(anims[anim_names.a_anim_horse_rider_idle])
        if (any_action.is_playing() is False
                # and base.player_states['is_idle']
                and base.player_states['is_attacked'] is False
                and base.player_states["is_blocking"] is False
                and base.player_states['is_busy'] is False
                and base.player_states['is_using'] is False
                and base.player_states['is_turning'] is False
                and base.player_states['is_moving'] is False
                and base.player_states['is_running'] is False
                and base.player_states['is_crouch_moving'] is False
                and base.player_states['is_crouching'] is False
                and base.player_states['is_mounted']
                and base.player_states['horse_riding']):
            self.fsm_player.request("Idle", player,
                                    anims[anim_names.a_anim_horse_rider_idle],
                                    "play")
            if self.base.game_instance['player_props']['stamina'] < 100:
                self.base.game_instance['player_props']['stamina'] += 5

            if (self.base.game_instance['hud_np']
                    and self.base.game_instance['hud_np'].player_bar_ui_stamina):
                if self.base.game_instance['hud_np'].player_bar_ui_stamina['value'] < 100:
                    self.base.game_instance['hud_np'].player_bar_ui_stamina['value'] += 5
                    stamina = self.base.game_instance['hud_np'].player_bar_ui_stamina['value']
                    player.set_python_tag("stamina", stamina)

    def _rider_actions_set(self, player, anims):
        if base.player_state_unarmed:
            self._rider_movement(anims)
            self._rider_regular_actions(anims)
            self._rider_equip_actions(player, anims)

            if not self.base.game_instance["is_indoor"]:
                self._rider_battle_actions(player, anims)

        if base.player_state_armed:
            self._rider_movement(anims)
            self._rider_regular_actions(anims)
            self._rider_equip_actions(player, anims)

            if not self.base.game_instance["is_indoor"]:
                self._rider_battle_actions(player, anims)

        if base.player_state_magic:
            self._rider_movement(anims)
            self._rider_regular_actions(anims)
            self._rider_equip_actions(player, anims)

            if not self.base.game_instance["is_indoor"]:
                self._rider_battle_actions(player, anims)
                self._rider_battle_magic_actions(player, anims)

    """ Player Actions """
    def _regular_movement(self, player, anims):
        self.mov_actions.player_movement_action(player, anims)
        self.mov_actions.player_run_action(player, anims)
        self.actions.player_forwardroll_action(player, anims)

    def _regular_actions(self, player, anims):
        self.actions.player_crouch_action(player, 'crouch', anims)
        self.actions.player_jump_action(player, "jump", anims, anim_names.a_anim_jumping)

        if (not base.player_states['has_sword']
                and not base.player_states['has_bow']):
            self.actions.player_use_action(player, "use", anims, anim_names.a_anim_picking)
    
            self.actions.player_attack_action(player, "attack", anims, anim_names.a_anim_attack)
            self.actions.player_h_kick_action(player, "h_attack", anims, anim_names.a_anim_h_attack)
            self.actions.player_f_kick_action(player, "f_attack", anims, anim_names.a_anim_f_attack)
            self.actions.player_block_action(player, "block", anims, anim_names.a_anim_blocking)

    def _regular_equip_actions(self, player, anims):
        if not self.base.game_instance["is_player_laying"]:
            self.actions.player_get_sword_action(player, "sword", anims,
                                                 anim_names.a_anim_arm_sword)
            self.actions.player_get_bow_action(player, "bow", anims, anim_names.a_anim_arm_bow)

        elif not self.base.game_instance["is_player_sitting"]:
            self.actions.player_get_sword_action(player, "sword", anims,
                                                 anim_names.a_anim_arm_sword)
            self.actions.player_get_bow_action(player, "bow", anims, anim_names.a_anim_arm_bow)

    def _battle_actions(self, player, anims):
        if base.player_states['has_sword'] and not base.player_states['has_bow']:
            self.actions.player_attack_action(player, "attack", anims, anim_names.a_anim_melee_attack)
            self.actions.player_block_action(player, "block", anims, anim_names.a_anim_parring)
        elif not base.player_states['has_sword'] and base.player_states['has_bow']:
            self.actions.player_bow_shoot_action(player, anims, anim_names.a_anim_archery)

    def _battle_magic_actions(self, player, anims):
        self.actions.player_tengri_action(player, "tengri", anims, anim_names.a_anim_get_tengri)
        self.actions.player_umai_action(player, "umai", anims, anim_names.a_anim_get_umai)

    """ Rider Player Actions """
    def _rider_movement(self, anims):
        self.mov_actions.horse_riding_movement_action(anims)
        self.mov_actions.horse_riding_run_action(anims)

    def _rider_regular_actions(self, anims):
        # TODO: add crouch and jump actions for the rider
        pass
        # self.actions.player_crouch_action(player, 'crouch', anims)
        # self.actions.player_jump_action(player, "jump", anims,
        # anim_names.a_anim_horse_rider_jumping)

    def _rider_equip_actions(self, player, anims):
        self.actions.player_horse_riding_get_sword_action(player, "sword", anims,
                                                          anim_names.a_anim_horse_rider_arm_sword)
        self.actions.player_horse_riding_get_bow_action(player, "bow", anims,
                                                        anim_names.a_anim_horse_rider_arm_bow)

    def _rider_battle_actions(self, player, anims):
        if base.player_states['has_sword'] and not base.player_states['has_bow']:
            self.actions.player_horse_riding_swing_action(player, "attack", anims,
                                                          anim_names.a_anim_horse_rider_swing)
        elif not base.player_states['has_sword'] and base.player_states['has_bow']:
            self.actions.player_horse_riding_bow_shoot_action(player, anims,
                                                              anim_names.a_anim_horse_rider_archery)

    def _rider_battle_magic_actions(self, player, anims):
        # TODO: add magic actions for the rider
        self.actions.player_tengri_action(player, "tengri", anims, anim_names.a_anim_horse_riger_get_tengri)
        self.actions.player_umai_action(player, "umai", anims, anim_names.a_anim_horse_riger_get_umai)

    """ Prepares the player for scene """
    def player_actions_task(self, player, anims, task):
        if player and anims and base.player_states["is_alive"]:
            if (not self.base.game_instance["is_player_sitting"]
                    and not self.base.game_instance["is_player_laying"]):
                # Define player actions
                if not player.get_python_tag("is_on_horse"):
                    self._regular_anim_state_tracker(player, anims)
                elif player.get_python_tag("is_on_horse"):
                    self._rider_anim_state_tracker(player, anims)

                # Here we accept keys to do actions
                if not self.base.game_instance['ui_mode']:

                    if base.player_states["horse_is_ready_to_be_used"]:
                        self.actions.mount_action()

                    if not base.player_states['is_mounted']:
                        self._regular_actions_set(player, anims)

                    elif base.player_states['is_mounted']:
                        self._rider_actions_set(player, anims)

        return task.cont

    """ Prepares actions for scene"""

    def player_actions_init(self, player, anims):
        if (player
                and anims
                and isinstance(anims, dict)):

            for key in base.player_states:
                if key != "is_alive":
                    base.player_states[key] = False
                else:
                    base.player_states[key] = True
            self.base.game_instance['player_actions_init_is_activated'] = 0
            if self.game_settings['Debug']['set_editor_mode'] == 'YES':
                self.player = player

                physics_attr = self.base.game_instance["physics_attr_cls"]
                physics_attr.set_actor_collider(actor=self.player,
                                                col_name='{0}:BS'.format(self.player.get_name()),
                                                shape="capsule",
                                                type="player")

                # Define player weapons here
                self.state.set_player_equipment(player, "Korlan:Spine1")
                taskMgr.add(self.archery.prepare_arrows_helper(arrow_name="bow_arrow_kazakh",
                                                               joint_name="Korlan:Spine1"))

            elif self.game_settings['Debug']['set_editor_mode'] == 'NO':
                # Set the field of view
                self.base.game_instance["lens"].set_fov(self.base.game_instance["fov_indoor"])

                self.player = player
                self.kbd.keymap_init()
                self.kbd.keymap_init_released()
                self.base.game_instance["kbd_np"] = self.kbd
                base.input_state = self.kbd.bullet_keymap_init()
                self.archery.is_arrow_ready = False

                # Define player actions here
                self.mov_actions = PlayerMovement(self.kbd, self.state)
                self.actions = PlayerActions(self.kbd, self.state, self.archery)

                self.base.game_instance['person_look_mode'] = self.game_settings['Main']['person_look_mode']

                # Define mouse system
                self.mouse.mouse_wheel_init()

                # Define player's floater
                self.floater = self.mouse.set_floater(self.player)

                # Define player collider
                physics_attr = self.base.game_instance["physics_attr_cls"]
                physics_attr.set_actor_collider(actor=self.player,
                                                col_name='{0}:BS'.format(self.player.get_name()),
                                                shape="capsule",
                                                type="player")

                taskMgr.add(self.mouse.mouse_control_task,
                            "mouse_control_task",
                            appendTask=True)

                # Define player sheet here
                # Open and close sheet
                # Accept close_sheet command from close button, because
                # I suddenly can't do it inside the sheet class
                self.sheet = Sheet()
                self.sheet.sheet_init()
                self.base.game_instance["sheet_cls"] = self.sheet
                base.accept('i', self.sheet.set_sheet)
                base.accept('close_sheet', self.sheet.clear_sheet)

                # Add another initial arrows stack to inventory
                self.sheet.add_item_to_inventory(item="Arrows",
                                                 count=10,
                                                 inventory="INVENTORY_2",
                                                 item_type="weapon")
                self.base.shared_functions['add_item_to_inventory'] = self.sheet.add_item_to_inventory

                # Define player weapons here
                self.state.set_player_equipment(player, "Korlan:Spine1")
                taskMgr.add(self.archery.prepare_arrows_helper(arrow_name="bow_arrow_kazakh",
                                                               joint_name="Korlan:Spine1"))
                # Set Ground/Water Switching task
                taskMgr.add(self.actions.ground_water_action_switch_task,
                            "ground_water_action_switch_task")

                # Start actions
                base.player_states['is_idle'] = True

                taskMgr.add(self.player_actions_task, "player_actions_task",
                            extraArgs=[player, anims],
                            appendTask=True)

            self.base.game_instance['player_actions_init_is_activated'] = 1

