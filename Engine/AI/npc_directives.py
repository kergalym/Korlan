from direct.interval.MetaInterval import Sequence
from panda3d.core import NodePath, Vec3

from Engine.AI import ai_declaratives

""" ANIMATIONS"""
from Engine import anim_names


class NpcDirectives:
    def __init__(self):
        self.base = base
        # Keep this class instance for further usage in NpcBehavior class only
        self.npc_controller = self.base.game_instance['npc_controller_cls']
        self.seq = Sequence()
        self._directive_is_executing = False
        self.archery_distance = 4
        self.horse_archery_distance = 10

    def _melee_attack(self, actor, actor_rb_np, target, target_dist, hitbox_dist, request):
        if not actor.get_python_tag("human_states")['is_on_horse']:
            if target_dist is not None and target_dist <= 1:
                # If enemy is close start attacking
                self.attack_directive(actor, actor_rb_np,
                                      target,
                                      hitbox_dist, request)

        elif actor.get_python_tag("human_states")['is_on_horse']:
            if target_dist is not None and target_dist <= 2:
                # If enemy is close start attacking
                self.attack_directive(actor, actor_rb_np,
                                      target,
                                      hitbox_dist, request)

    def _archery_attack(self, actor, actor_rb_np, target, target_dist, hitbox_dist, request):
        if actor.get_python_tag("arrow_count") > 1:
            if target_dist is not None and target_dist > self.archery_distance:
                self.npc_controller.npc_in_walking_rd_logic(actor, actor_rb_np,
                                                            target, request)
            elif target_dist is not None and target_dist < 2:
                archery = NodePath("archery_position")
                _pos = target.get_pos() + Vec3(0, self.archery_distance, 0)
                archery.set_pos(_pos)
                self.npc_controller.npc_in_walking_rd_logic(actor, actor_rb_np,
                                                            archery, request)

            if (not actor.get_python_tag("generic_states")['is_moving']
                    and not actor.get_python_tag("generic_states")['is_crouch_moving']):
                self.npc_controller.face_actor_to(actor_rb_np, target)
                self.attack_directive(actor, actor_rb_np,
                                      target,
                                      hitbox_dist, request)

        elif actor.get_python_tag("arrow_count") <= 1:
            if target_dist is not None and target_dist > 1:
                self.npc_controller.npc_in_walking_rd_logic(actor, actor_rb_np,
                                                            target, request)
            else:
                if actor.get_python_tag("human_states")['has_bow']:
                    self.npc_controller.npc_remove_weapon(actor, request, "bow", "Korlan:Spine")
                if not actor.get_python_tag("human_states")['has_sword']:
                    self.npc_controller.npc_get_weapon(actor, request, "sword", "Korlan:LeftHand")

                if actor.get_python_tag("human_states")['has_sword']:
                    self.attack_directive(actor, actor_rb_np,
                                          target,
                                          hitbox_dist, request)

    def work_with_player(self, actor, actor_rb_np, player, player_dist, request):
        actor.set_python_tag("target_np", player)
        actor.set_python_tag("enemy_distance", player_dist)
        hitbox_dist = actor.get_python_tag("enemy_hitbox_distance")

        # Mount if player mounts
        if actor.get_python_tag("npc_type") == "npc":
            if base.player_states['is_mounted']:
                self.npc_controller.npc_in_mounting_logic(actor, actor_rb_np, request)
            elif not base.player_states['is_mounted']:
                self.npc_controller.npc_in_unmounting_logic(actor, actor_rb_np, request)

        # Equip/Unequip weapon if player does same
        if (actor.get_python_tag("npc_type") == "npc"
                and actor.get_python_tag("arrow_count") > 1):
            if actor.get_python_tag("generic_states")['is_idle']:
                if base.player_states['has_sword']:
                    self.npc_controller.npc_get_weapon(actor, request, "sword", "Korlan:LeftHand")
                elif not base.player_states['has_sword']:
                    self.npc_controller.npc_remove_weapon(actor, request, "sword", "Korlan:Spine")
                if base.player_states['has_bow']:
                    self.npc_controller.npc_get_weapon(actor, request, "bow", "Korlan:LeftHand")
                elif not base.player_states['has_bow']:
                    self.npc_controller.npc_remove_weapon(actor, request, "bow", "Korlan:Spine")

        # Pursue and attack!!!!
        if actor.get_python_tag("npc_type") == "npc":
            if not actor.get_python_tag("human_states")["has_bow"]:
                if not actor.get_python_tag("human_states")['is_on_horse']:
                    if not actor.get_python_tag("generic_states")['is_busy']:
                        if player_dist is not None:
                            if actor.get_python_tag("detour_nav") is False:
                                if player_dist > ai_declaratives.distance_to_target:
                                    # Won't follow player if it's indoor
                                    if not self.base.game_instance["is_indoor"]:

                                        # Walk/Run state goes here
                                        if actor.get_python_tag("move_type") == "walk":
                                            if base.player_states["is_running"]:
                                                actor.set_python_tag("move_type", "run")
                                        if actor.get_python_tag("move_type") == "run":
                                            if not base.player_states["is_running"]:
                                                actor.set_python_tag("move_type", "walk")

                                        self.npc_controller.face_actor_to(actor_rb_np, player)
                                        self.npc_controller.do_any_walking(actor, actor_rb_np,
                                                                           player, request)

                                if player_dist <= ai_declaratives.distance_to_target:
                                    self.npc_controller.npc_in_idle_logic(actor, request)
                                    self.npc_controller.face_actor_to(actor_rb_np, player)

                elif actor.get_python_tag("human_states")['is_on_horse']:
                    if not actor.get_python_tag("generic_states")['is_busy']:
                        if player_dist is not None:
                            if actor.get_python_tag("detour_nav") is False:
                                if player_dist > ai_declaratives.distance_to_animal:
                                    # Won't follow player if it's indoor
                                    if not self.base.game_instance["is_indoor"]:
                                        parent_rb_np = actor.get_python_tag("mounted_horse")
                                        parent = parent_rb_np.get_child(0)

                                        # Walk/Run state goes here
                                        if parent.get_python_tag("move_type") == "walk":
                                            if base.player_states["is_running"]:
                                                parent.set_python_tag("move_type", "run")
                                        if parent.get_python_tag("move_type") == "run":
                                            if not base.player_states["is_running"]:
                                                parent.set_python_tag("move_type", "walk")

                                        self.npc_controller.face_actor_to(actor_rb_np, player)
                                        self.npc_controller.do_any_walking(parent, parent_rb_np,
                                                                           player, request)

                                if player_dist <= ai_declaratives.distance_to_animal:
                                    self.npc_controller.npc_in_idle_logic(actor, request)
                                    self.npc_controller.face_actor_to(actor_rb_np, player)

            if not actor.get_python_tag("human_states")["has_bow"]:
                self._melee_attack(actor, actor_rb_np, player,
                                   player_dist, hitbox_dist, request)
            elif actor.get_python_tag("human_states")["has_bow"]:
                self._archery_attack(actor, actor_rb_np, player,
                                     player_dist, hitbox_dist, request)

    def work_with_enemy(self, actor, actor_rb_np, enemy_npc_ref,
                        enemy_rb_np, enemy_dist, hitbox_dist, request):
        # Friendly NPC starts attacking
        # the opponent when player first starts attacking it
        actor.set_python_tag("target_np", enemy_rb_np)
        actor.set_python_tag("enemy_distance", enemy_dist)

        # Mount if enemy mounts
        if actor.get_python_tag("npc_type") == "npc":
            if enemy_npc_ref.get_python_tag("human_states")['is_on_horse']:
                self.npc_controller.npc_in_mounting_logic(actor, actor_rb_np, request)
            elif not enemy_npc_ref.get_python_tag("human_states")['is_on_horse']:
                self.npc_controller.npc_in_unmounting_logic(actor, actor_rb_np, request)

        # Equip/Unequip weapon if enemy does same
        if (actor.get_python_tag("npc_type") == "npc"
                and actor.get_python_tag("arrow_count") > 1):
            if actor.get_python_tag("generic_states")['is_idle']:
                if enemy_npc_ref.get_python_tag("human_states")['has_sword']:
                    self.npc_controller.npc_get_weapon(actor, request, "sword", "Korlan:LeftHand")
                elif not enemy_npc_ref.get_python_tag("human_states")['has_sword']:
                    self.npc_controller.npc_remove_weapon(actor, request, "sword", "Korlan:Spine")
                if enemy_npc_ref.get_python_tag("human_states")["has_bow"]:
                    self.npc_controller.npc_get_weapon(actor, request, "bow", "Korlan:LeftHand")
                elif not enemy_npc_ref.get_python_tag("human_states")["has_bow"]:
                    self.npc_controller.npc_remove_weapon(actor, request, "bow", "Korlan:Spine")

        # Pursue and attack!!!!
        if actor.get_python_tag("npc_type") == "npc":
            if not actor.get_python_tag("human_states")["has_bow"]:
                if not actor.get_python_tag("human_states")['is_on_horse']:
                    if enemy_dist is not None:
                        if actor.get_python_tag("detour_nav") is False:
                            if enemy_dist > ai_declaratives.distance_to_target:
                                # Walk/Run state goes here
                                if actor.get_python_tag("move_type") == "walk":
                                    if enemy_rb_np.get_child(0).get_python_tag("generic_states")["is_running"]:
                                        actor.set_python_tag("move_type", "run")
                                if actor.get_python_tag("move_type") == "run":
                                    if not enemy_rb_np.get_child(0).get_python_tag("generic_states")["is_running"]:
                                        actor.set_python_tag("move_type", "walk")

                                self.npc_controller.face_actor_to(actor_rb_np, enemy_rb_np)
                                self.npc_controller.do_any_walking(actor, actor_rb_np,
                                                                   enemy_rb_np, request)
                            if enemy_dist <= ai_declaratives.distance_to_target:
                                self.npc_controller.npc_in_idle_logic(actor, request)
                                self.npc_controller.face_actor_to(actor_rb_np, enemy_rb_np)

                elif actor.get_python_tag("human_states")['is_on_horse']:
                    if enemy_dist is not None:
                        if actor.get_python_tag("detour_nav") is False:
                            if enemy_dist > ai_declaratives.distance_to_animal:
                                if actor.get_python_tag("current_task") is None:
                                    parent_rb_np = actor.get_python_tag("mounted_horse")
                                    parent = parent_rb_np.get_child(0)

                                    # Walk/Run state goes here
                                    if parent.get_python_tag("move_type") == "walk":
                                        if enemy_rb_np.get_parent().get_python_tag("generic_states")["is_running"]:
                                            parent.set_python_tag("move_type", "run")
                                    if parent.get_python_tag("move_type") == "run":
                                        if not enemy_rb_np.get_parent().get_python_tag("generic_states")["is_running"]:
                                            parent.set_python_tag("move_type", "walk")

                                    self.npc_controller.face_actor_to(actor_rb_np, enemy_rb_np)
                                    self.npc_controller.do_any_walking(actor, parent_rb_np,
                                                                       enemy_rb_np, request)
                            if enemy_dist <= ai_declaratives.distance_to_animal:
                                self.npc_controller.npc_in_idle_logic(actor, request)
                                self.npc_controller.face_actor_to(actor_rb_np, enemy_rb_np)

            if not actor.get_python_tag("human_states")["has_bow"]:
                self._melee_attack(actor, actor_rb_np, enemy_rb_np,
                                   enemy_dist, hitbox_dist, request)
            elif actor.get_python_tag("human_states")["has_bow"]:
                self._archery_attack(actor, actor_rb_np, enemy_rb_np,
                                     enemy_dist, hitbox_dist, request)

    def _set_priorited_npc_by_distance(self, target):
        for k in self.base.game_instance["actors_np"]:
            actor = self.base.game_instance["actors_np"][k].get_child(0)
            dist = target.get_distance(self.base.game_instance["actors_np"][k])
            if actor.get_python_tag("npc_type") == "npc":
                if not actor.get_python_tag("human_states")["has_bow"]:
                    if dist < 1:
                        if actor.get_python_tag("priority") == 0:
                            actor.set_python_tag("priority", 1)
                    else:
                        if actor.get_python_tag("priority") > 0:
                            actor.set_python_tag("priority", 0)

                elif actor.get_python_tag("human_states")["has_bow"]:
                    if dist <= 5:
                        if actor.get_python_tag("priority") == 0:
                            actor.set_python_tag("priority", 1)
                    else:
                        if actor.get_python_tag("priority") > 0:
                            actor.set_python_tag("priority", 0)

    def attack_directive(self, actor, actor_rb_np, oppo_rb_np, hitbox_dist, request):
        # Counterattack an enemy or do block
        # Do attack only if play did first attack
        if base.player_states['is_alive']:
            player = self.base.game_instance["player_ref"]
            if player.get_python_tag("first_attack"):
                if not actor.get_python_tag("human_states")['is_on_horse']:
                    self._set_priorited_npc_by_distance(oppo_rb_np)
                    self.npc_controller.do_defensive_prediction(actor, actor_rb_np,
                                                                request, hitbox_dist)
                else:
                    npc = actor.get_python_tag("mounted_horse")
                    npc_bs = npc.get_parent()
                    self.npc_controller.do_defensive_prediction(npc, npc_bs,
                                                                request, hitbox_dist)
        else:
            if not actor.get_python_tag("human_states")['is_on_horse']:
                self._set_priorited_npc_by_distance(oppo_rb_np)
                self.npc_controller.do_defensive_prediction(actor, actor_rb_np,
                                                            request, hitbox_dist)
            else:
                npc = actor.get_python_tag("mounted_horse")
                npc_bs = npc.get_parent()
                self.npc_controller.do_defensive_prediction(npc, npc_bs,
                                                            request, hitbox_dist)

    def work_with_outdoor_directive(self, actor, target, request):
        # Get required data about enemy to deal with it
        actor_name = "{0}:BS".format(actor.get_name())
        actor_rb_np = self.base.game_instance["actors_np"][actor_name]
        directive_np = render.find("**/{0}".format(target))
        directive_one_dist = int(actor_rb_np.get_distance(directive_np))

        # Go to the first directive
        if directive_one_dist > 1:
            self.npc_controller.npc_in_walking_rd_logic(actor, actor_rb_np,
                                                        directive_np,
                                                        request)

    def work_with_indoor_directives_queue(self, actor, num, request):
        # Get required data about directives
        # 0 yurt
        # 1 quest_empty_campfire
        # 2 quest_empty_rest_place
        # 3 quest_empty_hearth
        # 4 quest_empty_spring_water
        # 5 round_table
        actor_name = "{0}:BS".format(actor.get_name())
        actor_rb_np = self.base.game_instance["actors_np"][actor_name]
        directive_one_np = self.base.game_instance["static_indoor_targets"][0]
        directive_two_np = self.base.game_instance["static_indoor_targets"][num]
        directive_one_dist = int(actor_rb_np.get_distance(directive_one_np))
        directive_two_dist = int(actor_rb_np.get_distance(directive_two_np))

        # Go to the first directive
        if directive_one_dist > 1 and directive_two_dist > 1:
            self.npc_controller.npc_in_walking_rd_logic(actor, actor_rb_np,
                                                        directive_one_np,
                                                        request)
        # Got the first directive? Go to the second directive
        elif directive_one_dist < 2 and directive_two_dist > 1:
            if not directive_two_np.get_python_tag("place_is_busy"):
                self.npc_controller.npc_in_walking_rd_logic(actor, actor_rb_np,
                                                            directive_two_np,
                                                            request)
        # Got the second directive? Stop walking
        else:
            actor.set_python_tag("directive_num", num)

            if num == 5:
                self.npc_controller.face_actor_to(actor_rb_np, directive_two_np)
                self.npc_controller.npc_in_gathering_logic(actor=actor, request=request,
                                                           action=anim_names.a_anim_picking,
                                                           parent=directive_two_np, item="dombra")
                """self.npc_controller.npc_in_dropping_logic(actor=actor, request=request,
                                                          action=anim_names.a_anim_dropping)"""
