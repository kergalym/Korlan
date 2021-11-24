from direct.task.TaskManagerGlobal import taskMgr
from Engine.Items.items import Items
from Engine.Actors.Player.state import PlayerState
from direct.interval.IntervalGlobal import *
from Settings.UI.hud_ui import HUD


class SeqWrappers:
    def __init__(self):
        self.game_settings = base.game_settings
        self.base = base
        self.render = render
        self.walking_forward_action = "Walking"
        self.run_forward_action = "Running"
        self.crouch_walking_forward_action = 'crouch_walking_forward'
        self.crouched_to_standing_action = "crouched_to_standing"
        self.standing_to_crouch_action = "standing_to_crouch"
        self.hud = HUD()
        self.items = Items()
        self.state = PlayerState()

    """ Play animation after action """
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

    def seq_crouch_move_wrapper(self, player, anims, state):
        if player and anims and isinstance(state, str):
            crouch_walking_forward_seq = player.get_anim_control(anims[self.crouch_walking_forward_action])
            if state == 'loop' and crouch_walking_forward_seq.is_playing() is False:
                player.loop(anims[self.crouch_walking_forward_action])
                player.set_play_rate(self.base.actor_play_rate,
                                     anims[self.crouch_walking_forward_action])
            elif state == 'stop' and crouch_walking_forward_seq.is_playing():
                player.stop()
                player.pose(anims[self.crouch_walking_forward_action], 0)

    """ Sets current item after action """
    def seq_use_item_wrapper_task(self, player, anims, joint, task):
        if player and anims and joint:
            if player.get_current_frame(anims["PickingUp"]) == 69:
                char_joint = player.get_part_bundle("modelRoot").get_name()
                joint = "{0}:{1}".format(char_joint, joint)
                self.items.item_selector(actor=player,
                                         joint=joint)
                return task.done
        return task.cont

    def seq_use_item_wrapper(self, player, anims, joint):
        if player and anims and joint and base.player_states['is_using']:
            # Do task every frame until we get a respective frame
            taskMgr.add(self.seq_use_item_wrapper_task,
                        "seq_use_item_wrapper_task",
                        extraArgs=[player, anims, joint],
                        appendTask=True)

    """ Sets current player position after action """

    def seq_set_player_pos_wrapper(self, player, pos_y):
        if (player and pos_y
                and isinstance(pos_y, float)):
            player = self.base.get_actor_bullet_shape_node(asset=player.get_name(), type="Player")
            if player:
                player.set_y(player, pos_y)

    """ Helps to coordinate the bullet shape with player actions """
    def player_bullet_jump_helper(self):
        if hasattr(base, "bullet_char_contr_node"):
            if base.bullet_char_contr_node:
                # TODO: Implement player_bullet_jump_helper
                if not base.bullet_char_contr_node.is_on_ground():
                    base.bullet_char_contr_node.set_max_jump_height(2.0)
                    base.bullet_char_contr_node.set_jump_speed(self.base.actor_play_rate)

    def player_bullet_crouch_helper(self):
        if hasattr(base, "bullet_char_contr_node"):
            if base.bullet_char_contr_node:
                # TODO: Implement player_bullet_crouch_helper
                pass
                # size = 0.6
                # base.bullet_char_contr_node.get_shape().setLocalScale(Vec3(1, 1, size))

    def seq_movement(self, player, anims):
        if player and anims:
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
                    and base.player_states['is_idle'] is False):
                Sequence(Func(self.seq_crouch_move_wrapper, player, anims, 'loop')
                         ).start()

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

    def seq_run(self, player, anims):
        if player and anims:
            if (base.player_states['is_moving'] is False
                    and base.player_states['is_attacked'] is False
                    and base.player_states['is_busy'] is False
                    and base.player_states['is_crouch_moving'] is False
                    and base.player_states["is_running"] is False
                    and base.player_states['is_idle']):
                Sequence(Parallel(Func(self.seq_run_wrapper, player, anims, 'loop'),
                                  Func(self.state.set_action_state, "is_running", True)),
                         ).start()
            if (base.player_states['is_moving'] is False
                    and base.player_states['is_attacked'] is False
                    and base.player_states['is_busy'] is False
                    and base.player_states["is_crouch_moving"] is False
                    and base.player_states['is_running']
                    and base.player_states['is_idle'] is False):
                Sequence(Func(self.seq_run_wrapper, player, anims, 'loop')
                         ).start()

            if (base.player_states['is_running']
                    and base.player_states['is_attacked'] is False
                    and base.player_states['is_busy'] is False
                    and base.player_states["is_moving"] is False
                    and base.player_states['is_crouch_moving'] is False):
                Sequence(Func(self.seq_run_wrapper, player, anims, 'stop'),
                         Func(self.state.set_action_state, "is_running", False)
                         ).start()
            if (base.player_states['is_moving'] is False
                    and base.player_states['is_attacked'] is False
                    and base.player_states['is_busy'] is False
                    and base.player_states["is_crouch_moving"] is False
                    and base.player_states['is_running']):
                Sequence(Func(self.seq_run_wrapper, player, anims, 'stop')).start()

    def seq_crouch(self, player, anims):
        if player and anims:
            crouched_to_standing = player.get_anim_control(anims[self.crouched_to_standing_action])
            standing_to_crouch = player.get_anim_control(anims[self.standing_to_crouch_action])

            if (standing_to_crouch.is_playing() is False
                    and base.player_states['is_idle'] is False
                    and base.player_states['is_crouching'] is False
                    and base.player_states['is_crouch_moving'] is False):
                # TODO: Use blending for smooth transition between animations
                # Do an animation sequence if player is crouched.
                stand_to_crouch_seq = player.actor_interval(anims[self.standing_to_crouch_action],
                                                            playRate=self.base.actor_play_rate)

                Sequence(Parallel(stand_to_crouch_seq,
                                  Func(self.player_bullet_crouch_helper),
                                  Func(self.state.set_action_state, "is_crouching", True)),
                         Func(self.state.set_action_state_crouched, "is_crouch_moving", True)
                         ).start()

            elif (crouched_to_standing.is_playing() is False
                  and base.player_states['is_idle'] is False
                  and base.player_states['is_crouching'] is False
                  and base.player_states['is_crouch_moving']):
                any_action_seq = player.actor_interval(anims[self.crouched_to_standing_action],
                                                       playRate=self.base.actor_play_rate)
                Sequence(any_action_seq,
                         Func(self.state.set_action_state_crouched, "is_crouch_moving", False)
                         ).start()

    def seq_jump(self, player, anims, action):
        if player and anims and action:
            crouched_to_standing = player.get_anim_control(anims[self.crouched_to_standing_action])
            if (base.player_states['is_jumping'] is False
                    and crouched_to_standing.is_playing() is False
                    and base.player_states['is_crouching'] is True):
                # TODO: Use blending for smooth transition between animations
                # Do an animation sequence if player is crouched.
                crouch_to_stand_seq = player.actor_interval(anims[self.crouched_to_standing_action],
                                                            playRate=self.base.actor_play_rate)
                any_action_seq = player.actor_interval(anims[action],
                                                       playRate=self.base.actor_play_rate)

                Sequence(crouch_to_stand_seq,
                         Parallel(any_action_seq,
                                  Func(self.state.set_action_state, "is_jumping", True)),
                         Func(self.state.set_action_state, "is_jumping", False)
                         ).start()

            elif (base.player_states['is_jumping'] is False
                  and crouched_to_standing.is_playing() is False
                  and base.player_states['is_crouching'] is False):
                # Do an animation sequence if player is stayed.
                any_action_seq = player.actor_interval(anims[action],
                                                       playRate=self.base.actor_play_rate)
                Sequence(Parallel(any_action_seq,
                                  Func(self.player_bullet_jump_helper),
                                  Func(self.state.set_action_state, "is_jumping", True)),
                         Func(self.state.set_action_state, "is_jumping", False)
                         ).start()

    def seq_use(self, player, anims, action):
        if player and anims and action:
            crouched_to_standing = player.get_anim_control(anims[self.crouched_to_standing_action])
            if (hasattr(base, "is_item_close_to_use")
                    and base.is_item_close_to_use is True
                    and hasattr(base, "is_item_in_use")
                    and base.is_item_in_use is False):
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
                             Parallel(any_action_seq,
                                      Func(self.state.set_action_state, "is_using", True),
                                      Func(self.seq_use_item_wrapper, player, anims, "RightHand")),
                             Func(self.state.set_action_state, "is_using", False)
                             ).start()

                elif (base.player_states['is_using'] is False
                      and crouched_to_standing.is_playing() is False
                      and base.player_states['is_crouching'] is False):
                    any_action_seq = player.actor_interval(anims[action],
                                                           playRate=self.base.actor_play_rate)
                    Sequence(Parallel(any_action_seq,
                                      Func(self.state.set_action_state, "is_using", True),
                                      Func(self.seq_use_item_wrapper, player, anims, "RightHand")),
                             Func(self.state.set_action_state, "is_using", False)
                             ).start()

            elif (hasattr(base, "is_item_close_to_use")
                  and base.is_item_close_to_use is False
                  and hasattr(base, "is_item_in_use")
                  and base.is_item_in_use is True):
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
                             Parallel(any_action_seq,
                                      Func(self.state.set_action_state, "is_using", True),
                                      Func(self.seq_use_item_wrapper, player, anims, "RightHand")),
                             Func(self.state.set_action_state, "is_using", False)
                             ).start()

                elif (base.player_states['is_using'] is False
                      and crouched_to_standing.is_playing() is False
                      and base.player_states['is_crouching'] is False):
                    any_action_seq = player.actor_interval(anims[action],
                                                           playRate=self.base.actor_play_rate)
                    Sequence(Parallel(any_action_seq,
                                      Func(self.state.set_action_state, "is_using", True),
                                      Func(self.seq_use_item_wrapper, player, anims, "RightHand")),
                             Func(self.state.set_action_state, "is_using", False)
                             ).start()

    def seq_hit(self, player, anims, action):
        if player and anims and action:
            crouched_to_standing = player.get_anim_control(anims[self.crouched_to_standing_action])
            if (base.player_states['is_hitting'] is False
                    and crouched_to_standing.is_playing() is False
                    and base.player_states['is_crouching'] is True):
                # TODO: Use blending for smooth transition between animations
                # Do an animation sequence if player is crouched.
                crouch_to_stand_seq = player.actor_interval(anims[self.crouched_to_standing_action],
                                                            playRate=self.base.actor_play_rate)
                any_action_seq = player.actor_interval(anims[action],
                                                       playRate=self.base.actor_play_rate)
                Sequence(crouch_to_stand_seq,
                         Parallel(any_action_seq,
                                  Func(self.state.set_action_state, "is_hitting", True)),
                         Func(self.state.set_action_state, "is_hitting", False)
                         ).start()

            elif (base.player_states['is_hitting'] is False
                  and crouched_to_standing.is_playing() is False
                  and base.player_states['is_crouching'] is False):
                any_action_seq = player.actor_interval(anims[action],
                                                       playRate=self.base.actor_play_rate)
                Sequence(Parallel(any_action_seq,
                                  Func(self.state.set_action_state, "is_hitting", True)),
                         Func(self.state.set_action_state, "is_hitting", False)
                         ).start()

    def seq_h_kick(self, player, anims, action):
        if player and anims and action:
            crouched_to_standing = player.get_anim_control(anims[self.crouched_to_standing_action])
            if (base.player_states['is_h_kicking'] is False
                    and crouched_to_standing.is_playing() is False
                    and base.player_states['is_crouching'] is True):
                # TODO: Use blending for smooth transition between animations
                # Do an animation sequence if player is crouched.
                crouch_to_stand_seq = player.actor_interval(anims[self.crouched_to_standing_action],
                                                            playRate=self.base.actor_play_rate)
                any_action_seq = player.actor_interval(anims[action],
                                                       playRate=self.base.actor_play_rate)

                Sequence(crouch_to_stand_seq,
                         Parallel(any_action_seq,
                                  Func(self.state.set_action_state, "is_h_kicking", True)),
                         Func(self.seq_set_player_pos_wrapper, player, -1.5),
                         Func(self.state.set_action_state, "is_h_kicking", False)
                         ).start()

            elif (base.player_states['is_h_kicking'] is False
                  and crouched_to_standing.is_playing() is False
                  and base.player_states['is_crouching'] is False):
                any_action_seq = player.actor_interval(anims[action],
                                                       playRate=self.base.actor_play_rate)

                Sequence(Parallel(any_action_seq,
                                  Func(self.state.set_action_state, "is_h_kicking", True)),
                         Func(self.seq_set_player_pos_wrapper, player, -1.5),
                         Func(self.state.set_action_state, "is_h_kicking", False)
                         ).start()

    def seq_f_kick(self, player, anims, action):
        if player and anims and action:
            crouched_to_standing = player.get_anim_control(anims[self.crouched_to_standing_action])
            if (base.player_states['is_f_kicking'] is False
                    and crouched_to_standing.is_playing() is False
                    and base.player_states['is_crouching'] is True):
                # TODO: Use blending for smooth transition between animations
                # Do an animation sequence if player is crouched.
                crouch_to_stand_seq = player.actor_interval(anims[self.crouched_to_standing_action],
                                                            playRate=self.base.actor_play_rate)
                any_action_seq = player.actor_interval(anims[action],
                                                       playRate=self.base.actor_play_rate)
                Sequence(crouch_to_stand_seq,
                         Parallel(any_action_seq,
                                  Func(self.state.set_action_state, "is_f_kicking", True)),
                         Func(self.state.set_action_state, "is_f_kicking", False)
                         ).start()

            elif (base.player_states['is_f_kicking'] is False
                  and crouched_to_standing.is_playing() is False
                  and base.player_states['is_crouching'] is False):
                any_action_seq = player.actor_interval(anims[action],
                                                       playRate=self.base.actor_play_rate)
                Sequence(Parallel(any_action_seq,
                                  Func(self.state.set_action_state, "is_f_kicking", True)),
                         Func(self.state.set_action_state, "is_f_kicking", False)
                         ).start()

    def seq_block(self, player, anims, action):
        if player and anims and action:
            crouched_to_standing = player.get_anim_control(anims[self.crouched_to_standing_action])
            if (base.player_states['is_blocking'] is False
                    and crouched_to_standing.is_playing() is False
                    and base.player_states['is_crouching'] is True):
                # TODO: Use blending for smooth transition between animations
                # Do an animation sequence if player is crouched.
                crouch_to_stand_seq = player.actor_interval(anims[self.crouched_to_standing_action],
                                                            playRate=self.base.actor_play_rate)
                any_action_seq = player.actor_interval(anims[action],
                                                       playRate=self.base.actor_play_rate)
                Sequence(crouch_to_stand_seq,
                         Parallel(any_action_seq,
                                  Func(self.state.set_action_state, "is_blocking", True)),
                         Func(self.state.set_action_state, "is_blocking", False)
                         ).start()

            elif (base.player_states['is_blocking'] is False
                  and crouched_to_standing.is_playing() is False
                  and base.player_states['is_crouching'] is False):
                any_action_seq = player.actor_interval(anims[action],
                                                       playRate=self.base.actor_play_rate)
                Sequence(Parallel(any_action_seq,
                                  Func(self.state.set_action_state, "is_blocking", True)),
                         Func(self.state.set_action_state, "is_blocking", False)
                         ).start()

    def seq_sword(self, player, anims, action):
        if player and anims and action:
            crouched_to_standing = player.get_anim_control(anims[self.crouched_to_standing_action])
            # TODO: Use blending for smooth transition between animations

            if (base.player_states['has_sword'] is False
                    and crouched_to_standing.is_playing() is False
                    and base.player_states['is_crouching'] is True):
                self.hud.toggle_weapon_state(weapon_name="sword")
                # Do an animation sequence if player is crouched.
                crouch_to_stand_seq = player.actor_interval(anims[self.crouched_to_standing_action],
                                                            playRate=self.base.actor_play_rate)
                any_action_seq = player.actor_interval(anims[action],
                                                       playRate=self.base.actor_play_rate)
                Sequence(crouch_to_stand_seq,
                         Func(self.state.get_weapon, player, "sword", "Korlan:LeftHand"),
                         Func(self.state.set_action_state, "has_sword", True),
                         Parallel(any_action_seq, Func(self.state.set_action_state, "is_using", True)),
                         Func(self.state.set_action_state, "is_using", False),
                         ).start()

            elif (base.player_states['has_sword'] is False
                  and crouched_to_standing.is_playing() is False
                  and base.player_states['is_crouching'] is False):
                self.hud.toggle_weapon_state(weapon_name="sword")
                any_action_seq = player.actor_interval(anims[action],
                                                       playRate=self.base.actor_play_rate)
                Sequence(Func(self.state.get_weapon, player, "sword", "Korlan:LeftHand"),
                         Func(self.state.set_action_state, "has_sword", True),
                         Parallel(any_action_seq, Func(self.state.set_action_state, "is_using", True)),
                         Func(self.state.set_action_state, "is_using", False),
                         ).start()

            elif (base.player_states['has_sword']
                  and crouched_to_standing.is_playing() is False
                  and base.player_states['is_crouching'] is True):
                self.hud.toggle_weapon_state(weapon_name="hands")
                # Do an animation sequence if player is crouched.
                crouch_to_stand_seq = player.actor_interval(anims[self.crouched_to_standing_action],
                                                            playRate=self.base.actor_play_rate)
                any_action_seq = player.actor_interval(anims[action],
                                                       playRate=-self.base.actor_play_rate)
                Sequence(crouch_to_stand_seq,
                         Parallel(any_action_seq,
                                  Func(self.state.set_action_state, "is_using", True)),
                         Func(self.state.set_action_state, "is_using", False),
                         Func(self.state.remove_weapon, player, "sword", "Korlan:Spine1"),
                         Func(self.state.set_action_state, "has_sword", False),
                         ).start()

            elif (base.player_states['has_sword']
                  and crouched_to_standing.is_playing() is False
                  and base.player_states['is_crouching'] is False):
                self.hud.toggle_weapon_state(weapon_name="hands")
                any_action_seq = player.actor_interval(anims[action],
                                                       playRate=-self.base.actor_play_rate)
                Sequence(Parallel(any_action_seq,
                                  Func(self.state.set_action_state, "is_using", True)),
                         Func(self.state.set_action_state, "is_using", False),
                         Func(self.state.remove_weapon, player, "sword", "Korlan:Spine1"),
                         Func(self.state.set_action_state, "has_sword", False),
                         ).start()

    def seq_bow(self, player, anims, action):
        if player and anims and action:
            crouched_to_standing = player.get_anim_control(anims[self.crouched_to_standing_action])
            # TODO: Use blending for smooth transition between animations

            if (base.player_states['has_bow'] is False
                    and crouched_to_standing.is_playing() is False
                    and base.player_states['is_crouching'] is True):
                self.hud.toggle_weapon_state(weapon_name="bow")
                # Do an animation sequence if player is crouched.
                crouch_to_stand_seq = player.actor_interval(anims[self.crouched_to_standing_action],
                                                            playRate=self.base.actor_play_rate)
                any_action_seq = player.actor_interval(anims[action],
                                                       playRate=self.base.actor_play_rate)
                Sequence(crouch_to_stand_seq,
                         Func(self.state.get_weapon, player, "bow_kazakh", "Korlan:RightHand"),
                         Func(self.state.set_action_state, "has_bow", True),
                         Parallel(any_action_seq,
                                  Func(self.state.set_action_state, "is_using", True)),
                         Func(self.state.set_action_state, "is_using", False),
                         ).start()

            elif (base.player_states['has_bow'] is False
                  and crouched_to_standing.is_playing() is False
                  and base.player_states['is_crouching'] is False):
                self.hud.toggle_weapon_state(weapon_name="bow")
                any_action_seq = player.actor_interval(anims[action],
                                                       playRate=self.base.actor_play_rate)
                Sequence(Func(self.state.get_weapon, player, "bow_kazakh", "Korlan:RightHand"),
                         Func(self.state.set_action_state, "has_bow", True),
                         Parallel(any_action_seq,
                                  Func(self.state.set_action_state, "is_using", True)),
                         Func(self.state.set_action_state, "is_using", False),
                         ).start()

            elif (base.player_states['has_bow']
                  and crouched_to_standing.is_playing() is False
                  and base.player_states['is_crouching'] is True):
                self.hud.toggle_weapon_state(weapon_name="hands")
                # Do an animation sequence if player is crouched.
                crouch_to_stand_seq = player.actor_interval(anims[self.crouched_to_standing_action],
                                                            playRate=self.base.actor_play_rate)
                any_action_seq = player.actor_interval(anims[action],
                                                       playRate=self.base.actor_play_rate)
                Sequence(crouch_to_stand_seq,
                         Parallel(any_action_seq,
                                  Func(self.state.set_action_state, "is_using", True)),
                         Func(self.state.set_action_state, "is_using", False),
                         Func(self.state.remove_weapon, player, "bow_kazakh", "Korlan:Spine1"),
                         Func(self.state.set_action_state, "has_bow", False)
                         ).start()

            elif (base.player_states['has_bow']
                  and crouched_to_standing.is_playing() is False
                  and base.player_states['is_crouching'] is False):
                self.hud.toggle_weapon_state(weapon_name="hands")
                any_action_seq = player.actor_interval(anims[action],
                                                       playRate=self.base.actor_play_rate)
                Sequence(Parallel(any_action_seq,
                                  Func(self.state.set_action_state, "is_using", True)),
                         Func(self.state.set_action_state, "is_using", False),
                         Func(self.state.remove_weapon, player, "bow_kazakh", "Korlan:Spine1"),
                         Func(self.state.set_action_state, "has_bow", False)
                         ).start()

    def seq_tengri(self, player, anims, action):
        if player and anims and action:
            crouched_to_standing = player.get_anim_control(anims[self.crouched_to_standing_action])
            if (base.player_states['has_tengri'] is False
                    and crouched_to_standing.is_playing() is False
                    and base.player_states['is_crouching'] is True):
                # TODO: Use blending for smooth transition between animations
                # Do an animation sequence if player is crouched.
                crouch_to_stand_seq = player.actor_interval(anims[self.crouched_to_standing_action],
                                                            playRate=self.base.actor_play_rate)
                any_action_seq = player.actor_interval(anims[action],
                                                       playRate=self.base.actor_play_rate)
                Sequence(crouch_to_stand_seq,
                         Parallel(any_action_seq,
                                  Func(self.state.set_action_state, "has_tengri", True)),
                         Func(self.state.set_action_state, "has_tengri", False)
                         ).start()

            elif (base.player_states['has_tengri'] is False
                  and crouched_to_standing.is_playing() is False
                  and base.player_states['is_crouching'] is False):
                any_action_seq = player.actor_interval(anims[action],
                                                       playRate=self.base.actor_play_rate)
                Sequence(Parallel(any_action_seq,
                                  Func(self.state.set_action_state, "has_tengri", True)),
                         Func(self.state.set_action_state, "has_tengri", False)
                         ).start()

    def seq_umai(self, player, anims, action):
        if player and anims and action:
            crouched_to_standing = player.get_anim_control(anims[self.crouched_to_standing_action])
            if (base.player_states['has_umai'] is False
                    and crouched_to_standing.is_playing() is False
                    and base.player_states['is_crouching'] is True):
                # TODO: Use blending for smooth transition between animations
                # Do an animation sequence if player is crouched.
                crouch_to_stand_seq = player.actor_interval(anims[self.crouched_to_standing_action],
                                                            playRate=self.base.actor_play_rate)
                any_action_seq = player.actor_interval(anims[action],
                                                       playRate=self.base.actor_play_rate)
                Sequence(crouch_to_stand_seq,
                         Parallel(any_action_seq,
                                  Func(self.state.set_action_state, "has_umai", True)),
                         Func(self.state.set_action_state, "has_umai", False)
                         ).start()

            elif (base.player_states['has_umai'] is False
                  and crouched_to_standing.is_playing() is False
                  and base.player_states['is_crouching'] is False):
                any_action_seq = player.actor_interval(anims[action],
                                                       playRate=self.base.actor_play_rate)
                Sequence(Parallel(any_action_seq,
                                  Func(self.state.set_action_state, "has_umai", True)),
                         Func(self.state.set_action_state, "has_umai", False)
                         ).start()
