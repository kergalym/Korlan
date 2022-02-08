from direct.task.TaskManagerGlobal import taskMgr
from panda3d.core import BitMask32


class NpcsAI:

    def __init__(self, ai_world, ai_behaviors, ai_chars, ai_chars_bs, player,
                 player_fsm, npcs_fsm_states, npc_classes):
        self.base = base
        self.ai_world = ai_world
        self.ai_behaviors = ai_behaviors
        self.ai_chars = ai_chars
        self.ai_chars_bs = ai_chars_bs
        self.player = player
        self.player_fsm = player_fsm
        self.npcs_fsm_states = npcs_fsm_states
        self.npc_classes = npc_classes
        self.npc_rotations = {}
        self.start_attack = False

        taskMgr.add(self.update_npc_states_task,
                    "update_npc_states_task",
                    appendTask=True)

        taskMgr.add(self.update_pathfinding_task,
                    "update_pathfinding_task",
                    appendTask=True)

        for name in self.ai_chars_bs:
            actor = self.base.game_instance['actors_ref'][name]
            actor.set_blend(frameBlend=True)
            name_bs = "{0}:BS".format(name)
            actor_bs = self.base.game_instance['actors_np'][name_bs]
            request = self.npcs_fsm_states[name]
            taskMgr.add(self.actor_hitbox_trace_task,
                        "{0}_hitboxes_task".format(name.lower()),
                        extraArgs=[actor, actor_bs, request], appendTask=True)

    def actor_hitbox_trace_task(self, actor, actor_bs, request, task):
        if self.base.game_instance['menu_mode']:
            return task.done

        if actor and actor_bs and actor.find("**/**Hips:HB") and request:
            parent_node = actor.find("**/**Hips:HB").node()
            for node in parent_node.get_overlapping_nodes():
                damage_weapons = actor.get_python_tag("damage_weapons")
                for weapon in damage_weapons:
                    if weapon in node.get_name():
                        node.set_into_collide_mask(BitMask32.allOff())
                        request.request("Attacked", actor, "HitToBody", "Standing_idle_male", "play")
                        if actor.get_python_tag("health_np"):
                            if actor.get_python_tag("health_np")['value'] > 0:
                                actor.get_python_tag("health_np")['value'] -= 1
                            else:
                                if actor.get_python_tag("generic_states")['is_alive']:
                                    actor.get_python_tag("generic_states")['is_alive'] = False
                                    actor.play("Dying")
        return task.cont

    def update_pathfinding_task(self, task):
        if self.ai_chars_bs and self.ai_world and self.ai_behaviors:
            for actor_name in self.ai_behaviors:
                self.ai_chars[actor_name].set_max_force(5)

                for name in self.ai_chars_bs:
                    if "Horse" not in name:
                        # Add actors as obstacles except actor that avoids them
                        if name != actor_name:
                            ai_char_bs = self.ai_chars_bs[name]
                            if ai_char_bs:
                                # self.ai_behaviors[actor_name].path_find_to(ai_char_bs, "addPath")
                                self.ai_behaviors[actor_name].add_dynamic_obstacle(ai_char_bs)
                                # self.ai_behaviors[actor_name].path_find_to(self.player, "addPath")
                                self.ai_behaviors[actor_name].add_dynamic_obstacle(self.player)
                                # Obstacle avoidance behavior
                                # self.ai_behaviors[actor_name].obstacle_avoidance(1.0)
                                # self.ai_world.add_obstacle(ai_char_bs)

            return task.done

    def face_actor_to(self, actor, target, dt):
        if actor and target and dt:
            if actor.get_h() != 45.0:
                if actor.get_h() != actor.get_h() - target.get_h():
                    vec_h = actor.get_h() - target.get_h()
                    actor.set_h(actor, vec_h * dt)

    def set_npc_class(self, actor, npc_classes):
        if (actor and npc_classes
                and isinstance(npc_classes, dict)):

            for actor_cls in npc_classes:
                if actor_cls in actor.get_name():
                    return npc_classes[actor_cls]

    def npc_in_staying_logic(self, actor, request):
        if actor.get_python_tag("generic_states")['is_crouch_moving']:
            request.request("Idle", actor, "standing_to_crouch", "loop")
        elif not actor.get_python_tag("generic_states")['is_crouch_moving']:
            request.request("Idle", actor, "Standing_idle_male", "loop")

    def npc_in_gathering_logic(self):
        pass

    def npc_in_attacking_logic(self, actor, actor_npc_bs, dt, request):
        action = ""
        if (actor.get_python_tag("human_states")
                and actor.get_python_tag("human_states")['has_sword']):
            action = "great_sword_slash"
        else:
            action = "Boxing"
        """if actor_npc_bs.get_y() != actor_npc_bs.get_y() - 2:
            actor_npc_bs.set_y(actor_npc_bs, -2 * dt)
            request.request("ForwardRoll", actor, "forward_roll", "Standing_idle_male", "play")
        elif actor_npc_bs.get_y() != actor_npc_bs.get_y() + 2:
            actor_npc_bs.set_y(actor_npc_bs, 2 * dt)
            request.request("ForwardRoll", actor, "forward_roll", "Standing_idle_male", "play")"""
        request.request("Attack", actor, action, "Standing_idle_male", "play")
        """if actor_npc_bs.get_x() != actor_npc_bs.get_x() - 2:
            actor_npc_bs.set_x(actor_npc_bs, -2 * dt)
            request.request("ForwardRoll", actor, "forward_roll", "Standing_idle_male", "play")
        elif actor_npc_bs.get_x() != actor_npc_bs.get_x() + 2:
            actor_npc_bs.set_x(actor_npc_bs, 2 * dt)
            request.request("ForwardRoll", actor, "forward_roll", "Standing_idle_male", "play")"""

    def npc_friend_logic(self, actor, player, request, ai_behaviors,
                         npcs_fsm_states, passive):
        if (actor and player and request and npcs_fsm_states
                and self.ai_chars_bs
                and isinstance(passive, bool)):
            if actor.get_python_tag("generic_states")['is_alive']:
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
                self.ai_chars[actor_name].set_max_force(5)
                actor_ref = self.base.game_instance['actors_ref'][actor_name]

                if passive:
                    # Just stay
                    if "Horse" not in actor.get_name():
                        self.npc_in_staying_logic(actor, request)

                if passive is False:
                    # Get required data about enemy to deal with it
                    enemy_npc_bs = None
                    for k, cls in zip(self.base.game_instance['actors_ref'], self.npc_classes):
                        if actor.get_name() not in k and "Horse" not in k:
                            if self.npc_classes[cls] != "friend":
                                enemy_npc_ref = self.base.game_instance['actors_ref'][k]
                                enemy_npc_bs = self.ai_chars_bs[enemy_npc_ref.get_name()]

                    player_vec = int(actor_npc_bs.get_distance(player))
                    enemy_vec = 0
                    if enemy_npc_bs:
                        enemy_vec = int(actor_npc_bs.get_distance(enemy_npc_bs))

                    if not self.start_attack:
                        # If NPC is far from Player, do pursue Player
                        if (ai_behaviors[actor_name].behavior_status("pursue") == "disabled"
                                or ai_behaviors[actor_name].behavior_status("pursue") == "done"):
                            if player_vec <= 1:
                                ai_behaviors[actor_name].remove_ai("pursue")
                                self.npc_in_staying_logic(actor, request)
                                if (actor_ref.get_python_tag("health_np")['value']
                                        < actor_ref.get_python_tag("health_np")['range']):
                                    self.npc_in_attacking_logic(actor, player, dt, request)

                            elif player_vec > 1:
                                request.request("Walk", actor, player, self.ai_chars_bs,
                                                ai_behaviors[actor_name],
                                                "pursuer", "Walking", vect, "loop")

                    # If NPC is far from enemy, do pursue enemy
                    """if self.base.game_instance['player_ref'].get_current_frame("Boxing"):
                        if not self.start_attack:
                            self.start_attack = True

                        if (ai_behaviors[actor_name].behavior_status("pursue") == "disabled"
                                or ai_behaviors[actor_name].behavior_status("pursue") == "done"):
                            if enemy_vec <= 1:
                                if "Horse" not in actor.get_name():
                                    if ai_behaviors[actor_name].behavior_status("pursue") != "disabled":
                                        ai_behaviors[actor_name].remove_ai("pursue")
                                    self.npc_in_staying_logic(actor, request)

                                    # Friendly NPC starts attacking the opponent when player first starts attacking it
                                    if "Horse" not in actor.get_name():
                                        # self.set_actor_heading(actor_npc_bs, enemy_npc_bs, dt)
                                        self.npc_in_attacking_logic(actor, actor_npc_bs, dt,  request)

                            elif enemy_vec > 1:
                                if "Horse" not in actor.get_name():
                                    request.request("Walk", actor, enemy_npc_bs,
                                                    self.ai_chars_bs,
                                                    ai_behaviors[actor_name],
                                                    "pursuer", "Walking", vect, "loop")"""

    def npc_neutral_logic(self, actor, player, request, ai_behaviors,
                          npcs_fsm_states, passive):
        if (actor and player and request and npcs_fsm_states
                and isinstance(passive, bool)):
            if actor.get_python_tag("generic_states")['is_alive']:
                vect = {"panic_dist": 5,
                        "relax_dist": 5,
                        "wander_radius": 5,
                        "plane_flag": 0,
                        "area_of_effect": 10}

                actor_name = actor.get_name()
                self.ai_chars[actor_name].set_max_force(5)

                if passive:
                    # Just stay
                    self.npc_in_staying_logic(actor, request)

                elif passive is False:
                    # If NPC is far from Player, do pursue Player
                    if (ai_behaviors[actor_name].behavior_status("pursue") == "disabled"
                            or ai_behaviors[actor_name].behavior_status("pursue") == "done"):
                        request.request("Walk", actor, player, self.ai_chars_bs,
                                        ai_behaviors[actor_name],
                                        "pursuer", "Walking", vect, "loop")

    def npc_enemy_logic(self, actor, player, player_fsm, request, ai_behaviors,
                        npcs_fsm_states, passive):
        if (actor and player and player_fsm and request and npcs_fsm_states
                and isinstance(passive, bool)):
            if actor.get_python_tag("generic_states")['is_alive']:
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
                self.ai_chars[actor_name].set_max_force(5)

                # Just stay
                if passive:
                    self.npc_in_staying_logic(actor, request)

                elif passive is False:
                    # Get required data about enemy to deal with it
                    enemy_npc_bs = None
                    for k, cls in zip(self.base.game_instance['actors_ref'], self.npc_classes):
                        if actor.get_name() not in k and "Horse" not in k:
                            if self.npc_classes[cls] != "enemy":
                                enemy_npc_ref = self.base.game_instance['actors_ref'][k]
                                enemy_npc_bs = self.ai_chars_bs[enemy_npc_ref.get_name()]

                    player_vec = int(actor_npc_bs.get_distance(player))
                    enemy_vec = 0
                    if enemy_npc_bs:
                        enemy_vec = int(actor_npc_bs.get_distance(enemy_npc_bs))

                    # If NPC is far from Player, do pursue Player
                    """if (ai_behaviors[actor_name].behavior_status("pursue") == "disabled"
                            or ai_behaviors[actor_name].behavior_status("pursue") == "done"):
                        if player_vec <= 1:
                            if ai_behaviors[actor_name].behavior_status("pursue") != "disabled":
                                ai_behaviors[actor_name].remove_ai("pursue")
                            self.npc_in_staying_logic(actor, request)
                        elif player_vec > 1:
                            request.request("Walk", actor, player, self.ai_chars_bs,
                                            ai_behaviors[actor_name],
                                            "pursuer", "Walking", vect, "loop")
                    """
                    # If NPC is far from enemy, do pursue enemy
                    if self.base.game_instance['player_ref'].get_current_frame("Boxing"):
                        if (ai_behaviors[actor_name].behavior_status("pursue") == "disabled"
                                or ai_behaviors[actor_name].behavior_status("pursue") == "done"):
                            if enemy_vec <= 1:
                                if "Horse" not in actor.get_name():
                                    if ai_behaviors[actor_name].behavior_status("pursue") != "disabled":
                                        ai_behaviors[actor_name].remove_ai("pursue")
                                    self.npc_in_staying_logic(actor, request)

                                    # NPC starts attacking the opponent when player first starts attacking it
                                    if "Horse" not in actor.get_name():
                                        self.npc_in_attacking_logic(actor, actor_npc_bs, dt, request)

                            elif enemy_vec > 1:
                                if "Horse" not in actor.get_name():
                                    request.request("Walk", actor, enemy_npc_bs,
                                                    self.ai_chars_bs,
                                                    ai_behaviors[actor_name],
                                                    "pursuer", "Walking", vect, "loop")

                    """# Enemy returns back
                        if actor.get_python_tag("health_np"):
                            if (actor.get_python_tag("health_np")['value'] == 50.0
                                    and vec == 10.0 or vec == -10.0
                                    and ai_behaviors[actor_name].behavior_status("evade") == "paused"):
                                ai_behaviors[actor_name].remove_ai("evade")
                                # TODO: Change action to something more suitable
                                request.request("Idle", actor, "Standing_idle_male", "loop")"""

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
                                              passive=False)
                    """if npc_class == "neutral":
                        self.npc_neutral_logic(actor=actor,
                                               player=self.player,
                                               request=request,
                                               ai_behaviors=self.ai_behaviors,
                                               npcs_fsm_states=self.npcs_fsm_states,
                                               passive=True)
                    if npc_class == "enemy":
                        self.npc_enemy_logic(actor=actor,
                                             player=self.player,
                                             player_fsm=self.player_fsm,
                                             request=request,
                                             ai_behaviors=self.ai_behaviors,
                                             npcs_fsm_states=self.npcs_fsm_states,
                                             passive=False)"""
        return task.cont
