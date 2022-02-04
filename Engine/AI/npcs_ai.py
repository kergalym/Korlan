from direct.task.TaskManagerGlobal import taskMgr
from direct.gui.OnscreenText import OnscreenText


class NpcsAI:

    def __init__(self, ai_world, ai_behaviors, ai_chars, ai_chars_bs, player,
                 player_fsm, npcs_fsm_states, npc_classes, near_npc):
        self.base = base
        self.ai_world = ai_world
        self.ai_behaviors = ai_behaviors
        self.ai_chars = ai_chars
        self.ai_chars_bs = ai_chars_bs
        self.player = player
        self.player_fsm = player_fsm
        self.npcs_fsm_states = npcs_fsm_states
        self.npc_classes = npc_classes
        self.near_npc = near_npc

        self.dbg_text_npc_frame_hit = OnscreenText(text="",
                                                   pos=(0.5, 0.0),
                                                   scale=0.2,
                                                   fg=(255, 255, 255, 0.9),
                                                   mayChange=True)

        self.dbg_text_plr_frame_hit = OnscreenText(text="",
                                                   pos=(0.5, -0.2),
                                                   scale=0.2,
                                                   fg=(255, 255, 255, 1.1),
                                                   mayChange=True)

        taskMgr.add(self.keep_actor_pitch_task,
                    "keep_actor_pitch_task",
                    appendTask=True)

        taskMgr.add(self.update_npc_states_task,
                    "update_npc_states_task",
                    appendTask=True)

        """taskMgr.add(self.update_pathfinding_task,
                    "update_pathfinding_task",
                    appendTask=True)"""

    def keep_actor_pitch_task(self, task):
        # Fix me: Dirty hack for path finding issue
        # when actor's pitch changes for reasons unknown for me xD

        if self.base.game_instance['actors_ref']:
            for actor in self.base.game_instance['actors_ref']:
                if not self.base.game_instance['actors_ref'][actor].is_empty():
                    # Prevent pitch changing
                    self.base.game_instance['actors_ref'][actor].set_p(0)
                    self.base.game_instance['actors_ref'][actor].get_parent().set_p(0)

        return task.cont

    def set_actor_heading(self, actor, opponent, dt):
        if actor and opponent and dt:
            vec_h = 2 * actor.get_h() - opponent.get_h()
            actor.set_h(actor, vec_h * dt)

    def set_actor_heading_once(self, actor, degree, dt):
        if actor and degree and dt:
            if actor.get_h() - degree != actor.get_h():
                actor.set_h(actor, degree * dt)

    def set_npc_class(self, actor, npc_classes):
        if (actor and not actor.is_empty()
                and npc_classes
                and isinstance(npc_classes, dict)):

            for actor_cls in npc_classes:
                if actor_cls in actor.get_name():
                    return npc_classes[actor_cls]

    def update_pathfinding_task(self, task):
        if self.ai_chars_bs and self.ai_world and self.ai_behaviors:
            for actor_name in self.ai_behaviors:
                self.ai_chars[actor_name].set_max_force(7)

                for name in self.ai_chars_bs:
                    # Add actors as obstacles except actor that avoids them
                    if name != actor_name:
                        ai_char_bs = self.ai_chars_bs[name]
                        if ai_char_bs:
                            self.ai_behaviors[actor_name].path_find_to(ai_char_bs, "addPath")
                            # self.ai_behaviors[actor_name].add_dynamic_obstacle(ai_char_bs)

                            # Obstacle avoidance behavior
                            # self.ai_behaviors[actor_name].obstacle_avoidance(1.0)
                            # self.ai_world.add_obstacle(ai_char_bs)

            return task.done

    def update_npc_states_task(self, task):
        if (self.player
                and self.base.game_instance['actors_ref']):
            for actor_name, fsm_name in zip(self.base.game_instance['actors_ref'], self.npcs_fsm_states):
                actor = self.base.game_instance['actors_ref'][actor_name]
                request = self.npcs_fsm_states[fsm_name]
                npc_class = self.set_npc_class(actor=actor,
                                               npc_classes=self.npc_classes)

                if npc_class and "Horse" not in actor_name:
                    if npc_class == "friend":
                        self.npc_friend_logic(actor=actor,
                                              player=self.player,
                                              request=request,
                                              ai_behaviors=self.ai_behaviors,
                                              npcs_fsm_states=self.npcs_fsm_states,
                                              near_npc=self.near_npc,
                                              passive=False)
                    if npc_class == "neutral":
                        self.npc_neutral_logic(actor=actor,
                                               player=self.player,
                                               request=request,
                                               ai_behaviors=self.ai_behaviors,
                                               npcs_fsm_states=self.npcs_fsm_states,
                                               near_npc=self.near_npc,
                                               passive=True)
                    if npc_class == "enemy":
                        self.npc_enemy_logic(actor=actor,
                                             player=self.player,
                                             player_fsm=self.player_fsm,
                                             request=request,
                                             ai_behaviors=self.ai_behaviors,
                                             npcs_fsm_states=self.npcs_fsm_states,
                                             near_npc=self.near_npc,
                                             passive=False)
        return task.cont

    def npc_friend_logic(self, actor, player, request, ai_behaviors,
                         npcs_fsm_states, near_npc, passive):
        if (actor and player and request and npcs_fsm_states
                and isinstance(passive, bool)
                and isinstance(near_npc, dict)):

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
            actor_npc_bs = self.base.get_actor_bullet_shape_node(asset=actor_name, type="NPC")
            # actor.set_blend(frameBlend=True)

            if passive:
                # Just stay
                if "Horse" not in actor.get_name():
                    request.request("Idle", actor, "Standing_idle_male", "loop")

            if passive is False:
                # Get required data about enemy to deal with it
                enemy_npc_ref = None
                for k in self.base.game_instance['actors_ref']:
                    if actor.get_name() not in k:
                        enemy_npc_ref = self.base.game_instance['actors_ref'][k]

                enemy_npc_bs = None
                if enemy_npc_ref:
                    enemy_npc_ref_name = enemy_npc_ref.get_name()
                    if self.ai_chars_bs:
                        # fixme, Mongol
                        enemy_npc_bs = self.ai_chars_bs[enemy_npc_ref_name]

                enemy_fsm_request = None
                for fsm_name in npcs_fsm_states:
                    if actor.get_name() not in fsm_name:
                        enemy_fsm_request = npcs_fsm_states[fsm_name]

                player_vec = int(actor_npc_bs.get_distance(player))
                enemy_vec = actor_npc_bs.get_distance(enemy_npc_bs)

                # If NPC is far from Player, do pursue Player
                if ai_behaviors.get(actor_name):
                    if (ai_behaviors[actor_name].behavior_status("pursue") == "disabled"
                            or ai_behaviors[actor_name].behavior_status("pursue") == "active"):
                        if player_vec == 1:
                            ai_behaviors[actor_name].pause_ai("pursue")
                            near_npc[actor_name] = True
                        else:
                            ai_behaviors[actor_name].resume_ai("pursue")
                            near_npc[actor_name] = False
                            request.request("Walk", actor, player, self.ai_chars_bs,
                                            ai_behaviors[actor_name],
                                            "pathfind", "Walking", vect, "loop")

                    # If NPC is far from enemy, do pursue enemy
                if (ai_behaviors[actor_name].behavior_status("pursue") == "disabled"
                        or ai_behaviors[actor_name].behavior_status("pursue") == "active"):
                    if enemy_vec == 1.0 or enemy_vec == -1.0:
                        if "Horse" not in actor.get_name():
                            request.request("Walk", actor, enemy_npc_bs,
                                            self.ai_chars_bs,
                                            ai_behaviors[actor_name],
                                            "pathfind", "Walking", vect, "loop")

                    # If NPC is close to Enemy, do enemy attack
                    if (ai_behaviors[actor_name].behavior_status("pursue") == "done"
                            or ai_behaviors[actor_name].behavior_status("pursue") == "paused"):
                        if "Horse" not in actor.get_name():
                            request.request("Idle", actor, "Standing_idle_male", "loop")

                        # Friendly NPC starts attacking the opponent when player first starts attacking it
                        if self.base.game_instance['player_ref'].get_current_frame("Boxing"):
                            if "Horse" not in actor.get_name():
                                request.request("Attack", actor, "Boxing", "play")
                                if (actor.get_current_frame("Boxing") >= 23
                                        and actor.get_current_frame("Boxing") <= 25):
                                    enemy_fsm_request.request("Attacked", enemy_npc_ref, "BigHitToHead", "Boxing",
                                                              "play")

                            # NPC is attacked by enemy!
                            if (enemy_npc_ref.get_current_frame("Boxing")
                                    and enemy_npc_ref.get_current_frame("Boxing") >= 23
                                    and enemy_npc_ref.get_current_frame("Boxing") <= 25):
                                if actor:
                                    if "Horse" not in actor.get_name():
                                        request.request("Attacked", actor, "BigHitToHead", "Boxing", "play")

    def npc_neutral_logic(self, actor, player, request, ai_behaviors,
                          npcs_fsm_states, near_npc, passive):
        if (actor and player and request and npcs_fsm_states
                and isinstance(passive, bool)
                and isinstance(near_npc, dict)):
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
                request.request("Idle", actor, "Standing_idle_male", "loop")

            elif passive is False:
                # If NPC is far from Player, do pursue Player
                if (ai_behaviors[actor_name].behavior_status("pursue") == "disabled"
                        or ai_behaviors[actor_name].behavior_status("pursue") == "active"):
                    request.request("Walk", actor, player, self.ai_chars_bs,
                                    ai_behaviors[actor_name],
                                    "pathfind", "Walking", vect, "loop")

                    # If NPC is close to Player, just stay
                    if ai_behaviors[actor_name].behavior_status("pursue") == "done":
                        # TODO: Change action to something more suitable
                        request.request("Idle", actor, "Standing_idle_male", "loop")

    def npc_enemy_logic(self, actor, player, player_fsm, request, ai_behaviors,
                        npcs_fsm_states, near_npc, passive):
        if (actor and player and player_fsm and request and npcs_fsm_states
                and isinstance(passive, bool)
                and isinstance(near_npc, dict)):

            # Get the time that elapsed since last frame
            dt = globalClock.getDt()

            vect = {"panic_dist": 5,
                    "relax_dist": 5,
                    "wander_radius": 5,
                    "plane_flag": 0,
                    "area_of_effect": 10}

            # Add :BS suffix since we'll get Bullet Shape NodePath here
            actor_name = actor.get_name()
            actor_npc_bs = self.base.get_actor_bullet_shape_node(asset=actor_name, type="NPC")
            # actor.set_blend(frameBlend=True)

            vec = actor_npc_bs.get_distance(player)

            # Just stay
            if passive:
                request.request("Idle", actor, "Standing_idle_male", "loop")

            elif passive is False:
                # Get required data about enemy to deal with it
                enemy_npc_ref = None
                for k in self.base.game_instance['actors_ref']:
                    if actor.get_name() not in k:
                        enemy_npc_ref = self.base.game_instance['actors_ref'][k]

                enemy_fsm_request = None
                for fsm_name in npcs_fsm_states:
                    if actor.get_name() not in fsm_name:
                        enemy_fsm_request = npcs_fsm_states[fsm_name]

                enemy_npc_bs = None
                if enemy_npc_ref and enemy_fsm_request:
                    enemy_npc_ref_name = enemy_npc_ref.get_name()
                    if self.ai_chars_bs:
                        enemy_npc_bs = self.ai_chars_bs[enemy_npc_ref_name]

                # If NPC is far from Player/NPC, do pursue Player/NPC
                if ai_behaviors.get(actor_name):
                    if (ai_behaviors[actor_name].behavior_status("pursue") == "disabled"
                            or ai_behaviors[actor_name].behavior_status("pursue") == "active"):
                        request.request("Walk", actor, enemy_npc_bs, self.ai_chars_bs,
                                        ai_behaviors[actor_name],
                                        "pathfind", "Walking", vect, "loop")

                    if vec == 1.0 or vec == -1.0:
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
                                self.base.npcs_active_actions[self.base.game_instance['player_ref'].get_name()] = None
                                self.base.npcs_active_actions[actor_name] = "Boxing"
                            request.request("Attack", actor, "Boxing", "loop")

                        # Player/NPC is attacked by enemy!
                        if (actor.get_current_frame("Boxing") >= 23
                                and actor.get_current_frame("Boxing") <= 25):
                            if enemy_npc_ref:
                                player_fsm.request("Attacked", enemy_npc_ref, "BigHitToHead", "play")

                        if (actor.get_current_frame("Boxing") >= 23
                                and actor.get_current_frame("Boxing") <= 25
                                and self.base.player_states["is_blocking"] is False):
                            if not enemy_npc_ref:
                                player_fsm.request("Attacked", self.base.player_ref, "BigHitToHead", "play")

                        # Enemy is attacked by player!
                        if self.base.player_states["is_hitting"]:
                            if (self.base.game_instance['player_ref'].get_current_frame("Boxing") >= 23
                                    and self.base.game_instance['player_ref'].get_current_frame("Boxing") <= 25):
                                # Enemy does a block
                                request.request("Block", actor, "center_blocking", "Boxing", "play")

                            # Enemy health decreased when enemy miss a hits
                            if (actor.get_current_frame("center_blocking")
                                    and actor.get_current_frame("center_blocking") == 1):
                                if actor.get_python_tag("health_np"):
                                    if actor.get_python_tag("health_np")['value'] != 0:
                                        actor.get_python_tag("health_np")['value'] -= 5
                                request.request("Attacked", actor, "BigHitToHead", "Boxing", "play")

                            # Temporary thing, leave it here
                            """if actor.get_python_tag("health_np"):
                                value = actor.get_python_tag("health_np")['value']
                                self.dbg_text_npc_frame_hit.setText(str(value) + actor_name)"""

                            # Enemy will die if no health or flee:
                            if actor.get_python_tag("health_np"):
                                if actor.get_python_tag("health_np")['value'] != 0:
                                    # Evade or attack the player
                                    if actor.get_python_tag("health_np")['value'] == 50.0:
                                        near_npc[actor_name] = False
                                        ai_behaviors[actor_name].remove_ai("pursue")
                                        request.request("Walk", actor, player, self.ai_chars_bs,
                                                        ai_behaviors[actor_name],
                                                        "evader", "Walking", vect, "loop")
                                    pass
                                else:
                                    request.request("Death", actor, "Dying", "play")
                                    ai_behaviors[actor_name].pause_ai("pursue")
                                    near_npc[actor_name] = False

                        # Enemy is attacked by opponent!
                        if enemy_npc_ref and not self.base.player_states["is_hitting"]:
                            request.request("Attack", actor, "Boxing", "play")
                            if (actor.get_current_frame("Boxing") >= 23
                                    and actor.get_current_frame("Boxing") <= 25):
                                if enemy_npc_ref:
                                    enemy_fsm_request.request("Attacked", enemy_npc_ref, "BigHitToHead", "Boxing",
                                                              "play")

                                # Enemy does a block
                                request.request("Block", actor, "center_blocking", "Boxing", "play")

                            # Enemy health decreased when enemy miss a hits
                            if (actor.get_current_frame("center_blocking")
                                    and actor.get_current_frame("center_blocking") == 1):
                                if actor.get_python_tag("health_np"):
                                    if actor.get_python_tag("health_np")['value'] != 0:
                                        actor.get_python_tag("health_np")['value'] -= 5
                                request.request("Attacked", actor, "BigHitToHead", "Boxing", "play")

                            # Enemy will die if no health or flee:
                            if actor.get_python_tag("health_np"):
                                if actor.get_python_tag("health_np")['value'] != 0:
                                    # Evade or attack the player
                                    if actor.get_python_tag("health_np")['value'] == 50.0:
                                        near_npc[actor_name] = False
                                        ai_behaviors[actor_name].remove_ai("pursue")
                                        request.request("Walk", actor, enemy_npc_bs, self.ai_chars_bs,
                                                        ai_behaviors[actor_name],
                                                        "evader", "Walking", vect, "loop")
                                    pass
                                else:
                                    request.request("Death", actor, "Dying", "play")
                                    ai_behaviors[actor_name].pause_ai("pursue")
                                    near_npc[actor_name] = False

                    # Enemy returns back
                    if actor.get_python_tag("health_np"):
                        if (actor.get_python_tag("health_np")['value'] == 50.0
                                and vec == 10.0 or vec == -10.0
                                and ai_behaviors[actor_name].behavior_status("evade") == "paused"):
                            ai_behaviors[actor_name].remove_ai("evade")
                            # TODO: Change action to something more suitable
                            request.request("Idle", actor, "Standing_idle_male", "loop")
