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

                    for actor_cls in assets["class"]:
                        if actor_cls:

                            if "env" in actor_cls:
                                continue
                            elif "hero" in actor_cls:
                                continue

                            if self.actor and self.player:
                                speed = 6

                                # Do not duplicate if name is exist
                                if self.actor.get_name() not in self.npc_fsm.npcs_names:
                                    self.npc_fsm.npcs_names.append(self.actor.get_name())

                                # Reset object(s) for every method call to prevent Assertion errors
                                if self.ai_char:
                                    self.ai_world.remove_ai_char(actor_cls)
                                    self.ai_world.remove_ai_char(self.actor.get_name())
                                    self.ai_world = AIWorld(render)
                                    self.npc_fsm.state = "Off"

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
                # self.ai_world.update()
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
                        self.npc_fsm.request("Walk", self.actor, self.player, self.ai_behaviors,
                                             "seek", "Walking", "loop")

                    if int(self.npc_fsm.npcs_xyz_vec[name][0]) < 2:
                        self.npc_fsm.request("Walk", self.actor, self.player, self.ai_behaviors,
                                             "flee", "Walking", "loop")

                    if int(self.npc_fsm.npcs_xyz_vec[name][0]) < 1:
                        self.npc_fsm.request("Walk", self.actor, self.player, self.ai_behaviors,
                                             "evader", "Walking", "loop")

                    if int(self.npc_fsm.npcs_xyz_vec[name][0]) > 1:
                        self.npc_fsm.request("Walk", self.actor, self.player, self.ai_behaviors,
                                             "wanderer", "Walking", "loop")

                    if int(self.npc_fsm.npcs_xyz_vec[name][0]) < 1:
                        self.npc_fsm.request("Walk", self.actor, self.player, self.ai_behaviors,
                                             "obs_avoid", "Walking", "loop")

                    if int(self.npc_fsm.npcs_xyz_vec[name][0]) > 1:
                        self.npc_fsm.request("Walk", self.actor, self.player, self.ai_behaviors,
                                             "path_follow", "Walking", "loop")

                    if int(self.npc_fsm.npcs_xyz_vec[name][0]) > 1:
                        self.npc_fsm.request("Walk", self.actor, self.player, self.ai_behaviors,
                                             "path_finding", "Walking", "loop")

        if base.game_mode is False and base.menu_mode:
            return task.done

        return task.cont

    def npc_friend_logic(self, boolean):
        if (self.actor and boolean and self.npc_fsm.npcs_xyz_vec
                and isinstance(self.npc_fsm.npcs_xyz_vec, dict)):
            name = self.actor.get_name()
            vec_x = self.npc_fsm.npcs_xyz_vec[name][0]

            # Get correct NodePath
            self.actor = render.find("*/{0}".format(self.actor.get_name()))

            # If NPC is far from Player
            if vec_x > 1.0 or vec_x < -1.0:
                self.npc_fsm.request("Walk", self.actor, self.player, self.ai_behaviors,
                                     "pursuer", "Walking", "loop")

            # If NPC is close to Player, just stay
            elif self.ai_behaviors.behavior_status("pursue") == "done":
                # TODO: Change action to something more suitable
                self.npc_fsm.request("Idle", self.actor, "LookingAround", "loop")

            """# If NPC is close to Player, do attack
            elif self.ai_behaviors.behavior_status("pursue") == "done":
                self.npc_fsm.request("Attack", self.actor, "Boxing", "loop")"""

    def npc_neutral_logic(self, boolean):
        if (self.actor and boolean and self.npc_fsm.npcs_xyz_vec
                and isinstance(self.npc_fsm.npcs_xyz_vec, dict)):
            name = self.actor.get_name()
            vec_x = int(self.npc_fsm.npcs_xyz_vec[name][0])

            # Get correct NodePath
            self.actor = render.find("*/{0}".format(self.actor.get_name()))

            # If NPC is far from Player
            if vec_x > 1.0 or vec_x < -1.0:
                self.npc_fsm.request("Walk", self.actor, self.player, self.ai_behaviors,
                                     "pursuer", "Walking", "loop")

            # If NPC is close to Player, just stay
            elif self.ai_behaviors.behavior_status("pursue") == "done":
                # TODO: Change action to something more suitable
                self.npc_fsm.request("Idle", self.actor, "LookingAround", "loop")

    def npc_enemy_logic(self, boolean):
        if (self.actor and boolean and self.npc_fsm.npcs_xyz_vec
                and isinstance(self.npc_fsm.npcs_xyz_vec, dict)):
            name = self.actor.get_name()
            vec_x = int(self.npc_fsm.npcs_xyz_vec[name][0])

            # Get correct NodePath
            self.actor = render.find("*/{0}".format(self.actor.get_name()))

            # If NPC is far from Player
            if vec_x > 1.0 or vec_x < -1.0:
                self.npc_fsm.request("Walk", self.actor, self.player, self.ai_behaviors,
                                     "pursuer", "Walking", "loop")

            # If NPC is close to Player, just stay
            elif self.ai_behaviors.behavior_status("pursue") == "done":
                # TODO: Change action to something more suitable
                self.npc_fsm.request("Idle", self.actor, "LookingAround", "loop")

            # If NPC is close to Player, do attack
            elif self.ai_behaviors.behavior_status("pursue") == "done":
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
