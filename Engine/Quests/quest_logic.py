from direct.interval.FunctionInterval import Func
from direct.interval.MetaInterval import Sequence
from panda3d.core import Vec3


class QuestLogic:
    def __init__(self):
        self.base = base
        self.render = render
        self.actor_geom_pos_z = 0
        self.cam_p = 0

        self.npc_sit_time_start = [18, 1]
        self.npc_sit_time_stop = [18, 15]

        self.npc_rest_time_start = [18, 1]
        self.npc_rest_time_stop = [18, 15]

        # self.npc_rest_time_start = [23, 1]
        # self.npc_rest_time_stop = [6, 15]

        self.current_seq = None

    def set_action_state(self, actor, action, bool_):
        if (actor and action
                and isinstance(action, str)
                and isinstance(bool_, bool)):
            if "Player" in actor.get_name():
                self.base.player_states[action] = bool_
            if "NPC" in actor.get_name():
                actor.get_python_tag("generic_states")[action] = bool_

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

    def play_action_state(self, actor, anim, task):
        if actor and anim and task:
            any_action = actor.get_anim_control(anim)
            any_action_seq = actor.actor_interval(anim, loop=0)

            if any_action.is_playing():
                actor.stop(anim)
                self.set_action_state(actor, "is_busy", False)
            else:
                if task == "loop":
                    Sequence(Func(self.set_action_state, actor, "is_busy", True),
                             any_action_seq).start()
                elif task == "play":
                    Sequence(Func(self.set_action_state, actor, "is_busy", True),
                             any_action_seq).start()

    def _reset_current_sequence(self):
        if self.current_seq:
            self.current_seq = None

    def toggle_sitting_state(self, actor, place, anim, anim_next, task):
        any_action_seq = actor.actor_interval(anim, loop=0)
        any_action_next_seq = actor.actor_interval(anim_next, loop=1)

        txt_cap = render.find("**/txt_sit")

        if (self.base.game_instance["is_player_sitting"]
                and self.base.game_instance["is_indoor"]
                and self.base.player_states["is_busy"]):
            if txt_cap:
                txt_cap.hide()
            if "Player" in actor.get_name():
                self.base.game_instance["is_player_sitting"] = False
                self.base.camera.set_z(0.0)
                self.base.camera.set_y(-1)

                # Reverse play for standing_to_sit animation
                any_action_seq = actor.actor_interval(anim, loop=0, playRate=-1.0)
                Sequence(any_action_seq,
                         Func(self.set_do_once_key, "use", False),
                         Func(self.set_action_state, actor, "is_busy", False)
                         ).start()

        elif (not self.base.game_instance["is_player_sitting"]
              and self.base.game_instance["is_indoor"]
              and not self.base.player_states["is_busy"]):
            if "Player" in actor.get_name():
                self.base.game_instance["is_player_sitting"] = True
                self.base.camera.set_z(-0.5)
                self.base.camera.set_y(-3.0)
                actor_name = actor.get_name()
                actor_bs = self.base.get_actor_bullet_shape_node(asset=actor_name, type="Player")
                heading = place.get_h() - 180
                actor_bs.set_h(heading)
                place_pos = place.get_pos()
                actor_bs.set_x(place_pos[0])
                actor_bs.set_y(place_pos[1])

                if task == "loop":
                    Sequence(any_action_seq,
                             Func(self.set_action_state, actor, "is_busy", True),
                             any_action_next_seq,
                             ).start()
                elif task == "play":
                    Sequence(any_action_seq,
                             Func(self.set_action_state, actor, "is_busy", True)).start()

    def toggle_npc_sitting_state(self, actor, place, anim, anim_next, task):
        if actor.get_python_tag('generic_states')["is_sitting"]:
            hour, minutes = self.base.game_instance["world_time"].split(":")
            if (int(hour) == self.npc_sit_time_stop[0]
                    and int(minutes) == self.npc_sit_time_stop[1]):
                if "NPC" in actor.get_name():
                    actor.set_z(self.actor_geom_pos_z)
                    actor_name = actor.get_name()
                    actor_bs = self.base.get_actor_bullet_shape_node(asset=actor_name, type="NPC")
                    # Reverse play for standing_to_sit animation
                    any_action_seq = actor.actor_interval(anim, loop=0, playRate=-1.0)

                    if self.current_seq:
                        self.current_seq = Sequence(Func(actor_bs.set_z, 0),
                                                    any_action_seq,
                                                    Func(self.set_action_state, actor, "is_laying", False),
                                                    Func(self._reset_current_sequence)
                                                    )
                    if self.current_seq and not self.current_seq.is_playing():
                        self.current_seq.start()

        if not actor.get_python_tag('generic_states')["is_sitting"]:
            any_action_seq = actor.actor_interval(anim, loop=0)
            hour, minutes = self.base.game_instance["world_time"].split(":")
            if (int(hour) == self.npc_sit_time_start[0]
                    and int(minutes) >= self.npc_sit_time_start[1]
                    and int(minutes) < self.npc_sit_time_stop[1]):
                if "NPC" in actor.get_name():
                    actor_name = actor.get_name()
                    actor_bs = self.base.get_actor_bullet_shape_node(asset=actor_name, type="NPC")
                    actor.set_z(-0.75)
                    heading = place.get_h() - 170
                    pos = actor_bs.get_pos() - Vec3(-0.3, -0.1, 0)
                    actor_bs.set_h(heading)
                    actor_bs.set_pos(pos)
                    place_pos = place.get_pos()
                    actor_bs.set_x(place_pos[0])
                    actor_bs.set_y(place_pos[1])

                    if task == "loop":
                        if not self.current_seq:
                            self.current_seq = Sequence(any_action_seq,
                                                        Func(self.set_action_state, actor, "is_laying", True),
                                                        Func(self._reset_current_sequence)
                                                        )
                        if self.current_seq and not self.current_seq.is_playing():
                            self.current_seq.start()
                    elif task == "play":
                        if not self.current_seq:
                            self.current_seq = Sequence(any_action_seq)
                        if self.current_seq and not self.current_seq.is_playing():
                            self.current_seq.start()

        if actor.get_python_tag('generic_states')["is_sitting"]:
            any_action_seq = actor.actor_interval(anim, loop=0)
            any_action_next_seq = actor.actor_interval(anim_next, loop=1)
            hour, minutes = self.base.game_instance["world_time"].split(":")
            if (int(hour) == self.npc_sit_time_start[0]
                    and int(minutes) >= self.npc_sit_time_start[1]):
                if "NPC" in actor.get_name():
                    actor_name = actor.get_name()
                    actor_bs = self.base.get_actor_bullet_shape_node(asset=actor_name, type="NPC")
                    heading = place.get_h() - 170
                    pos = actor_bs.get_pos() - Vec3(-0.3, -0.1, 0)
                    actor_bs.set_h(heading)
                    actor_bs.set_pos(pos)
                    place_pos = place.get_pos()
                    actor_bs.set_x(place_pos[0])
                    actor_bs.set_y(place_pos[1])

                    if task == "loop":
                        if not self.current_seq:
                            self.current_seq = Sequence(any_action_next_seq)
                        if self.current_seq and not self.current_seq.is_playing():
                            self.current_seq.start()
                    elif task == "play":
                        if not self.current_seq:
                            self.current_seq = Sequence(any_action_seq)
                        if self.current_seq and not self.current_seq.is_playing():
                            self.current_seq.start()

    def toggle_laying_state(self, actor, place, anim, anim_next, task):
        any_action_seq = actor.actor_interval(anim, loop=0)
        any_action_next_seq = actor.actor_interval(anim_next, loop=1)

        txt_cap = render.find("**/txt_rest")

        if (self.base.game_instance["is_player_laying"]
                and self.base.game_instance["is_indoor"]
                and self.base.player_states["is_busy"]):
            if txt_cap:
                txt_cap.show()
            # Stop having rest
            if "Player" in actor.get_name():
                self.base.game_instance["is_player_laying"] = False
                self.base.camera.set_z(0.0)
                self.base.camera.set_p(self.cam_p)
                self.base.camera.set_y(-1)
                actor.set_z(self.actor_geom_pos_z)
                actor_name = actor.get_name()
                actor_bs = self.base.get_actor_bullet_shape_node(asset=actor_name, type="Player")
                # Reverse play for standing_to_sit animation
                any_action_seq = actor.actor_interval(anim, loop=0, playRate=-1.0)

                Sequence(Func(actor_bs.set_z, 0),
                         any_action_seq,
                         Func(self.set_do_once_key, "use", False),
                         Func(self.set_action_state, actor, "is_busy", False)).start()

        if (not self.base.game_instance["is_player_laying"]
                and self.base.game_instance["is_indoor"]
                and not self.base.player_states["is_busy"]):
            if txt_cap:
                txt_cap.hide()
            # Start having rest
            if "Player" in actor.get_name():
                self.base.game_instance["is_player_laying"] = True
                self.base.camera.set_z(-1.3)
                self.base.camera.set_y(-4.2)
                self.base.camera.set_h(0)
                self.cam_p = self.base.camera.get_p()
                self.base.camera.set_p(10)
                actor_name = actor.get_name()
                actor_bs = self.base.get_actor_bullet_shape_node(asset=actor_name, type="Player")
                self.actor_geom_pos_z = actor.get_z()
                actor.set_z(-0.75)
                heading = place.get_h() - 170
                pos = actor_bs.get_pos() - Vec3(-0.3, -0.1, 0)
                actor_bs.set_h(heading)
                actor_bs.set_pos(pos)
                place_pos = place.get_pos()
                actor_bs.set_x(place_pos[0])
                actor_bs.set_y(place_pos[1])

                if task == "loop":
                    Sequence(any_action_seq,
                             Func(self.set_action_state, actor, "is_busy", True),
                             any_action_next_seq,
                             ).start()
                elif task == "play":
                    Sequence(any_action_seq,
                             Func(self.set_action_state, actor, "is_busy", True)).start()

    def toggle_npc_laying_state(self, actor, place, anim, anim_next, task):
        if actor.get_python_tag('generic_states')["is_laying"]:
            hour, minutes = self.base.game_instance["world_time"].split(":")
            if (int(hour) == self.npc_rest_time_stop[0]
                    and int(minutes) == self.npc_rest_time_stop[1]):
                if "NPC" in actor.get_name():
                    actor.set_z(self.actor_geom_pos_z)
                    actor_name = actor.get_name()
                    actor_bs = self.base.get_actor_bullet_shape_node(asset=actor_name, type="NPC")
                    # Reverse play for standing_to_sit animation
                    any_action_seq = actor.actor_interval(anim, loop=0, playRate=-1.0)

                    if self.current_seq:
                        self.current_seq = Sequence(Func(actor_bs.set_z, 0),
                                                    any_action_seq,
                                                    Func(self.set_action_state, actor, "is_laying", False),
                                                    Func(self._reset_current_sequence)
                                                    )
                    if self.current_seq and not self.current_seq.is_playing():
                        self.current_seq.start()

        if not actor.get_python_tag('generic_states')["is_laying"]:
            any_action_seq = actor.actor_interval(anim, loop=0)
            hour, minutes = self.base.game_instance["world_time"].split(":")
            if (int(hour) == self.npc_rest_time_start[0]
                    and int(minutes) >= self.npc_rest_time_start[1]
                    and int(minutes) < self.npc_rest_time_stop[1]):
                if "NPC" in actor.get_name():
                    actor_name = actor.get_name()
                    actor_bs = self.base.get_actor_bullet_shape_node(asset=actor_name, type="NPC")
                    actor.set_z(-0.75)
                    heading = place.get_h() - 170
                    pos = actor_bs.get_pos() - Vec3(-0.3, -0.1, 0)
                    actor_bs.set_h(heading)
                    actor_bs.set_pos(pos)
                    place_pos = place.get_pos()
                    actor_bs.set_x(place_pos[0])
                    actor_bs.set_y(place_pos[1])

                    if task == "loop":
                        if not self.current_seq:
                            self.current_seq = Sequence(any_action_seq,
                                                        Func(self.set_action_state, actor, "is_laying", True),
                                                        Func(self._reset_current_sequence)
                                                        )
                        if self.current_seq and not self.current_seq.is_playing():
                            self.current_seq.start()
                    elif task == "play":
                        if not self.current_seq:
                            self.current_seq = Sequence(any_action_seq)
                        if self.current_seq and not self.current_seq.is_playing():
                            self.current_seq.start()

        if actor.get_python_tag('generic_states')["is_laying"]:
            any_action_seq = actor.actor_interval(anim, loop=0)
            any_action_next_seq = actor.actor_interval(anim_next, loop=1)
            hour, minutes = self.base.game_instance["world_time"].split(":")
            if (int(hour) == self.npc_rest_time_start[0]
                    and int(minutes) >= self.npc_rest_time_start[1]):
                if "NPC" in actor.get_name():
                    actor_name = actor.get_name()
                    actor_bs = self.base.get_actor_bullet_shape_node(asset=actor_name, type="NPC")
                    heading = place.get_h() - 170
                    pos = actor_bs.get_pos() - Vec3(-0.3, -0.1, 0)
                    actor_bs.set_h(heading)
                    actor_bs.set_pos(pos)
                    place_pos = place.get_pos()
                    actor_bs.set_x(place_pos[0])
                    actor_bs.set_y(place_pos[1])

                    if task == "loop":
                        if not self.current_seq:
                            self.current_seq = Sequence(any_action_next_seq)
                        if self.current_seq and not self.current_seq.is_playing():
                            self.current_seq.start()
                    elif task == "play":
                        if not self.current_seq:
                            self.current_seq = Sequence(any_action_seq)
                        if self.current_seq and not self.current_seq.is_playing():
                            self.current_seq.start()
