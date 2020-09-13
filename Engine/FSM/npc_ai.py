from direct.fsm.FSM import FSM
from direct.task.TaskManagerGlobal import taskMgr
from panda3d.ai import AIWorld
from panda3d.ai import AICharacter
from Engine.FSM.player_fsm import FsmPlayer
from Engine.Actors.NPC.Classes.npc_husband import Husband


class NpcAI(FSM):
    def __init__(self):
        FSM.__init__(self, "NpcAI")
        self.base = base
        self.render = render
        self.taskMgr = taskMgr
        self.ai_char = None
        self.actor = None
        self.player = None
        self.ai_world = None
        self.ai_behaviors = None
        self.fsm_player = FsmPlayer()
        self.husband = Husband()

        base.behaviors = {
            "idle": True,
            "walk": False,
            "swim": False,
            "stay": False,
            "jump": False,
            "crouch": False,
            "lay": False,
            "attack": False,
            "interact": False,
            "life": False,
            "death": False,
            "misc_act": False
        }

    def get_actor_instance(self, actor):
        if actor:
            return actor

    def set_ai_world(self, assets, task):
        if assets and isinstance(assets, dict):
            self.ai_world = AIWorld(render)
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
                                    self.ai_char = AICharacter(actor_cls, self.actor, 100, 0.05, speed)
                                    self.ai_world.add_ai_char(self.ai_char)
                                    self.ai_behaviors = self.ai_char.get_ai_behaviors()

                                    base.behaviors['walk'] = True
                                    base.behaviors['idle'] = False

                                    taskMgr.add(self.update_ai_world_task,
                                                "update_ai_world",
                                                appendTask=True)

                                    taskMgr.add(self.update_npc_actions,
                                                "update_npc_actions",
                                                appendTask=True)

                                    return task.done
        return task.cont

    def update_ai_world_task(self, task):
        if self.ai_world:
            self.ai_world.update()
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

    def update_npc_actions(self, task):
        if self.actor and self.player:
            xyz_vec = self.base.npc_distance_calculate(player=self.player, actor=self.actor)['vector']
            npc_class = self.set_npc_class(actor=self.actor)
            if xyz_vec and npc_class:
                if npc_class.get('class') == "friend":
                    self.set_npc_behavior(actor=self.actor, behavior="pursuer")
                    self.request("Walk", self.actor, "Walking", "loop")
                else:
                    print("seek")
                    self.set_npc_behavior(actor=self.actor, behavior="seek")
                    if int(xyz_vec[0]) < 1:
                        self.set_npc_behavior(actor=self.actor, behavior="flee")
                        print("flee")
                    if int(xyz_vec[0]) > 50:
                        self.set_npc_behavior(actor=self.actor, behavior="pursuer")
                        print("pursuer")
                    if int(xyz_vec[0]) < 1:
                        self.set_npc_behavior(actor=self.actor, behavior="evader")
                        print("evader")
                    if int(xyz_vec[0]) > 1:
                        self.set_npc_behavior(actor=self.actor, behavior="wanderer")
                        print("wanderer")
                    if int(xyz_vec[0]) < 1:
                        self.set_npc_behavior(actor=self.actor, behavior="obs_avoid")
                        print("obs_avoid")
                    if int(xyz_vec[0]) > 1:
                        self.set_npc_behavior(actor=self.actor, behavior="path_follow")
                        print("path_follow")
                    if int(xyz_vec[0]) > 50:
                        self.set_npc_behavior(actor=self.actor, behavior="path_finding")
                        print("path_finding")
                    self.request("Walk", self.actor, "Walking", "loop")

                return task.done

        if base.game_mode is False and base.menu_mode:
            return task.done

        return task.cont

    def set_npc_class(self, actor):
        if actor and not actor.is_empty():
            if self.husband.name in self.actor.get_name():
                return {'class': 'friend'}

            # elif self.mongol_warrior.name in self.actor.get_name():
                # return {'class': 'enemy'}

    def set_npc_behavior(self, actor, behavior):
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

    def enterIdle(self, actor, action, state):
        if actor and action and state:
            any_action = actor.getAnimControl(action)
            if (isinstance(state, str)
                    and any_action.isPlaying() is False
                    and base.behaviors['idle']
                    and base.behaviors['walk'] is False):
                if state == "play":
                    actor.play(action)
                elif state == "loop":
                    actor.loop(action)
                actor.set_play_rate(self.base.actor_play_rate, action)

    def exitIdle(self):
        base.behaviors['idle'] = False
        base.behaviors['walk'] = False

    def enterWalk(self, actor, action, state):
        if actor and action and state:
            base.behaviors['idle'] = False
            base.behaviors['walk'] = True
            # Since it's Bullet shaped actor, we need access the model which is now child of
            if hasattr(base, 'actor_node') and base.actor_node:
                actor_node = base.actor_node
                # Check if node is same as bullet shape node
                if actor_node.get_name() in self.actor.get_name():
                    any_action = actor_node.actor_interval(action)
                    if (isinstance(state, str)
                            and any_action.isPlaying() is False
                            and base.behaviors['idle'] is False
                            and base.behaviors['walk']):
                        if state == "play":
                            actor_node.play(action)
                        elif state == "loop":
                            actor_node.loop(action)
                            self.enter_walk = 1
                        actor_node.set_play_rate(self.base.actor_play_rate, action)

    def exitWalk(self):
        base.behaviors['idle'] = True
        base.behaviors['walk'] = False

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

    def EnterAttack(self):
        pass

    def exitAttack(self):
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
