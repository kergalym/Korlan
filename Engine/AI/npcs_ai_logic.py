from direct.task.TaskManagerGlobal import taskMgr
from panda3d.core import Vec3, Vec2

from Engine.Physics.npc_physics import NpcPhysics


class NpcsAILogic:

    def __init__(self, ai_world, ai_behaviors, ai_chars, ai_chars_bs, player,
                 player_fsm, npcs_fsm_states, npc_classes):
        self.base = base
        self.ai_world = ai_world
        self.ai_behaviors = ai_behaviors
        self.ai_chars = ai_chars
        self.ai_chars_bs = ai_chars_bs
        self.player = player
        self.player_fsm = player_fsm
        self.npc_physics = NpcPhysics()
        self.npcs_fsm_states = npcs_fsm_states
        self.npc_classes = npc_classes
        self.npc_rotations = {}
        self.start_attack = False
        self.navmesh_query = self.base.game_instance["navmesh_query"]
        if not self.navmesh_query:
            self.base.game_instance["use_pandai"] = True
        else:
            self.base.game_instance["use_pandai"] = False

        self.vect = {"panic_dist": 5,
                     "relax_dist": 5,
                     "wander_radius": 5,
                     "plane_flag": 0,
                     "area_of_effect": 10}

        taskMgr.add(self.update_pathfinding_task,
                    "update_pathfinding_task",
                    appendTask=True)

        taskMgr.add(self.update_npc_actions_task,
                    "update_npc_actions_task",
                    appendTask=True)

        for name in self.ai_chars_bs:
            actor = self.base.game_instance['actors_ref'][name]
            actor.get_python_tag("generic_states")['is_idle'] = True
            actor.set_blend(frameBlend=True)
            name_bs = "{0}:BS".format(name)
            actor_bs = self.base.game_instance['actors_np'][name_bs]
            request = self.npcs_fsm_states[name]

            # todo: yurt place actions

            taskMgr.add(self.npc_physics.actor_hitbox_trace_task,
                        "{0}_hitboxes_task".format(name.lower()),
                        extraArgs=[actor, actor_bs, request], appendTask=True)

    def update_pathfinding_task(self, task):
        if self.ai_chars_bs and self.ai_world and self.ai_behaviors:
            for actor_name in self.ai_behaviors:
                self.ai_chars[actor_name].set_max_force(5)

                for name in self.ai_chars_bs:
                    if "Horse" not in name:
                        # Add actors as obstacles except actor that avoids them
                        if name != actor_name and "Ernar" in name:
                            ai_char_bs = self.ai_chars_bs[name]
                            if ai_char_bs:
                                # self.ai_behaviors[actor_name].path_find_to(ai_char_bs, "addPath")
                                self.ai_behaviors[actor_name].add_dynamic_obstacle(ai_char_bs)
                                # self.ai_behaviors[actor_name].path_find_to(self.player, "addPath")
                                self.ai_behaviors[actor_name].add_dynamic_obstacle(self.player)
                                # Obstacle avoidance behavior
                                self.ai_behaviors[actor_name].obstacle_avoidance(1.0)
                                self.ai_world.add_obstacle(self.base.box_np)

            return task.done

    def update_npc_actions_task(self, task):
        if self.base.game_instance['loading_is_done'] == 1:
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
                                                  npcs_fsm_states=self.npcs_fsm_states,
                                                  passive=False)
                        if npc_class == "neutral":
                            self.npc_neutral_logic(actor=actor,
                                                   player=self.player,
                                                   request=request,
                                                   npcs_fsm_states=self.npcs_fsm_states,
                                                   passive=True)
                        if npc_class == "enemy":
                            self.npc_enemy_logic(actor=actor,
                                                 player=self.player,
                                                 player_fsm=self.player_fsm,
                                                 request=request,
                                                 npcs_fsm_states=self.npcs_fsm_states,
                                                 passive=False)
        return task.cont

    def set_npc_class(self, actor, npc_classes):
        if (actor and npc_classes
                and isinstance(npc_classes, dict)):

            for actor_cls in npc_classes:
                if actor_cls in actor.get_name():
                    return npc_classes[actor_cls]

    def actor_rotate(self, actor_npc_bs, path_points):
        current_dir = actor_npc_bs.get_hpr()

        for i in range(len(path_points) - 1):
            new_hpr = Vec3(Vec2(0, -1).signed_angle_deg(path_points[i + 1].xy - path_points[i].xy), current_dir[1],
                           current_dir[2])
            actor_npc_bs.set_hpr(new_hpr)
            # actor_npc_bs.hprInterval(0, new_hpr)

    def is_ready_for_staying(self, actor):
        if (actor.get_python_tag("generic_states")['is_moving']
                and not actor.get_python_tag("generic_states")['is_running']
                and not actor.get_python_tag("generic_states")['is_crouch_moving']
                and not actor.get_python_tag("generic_states")['is_crouching']
                and not actor.get_python_tag("generic_states")['is_jumping']
                and not actor.get_python_tag("generic_states")['is_attacked']
                and not actor.get_python_tag("generic_states")['is_busy']
                and not actor.get_python_tag("generic_states")['is_using']
                and not actor.get_python_tag("generic_states")['is_turning']
                and not actor.get_python_tag("human_states")['horse_riding']
                and not actor.get_python_tag("human_states")['is_on_horse']):
            return True
        else:
            return False

    def is_ready_for_walking(self, actor):
        if (actor.get_python_tag("generic_states")['is_idle']
                and not actor.get_python_tag("generic_states")['is_running']
                and not actor.get_python_tag("generic_states")['is_crouch_moving']
                and not actor.get_python_tag("generic_states")['is_crouching']
                and not actor.get_python_tag("generic_states")['is_jumping']
                and not actor.get_python_tag("generic_states")['is_attacked']
                and not actor.get_python_tag("generic_states")['is_busy']
                and not actor.get_python_tag("generic_states")['is_using']
                and not actor.get_python_tag("generic_states")['is_turning']
                and not actor.get_python_tag("human_states")['horse_riding']
                and not actor.get_python_tag("human_states")['is_on_horse']):
            return True
        else:
            return False

    def npc_in_staying_logic(self, actor, request):
        if actor and request:
            if self.base.game_instance["use_pandai"]:
                if self.is_ready_for_staying(actor):
                    actor_name = actor.get_name()
                    if (self.ai_behaviors[actor_name].behavior_status("pursue") == "disabled"
                            or self.ai_behaviors[actor_name].behavior_status("pursue") == "done"):
                        if self.ai_behaviors[actor_name].behavior_status("pursue") != "disabled":
                            self.ai_behaviors[actor_name].remove_ai("pursue")
                        actor.get_python_tag("generic_states")['is_moving'] = False
                        actor.get_python_tag("generic_states")['is_idle'] = True
            else:
                if self.is_ready_for_staying(actor):
                    actor.get_python_tag("generic_states")['is_moving'] = False
                    actor.get_python_tag("generic_states")['is_idle'] = True

            if actor.get_python_tag("generic_states")['is_idle']:
                if actor.get_python_tag("generic_states")['is_crouch_moving']:
                    request.request("Idle", actor, "standing_to_crouch", "loop")
                elif not actor.get_python_tag("generic_states")['is_crouch_moving']:
                    request.request("Idle", actor, "Standing_idle_male", "loop")

    def npc_in_walking_logic(self, actor, actor_npc_bs, oppo_npc_bs, request):
        if actor and actor_npc_bs and oppo_npc_bs and request:
            actor_name = actor.get_name()

            if self.base.game_instance["use_pandai"]:
                if self.is_ready_for_walking(actor):
                    if (self.ai_behaviors[actor_name].behavior_status("pursue") == "disabled"
                            or self.ai_behaviors[actor_name].behavior_status("pursue") == "done"):
                        actor.get_python_tag("generic_states")['is_idle'] = False
                        actor.get_python_tag("generic_states")['is_moving'] = True
            else:
                if self.is_ready_for_walking(actor):
                    actor.get_python_tag("generic_states")['is_idle'] = False
                    actor.get_python_tag("generic_states")['is_moving'] = True

            if actor.get_python_tag("generic_states")['is_moving']:
                request.request("Walk", actor, oppo_npc_bs,
                                self.ai_chars_bs,
                                self.ai_behaviors[actor_name],
                                "pursuer", "Walking", self.vect, "loop")

            if self.navmesh_query:
                # Start path from actor's pose
                pos = actor_npc_bs.get_pos()
                current_dir = actor_npc_bs.get_hpr()

                self.navmesh_query.nearest_point(pos)
                # Set last pos from opposite actor's pos
                last_pos = oppo_npc_bs.get_pos()

                # Find path
                path = self.navmesh_query.find_path(pos, last_pos)
                path_points = list(path.points)

                for i in range(len(path_points) - 1):
                    speed = 5
                    # Rotation
                    new_hpr = Vec3(Vec2(0, -1).signed_angle_deg(path_points[i + 1].xy - path_points[i].xy),
                                   current_dir[1],
                                   current_dir[2])
                    actor_npc_bs.set_hpr(new_hpr)

                    # Movement
                    dist = (path_points[i + 1] - path_points[i]).length()
                    # dist / speed
                    actor_npc_bs.set_pos(path_points[i+speed])

    def npc_in_gathering_logic(self, actor, request):
        pass

    def npc_in_attacking_logic(self, actor, actor_npc_bs, dt, request):
        if (actor.get_python_tag("generic_states")['is_idle']
                and not actor.get_python_tag("generic_states")['is_attacked']
                and not actor.get_python_tag("generic_states")['is_busy']
                and not actor.get_python_tag("generic_states")['is_moving']):
            action = ""
            if (actor.get_python_tag("human_states")
                    and actor.get_python_tag("human_states")['has_sword']):
                action = "great_sword_slash"
            else:
                action = "Boxing"

            if actor_npc_bs.get_y() != actor_npc_bs.get_y() - 2:
                actor_npc_bs.set_y(actor_npc_bs, -2 * dt)
                request.request("ForwardRoll", actor, "forward_roll", "play")
            elif actor_npc_bs.get_y() != actor_npc_bs.get_y() + 2:
                actor_npc_bs.set_y(actor_npc_bs, 2 * dt)
                request.request("ForwardRoll", actor, "forward_roll", "play")
            request.request("Attack", actor, action, "play")
            if actor_npc_bs.get_x() != actor_npc_bs.get_x() - 2:
                actor_npc_bs.set_x(actor_npc_bs, -2 * dt)
                request.request("ForwardRoll", actor, "forward_roll", "play")
            elif actor_npc_bs.get_x() != actor_npc_bs.get_x() + 2:
                actor_npc_bs.set_x(actor_npc_bs, 2 * dt)
                request.request("ForwardRoll", actor, "forward_roll", "play")

    def face_actor_to(self, actor, target, dt):
        if actor and target and dt:
            if actor.get_h() != 45.0:
                if actor.get_h() != actor.get_h() - target.get_h():
                    vec_h = actor.get_h() - target.get_h()
                    actor.set_h(actor, vec_h * dt)

    def get_enemy_ref(self, exclude_cls):
        if exclude_cls and isinstance(exclude_cls, str):
            for k, cls in zip(self.base.game_instance['actors_ref'], self.npc_classes):
                if self.npc_classes[cls] != exclude_cls:
                    return self.base.game_instance['actors_ref'][k]

    def get_enemy_bs(self, exclude_cls):
        if exclude_cls and isinstance(exclude_cls, str):
            for k, cls in zip(self.base.game_instance['actors_ref'], self.npc_classes):
                if self.npc_classes[cls] != exclude_cls:
                    enemy_npc_ref = self.base.game_instance['actors_ref'][k]
                    return self.ai_chars_bs[enemy_npc_ref.get_name()]

    def get_enemy_vector(self, actor_npc_bs, exclude_cls):
        if actor_npc_bs and exclude_cls:
            for k, cls in zip(self.base.game_instance['actors_ref'], self.npc_classes):
                if self.npc_classes[cls] != exclude_cls:
                    enemy_npc_ref = self.base.game_instance['actors_ref'][k]
                    enemy_npc_bs = self.ai_chars_bs[enemy_npc_ref.get_name()]
                    if enemy_npc_bs:
                        return int(actor_npc_bs.get_distance(enemy_npc_bs))

    def npc_friend_logic(self, actor, player, request,
                         npcs_fsm_states, passive):
        if (actor and player and request and npcs_fsm_states
                and self.ai_chars_bs
                and isinstance(passive, bool)):
            if actor.get_python_tag("generic_states")['is_alive']:
                # Get the time that elapsed since last frame
                dt = globalClock.getDt()

                # Add :BS suffix since we'll get Bullet Shape NodePath here
                actor_name = actor.get_name()
                self.ai_chars[actor_name].set_max_force(5)

                if passive:
                    # Just stay
                    if "Horse" not in actor.get_name():
                        self.npc_in_staying_logic(actor, request)

                if passive is False:
                    # Get required data about enemy to deal with it
                    actor_npc_bs = self.base.get_actor_bullet_shape_node(asset=actor_name, type="NPC")
                    enemy_npc_ref = self.get_enemy_ref(exclude_cls="friend")
                    enemy_npc_bs = self.get_enemy_bs(exclude_cls="friend")

                    player_dist = int(actor_npc_bs.get_distance(player))
                    enemy_dist = self.get_enemy_vector(actor_npc_bs=actor_npc_bs, exclude_cls="friend")

                    if base.player_states['is_alive']:
                        # If NPC is far from Player, do pursue Player
                        if player_dist > 1:
                            self.npc_in_walking_logic(actor, actor_npc_bs, player, request)
                        elif player_dist <= 1:
                            # if not actor.get_python_tag("generic_states")['is_busy']:
                            self.npc_in_staying_logic(actor, request)
                            # self.npc_in_gathering_logic(actor, request)

                        if self.base.game_instance['player_ref'].get_current_frame("Boxing"):

                            # Leave this here for debugging purposes
                            """if player_dist <= 1:
                                if not actor.get_python_tag("generic_states")['is_busy']:
                                    self.npc_in_attacking_logic(actor, player, dt, request)
                            """

                            if not self.start_attack:
                                self.start_attack = True
                    else:
                        self.npc_in_staying_logic(actor, request)

                    if enemy_npc_ref.get_python_tag("generic_states")['is_alive']:
                        # Friendly NPC starts attacking the opponent when player first starts attacking it
                        if self.start_attack:
                            if enemy_dist > 1:
                                self.npc_in_walking_logic(actor, actor_npc_bs, enemy_npc_bs, request)
                            elif enemy_dist <= 1:
                                self.npc_in_staying_logic(actor, request)

                            if self.base.game_instance['player_ref'].get_current_frame("Boxing"):
                                if enemy_dist <= 1:
                                    # if not actor.get_python_tag("generic_states")['is_busy']:
                                    self.npc_in_attacking_logic(actor, enemy_npc_bs, dt, request)
                    else:
                        self.npc_in_staying_logic(actor, request)

    def npc_neutral_logic(self, actor, player, request,
                          npcs_fsm_states, passive):
        if (actor and player and request and npcs_fsm_states
                and isinstance(passive, bool)):
            if actor.get_python_tag("generic_states")['is_alive']:
                actor_name = actor.get_name()
                self.ai_chars[actor_name].set_max_force(5)

                if passive:
                    # Just stay
                    self.npc_in_staying_logic(actor, request)

                elif passive is False:
                    actor_npc_bs = self.base.get_actor_bullet_shape_node(asset=actor_name, type="NPC")
                    # Get required data about enemy to deal with it
                    enemy_npc_ref = self.get_enemy_ref(exclude_cls="friend")
                    enemy_npc_bs = self.get_enemy_bs(exclude_cls="friend")

                    player_dist = int(actor_npc_bs.get_distance(player))
                    enemy_dist = self.get_enemy_vector(actor_npc_bs=actor_npc_bs, exclude_cls="friend")

                    if base.player_states['is_alive']:
                        # If NPC is far from Player, do pursue Player
                        if player_dist > 1:
                            self.npc_in_walking_logic(actor, actor_npc_bs, player, request)
                        elif player_dist <= 1:
                            self.npc_in_staying_logic(actor, request)
                    else:
                        self.npc_in_staying_logic(actor, request)

                    if enemy_npc_ref.get_python_tag("generic_states")['is_alive']:
                        if enemy_dist > 1:
                            self.npc_in_walking_logic(actor, actor_npc_bs, enemy_npc_bs, request)
                        elif enemy_dist <= 1:
                            self.npc_in_staying_logic(actor, request)
                    else:
                        self.npc_in_staying_logic(actor, request)

    def npc_enemy_logic(self, actor, player, player_fsm, request,
                        npcs_fsm_states, passive):
        if (actor and player and player_fsm and request and npcs_fsm_states
                and isinstance(passive, bool)):
            if actor.get_python_tag("generic_states")['is_alive']:
                # Get the time that elapsed since last frame
                dt = globalClock.getDt()

                # Add :BS suffix since we'll get Bullet Shape NodePath here
                actor_name = actor.get_name()
                self.ai_chars[actor_name].set_max_force(5)

                # Just stay
                if passive:
                    self.npc_in_staying_logic(actor, request)

                elif passive is False:
                    # Get required data about enemy to deal with it
                    actor_npc_bs = self.base.get_actor_bullet_shape_node(asset=actor_name, type="NPC")
                    enemy_npc_ref = self.get_enemy_ref(exclude_cls="enemy")
                    enemy_npc_bs = self.get_enemy_bs(exclude_cls="enemy")

                    player_dist = int(actor_npc_bs.get_distance(player))
                    enemy_dist = self.get_enemy_vector(actor_npc_bs=actor_npc_bs, exclude_cls="enemy")

                    if base.player_states['is_alive']:
                        # If NPC is far from Player, do pursue Player
                        if player_dist > 1:
                            self.npc_in_walking_logic(actor, actor_npc_bs, player, request)
                        elif player_dist <= 1:
                            self.npc_in_staying_logic(actor, request)
                            # self.npc_in_gathering_logic(actor, request)
                            if self.base.game_instance['player_ref'].get_current_frame("Boxing"):
                                self.npc_in_attacking_logic(actor, player, dt, request)
                    else:
                        self.npc_in_staying_logic(actor, request)

                    if enemy_npc_ref.get_python_tag("generic_states")['is_alive']:
                        # If NPC is far from enemy, do pursue enemy
                        if enemy_dist > 1:
                            self.npc_in_walking_logic(actor, actor_npc_bs, enemy_npc_bs, request)
                        elif enemy_dist <= 1:
                            self.npc_in_staying_logic(actor, request)
                            if self.base.game_instance['player_ref'].get_current_frame("Boxing"):
                                self.npc_in_attacking_logic(actor, enemy_npc_bs, dt, request)
                    else:
                        self.npc_in_staying_logic(actor, request)

                    """# Enemy returns back
                        if actor.get_python_tag("health_np"):
                            if (actor.get_python_tag("health_np")['value'] == 50.0
                                    and vec == 10.0 or vec == -10.0
                                    and ai_behaviors[actor_name].behavior_status("evade") == "paused"):
                                ai_behaviors[actor_name].remove_ai("evade")
                                # TODO: Change action to something more suitable
                                request.request("Idle", actor, "Standing_idle_male", "loop")"""
