from direct.fsm.FSM import FSM
from direct.task.TaskManagerGlobal import taskMgr
from panda3d.ai import AIWorld
from panda3d.ai import AICharacter
from Engine.Actors.NPC.state import NpcState
from Engine.FSM.player_fsm import FsmPlayer
from Engine.Actors.NPC.Classes.npc_husband import Husband


class NpcAI(FSM):
    def __init__(self):
        FSM.__init__(self, "NpcAI")
        self.base = base
        self.render = render
        self.taskMgr = taskMgr
        self.ai_world = AIWorld(render)
        self.npc_state = NpcState()
        self.ai_char = None
        self.actor = None
        self.player = None
        self.ai_behaviors = None
        self.fsm_player = FsmPlayer()
        self.husband = Husband()
        self.npcs_names = []
        self.npcs_xyz_vec = {}

        """Behavior states"""
        base.npc_states = {
            "idle": False,
            "walk": False,
            "swim": False,
            "stay": False,
            "jump": False,
            "crouch": False,
            "lay": False,
            "attack": False,
            "f_attack": False,
            "h_attack": False,
            "block": False,
            "interact": False,
            "life": False,
            "death": False,
            "misc_act": False,
            "obs_avoid": False
        }

    def npc_distance_calculate_task(self, task):
        if self.npcs_names and isinstance(self.npcs_names, list):
            for npc in self.npcs_names:

                # Drop :BS suffix since we'll get Bullet Shape Nodepath here
                # by our special get_actor_bullet_shape_node()
                npc = npc.split(":")[0]

                actor = self.base.get_actor_bullet_shape_node(asset=npc, type="NPC")
                xyz_vec = self.base.npc_distance_calculate(player=self.player, actor=actor)

                if xyz_vec:
                    tuple_xyz_vec = xyz_vec['vector']
                    # Here we put tuple xyz values to our class member npcs_xyz_vec
                    # for every actor name like 'NPC_Ernar:BS'
                    self.npcs_xyz_vec = {actor.get_name(): tuple_xyz_vec}

        if base.game_mode is False and base.menu_mode:
            return task.done

        return task.cont

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
                                    if self.actor.get_name() not in self.npcs_names:
                                        self.npcs_names.append(self.actor.get_name())

                                    self.ai_char = AICharacter(actor_cls, self.actor, 100, 0.05, speed)
                                    self.ai_world.add_ai_char(self.ai_char)
                                    self.ai_behaviors = self.ai_char.get_ai_behaviors()

                                    taskMgr.add(self.npc_distance_calculate_task,
                                                "npc_distance_calculate_task",
                                                appendTask=True)

                                    taskMgr.add(self.update_npc_states_task,
                                                "update_npc_states_task",
                                                appendTask=True)

                                    taskMgr.add(self.update_ai_world_task,
                                                "update_ai_world",
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

    def keep_actor_pitch_task(self, actor, task):
        if actor:
            # Prevent pitch changing
            actor.set_p(0)
            if base.game_mode is False and base.menu_mode:
                return task.done
        return task.cont

    def update_npc_states_task(self, task):
        if self.actor and self.player:
            npc_class = self.set_npc_class(actor=self.actor)
            if npc_class:
                name = self.actor.get_name()
                if npc_class.get('class') == "friend":
                    self.npc_friend_logic(True)
                else:
                    if int(self.npcs_xyz_vec[name][0]) > 1:
                        self.request("Walk", self.actor, "Walking", "loop")
                        self.set_basic_npc_behaviors(actor=self.actor, behavior="seek")
                    if int(self.npcs_xyz_vec[name][0]) < 2:
                        self.request("Idle", self.actor, "LookingAround", "loop")
                        self.set_basic_npc_behaviors(actor=self.actor, behavior="flee")
                    if int(self.npcs_xyz_vec[name][0]) < 1:
                        self.set_basic_npc_behaviors(actor=self.actor, behavior="evader")
                        self.request("Idle", self.actor, "LookingAround", "loop")
                    if int(self.npcs_xyz_vec[name][0]) > 1:
                        self.set_basic_npc_behaviors(actor=self.actor, behavior="wanderer")
                        self.request("Walk", self.actor, "Walking", "loop")
                    if int(self.npcs_xyz_vec[name][0]) < 1:
                        self.set_basic_npc_behaviors(actor=self.actor, behavior="obs_avoid")
                        self.request("Idle", self.actor, "LookingAround", "loop")
                    if int(self.npcs_xyz_vec[name][0]) > 1:
                        self.set_basic_npc_behaviors(actor=self.actor, behavior="path_follow")
                        self.request("Idle", self.actor, "LookingAround", "loop")
                    if int(self.npcs_xyz_vec[name][0]) > 1:
                        self.set_basic_npc_behaviors(actor=self.actor, behavior="path_finding")
                        self.request("Idle", self.actor, "LookingAround", "loop")

        if base.game_mode is False and base.menu_mode:
            return task.done

        return task.cont

    def set_npc_class(self, actor):
        if actor and not actor.is_empty():
            if self.husband.name in self.actor.get_name():
                return {'class': 'friend'}
            # test
            elif "NPC" in self.husband.name:
                return {'class': 'friend'}

            # elif self.mongol_warrior.name in self.actor.get_name():
                # return {'class': 'enemy'}

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

                taskMgr.add(self.keep_actor_pitch_task,
                            "keep_actor_pitch",
                            extraArgs=[actor],
                            appendTask=True)

    def npc_friend_logic(self, bool):
        if (self.actor and bool and self.npcs_xyz_vec
                and isinstance(self.npcs_xyz_vec, dict)):
            name = self.actor.get_name()
            states = base.npc_states
            vec_x = int(self.npcs_xyz_vec[name][0])

            # If NPC is far from Player and is not attacking, do attack
            if vec_x > 1:
                if not states['walk']:
                    self.set_basic_npc_behaviors(actor=self.actor, behavior="path_follow")
                    self.request("Walk", self.actor, "Walking", "loop", states)
            # If NPC is far from Player and is attacking, make it stop attack and pursue Player
            elif vec_x > 1 and states['attack']:
                states['walk'] = False

            # If NPC is close to Player, just stay
            if vec_x < 1:
                if not states['idle']:
                    # TODO: Change action to something more suitable
                    self.request("Idle", self.actor, "LookingAround", "loop", states)
            # If NPC is close to Player and is doing attack, just stay
            elif vec_x > 1 and states['attack']:
                states['idle'] = False

            # If NPC is close to Player, do attack
            if vec_x < 1:
                if not states['attack']:
                    self.request("Attack", self.actor, "Boxing", "loop", states)
            # If NPC is far from Player and is doing attack, stop it
            elif vec_x > 1 and not states['attack']:
                states['attack'] = True

    def npc_neutral_logic(self, bool):
        if (self.actor and bool and self.npcs_xyz_vec
                and isinstance(self.npcs_xyz_vec, dict)):
            name = self.actor.get_name()
            states = base.npc_states
            if int(self.npcs_xyz_vec[name][0]) > 1 and not states['walk']:
                self.set_basic_npc_behaviors(actor=self.actor, behavior="flee")
                self.request("Walk", self.actor, "Walking", "loop", states)
            if int(self.npcs_xyz_vec[name][0]) < 1 and not states['idle']:
                self.set_basic_npc_behaviors(actor=self.actor, behavior="path_follow")
                # TODO: Change action to something more suitable
                self.request("Idle", self.actor, "LookingAround", "loop", states)

    def npc_enemy_logic(self, bool):
        if (self.actor and bool and self.npcs_xyz_vec
                and isinstance(self.npcs_xyz_vec, dict)):
            name = self.actor.get_name()
            states = base.npc_states
            if int(self.npcs_xyz_vec[name][0]) > 1 and not states['walk']:
                self.set_basic_npc_behaviors(actor=self.actor, behavior="pursuer")
                self.request("Walk", self.actor, "Walking", "loop", states)
            if int(self.npcs_xyz_vec[name][0]) < 1 and not states['idle']:
                self.set_basic_npc_behaviors(actor=self.actor, behavior="path_follow")
                # TODO: Change action to something more suitable
                self.request("Idle", self.actor, "LookingAround", "loop", states)

    def enterIdle(self, actor, action, task, states):
        if actor and action and task and states:
            # Since it's Bullet shaped actor, we need access the model which is now child of
            if hasattr(base, 'actor_node') and base.actor_node:
                actor_node = base.actor_node
                # Check if node is same as bullet shape node
                if actor_node.get_name() in self.actor.get_name():
                    any_action = actor_node.actor_interval(action)
                    if isinstance(task, str):
                        if task == "play":
                            if not any_action.isPlaying():
                                actor_node.play(action)
                        elif task == "loop":
                            if not any_action.isPlaying():
                                states['idle'] = True
                                actor_node.stop("Walking")
                                actor_node.loop(action)
                            else:
                                actor_node.stop(action)
                        actor_node.set_play_rate(self.base.actor_play_rate, action)

    def enterWalk(self, actor, action, task, states):
        if actor and action and task and states:
            # Since it's Bullet shaped actor, we need access the model which is now child of
            if hasattr(base, 'actor_node') and base.actor_node:
                actor_node = base.actor_node
                # Check if node is same as bullet shape node
                if actor_node.get_name() in self.actor.get_name():
                    any_action = actor_node.actor_interval(action)
                    if isinstance(task, str):
                        if task == "play":
                            if not any_action.isPlaying():
                                actor_node.play(action)
                        elif task == "loop":
                            if not any_action.isPlaying():
                                states['walk'] = True
                                actor_node.loop(action)
                            else:
                                actor_node.stop(action)
                        actor_node.set_play_rate(self.base.actor_play_rate, action)

    def exitIdle(self):
        actor_node = base.actor_node
        actor_node.stop("LookingAround")

    def exitWalk(self):
        actor_node = base.actor_node
        actor_node.stop("Walking")

    def enterCrouch(self):
        pass

    def exitCrouch(self):
        pass

    def enterSwim(self):
        pass

    def exitSwim(self):
        pass

    def enterStay(self):
        pass

    def exitStay(self):
        pass

    def enterJump(self):
        pass

    def exitJump(self):
        pass

    def enterLay(self):
        pass

    def exitLay(self):
        pass

    def enterAttack(self, actor, action, task, states):
        if actor and action and task and states:
            # Since it's Bullet shaped actor, we need access the model which is now child of
            if hasattr(base, 'actor_node') and base.actor_node:
                actor_node = base.actor_node
                # Check if node is same as bullet shape node
                if actor_node.get_name() in self.actor.get_name():
                    any_action = actor_node.actor_interval(action)
                    if isinstance(task, str):
                        if task == "play":
                            if not any_action.isPlaying():
                                actor_node.play(action)
                        elif task == "loop":
                            if not any_action.isPlaying():
                                states['attack'] = True
                                actor_node.loop(action)
                            else:
                                actor_node.stop(action)
                        actor_node.set_play_rate(self.base.actor_play_rate, action)

    def exitAttack(self):
        actor_node = base.actor_node
        actor_node.stop("Boxing")

    def enterHAttack(self):
        pass

    def exitHAttack(self):
        pass

    def enterFAttack(self):
        pass

    def exitFAttack(self):
        pass

    def enterBlock(self):
        pass

    def exitBlock(self):
        pass

    def enterInteract(self):
        pass

    def exitInteract(self):
        pass

    def enterLife(self):
        pass

    def exitLife(self):
        pass

    def enterDeath(self):
        pass

    def exitDeath(self):
        pass

    def enterMiscAct(self):
        pass

    def exitMiscAct(self):
        pass

