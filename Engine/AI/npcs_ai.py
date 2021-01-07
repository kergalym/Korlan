class NpcsAI:

    def __init__(self):
        self.base = base

    def npc_friend_logic(self, actor, player, player_fsm, request, ai_behaviors,
                         npcs_xyz_vec, npcs_fsm_states, near_npc, passive):
        if (actor and player and player_fsm and request and npcs_xyz_vec and npcs_fsm_states
                and isinstance(passive, bool)
                and isinstance(near_npc, dict)
                and isinstance(npcs_xyz_vec, dict)):

            # Get the time that elapsed since last frame
            dt = globalClock.getDt()

            vect = {"panic_dist": 5,
                    "relax_dist": 5,
                    "wander_radius": 5,
                    "plane_flag": 0,
                    "area_of_effect": 10}

            # Add :BS suffix since we'll get Bullet Shape NodePath here
            actor_bs_name = "{0}:BS".format(actor.get_name())
            actor_name = actor.get_name()
            # actor_npc_bs = self.base.get_actor_bullet_shape_node(asset=actor_name, type="NPC")
            # actor_npc_bs = actor.get_parent()

            # actor.set_blend(frameBlend=True)

            vec_x = None
            if npcs_xyz_vec.get(actor_bs_name):
                vec_x = npcs_xyz_vec[actor_bs_name].length()

            if passive:
                # Just stay
                request.request("Idle", actor, "LookingAround", "loop")

            if passive is False:
                # Get required data about enemy to deal with it
                enemy_npc_ref = None
                for k in base.npcs_actor_refs:
                    if actor.get_name() not in k:
                        enemy_npc_ref = base.npcs_actor_refs[k]

                enemy_fsm_request = None
                for fsm_name in npcs_fsm_states:
                    if actor.get_name() not in fsm_name:
                        enemy_fsm_request = npcs_fsm_states[fsm_name]

                if enemy_npc_ref and enemy_fsm_request:
                    enemy_npc_ref_name = enemy_npc_ref.get_name()
                    enemy_npc_bs = None
                    if hasattr(self.base, "ai_chars_bs") and self.base.ai_chars_bs:
                        enemy_npc_bs = self.base.ai_chars_bs[enemy_npc_ref_name]

                    # If NPC is far from enemy, do pursue enemy
                    if (ai_behaviors[actor_name].behavior_status("pursue") == "disabled"
                            or ai_behaviors[actor_name].behavior_status("pursue") == "active"):
                        request.request("Walk", actor, enemy_npc_bs,
                                        ai_behaviors[actor_name],
                                        "pathfind", "Walking", vect, "loop")

                    # If NPC is close to Enemy, do enemy attack
                    if (ai_behaviors[actor_name].behavior_status("pursue") == "done"
                            or ai_behaviors[actor_name].behavior_status("pursue") == "paused"):
                        request.request("Idle", actor, "LookingAround", "loop")

                        # Friendly NPC starts attacking the opponent when player first starts attacking it
                        if self.base.player_ref.get_current_frame("Boxing"):
                            request.request("Attack", actor, "Boxing", "play")
                            if (actor.get_current_frame("Boxing") >= 23
                                    and actor.get_current_frame("Boxing") <= 25):
                                self.base.npcs_hits[enemy_npc_ref.get_name()] = True
                                enemy_fsm_request.request("Attacked", enemy_npc_ref, "BigHitToHead", "Boxing", "play")

                            # NPC is attacked by enemy!
                            if (enemy_npc_ref.get_current_frame("Boxing")
                                    and enemy_npc_ref.get_current_frame("Boxing") >= 23
                                    and enemy_npc_ref.get_current_frame("Boxing") <= 25):
                                self.base.npcs_hits[actor_name] = True
                                if actor:
                                    request.request("Attacked", actor, "BigHitToHead", "Boxing", "play")

    def npc_neutral_logic(self, actor, player, player_fsm, request, ai_behaviors,
                          npcs_xyz_vec, npcs_fsm_states, near_npc, passive):
        if (actor and player and player_fsm and request and npcs_xyz_vec and npcs_fsm_states
                and isinstance(passive, bool)
                and isinstance(near_npc, dict)
                and isinstance(npcs_xyz_vec, dict)):
            vect = {"panic_dist": 5,
                    "relax_dist": 5,
                    "wander_radius": 5,
                    "plane_flag": 0,
                    "area_of_effect": 10}

            # Add :BS suffix since we'll get Bullet Shape NodePath here
            # actor_bs_name = "{0}:BS".format(actor.get_name())
            actor_name = actor.get_name()
            # actor_npc_bs = actor.get_parent()
            # actor.set_blend(frameBlend=True)

            # Leave it here for debugging purposes
            # self.get_npc_hits()

            # if npcs_xyz_vec.get(actor_bs_name):
            # vec_x = npcs_xyz_vec[actor_bs_name].length()

            if passive:
                # Just stay
                request.request("Idle", actor, "LookingAround", "loop")

            elif passive is False:
                # If NPC is far from Player, do pursue Player
                if (ai_behaviors[actor_name].behavior_status("pursue") == "disabled"
                        or ai_behaviors[actor_name].behavior_status("pursue") == "active"):
                    request.request("Walk", actor, player, ai_behaviors[actor_name],
                                    "pathfind", "Walking", vect, "loop")

                    # If NPC is close to Player, just stay
                    if ai_behaviors[actor_name].behavior_status("pursue") == "done":
                        # TODO: Change action to something more suitable
                        request.request("Idle", actor, "LookingAround", "loop")

    def npc_enemy_logic(self, actor, player, player_fsm, request, ai_behaviors,
                        npcs_xyz_vec, npcs_fsm_states, near_npc, passive):
        if (actor and player and player_fsm and request and npcs_xyz_vec and npcs_fsm_states
                and isinstance(passive, bool)
                and isinstance(near_npc, dict)
                and isinstance(npcs_xyz_vec, dict)
                and hasattr(self.base, "alive_actors")
                and self.base.alive_actors):

            # Get the time that elapsed since last frame
            dt = globalClock.getDt()

            vect = {"panic_dist": 5,
                    "relax_dist": 5,
                    "wander_radius": 5,
                    "plane_flag": 0,
                    "area_of_effect": 10}

            # Add :BS suffix since we'll get Bullet Shape NodePath here
            actor_bs_name = "{0}:BS".format(actor.get_name())
            actor_name = actor.get_name()

            # actor_npc_bs = self.base.get_actor_bullet_shape_node(asset=actor_name, type="NPC")
            # actor_npc_bs = actor.get_parent()

            # actor.set_blend(frameBlend=True)

            # Leave it here for debugging purposes
            # self.get_npc_hits()

            vec_x = None
            if npcs_xyz_vec.get(actor_bs_name):
                vec_x = npcs_xyz_vec[actor_bs_name].length()

            # Just stay
            if passive and self.base.alive_actors[actor_name]:
                request.request("Idle", actor, "LookingAround", "loop")

            elif passive is False and self.base.alive_actors[actor_name]:
                # Get required data about enemy to deal with it
                enemy_npc_ref = None
                for k in base.npcs_actor_refs:
                    if actor.get_name() not in k:
                        if self.base.npcs_hits.get(k):
                            enemy_npc_ref = base.npcs_actor_refs[k]

                enemy_fsm_request = None
                for fsm_name in npcs_fsm_states:
                    if actor.get_name() not in fsm_name:
                        if self.base.npcs_hits.get(fsm_name):
                            enemy_fsm_request = npcs_fsm_states[fsm_name]

                enemy_npc_bs = None
                if enemy_npc_ref and enemy_fsm_request:
                    enemy_npc_ref_name = enemy_npc_ref.get_name()
                    if hasattr(self.base, "ai_chars_bs") and self.base.ai_chars_bs:
                        enemy_npc_bs = self.base.ai_chars_bs[enemy_npc_ref_name]

                # print(self.base.npcs_hits)

                # If NPC is far from Player/NPC, do pursue Player/NPC
                if ai_behaviors.get(actor_name):
                    if (ai_behaviors[actor_name].behavior_status("pursue") == "disabled"
                            or ai_behaviors[actor_name].behavior_status("pursue") == "active"):
                        if self.base.npcs_hits.get(actor_name):
                            request.request("Walk", actor, enemy_npc_bs, ai_behaviors[actor_name],
                                            "pathfind", "Walking", vect, "loop")
                        if not self.base.npcs_hits.get(actor_name):
                            request.request("Walk", actor, player, ai_behaviors[actor_name],
                                            "pathfind", "Walking", vect, "loop")

                    if vec_x == 1.0 or vec_x == -1.0:
                        ai_behaviors[actor_name].pause_ai("pursue")
                        near_npc[actor_name] = True
                    else:
                        ai_behaviors[actor_name].resume_ai("pursue")
                        near_npc[actor_name] = False
                        request.request("Walk", actor, player, ai_behaviors[actor_name],
                                        "pathfind", "Walking", vect, "loop")

                    # If NPC is close to Player/NPC, do enemy attack
                    if ai_behaviors[actor_name].behavior_status("pursue") == "paused":
                        if enemy_npc_ref:

                            if hasattr(self.base, 'npcs_active_actions'):
                                self.base.npcs_active_actions[enemy_npc_ref.get_name()] = None
                                self.base.npcs_active_actions[actor_name] = "Boxing"
                            request.request("Attack", actor, "Boxing", "loop")
                        else:
                            if hasattr(self.base, 'npcs_active_actions'):
                                self.base.npcs_active_actions[self.base.player_ref.get_name()] = None
                                self.base.npcs_active_actions[actor_name] = "Boxing"
                            request.request("Attack", actor, "Boxing", "loop")

                        # Player/NPC is attacked by enemy!
                        if (actor.get_current_frame("Boxing") >= 23
                                and actor.get_current_frame("Boxing") <= 25):
                            if enemy_npc_ref:
                                self.base.npcs_hits[enemy_npc_ref.get_name()] = True
                                player_fsm.request("Attacked", enemy_npc_ref, "BigHitToHead", "play")

                        if (actor.get_current_frame("Boxing") >= 23
                                and actor.get_current_frame("Boxing") <= 25
                                and self.base.player_states["is_blocking"] is False):
                            if not enemy_npc_ref:
                                for k in self.base.npcs_hits:
                                    self.base.npcs_hits[k] = False
                                player_fsm.request("Attacked", self.base.player_ref, "BigHitToHead", "play")

                        # Enemy is attacked by player!
                        if (self.base.player_states["is_hitting"]
                                and self.base.alive_actors[actor_name]):
                            if (self.base.player_ref.get_current_frame("Boxing") >= 23
                                    and self.base.player_ref.get_current_frame("Boxing") <= 25):
                                # Enemy does a block
                                request.request("Block", actor, "center_blocking", "Boxing", "play")

                            # Enemy health decreased when enemy miss a hits
                            if (actor.get_current_frame("center_blocking")
                                    and actor.get_current_frame("center_blocking") == 1):
                                if hasattr(base, "npcs_actors_health") and base.npcs_actors_health:
                                    if base.npcs_actors_health[actor_name].getPercent() != 0:
                                        base.npcs_actors_health[actor_name]['value'] -= 5
                                request.request("Attacked", actor, "BigHitToHead", "Boxing", "play")

                            # Temporary thing, leave it here
                            """if (hasattr(base, "npcs_actors_health")
                                    and base.npcs_actors_health):
                                value = base.npcs_actors_health[actor_name]['value']
                                self.dbg_text_npc_frame_hit.setText(str(value) + actor_name)"""

                            # Enemy will die if no health or flee:
                            if (hasattr(base, "npcs_actors_health")
                                    and base.npcs_actors_health):
                                if base.npcs_actors_health[actor_name].getPercent() != 0:
                                    # Evade or attack the player
                                    if base.npcs_actors_health[actor_name].getPercent() == 50.0:
                                        near_npc[actor_name] = False
                                        ai_behaviors[actor_name].remove_ai("pursue")
                                        request.request("Walk", actor, player, ai_behaviors[actor_name],
                                                        "evader", "Walking", vect, "loop")
                                    pass
                                else:
                                    request.request("Death", actor, "Dying", "play")
                                    self.base.alive_actors[actor_name] = False
                                    ai_behaviors[actor_name].pause_ai("pursue")
                                    near_npc[actor_name] = False

                        # Enemy is attacked by opponent!
                        if enemy_npc_ref and not self.base.player_states["is_hitting"]:
                            request.request("Attack", actor, "Boxing", "play")
                            if (actor.get_current_frame("Boxing") >= 23
                                    and actor.get_current_frame("Boxing") <= 25):
                                if enemy_npc_ref:
                                    self.base.npcs_hits[enemy_npc_ref.get_name()] = True
                                    enemy_fsm_request.request("Attacked", enemy_npc_ref, "BigHitToHead", "Boxing",
                                                              "play")

                                # Enemy does a block
                                request.request("Block", actor, "center_blocking", "Boxing", "play")

                            # Enemy health decreased when enemy miss a hits
                            if (actor.get_current_frame("center_blocking")
                                    and actor.get_current_frame("center_blocking") == 1):
                                if hasattr(base, "npcs_actors_health") and base.npcs_actors_health:
                                    if base.npcs_actors_health[actor_name].getPercent() != 0:
                                        base.npcs_actors_health[actor_name]['value'] -= 5
                                request.request("Attacked", actor, "BigHitToHead", "Boxing", "play")

                            # Enemy will die if no health or flee:
                            if (hasattr(base, "npcs_actors_health")
                                    and base.npcs_actors_health):
                                if base.npcs_actors_health[actor_name].getPercent() != 0:
                                    # Evade or attack the player
                                    if base.npcs_actors_health[actor_name].getPercent() == 50.0:
                                        near_npc[actor_name] = False
                                        ai_behaviors[actor_name].remove_ai("pursue")
                                        request.request("Walk", actor, enemy_npc_bs, ai_behaviors[actor_name],
                                                        "evader", "Walking", vect, "loop")
                                    pass
                                else:
                                    request.request("Death", actor, "Dying", "play")
                                    self.base.alive_actors[actor_name] = False
                                    ai_behaviors[actor_name].pause_ai("pursue")
                                    near_npc[actor_name] = False

                    # Enemy returns back
                    if base.npcs_actors_health[actor_name]:
                        if (base.npcs_actors_health[actor_name].getPercent() == 50.0
                                and vec_x == 10.0 or vec_x == -10.0
                                and ai_behaviors[actor_name].behavior_status("evade") == "paused"):
                            ai_behaviors[actor_name].remove_ai("evade")
                            # TODO: Change action to something more suitable
                            request.request("Idle", actor, "LookingAround", "loop")