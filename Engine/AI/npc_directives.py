from direct.interval.MetaInterval import Sequence
from panda3d.core import NodePath, Vec3

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

    def _melee_attack(self, actor, actor_npc_bs, target, target_dist, hitbox_dist, request):
        if not actor.get_python_tag("human_states")['is_on_horse']:
            if target_dist is not None and target_dist <= 1:
                # If enemy is close start attacking
                if (not actor.get_python_tag("generic_states")['is_moving']
                        and not actor.get_python_tag("generic_states")['is_crouch_moving']):
                    self.npc_controller.npc_in_staying_logic(actor, request)

                self.attack_directive(actor, actor_npc_bs,
                                      target,
                                      hitbox_dist, request)

        elif actor.get_python_tag("human_states")['is_on_horse']:
            if target_dist is not None and target_dist <= 2:
                # If enemy is close start attacking
                if (not actor.get_python_tag("generic_states")['is_moving']
                        and not actor.get_python_tag("generic_states")['is_crouch_moving']):
                    self.npc_controller.npc_in_staying_logic(actor, request)

                self.attack_directive(actor, actor_npc_bs,
                                      target,
                                      hitbox_dist, request)

    def _archery_attack(self, actor, actor_npc_bs, target, target_dist, hitbox_dist, request):
        if actor.get_python_tag("arrow_count") > 1:
            if target_dist > self.archery_distance:
                self.npc_controller.npc_in_walking_logic(actor, actor_npc_bs,
                                                         target, request)
            elif target_dist is not None and target_dist < 2:
                archery = NodePath("archery_position")
                player_pos = target.get_pos() + Vec3(0, self.archery_distance, 0)
                archery.set_pos(player_pos)
                self.npc_controller.npc_in_walking_logic(actor, actor_npc_bs,
                                                         archery, request)

            if (not actor.get_python_tag("generic_states")['is_moving']
                    and not actor.get_python_tag("generic_states")['is_crouch_moving']):
                self.npc_controller.npc_in_staying_logic(actor, request)
                self.attack_directive(actor, actor_npc_bs,
                                      target,
                                      hitbox_dist, request)

        elif actor.get_python_tag("arrow_count") <= 1:
            if (not actor.get_python_tag("generic_states")['is_moving']
                    and not actor.get_python_tag("generic_states")['is_crouch_moving']):
                self.npc_controller.npc_in_staying_logic(actor, request)
            if target_dist is not None and target_dist > 1:
                self.npc_controller.npc_in_walking_logic(actor, actor_npc_bs,
                                                         target, request)
            else:
                if actor.get_python_tag("human_states")['has_bow']:
                    self.npc_controller.npc_remove_weapon(actor, request, "bow", "Korlan:Spine")
                if not actor.get_python_tag("human_states")['has_sword']:
                    self.npc_controller.npc_get_weapon(actor, request, "sword", "Korlan:LeftHand")

                if actor.get_python_tag("human_states")['has_sword']:
                    self.npc_controller.npc_in_staying_logic(actor, request)
                    self.attack_directive(actor, actor_npc_bs,
                                          target,
                                          hitbox_dist, request)

    def work_with_player(self, actor, actor_npc_bs, player, player_dist, request):
        actor.set_python_tag("target_np", player)
        actor.set_python_tag("enemy_distance", player_dist)
        hitbox_dist = actor.get_python_tag("enemy_hitbox_distance")

        # Mount if player mounts
        if actor.get_python_tag("npc_type") == "npc":
            if base.player_states['is_mounted']:
                self.npc_controller.npc_in_mounting_logic(actor, actor_npc_bs, request)
            elif not base.player_states['is_mounted']:
                self.npc_controller.npc_in_unmounting_logic(actor, actor_npc_bs, request)

        # Equip/Unequip weapon if player does same
        if (actor.get_python_tag("npc_type") == "npc"
                and actor.get_python_tag("arrow_count") > 1):
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
            if not actor.get_python_tag("human_states")['is_on_horse']:
                if not actor.get_python_tag("generic_states")['is_busy']:
                    if player_dist is not None and player_dist > 1:
                        if "Horse" in player.get_parent().get_name():
                            if actor.get_python_tag("current_task") is None:
                                pos = player.get_parent().get_parent().get_pos() + Vec3(2, 2, 0)
                                rider_horse_bs = NodePath("destpoint")
                                rider_horse_bs.set_pos(pos)
                                self.npc_controller.npc_in_walking_logic(actor, actor_npc_bs,
                                                                         rider_horse_bs, request)
                        else:
                            if actor.get_python_tag("current_task") is None:
                                # Won't follow player is it's indoor
                                if not self.base.game_instance["is_indoor"]:
                                    self.npc_controller.npc_in_walking_logic(actor, actor_npc_bs,
                                                                             player, request)

            elif actor.get_python_tag("human_states")['is_on_horse']:
                if not actor.get_python_tag("generic_states")['is_busy']:
                    if player_dist is not None and player_dist > 2:
                        if "Horse" in player.get_parent().get_name():
                            if actor.get_python_tag("current_task") is None:
                                pos = player.get_parent().get_parent().get_pos() + Vec3(2, 2, 0)
                                rider_horse_bs = NodePath("destpoint")
                                rider_horse_bs.set_pos(pos)
                                self.npc_controller.npc_in_walking_logic(actor, actor_npc_bs,
                                                                         rider_horse_bs, request)
                        else:
                            if actor.get_python_tag("current_task") is None:
                                # Won't follow player is it's indoor
                                if not self.base.game_instance["is_indoor"]:
                                    self.npc_controller.npc_in_walking_logic(actor, actor_npc_bs,
                                                                             player, request)

            if not actor.get_python_tag("human_states")["has_bow"]:
                self._melee_attack(actor, actor_npc_bs, player,
                                   player_dist, hitbox_dist, request)
            elif actor.get_python_tag("human_states")["has_bow"]:
                self._archery_attack(actor, actor_npc_bs, player,
                                     player_dist, hitbox_dist, request)

    def work_with_enemy(self, actor, actor_npc_bs, enemy_npc_ref,
                        enemy_npc_bs, enemy_dist, hitbox_dist, request):
        # Friendly NPC starts attacking
        # the opponent when player first starts attacking it
        actor.set_python_tag("target_np", enemy_npc_bs)
        actor.set_python_tag("enemy_distance", enemy_dist)

        # Mount if enemy mounts
        if actor.get_python_tag("npc_type") == "npc":
            if enemy_npc_ref.get_python_tag("human_states")['is_on_horse']:
                self.npc_controller.npc_in_mounting_logic(actor, actor_npc_bs, request)
            elif not enemy_npc_ref.get_python_tag("human_states")['is_on_horse']:
                self.npc_controller.npc_in_unmounting_logic(actor, actor_npc_bs, request)

        # Equip/Unequip weapon if enemy does same
        if (actor.get_python_tag("npc_type") == "npc"
                and actor.get_python_tag("arrow_count") > 1):
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
            if not actor.get_python_tag("human_states")['is_on_horse']:
                if enemy_dist is not None and enemy_dist > 1:
                    if "Horse" in enemy_npc_bs.get_parent().get_name():
                        if actor.get_python_tag("current_task") is None:
                            pos = enemy_npc_bs.get_parent().get_parent().get_pos() + Vec3(2, 2, 0)
                            rider_horse_bs = NodePath("destpoint")
                            rider_horse_bs.set_pos(pos)
                            self.npc_controller.npc_in_walking_logic(actor, actor_npc_bs,
                                                                     rider_horse_bs, request)
                    else:
                        if actor.get_python_tag("current_task") is None:
                            self.npc_controller.npc_in_walking_logic(actor, actor_npc_bs,
                                                                     enemy_npc_bs, request)

            elif actor.get_python_tag("human_states")['is_on_horse']:
                if enemy_dist is not None and enemy_dist > 2:
                    if "Horse" in enemy_npc_bs.get_parent().get_name():
                        if actor.get_python_tag("current_task") is None:
                            pos = enemy_npc_bs.get_parent().get_parent().get_pos() + Vec3(2, 2, 0)
                            rider_horse_bs = NodePath("destpoint")
                            rider_horse_bs.set_pos(pos)
                            self.npc_controller.npc_in_walking_logic(actor, actor_npc_bs,
                                                                     rider_horse_bs, request)
                    else:
                        if actor.get_python_tag("current_task") is None:
                            self.npc_controller.npc_in_walking_logic(actor, actor_npc_bs,
                                                                     enemy_npc_bs, request)

            if not actor.get_python_tag("human_states")["has_bow"]:
                self._melee_attack(actor, actor_npc_bs, enemy_npc_bs,
                                   enemy_dist, hitbox_dist, request)
            elif actor.get_python_tag("human_states")["has_bow"]:
                self._archery_attack(actor, actor_npc_bs, enemy_npc_bs,
                                     enemy_dist, hitbox_dist, request)

    def attack_directive(self, actor, actor_npc_bs, oppo_npc_bs, hitbox_dist, request):
        # Facing to enemy
        self.npc_controller.face_actor_to(actor_npc_bs, oppo_npc_bs)
        # Counterattack an enemy or do block
        # Do attack only if play did first attack
        player = self.base.game_instance["player_ref"]
        if player.get_python_tag("first_attack"):
            if not actor.get_python_tag("human_states")['is_on_horse']:
                self.npc_controller.do_defensive_prediction(actor, actor_npc_bs,
                                                            request, hitbox_dist)
            else:
                npc = actor.get_python_tag("mounted_horse")
                npc_bs = npc.get_parent()
                self.npc_controller.do_defensive_prediction(npc, npc_bs,
                                                            request, hitbox_dist)

    def work_with_outdoor_directive(self, actor, target, request):
        # Get required data about enemy to deal with it
        actor_name = "{0}:BS".format(actor.get_name())
        actor_npc_bs = self.base.game_instance["actors_np"][actor_name]
        directive_np = render.find("**/{0}".format(target))
        directive_one_dist = int(actor_npc_bs.get_distance(directive_np))

        # Go to the first directive
        if directive_one_dist > 1:
            self.npc_controller.npc_in_walking_logic(actor, actor_npc_bs,
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
        actor_npc_bs = self.base.game_instance["actors_np"][actor_name]
        directive_one_np = self.base.game_instance["static_indoor_targets"][0]
        directive_two_np = self.base.game_instance["static_indoor_targets"][num]
        directive_one_dist = int(actor_npc_bs.get_distance(directive_one_np))
        directive_two_dist = int(actor_npc_bs.get_distance(directive_two_np))

        # Go to the first directive
        if directive_one_dist > 1 and directive_two_dist > 1:
            self.npc_controller.npc_in_walking_logic(actor, actor_npc_bs,
                                                     directive_one_np,
                                                     request)
        # Got the first directive? Go to the second directive
        elif directive_one_dist < 2 and directive_two_dist > 1:
            if not directive_two_np.get_python_tag("place_is_busy"):
                self.npc_controller.npc_in_walking_logic(actor, actor_npc_bs,
                                                         directive_two_np,
                                                         request)
        # Got the second directive? Stop walking
        else:
            actor.set_python_tag("directive_num", num)

            if num == 5:
                self.npc_controller.face_actor_to(actor_npc_bs, directive_two_np)
                self.npc_controller.npc_in_gathering_logic(actor=actor, request=request,
                                                           action=anim_names.a_anim_picking,
                                                           parent=directive_two_np, item="dombra")
                """self.npc_controller.npc_in_dropping_logic(actor=actor, request=request,
                                                          action=anim_names.a_anim_dropping)"""
