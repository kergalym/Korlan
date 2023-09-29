from panda3d.core import Vec3
from direct.interval.IntervalGlobal import *

""" ANIMATIONS"""
from Engine import anim_names


class PlayerMovement:

    def __init__(self, kbd, state):
        self.game_settings = base.game_settings
        self.base = base
        self.render = render
        self.kbd = kbd
        self.state = state
        self.actor_play_rate = None

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
                                     anims[anim_names.a_anim_walking])
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
                                     anims[anim_names.a_anim_horse_walking])
            elif state == 'stop' and turning_seq.is_playing():
                player.stop()
                player.pose(anims[action], 0)

    def seq_move_wrapper(self, player, anims, state):
        if player and anims and isinstance(state, str):
            walking_forward_seq = player.get_anim_control(anims[anim_names.a_anim_walking])
            if state == 'loop' and walking_forward_seq.is_playing() is False:
                player.loop(anims[anim_names.a_anim_walking])
                player.set_play_rate(self.base.actor_play_rate,
                                     anims[anim_names.a_anim_walking])
            elif state == 'stop' and walking_forward_seq.is_playing():
                player.stop()
                player.pose(anims[anim_names.a_anim_walking], 0)

    def seq_run_wrapper(self, player, anims, state):
        if player and anims and isinstance(state, str):
            run_forward_seq = player.get_anim_control(anims[anim_names.a_anim_run])
            if state == 'loop' and run_forward_seq.is_playing() is False:
                player.loop(anims[anim_names.a_anim_run])
                player.set_play_rate(2.2,
                                     anims[anim_names.a_anim_run])
            elif state == 'stop' and run_forward_seq.is_playing():
                player.stop()
                player.pose(anims[anim_names.a_anim_run], 0)

    def seq_horse_move_wrapper(self, player, anims, state):
        if player and anims and isinstance(state, str):
            walking_forward_seq = player.get_anim_control(anims[anim_names.a_anim_horse_walking])
            if state == 'loop' and walking_forward_seq.is_playing() is False:
                player.stop(anim_names.a_anim_horse_idle)
                player.loop(anims[anim_names.a_anim_horse_walking])
                player.set_play_rate(self.base.actor_play_rate,
                                     anims[anim_names.a_anim_horse_walking])
            elif state == 'stop' and walking_forward_seq.is_playing():
                player.stop(anim_names.a_anim_horse_walking)
                player.pose(anims[anim_names.a_anim_horse_walking], 0)
                player.loop(anim_names.a_anim_horse_idle)

    def seq_horse_run_wrapper(self, player, anims, state):
        if player and anims and isinstance(state, str):
            run_forward_seq = player.get_anim_control(anims[anim_names.a_anim_horse_run])
            if state == 'loop' and run_forward_seq.is_playing() is False:
                player.stop(anim_names.a_anim_horse_idle)
                player.loop(anims[anim_names.a_anim_horse_run])
                player.set_play_rate(2.2,
                                     anims[anim_names.a_anim_horse_run])
            elif state == 'stop' and run_forward_seq.is_playing():
                player.stop(anim_names.a_anim_horse_run)
                player.pose(anims[anim_names.a_anim_horse_run], 0)
                player.loop(anim_names.a_anim_horse_idle)

    def seq_crouch_move_wrapper(self, player, anims, state):
        if player and anims and isinstance(state, str):
            crouch_walking_forward_seq = player.get_anim_control(anims[anim_names.a_anim_crouch_walking])
            if state == 'loop' and crouch_walking_forward_seq.is_playing() is False:
                player.loop(anims[anim_names.a_anim_crouch_walking])
                player.set_play_rate(self.base.actor_play_rate,
                                     anims[anim_names.a_anim_crouch_walking])
            elif state == 'stop' and crouch_walking_forward_seq.is_playing():
                player.stop()
                player.pose(anims[anim_names.a_anim_crouch_walking], 0)

    def seq_horse_crouch_move_wrapper(self, player, anims, state):
        if player and anims and isinstance(state, str):
            crouch_walking_forward_seq = player.get_anim_control(anims[anim_names.a_anim_horse_crouch_walking])
            if state == 'loop' and crouch_walking_forward_seq.is_playing() is False:
                player.stop(anim_names.a_anim_horse_idle)
                player.loop(anims[anim_names.a_anim_horse_crouch_walking])
                player.set_play_rate(self.base.actor_play_rate,
                                     anims[anim_names.a_anim_horse_crouch_walking])
            elif state == 'stop' and crouch_walking_forward_seq.is_playing():
                player.stop()
                player.pose(anims[anim_names.a_anim_horse_crouch_walking], 0)
                player.loop(anim_names.a_anim_horse_idle)

    def turning_in_place(self, actor, anims, seq_turning_wrapper):
        # Get the time that elapsed since last frame
        dt = globalClock.getDt()

        if "Player" in actor.get_name():
            actor_rb_np = self.base.game_instance["player_np"]

            # Turning in place
            if self.kbd.keymap["left"] and actor_rb_np:
                actor_rb_np.set_h(actor_rb_np.get_h() + 100 * dt)
            if self.kbd.keymap["right"] and actor_rb_np:
                actor_rb_np.set_h(actor_rb_np.get_h() - 100 * dt)

        elif "Horse" in actor.get_name():
            name = "{0}:BS".format(actor.get_name())
            actor_rb_np = self.base.game_instance["actors_np"][name]

            # Turning in place
            if self.kbd.keymap["left"] and actor_rb_np:
                actor_rb_np.set_h(actor_rb_np.get_h() + 100 * dt)
            if self.kbd.keymap["right"] and actor_rb_np:
                actor_rb_np.set_h(actor_rb_np.get_h() - 100 * dt)

        # TODO: Add turning in place when player is crouched
        if (not base.player_states["is_crouch_moving"]
                and not base.player_states["is_crouching"]):
            if (not self.kbd.keymap["forward"]
                    and not self.kbd.keymap["run"]
                    and self.kbd.keymap["left"]):
                Sequence(Parallel(Func(seq_turning_wrapper, actor, anims, "left_turn", 'loop'),
                                  Func(self.state.set_action_state, "is_turning", True)),
                         ).start()
                self.base.sound.play_turning()

            if (not self.kbd.keymap["forward"]
                    and not self.kbd.keymap["run"]
                    and self.kbd.keymap["right"]):
                Sequence(Parallel(Func(seq_turning_wrapper, actor, anims, "right_turn", 'loop'),
                                  Func(self.state.set_action_state, "is_turning", True)),
                         ).start()
                self.base.sound.play_turning()

        # Stop turning in place
        if (not self.kbd.keymap["forward"]
                and not self.kbd.keymap["run"]
                and not self.kbd.keymap["left"]):
            if base.player_states["is_turning"]:
                Sequence(Parallel(Func(seq_turning_wrapper, actor, anims, "left_turn", 'stop'),
                                  Func(self.state.set_action_state, "is_turning", False)),
                         ).start()
                self.base.sound.stop_turning()

        if (not self.kbd.keymap["forward"]
                and not self.kbd.keymap["run"]
                and not self.kbd.keymap["right"]):
            if base.player_states["is_turning"]:
                Sequence(Parallel(Func(seq_turning_wrapper, actor, anims, "right_turn", 'stop'),
                                  Func(self.state.set_action_state, "is_turning", False)),
                         ).start()
                self.base.sound.stop_turning()

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
                and not base.player_states['is_mounted']
                and self.is_ready_for_move()
                and not self.kbd.keymap["attack"]
                and not self.kbd.keymap["block"]):
            # If a move-key is pressed, move the player in the specified direction.
            force = Vec3(0, 0, 0)
            torque = Vec3(0, 0, 0)
            omega = 0.0
            speed = 2

            # Get the time that elapsed since last frame
            dt = globalClock.getDt()
            self.turning_in_place(player, anims, self.seq_turning_wrapper)

            # Forward walk
            if (self.kbd.keymap["forward"]
                    and not self.kbd.keymap["backward"]
                    and self.kbd.keymap["run"] is False
                    and not base.player_states['is_crouch_moving']
                    and base.player_states['is_idle']):

                if base.input_state.is_set('forward'):
                    if str(self.base.game_instance['player_controller'].type) != "BulletCharacterControllerNode":
                        player_rb_np = self.base.game_instance["player_np"]
                        player_rb_np.set_y(player_rb_np, -speed * dt)
                        force.set_y(-speed)
                        force *= 10
                    else:
                        force.set_y(-speed)
                else:
                    player_rb_np = self.base.game_instance["player_np"]
                    lin_vec_z = player_rb_np.node().get_linear_velocity()[2]
                    player_rb_np.node().set_active(True)
                    player_rb_np.node().set_linear_velocity(Vec3(0, 0, lin_vec_z))

            # Backward
            if (self.kbd.keymap["backward"]
                    and self.kbd.keymap["run"] is False
                    and self.kbd.keymap["left"] is False
                    and self.kbd.keymap["right"] is False
                    and not base.player_states['is_crouch_moving']):
                player.set_play_rate(-1.0,
                                     anims[anim_names.a_anim_walking])
                if base.input_state.is_set('reverse'):
                    if str(self.base.game_instance['player_controller'].type) != "BulletCharacterControllerNode":
                        player_rb_np = self.base.game_instance["player_np"]
                        player_rb_np.set_y(player_rb_np, speed * dt)
                        force.set_y(speed)
                        force *= 30
                    else:
                        force.set_y(speed)
                else:
                    player_rb_np = self.base.game_instance["player_np"]
                    lin_vec_z = player_rb_np.node().get_linear_velocity()[2]
                    player_rb_np.node().set_active(True)
                    player_rb_np.node().set_linear_velocity(Vec3(0, 0, lin_vec_z))

            # Forward crouch walk
            if (self.kbd.keymap["forward"]
                    and not self.kbd.keymap["backward"]
                    and self.kbd.keymap["run"] is False
                    and base.player_states['is_crouch_moving']):
                if base.input_state.is_set('forward'):
                    if str(self.base.game_instance['player_controller'].type) != "BulletCharacterControllerNode":
                        player_rb_np = self.base.game_instance["player_np"]
                        player_rb_np.set_y(player_rb_np, -speed * dt)
                        force.set_y(-speed)
                        force *= 10
                    else:
                        force.set_y(-speed)
                else:
                    player_rb_np = self.base.game_instance["player_np"]
                    lin_vec_z = player_rb_np.node().get_linear_velocity()[2]
                    player_rb_np.node().set_active(True)
                    player_rb_np.node().set_linear_velocity(Vec3(0, 0, lin_vec_z))

            player_rb_np = self.base.game_instance["player_np"]
            force = render.getRelativeVector(player_rb_np, force)
            player_rb_np.node().set_active(True)
            player_rb_np.node().apply_central_force(force)
            player_rb_np.node().apply_torque(torque)

            if self.base.game_instance['player_controller']:
                if str(self.base.game_instance['player_controller'].type) == "BulletCharacterControllerNode":
                    self.base.game_instance['player_controller'].set_linear_movement(force, True)
                    self.base.game_instance['player_controller'].set_angular_movement(omega)

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
                    self.base.sound.play_walking()
            else:
                # Stop animation
                if base.player_states['is_moving']:
                    Sequence(Func(self.seq_move_wrapper, player, anims, 'stop'),
                             Func(self.state.set_action_state, "is_moving", False)
                             ).start()
                    self.base.sound.stop_walking()

            if base.player_states['is_crouch_moving']:
                if (self.kbd.keymap["forward"]
                        and self.kbd.keymap["run"] is False
                        and not self.kbd.keymap["backward"]
                        and self.kbd.keymap["run"] is False
                        and self.kbd.keymap["left"] is False
                        and self.kbd.keymap["right"] is False):
                    if not base.player_states['is_idle']:
                        Sequence(Func(self.seq_crouch_move_wrapper, player, anims, 'loop')
                                 ).start()
                        self.base.sound.play_walking()
                else:
                    if base.player_states['is_crouch_moving']:
                        Sequence(Func(self.seq_crouch_move_wrapper, player, anims, 'stop')).start()
                        self.base.sound.stop_walking()

    def player_run_action(self, player, anims):
        if player:
            # When stamina is low, player changes running state to moving
            if (self.kbd.keymap["forward"]
                    and not self.kbd.keymap["backward"]
                    and self.kbd.keymap["run"]
                    and player.get_python_tag('stamina') <= 10):
                force = Vec3(0, 0, 0)
                torque = Vec3(0, 0, 0)
                omega = 0.0
                speed = 2

                if base.input_state.is_set('forward'):
                    if str(self.base.game_instance['player_controller'].type) != "BulletCharacterControllerNode":
                        # Get the time that elapsed since last frame
                        dt = globalClock.getDt()
                        player_rb_np = self.base.game_instance["player_np"]
                        player_rb_np.set_y(player_rb_np, -speed * dt)
                        force *= 10
                        force.set_y(-speed)
                    else:
                        force.set_y(-speed)
                else:
                    player_rb_np = self.base.game_instance["player_np"]
                    lin_vec_z = player_rb_np.node().get_linear_velocity()[2]
                    player_rb_np.node().set_active(True)
                    player_rb_np.node().set_linear_velocity(Vec3(0, 0, lin_vec_z))

                if self.base.game_instance['player_controller']:
                    if str(player.node().type) == "BulletCharacterControllerNode":
                        self.base.game_instance['player_controller'].set_linear_movement(force, True)
                        self.base.game_instance['player_controller'].set_angular_movement(omega)

                player_rb_np = self.base.game_instance["player_np"]
                player_rb_np.node().set_active(True)
                player_rb_np.node().apply_central_force(force)
                player_rb_np.node().apply_torque(torque)

                Sequence(Func(self.seq_move_wrapper, player, anims, 'loop')
                         ).start()

            elif (not self.kbd.keymap["forward"]
                    and not self.kbd.keymap["backward"]
                  and not self.kbd.keymap["run"]
                  and player.get_python_tag('stamina') <= 10):
                Sequence(Func(self.seq_move_wrapper, player, anims, 'stop'),
                         Func(self.state.set_action_state, "is_running", False)
                         ).start()

            # When stamina is higher than 10 units, player changes moving state to running
            if player.get_python_tag('stamina') > 10:
                if (isinstance(anims, dict)
                        and not self.base.game_instance['is_aiming']
                        and not base.player_states['is_using']
                        and not base.player_states['is_attacked']
                        and not base.player_states['is_mounted']
                        and self.is_ready_for_move()
                        and not self.kbd.keymap["attack"]
                        and not self.kbd.keymap["block"]):
                    # If a move-key is pressed, move the player in the specified direction.
                    force = Vec3(0, 0, 0)
                    torque = Vec3(0, 0, 0)
                    speed = 5

                    self.decrement_stamina_while_running(player, speed)

                    if (self.kbd.keymap["forward"]
                            and not self.kbd.keymap["backward"]
                            and self.kbd.keymap["run"]):
                        if base.input_state.is_set('forward'):
                            if str(self.base.game_instance['player_controller'].type) != "BulletCharacterControllerNode":
                                # Get the time that elapsed since last frame
                                dt = globalClock.getDt()
                                player_rb_np = self.base.game_instance["player_np"]
                                # player_rb_np.set_y(player_rb_np, -speed * dt)
                                force *= 10
                                force.set_y(-speed)
                            else:
                                force.set_y(-speed)

                            if self.base.game_instance['player_controller']:
                                if str(self.base.game_instance['player_controller'].type) == "BulletCharacterControllerNode":
                                    self.base.game_instance['player_controller'].set_linear_movement(force, True)
                        else:
                            player_rb_np = self.base.game_instance["player_np"]
                            lin_vec_z = player_rb_np.node().get_linear_velocity()[2]
                            player_rb_np.node().set_active(True)
                            player_rb_np.node().set_linear_velocity(Vec3(0, 0, lin_vec_z))

                    player_rb_np = self.base.game_instance["player_np"]
                    force = render.getRelativeVector(player_rb_np, force)
                    player_rb_np.node().set_active(True)
                    player_rb_np.node().apply_central_force(force)
                    player_rb_np.node().apply_torque(torque)

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

                            self.base.sound.play_running()
                    else:
                        # Stop animation
                        if (base.player_states['is_running']
                                and self.kbd.keymap["left"] is False
                                and self.kbd.keymap["right"] is False
                                and base.player_states['is_crouch_moving'] is False):
                            Sequence(Func(self.seq_run_wrapper, player, anims, 'stop'),
                                     Func(self.state.set_action_state, "is_running", False)
                                     ).start()
                            self.base.sound.stop_running()

                        if not self.kbd.keymap["run"] and player.get_python_tag('stamina') < 2:
                            Sequence(Func(self.seq_run_wrapper, player, anims, 'stop'),
                                     Func(self.state.set_action_state, "is_running", False)
                                     ).start()
                            self.base.sound.stop_running()

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
                horse_rb_np = render.find("**/{0}:BS".format(horse_name))

                force = Vec3(0, 0, 0)
                torque = Vec3(0, 0, 0)
                speed = 2

                # Get the time that elapsed since last frame
                dt = globalClock.getDt()

                # Turning in place
                if self.kbd.keymap["left"] and not self.kbd.keymap["right"]:
                    horse_rb_np.set_h(horse_rb_np.get_h() + 100 * dt)
                if self.kbd.keymap["right"] and not self.kbd.keymap["left"]:
                    horse_rb_np.set_h(horse_rb_np.get_h() - 100 * dt)

                # todo: uncomment when horse turning anims become ready
                # self.turning_in_place(player, anims, self.seq_horse_turning_wrapper)

                # Movement
                if (self.kbd.keymap["forward"]
                        and not self.kbd.keymap["backward"]
                        and self.kbd.keymap["run"] is False):
                    if base.input_state.is_set('forward'):
                        horse_rb_np.set_y(horse_rb_np, -speed * dt)
                        force.set_y(-speed)
                        force *= 10
                    else:
                        lin_vec_z = horse_rb_np.node().get_linear_velocity()[2]
                        horse_rb_np.node().set_active(True)
                        horse_rb_np.node().set_linear_velocity(Vec3(0, 0, lin_vec_z))

                if (self.kbd.keymap["backward"]
                        and self.kbd.keymap["run"] is False):
                    if base.input_state.is_set('reverse'):
                        horse_rb_np.set_y(horse_rb_np, speed * dt)
                        force.set_y(-speed)
                        force *= 10
                    else:
                        lin_vec_z = horse_rb_np.node().get_linear_velocity()[2]
                        horse_rb_np.node().set_active(True)
                        horse_rb_np.node().set_linear_velocity(Vec3(0, 0, lin_vec_z))

                horse_rb_np.node().set_active(True)
                force = render.getRelativeVector(horse_rb_np, force)
                horse_rb_np.node().apply_central_force(force)
                horse_rb_np.node().apply_torque(torque)

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
                                         anims[anim_names.a_anim_horse_walking])

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
                horse_rb_np = render.find("**/{0}:BS".format(horse_name))

                force = Vec3(0, 0, 0)
                torque = Vec3(0, 0, 0)
                speed = 7

                self.decrement_stamina_while_running(player, speed)

                # Get the time that elapsed since last frame
                dt = globalClock.getDt()

                if (self.kbd.keymap["forward"]
                        and not self.kbd.keymap["backward"]
                        and self.kbd.keymap["run"]):
                    if base.input_state.is_set('forward'):
                        horse_rb_np.set_y(horse_rb_np, -speed * dt)
                        force.set_y(-speed)
                        force *= 20
                    else:
                        lin_vec_z = horse_rb_np.node().get_linear_velocity()[2]
                        horse_rb_np.node().set_active(True)
                        horse_rb_np.node().set_linear_velocity(Vec3(0, 0, lin_vec_z))

                horse_rb_np.node().set_active(True)
                force = render.getRelativeVector(horse_rb_np, force)
                horse_rb_np.node().apply_central_force(force)
                horse_rb_np.node().apply_torque(torque)

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
