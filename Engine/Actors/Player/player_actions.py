from panda3d.core import Vec3, BitMask32, Point3

from direct.interval.IntervalGlobal import *
from direct.task.TaskManagerGlobal import taskMgr

""" ANIMATIONS"""
from Engine import anim_names


class PlayerActions:

    def __init__(self, kbd, state, archery):
        self.game_settings = base.game_settings
        self.base = base
        self.render = render
        self.state = state
        self.actor_play_rate = None
        self.kbd = kbd
        self.archery = archery
        self.base.game_instance["player_actions_cls"] = self

    def seq_pick_item_wrapper_task(self, player, anims, action, joint_name, task):
        if player and anims and action and joint_name:
            if player.get_current_frame(action):
                if (player.get_current_frame(action) > 67
                        and player.get_current_frame(action) < 72):
                    self.state.pick_up_item(player, joint_name)
        return task.cont

    def seq_drop_item_wrapper_task(self, player, anims, action, task):
        if player and anims and action:
            if player.get_current_frame(action):
                if (player.get_current_frame(action) > 67
                        and player.get_current_frame(action) < 72):
                    self.state.drop_item(player)
        return task.cont

    def remove_seq_pick_item_wrapper_task(self):
        taskMgr.remove("seq_pick_item_wrapper_task")

    def remove_seq_drop_item_wrapper_task(self):
        taskMgr.remove("seq_drop_item_wrapper_task")

    def seq_set_player_pos_wrapper(self, player, pos_y):
        if player and isinstance(pos_y, float):
            dt = globalClock.getDt()
            player.set_y(player, pos_y * dt)

    def _player_jump_move_task(self, action, task):
        player = self.base.game_instance["player_ref"]

        if player.get_current_frame(action):
            if (player.get_current_frame(action) > 24
                    and player.get_current_frame(action) < 27):
                player_bs = self.base.game_instance["player_np"]
                current_pos = player_bs.get_pos()
                delta_offset = current_pos + Vec3(0, -2.0, 0)
                pos_interval_seq = player_bs.posInterval(1.0, delta_offset,
                                                         startPos=current_pos)
                seq = Sequence(pos_interval_seq)
                if not seq.is_playing():
                    seq.start()

                return task.done

        return task.cont

    def _player_bullet_jump_helper(self, action):
        if self.base.game_instance['player_controller_np']:
            if self.base.game_instance['player_controller_np'].is_on_ground():
                self.base.game_instance['player_controller_np'].set_max_jump_height(3.0)
                self.base.game_instance['player_controller_np'].set_jump_speed(8.0)
                self.base.game_instance['player_controller_np'].do_jump()

                if taskMgr.hasTaskNamed("player_jump_move_task"):
                    taskMgr.remove("player_jump_move_task")

                taskMgr.add(self._player_jump_move_task,
                            "player_jump_move_task",
                            extraArgs=[action],
                            appendTask=True)

    def player_bullet_crouch_helper(self):
        crouch_bs_mask = BitMask32.allOff()
        capsule_bs_mask = BitMask32.allOff()
        if base.player_states["is_crouch_moving"]:
            crouch_bs_mask = self.base.game_instance['player_crouch_bs_np_mask']
            capsule_bs_mask = BitMask32.allOff()
        elif not base.player_states["is_crouch_moving"]:
            crouch_bs_mask = BitMask32.allOff()
            capsule_bs_mask = self.base.game_instance["player_np_mask"]
        self.base.game_instance['player_crouch_bs_np'].set_collide_mask(crouch_bs_mask)
        self.base.game_instance['player_np'].set_collide_mask(capsule_bs_mask)

    def ground_water_action_switch_task(self, task):
        if self.base.game_instance['menu_mode']:
            return task.done

        if self.base.game_instance['water_trigger_np']:
            trigger_np = self.base.game_instance['water_trigger_np']
            for node in trigger_np.node().get_overlapping_nodes():
                if "Player" in node.get_name():
                    # todo: change idle_action to swim_idle
                    if anim_names.a_anim_idle_player != "Standing_idle_female":
                        anim_names.a_anim_idle_player = "Standing_idle_female"
                    if anim_names.a_anim_walking != "Swimming":
                        anim_names.a_anim_walking = "Swimming"
                else:
                    if anim_names.a_anim_idle_player != "Standing_idle_female":
                        anim_names.a_anim_idle_player = "Standing_idle_female"
                    if anim_names.a_anim_walking != "Walking":
                        anim_names.a_anim_walking = "Walking"

        return task.cont

    def player_in_crouched_to_stand_with_any_action(self, player, key, anims, action, is_in_action):
        if player and key and anims and action and is_in_action and isinstance(is_in_action, str):
            crouched_to_standing = player.get_anim_control(anims[anim_names.a_anim_crouching_stand])
            if (base.player_states[is_in_action] is False
                    and crouched_to_standing.is_playing() is False
                    and base.player_states['is_crouching'] is False
                    and base.player_states['is_crouch_moving']):
                # TODO: Use blending for smooth transition between animations
                # Do an animation sequence if player is crouched.
                crouch_to_stand_seq = player.actor_interval(anims[anim_names.a_anim_crouching_stand],
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
            crouched_to_standing = player.get_anim_control(anims[anim_names.a_anim_crouching_stand])
            if (base.player_states[has_weapon] is False
                    and crouched_to_standing.is_playing() is False
                    and base.player_states['is_crouching'] is False
                    and base.player_states['is_crouch_moving']):
                # TODO: Use blending for smooth transition between animations
                # Do an animation sequence if player is crouched.
                crouch_to_stand_seq = player.actor_interval(anims[anim_names.a_anim_crouching_stand],
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
                crouched_to_standing = player.get_anim_control(anims[anim_names.a_anim_crouching_stand])
                standing_to_crouch = player.get_anim_control(anims[anim_names.a_anim_standing_crouch])
                # If the player does action, play the animation through sequence.
                base.player_states['is_idle'] = False
                if (standing_to_crouch.is_playing() is False
                        and base.player_states['is_idle'] is False
                        and base.player_states['is_crouching'] is False
                        and base.player_states['is_crouch_moving'] is False):
                    # TODO: Use blending for smooth transition between animations
                    # Do an animation sequence if player is crouched.
                    stand_to_crouch_seq = player.actor_interval(anims[anim_names.a_anim_standing_crouch],
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
                    any_action_seq = player.actor_interval(anims[anim_names.a_anim_crouching_stand],
                                                           playRate=self.base.actor_play_rate)

                    self.base.game_instance["player_ref"].set_control_effect(anim_names.a_anim_idle_player, 0.1)
                    self.base.game_instance["player_ref"].set_control_effect(anim_names.a_anim_crouching_stand, 0.9)

                    Sequence(any_action_seq,
                             Func(self.state.set_action_state_crouched, "is_crouch_moving", False),
                             Func(self.state.set_do_once_key, key, False),
                             ).start()

    def player_jump_action(self, player, key, anims, action):
        if (player and isinstance(anims, dict)
                and isinstance(action, str)
                and isinstance(key, str)
                and not base.player_states['is_using']
                and not base.player_states['is_attacked']
                and not base.player_states['is_busy']
                and not base.player_states['is_moving']
                and not self.base.game_instance['is_aiming']):
            if self.kbd.keymap[key] and not base.do_key_once[key]:
                self.state.set_do_once_key(key, True)
                crouched_to_standing = player.get_anim_control(anims[anim_names.a_anim_crouching_stand])
                base.player_states['is_idle'] = False

                self.player_in_crouched_to_stand_with_any_action(player, key, anims, action, "is_jumping")

                if (base.player_states['is_jumping'] is False
                        and crouched_to_standing.is_playing() is False
                        and base.player_states['is_crouch_moving']):
                    crouch_to_stand_seq = player.actor_interval(anims[anim_names.a_anim_crouching_stand],
                                                                playRate=self.base.actor_play_rate)
                    # Do an animation sequence if player is stayed.
                    any_action_seq = player.actor_interval(anims[action],
                                                           playRate=self.base.actor_play_rate)
                    Sequence(crouch_to_stand_seq,
                             Func(self.state.set_action_state, "is_jumping", True),
                             Func(self._player_bullet_jump_helper, action),
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
                             Func(self._player_bullet_jump_helper, action),
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
                and not base.player_states['is_attacked']
                and not base.player_states['is_busy']
                and not base.player_states['is_moving']
                and not self.base.game_instance['is_aiming']):
            if self.kbd.keymap[key] and not base.do_key_once[key]:
                self.state.set_do_once_key(key, True)
                crouched_to_standing = player.get_anim_control(anims[anim_names.a_anim_crouching_stand])

                if not player.get_python_tag("is_item_using"):
                    # No item near player, reset key
                    if not player.get_python_tag("is_close_to_use_item"):
                        self.state.set_do_once_key(key, False)

                    # Take item
                    if player.get_python_tag("is_close_to_use_item"):
                        # Show item menu here if indoor
                        if self.base.game_instance["is_indoor"]:
                            if not self.base.game_instance['item_menu_np'].item_menu_ui:
                                self.base.game_instance['item_menu_np'].set_item_menu(anims, action)
                        else:
                            base.player_states['is_idle'] = False
                            # just take item if not indoor
                            taskMgr.add(self.seq_pick_item_wrapper_task,
                                        "seq_pick_item_wrapper_task",
                                        extraArgs=[player, anims, action, "Korlan:RightHand"],
                                        appendTask=True)

                            if (base.player_states['is_using'] is False
                                    and crouched_to_standing.is_playing() is False
                                    and base.player_states['is_crouch_moving'] is True):
                                # TODO: Use blending for smooth transition between animations
                                # Do an animation sequence if player is crouched.
                                crouch_to_stand_seq = player.actor_interval(anims[anim_names.a_anim_crouching_stand],
                                                                            playRate=self.base.actor_play_rate)
                                any_action_seq = player.actor_interval(anims[action],
                                                                       playRate=self.base.actor_play_rate)
                                Sequence(crouch_to_stand_seq,
                                         Func(self.state.set_action_state, "is_using", True),
                                         any_action_seq,
                                         Func(self.remove_seq_pick_item_wrapper_task),
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
                                         Func(self.remove_seq_pick_item_wrapper_task),
                                         Func(self.state.set_action_state, "is_using", False),
                                         Func(self.state.set_do_once_key, key, False),
                                         ).start()

                elif player.get_python_tag("is_item_using"):
                    # Drop item if is using
                    if self.base.game_instance["is_indoor"]:
                        # Show item menu here if indoor
                        if not self.base.game_instance['item_menu_np'].item_menu_ui:
                            self.base.game_instance['item_menu_np'].set_item_menu(anims, action)
                    else:
                        base.player_states['is_idle'] = False
                        # Just drop item if not indoor
                        taskMgr.add(self.seq_drop_item_wrapper_task,
                                    "seq_drop_item_wrapper_task",
                                    extraArgs=[player, anims, action],
                                    appendTask=True)

                        if (base.player_states['is_using'] is False
                                and crouched_to_standing.is_playing() is False
                                and base.player_states['is_crouching'] is True):
                            # TODO: Use blending for smooth transition between animations
                            # Do an animation sequence if player is crouched.
                            crouch_to_stand_seq = player.actor_interval(anims[anim_names.a_anim_crouching_stand],
                                                                        playRate=self.base.actor_play_rate)
                            any_action_seq = player.actor_interval(anims[action],
                                                                   playRate=self.base.actor_play_rate)
                            Sequence(crouch_to_stand_seq,
                                     Func(self.state.set_action_state, "is_using", True),
                                     any_action_seq,
                                     Func(self.remove_seq_drop_item_wrapper_task),
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
                                     Func(self.remove_seq_drop_item_wrapper_task),
                                     Func(self.state.set_action_state, "is_using", False),
                                     Func(self.state.set_do_once_key, key, False),
                                     ).start()

    def player_forwardroll_action(self, player, anims):
        if (player and isinstance(anims, dict)
                and not base.player_states['is_using']
                and not base.player_states['is_attacked']
                and not base.player_states['is_busy']
                and not self.base.game_instance['is_aiming']):
            crouched_to_standing = player.get_anim_control(anims[anim_names.a_anim_crouching_stand])

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
            elif (self.kbd.keymap["forward"]
                  and not self.kbd.keymap["run"]
                  and not self.kbd.keymap["jump"]):
                if (base.player_states['is_busy'] is False
                        and crouched_to_standing.is_playing() is False
                        and base.player_states['is_crouch_moving'] is False):
                    walking_forward_seq = player.get_anim_control(anims[anim_names.a_anim_walking])
                    if walking_forward_seq.is_playing() is False:
                        player.loop(anims[anim_names.a_anim_walking])
                        player.set_play_rate(self.base.actor_play_rate,
                                             anims[anim_names.a_anim_walking])
                elif (base.player_states['is_busy'] is False
                      and crouched_to_standing.is_playing()
                      and base.player_states['is_crouch_moving']):
                    crouch_move_forward_seq = player.get_anim_control(anims[anim_names.a_anim_crouch_walking])
                    if crouch_move_forward_seq.is_playing() is False:
                        player.loop(anims[anim_names.a_anim_crouch_walking])
                        player.set_play_rate(self.base.actor_play_rate,
                                             anims[anim_names.a_anim_crouch_walking])

    def player_attack_action(self, player, key, anims, action):
        dt = globalClock.getDt()
        if (player and isinstance(anims, dict)
                and isinstance(key, str)
                and not base.player_states['is_using']
                and not base.player_states['is_attacked']
                and not base.player_states['is_busy']
                and not base.player_states['is_moving']
                and not self.base.game_instance['is_aiming']):
            if self.kbd.keymap[key] and not base.do_key_once[key]:
                self.state.set_do_once_key(key, True)

                if not player.get_python_tag("first_attack"):
                    player.set_python_tag("first_attack", True)

                crouched_to_standing = player.get_anim_control(anims[anim_names.a_anim_crouching_stand])
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

                    player_bs = self.base.game_instance["player_np"]
                    if player_bs.get_y() != player_bs.get_y() - 2:
                        player_bs.set_y(player_bs, -1.0 * dt)

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
                and not base.player_states['is_attacked']
                and not base.player_states['is_busy']
                and not base.player_states['is_moving']
                and not self.base.game_instance['is_aiming']):
            if self.kbd.keymap[key] and not base.do_key_once[key]:
                self.state.set_do_once_key(key, True)
                crouched_to_standing = player.get_anim_control(anims[anim_names.a_anim_crouching_stand])
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
                and not base.player_states['is_attacked']
                and not base.player_states['is_busy']
                and not base.player_states['is_moving']
                and not self.base.game_instance['is_aiming']):
            if self.kbd.keymap[key] and not base.do_key_once[key]:
                self.state.set_do_once_key(key, True)
                crouched_to_standing = player.get_anim_control(anims[anim_names.a_anim_crouching_stand])
                base.player_states['is_idle'] = False
                if (base.player_states['is_h_kicking'] is False
                        and crouched_to_standing.is_playing() is False
                        and base.player_states['is_crouch_moving'] is True):
                    player_bs = self.base.game_instance["player_np"]
                    # TODO: Use blending for smooth transition between animations
                    # Do an animation sequence if player is crouched.
                    crouch_to_stand_seq = player.actor_interval(anims[anim_names.a_anim_crouching_stand],
                                                                playRate=self.base.actor_play_rate)
                    any_action_seq = player.actor_interval(anims[action],
                                                           playRate=self.base.actor_play_rate)
                    Sequence(crouch_to_stand_seq,
                             Func(self.state.set_action_state, "is_h_kicking", True),
                             Parallel(any_action_seq,
                                      Func(self.seq_set_player_pos_wrapper, player_bs, -2.5),
                                      ),
                             Func(self.state.set_action_state, "is_h_kicking", False),
                             Func(self.state.set_do_once_key, key, False),
                             ).start()

                elif (base.player_states['is_h_kicking'] is False
                      and crouched_to_standing.is_playing() is False
                      and base.player_states['is_crouch_moving'] is False):
                    player_bs = self.base.game_instance["player_np"]
                    any_action_seq = player.actor_interval(anims[action],
                                                           playRate=self.base.actor_play_rate)
                    Sequence(Func(self.state.set_action_state, "is_h_kicking", True),
                             Parallel(any_action_seq,
                                      Func(self.seq_set_player_pos_wrapper, player_bs, -2.5),
                                      ),
                             Func(self.state.set_action_state, "is_h_kicking", False),
                             Func(self.state.set_do_once_key, key, False),
                             ).start()

    def player_f_kick_action(self, player, key, anims, action):
        if (player and isinstance(anims, dict)
                and isinstance(action, str)
                and isinstance(key, str)
                and not base.player_states['is_using']
                and not base.player_states['is_attacked']
                and not base.player_states['is_busy']
                and not base.player_states['is_moving']
                and not self.base.game_instance['is_aiming']):
            if self.kbd.keymap[key] and not base.do_key_once[key]:
                self.state.set_do_once_key(key, True)
                crouched_to_standing = player.get_anim_control(anims[anim_names.a_anim_crouching_stand])
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
                and not base.player_states['is_attacked']
                and not base.player_states['is_busy']
                and not base.player_states['is_moving']
                and not self.base.game_instance['is_aiming']):
            if self.kbd.keymap[key] and not base.do_key_once[key]:
                self.state.set_do_once_key(key, True)
                crouched_to_standing = player.get_anim_control(anims[anim_names.a_anim_crouching_stand])
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
                and not base.player_states['is_attacked']
                and not base.player_states['is_busy']
                and not self.base.game_instance['is_aiming']):
            if self.kbd.keymap[key] and not base.do_key_once[key]:
                crouched_to_standing = player.get_anim_control(anims[anim_names.a_anim_crouching_stand])
                self.state.set_do_once_key(key, True)
                base.player_states['is_idle'] = False
                if (base.player_states['has_sword'] is False
                        and crouched_to_standing.is_playing() is False
                        and base.player_states['is_crouch_moving']):
                    # Do an animation sequence if player is crouched.
                    if self.base.game_instance['hud_np']:
                        self.base.game_instance['hud_np'].toggle_weapon_state(weapon_name="sword")
                    crouch_to_stand_seq = player.actor_interval(anims[anim_names.a_anim_crouching_stand],
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
                    crouch_to_stand_seq = player.actor_interval(anims[anim_names.a_anim_crouching_stand],
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
                and not base.player_states['is_attacked']
                and not base.player_states['is_busy']
                and isinstance(action, str)
                and isinstance(key, str)):
            if self.kbd.keymap[key] and not base.do_key_once[key]:
                self.state.set_do_once_key(key, True)
                crouched_to_standing = player.get_anim_control(anims[anim_names.a_anim_crouching_stand])
                base.player_states['is_idle'] = False
                # TODO: Use blending for smooth transition between animations

                if (base.player_states['has_bow'] is False
                        and crouched_to_standing.is_playing() is False
                        and base.player_states['is_crouch_moving']):
                    if self.base.game_instance['hud_np']:
                        self.base.game_instance['hud_np'].toggle_weapon_state(weapon_name="bow")
                    # Do an animation sequence if player is crouched.
                    crouch_to_stand_seq = player.actor_interval(anims[anim_names.a_anim_crouching_stand],
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
                    crouch_to_stand_seq = player.actor_interval(anims[anim_names.a_anim_crouching_stand],
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
                and not base.player_states['is_attacked']
                and not base.player_states['is_busy']
                and not self.base.game_instance['is_aiming']):
            if self.kbd.keymap[key] and not base.do_key_once[key]:
                crouched_to_standing = player.get_anim_control(anims[anim_names.a_anim_crouching_stand])
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
                and not base.player_states['is_attacked']
                and not base.player_states['is_busy']
                and isinstance(action, str)
                and isinstance(key, str)):
            if self.kbd.keymap[key] and not base.do_key_once[key]:
                self.state.set_do_once_key(key, True)
                crouched_to_standing = player.get_anim_control(anims[anim_names.a_anim_crouching_stand])
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
                and not base.player_states['is_attacked']
                and not base.player_states['is_busy']
                and not base.player_states['is_moving']):
            if self.kbd.keymap[key] and not base.do_key_once[key]:
                self.state.set_do_once_key(key, True)
                crouched_to_standing = player.get_anim_control(anims[anim_names.a_anim_crouching_stand])
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
                and not base.player_states['is_attacked']
                and not base.player_states['is_busy']
                and not base.player_states['is_moving']):
            if self.kbd.keymap[key] and not base.do_key_once[key]:
                self.state.set_do_once_key(key, True)
                crouched_to_standing = player.get_anim_control(anims[anim_names.a_anim_crouching_stand])
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
                crouched_to_standing = player.get_anim_control(anims[anim_names.a_anim_crouching_stand])

                if self.archery.arrow_ref:
                    if self.archery.arrow_ref.get_python_tag("power") > 0:
                        self.archery.arrow_ref.set_python_tag("power", 0)

                if (crouched_to_standing.is_playing() is False
                        and base.player_states['is_crouching'] is True):
                    # TODO: Use blending for smooth transition between animations
                    # Do an animation sequence if player is crouched.
                    crouch_to_stand_seq = player.actor_interval(anims[anim_names.a_anim_crouching_stand],
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

                    if not player.get_python_tag("first_attack"):
                        player.set_python_tag("first_attack", True)

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
                crouched_to_standing = player.get_anim_control(anims[anim_names.a_anim_crouching_stand])

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

                    if not player.get_python_tag("first_attack"):
                        player.set_python_tag("first_attack", True)

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

    def player_mount_helper_task(self, child, player,  horse_np, saddle_pos, task):
        if child and player:
            if self.base.game_instance['player_ref'].get_python_tag("is_on_horse"):
                child.set_x(saddle_pos[0])
                child.set_y(saddle_pos[1])
                # child.set_h(horse_np.get_h())

                if not self.base.game_instance['is_aiming']:
                    self.base.camera.set_y(-5.5)

                self.base.camera.set_z(0.5)
            else:
                self.base.camera.set_y(self.base.game_instance["mouse_y_cam"])
                self.base.camera.set_z(0)
        return task.cont

    def mount_action(self):
        if self.kbd.keymap["use"] and not base.do_key_once["use"]:
            self.state.set_do_once_key("use", True)
            horse_name = base.game_instance['player_using_horse']
            parent = self.base.game_instance['actors_ref'][horse_name]
            child = self.base.game_instance["player_np"]
            player = self.base.game_instance['player_ref']
            if parent and child and not self.base.game_instance['is_aiming']:
                if (self.base.game_instance['player_ref'].get_python_tag("is_on_horse")
                        and parent.get_python_tag("is_mounted")):
                    self.unmount_action()
                else:
                    # with inverted Z -0.5 stands for Up
                    # Our horse (un)mounting animations have been made with imperfect positions,
                    # so, I had to change child positions to get more satisfactory result
                    # with these animations in my game.
                    mounting_pos = Vec3(0.5, -0.16, -0.45)
                    saddle_pos = Vec3(0, -0.32, 0.16)
                    mount_action_seq = player.actor_interval(anim_names.a_anim_horse_mounting,
                                                             playRate=self.base.actor_play_rate)
                    horse_riding_action_seq = player.actor_interval(anim_names.a_anim_horse_rider_idle,
                                                                    playRate=self.base.actor_play_rate)
                    horse_np = self.base.game_instance['actors_np']["{0}:BS".format(horse_name)]

                    taskMgr.add(self.player_mount_helper_task,
                                "player_mount_helper_task",
                                extraArgs=[child, player,  horse_np, saddle_pos],
                                appendTask=True)

                    # child.node().set_kinematic(True)

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

    def unmount_action(self):
        horse_name = base.game_instance['player_using_horse']
        parent = render.find("**/{0}".format(horse_name))
        parent_bs = render.find("**/{0}:BS".format(horse_name))
        child = self.base.game_instance["player_np"]
        player = self.base.game_instance['player_ref']
        if parent and child and not self.base.game_instance['is_aiming']:
            # with inverted Z -0.7 stands for Up
            # Our horse (un)mounting animations have been made with imperfect positions,
            # so, I had to change child positions to get more satisfactory result
            # with these animations in my game.
            unmounting_pos = Vec3(0.5, -0.16, -0.45)
            # Reparent parent/child node back to its BulletCharacterControllerNode
            unmount_action_seq = player.actor_interval(anim_names.a_anim_horse_unmounting,
                                                       playRate=self.base.actor_play_rate)
            horse_near_pos = Vec3(parent_bs.get_x(), parent_bs.get_y(), child.get_z()) + Vec3(1, 0, 0)
            base.game_instance['player_using_horse'] = ''
            horse_np = self.base.game_instance['actors_np']["{0}:BS".format(horse_name)]

            # child.node().set_kinematic(False)

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
