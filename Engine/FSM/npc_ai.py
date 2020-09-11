from direct.fsm.FSM import FSM
from direct.task.TaskManagerGlobal import taskMgr
from panda3d.ai import AIWorld
from panda3d.ai import AICharacter
from Engine.FSM.player_fsm import FsmPlayer


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
        self.fsm_player = FsmPlayer()
        self.ai_behaviors = None

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

    def set_ai_world(self, actor, actor_cls):
        if actor and actor_cls and isinstance(actor_cls, str):
            self.actor = actor
            self.ai_world = AIWorld(render)
            self.player = render.find("**/Korlan:BS")

            if "BS" in self.actor.get_parent().get_name():
                self.actor = self.actor.get_parent()

            speed = 5

            self.ai_char = AICharacter(actor_cls, self.actor, 100, 0.05, speed)
            self.ai_world.add_ai_char(self.ai_char)
            self.ai_behaviors = self.ai_char.get_ai_behaviors()

            base.behaviors['walk'] = True
            base.behaviors['idle'] = False

            taskMgr.add(self.update_ai_world_task,
                        "update_ai_world",
                        appendTask=True)

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

    def target_distance(self, actor):
        if actor and not render.find("**/Korlan:BS").is_empty():
            player = render.find("**/Korlan:BS")
            dist = actor.get_y() - player.get_y()
            return dist

    def update_npc_ai_stat(self, actor, task):
        if actor and "BS" in actor.get_parent().get_name():
            self.actor = actor.get_parent()
            self.set_npc_behavior(actor=self.actor, behavior="seek")
            if self.target_distance(actor=self.actor) <= 1:
                self.set_npc_behavior(actor=self.actor, behavior="flee")
            if self.target_distance(actor=self.actor) > 50:
                self.set_npc_behavior(actor=self.actor, behavior="pursuer")
            if self.target_distance(actor=self.actor) <= 1:
                self.set_npc_behavior(actor=self.actor, behavior="evader")
            if self.target_distance(actor=self.actor) >= 1:
                self.set_npc_behavior(actor=self.actor, behavior="wanderer")
            if self.target_distance(actor=self.actor) <= 1:
                self.set_npc_behavior(actor=self.actor, behavior="obs_avoid")
            if self.target_distance(actor=self.actor) >= 1:
                self.set_npc_behavior(actor=self.actor, behavior="path_follow")
            if self.target_distance(actor=self.actor) > 50:
                self.set_npc_behavior(actor=self.actor, behavior="path_finding")
            # TODO: Fix the walk request
            # self.request("Walk", actor, action="walk", state="loop")
            return task.done
        return task.cont

    # TODO: Run this call in task
    def set_npc_behavior(self, actor, behavior):
        if (actor
                and behavior
                and isinstance(behavior, str)):

            self.player = render.find("**/Korlan:BS")

            if self.ai_world:
                vect = {"panic_dist": 5,
                        "relax_dist": 5,
                        "wander_radius": 5,
                        "plane_flag": 0,
                        "area_of_effect": 10}

                # speed = 5
                # self.ai_char = AICharacter(behavior, actor, 100, 0.05, speed)
                # Prevent duplicating since we in loop
                # self.ai_world.remove_ai_char(actor.get_name())
                # self.ai_world.add_ai_char(self.ai_char)

                navmeshes = self.base.navmesh_collector()
                if behavior == "obs_avoid":
                    self.ai_behaviors.obstacle_avoidance(1.0)
                    self.ai_world.add_obstacle(actor)
                    self.ai_behaviors.initPathFind(navmeshes["lvl_one"])

                elif behavior == "seek":
                    self.ai_behaviors.seek(self.player)
                    self.ai_behaviors.initPathFind(navmeshes["lvl_one"])
                    self.ai_behaviors.path_find_to(self.player, "addPath")
                elif behavior == "flee":
                    self.ai_behaviors.flee(actor,
                                           vect['panic_dist'],
                                           vect['relax_dist'])
                    self.ai_behaviors.initPathFind(navmeshes["lvl_one"])
                    self.ai_behaviors.path_find_to(self.player, "addPath")
                elif behavior == "pursuer":
                    self.ai_behaviors.pursue(self.player)
                    self.ai_behaviors.initPathFind(navmeshes["lvl_one"])
                elif behavior == "evader":
                    self.ai_behaviors.evade(self.player,
                                            vect['panic_dist'],
                                            vect['relax_dist'])
                    self.ai_behaviors.initPathFind(navmeshes["lvl_one"])
                elif behavior == "wanderer":
                    self.ai_behaviors.wander(vect["wander_radius"],
                                             vect["plane_flag"],
                                             vect["area_of_effect"])
                    self.ai_behaviors.initPathFind(navmeshes["lvl_one"])
                elif behavior == "path_finding":
                    self.ai_behaviors.initPathFind(navmeshes["lvl_one"])
                elif behavior == "path_follow":
                    self.ai_behaviors.initPathFind(navmeshes["lvl_one"])
                    self.ai_behaviors.path_follow(1)
                    self.ai_behaviors.add_to_path(self.player.get_pos())
                    self.ai_behaviors.start_follow()
                base.behaviors['walk'] = True
                base.behaviors['idle'] = False

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
            any_action = actor.getAnimControl(action)
            if (isinstance(state, str)
                    and any_action.isPlaying() is False
                    and base.behaviors['idle'] is False
                    and base.behaviors['walk']):
                if state == "play":
                    actor.play(action)
                elif state == "loop":
                    actor.loop(action)
                actor.set_play_rate(self.base.actor_play_rate, action)

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
