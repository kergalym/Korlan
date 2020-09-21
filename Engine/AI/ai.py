from panda3d.ai import AIWorld
from panda3d.ai import AICharacter
from direct.task.TaskManagerGlobal import taskMgr
from Engine.FSM.player_fsm import PlayerFSM
from Engine.FSM.npc_fsm import NpcFSM


class AI:
    def __init__(self):
        self.base = base
        self.render = render
        self.taskMgr = taskMgr
        self.ai_world = AIWorld(render)
        self.player_fsm = PlayerFSM()
        self.npc_fsm = NpcFSM()
        self.ai_char = None
        self.actor = None
        self.player = None
        self.ai_behaviors = None

    def set_ai_world(self, assets, task):
        if assets and isinstance(assets, dict):
            if assets.get("name") and assets.get("class"):
                for actor in assets.get("name"):
                    if actor == "NPC":
                        actor = self.base.get_actor_bullet_shape_node(asset=actor, type="NPC")
                        self.actor = actor
                    if actor == "Player":
                        player = self.base.get_actor_bullet_shape_node(asset=actor, type="Player")
                        self.player = player

                    for actor_cls in assets.get("class"):
                        if actor_cls:
                            if "env" not in actor_cls or "hero" not in actor_cls:
                                if self.actor and self.player:
                                    speed = 6

                                    # Do not duplicate if name is exist
                                    if self.actor.get_name() not in self.npc_fsm.npcs_names:
                                        self.npc_fsm.npcs_names.append(self.actor.get_name())

                                    self.ai_char = AICharacter(actor_cls, self.actor, 100, 0.05, speed)
                                    self.ai_world.add_ai_char(self.ai_char)
                                    self.ai_behaviors = self.ai_char.get_ai_behaviors()

                                    taskMgr.add(self.update_ai_world_task,
                                                "update_ai_world",
                                                appendTask=True)

                                    taskMgr.add(self.update_npc_states_task,
                                                "update_npc_states_task",
                                                appendTask=True)

                                    taskMgr.add(self.npc_fsm.npc_distance_calculate_task,
                                                "npc_distance_calculate_task",
                                                extraArgs=[self.player, self.actor],
                                                appendTask=True)

                                    return task.done

        return task.cont

    def update_ai_world_task(self, task):
        if self.ai_world:
            # Oh... Workaround for evil assertion error, again!
            try:
                self.ai_world.update()
            except AssertionError:
                pass

        if base.game_mode is False and base.menu_mode:
            return task.done

        return task.cont

    def update_npc_states_task(self, task):
        if self.actor and self.player:
            npc_class = self.npc_fsm.set_npc_class(actor=self.actor)
            if npc_class and self.npc_fsm.npcs_xyz_vec:
                name = self.actor.get_name()
                if npc_class.get('class') == "friend":
                    self.npc_friend_logic(True)
                else:
                    if int(self.npc_fsm.npcs_xyz_vec[name][0]) > 1:
                        self.npc_fsm.request("Walk", self.actor, "Walking", "loop")
                        self.set_basic_npc_behaviors(actor=self.actor, behavior="seek")
                    if int(self.npc_fsm.npcs_xyz_vec[name][0]) < 2:
                        self.npc_fsm.request("Idle", self.actor, "Walking", "loop")
                        self.set_basic_npc_behaviors(actor=self.actor, behavior="flee")
                    if int(self.npc_fsm.npcs_xyz_vec[name][0]) < 1:
                        self.set_basic_npc_behaviors(actor=self.actor, behavior="evader")
                        self.npc_fsm.request("Idle", self.actor, "Walking", "loop")
                    if int(self.npc_fsm.npcs_xyz_vec[name][0]) > 1:
                        self.set_basic_npc_behaviors(actor=self.actor, behavior="wanderer")
                        self.npc_fsm.request("Walk", self.actor, "Walking", "loop")
                    if int(self.npc_fsm.npcs_xyz_vec[name][0]) < 1:
                        self.set_basic_npc_behaviors(actor=self.actor, behavior="obs_avoid")
                        self.npc_fsm.request("Idle", self.actor, "Walking", "loop")
                    if int(self.npc_fsm.npcs_xyz_vec[name][0]) > 1:
                        self.set_basic_npc_behaviors(actor=self.actor, behavior="path_follow")
                        self.npc_fsm.request("Idle", self.actor, "Walking", "loop")
                    if int(self.npc_fsm.npcs_xyz_vec[name][0]) > 1:
                        self.set_basic_npc_behaviors(actor=self.actor, behavior="path_finding")
                        self.npc_fsm.request("Idle", self.actor, "Walking", "loop")

        if base.game_mode is False and base.menu_mode:
            return task.done

        return task.cont

    def set_basic_npc_behaviors(self, actor, behavior):
        if (actor and self.player
                and not actor.is_empty()
                and not self.player.is_empty()
                and behavior
                and isinstance(behavior, str)):

            if self.ai_world and self.ai_behaviors:
                vect = {"panic_dist": 5,
                        "relax_dist": 5,
                        "wander_radius": 5,
                        "plane_flag": 0,
                        "area_of_effect": 10}

                navmeshes = self.base.navmesh_collector()
                self.ai_behaviors.init_path_find(navmeshes["lvl_one"])
                if behavior == "obs_avoid":
                    self.ai_behaviors.path_find_to(self.player, "addPath")
                    self.ai_behaviors.add_dynamic_obstacle(self.player)
                elif behavior == "seek":
                    self.ai_behaviors.path_find_to(self.player, "addPath")
                    self.ai_behaviors.seek(self.player)
                elif behavior == "flee":
                    self.ai_behaviors.path_find_to(self.player, "addPath")
                    self.ai_behaviors.flee(actor,
                                           vect['panic_dist'],
                                           vect['relax_dist'])
                elif behavior == "pursuer":
                    self.ai_behaviors.path_find_to(self.player, "addPath")
                    self.ai_behaviors.pursue(self.player)
                elif behavior == "evader":
                    self.ai_behaviors.path_find_to(self.player, "addPath")
                    self.ai_behaviors.evade(self.player,
                                            vect['panic_dist'],
                                            vect['relax_dist'])
                elif behavior == "wanderer":
                    self.ai_behaviors.path_find_to(self.player, "addPath")
                    self.ai_behaviors.wander(vect["wander_radius"],
                                             vect["plane_flag"],
                                             vect["area_of_effect"])
                elif behavior == "path_finding":
                    self.ai_behaviors.path_find_to(self.player, "addPath")
                elif behavior == "path_follow":
                    self.ai_behaviors.path_follow(1)
                    self.ai_behaviors.add_to_path(self.player.get_pos())
                    self.ai_behaviors.start_follow()

                taskMgr.add(self.npc_fsm.keep_actor_pitch_task,
                            "keep_actor_pitch",
                            extraArgs=[actor],
                            appendTask=True)

    def npc_friend_logic(self, boolean):
        if (self.actor and boolean and self.npc_fsm.npcs_xyz_vec
                and isinstance(self.npc_fsm.npcs_xyz_vec, dict)):
            name = self.actor.get_name()
            vec_x = int(self.npc_fsm.npcs_xyz_vec[name][0])

            # If NPC is far from Player
            if vec_x > 1:
                self.set_basic_npc_behaviors(actor=self.actor, behavior="path_follow")
                self.npc_fsm.request("Walk", self.actor, "Walking", "loop")

            # If NPC is close to Player, just stay
            if vec_x < 1:
                # TODO: Change action to something more suitable
                self.npc_fsm.request("Idle", self.actor, "LookingAround", "loop")

            """# If NPC is close to Player, do attack
            if vec_x < 1:
                self.request("Attack", self.actor, "Boxing", "loop")"""

    def npc_neutral_logic(self, boolean):
        if (self.actor and boolean and self.npc_fsm.npcs_xyz_vec
                and isinstance(self.npc_fsm.npcs_xyz_vec, dict)):
            name = self.actor.get_name()
            vec_x = int(self.npc_fsm.npcs_xyz_vec[name][0])

            # If NPC is far from Player, do walk
            if vec_x > 1:
                self.set_basic_npc_behaviors(actor=self.actor, behavior="path_follow")
                self.npc_fsm.request("Walk", self.actor, "Walking", "loop")

            # If NPC is close to Player, just stay
            if vec_x < 1:
                # TODO: Change action to something more suitable
                self.npc_fsm.request("Idle", self.actor, "LookingAround", "loop")

    def npc_enemy_logic(self, boolean):
        if (self.actor and boolean and self.npc_fsm.npcs_xyz_vec
                and isinstance(self.npc_fsm.npcs_xyz_vec, dict)):
            name = self.actor.get_name()
            vec_x = int(self.npc_fsm.npcs_xyz_vec[name][0])

            # If NPC is far from Player
            if vec_x > 1:
                self.set_basic_npc_behaviors(actor=self.actor, behavior="path_follow")
                self.npc_fsm.request("Walk", self.actor, "Walking", "loop")

            # If NPC is close to Player, just stay
            if vec_x < 1:
                # TODO: Change action to something more suitable
                self.npc_fsm.request("Idle", self.actor, "LookingAround", "loop")

            # If NPC is close to Player, do attack
            if vec_x < 1:
                self.npc_fsm.request("Attack", self.actor, "Boxing", "loop")

    def set_weather(self, weather):
        if weather and isinstance(weather, str):
            if weather == "wind":
                pass
            elif weather == "rain":
                pass
            elif weather == "storm":
                pass
            elif weather == "day":
                pass
            elif weather == "night":
                pass
