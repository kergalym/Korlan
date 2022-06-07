from Engine.Actors.Player.state import PlayerState
from Engine.FSM.player_fsm import PlayerFSM
from direct.task.TaskManagerGlobal import taskMgr
from Settings.Input.keyboard import Keyboard
from Settings.Input.mouse import Mouse
from Settings.Input.player_camera import PlayerCamera
from Engine.Inventory.sheet import Sheet
from Engine.Actors.Player.player_archery import PlayerArchery
from Engine.Actors.Player.player_movement import PlayerMovement
from Engine.Actors.Player.player_actions import PlayerActions


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
        self.player_cam = PlayerCamera()
        self.fsm_player = PlayerFSM()
        self.sheet = Sheet()
        self.state = PlayerState()
        self.archery = PlayerArchery()
        self.mov_actions = None
        self.actions = None
        self.base.is_cutscene_active = False

    """ Prepares the player for scene """

    def player_actions_task(self, player, anims, task):
        if player and anims:
            if (not self.base.game_instance["is_player_sitting"]
                    and not self.base.game_instance["is_player_laying"]):
                # Define player actions
                if not player.get_python_tag("is_on_horse"):
                    any_action = player.get_anim_control(anims[self.mov_actions.idle_action])
                    if (any_action.is_playing() is False
                            and base.player_states['is_idle']
                            and base.player_states['is_attacked'] is False
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
                                                anims[self.mov_actions.idle_action],
                                                "play")
                        if self.base.game_instance['player_props']['stamina'] < 100:
                            self.base.game_instance['player_props']['stamina'] += 5

                        if (self.base.game_instance['hud_np']
                                and self.base.game_instance['hud_np'].player_bar_ui_stamina):
                            if self.base.game_instance['hud_np'].player_bar_ui_stamina['value'] < 100:
                                self.base.game_instance['hud_np'].player_bar_ui_stamina['value'] += 5
                                stamina = self.base.game_instance['hud_np'].player_bar_ui_stamina['value']
                                player.set_python_tag("health", stamina)

                elif player.get_python_tag("is_on_horse"):
                    any_action = player.get_anim_control(anims['horse_riding_idle'])
                    if (any_action.is_playing() is False
                            and base.player_states['is_idle']
                            and base.player_states['is_attacked'] is False
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
                                                anims['horse_riding_idle'],
                                                "play")
                        if self.base.game_instance['player_props']['stamina'] < 100:
                            self.base.game_instance['player_props']['stamina'] += 5

                        if (self.base.game_instance['hud_np']
                                and self.base.game_instance['hud_np'].player_bar_ui_stamina):
                            if self.base.game_instance['hud_np'].player_bar_ui_stamina['value'] < 100:
                                self.base.game_instance['hud_np'].player_bar_ui_stamina['value'] += 5
                                stamina = self.base.game_instance['hud_np'].player_bar_ui_stamina['value']
                                player.set_python_tag("health", stamina)

                # Here we accept keys
                if (not self.base.game_instance['ui_mode']
                        and not self.base.game_instance['dev_ui_mode']
                        or self.base.game_instance['dev_ui_mode']):
                    if base.player_state_unarmed:
                        if self.floater and not base.player_states['is_mounted']:
                            self.mov_actions.player_movement_action(player, anims)
                            self.mov_actions.player_run_action(player, anims)
                            self.actions.player_forwardroll_action(player, anims)
                        elif base.player_states['is_mounted']:
                            self.mov_actions.horse_riding_movement_action(anims)
                            self.mov_actions.horse_riding_run_action(anims)

                if (not self.base.game_instance['ui_mode']
                        and not self.base.game_instance['dev_ui_mode']):

                    # is horse ready?
                    if base.player_states["horse_is_ready_to_be_used"]:
                        self.actions.mount_action(anims)

                    if not base.player_states['is_mounted']:
                        if base.player_state_unarmed:
                            self.actions.player_crouch_action(player, 'crouch', anims)
                            self.actions.player_jump_action(player, "jump", anims, "Jumping")
                            self.actions.player_use_action(player, "use", anims, "PickingUp")

                            if not self.base.game_instance["is_indoor"]:
                                self.actions.player_attack_action(player, "attack", anims, "Boxing")
                                self.actions.player_h_kick_action(player, "h_attack", anims, "Kicking_3")
                                self.actions.player_f_kick_action(player, "f_attack", anims, "Kicking_5")
                                self.actions.player_block_action(player, "block", anims, "center_blocking")
                                self.actions.player_get_sword_action(player, "sword", anims,
                                                                     "sword_disarm_over_shoulder")
                                self.actions.player_get_bow_action(player, "bow", anims, "archer_standing_disarm_bow")

                        if base.player_state_armed:
                            if self.floater:
                                self.mov_actions.player_movement_action(player, anims)
                                self.mov_actions.player_run_action(player, anims)
                                self.actions.player_forwardroll_action(player, anims)

                                self.actions.player_crouch_action(player, 'crouch', anims)
                                self.actions.player_jump_action(player, "jump", anims, "Jumping")
                                self.actions.player_use_action(player, "use", anims, "PickingUp")
                            elif base.player_states['is_mounted']:
                                self.mov_actions.horse_riding_movement_action(anims)
                                self.mov_actions.horse_riding_run_action(anims)

                            if not self.base.game_instance["is_indoor"]:
                                if base.player_states['has_sword'] and not base.player_states['has_bow']:
                                    self.actions.player_attack_action(player, "attack", anims, "great_sword_slash")
                                    self.actions.player_block_action(player, "block", anims, "great_sword_blocking")
                                elif not base.player_states['has_sword'] and base.player_states['has_bow']:
                                    self.actions.player_bow_shoot_action(player, anims, "archer_standing_draw_arrow")

                                self.actions.player_h_kick_action(player, "h_attack", anims, "Kicking_3")
                                self.actions.player_f_kick_action(player, "f_attack", anims, "Kicking_5")
                                self.actions.player_get_sword_action(player, "sword", anims,
                                                                     "sword_disarm_over_shoulder")
                                self.actions.player_get_bow_action(player, "bow", anims, "archer_standing_disarm_bow")

                        if base.player_state_magic:
                            if self.floater:
                                self.mov_actions.player_movement_action(player, anims)
                                self.mov_actions.player_run_action(player, anims)
                                self.actions.player_forwardroll_action(player, anims)

                                self.actions.player_crouch_action(player, 'crouch', anims)
                                self.actions.player_jump_action(player, "jump", anims, "Jumping")
                                self.actions.player_use_action(player, "use", anims, "PickingUp")

                                if not self.base.game_instance["is_indoor"]:
                                    self.actions.player_h_kick_action(player, "h_attack", anims, "Kicking_3")
                                    self.actions.player_f_kick_action(player, "f_attack", anims, "Kicking_5")
                                    self.actions.player_block_action(player, "block", anims, "center_blocking")
                                    self.actions.player_tengri_action(player, "tengri", anims, "PickingUp")
                                    self.actions.player_umai_action(player, "umai", anims, "PickingUp")

                    elif base.player_states['is_mounted']:
                        if base.player_state_unarmed:
                            if self.floater:
                                self.mov_actions.horse_riding_movement_action(anims)
                                self.mov_actions.horse_riding_run_action(anims)
                            # todo: add getting sword and bow anims
                            """self.actions.player_crouch_action(player, 'crouch', anims)
                            self.actions.player_jump_action(player, "jump", anims, "Jumping")"""
                            self.actions.player_horse_riding_get_sword_action(player, "sword", anims,
                                                                              "horse_riding_arm_sword")
                            self.actions.player_horse_riding_get_bow_action(player, "bow", anims,
                                                                            "horse_riding_arm_bow")
                        if base.player_state_armed:
                            if self.floater:
                                self.mov_actions.horse_riding_movement_action(anims)
                                self.mov_actions.horse_riding_run_action(anims)

                            # todo: add getting sword and bow anims
                            """self.actions.player_crouch_action(player, 'crouch', anims)
                            self.actions.player_jump_action(player, "jump", anims, "Jumping")"""

                            if base.player_states['has_sword'] and not base.player_states['has_bow']:
                                self.actions.player_horse_riding_swing_action(player, "attack", anims,
                                                                              "horse_riding_swing")
                            elif not base.player_states['has_sword'] and base.player_states['has_bow']:
                                self.actions.player_horse_riding_bow_shoot_action(player, anims,
                                                                                  "horse_riding_draw_arrow")

                            self.actions.player_horse_riding_get_sword_action(player, "sword", anims,
                                                                              "horse_riding_disarm_sword")
                            self.actions.player_horse_riding_get_bow_action(player, "bow", anims,
                                                                            "horse_riding_disarm_bow")
                        if base.player_state_magic:
                            if self.floater:
                                self.mov_actions.horse_riding_movement_action(anims)
                                self.mov_actions.horse_riding_run_action(anims)

                            # todo: add crouch and jump anims
                            """self.actions.player_crouch_action(player, 'crouch', anims)
                            self.actions.player_jump_action(player, "jump", anims, "Jumping")"""

                            # fixme
                            """self.actions.player_tengri_action(player, "tengri", anims, "PickingUp")
                            self.actions.player_umai_action(player, "umai", anims, "PickingUp")"""

        return task.cont

    """ Prepares actions for scene"""

    def player_actions_init(self, player, anims):
        if (player
                and anims
                and isinstance(anims, dict)):

            for key in base.player_states:
                if key != "is_alive":
                    base.player_states[key] = False

            self.base.game_instance['player_actions_init_is_activated'] = 0
            if self.game_settings['Debug']['set_editor_mode'] == 'NO':
                self.player = player
                self.kbd.keymap_init()
                self.kbd.keymap_init_released()
                self.base.game_instance["kbd_np"] = self.kbd
                base.input_state = self.kbd.bullet_keymap_init()
                self.archery.is_arrow_ready = False

                self.mov_actions = PlayerMovement(self.kbd, self.state)
                self.actions = PlayerActions(self.kbd, self.state, self.archery)

                self.base.game_instance['person_look_mode'] = self.game_settings['Main']['person_look_mode']

                # Define Mouse System
                self.mouse.mouse_wheel_init()
                self.floater = self.mouse.set_floater(self.player)
                self.base.messenger.send("add_bullet_collider")

                taskMgr.add(self.mouse.mouse_control_task,
                            "mouse_control_task",
                            appendTask=True)

                # Set Camera System
                taskMgr.add(self.player_cam.set_camera_trigger,
                            "set_camera_trigger",
                            appendTask=True)

                # Define player sheet here
                # Open and close sheet
                # Accept close_sheet command from close button, because
                # I suddenly can't do it inside the sheet class
                # self.sheet = Sheet()
                base.accept('i', self.sheet.set_sheet)
                base.accept('close_sheet', self.sheet.clear_sheet)

                # Add another initial arrows stack to inventory
                self.sheet.add_item_to_inventory(item="Arrows",
                                                 count=10,
                                                 inventory="INVENTORY_2",
                                                 inventory_type="weapon")
                self.base.shared_functions['add_item_to_inventory'] = self.sheet.add_item_to_inventory

                # Define player attack here
                self.state.set_player_equipment(player, "Korlan:Spine1")
                taskMgr.add(self.archery.prepare_arrows_helper(arrow_name="bow_arrow_kazakh",
                                                               joint_name="Korlan:Spine1"))
                # Set Ground/Water Switching task
                taskMgr.add(self.actions.ground_water_action_switch_task,
                            "ground_water_action_switch_task")

                # Start actions
                taskMgr.add(self.player_actions_task, "player_actions_task",
                            extraArgs=[player, anims],
                            appendTask=True)

            self.base.game_instance['player_actions_init_is_activated'] = 1

