from panda3d.core import Vec3
from direct.interval.IntervalGlobal import *


class PlayerMovement:

    def __init__(self, kbd, state):
        self.game_settings = base.game_settings
        self.base = base
        self.render = render
        self.kbd = kbd
        self.state = state
        self.actor_bs = None
        self.actor_play_rate = None

        self.idle_action = "Standing_idle_female"
        self.walking_forward_action = "Walking"
        self.run_forward_action = "Running"
        self.crouch_walking_forward_action = 'crouch_walking_forward'
        self.horse_idle_action = "horse_idle"
        self.horse_walking_forward_action = "horse_walking"
        self.horse_run_forward_action = "horse_running"
        self.horse_crouch_walking_forward_action = ""

        self.exclude_while_move = dict(base.player_states)
        self.exclude_while_move.pop("is_alive")
        self.exclude_while_move.pop("is_idle")
        self.exclude_while_move.pop("is_moving")
        self.exclude_while_move.pop("is_running")
        self.exclude_while_move.pop("is_crouch_moving")
        self.exclude_while_move.pop("is_mounted")
        self.exclude_while_move.pop("is_blocking")
        self.exclude_while_move.pop("is_hitting")
        self.exclude_while_move.pop("horse_riding")
        self.exclude_while_move.pop("horse_is_ready_to_be_used")
        self.exclude_while_move.pop("has_sword")
        self.exclude_while_move.pop("has_bow")
        self.exclude_while_move.pop("has_tengri")
        self.exclude_while_move.pop("has_umai")

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

    def turning_in_place(self, actor, anims, seq_turning_wrapper):
        # Get the time that elapsed since last frame
        dt = globalClock.getDt()

        if "Player" in actor.get_name():
            if not self.actor_bs:
                self.actor_bs = self.base.get_actor_bullet_shape_node(asset=actor.get_name(), type="Player")
        elif "Horse" in actor.get_name():
            if not self.actor_bs:
                self.actor_bs = self.base.get_actor_bullet_shape_node(asset=actor.get_name(), type="NPC")

        # Turning in place
        if self.kbd.keymap["left"] and self.actor_bs:
            self.actor_bs.set_h(self.actor_bs.get_h() + 100 * dt)
        if self.kbd.keymap["right"] and self.actor_bs:
            self.actor_bs.set_h(self.actor_bs.get_h() - 100 * dt)

        if (not self.kbd.keymap["forward"]
                and not self.kbd.keymap["run"]
                and self.kbd.keymap["left"]):
            Sequence(Parallel(Func(seq_turning_wrapper, actor, anims, "left_turn", 'loop'),
                              Func(self.state.set_action_state, "is_turning", True)),
                     ).start()
        if (not self.kbd.keymap["forward"]
                and not self.kbd.keymap["run"]
                and self.kbd.keymap["right"]):
            Sequence(Parallel(Func(seq_turning_wrapper, actor, anims, "right_turn", 'loop'),
                              Func(self.state.set_action_state, "is_turning", True)),
                     ).start()

        # Stop turning in place
        if (not self.kbd.keymap["forward"]
                and not self.kbd.keymap["run"]
                and not self.kbd.keymap["left"]):
            Sequence(Parallel(Func(seq_turning_wrapper, actor, anims, "left_turn", 'stop'),
                              Func(self.state.set_action_state, "is_turning", False)),
                     ).start()
        if (not self.kbd.keymap["forward"]
                and not self.kbd.keymap["run"]
                and not self.kbd.keymap["right"]):
            Sequence(Parallel(Func(seq_turning_wrapper, actor, anims, "right_turn", 'stop'),
                              Func(self.state.set_action_state, "is_turning", False)),
                     ).start()

    def decrement_stamina_while_running(self, player, move_unit):
        # Get the time that elapsed since last frame
        dt = globalClock.getDt()
        seconds = int(60 * dt)

        if self.kbd.keymap["forward"] and self.kbd.keymap["run"]:
            if self.base.game_instance['hud_np']:
                if self.base.game_instance['player_props']['stamina'] > 1:
                    if seconds == 2:
                        self.base.game_instance['player_props']['stamina'] -= move_unit
                        stamina = self.base.game_instance['player_props']['stamina']
                        self.base.game_instance['hud_np'].player_bar_ui_stamina['value'] = stamina
                        player.set_python_tag('stamina', stamina)

    def is_ready_for_move(self):
        # Store player states which should not be played before walking
        if not any(self.exclude_while_move.values()):
            return True

    def player_movement_action(self, player, anims):
        if (player and isinstance(anims, dict)
                and not self.base.game_instance['is_aiming']
                and not base.player_states['is_using']
                and not base.player_states['is_attacked']
                and self.is_ready_for_move()
                and not self.kbd.keymap["attack"]
                and not self.kbd.keymap["block"]):
            # If a move-key is pressed, move the player in the specified direction.
            speed = Vec3(0, 0, 0)
            omega = 0.0
            move_unit = 2

            self.turning_in_place(player, anims, self.seq_turning_wrapper)

            # Forward walk
            if (self.kbd.keymap["forward"]
                    and not self.kbd.keymap["backward"]
                    and self.kbd.keymap["run"] is False
                    and base.player_states['is_moving']
                    and base.player_states['is_idle']):
                if base.input_state.is_set('forward'):
                    speed.set_y(-move_unit)
            # Forward crouch walk
            if (self.kbd.keymap["forward"]
                    and not self.kbd.keymap["backward"]
                    and self.kbd.keymap["run"] is False
                    and base.player_states['is_crouch_moving']
                    and base.player_states['is_idle']):
                if base.input_state.is_set('forward'):
                    speed.set_y(-move_unit)
            # Backward
            if (self.kbd.keymap["backward"]
                    and self.kbd.keymap["run"] is False
                    and self.kbd.keymap["left"] is False
                    and self.kbd.keymap["right"] is False
                    and base.player_states['is_moving']
                    and base.player_states['is_idle']):
                if base.input_state.is_set('reverse'):
                    speed.set_y(move_unit)
            # Crouch backward
            if (self.kbd.keymap["backward"]
                    and self.kbd.keymap["run"] is False
                    and self.kbd.keymap["left"] is False
                    and self.kbd.keymap["right"] is False
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
                        and base.player_states['is_idle']):
                    Sequence(Parallel(Func(self.seq_move_wrapper, player, anims, 'loop'),
                                      Func(self.state.set_action_state, "is_moving", True)),
                             ).start()
                if (base.player_states['is_crouch_moving']
                        and base.player_states['is_idle']):
                    Sequence(Func(self.seq_crouch_move_wrapper, player, anims, 'loop')
                             ).start()
            else:
                # Stop animation
                if base.player_states['is_moving']:
                    Sequence(Func(self.seq_move_wrapper, player, anims, 'stop'),
                             Func(self.state.set_action_state, "is_moving", False)
                             ).start()
                if base.player_states['is_crouch_moving']:
                    Sequence(Func(self.seq_crouch_move_wrapper, player, anims, 'stop')).start()

            # Actor backward movement
            if (self.kbd.keymap["backward"]
                    and self.kbd.keymap["run"] is False
                    and self.kbd.keymap["left"] is False
                    and self.kbd.keymap["right"] is False):
                player.set_play_rate(-1.0,
                                     anims[self.walking_forward_action])

    def player_run_action(self, player, anims):
        if (player and isinstance(anims, dict)
                and not self.base.game_instance['is_aiming']
                and not base.player_states['is_using']
                and not base.player_states['is_attacked']
                and self.is_ready_for_move()
                and not self.kbd.keymap["attack"]
                and not self.kbd.keymap["block"]):
            # If a move-key is pressed, move the player in the specified direction.
            speed = Vec3(0, 0, 0)
            move_unit = 7

            self.decrement_stamina_while_running(player, move_unit)

            if (self.kbd.keymap["forward"]
                    and not self.kbd.keymap["backward"]
                    and self.kbd.keymap["run"]):
                if base.input_state.is_set('forward'):
                    if self.base.game_instance['player_props']['stamina'] > 1:
                        speed.set_y(-move_unit)

                    if self.base.game_instance['player_controller_np']:
                        self.base.game_instance['player_controller_np'].set_linear_movement(speed, True)

            # If the player does action, loop the animation.
            # If it is standing still, stop the animation.
            if (self.kbd.keymap["forward"]
                    and not self.kbd.keymap["backward"]
                    and self.kbd.keymap["run"]):
                if (not base.player_states['is_running']
                        and base.player_states['is_idle']
                        and player.get_python_tag('stamina') > 3):
                    Sequence(Parallel(Func(self.seq_run_wrapper, player, anims, 'loop'),
                                      Func(self.state.set_action_state, "is_running", True))).start()
                if (base.player_states['is_running']
                        and player.get_python_tag('stamina') > 3):
                    Sequence(Func(self.seq_run_wrapper, player, anims, 'loop')
                             ).start()
            else:
                # Stop animation
                if (base.player_states['is_running']
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
                and not base.player_states['is_attacked']
                and base.player_states['is_mounted']
                and self.is_ready_for_move()):

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

                # todo: uncomment when horse turning anims become ready
                # self.turning_in_place(player, anims, self.seq_horse_turning_wrapper)

                # Movement
                if (self.kbd.keymap["forward"]
                        and not self.kbd.keymap["backward"]
                        and self.kbd.keymap["run"] is False):
                    if base.input_state.is_set('forward'):
                        horse_bs.set_y(horse_bs, -move_unit * dt)
                if (self.kbd.keymap["backward"]
                        and self.kbd.keymap["run"] is False):
                    if base.input_state.is_set('reverse'):
                        horse_bs.set_y(horse_bs, move_unit * dt)

                # If the player does action, loop the animation through messenger.
                if (self.kbd.keymap["forward"]
                        and not self.kbd.keymap["backward"]
                        and self.kbd.keymap["run"] is False
                        or self.kbd.keymap["backward"]):
                    if (base.player_states['is_moving'] is False
                            and base.player_states['is_crouch_moving'] is False
                            and base.player_states["is_running"] is False
                            and base.player_states['is_idle']):
                        Sequence(Parallel(Func(self.seq_horse_move_wrapper, player, anims, 'loop'),
                                          Func(self.state.set_action_state, "is_moving", True)),
                                 ).start()
                    # crouch walking
                    if (base.player_states['is_moving'] is False
                            and base.player_states["is_running"] is False
                            and base.player_states['is_crouch_moving']
                            and base.player_states['is_idle']):
                        # todo: add anim and uncomment
                        """Sequence(Func(self.seq_crouch_horse_move_wrapper, player, anims, 'loop')
                                 ).start()"""
                else:
                    # Stop animation
                    if (base.player_states['is_moving']
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
                        and self.kbd.keymap["run"] is False
                        and base.player_states["is_running"] is False):
                    player.set_play_rate(-1.0,
                                         anims[self.horse_walking_forward_action])

    def horse_riding_run_action(self, anims):
        if (isinstance(anims, dict)
                and not self.base.game_instance['is_aiming']
                and not base.player_states['is_attacked']
                and self.is_ready_for_move()
                and base.player_states['is_mounted']
                and not base.player_states['is_crouch_moving']):
            # If a move-key is pressed, move the player in the specified direction.
            horse_name = base.game_instance['player_using_horse']
            if self.base.game_instance['actors_ref'].get(horse_name):
                player = self.base.game_instance['actors_ref'][horse_name]
                horse_bs = render.find("**/{0}:BS".format(horse_name))
                move_unit = 7

                self.decrement_stamina_while_running(player, move_unit)

                # Get the time that elapsed since last frame
                dt = globalClock.getDt()

                if (self.kbd.keymap["forward"]
                        and not self.kbd.keymap["backward"]
                        and self.kbd.keymap["run"]):
                    if base.input_state.is_set('forward'):
                        horse_bs.set_y(horse_bs, -move_unit * dt)

                # If the player does action, loop the animation.
                # If it is standing still, stop the animation.
                if (self.kbd.keymap["forward"]
                        and not self.kbd.keymap["backward"]
                        and self.kbd.keymap["run"]):
                    if (base.player_states['is_moving'] is False
                            and base.player_states['is_crouch_moving'] is False
                            and base.player_states["is_running"] is False
                            and base.player_states['is_idle']):
                        Sequence(Parallel(Func(self.seq_horse_run_wrapper, player, anims, 'loop'),
                                          Func(self.state.set_action_state, "is_running", True)),
                                 ).start()
                    if (base.player_states['is_moving'] is False
                            and base.player_states["is_crouch_moving"] is False
                            and base.player_states['is_running']
                            and base.player_states['is_idle'] is False):
                        self.seq_horse_run_wrapper(player, anims, 'loop')

                else:
                    # Stop animation
                    if (base.player_states['is_running']
                            and base.player_states["is_moving"] is False
                            and base.player_states['is_crouch_moving'] is False):
                        self.seq_horse_run_wrapper(player, anims, 'stop'),
                        self.state.set_action_state("is_running", False)
