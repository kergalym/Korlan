from direct.interval.FunctionInterval import Func
from direct.interval.MetaInterval import Sequence


class NpcBehavior:
    def __init__(self):
        self.base = base
        # Keep this class instance for further usage in NpcBehavior class only
        self.npc_ai_logic = self.base.game_instance['npc_ai_logic_cls']
        self.seq = Sequence()

    def _attack_directive(self, actor, actor_npc_bs, oppo_npc_bs, distance, hitbox_dist, request):
        if (not actor.get_python_tag("human_states")["has_sword"]
                or not actor.get_python_tag("human_states")["has_bow"]):
            if distance <= 1:
                # Facing to enemy
                self.npc_ai_logic.face_actor_to(actor_npc_bs, oppo_npc_bs)
                # Counterattack an enemy or do block
                self.npc_ai_logic.do_defensive_prediction(actor, actor_npc_bs, request, hitbox_dist)

        if actor.get_python_tag("human_states")["has_sword"]:
            if distance <= 1:
                # Facing to enemy
                self.npc_ai_logic.face_actor_to(actor_npc_bs, oppo_npc_bs)
                # Counterattack an enemy or do block
                self.npc_ai_logic.do_defensive_prediction(actor, actor_npc_bs, request, hitbox_dist)

        elif actor.get_python_tag("human_states")["has_bow"]:
            # todo: test npc archery on player first
            if distance <= 5:
                self.npc_ai_logic.npc_in_staying_logic(actor, request)
                # Facing to enemy
                self.npc_ai_logic.face_actor_to(actor_npc_bs, oppo_npc_bs)
                # If enemy is close start attacking
                self.npc_ai_logic.do_defensive_prediction(actor, actor_npc_bs, request, hitbox_dist)

    def _work_with_player(self, actor, player, actor_npc_bs, request):
        player_dist = int(actor_npc_bs.get_distance(player))
        hitbox_dist = self.npc_ai_logic.get_hit_distance(actor)

        # Mount if player mounts
        if base.player_states['is_mounted']:
            self.npc_ai_logic.npc_in_mounting_logic(actor, actor_npc_bs, request)
        elif not base.player_states['is_mounted']:
            self.npc_ai_logic.npc_in_unmounting_logic(actor, actor_npc_bs, request)

        # Equip/Unequip weapon if player does same
        if base.player_states['has_sword']:
            self.npc_ai_logic.npc_get_weapon(actor, request, "sword", "Korlan:LeftHand")
        elif not base.player_states['has_sword']:
            self.npc_ai_logic.npc_remove_weapon(actor, request, "sword", "Korlan:Spine")
        if base.player_states['has_bow']:
            self.npc_ai_logic.npc_get_weapon(actor, request, "bow", "Korlan:LeftHand")
        elif not base.player_states['has_bow']:
            self.npc_ai_logic.npc_remove_weapon(actor, request, "bow", "Korlan:Spine")

        # Pursue and attack!!!!
        if not base.player_states['is_mounted']:
            if (not actor.get_python_tag("human_states")["has_sword"]
                    or not actor.get_python_tag("human_states")["has_bow"]):
                if player_dist > 1:
                    self.npc_ai_logic.npc_in_walking_logic(actor, actor_npc_bs, player, request)
                elif player_dist <= 1:
                    self.npc_ai_logic.npc_in_staying_logic(actor, request)
                    # If enemy is close start attacking
                    self._attack_directive(actor, actor_npc_bs, player, player_dist,
                                           hitbox_dist, request)
            if actor.get_python_tag("human_states")["has_sword"]:
                if player_dist > 1:
                    self.npc_ai_logic.npc_in_walking_logic(actor, actor_npc_bs, player, request)
                elif player_dist <= 1:
                    self.npc_ai_logic.npc_in_staying_logic(actor, request)
                    # If enemy is close start attacking
                    self._attack_directive(actor, actor_npc_bs, player, player_dist,
                                           hitbox_dist, request)
            elif actor.get_python_tag("human_states")["has_bow"]:
                # todo: test npc archery on player first
                if player_dist > 1:
                    self.npc_ai_logic.npc_in_walking_logic(actor, actor_npc_bs, player, request)
                elif player_dist <= 5:
                    self.npc_ai_logic.npc_in_staying_logic(actor, request)
                    self._attack_directive(actor, actor_npc_bs, player, player_dist,
                                           hitbox_dist, request)

    def _work_with_enemy(self, actor, player, actor_npc_bs, enemy_npc_bs, enemy_dist, hitbox_dist, request):
        # Friendly NPC starts attacking
        # the opponent when player first starts attacking it
        if enemy_dist > 1:
            self.npc_ai_logic.npc_in_walking_logic(actor, actor_npc_bs,
                                                   enemy_npc_bs, request)
        elif enemy_dist <= 1:
            self.npc_ai_logic.npc_in_staying_logic(actor, request)
            self._attack_directive(actor, actor_npc_bs, player, enemy_dist,
                                   hitbox_dist, request)

        elif actor.get_python_tag("human_states")["has_bow"]:
            if enemy_dist > 1:
                self.npc_ai_logic.npc_in_walking_logic(actor, actor_npc_bs,
                                                       enemy_npc_bs,
                                                       request)
            elif enemy_dist <= 5:
                self.npc_ai_logic.npc_in_staying_logic(actor, request)
                # Facing to enemy
                self._attack_directive(actor, actor_npc_bs, player, enemy_dist,
                                       hitbox_dist, request)

    def _work_with_outdoor_directive(self, actor, target, request):
        # Get required data about enemy to deal with it
        actor_name = "{0}:BS".format(actor.get_name())
        actor_npc_bs = self.base.game_instance["actors_np"][actor_name]
        directive_np = render.find("**/{0}".format(target))
        directive_one_dist = int(actor_npc_bs.get_distance(directive_np))

        # Go to the first directive
        if directive_one_dist > 1:
            if self.base.game_instance["use_pandai"]:
                self.base.game_instance["use_pandai"] = False
            self.npc_ai_logic.npc_in_walking_logic(actor, actor_npc_bs,
                                                   directive_np,
                                                   request)
        # elif directive_two_dist < 2:
        else:
            if not self.base.game_instance["use_pandai"]:
                self.base.game_instance["use_pandai"] = True
            self.npc_ai_logic.npc_in_staying_logic(actor, request)

    def _work_with_indoor_directives_queue(self, actor, request):
        # Get required data about directives
        # 0 yurt
        # 1 quest_empty_campfire
        # 2 quest_empty_rest_place
        # 3 quest_empty_hearth
        # 4 quest_empty_spring_water
        # 5 round_table
        actor_name = "{0}:BS".format(actor.get_name())
        actor_npc_bs = self.base.game_instance["actors_np"][actor_name]
        directive_one_np = self.base.game_instance["static_indoor_targets"][0]
        directive_two_np = self.base.game_instance["static_indoor_targets"][2]
        directive_one_dist = int(actor_npc_bs.get_distance(directive_one_np))
        directive_two_dist = int(actor_npc_bs.get_distance(directive_two_np))

        # print(directive_one_dist, directive_two_dist)

        # Go to the first directive
        if directive_one_dist > 1 and directive_two_dist > 1:
            if self.base.game_instance["use_pandai"]:
                self.base.game_instance["use_pandai"] = False
            self.npc_ai_logic.npc_in_walking_logic(actor, actor_npc_bs,
                                                   directive_one_np,
                                                   request)
        # Got the first directive? Go to the second directive
        elif directive_one_dist < 2 and directive_two_dist > 1:
            self.npc_ai_logic.npc_in_walking_logic(actor, actor_npc_bs,
                                                   directive_two_np,
                                                   request)
        # Got the second directive? Stop walking
        # elif directive_two_dist < 2 and directive_one_dist > 1:
        else:
            if not self.base.game_instance["use_pandai"]:
                self.base.game_instance["use_pandai"] = True
            self.npc_ai_logic.npc_in_staying_logic(actor, request)

    def npc_generic_logic(self, actor, player, request, passive, task):
        if self.base.game_instance['menu_mode']:
            return task.done

        if (actor and player and request
                and isinstance(passive, bool)):

            if actor.get_python_tag("generic_states")['is_alive']:
                actor_name = actor.get_name()

                if passive:
                    # FIXME: TEST the directives
                    self._work_with_indoor_directives_queue(actor, request)
                    # self._work_with_outdoor_directive(actor=actor, target="yurt", request=request)

                    # Just stay
                    # self.npc_ai_logic.npc_in_staying_logic(actor, request)

                if not passive:

                    # Get required data about enemy to deal with it
                    actor_npc_bs = self.base.get_actor_bullet_shape_node(asset=actor_name, type="NPC")

                    # No alive enemy around, just stay tuned
                    if not self.npc_ai_logic.get_enemy(actor=actor):
                        if not base.player_states['is_alive']:
                            self.npc_ai_logic.npc_in_staying_logic(actor, request)

                        if base.player_states['is_alive']:
                            self._work_with_player(actor, player, actor_npc_bs, request)

                    # Check if we have alive someone around us
                    if self.npc_ai_logic.get_enemy(actor=actor):
                        enemy_npc_ref, enemy_npc_bs = self.npc_ai_logic.get_enemy(actor=actor)

                        if actor_npc_bs and enemy_npc_ref and enemy_npc_bs:
                            player_dist = int(actor_npc_bs.get_distance(player))
                            enemy_dist = int(actor_npc_bs.get_distance(enemy_npc_bs))
                            hitbox_dist = self.npc_ai_logic.get_hit_distance(actor)

                            # PLAYER
                            if base.player_states['is_alive']:
                                self._work_with_player(actor, player, actor_npc_bs, request)
                            elif not base.player_states['is_alive']:
                                if player_dist <= 1:
                                    self.npc_ai_logic.npc_in_staying_logic(actor, request)

                            # ENEMY
                            if enemy_npc_ref.get_python_tag("generic_states")['is_alive']:
                                if enemy_npc_ref.get_python_tag("generic_states")['is_alive']:
                                    self._work_with_enemy(actor, player, actor_npc_bs,
                                                          enemy_npc_bs, enemy_dist,
                                                          hitbox_dist, request)
                                else:
                                    if enemy_dist <= 1:
                                        self.npc_ai_logic.npc_in_staying_logic(actor, request)
            # If me is dead
            else:
                self.npc_ai_logic.npc_in_dying_logic(actor, request)

        return task.cont
