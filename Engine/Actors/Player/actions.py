from panda3d.core import Vec3, BitMask32

from Engine.Actors.Player.state import PlayerState
from Engine.FSM.player_fsm import PlayerFSM
from direct.interval.IntervalGlobal import *
from direct.task.TaskManagerGlobal import taskMgr
from Settings.Input.keyboard import Keyboard
from Settings.Input.mouse import Mouse
from Settings.Input.player_camera import PlayerCamera
from Engine.Inventory.sheet import Sheet
from Engine.Actors.archery import Archery


class Actions:

    def __init__(self):
        self.game_settings = base.game_settings
        self.base = base
        self.render = render
        self.actor_play_rate = None
        self.idle_action = "Standing_idle_female"
        self.walking_forward_action = "Walking"
        self.run_forward_action = "Running"
        self.crouch_walking_forward_action = 'crouch_walking_forward'
        self.crouched_to_standing_action = "crouched_to_standing"
        self.standing_to_crouch_action = "standing_to_crouch"

        self.horse_idle_action = "horse_idle"
        self.horse_walking_forward_action = "horse_walking"
        self.horse_run_forward_action = "horse_running"
        self.horse_crouch_walking_forward_action = ""
        self.horse_crouched_to_standing_action = ""
        self.horse_standing_to_crouch_action = ""

        self.korlan = None
        self.player = None
        self.player_bs = None
        self.floater = None
        self.taskMgr = taskMgr
        self.kbd = Keyboard()
        self.mouse = Mouse()
        self.player_cam = PlayerCamera()
        self.fsm_player = PlayerFSM()
        self.sheet = Sheet()
        self.state = PlayerState()
        self.archery = Archery("Player")
        self.base.is_cutscene_active = False

    """ Play animation after action """

    def seq_turning_wrapper(self, player, anims, action, state):
        if player and anims and isinstance(state, str):
            turning_seq = player.get_anim_control(anims[action])
            if state == 'loop' and turning_seq.is_playing() is False:
                base.player_states["idle"] = False
                player.loop(anims[action])
                player.set_play_rate(self.base.actor_play_rate,
                                     anims[self.walking_forward_action])
            elif state == 'stop' and turning_seq.is_playing():
                player.stop()
                player.pose(anims[action], 0)

    def seq_horse_turning_wrapper(self, player, anims, action, state):
        if player and anims and isinstance(state, str):
            turning_seq = player.get_anim_control(anims[action])
            if state == 'loop' and turning_seq.is_playing() is False:
                base.player_states["idle"] = False
                player.loop(anims[action])
                player.set_play_rate(self.base.actor_play_rate,
                                     anims[self.horse_walking_forward_action])
            elif state == 'stop' and turning_seq.is_playing():
                player.stop()
                player.pose(anims[action], 0)

    def seq_move_wrapper(self, player, anims, state):
        if player and anims and isinstance(state, str):
            walking_forward_seq = player.get_anim_control(anims[self.walking_forward_action])
            if state == 'loop' and walking_forward_seq.is_playing() is False:
                player.loop(anims[self.walking_forward_action])
                player.set_play_rate(self.base.actor_play_rate,
                                     anims[self.walking_forward_action])
            elif state == 'stop' and walking_forward_seq.is_playing():
                player.stop()
                player.pose(anims[self.walking_forward_action], 0)

    def seq_run_wrapper(self, player, anims, state):
        if player and anims and isinstance(state, str):
            run_forward_seq = player.get_anim_control(anims[self.run_forward_action])
            if state == 'loop' and run_forward_seq.is_playing() is False:
                player.loop(anims[self.run_forward_action])
                player.set_play_rate(2.2,
                                     anims[self.run_forward_action])
            elif state == 'stop' and run_forward_seq.is_playing():
                player.stop()
                player.pose(anims[self.run_forward_action], 0)

    def seq_horse_move_wrapper(self, player, anims, state):
        if player and anims and isinstance(state, str):
            walking_forward_seq = player.get_anim_control(anims[self.horse_walking_forward_action])
            if state == 'loop' and walking_forward_seq.is_playing() is False:
                player.stop(self.horse_idle_action)
                player.loop(anims[self.horse_walking_forward_action])
                player.set_play_rate(self.base.actor_play_rate,
                                     anims[self.horse_walking_forward_action])
            elif state == 'stop' and walking_forward_seq.is_playing():
                player.stop(self.horse_walking_forward_action)
                player.pose(anims[self.horse_walking_forward_action], 0)
                player.loop(self.horse_idle_action)

    def seq_horse_run_wrapper(self, player, anims, state):
        if player and anims and isinstance(state, str):
            run_forward_seq = player.get_anim_control(anims[self.horse_run_forward_action])
            if state == 'loop' and run_forward_seq.is_playing() is False:
                player.stop(self.horse_idle_action)
                player.loop(anims[self.horse_run_forward_action])
                player.set_play_rate(2.2,
                                     anims[self.horse_run_forward_action])
            elif state == 'stop' and run_forward_seq.is_playing():
                player.stop(self.horse_run_forward_action)
                player.pose(anims[self.horse_run_forward_action], 0)
                player.loop(self.horse_idle_action)

    def seq_crouch_move_wrapper(self, player, anims, state):
        if player and anims and isinstance(state, str):
            crouch_walking_forward_seq = player.get_anim_control(anims[self.crouch_walking_forward_action])
            if state == 'loop' and crouch_walking_forward_seq.is_playing() is False:
                player.loop(anims[self.crouch_walking_forward_action])
                if self.kbd.keymap['backward']:
                    player.set_play_rate(-self.base.actor_play_rate,
                                         anims[self.crouch_walking_forward_action])
                else:
                    player.set_play_rate(self.base.actor_play_rate,
                                         anims[self.crouch_walking_forward_action])
            elif state == 'stop' and crouch_walking_forward_seq.is_playing():
                player.stop()
                player.pose(anims[self.crouch_walking_forward_action], 0)

    def seq_horse_crouch_move_wrapper(self, player, anims, state):
        if player and anims and isinstance(state, str):
            crouch_walking_forward_seq = player.get_anim_control(anims[self.horse_crouch_walking_forward_action])
            if state == 'loop' and crouch_walking_forward_seq.is_playing() is False:
                player.stop(self.horse_idle_action)
                player.loop(anims[self.horse_crouch_walking_forward_action])
                if self.kbd.keymap['backward']:
                    player.set_play_rate(-self.base.actor_play_rate,
                                         anims[self.horse_crouch_walking_forward_action])
                else:
                    player.set_play_rate(self.base.actor_play_rate,
                                         anims[self.horse_crouch_walking_forward_action])
            elif state == 'stop' and crouch_walking_forward_seq.is_playing():
                player.stop()
                player.pose(anims[self.horse_crouch_walking_forward_action], 0)
                player.loop(self.horse_idle_action)

    """ Sets current player position after action """

    def seq_set_player_pos_wrapper(self, player, pos_y):
        if (player and pos_y
                and isinstance(pos_y, float)):
            player = self.base.get_actor_bullet_shape_node(asset=player.get_name(), type="Player")
            if player:
                player.set_y(player, pos_y)

    """ Helps to coordinate the bullet shape with player actions """

    def player_bullet_jump_helper(self):
        if self.base.game_instance['player_controller_np']:
            # TODO: Implement player_bullet_jump_helper
            # self.base.game_instance['player_controller_np'].get_shape().set_local_scale(Vec3(1, 1, 1))
            if not self.base.game_instance['player_controller_np'].is_on_ground():
                self.base.game_instance['player_controller_np'].set_max_jump_height(2.0)
                self.base.game_instance['player_controller_np'].set_jump_speed(self.base.actor_play_rate)

    def player_bullet_crouch_helper(self):
        if self.base.game_instance['player_controller_np']:
            # TODO: Implement player_bullet_crouch_helper
            """size = 0.6
            print(self.base.game_instance['player_controller_np'].get_shape().get_local_scale())
            self.base.game_instance['player_controller_np'].get_shape().set_local_scale(Vec3(1, 1, size))"""

    def ground_water_action_switch_task(self, task):
        if self.base.game_instance['menu_mode']:
            return task.done

        if self.base.game_instance['water_trigger_np']:
            trigger_np = self.base.game_instance['water_trigger_np']
            for node in trigger_np.node().get_overlapping_nodes():
                if "Player" in node.get_name():
                    # todo: change idle_action to swim_idle
                    if self.idle_action != "Standing_idle_female":
                        self.idle_action = "Standing_idle_female"
                    if self.walking_forward_action != "Swimming":
                        self.walking_forward_action = "Swimming"
                else:
                    if self.idle_action != "Standing_idle_female":
                        self.idle_action = "Standing_idle_female"
                    if self.walking_forward_action != "Walking":
                        self.walking_forward_action = "Walking"

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
                taskMgr.add(self.ground_water_action_switch_task,
                            "ground_water_action_switch_task")

                # Start actions
                taskMgr.add(self.player_actions_task, "player_actions_task",
                            extraArgs=[player, anims],
                            appendTask=True)

            self.base.game_instance['player_actions_init_is_activated'] = 1

    """ Prepares the player for scene """

    def player_actions_task(self, player, anims, task):
        if player and anims:
            if (not self.base.game_instance["is_player_sitting"]
                    and not self.base.game_instance["is_player_laying"]):
                # Define player actions
                if not player.get_python_tag("is_on_horse"):
                    any_action = player.get_anim_control(anims[self.idle_action])
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
                                                anims[self.idle_action],
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
                            self.player_movement_action(player, anims)
                            self.player_run_action(player, anims)
                            self.player_forwardroll_action(player, anims)
                        elif base.player_states['is_mounted']:
                            self.horse_riding_movement_action(anims)
                            self.horse_riding_run_action(anims)

                if (not self.base.game_instance['ui_mode']
                        and not self.base.game_instance['dev_ui_mode']):

                    # is horse ready?
                    if base.player_states["horse_is_ready_to_be_used"]:
                        self.mount_action(anims)

                    if not base.player_states['is_mounted']:
                        if base.player_state_unarmed:
                            self.player_crouch_action(player, 'crouch', anims)
                            self.player_jump_action(player, "jump", anims, "Jumping")
                            self.player_use_action(player, "use", anims, "PickingUp")

                            if not self.base.game_instance["is_indoor"]:
                                self.player_attack_action(player, "attack", anims, "Boxing")
                                self.player_h_kick_action(player, "h_attack", anims, "Kicking_3")
                                self.player_f_kick_action(player, "f_attack", anims, "Kicking_5")
                                self.player_block_action(player, "block", anims, "center_blocking")
                                self.player_get_sword_action(player, "sword", anims, "sword_disarm_over_shoulder")
                                self.player_get_bow_action(player, "bow", anims, "archer_standing_disarm_bow")

                        if base.player_state_armed:
                            if self.floater:
                                self.player_movement_action(player, anims)
                                self.player_run_action(player, anims)
                                self.player_forwardroll_action(player, anims)

                                self.player_crouch_action(player, 'crouch', anims)
                                self.player_jump_action(player, "jump", anims, "Jumping")
                                self.player_use_action(player, "use", anims, "PickingUp")
                            elif base.player_states['is_mounted']:
                                self.horse_riding_movement_action(anims)
                                self.horse_riding_run_action(anims)

                            if not self.base.game_instance["is_indoor"]:
                                if base.player_states['has_sword'] and not base.player_states['has_bow']:
                                    self.player_attack_action(player, "attack", anims, "great_sword_slash")
                                    self.player_block_action(player, "block", anims, "great_sword_blocking")
                                elif not base.player_states['has_sword'] and base.player_states['has_bow']:
                                    self.player_bow_shoot_action(player, anims, "archer_standing_draw_arrow")

                                self.player_h_kick_action(player, "h_attack", anims, "Kicking_3")
                                self.player_f_kick_action(player, "f_attack", anims, "Kicking_5")
                                self.player_get_sword_action(player, "sword", anims, "sword_disarm_over_shoulder")
                                self.player_get_bow_action(player, "bow", anims, "archer_standing_disarm_bow")

                        if base.player_state_magic:
                            if self.floater:
                                self.player_movement_action(player, anims)
                                self.player_run_action(player, anims)
                                self.player_forwardroll_action(player, anims)

                                self.player_crouch_action(player, 'crouch', anims)
                                self.player_jump_action(player, "jump", anims, "Jumping")
                                self.player_use_action(player, "use", anims, "PickingUp")

                                if not self.base.game_instance["is_indoor"]:
                                    self.player_h_kick_action(player, "h_attack", anims, "Kicking_3")
                                    self.player_f_kick_action(player, "f_attack", anims, "Kicking_5")
                                    self.player_block_action(player, "block", anims, "center_blocking")
                                    self.player_tengri_action(player, "tengri", anims, "PickingUp")
                                    self.player_umai_action(player, "umai", anims, "PickingUp")

                    elif base.player_states['is_mounted']:
                        if base.player_state_unarmed:
                            if self.floater:
                                self.horse_riding_movement_action(anims)
                                self.horse_riding_run_action(anims)
                            # todo: add getting sword and bow anims
                            """self.player_crouch_action(player, 'crouch', anims)
                            self.player_jump_action(player, "jump", anims, "Jumping")"""
                            self.player_horse_riding_get_sword_action(player, "sword", anims, "horse_riding_arm_sword")
                            self.player_horse_riding_get_bow_action(player, "bow", anims, "horse_riding_arm_bow")
                        if base.player_state_armed:
                            if self.floater:
                                self.horse_riding_movement_action(anims)
                                self.horse_riding_run_action(anims)

                            # todo: add getting sword and bow anims
                            """self.player_crouch_action(player, 'crouch', anims)
                            self.player_jump_action(player, "jump", anims, "Jumping")"""

                            if base.player_states['has_sword'] and not base.player_states['has_bow']:
                                self.player_horse_riding_swing_action(player, "attack", anims,
                                                                      "horse_riding_swing")
                            elif not base.player_states['has_sword'] and base.player_states['has_bow']:
                                self.player_horse_riding_bow_shoot_action(player, anims,
                                                                          "horse_riding_draw_arrow")

                            self.player_horse_riding_get_sword_action(player, "sword", anims, "horse_riding_disarm_sword")
                            self.player_horse_riding_get_bow_action(player, "bow", anims, "horse_riding_disarm_bow")
                        if base.player_state_magic:
                            if self.floater:
                                self.horse_riding_movement_action(anims)
                                self.horse_riding_run_action(anims)

                            # todo: add crouch and jump anims
                            """self.player_crouch_action(player, 'crouch', anims)
                            self.player_jump_action(player, "jump", anims, "Jumping")"""

                            # fixme
                            """self.player_tengri_action(player, "tengri", anims, "PickingUp")
                            self.player_umai_action(player, "umai", anims, "PickingUp")"""

        return task.cont

    def player_movement_action(self, player, anims):
        if (player and isinstance(anims, dict)
                and not self.base.game_instance['is_aiming']
                and not base.player_states['is_using']
                and not base.player_states['is_mounted']
                and not base.player_states['is_crouching']
                and not base.player_states['is_jumping']):
            # If a move-key is pressed, move the player in the specified direction.
            speed = Vec3(0, 0, 0)
            omega = 0.0
            move_unit = 2

            # Get the time that elapsed since last frame
            dt = globalClock.getDt()

            self.player_bs = self.base.get_actor_bullet_shape_node(asset=player.get_name(), type="Player")

            # Turning in place
            if self.kbd.keymap["left"] and self.player_bs:
                self.player_bs.set_h(self.player_bs.get_h() + 100 * dt)
            if self.kbd.keymap["right"] and self.player_bs:
                self.player_bs.set_h(self.player_bs.get_h() - 100 * dt)

            if (not self.kbd.keymap["forward"]
                    and not self.kbd.keymap["run"]
                    and self.kbd.keymap["left"]):
                Sequence(Parallel(Func(self.seq_turning_wrapper, player, anims, "left_turn", 'loop'),
                                  Func(self.state.set_action_state, "is_turning", True)),
                         ).start()
            if (not self.kbd.keymap["forward"]
                    and not self.kbd.keymap["run"]
                    and self.kbd.keymap["right"]):
                Sequence(Parallel(Func(self.seq_turning_wrapper, player, anims, "right_turn", 'loop'),
                                  Func(self.state.set_action_state, "is_turning", True)),
                         ).start()

            # Stop turning in place
            if (not self.kbd.keymap["forward"]
                    and not self.kbd.keymap["run"]
                    and not self.kbd.keymap["left"]):
                Sequence(Parallel(Func(self.seq_turning_wrapper, player, anims, "left_turn", 'stop'),
                                  Func(self.state.set_action_state, "is_turning", False)),
                         ).start()
            if (not self.kbd.keymap["forward"]
                    and not self.kbd.keymap["run"]
                    and not self.kbd.keymap["right"]):
                Sequence(Parallel(Func(self.seq_turning_wrapper, player, anims, "right_turn", 'stop'),
                                  Func(self.state.set_action_state, "is_turning", False)),
                         ).start()

            if (self.kbd.keymap["forward"]
                    and self.kbd.keymap["run"] is False
                    and base.player_states['is_moving']
                    and base.player_states['is_running'] is False
                    and base.player_states['is_attacked'] is False
                    and base.player_states['is_busy'] is False
                    and base.player_states['is_crouch_moving'] is False
                    and base.player_states['is_idle']):
                if (base.input_state.is_set('forward')
                        and self.kbd.keymap["run"] is False):
                    speed.set_y(-move_unit)
            if (self.kbd.keymap["forward"]
                    and self.kbd.keymap["run"] is False
                    and base.player_states['is_moving'] is False
                    and base.player_states['is_attacked'] is False
                    and base.player_states['is_busy'] is False
                    and base.player_states['is_running'] is False
                    and base.player_states['is_crouch_moving']
                    and base.player_states['is_idle']):
                if (base.input_state.is_set('forward')
                        and self.kbd.keymap["run"] is False):
                    speed.set_y(-move_unit)
            if (self.kbd.keymap["backward"]
                    and self.kbd.keymap["run"] is False
                    and self.kbd.keymap["left"] is False
                    and self.kbd.keymap["right"] is False
                    and base.player_states['is_moving']
                    and base.player_states['is_attacked'] is False
                    and base.player_states['is_busy'] is False
                    and base.player_states['is_crouch_moving'] is False
                    and base.player_states['is_idle']):
                if base.input_state.is_set('reverse'):
                    speed.set_y(move_unit)
            if (self.kbd.keymap["backward"]
                    and self.kbd.keymap["run"] is False
                    and self.kbd.keymap["left"] is False
                    and self.kbd.keymap["right"] is False
                    and base.player_states['is_moving'] is False
                    and base.player_states['is_attacked'] is False
                    and base.player_states['is_busy'] is False
                    and base.player_states['is_crouch_moving']
                    and base.player_states['is_idle']):
                if base.input_state.is_set('reverse'):
                    speed.set_y(move_unit)

            if self.base.game_instance['player_controller_np']:
                self.base.game_instance['player_controller_np'].set_linear_movement(speed, True)
                self.base.game_instance['player_controller_np'].set_angular_movement(omega)

            # If the player does action, loop the animation through messenger.
            if (self.kbd.keymap["forward"]
                    and self.kbd.keymap["run"] is False
                    or self.kbd.keymap["backward"]
                    and self.kbd.keymap["run"] is False
                    and self.kbd.keymap["left"] is False
                    and self.kbd.keymap["right"] is False):
                if (base.player_states['is_moving'] is False
                        and base.player_states['is_attacked'] is False
                        and base.player_states['is_busy'] is False
                        and base.player_states['is_crouch_moving'] is False
                        and base.player_states["is_running"] is False
                        and base.player_states['is_idle']):
                    Sequence(Parallel(Func(self.seq_move_wrapper, player, anims, 'loop'),
                                      Func(self.state.set_action_state, "is_moving", True)),
                             ).start()
                if (base.player_states['is_moving'] is False
                        and base.player_states['is_attacked'] is False
                        and base.player_states['is_busy'] is False
                        and base.player_states["is_running"] is False
                        and base.player_states['is_crouch_moving']
                        and base.player_states['is_idle']):
                    Sequence(Func(self.seq_crouch_move_wrapper, player, anims, 'loop')
                             ).start()
            else:
                if (base.player_states['is_moving']
                        and base.player_states['is_attacked'] is False
                        and base.player_states['is_busy'] is False
                        and base.player_states["is_running"] is False
                        and base.player_states['is_crouch_moving'] is False):
                    Sequence(Func(self.seq_move_wrapper, player, anims, 'stop'),
                             Func(self.state.set_action_state, "is_moving", False)
                             ).start()
                if (base.player_states['is_moving'] is False
                        and base.player_states['is_attacked'] is False
                        and base.player_states['is_busy'] is False
                        and base.player_states["is_running"] is False
                        and base.player_states['is_crouch_moving']):
                    Sequence(Func(self.seq_crouch_move_wrapper, player, anims, 'stop')).start()

            # Actor backward movement
            if (self.kbd.keymap["backward"]
                    and base.player_states['is_attacked'] is False
                    and base.player_states['is_busy'] is False
                    and self.kbd.keymap["run"] is False
                    and base.player_states["is_running"] is False
                    and self.kbd.keymap["left"] is False
                    and self.kbd.keymap["right"] is False):
                player.set_play_rate(-1.0,
                                     anims[self.walking_forward_action])

    def player_run_action(self, player, anims):
        if (player and isinstance(anims, dict)
                and not self.base.game_instance['is_aiming']
                and not base.player_states['is_using']
                and not base.player_states['is_mounted']
                and not base.player_states['is_jumping']
                and not base.player_states['is_crouching']
                and not base.player_states['is_crouch_moving']):
            # If a move-key is pressed, move the player in the specified direction.
            speed = Vec3(0, 0, 0)
            move_unit = 7

            # Get the time that elapsed since last frame
            dt = globalClock.getDt()
            seconds = int(60 * dt)

            if (self.kbd.keymap["forward"]
                    and self.kbd.keymap["run"]
                    and not base.player_states['is_jumping']):
                if base.input_state.is_set('forward'):
                    if self.base.game_instance['player_props']['stamina'] > 1:
                        if seconds == 1:
                            self.base.game_instance['player_props']['stamina'] -= move_unit
                            stamina = self.base.game_instance['player_props']['stamina']
                            self.base.game_instance['hud_np'].player_bar_ui_stamina['value'] = stamina
                            player.set_python_tag('stamina', stamina)
                        speed.set_y(-move_unit)

                    if self.base.game_instance['player_controller_np']:
                        self.base.game_instance['player_controller_np'].set_linear_movement(speed, True)

            # If the player does action, loop the animation.
            # If it is standing still, stop the animation.
            if (self.kbd.keymap["forward"]
                    and self.kbd.keymap["run"]):
                if (base.player_states['is_moving'] is False
                        and base.player_states['is_attacked'] is False
                        and base.player_states['is_busy'] is False
                        and base.player_states['is_crouch_moving'] is False
                        and base.player_states["is_running"] is False
                        and base.player_states['is_idle']
                        and player.get_python_tag('stamina') > 1
                        and not player.get_python_tag('stamina') < 3):
                    Sequence(Parallel(Func(self.seq_run_wrapper, player, anims, 'loop'),
                                      Func(self.state.set_action_state, "is_running", True)),
                             ).start()
                if (base.player_states['is_moving'] is False
                        and base.player_states['is_attacked'] is False
                        and base.player_states['is_busy'] is False
                        and base.player_states["is_crouch_moving"] is False
                        and base.player_states['is_running']
                        and base.player_states['is_idle'] is False
                        and player.get_python_tag('stamina') > 1
                        and not player.get_python_tag('stamina') < 3):
                    Sequence(Func(self.seq_run_wrapper, player, anims, 'loop')
                             ).start()
            else:
                if (base.player_states['is_running']
                        and base.player_states['is_attacked'] is False
                        and base.player_states['is_busy'] is False
                        and base.player_states["is_moving"] is False
                        and self.kbd.keymap["left"] is False
                        and self.kbd.keymap["right"] is False
                        and base.player_states['is_crouch_moving'] is False):
                    Sequence(Func(self.seq_run_wrapper, player, anims, 'stop'),
                             Func(self.state.set_action_state, "is_running", False)
                             ).start()

                if not self.kbd.keymap["run"] and player.get_python_tag('stamina') < 2:
                    Sequence(Func(self.seq_run_wrapper, player, anims, 'stop'),
                             Func(self.state.set_action_state, "is_running", False)
                             ).start()

    def horse_riding_movement_action(self, anims):
        if (isinstance(anims, dict)
                and not self.base.game_instance['is_aiming']
                and not base.player_states['is_using']
                and base.player_states['is_mounted']
                and not base.player_states['is_crouching']
                and not base.player_states['is_jumping']):

            # If a move-key is pressed, move the player in the specified direction.
            horse_name = base.game_instance['player_using_horse']
            if self.base.game_instance['actors_ref'].get(horse_name):
                player = self.base.game_instance['actors_ref'][horse_name]
                horse_bs = render.find("**/{0}:BS".format(horse_name))
                move_unit = 2

                # Get the time that elapsed since last frame
                dt = globalClock.getDt()

                # Turning in place
                if self.kbd.keymap["left"] and horse_bs:
                    horse_bs.set_h(horse_bs.get_h() + 100 * dt)
                if self.kbd.keymap["right"] and horse_bs:
                    horse_bs.set_h(horse_bs.get_h() - 100 * dt)

                if (not self.kbd.keymap["forward"]
                        and not self.kbd.keymap["run"]
                        and self.kbd.keymap["left"]):
                    # todo: add anim and uncomment
                    """Sequence(Parallel(Func(self.seq_horse_turning_wrapper, player, anims, "left_turn", 'loop'),
                                      Func(self.state.set_action_state, "is_turning", True)),
                             ).start()"""
                if (not self.kbd.keymap["forward"]
                        and not self.kbd.keymap["run"]
                        and self.kbd.keymap["right"]):
                    # todo: add anim and uncomment
                    """Sequence(Parallel(Func(self.seq_horse_turning_wrapper, player, anims, "right_turn", 'loop'),
                                      Func(self.state.set_action_state, "is_turning", True)),
                             ).start()"""

                # Stop turning in place
                if (not self.kbd.keymap["forward"]
                        and not self.kbd.keymap["run"]
                        and not self.kbd.keymap["left"]):
                    # todo: add anim and uncomment
                    """Sequence(Parallel(Func(self.seq_horse_turning_wrapper, player, anims, "left_turn", 'stop'),
                                      Func(self.state.set_action_state, "is_turning", False)),
                             ).start()"""
                if (not self.kbd.keymap["forward"]
                        and not self.kbd.keymap["run"]
                        and not self.kbd.keymap["right"]):
                    # todo: add anim and uncomment
                    """Sequence(Parallel(Func(self.seq_horse_turning_wrapper, player, anims, "right_turn", 'stop'),
                                      Func(self.state.set_action_state, "is_turning", False)),
                             ).start()"""

                if (self.kbd.keymap["forward"]
                        and self.kbd.keymap["run"] is False):
                    if base.input_state.is_set('forward'):
                        horse_bs.set_y(horse_bs, -move_unit * dt)
                if (self.kbd.keymap["backward"]
                        and self.kbd.keymap["run"] is False):
                    if base.input_state.is_set('reverse'):
                        horse_bs.set_y(horse_bs, move_unit * dt)

                # If the player does action, loop the animation through messenger.
                if (self.kbd.keymap["forward"]
                        and self.kbd.keymap["run"] is False
                        or self.kbd.keymap["backward"]):
                    if (base.player_states['is_moving'] is False
                            and base.player_states['is_attacked'] is False
                            and base.player_states['is_busy'] is False
                            and base.player_states['is_crouch_moving'] is False
                            and base.player_states["is_running"] is False
                            and base.player_states['is_idle']):
                        Sequence(Parallel(Func(self.seq_horse_move_wrapper, player, anims, 'loop'),
                                          Func(self.state.set_action_state, "is_moving", True)),
                                 ).start()
                    if (base.player_states['is_moving'] is False
                            and base.player_states['is_attacked'] is False
                            and base.player_states['is_busy'] is False
                            and base.player_states["is_running"] is False
                            and base.player_states['is_crouch_moving']
                            and base.player_states['is_idle']):
                        # todo: add anim and uncomment
                        """Sequence(Func(self.seq_crouch_horse_move_wrapper, player, anims, 'loop')
                                 ).start()"""
                else:
                    if (base.player_states['is_moving']
                            and base.player_states['is_attacked'] is False
                            and base.player_states['is_busy'] is False
                            and base.player_states["is_running"] is False
                            and base.player_states['is_crouch_moving'] is False):
                        self.seq_horse_move_wrapper(player, anims, 'stop')
                        self.state.set_action_state("is_moving", False)

                    if (base.player_states['is_moving'] is False
                            and base.player_states['is_attacked'] is False
                            and base.player_states['is_busy'] is False
                            and base.player_states["is_running"] is False
                            and base.player_states['is_crouch_moving']):
                        # todo: add anim and uncomment
                        """Sequence(Func(self.seq_horse_crouch_move_wrapper, player, anims, 'stop')).start()"""

                # Actor backward movement
                if (self.kbd.keymap["backward"]
                        and base.player_states['is_attacked'] is False
                        and base.player_states['is_busy'] is False
                        and self.kbd.keymap["run"] is False
                        and base.player_states["is_running"] is False):
                    player.set_play_rate(-1.0,
                                         anims[self.horse_walking_forward_action])

    def horse_riding_run_action(self, anims):
        if (isinstance(anims, dict)
                and not self.base.game_instance['is_aiming']
                and not base.player_states['is_using']
                and base.player_states['is_mounted']
                and not base.player_states['is_jumping']
                and not base.player_states['is_crouching']
                and not base.player_states['is_crouch_moving']):
            # If a move-key is pressed, move the player in the specified direction.
            horse_name = base.game_instance['player_using_horse']
            if self.base.game_instance['actors_ref'].get(horse_name):
                player = self.base.game_instance['actors_ref'][horse_name]
                horse_bs = render.find("**/{0}:BS".format(horse_name))
                move_unit = 7

                # Get the time that elapsed since last frame
                dt = globalClock.getDt()

                if (self.kbd.keymap["forward"]
                        and self.kbd.keymap["run"]):
                    if base.input_state.is_set('forward'):
                        if (player.get_python_tag('stamina')
                                and player.get_python_tag('stamina') > 1):
                            stamina = player.get_python_tag('stamina')
                            stamina -= 5
                            player.set_python_tag("stamina", stamina)
                        if self.base.game_instance['player_props']['stamina'] > 1:
                            self.base.game_instance['player_props']['stamina'] -= 5
                        if self.base.game_instance['hud_np'].player_bar_ui_stamina['value'] > 1:
                            self.base.game_instance['hud_np'].player_bar_ui_stamina['value'] -= 5

                        horse_bs.set_y(horse_bs, -move_unit * dt)

                # If the player does action, loop the animation.
                # If it is standing still, stop the animation.
                if (self.kbd.keymap["forward"]
                        and self.kbd.keymap["run"]):
                    if (base.player_states['is_moving'] is False
                            and base.player_states['is_attacked'] is False
                            and base.player_states['is_busy'] is False
                            and base.player_states['is_crouch_moving'] is False
                            and base.player_states["is_running"] is False
                            and base.player_states['is_idle']):
                        Sequence(Parallel(Func(self.seq_horse_run_wrapper, player, anims, 'loop'),
                                          Func(self.state.set_action_state, "is_running", True)),
                                 ).start()
                    if (base.player_states['is_moving'] is False
                            and base.player_states['is_attacked'] is False
                            and base.player_states['is_busy'] is False
                            and base.player_states["is_crouch_moving"] is False
                            and base.player_states['is_running']
                            and base.player_states['is_idle'] is False):
                        self.seq_horse_run_wrapper(player, anims, 'loop')

                else:
                    if (base.player_states['is_running']
                            and base.player_states['is_attacked'] is False
                            and base.player_states['is_busy'] is False
                            and base.player_states["is_moving"] is False
                            and base.player_states['is_crouch_moving'] is False):
                        self.seq_horse_run_wrapper(player, anims, 'stop'),
                        self.state.set_action_state("is_running", False)

    def player_in_crouched_to_stand_with_any_action(self, player, key, anims, action, is_in_action):
        if player and key and anims and action and is_in_action and isinstance(is_in_action, str):
            crouched_to_standing = player.get_anim_control(anims[self.crouched_to_standing_action])
            if (base.player_states[is_in_action] is False
                    and crouched_to_standing.is_playing() is False
                    and base.player_states['is_crouching'] is False
                    and base.player_states['is_crouch_moving']):
                # TODO: Use blending for smooth transition between animations
                # Do an animation sequence if player is crouched.
                crouch_to_stand_seq = player.actor_interval(anims[self.crouched_to_standing_action],
                                                            playRate=self.base.actor_play_rate)
                any_action_seq = player.actor_interval(anims[action],
                                                       playRate=self.base.actor_play_rate)
                Sequence(crouch_to_stand_seq,
                         Func(self.state.set_action_state_crouched, "is_crouch_moving", False),
                         Func(self.state.set_action_state, is_in_action, True),
                         any_action_seq,
                         Func(self.state.set_action_state, is_in_action, False),
                         Func(self.state.set_do_once_key, key, False),
                         ).start()

    def player_in_crouched_to_stand_with_magic_weapon_action(self, player, key, anims, action, has_weapon):
        if player and key and anims and action and has_weapon and isinstance(has_weapon, str):
            crouched_to_standing = player.get_anim_control(anims[self.crouched_to_standing_action])
            if (base.player_states[has_weapon] is False
                    and crouched_to_standing.is_playing() is False
                    and base.player_states['is_crouching'] is False
                    and base.player_states['is_crouch_moving']):
                # TODO: Use blending for smooth transition between animations
                # Do an animation sequence if player is crouched.
                crouch_to_stand_seq = player.actor_interval(anims[self.crouched_to_standing_action],
                                                            playRate=self.base.actor_play_rate)
                any_action_seq = player.actor_interval(anims[action],
                                                       playRate=self.base.actor_play_rate)
                Sequence(crouch_to_stand_seq,
                         Func(self.state.set_action_state_crouched, "is_crouch_moving", False),
                         Func(self.state.set_action_state, has_weapon, True),
                         any_action_seq,
                         Func(self.state.set_action_state, has_weapon, False),
                         Func(self.state.set_do_once_key, key, False),
                         ).start()

    def player_crouch_action(self, player, key, anims):
        if (player and isinstance(anims, dict)
                and isinstance(key, str)
                and not base.player_states['is_using']
                and not base.player_states['is_moving']
                and not self.base.game_instance['is_aiming']):
            if self.kbd.keymap[key] and not base.do_key_once[key]:
                self.state.set_do_once_key(key, True)
                crouched_to_standing = player.get_anim_control(anims[self.crouched_to_standing_action])
                standing_to_crouch = player.get_anim_control(anims[self.standing_to_crouch_action])
                # If the player does action, play the animation through sequence.
                base.player_states['is_idle'] = False
                if (standing_to_crouch.is_playing() is False
                        and base.player_states['is_idle'] is False
                        and base.player_states['is_crouching'] is False
                        and base.player_states['is_crouch_moving'] is False):
                    self.base.game_instance['is_player_sitting'] = True
                    # TODO: Use blending for smooth transition between animations
                    # Do an animation sequence if player is crouched.
                    stand_to_crouch_seq = player.actor_interval(anims[self.standing_to_crouch_action],
                                                                playRate=self.base.actor_play_rate)
                    Sequence(Func(self.state.set_action_state, "is_crouching", True),
                             stand_to_crouch_seq,
                             Func(self.player_bullet_crouch_helper),
                             Func(self.state.set_action_state, "is_crouching", False),
                             Func(self.state.set_action_state_crouched, "is_crouch_moving", True),
                             Func(self.state.set_do_once_key, key, False),
                             ).start()

                elif (crouched_to_standing.is_playing() is False
                      and base.player_states['is_idle'] is False
                      and base.player_states['is_crouching'] is False
                      and base.player_states['is_crouch_moving']):
                    self.base.game_instance['is_player_sitting'] = False
                    any_action_seq = player.actor_interval(anims[self.crouched_to_standing_action],
                                                           playRate=self.base.actor_play_rate)

                    self.base.game_instance["player_ref"].set_control_effect(self.idle_action, 0.1)
                    self.base.game_instance["player_ref"].set_control_effect(self.crouched_to_standing_action, 0.9)

                    Sequence(any_action_seq,
                             Func(self.state.set_action_state_crouched, "is_crouch_moving", False),
                             Func(self.state.set_do_once_key, key, False),
                             ).start()

    def player_jump_action(self, player, key, anims, action):
        if (player and isinstance(anims, dict)
                and isinstance(action, str)
                and isinstance(key, str)
                and not base.player_states['is_using']
                and not base.player_states['is_moving']
                and not self.base.game_instance['is_aiming']):
            if self.kbd.keymap[key] and not base.do_key_once[key]:
                self.state.set_do_once_key(key, True)
                crouched_to_standing = player.get_anim_control(anims[self.crouched_to_standing_action])
                base.player_states['is_idle'] = False

                self.player_in_crouched_to_stand_with_any_action(player, key, anims, action, "is_jumping")

                if (base.player_states['is_jumping'] is False
                        and crouched_to_standing.is_playing() is False
                        and base.player_states['is_crouch_moving']):
                    crouch_to_stand_seq = player.actor_interval(anims[self.crouched_to_standing_action],
                                                                playRate=self.base.actor_play_rate)
                    # Do an animation sequence if player is stayed.
                    any_action_seq = player.actor_interval(anims[action],
                                                           playRate=self.base.actor_play_rate)
                    Sequence(crouch_to_stand_seq,
                             Func(self.state.set_action_state, "is_jumping", True),
                             Func(self.player_bullet_jump_helper),
                             any_action_seq,
                             Func(self.state.set_action_state, "is_jumping", False),
                             Func(self.state.set_do_once_key, key, False),
                             ).start()

                elif (base.player_states['is_jumping'] is False
                      and crouched_to_standing.is_playing() is False
                      and base.player_states['is_crouch_moving'] is False):
                    # Do an animation sequence if player is stayed.
                    any_action_seq = player.actor_interval(anims[action],
                                                           playRate=self.base.actor_play_rate)
                    Sequence(Func(self.state.set_action_state, "is_jumping", True),
                             Func(self.player_bullet_jump_helper),
                             any_action_seq,
                             Func(self.state.set_action_state, "is_jumping", False),
                             Func(self.state.set_do_once_key, key, False),
                             ).start()

    def player_use_action(self, player, key, anims, action):
        if (player and isinstance(anims, dict)
                and isinstance(action, str)
                and isinstance(key, str)
                and not self.base.game_instance['is_player_sitting']
                and not self.base.game_instance['is_player_laying']
                and not base.player_states['is_using']
                and not base.player_states['is_moving']
                and not self.base.game_instance['is_aiming']):
            if self.kbd.keymap[key] and not base.do_key_once[key]:
                self.state.set_do_once_key(key, True)
                crouched_to_standing = player.get_anim_control(anims[self.crouched_to_standing_action])
                # TODO: DEBUG ME!
                if (not player.get_python_tag("is_item_using")
                        and player.get_python_tag("is_item_ready")):
                    base.player_states['is_idle'] = False

                    if (base.player_states['is_using'] is False
                            and crouched_to_standing.is_playing() is False
                            and base.player_states['is_crouch_moving'] is True):
                        base.player_states['is_standing'] = False
                        # TODO: Use blending for smooth transition between animations
                        # Do an animation sequence if player is crouched.
                        crouch_to_stand_seq = player.actor_interval(anims[self.crouched_to_standing_action],
                                                                    playRate=self.base.actor_play_rate)
                        any_action_seq = player.actor_interval(anims[action],
                                                               playRate=self.base.actor_play_rate)
                        Sequence(crouch_to_stand_seq,
                                 Func(self.state.set_action_state, "is_using", True),
                                 any_action_seq,
                                 Func(self.state.pick_up_item, player, "RightHand"),
                                 Func(self.state.set_action_state, "is_using", False),
                                 Func(self.state.set_do_once_key, key, False),
                                 ).start()

                    elif (base.player_states['is_using'] is False
                          and crouched_to_standing.is_playing() is False
                          and base.player_states['is_crouch_moving'] is False):
                        any_action_seq = player.actor_interval(anims[action],
                                                               playRate=self.base.actor_play_rate)
                        Sequence(Func(self.state.set_action_state, "is_using", True),
                                 any_action_seq,
                                 Func(self.state.pick_up_item, player, "RightHand"),
                                 Func(self.state.set_action_state, "is_using", False),
                                 Func(self.state.set_do_once_key, key, False),
                                 ).start()

                elif player.get_python_tag("is_item_using"):
                    base.player_states['is_idle'] = False

                    if (base.player_states['is_using'] is False
                            and crouched_to_standing.is_playing() is False
                            and base.player_states['is_crouching'] is True):
                        base.player_states['is_standing'] = False
                        # TODO: Use blending for smooth transition between animations
                        # Do an animation sequence if player is crouched.
                        crouch_to_stand_seq = player.actor_interval(anims[self.crouched_to_standing_action],
                                                                    playRate=self.base.actor_play_rate)
                        any_action_seq = player.actor_interval(anims[action],
                                                               playRate=self.base.actor_play_rate)
                        Sequence(crouch_to_stand_seq,
                                 Func(self.state.set_action_state, "is_using", True),
                                 any_action_seq,
                                 Func(self.state.drop_item, player),
                                 Func(self.state.set_action_state, "is_using", False),
                                 Func(self.state.set_do_once_key, key, False),
                                 ).start()

                    elif (base.player_states['is_using'] is False
                          and crouched_to_standing.is_playing() is False
                          and base.player_states['is_crouching'] is False):
                        any_action_seq = player.actor_interval(anims[action],
                                                               playRate=self.base.actor_play_rate)
                        Sequence(Func(self.state.set_action_state, "is_using", True),
                                 any_action_seq,
                                 Func(self.state.drop_item, player),
                                 Func(self.state.set_action_state, "is_using", False),
                                 Func(self.state.set_do_once_key, key, False),
                                 ).start()

    def player_forwardroll_action(self, player, anims):
        if (player and isinstance(anims, dict)
                and not base.player_states['is_using']
                and not self.base.game_instance['is_aiming']):
            crouched_to_standing = player.get_anim_control(anims[self.crouched_to_standing_action])

            if (self.kbd.keymap["forward"]
                    and self.kbd.keymap["jump"]
                    and not base.do_key_once["jump"]):
                self.state.set_do_once_key("jump", True)
                if base.player_states['is_busy'] is False:
                    any_action_seq = player.actor_interval(anims["forward_roll"],
                                                           playRate=self.base.actor_play_rate)
                    Sequence(Func(self.state.set_action_state, "is_busy", True),
                             any_action_seq,
                             Func(self.state.set_action_state, "is_busy", False),
                             Func(self.state.set_do_once_key, "jump", False),
                             ).start()
            elif self.kbd.keymap["forward"] and not self.kbd.keymap["jump"]:
                if (base.player_states['is_busy'] is False
                        and crouched_to_standing.is_playing() is False
                        and base.player_states['is_crouch_moving'] is False):
                    walking_forward_seq = player.get_anim_control(anims[self.walking_forward_action])
                    if walking_forward_seq.is_playing() is False:
                        player.loop(anims[self.walking_forward_action])
                        player.set_play_rate(self.base.actor_play_rate,
                                             anims[self.walking_forward_action])
                elif (base.player_states['is_busy'] is False
                        and crouched_to_standing.is_playing()
                        and base.player_states['is_crouch_moving']):
                    crouch_move_forward_seq = player.get_anim_control(anims[self.crouch_walking_forward_action])
                    if crouch_move_forward_seq.is_playing() is False:
                        player.loop(anims[self.crouch_walking_forward_action])
                        player.set_play_rate(self.base.actor_play_rate,
                                             anims[self.crouch_walking_forward_action])

    def player_attack_action(self, player, key, anims, action):
        if (player and isinstance(anims, dict)
                and isinstance(key, str)
                and not base.player_states['is_using']
                and not base.player_states['is_moving']
                and not self.base.game_instance['is_aiming']):
            if self.kbd.keymap[key] and not base.do_key_once[key]:
                self.state.set_do_once_key(key, True)
                crouched_to_standing = player.get_anim_control(anims[self.crouched_to_standing_action])
                base.player_states['is_idle'] = False

                suffix = ''
                if base.player_states['has_sword']:
                    suffix = "sword_BGN"
                elif not base.player_states['has_sword']:
                    suffix = "**RightHand:HB"

                hitbox_np = player.find("**/{0}".format(suffix))

                self.player_in_crouched_to_stand_with_any_action(player, key, anims, action, "is_hitting")

                if (hitbox_np and base.player_states['is_hitting'] is False
                        and crouched_to_standing.is_playing() is False
                        and base.player_states['is_crouching'] is False):
                    any_action_seq = player.actor_interval(anims[action],
                                                           playRate=self.base.actor_play_rate)
                    Sequence(Func(self.state.set_action_state, "is_hitting", True),
                             Func(hitbox_np.set_collide_mask, BitMask32.bit(0)),
                             any_action_seq,
                             Func(hitbox_np.set_collide_mask, BitMask32.allOff()),
                             Func(self.state.set_action_state, "is_hitting", False),
                             Func(self.state.set_do_once_key, key, False),
                             ).start()

    def player_horse_riding_swing_action(self, player, key, anims, action):
        if (player and isinstance(anims, dict)
                and isinstance(key, str)
                and not base.player_states['is_using']
                and not base.player_states['is_moving']
                and not self.base.game_instance['is_aiming']):
            if self.kbd.keymap[key] and not base.do_key_once[key]:
                self.state.set_do_once_key(key, True)
                crouched_to_standing = player.get_anim_control(anims[self.crouched_to_standing_action])
                base.player_states['is_idle'] = False

                suffix = ''
                if base.player_states['has_sword']:
                    suffix = "sword_BGN"
                elif not base.player_states['has_sword']:
                    suffix = "LeftHand:HB"

                actor_node = player.find("**/{0}".format(suffix)).node()

                self.player_in_crouched_to_stand_with_any_action(player, key, anims, action, "is_hitting")

                if (actor_node and base.player_states['is_hitting'] is False
                        and crouched_to_standing.is_playing() is False
                        and base.player_states['is_crouching'] is False):
                    any_action_seq = player.actor_interval(anims[action],
                                                           playRate=self.base.actor_play_rate)
                    Sequence(Func(self.state.set_action_state, "is_hitting", True),
                             Func(actor_node.set_into_collide_mask, BitMask32.bit(0)),
                             any_action_seq,
                             Func(actor_node.set_into_collide_mask, BitMask32.allOff()),
                             Func(self.state.set_action_state, "is_hitting", False),
                             Func(self.state.set_do_once_key, key, False),
                             ).start()

    def player_h_kick_action(self, player, key, anims, action):
        if (player and isinstance(anims, dict)
                and isinstance(action, str)
                and isinstance(key, str)
                and not base.player_states['is_using']
                and not base.player_states['is_moving']
                and not self.base.game_instance['is_aiming']):
            if self.kbd.keymap[key] and not base.do_key_once[key]:
                self.state.set_do_once_key(key, True)
                crouched_to_standing = player.get_anim_control(anims[self.crouched_to_standing_action])
                base.player_states['is_idle'] = False
                if (base.player_states['is_h_kicking'] is False
                        and crouched_to_standing.is_playing() is False
                        and base.player_states['is_crouch_moving'] is True):
                    player_bs = self.base.get_actor_bullet_shape_node(asset="Player", type="Player")
                    # TODO: Use blending for smooth transition between animations
                    # Do an animation sequence if player is crouched.
                    crouch_to_stand_seq = player.actor_interval(anims[self.crouched_to_standing_action],
                                                                playRate=self.base.actor_play_rate)
                    any_action_seq = player.actor_interval(anims[action],
                                                           playRate=self.base.actor_play_rate)

                    Sequence(crouch_to_stand_seq,
                             Func(self.state.set_action_state, "is_h_kicking", True),
                             any_action_seq,
                             Func(self.seq_set_player_pos_wrapper, player_bs, -1.5),
                             Func(self.state.set_action_state, "is_h_kicking", False),
                             Func(self.state.set_do_once_key, key, False),
                             ).start()

                elif (base.player_states['is_h_kicking'] is False
                      and crouched_to_standing.is_playing() is False
                      and base.player_states['is_crouch_moving'] is False):
                    player_bs = self.base.get_actor_bullet_shape_node(asset="Player", type="Player")
                    any_action_seq = player.actor_interval(anims[action],
                                                           playRate=self.base.actor_play_rate)

                    Sequence(Func(self.state.set_action_state, "is_h_kicking", True),
                             any_action_seq,
                             Func(self.seq_set_player_pos_wrapper, player_bs, -1.5),
                             Func(self.state.set_action_state, "is_h_kicking", False),
                             Func(self.state.set_do_once_key, key, False),
                             ).start()

    def player_f_kick_action(self, player, key, anims, action):
        if (player and isinstance(anims, dict)
                and isinstance(action, str)
                and isinstance(key, str)
                and not base.player_states['is_using']
                and not base.player_states['is_moving']
                and not self.base.game_instance['is_aiming']):
            if self.kbd.keymap[key] and not base.do_key_once[key]:
                self.state.set_do_once_key(key, True)
                crouched_to_standing = player.get_anim_control(anims[self.crouched_to_standing_action])
                base.player_states['is_idle'] = False

                self.player_in_crouched_to_stand_with_any_action(player, key, anims, action, "is_f_kicking")

                if (base.player_states['is_f_kicking'] is False
                        and crouched_to_standing.is_playing() is False
                        and base.player_states['is_crouch_moving'] is False):
                    any_action_seq = player.actor_interval(anims[action],
                                                           playRate=self.base.actor_play_rate)
                    Sequence(Func(self.state.set_action_state, "is_f_kicking", True),
                             any_action_seq,
                             Func(self.state.set_action_state, "is_f_kicking", False),
                             Func(self.state.set_do_once_key, key, False),
                             ).start()

    def player_block_action(self, player, key, anims, action):
        if (player and isinstance(anims, dict)
                and isinstance(action, str)
                and isinstance(key, str)
                and not base.player_states['is_using']
                and not base.player_states['is_moving']
                and not self.base.game_instance['is_aiming']):
            if self.kbd.keymap[key] and not base.do_key_once[key]:
                self.state.set_do_once_key(key, True)
                crouched_to_standing = player.get_anim_control(anims[self.crouched_to_standing_action])
                base.player_states['is_idle'] = False

                self.player_in_crouched_to_stand_with_any_action(player, key, anims, action, "is_blocking")

                if (base.player_states['is_blocking'] is False
                        and crouched_to_standing.is_playing() is False
                        and base.player_states['is_crouch_moving'] is False):
                    any_action_seq = player.actor_interval(anims[action],
                                                           playRate=self.base.actor_play_rate)
                    Sequence(Func(self.state.set_action_state, "is_blocking", True),
                             any_action_seq,
                             Func(self.state.set_action_state, "is_blocking", False),
                             Func(self.state.set_do_once_key, key, False),
                             ).start()

    def player_get_sword_action(self, player, key, anims, action):
        if (player and isinstance(anims, dict)
                and isinstance(action, str)
                and isinstance(key, str)
                and not base.player_states['is_using']
                and not self.base.game_instance['is_aiming']):
            if self.kbd.keymap[key] and not base.do_key_once[key]:
                crouched_to_standing = player.get_anim_control(anims[self.crouched_to_standing_action])
                self.state.set_do_once_key(key, True)
                base.player_states['is_idle'] = False
                if (base.player_states['has_sword'] is False
                        and crouched_to_standing.is_playing() is False
                        and base.player_states['is_crouch_moving']):
                    # Do an animation sequence if player is crouched.
                    if self.base.game_instance['hud_np']:
                        self.base.game_instance['hud_np'].toggle_weapon_state(weapon_name="sword")
                    crouch_to_stand_seq = player.actor_interval(anims[self.crouched_to_standing_action],
                                                                playRate=self.base.actor_play_rate)
                    any_action_seq = player.actor_interval(anims[action],
                                                           playRate=self.base.actor_play_rate)
                    Sequence(crouch_to_stand_seq,
                             Func(self.state.get_weapon, player, "sword", "Korlan:LeftHand"),
                             Func(self.state.set_action_state, "has_sword", True),
                             Func(self.state.set_action_state, "is_using", True),
                             any_action_seq,
                             Func(self.state.set_action_state, "is_using", False),
                             Func(self.state.set_do_once_key, key, False),
                             ).start()

                elif (base.player_states['has_sword'] is False
                      and crouched_to_standing.is_playing() is False
                      and base.player_states['is_crouch_moving'] is False):
                    if self.base.game_instance['hud_np']:
                        self.base.game_instance['hud_np'].toggle_weapon_state(weapon_name="sword")
                    any_action_seq = player.actor_interval(anims[action],
                                                           playRate=self.base.actor_play_rate)
                    Sequence(Func(self.state.get_weapon, player, "sword", "Korlan:LeftHand"),
                             Func(self.state.set_action_state, "has_sword", True),
                             Func(self.state.set_action_state, "is_using", True),
                             any_action_seq,
                             Func(self.state.set_action_state, "is_using", False),
                             Func(self.state.set_do_once_key, key, False),
                             ).start()

                elif (base.player_states['has_sword']
                      and crouched_to_standing.is_playing() is False
                      and base.player_states['is_crouch_moving']):
                    if self.base.game_instance['hud_np']:
                        self.base.game_instance['hud_np'].toggle_weapon_state(weapon_name="hands")
                    # Do an animation sequence if player is crouched.
                    crouch_to_stand_seq = player.actor_interval(anims[self.crouched_to_standing_action],
                                                                playRate=self.base.actor_play_rate)
                    any_action_seq = player.actor_interval(anims[action],
                                                           playRate=-self.base.actor_play_rate)
                    Sequence(crouch_to_stand_seq,
                             Func(self.state.set_action_state, "is_using", True),
                             any_action_seq,
                             Func(self.state.set_action_state, "is_using", False),
                             Func(self.state.remove_weapon, player, "sword", "Korlan:Spine1"),
                             Func(self.state.set_action_state, "has_sword", False),
                             Func(self.state.set_do_once_key, key, False),
                             ).start()

                elif (base.player_states['has_sword']
                      and crouched_to_standing.is_playing() is False
                      and base.player_states['is_crouch_moving'] is False):
                    if self.base.game_instance['hud_np']:
                        self.base.game_instance['hud_np'].toggle_weapon_state(weapon_name="hands")
                    any_action_seq = player.actor_interval(anims[action],
                                                           playRate=-self.base.actor_play_rate)
                    Sequence(Func(self.state.set_action_state, "is_using", True),
                             any_action_seq,
                             Func(self.state.set_action_state, "is_using", False),
                             Func(self.state.remove_weapon, player, "sword", "Korlan:Spine1"),
                             Func(self.state.set_action_state, "has_sword", False),
                             Func(self.state.set_do_once_key, key, False),
                             ).start()

    def player_get_bow_action(self, player, key, anims, action):
        if (player and isinstance(anims, dict)
                and not base.player_states['is_using']
                and isinstance(action, str)
                and isinstance(key, str)):
            if self.kbd.keymap[key] and not base.do_key_once[key]:
                self.state.set_do_once_key(key, True)
                crouched_to_standing = player.get_anim_control(anims[self.crouched_to_standing_action])
                base.player_states['is_idle'] = False
                # TODO: Use blending for smooth transition between animations

                if (base.player_states['has_bow'] is False
                        and crouched_to_standing.is_playing() is False
                        and base.player_states['is_crouch_moving']):
                    if self.base.game_instance['hud_np']:
                        self.base.game_instance['hud_np'].toggle_weapon_state(weapon_name="bow")
                    # Do an animation sequence if player is crouched.
                    crouch_to_stand_seq = player.actor_interval(anims[self.crouched_to_standing_action],
                                                                playRate=self.base.actor_play_rate)
                    any_action_seq = player.actor_interval(anims[action],
                                                           playRate=self.base.actor_play_rate)
                    Sequence(crouch_to_stand_seq,
                             Func(self.state.get_weapon, player, "bow_kazakh", "Korlan:LeftHand"),
                             Func(self.archery.prepare_arrow_for_shoot, "bow_kazakh"),
                             Func(self.state.set_action_state, "has_bow", True),
                             Func(self.state.set_action_state, "is_using", True),
                             any_action_seq,
                             Func(self.state.set_action_state, "is_using", False),
                             Func(self.state.set_do_once_key, "bow", False),
                             Func(self.archery.start_archery_helper_tasks),
                             ).start()

                elif (base.player_states['has_bow'] is False
                      and crouched_to_standing.is_playing() is False
                      and base.player_states['is_crouch_moving'] is False):
                    if self.base.game_instance['hud_np']:
                        self.base.game_instance['hud_np'].toggle_weapon_state(weapon_name="bow")
                    any_action_seq = player.actor_interval(anims[action],
                                                           playRate=self.base.actor_play_rate)
                    Sequence(Func(self.state.get_weapon, player, "bow_kazakh", "Korlan:LeftHand"),
                             Func(self.archery.prepare_arrow_for_shoot, "bow_kazakh"),
                             Func(self.state.set_action_state, "has_bow", True),
                             Func(self.state.set_action_state, "is_using", True),
                             any_action_seq,
                             Func(self.state.set_action_state, "is_using", False),
                             Func(self.state.set_do_once_key, "bow", False),
                             Func(self.archery.start_archery_helper_tasks),
                             ).start()

                elif (base.player_states['has_bow']
                      and crouched_to_standing.is_playing() is False
                      and base.player_states['is_crouch_moving']):
                    if self.base.game_instance['hud_np']:
                        self.base.game_instance['hud_np'].toggle_weapon_state(weapon_name="hands")
                    # Do an animation sequence if player is crouched.
                    crouch_to_stand_seq = player.actor_interval(anims[self.crouched_to_standing_action],
                                                                playRate=self.base.actor_play_rate)
                    any_action_seq = player.actor_interval(anims[action],
                                                           playRate=self.base.actor_play_rate)
                    Sequence(crouch_to_stand_seq,
                             Func(self.state.set_action_state, "is_using", True),
                             any_action_seq,
                             Func(self.state.set_action_state, "is_using", False),
                             Func(self.state.remove_weapon, player, "bow_kazakh", "Korlan:Spine1"),
                             Func(self.archery.return_arrow_back, "Korlan:Spine1"),
                             Func(self.state.set_action_state, "has_bow", False),
                             Func(self.state.set_do_once_key, "bow", False),
                             Func(self.archery.stop_archery_helper_tasks),
                             ).start()

                elif (base.player_states['has_bow']
                      and crouched_to_standing.is_playing() is False
                      and base.player_states['is_crouch_moving'] is False):
                    if self.base.game_instance['hud_np']:
                        self.base.game_instance['hud_np'].toggle_weapon_state(weapon_name="hands")
                    any_action_seq = player.actor_interval(anims[action],
                                                           playRate=self.base.actor_play_rate)
                    Sequence(Func(self.state.set_action_state, "is_using", True),
                             any_action_seq,
                             Func(self.state.set_action_state, "is_using", False),
                             Func(self.state.remove_weapon, player, "bow_kazakh", "Korlan:Spine1"),
                             Func(self.archery.return_arrow_back, "Korlan:Spine1"),
                             Func(self.state.set_action_state, "has_bow", False),
                             Func(self.state.set_do_once_key, "bow", False),
                             Func(self.archery.stop_archery_helper_tasks),
                             ).start()

    def player_horse_riding_get_sword_action(self, player, key, anims, action):
        if (player and isinstance(anims, dict)
                and isinstance(action, str)
                and isinstance(key, str)
                and not base.player_states['is_using']
                and not self.base.game_instance['is_aiming']):
            if self.kbd.keymap[key] and not base.do_key_once[key]:
                crouched_to_standing = player.get_anim_control(anims[self.crouched_to_standing_action])
                self.state.set_do_once_key(key, True)
                base.player_states['is_idle'] = False

                if (base.player_states['has_sword'] is False
                        and crouched_to_standing.is_playing() is False
                        and base.player_states['is_crouch_moving'] is False):
                    if self.base.game_instance['hud_np']:
                        self.base.game_instance['hud_np'].toggle_weapon_state(weapon_name="sword")
                    any_action_seq = player.actor_interval(anims[action],
                                                           playRate=self.base.actor_play_rate)
                    Sequence(Func(self.state.get_weapon, player, "sword", "Korlan:LeftHand"),
                             Func(self.state.set_horse_riding_weapon_state, "has_sword", True),
                             Func(self.state.set_action_state, "is_using", True),
                             any_action_seq,
                             Func(self.state.set_action_state, "is_using", False),
                             Func(self.state.set_do_once_key, key, False),
                             ).start()

                elif (base.player_states['has_sword']
                      and crouched_to_standing.is_playing() is False
                      and base.player_states['is_crouch_moving'] is False):
                    if self.base.game_instance['hud_np']:
                        self.base.game_instance['hud_np'].toggle_weapon_state(weapon_name="hands")
                    any_action_seq = player.actor_interval(anims[action],
                                                           playRate=-self.base.actor_play_rate)
                    Sequence(
                        Func(self.state.set_action_state, "is_using", True),
                        any_action_seq,
                        Func(self.state.set_action_state, "is_using", False),
                        Func(self.state.remove_weapon, player, "sword", "Korlan:Spine1"),
                        Func(self.state.set_horse_riding_weapon_state, "has_sword", False),
                        Func(self.state.set_do_once_key, key, False),
                    ).start()

    def player_horse_riding_get_bow_action(self, player, key, anims, action):
        if (player and isinstance(anims, dict)
                and not base.player_states['is_using']
                and isinstance(action, str)
                and isinstance(key, str)):
            if self.kbd.keymap[key] and not base.do_key_once[key]:
                self.state.set_do_once_key(key, True)
                crouched_to_standing = player.get_anim_control(anims[self.crouched_to_standing_action])
                base.player_states['is_idle'] = False
                # TODO: Use blending for smooth transition between animations

                if (base.player_states['has_bow'] is False
                        and crouched_to_standing.is_playing() is False
                        and base.player_states['is_crouch_moving'] is False):
                    if self.base.game_instance['hud_np']:
                        self.base.game_instance['hud_np'].toggle_weapon_state(weapon_name="bow")
                    any_action_seq = player.actor_interval(anims[action],
                                                           playRate=self.base.actor_play_rate)
                    Sequence(Func(self.state.get_weapon, player, "bow_kazakh", "Korlan:LeftHand"),
                             Func(self.archery.prepare_arrow_for_shoot, "bow_kazakh"),
                             Func(self.state.set_horse_riding_weapon_state, "has_bow", True),
                             Func(self.state.set_action_state, "is_using", True),
                             any_action_seq,
                             Func(self.state.set_action_state, "is_using", False),
                             Func(self.state.set_do_once_key, "bow", False),
                             Func(self.archery.start_archery_helper_tasks),
                             ).start()

                elif (base.player_states['has_bow']
                      and crouched_to_standing.is_playing() is False
                      and base.player_states['is_crouch_moving'] is False):
                    if self.base.game_instance['hud_np']:
                        self.base.game_instance['hud_np'].toggle_weapon_state(weapon_name="hands")
                    any_action_seq = player.actor_interval(anims[action],
                                                           playRate=self.base.actor_play_rate)
                    Sequence(Func(self.state.set_action_state, "is_using", True),
                             any_action_seq,
                             Func(self.state.set_action_state, "is_using", False),
                             Func(self.state.remove_weapon, player, "bow_kazakh", "Korlan:Spine1"),
                             Func(self.archery.return_arrow_back, "Korlan:Spine1"),
                             Func(self.state.set_horse_riding_weapon_state, "has_bow", False),
                             Func(self.state.set_do_once_key, "bow", False),
                             Func(self.archery.stop_archery_helper_tasks),
                             ).start()

    def player_tengri_action(self, player, key, anims, action):
        if (player and isinstance(anims, dict)
                and isinstance(action, str)
                and isinstance(key, str)
                and not base.player_states['is_using']
                and not base.player_states['is_moving']):
            if self.kbd.keymap[key] and not base.do_key_once[key]:
                self.state.set_do_once_key(key, True)
                crouched_to_standing = player.get_anim_control(anims[self.crouched_to_standing_action])
                base.player_states['is_idle'] = False

                self.player_in_crouched_to_stand_with_magic_weapon_action(player, key, anims, action, "has_tengri")

                if (base.player_states['has_tengri'] is False
                        and crouched_to_standing.is_playing() is False
                        and base.player_states['is_crouch_moving'] is False):
                    any_action_seq = player.actor_interval(anims[action],
                                                           playRate=self.base.actor_play_rate)
                    Sequence(Func(self.state.set_action_state, "has_tengri", True),
                             any_action_seq,
                             Func(self.state.set_action_state, "has_tengri", False),
                             Func(self.state.set_do_once_key, key, False),
                             ).start()

    def player_umai_action(self, player, key, anims, action):
        if (player and isinstance(anims, dict)
                and isinstance(action, str)
                and isinstance(key, str)
                and not base.player_states['is_using']
                and not base.player_states['is_moving']):
            if self.kbd.keymap[key] and not base.do_key_once[key]:
                self.state.set_do_once_key(key, True)
                crouched_to_standing = player.get_anim_control(anims[self.crouched_to_standing_action])
                base.player_states['is_idle'] = False

                self.player_in_crouched_to_stand_with_magic_weapon_action(player, key, anims, action, "has_umai")

                if (base.player_states['has_umai'] is False
                        and crouched_to_standing.is_playing() is False
                        and base.player_states['is_crouch_moving'] is False):
                    any_action_seq = player.actor_interval(anims[action],
                                                           playRate=self.base.actor_play_rate)
                    Sequence(Func(self.state.set_action_state, "has_umai", True),
                             any_action_seq,
                             Func(self.state.set_action_state, "has_umai", False),
                             Func(self.state.set_do_once_key, key, False),
                             ).start()

    def player_bow_shoot_action(self, player, anims, action):
        if (player and isinstance(anims, dict)
                and isinstance(action, str)
                and not base.player_states['is_using']
                and base.player_states['has_bow']):
            if (self.kbd.keymap["block"]
                    and not self.kbd.keymap["attack"]
                    and not base.do_key_once["block"]
                    and len(self.archery.arrows) > 0):
                self.state.set_do_once_key("block", True)
                crouched_to_standing = player.get_anim_control(anims[self.crouched_to_standing_action])

                if self.archery.arrow_ref:
                    if self.archery.arrow_ref.get_python_tag("power") > 0:
                        self.archery.arrow_ref.set_python_tag("power", 0)

                if (crouched_to_standing.is_playing() is False
                        and base.player_states['is_crouching'] is True):
                    # TODO: Use blending for smooth transition between animations
                    # Do an animation sequence if player is crouched.
                    crouch_to_stand_seq = player.actor_interval(anims[self.crouched_to_standing_action],
                                                                playRate=self.base.actor_play_rate)
                    any_action_seq = player.actor_interval(anims[action],
                                                           playRate=self.base.actor_play_rate)

                    Sequence(crouch_to_stand_seq,
                             Func(self.archery.prepare_arrow_for_shoot, "bow_kazakh"),
                             any_action_seq,
                             Func(self.state.set_action_state, "is_busy", True)
                             ).start()

                elif (crouched_to_standing.is_playing() is False
                      and base.player_states['is_crouching'] is False):
                    any_action_seq = player.actor_interval(anims[action],
                                                           playRate=self.base.actor_play_rate)
                    Sequence(Func(self.archery.prepare_arrow_for_shoot, "bow_kazakh"),
                             any_action_seq,
                             Func(self.state.set_action_state, "is_busy", True)
                             ).start()

            if (self.kbd.keymap["block"]
                    and self.kbd.keymap["attack"]
                    and base.do_key_once["block"]
                    and len(self.archery.arrows) > 0
                    and self.archery.arrow_ref.get_python_tag("ready") == 0):

                if self.archery.arrow_ref and self.archery.arrow_is_prepared:
                    if self.archery.target_test_ui:
                        self.archery.target_test_ui.show()
                    power = self.archery.arrow_ref.get_python_tag("power")
                    if power < self.archery.arrow_charge_units:
                        if self.base.game_instance['hud_np'].charge_arrow_bar_ui:
                            self.base.game_instance['hud_np'].charge_arrow_bar_ui['value'] = power
                        power += 10
                        self.archery.arrow_ref.set_python_tag("power", power)

                    self.base.game_instance['free_camera'] = True

                    Sequence(Wait(0.1),
                             Func(player.pose, action, -0.98),
                             Wait(0.1),
                             Func(player.pose, action, -0.99),
                             Wait(0.1),
                             Func(player.pose, action, -1),
                             ).start()

            if (not self.kbd.keymap["attack"]
                    and self.kbd.keymap["block"]
                    and self.archery.arrow_ref.get_python_tag("ready") == 0
                    and self.archery.arrow_ref.get_python_tag("shot") == 0
                    and self.archery.arrow_ref.get_python_tag("power") > 0):

                if (self.archery.arrow_ref
                        and self.archery.arrow_is_prepared
                        and len(self.archery.arrows) > 0):
                    self.archery.arrow_ref.set_python_tag("ready", 1)
                    self.archery.bow_shoot()
                    if self.base.game_instance['hud_np'].charge_arrow_bar_ui:
                        self.base.game_instance['hud_np'].charge_arrow_bar_ui['value'] = 0
                    self.base.game_instance['free_camera'] = False

            if (not self.kbd.keymap["attack"]
                    and not self.kbd.keymap["block"]
                    and base.do_key_once["block"]):
                if self.archery.target_test_ui:
                    self.archery.target_test_ui.hide()
                self.state.set_do_once_key('block', False),
                self.state.set_action_state("is_busy", False)
                if self.base.game_instance['hud_np'].charge_arrow_bar_ui:
                    self.base.game_instance['hud_np'].charge_arrow_bar_ui['value'] = 0

                if self.archery.arrow_ref:
                    if self.archery.arrow_ref.get_python_tag("power") > 0:
                        self.archery.arrow_ref.set_python_tag("power", 0)
                    self.archery.arrow_ref.set_python_tag("ready", 0)

                self.base.game_instance['free_camera'] = False

            if (not self.kbd.keymap["attack"]
                    and not self.kbd.keymap["block"]
                    and not base.do_key_once["block"]):
                if self.archery.target_test_ui:
                    self.archery.target_test_ui.hide()
                if self.base.game_instance['hud_np'].charge_arrow_bar_ui:
                    self.base.game_instance['hud_np'].charge_arrow_bar_ui['value'] = 0
                self.state.set_action_state("is_busy", False)

                if self.archery.arrow_ref:
                    if self.archery.arrow_ref.get_python_tag("power") > 0:
                        self.archery.arrow_ref.set_python_tag("power", 0)
                    self.archery.arrow_ref.set_python_tag("ready", 0)

                self.base.game_instance['free_camera'] = False

    def player_horse_riding_bow_shoot_action(self, player, anims, action):
        if (player and isinstance(anims, dict)
                and isinstance(action, str)
                and not base.player_states['is_using']
                and base.player_states['has_bow']):
            if (self.kbd.keymap["block"]
                    and not self.kbd.keymap["attack"]
                    and not base.do_key_once["block"]
                    and len(self.archery.arrows) > 0):
                self.state.set_do_once_key("block", True)
                crouched_to_standing = player.get_anim_control(anims[self.crouched_to_standing_action])

                if self.archery.arrow_ref:
                    if self.archery.arrow_ref.get_python_tag("power") > 0:
                        self.archery.arrow_ref.set_python_tag("power", 0)

                if (crouched_to_standing.is_playing() is False
                        and base.player_states['is_crouching'] is False):
                    any_action_seq = player.actor_interval(anims[action],
                                                           playRate=self.base.actor_play_rate)
                    Sequence(Func(self.archery.prepare_arrow_for_shoot, "bow_kazakh"),
                             any_action_seq,
                             Func(self.state.set_action_state, "is_busy", True)
                             ).start()

            if (self.kbd.keymap["block"]
                    and self.kbd.keymap["attack"]
                    and base.do_key_once["block"]
                    and len(self.archery.arrows) > 0
                    and self.archery.arrow_ref.get_python_tag("ready") == 0):

                if self.archery.arrow_ref and self.archery.arrow_is_prepared:
                    if self.archery.target_test_ui:
                        self.archery.target_test_ui.show()
                    power = self.archery.arrow_ref.get_python_tag("power")
                    if self.base.game_instance['hud_np'].charge_arrow_bar_ui:
                        self.base.game_instance['hud_np'].charge_arrow_bar_ui['value'] = power
                    power += 10
                    self.archery.arrow_ref.set_python_tag("power", power)

                    Sequence(Wait(0.1),
                             Func(player.pose, action, -0.98),
                             Wait(0.1),
                             Func(player.pose, action, -0.99),
                             Wait(0.1),
                             Func(player.pose, action, -1),
                             ).start()

            if (not self.kbd.keymap["attack"]
                    and self.kbd.keymap["block"]
                    and self.archery.arrow_ref.get_python_tag("ready") == 0
                    and self.archery.arrow_ref.get_python_tag("shot") == 0
                    and self.archery.arrow_ref.get_python_tag("power") > 0):

                if (self.archery.arrow_ref
                        and self.archery.arrow_is_prepared
                        and len(self.archery.arrows) > 0):
                    self.archery.arrow_ref.set_python_tag("ready", 1)
                    self.archery.bow_shoot()
                    if self.base.game_instance['hud_np'].charge_arrow_bar_ui:
                        self.base.game_instance['hud_np'].charge_arrow_bar_ui['value'] = 0

            if (not self.kbd.keymap["attack"]
                    and not self.kbd.keymap["block"]
                    and base.do_key_once["block"]):
                if self.archery.target_test_ui:
                    self.archery.target_test_ui.hide()
                self.state.set_do_once_key('block', False),
                self.state.set_action_state("is_busy", False)
                self.state.set_action_state("horse_riding", True)
                if self.base.game_instance['hud_np'].charge_arrow_bar_ui:
                    self.base.game_instance['hud_np'].charge_arrow_bar_ui['value'] = 0

                if self.archery.arrow_ref:
                    if self.archery.arrow_ref.get_python_tag("power") > 0:
                        self.archery.arrow_ref.set_python_tag("power", 0)
                    self.archery.arrow_ref.set_python_tag("ready", 0)

            if (not self.kbd.keymap["attack"]
                    and not self.kbd.keymap["block"]
                    and not base.do_key_once["block"]):
                if self.archery.target_test_ui:
                    self.archery.target_test_ui.hide()
                if self.base.game_instance['hud_np'].charge_arrow_bar_ui:
                    self.base.game_instance['hud_np'].charge_arrow_bar_ui['value'] = 0
                self.state.set_action_state("is_busy", False)
                self.state.set_action_state("horse_riding", True)

                if self.archery.arrow_ref:
                    if self.archery.arrow_ref.get_python_tag("power") > 0:
                        self.archery.arrow_ref.set_python_tag("power", 0)
                    self.archery.arrow_ref.set_python_tag("ready", 0)

    def player_mount_helper_task(self, child, player, saddle_pos, task):
        if child and player:
            if self.base.game_instance['player_ref'].get_python_tag("is_on_horse"):
                child.set_x(saddle_pos[0])
                child.set_y(saddle_pos[1])

                if not self.base.game_instance['is_aiming']:
                    self.base.camera.set_y(-5.5)

                self.base.camera.set_z(0.5)
            else:
                self.base.camera.set_y(self.base.game_instance["mouse_y_cam"])
                self.base.camera.set_z(0)
        return task.cont

    def mount_action(self, anims):
        if self.kbd.keymap["use"] and not base.do_key_once["use"]:
            self.state.set_do_once_key("use", True)
            horse_name = base.game_instance['player_using_horse']
            parent = render.find("**/{0}".format(horse_name))
            child = self.base.get_actor_bullet_shape_node(asset="Player", type="Player")
            player = self.base.game_instance['player_ref']
            if parent and child and anims and not self.base.game_instance['is_aiming']:
                if (self.base.game_instance['player_ref'].get_python_tag("is_on_horse")
                        and parent.get_python_tag("is_mounted")):
                    self.unmount_action(anims)
                else:
                    # with inverted Z -0.5 stands for Up
                    # Our horse (un)mounting animations have been made with imperfect positions,
                    # so, I had to change child positions to get more satisfactory result
                    # with these animations in my game.
                    mounting_pos = Vec3(0.5, -0.15, -0.45)
                    saddle_pos = Vec3(0, -0.32, 0.16)
                    mount_action_seq = player.actor_interval(anims["horse_mounting"],
                                                             playRate=self.base.actor_play_rate)
                    horse_riding_action_seq = player.actor_interval(anims["horse_riding_idle"],
                                                                    playRate=self.base.actor_play_rate)
                    horse_np = self.base.game_instance['actors_np']["{0}:BS".format(horse_name)]

                    taskMgr.add(self.player_mount_helper_task,
                                "player_mount_helper_task",
                                extraArgs=[child, player, saddle_pos],
                                appendTask=True)

                    Sequence(Func(horse_np.set_collide_mask, BitMask32.bit(0)),
                             Func(child.set_collide_mask, BitMask32.allOff()),
                             Func(self.state.set_action_state, "is_using", True),
                             Parallel(mount_action_seq,
                                      Func(child.reparent_to, parent),
                                      Func(child.set_x, mounting_pos[0]),
                                      Func(child.set_y, mounting_pos[1]),
                                      Func(player.set_z, mounting_pos[2]),
                                      Func(child.set_h, 0)),
                             Func(child.set_x, saddle_pos[0]),
                             Func(child.set_y, saddle_pos[1]),
                             # bullet shape has impact of gravity
                             # so make player geom stay higher instead
                             Func(player.set_z, saddle_pos[2]),
                             Func(child.set_collide_mask, BitMask32.bit(0)),
                             Func(self.base.game_instance['player_ref'].set_python_tag, "is_on_horse", True),
                             Func(self.state.set_action_state, "is_using", False),
                             Func(self.state.set_action_state, "horse_riding", True),
                             Func(self.state.set_action_state, "is_mounted", True),
                             Func(parent.set_python_tag, "is_mounted", True),
                             Func(self.state.set_do_once_key, "use", False),
                             horse_riding_action_seq
                             ).start()

    def unmount_action(self, anims):
        horse_name = base.game_instance['player_using_horse']
        parent = render.find("**/{0}".format(horse_name))
        parent_bs = render.find("**/{0}:BS".format(horse_name))
        child = self.base.get_actor_bullet_shape_node(asset="Player", type="Player")
        player = self.base.game_instance['player_ref']
        if parent and child and anims and not self.base.game_instance['is_aiming']:
            # with inverted Z -0.7 stands for Up
            # Our horse (un)mounting animations have been made with imperfect positions,
            # so, I had to change child positions to get more satisfactory result
            # with these animations in my game.
            unmounting_pos = Vec3(0.5, -0.15, -0.45)
            # Reparent parent/child node back to its BulletCharacterControllerNode
            unmount_action_seq = player.actor_interval(anims["horse_unmounting"],
                                                       playRate=self.base.actor_play_rate)
            horse_near_pos = Vec3(parent_bs.get_x(), parent_bs.get_y(), child.get_z()) + Vec3(1, 0, 0)
            base.game_instance['player_using_horse'] = ''
            horse_np = self.base.game_instance['actors_np']["{0}:BS".format(horse_name)]

            Sequence(Func(self.base.game_instance['player_ref'].set_python_tag, "is_on_horse", False),
                     Func(self.state.set_action_state, "is_using", True),
                     Func(child.set_collide_mask, BitMask32.allOff()),
                     Parallel(unmount_action_seq,
                              Func(child.set_x, unmounting_pos[0]),
                              Func(child.set_y, unmounting_pos[1]),
                              Func(player.set_z, unmounting_pos[2])),
                     # revert player geom height
                     Func(child.reparent_to, render),
                     Func(child.set_x, horse_near_pos[0]),
                     Func(child.set_y, horse_near_pos[1]),
                     Func(player.set_z, -1),
                     Func(self.state.set_action_state, "is_using", False),
                     Func(self.state.set_action_state, "horse_riding", False),
                     Func(self.state.set_action_state, "is_mounted", False),
                     Func(parent.set_python_tag, "is_mounted", False),
                     Func(taskMgr.remove, "player_mount_helper_task"),
                     Func(horse_np.set_collide_mask, BitMask32.allOn()),
                     Func(child.set_collide_mask, BitMask32.bit(0)),
                     Func(self.state.set_do_once_key, "use", False)
                     ).start()
