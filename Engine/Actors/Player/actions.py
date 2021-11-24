from panda3d.core import Vec3

from Engine.Actors.Player.state import PlayerState
from Engine.FSM.player_fsm import PlayerFSM
from direct.interval.IntervalGlobal import *
from direct.task.TaskManagerGlobal import taskMgr

from Settings.Input.keyboard import Keyboard
from Settings.Input.mouse import Mouse
from Engine.Actors.Player.sequences import Sequences
from Settings.UI.player_menu_ui import PlayerMenuUI


class Actions:

    def __init__(self):
        self.game_settings = base.game_settings
        self.base = base
        self.actor_play_rate = None
        self.walking_forward_action = "Walking"
        self.render = render
        self.korlan = None
        self.player = None
        self.player_bs = None
        self.floater = None
        self.taskMgr = taskMgr
        self.seq_wrappers = Sequences()
        self.kbd = Keyboard()
        self.mouse = Mouse()
        self.fsm_player = PlayerFSM()
        self.player_menu = PlayerMenuUI()
        self.state = PlayerState()
        self.base.is_ui_active = False
        self.base.is_dev_ui_active = False
        self.base.is_cutscene_active = False
        self.is_aiming = False

    """ Prepares actions for scene"""

    def player_actions_init(self, player, anims):
        if (player
                and anims
                and isinstance(anims, dict)):
            self.base.player_actions_init_is_activated = 0
            if self.game_settings['Debug']['set_editor_mode'] == 'NO':
                self.player = player
                self.kbd.keymap_init()
                self.kbd.keymap_init_released()
                base.input_state = self.kbd.bullet_keymap_init()

                # Define mouse
                taskMgr.add(self.wait_for_physics_ready_player_task,
                            "wait_for_physics_ready_player_task")
                taskMgr.add(self.mouse.mouse_control_task,
                            "mouse_control_task",
                            extraArgs=[player, self.is_aiming],
                            appendTask=True)

                # Define weapon state
                self.seq_wrappers.hud.set_weapon_ui()
                self.seq_wrappers.hud.set_player_bar()

                # Define player menu here
                base.accept('i', self.player_menu.set_ui_inventory)

                # Define accepting player events here
                base.accept("player_movement", self.seq_wrappers.seq_movement, extraArgs=[player, anims])
                base.accept("player_run", self.seq_wrappers.seq_run, extraArgs=[player, anims])
                base.accept("player_crouch", self.seq_wrappers.seq_crouch, extraArgs=[player, anims])
                base.accept("player_jump", self.seq_wrappers.seq_jump, extraArgs=[player, anims, "Jumping"])
                base.accept("player_use", self.seq_wrappers.seq_use, extraArgs=[player, anims, "PickingUp"])
                # base.accept("player_hit", self.seq_wrappers.seq_hit, extraArgs=[player, anims])
                base.accept("player_h_kick", self.seq_wrappers.seq_h_kick, extraArgs=[player, anims, "Kicking_3"])
                base.accept("player_f_kick", self.seq_wrappers.seq_f_kick, extraArgs=[player, anims, "Kicking_5"])
                base.accept("player_block", self.seq_wrappers.seq_block, extraArgs=[player, anims, "center_blocking"])
                base.accept("player_sword", self.seq_wrappers.seq_sword, extraArgs=[player, anims,
                                                                                    "sword_disarm_over_shoulder"])
                base.accept("player_bow", self.seq_wrappers.seq_bow, extraArgs=[player, anims,
                                                                                "archer_standing_disarm_bow"])
                # base.accept("player_tengri", self.seq_wrappers.seq_tengri, extraArgs=[player, anims, ""])
                # base.accept("player_umai", self.seq_wrappers.seq_umai, extraArgs=[player, anims, ""])

                # Define player attack here
                self.state.set_player_equipment(player, "Korlan:Spine1")
                if not base.player_states['has_sword'] and not base.player_states['has_bow']:
                    base.accept("mouse1", self.player_hit_action, extraArgs=[player, "attack", anims,
                                                                             "Boxing"])
                elif base.player_states['has_sword'] and not base.player_states['has_bow']:
                    base.accept("mouse1", self.player_hit_action, extraArgs=[player, "attack", anims,
                                                                             "draw_great_sword_1"])
                elif not base.player_states['has_sword'] and base.player_states['has_bow']:
                    base.accept("mouse3", self.player_hit_action, extraArgs=[player, "attack", anims,
                                                                             "archer_standing_draw_arrow"])

                # Pass the player object to FSM
                self.fsm_player.get_player(actor=player)
                player.set_blend(frameBlend=True)

                taskMgr.add(self.player_actions_task, "player_actions_task",
                            extraArgs=[player, anims],
                            appendTask=True)

                taskMgr.add(self.seq_wrappers.items.get_item_distance_task,
                            "get_item_distance_task",
                            extraArgs=[player],
                            appendTask=True)

                excluded_assets = ['Sky', 'Mountains', 'Grass', 'Ground', 'NPC']
                assets_dist_vec = base.distance_calculate(
                    base.assets_pos_collector_no_player(player, excluded_assets), player)

                taskMgr.add(self.state.player_view_mode_task,
                            "player_view_mode_task",
                            extraArgs=[assets_dist_vec],
                            appendTask=True)

            self.base.player_actions_init_is_activated = 1

    """ Prepares the player for scene """
    def wait_for_physics_ready_player_task(self, task):
        if self.player and not self.player.is_empty():
            self.floater = self.mouse.set_floater(self.player)
            return task.done
        return task.cont

    def player_actions_task(self, player, anims, task):
        # TODO: change animation
        if player and anims:
            any_action = player.get_anim_control(anims['Standing_idle_female'])

            if (any_action.is_playing() is False
                    and base.player_states['is_idle']
                    and base.player_states['is_attacked'] is False
                    and base.player_states['is_busy'] is False
                    and base.player_states['is_moving'] is False
                    and base.player_states['is_running'] is False
                    and base.player_states['is_crouch_moving'] is False
                    and base.player_states['is_crouching'] is False):
                self.fsm_player.request("Idle", player,
                                        anims['Standing_idle_female'],
                                        "play")

            # Here we accept keys
            # TODO: change animation and implement state for actions
            #  except movement, crouch and jump action
            if (not self.base.is_ui_active
                    and not self.base.is_dev_ui_active
                    or self.base.is_dev_ui_active):
                if base.player_state_unarmed:
                    if self.floater:
                        self.player_movement_action(player, anims)
                        self.player_run_action(player, anims)

            if (not self.base.is_ui_active
                    and not self.base.is_dev_ui_active):
                if base.player_state_unarmed:
                    self.seq_wrappers.hud.toggle_weapon_state(weapon_name="hands")
                    self.player_crouch_action(player, 'crouch', anims)
                    self.player_jump_action(player, "jump", anims, "Jumping")
                    self.player_use_action(player, "use", anims, "PickingUp")
                    self.player_h_kick_action(player, "h_attack", anims, "Kicking_3")
                    self.player_f_kick_action(player, "f_attack", anims, "Kicking_5")
                    self.player_block_action(player, "block", anims, "center_blocking")
                    self.player_sword_action(player, "sword", anims, "sword_disarm_over_shoulder")
                    self.player_bow_action(player, "bow", anims, "archer_standing_disarm_bow")
                if base.player_state_armed:
                    if self.floater:
                        self.player_movement_action(player, anims)
                        self.player_run_action(player, anims)
                    self.player_crouch_action(player, 'crouch', anims)
                    self.player_jump_action(player, "jump", anims, "Jumping")
                    self.player_use_action(player, "use", anims, "PickingUp")
                    self.player_h_kick_action(player, "h_attack", anims, "Kicking_3")
                    self.player_f_kick_action(player, "f_attack", anims, "Kicking_5")
                    self.player_block_action(player, "block", anims, "center_blocking")
                    self.player_sword_action(player, "sword", anims, "sword_disarm_over_shoulder")
                    self.player_bow_action(player, "bow", anims, "archer_standing_disarm_bow")
                if base.player_state_magic:
                    if self.floater:
                        self.player_movement_action(player, anims)
                        self.player_run_action(player, anims)
                    self.player_crouch_action(player, 'crouch', anims)
                    self.player_jump_action(player, "jump", anims, "Jumping")
                    self.player_use_action(player, "use", anims, "PickingUp")
                    self.player_h_kick_action(player, "h_attack", anims, "Kicking_3")
                    self.player_f_kick_action(player, "f_attack", anims, "Kicking_5")
                    self.player_block_action(player, "block", anims, "center_blocking")
                    self.player_tengri_action(player, "tengri", anims, "PickingUp")
                    self.player_umai_action(player, "umai", anims, "PickingUp")

        # If player has the bullet shape
        if not self.player_bs:
            if "Player:BS" in player.get_parent().get_name():
                self.player_bs = player.get_parent()

        if self.base.game_mode is False and self.base.menu_mode:
            return task.done

        return task.cont

    def player_movement_action(self, player, anims):
        if player and isinstance(anims, dict):
            # If a move-key is pressed, move the player in the specified direction.
            speed = Vec3(0, 0, 0)
            omega = 0.0
            move_unit = 2

            # Get the time that elapsed since last frame
            dt = globalClock.getDt()

            base.gameplay_mode = self.game_settings['Main']['gameplay_mode']
            self.player_bs = self.base.get_actor_bullet_shape_node(asset=player.get_name(), type="Player")

            if hasattr(base, "gameplay_mode"):
                if base.gameplay_mode == 'enhanced':
                    if self.kbd.keymap["left"] and self.player_bs:
                        self.player_bs.set_h(self.player_bs.get_h() + 100 * dt)
                    if self.kbd.keymap["right"] and self.player_bs:
                        self.player_bs.set_h(self.player_bs.get_h() - 100 * dt)

            if hasattr(base, "gameplay_mode"):
                if base.gameplay_mode == 'simple' and self.mouse.pivot:
                    self.mouse.pivot.set_h(self.base.camera.get_h())

                if hasattr(base, "first_person_mode") and base.first_person_mode and self.mouse.pivot:
                    self.mouse.pivot.set_h(self.base.camera.get_h())

            if (self.kbd.keymap["forward"]
                    and self.kbd.keymap["run"] is False
                    and base.player_states['is_moving']
                    and base.player_states['is_running'] is False
                    and base.player_states['is_attacked'] is False
                    and base.player_states['is_busy'] is False
                    and base.player_states['is_crouch_moving'] is False
                    and base.player_states['is_idle']):
                if base.input_state.is_set('forward'):
                    speed.setY(-move_unit)
            if (self.kbd.keymap["forward"]
                    and self.kbd.keymap["run"] is False
                    and base.player_states['is_moving'] is False
                    and base.player_states['is_attacked'] is False
                    and base.player_states['is_busy'] is False
                    and base.player_states['is_running'] is False
                    and base.player_states['is_crouch_moving']
                    and base.player_states['is_idle'] is False):
                if base.input_state.is_set('forward'):
                    speed.setY(-move_unit)
            if (self.kbd.keymap["backward"]
                    and self.kbd.keymap["run"] is False
                    and base.player_states['is_moving']
                    and base.player_states['is_attacked'] is False
                    and base.player_states['is_busy'] is False
                    and base.player_states['is_crouch_moving'] is False
                    and base.player_states['is_idle']):
                if base.input_state.is_set('reverse'):
                    speed.setY(move_unit)
            if (self.kbd.keymap["backward"]
                    and self.kbd.keymap["run"] is False
                    and base.player_states['is_moving'] is False
                    and base.player_states['is_attacked'] is False
                    and base.player_states['is_busy'] is False
                    and base.player_states['is_crouch_moving']
                    and base.player_states['is_idle'] is False):
                if base.input_state.is_set('reverse'):
                    speed.setY(move_unit)

            if (hasattr(base, "bullet_char_contr_node")
                    and base.bullet_char_contr_node):
                base.bullet_char_contr_node.set_linear_movement(speed, True)
                base.bullet_char_contr_node.set_angular_movement(omega)

            # If the player does action, loop the animation through messenger.
            if (self.kbd.keymap["forward"]
                    and self.kbd.keymap["run"] is False
                    or self.kbd.keymap["backward"]
                    or self.kbd.keymap["left"]
                    or self.kbd.keymap["right"]):
                if (base.player_states['is_moving'] is False
                        and base.player_states['is_attacked'] is False
                        and base.player_states['is_busy'] is False
                        and base.player_states['is_crouch_moving'] is False
                        and base.player_states["is_running"] is False
                        and base.player_states['is_idle']):
                    base.messenger.send("player_movement")
                if (base.player_states['is_moving'] is False
                        and base.player_states['is_attacked'] is False
                        and base.player_states['is_busy'] is False
                        and base.player_states["is_running"] is False
                        and base.player_states['is_crouch_moving']
                        and base.player_states['is_idle'] is False):
                    base.messenger.send("player_movement")
            else:
                if (base.player_states['is_moving']
                        and base.player_states['is_attacked'] is False
                        and base.player_states['is_busy'] is False
                        and base.player_states["is_running"] is False
                        and base.player_states['is_crouch_moving'] is False):
                    base.messenger.send("player_movement")
                if (base.player_states['is_moving'] is False
                        and base.player_states['is_attacked'] is False
                        and base.player_states['is_busy'] is False
                        and base.player_states["is_running"] is False
                        and base.player_states['is_crouch_moving']):
                    base.messenger.send("player_movement")

            # Actor backward movement
            if (self.kbd.keymap["backward"]
                    and base.player_states['is_attacked'] is False
                    and base.player_states['is_busy'] is False
                    and self.kbd.keymap["run"] is False
                    and base.player_states["is_running"] is False):
                player.set_play_rate(-1.0,
                                     anims[self.walking_forward_action])

    def player_run_action(self, player, anims):
        if player and isinstance(anims, dict):
            # If a move-key is pressed, move the player in the specified direction.
            speed = Vec3(0, 0, 0)
            move_unit = 7
            # TODO check if base.state elements are False
            #  except forward and run
            if (self.kbd.keymap["forward"]
                    and self.kbd.keymap["run"]):
                for key in base.player_states:
                    if (not base.player_states[key]
                            and base.player_states['is_idle']):
                        if base.input_state.is_set('forward'):
                            speed.setY(-move_unit)
                        if (hasattr(base, "bullet_char_contr_node")
                                and base.bullet_char_contr_node):
                            base.bullet_char_contr_node.set_linear_movement(speed, True)

            # If the player does action, loop the animation.
            # If it is standing still, stop the animation.
            if (self.kbd.keymap["forward"]
                    and self.kbd.keymap["run"]
                    or self.kbd.keymap["left"]
                    or self.kbd.keymap["right"]):
                if (base.player_states['is_moving'] is False
                        and base.player_states['is_attacked'] is False
                        and base.player_states['is_busy'] is False
                        and base.player_states['is_crouch_moving'] is False
                        and base.player_states["is_running"] is False
                        and base.player_states['is_idle']):
                    base.messenger.send("player_run")
                if (base.player_states['is_moving'] is False
                        and base.player_states['is_attacked'] is False
                        and base.player_states['is_busy'] is False
                        and base.player_states["is_crouch_moving"] is False
                        and base.player_states['is_running']
                        and base.player_states['is_idle'] is False):
                    base.messenger.send("player_run")

            else:
                if (base.player_states['is_running']
                        and base.player_states['is_attacked'] is False
                        and base.player_states['is_busy'] is False
                        and base.player_states["is_moving"] is False
                        and base.player_states['is_crouch_moving'] is False):
                    base.messenger.send("player_run")
                if (base.player_states['is_moving'] is False
                        and base.player_states['is_attacked'] is False
                        and base.player_states['is_busy'] is False
                        and base.player_states["is_crouch_moving"] is False
                        and base.player_states['is_running']):
                    base.messenger.send("player_run")

    def player_crouch_action(self, player, key, anims):
        if (player and isinstance(anims, dict)
                and isinstance(key, str)):
            # If the player does action, play the animation through event.
            if self.kbd.keymap[key]:
                base.player_states['is_idle'] = False
                base.messenger.send("player_crouch")

    def player_jump_action(self, player, key, anims, action):
        if (player and isinstance(anims, dict)
                and isinstance(action, str)
                and isinstance(key, str)):
            if self.kbd.keymap[key]:
                base.player_states['is_idle'] = False
                base.messenger.send("player_jump")

    def player_use_action(self, player, key, anims, action):
        if (player and isinstance(anims, dict)
                and isinstance(action, str)
                and isinstance(key, str)):
            if self.kbd.keymap[key]:
                base.messenger.send("player_use")

    def player_hit_action(self, player, key, anims, action):
        if (player and isinstance(anims, dict)
                and isinstance(action, str)
                and isinstance(key, str)):
            base.player_states['is_idle'] = False
            base.messenger.send("player_hit")

    def player_h_kick_action(self, player, key, anims, action):
        if (player and isinstance(anims, dict)
                and isinstance(action, str)
                and isinstance(key, str)):
            if self.kbd.keymap[key]:
                base.player_states['is_idle'] = False
                base.messenger.send("player_h_kick")

    def player_f_kick_action(self, player, key, anims, action):
        if (player and isinstance(anims, dict)
                and isinstance(action, str)
                and isinstance(key, str)):

            if self.kbd.keymap[key]:
                base.player_states['is_idle'] = False
                base.messenger.send("player_h_kick")

    def player_block_action(self, player, key, anims, action):
        if (player and isinstance(anims, dict)
                and isinstance(action, str)
                and isinstance(key, str)):
            if self.kbd.keymap[key]:
                base.player_states['is_idle'] = False
                base.messenger.send("player_block")

    def player_sword_action(self, player, key, anims, action):
        if (player and isinstance(anims, dict)
                and isinstance(action, str)
                and isinstance(key, str)):
            if self.kbd.keymap[key]:
                base.player_states['is_idle'] = False
                base.messenger.send("player_sword")

    def player_bow_action(self, player, key, anims, action):
        if (player and isinstance(anims, dict)
                and isinstance(action, str)
                and isinstance(key, str)):
            if self.kbd.keymap[key]:
                base.player_states['is_idle'] = False
                base.messenger.send("player_bow")

    def player_tengri_action(self, player, key, anims, action):
        if (player and isinstance(anims, dict)
                and isinstance(action, str)
                and isinstance(key, str)):
            if self.kbd.keymap[key]:
                base.player_states['is_idle'] = False
                base.messenger.send("player_tengri")

    def player_umai_action(self, player, key, anims, action):
        if (player and isinstance(anims, dict)
                and isinstance(action, str)
                and isinstance(key, str)):
            if self.kbd.keymap[key]:
                base.player_states['is_idle'] = False
                base.messenger.send("player_umai")

