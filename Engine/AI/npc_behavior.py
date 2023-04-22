from Engine.AI.npc_directives import NpcDirectives


class NpcBehavior:
    def __init__(self):
        self.base = base
        # Keep this class instance for further usage in NpcBehavior class only
        self.npc_controller = self.base.game_instance['npc_controller_cls']
        self._directive_is_executing = False
        self.npc_directives = NpcDirectives()

    def npc_generic_logic(self, actor, player, request, passive, task):
        if self.base.game_instance['menu_mode']:
            return task.done

        if (actor and player and request
                and isinstance(passive, bool)):

            if actor.get_python_tag("generic_states")['is_alive']:
                actor_name = actor.get_name()

                if not passive:
                    if (not actor.get_python_tag("generic_states")['is_sitting']
                            and not actor.get_python_tag("generic_states")['is_laying']):
                        if (self.base.game_instance["world_time"]
                                and self.base.game_instance["sit_time_start"]):
                            hour, minutes = self.base.game_instance["world_time"].split(":")
                            if (int(hour) == self.base.game_instance["sit_time_start"][0]
                                    and int(minutes) >= self.base.game_instance["sit_time_start"][1]
                                    and int(minutes) < self.base.game_instance["sit_time_stop"][1]):

                                if not self._directive_is_executing:
                                    self._directive_is_executing = True

                                # Get required data about directives
                                # 0 yurt
                                # 1 quest_empty_campfire
                                # 2 quest_empty_rest_place
                                # 3 quest_empty_hearth
                                # 4 quest_empty_spring_water
                                # 5 round_table
                                self.npc_directives.work_with_indoor_directives_queue(actor=actor, num=1,
                                                                                      request=request)
                                # self._work_with_outdoor_directive(actor=actor, target="yurt", request=request)
                            else:
                                if (int(hour) == self.base.game_instance["sit_time_stop"][0]
                                        and int(minutes) == self.base.game_instance["sit_time_stop"][1]):
                                    if self._directive_is_executing:
                                        self._directive_is_executing = False

                    if (not actor.get_python_tag("generic_states")['is_sitting']
                            and not actor.get_python_tag("generic_states")['is_laying']):
                        if (self.base.game_instance["world_time"]
                                and self.base.game_instance["rest_time_start"]):
                            hour, minutes = self.base.game_instance["world_time"].split(":")
                            if (int(hour) == self.base.game_instance["rest_time_start"][0]
                                    and int(minutes) >= self.base.game_instance["rest_time_start"][1]
                                    and int(minutes) < self.base.game_instance["rest_time_stop"][1]):

                                if not self._directive_is_executing:
                                    self._directive_is_executing = True

                                # Get required data about directives
                                # 0 yurt
                                # 1 quest_empty_campfire
                                # 2 quest_empty_rest_place
                                # 3 quest_empty_hearth
                                # 4 quest_empty_spring_water
                                # 5 round_table
                                self.npc_directives.work_with_indoor_directives_queue(actor=actor, num=2,
                                                                                      request=request)
                                # self.npc_directives.work_with_outdoor_directive(actor=actor, target="yurt",
                                #                                                  request=request)
                            else:
                                if (int(hour) == self.base.game_instance["rest_time_stop"][0]
                                        and int(minutes) == self.base.game_instance["rest_time_stop"][1]):
                                    if self._directive_is_executing:
                                        self._directive_is_executing = False

                    if not self._directive_is_executing:

                        # Get required data about enemy to deal with it
                        actor_name_bs = "{0}:BS".format(actor_name)
                        actor_npc_rb = self.base.game_instance["actors_np"][actor_name_bs]

                        # No alive enemy around, just stay tuned
                        if not self.npc_controller.get_enemy(actor=actor) and actor_npc_rb:
                            if base.player_states['is_alive']:
                                player_dist = self.npc_controller.get_enemy_distance(actor=actor,
                                                                                     actor_npc_rb=actor_npc_rb,
                                                                                     opponent=player)
                                if not actor.get_python_tag("generic_states")['is_busy']:
                                    self.npc_directives.work_with_player(actor, actor_npc_rb,
                                                                         player,
                                                                         player_dist, request)

                        # Check if we have alive someone around us
                        if self.npc_controller.get_enemy(actor=actor):
                            enemy_npc_ref, enemy_npc_rb = self.npc_controller.get_enemy(actor=actor)

                            if actor_npc_rb and enemy_npc_ref and enemy_npc_rb:
                                player_dist = self.npc_controller.get_enemy_distance(actor=actor,
                                                                                     actor_npc_rb=actor_npc_rb,
                                                                                     opponent=player)
                                enemy_dist = self.npc_controller.get_enemy_distance(actor=actor,
                                                                                    actor_npc_rb=actor_npc_rb,
                                                                                    opponent=enemy_npc_rb)
                                hitbox_dist = actor.get_python_tag("enemy_hitbox_distance")

                                # PLAYER
                                if base.player_states['is_alive']:
                                    if not actor.get_python_tag("generic_states")['is_busy']:
                                        self.npc_directives.work_with_player(actor, actor_npc_rb,
                                                                             player,
                                                                             player_dist, request)
                                elif not base.player_states['is_alive']:
                                    # ENEMY
                                    if enemy_npc_ref.get_python_tag("generic_states")['is_alive']:
                                        if not actor.get_python_tag("generic_states")['is_busy']:
                                            self.npc_directives.work_with_enemy(actor, actor_npc_rb,
                                                                                enemy_npc_ref,
                                                                                enemy_npc_rb, enemy_dist,
                                                                                hitbox_dist, request)

            # If me is dead
            else:
                self.npc_controller.npc_in_dying_logic(actor, request)

        return task.cont
