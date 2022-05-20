class NpcBehavior:
    def __init__(self, ai_chars, ai_chars_bs):
        self.base = base
        self.ai_chars = ai_chars
        self.ai_chars_bs = ai_chars_bs
        # Keep this class instance for further usage in NpcBehavior class only
        self.npc_ai_logic = self.base.game_instance['npc_ai_logic_cls']

    def npc_friend_logic(self, actor, player, request, passive, task):
        if self.base.game_instance['menu_mode']:
            return task.done

        if (actor and player and request and self.ai_chars_bs
                and isinstance(passive, bool)):
            if actor.get_python_tag("generic_states")['is_alive']:
                # Get the time that elapsed since last frame
                dt = globalClock.getDt()

                # Add :BS suffix since we'll get Bullet Shape NodePath here
                actor_name = actor.get_name()
                self.ai_chars[actor_name].set_max_force(5)

                if passive:
                    # Just stay
                    self.npc_ai_logic.npc_in_staying_logic(actor, request)

                if passive is False:
                    # Get required data about enemy to deal with it
                    actor_npc_bs = self.base.get_actor_bullet_shape_node(asset=actor_name, type="NPC")
                    enemy_npc_ref = self.npc_ai_logic.get_enemy_ref(enemy_cls="enemy")
                    enemy_npc_bs = self.npc_ai_logic.get_enemy_bs(enemy_cls="enemy")

                    if actor_npc_bs and enemy_npc_ref and enemy_npc_bs:
                        player_dist = int(actor_npc_bs.get_distance(player))
                        enemy_dist = int(actor_npc_bs.get_distance(enemy_npc_bs))
                        hitbox_dist = self.npc_ai_logic.get_hit_distance(actor)

                        if base.player_states['is_alive']:
                            if base.player_states['is_mounted']:
                                self.npc_ai_logic.npc_in_mounting_logic(actor, actor_npc_bs, request)
                            else:
                                self.npc_ai_logic.npc_in_unmounting_logic(actor, actor_npc_bs, request)

                            # If NPC is far from Player, do pursue Player
                            if player_dist > 1:
                                if not base.player_states['is_mounted']:
                                    self.npc_ai_logic.npc_in_walking_logic(actor, actor_npc_bs, player, request)
                            elif player_dist <= 1:
                                self.npc_ai_logic.npc_in_staying_logic(actor, request)
                                # If enemy is close start attacking
                                if enemy_dist <= 1:
                                    # Facing to enemy
                                    self.npc_ai_logic.face_actor_to(actor_npc_bs, enemy_npc_bs)
                                    self.npc_ai_logic.npc_get_weapon(actor, request, "sword",
                                                                     "Korlan:LeftHand")
                                    # self.npc_ai_logic.npc_get_weapon(actor, request, "bow",
                                    #                                 "Korlan:LeftHand")
                                    # self.npc_ai_logic.npc_remove_weapon(actor, request, "sword", "Korlan:Spine")
                                    # self.npc_ai_logic.npc_remove_weapon(actor, request, "bow", "Korlan:Spine")
                                    # request.request("Attack", actor, "right_turn", "play")
                                    # Counterattack an enemy or do block
                                    if hitbox_dist:
                                        if hitbox_dist >= 0.5 and hitbox_dist <= 1.8:
                                            self.npc_ai_logic.npc_in_blocking_logic(actor, request)
                                        else:
                                            self.npc_ai_logic.npc_in_attacking_logic(actor, enemy_npc_bs,
                                                                                     dt, request)
                        else:
                            if player_dist <= 1:
                                self.npc_ai_logic.npc_in_staying_logic(actor, request)

                                if enemy_npc_ref.get_python_tag("generic_states")['is_alive']:
                                    # Friendly NPC starts attacking the opponent when player first starts attacking it
                                    if enemy_dist > 1:
                                        self.npc_ai_logic.npc_in_walking_logic(actor, actor_npc_bs,
                                                                               enemy_npc_bs, request)
                                    elif enemy_dist <= 1:
                                        self.npc_ai_logic.npc_in_staying_logic(actor, request)
                                        self.npc_ai_logic.npc_in_attacking_logic(actor, enemy_npc_bs,
                                                                                 dt, request)
                                else:
                                    if enemy_dist <= 1:
                                        self.npc_ai_logic.npc_in_staying_logic(actor, request)
                    else:
                        self.npc_ai_logic.npc_in_staying_logic(actor, request)

        return task.cont

    def npc_neutral_logic(self, actor, player, request, passive, task):
        if self.base.game_instance['menu_mode']:
            return task.done

        if actor and player and request and isinstance(passive, bool):
            if actor.get_python_tag("generic_states")['is_alive']:
                actor_name = actor.get_name()
                self.ai_chars[actor_name].set_max_force(5)

                if passive:
                    # Just stay
                    self.npc_ai_logic.npc_in_staying_logic(actor, request)

                elif passive is False:
                    actor_npc_bs = self.base.get_actor_bullet_shape_node(asset=actor_name, type="NPC")
                    # Get required data about enemy to deal with it
                    enemy_npc_ref = self.npc_ai_logic.get_enemy_ref(enemy_cls="enemy")
                    enemy_npc_bs = self.npc_ai_logic.get_enemy_bs(enemy_cls="enemy")

                    if actor_npc_bs and enemy_npc_ref and enemy_npc_bs:

                        player_dist = int(actor_npc_bs.get_distance(player))
                        enemy_dist = int(actor_npc_bs.get_distance(enemy_npc_bs))

                        """if base.player_states['is_alive']:
                            # If NPC is far from Player, do pursue Player
                            if player_dist > 1:
                                self.npc_ai_logic.npc_in_walking_logic(actor, actor_npc_bs, player, request)
                            elif player_dist <= 1:
                                self.npc_ai_logic.npc_in_staying_logic(actor, request)
                        else:
                            if player_dist > 1:
                                self.npc_ai_logic.npc_in_staying_logic(actor, request)"""

                        if enemy_npc_ref.get_python_tag("generic_states")['is_alive']:
                            if enemy_dist > 1:
                                self.npc_ai_logic.npc_in_walking_logic(actor, actor_npc_bs, enemy_npc_bs, request)
                            elif enemy_dist <= 1:
                                self.npc_ai_logic.npc_in_staying_logic(actor, request)
                        else:
                            if enemy_dist >= 1:
                                self.npc_ai_logic.npc_in_staying_logic(actor, request)

                    else:
                        self.npc_ai_logic.npc_in_staying_logic(actor, request)

        return task.cont

    def npc_enemy_logic(self, actor, player, request, passive, task):
        if self.base.game_instance['menu_mode']:
            return task.done

        if actor and player and request and isinstance(passive, bool):
            if actor.get_python_tag("generic_states")['is_alive']:
                # Get the time that elapsed since last frame
                dt = globalClock.getDt()

                # Add :BS suffix since we'll get Bullet Shape NodePath here
                actor_name = actor.get_name()
                self.ai_chars[actor_name].set_max_force(5)

                # Just stay
                if passive:
                    self.npc_ai_logic.npc_in_staying_logic(actor, request)

                elif passive is False:
                    # Get required data about enemy to deal with it
                    actor_npc_bs = self.base.get_actor_bullet_shape_node(asset=actor_name, type="NPC")
                    enemy_npc_ref = self.npc_ai_logic.get_enemy_ref(enemy_cls="friend")
                    enemy_npc_bs = self.npc_ai_logic.get_enemy_bs(enemy_cls="friend")

                    if actor_npc_bs and enemy_npc_ref and enemy_npc_bs:
                        player_dist = int(actor_npc_bs.get_distance(player))
                        enemy_dist = int(actor_npc_bs.get_distance(enemy_npc_bs))

                        if enemy_npc_ref.get_python_tag("generic_states")['is_alive']:
                            # If NPC is far from enemy, do pursue enemy
                            if enemy_dist > 1:
                                self.npc_ai_logic.npc_in_walking_logic(actor, actor_npc_bs, enemy_npc_bs, request)
                            elif enemy_dist <= 1:
                                self.npc_ai_logic.npc_in_staying_logic(actor, request)
                                self.npc_ai_logic.npc_in_attacking_logic(actor, enemy_npc_bs, dt, request)
                                """if self.base.game_instance['player_ref'].get_current_frame("Boxing"):
                                    self.npc_ai_logic.npc_in_attacking_logic(actor, enemy_npc_bs, dt, request)"""
                        else:
                            if enemy_dist <= 1:
                                self.npc_ai_logic.npc_in_staying_logic(actor, request)

                                if base.player_states['is_alive']:
                                    # If NPC is far from Player, do pursue Player
                                    if player_dist > 1:
                                        self.npc_ai_logic.npc_in_walking_logic(actor, actor_npc_bs, player, request)
                                    elif player_dist <= 1:
                                        self.npc_ai_logic.npc_in_staying_logic(actor, request)
                                        # self.npc_in_gathering_logic(actor, request)
                                        if self.base.game_instance['player_ref'].get_current_frame("Boxing"):
                                            self.npc_ai_logic.npc_in_attacking_logic(actor, player, dt, request)
                                else:
                                    if player_dist <= 1:
                                        self.npc_ai_logic.npc_in_staying_logic(actor, request)

                        """# Enemy returns back
                            if actor.get_python_tag("health_np"):
                                if (actor.get_python_tag("health_np")['value'] == 50.0
                                        and vec == 10.0 or vec == -10.0
                                        and ai_behaviors[actor_name].behavior_status("evade") == "paused"):
                                    ai_behaviors[actor_name].remove_ai("evade")
                                    # TODO: Change action to something more suitable
                                    request.request("Idle", actor, "Standing_idle_male", "loop")"""

                    else:
                        self.npc_ai_logic.npc_in_staying_logic(actor, request)

        return task.cont
