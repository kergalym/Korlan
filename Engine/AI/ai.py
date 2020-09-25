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
        self.ai_chars = {}
        self.player = None
        self.ai_behaviors = None

    def set_ai_world(self, assets, task):
        if (assets and isinstance(assets, dict)
                and hasattr(base, "npcs_actor_refs")
                and base.npcs_actor_refs):
            if assets.get("name") and assets.get("class"):
                actor = None

                for name, in zip(assets.get("name")):

                    if name == "Player":
                        self.player = self.base.get_actor_bullet_shape_node(asset=name, type="Player")

                    for actor_cls in assets["class"]:
                        if actor_cls:
                            if "env" in actor_cls:
                                continue
                            elif "hero" in actor_cls:
                                continue

                            for ref_name in base.npcs_actor_refs:
                                if "NPC" in ref_name:
                                    actor = self.base.get_actor_bullet_shape_node(asset=ref_name, type="NPC")

                                if actor and self.player:
                                    speed = 6

                                    # Do not duplicate if name is exist
                                    if actor.get_name() not in self.npc_fsm.npcs_names:
                                        self.npc_fsm.npcs_names.append(actor.get_name())

                                    # TODO: Add more characters
                                    # Reset object(s) for every method call to prevent Assertion errors
                                    if self.ai_char:
                                        # self.ai_world.remove_ai_char(actor_cls)
                                        # self.ai_world.remove_ai_char(actor.get_name())
                                        # self.ai_world = AIWorld(render)
                                        self.npc_fsm.state = "Off"

                                    self.ai_char = AICharacter(actor_cls, actor, 100, 0.05, speed)
                                    self.ai_world.add_ai_char(self.ai_char)
                                    self.ai_behaviors = self.ai_char.get_ai_behaviors()
                                    self.ai_chars[actor.get_name()] = actor

                                    taskMgr.add(self.npc_fsm.npc_distance_calculate_task,
                                                "npc_distance_calculate_task",
                                                extraArgs=[self.player, actor, base.npcs_actor_refs],
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

            # self.ai_world.print_list()

        if base.game_mode is False and base.menu_mode:
            return task.done

        return task.cont

    def update_npc_states_task(self, task):
        if (self.player
                and hasattr(base, 'npcs_actor_refs')
                and base.npcs_actor_refs):
            for actor_name in base.npcs_actor_refs:
                actor = base.npcs_actor_refs[actor_name]
                npc_class = self.npc_fsm.set_npc_class(actor=actor)
                if npc_class and self.npc_fsm.npcs_xyz_vec:

                    # Add :BS suffix since we'll get Bullet Shape NodePath here
                    actor_bs_name = "{0}:BS".format(actor.get_name())

                    if npc_class.get('class') == "friend":
                        self.npc_friend_logic(actor=actor, boolean=True)
                    if npc_class.get('class') == "enemy":
                        self.npc_enemy_logic(actor=actor, boolean=True)

                    else:
                        if int(self.npc_fsm.npcs_xyz_vec[actor_bs_name][0]) > 1:
                            self.npc_fsm.request("Walk", actor, self.player, self.ai_behaviors,
                                                 "seek", "Walking", "loop")

                        if int(self.npc_fsm.npcs_xyz_vec[actor_bs_name][0]) < 2:
                            self.npc_fsm.request("Walk", actor, self.player, self.ai_behaviors,
                                                 "flee", "Walking", "loop")

                        if int(self.npc_fsm.npcs_xyz_vec[actor_bs_name][0]) < 1:
                            self.npc_fsm.request("Walk", actor, self.player, self.ai_behaviors,
                                                 "evader", "Walking", "loop")

                        if int(self.npc_fsm.npcs_xyz_vec[actor_bs_name][0]) > 1:
                            self.npc_fsm.request("Walk", actor, self.player, self.ai_behaviors,
                                                 "wanderer", "Walking", "loop")

                        if int(self.npc_fsm.npcs_xyz_vec[actor_bs_name][0]) < 1:
                            self.npc_fsm.request("Walk", actor, self.player, self.ai_behaviors,
                                                 "obs_avoid", "Walking", "loop")

                        if int(self.npc_fsm.npcs_xyz_vec[actor_bs_name][0]) > 1:
                            self.npc_fsm.request("Walk", actor, self.player, self.ai_behaviors,
                                                 "path_follow", "Walking", "loop")

                        if int(self.npc_fsm.npcs_xyz_vec[actor_bs_name][0]) > 1:
                            self.npc_fsm.request("Walk", actor, self.player, self.ai_behaviors,
                                                 "path_finding", "Walking", "loop")

        if base.game_mode is False and base.menu_mode:
            return task.done

        return task.cont

    def npc_friend_logic(self, actor, boolean):
        if (actor and boolean and self.npc_fsm.npcs_xyz_vec
                and isinstance(self.npc_fsm.npcs_xyz_vec, dict)):

            # Add :BS suffix since we'll get Bullet Shape NodePath here
            actor_bs_name = "{0}:BS".format(actor.get_name())

            if actor_bs_name:
                vec_x = self.npc_fsm.npcs_xyz_vec[actor_bs_name][0]

                # If NPC is far from Player
                if vec_x > 1.0 or vec_x < -1.0:
                    self.npc_fsm.request("Walk", actor, self.player, self.ai_behaviors,
                                         "pursuer", "Walking", "loop")

                # If NPC is close to Player, just stay
                elif self.ai_behaviors.behavior_status("pursue") == "done":
                    # TODO: Change action to something more suitable
                    self.npc_fsm.request("Idle", actor, "LookingAround", "loop")

                """# If NPC is close to Player, do attack
                elif self.ai_behaviors.behavior_status("pursue") == "done":
                    self.npc_fsm.request("Attack", actor, "Boxing", "loop")"""

    def npc_neutral_logic(self, actor, boolean):
        if (actor and boolean and self.npc_fsm.npcs_xyz_vec
                and isinstance(self.npc_fsm.npcs_xyz_vec, dict)):

            # Add :BS suffix since we'll get Bullet Shape NodePath here
            actor_bs_name = "{0}:BS".format(actor.get_name())

            if actor_bs_name:
                vec_x = self.npc_fsm.npcs_xyz_vec[actor_bs_name][0]

                # If NPC is far from Player
                if vec_x > 1.0 or vec_x < -1.0:
                    self.npc_fsm.request("Walk", actor, self.player, self.ai_behaviors,
                                         "pursuer", "Walking", "loop")

                # If NPC is close to Player, just stay
                elif self.ai_behaviors.behavior_status("pursue") == "done":
                    # TODO: Change action to something more suitable
                    self.npc_fsm.request("Idle", actor, "LookingAround", "loop")

    def npc_enemy_logic(self, actor, boolean):
        if (actor and boolean and self.npc_fsm.npcs_xyz_vec
                and isinstance(self.npc_fsm.npcs_xyz_vec, dict)):

            # Add :BS suffix since we'll get Bullet Shape NodePath here
            actor_bs_name = "{0}:BS".format(actor.get_name())

            if actor_bs_name:
                import pdb; pdb.set_trace()
                vec_x = self.npc_fsm.npcs_xyz_vec[actor_bs_name][0]

                # If NPC is far from Player
                if vec_x > 1.0 or vec_x < -1.0:
                    self.npc_fsm.request("Walk", actor, self.player, self.ai_behaviors,
                                         "pursuer", "Walking", "loop")

                # If NPC is close to Player, just stay
                elif self.ai_behaviors.behavior_status("pursue") == "done":
                    # TODO: Change action to something more suitable
                    self.npc_fsm.request("Idle", actor, "LookingAround", "loop")

                # If NPC is close to Player, do attack
                elif self.ai_behaviors.behavior_status("pursue") == "done":
                    self.npc_fsm.request("Attack", actor, "Boxing", "loop")

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
