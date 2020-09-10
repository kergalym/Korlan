from direct.fsm.FSM import FSM
from direct.task.TaskManagerGlobal import taskMgr
from panda3d.ai import AICharacter


class NpcAI(FSM):
    def __init__(self):
        FSM.__init__(self, "NpcAI")
        self.base = base
        self.render = render
        self.taskMgr = taskMgr
        self.ai_char = None
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
            actor = actor.get_parent()
            self.set_npc_behavior(actor=actor, behavior="seek")
            if self.target_distance(actor=actor) <= 1:
                self.set_npc_behavior(actor=actor, behavior="flee")
            if self.target_distance(actor=actor) > 50:
                self.set_npc_behavior(actor=actor, behavior="pursuer")
            if self.target_distance(actor=actor) <= 1:
                self.set_npc_behavior(actor=actor, behavior="evader")
            if self.target_distance(actor=actor) >= 1:
                self.set_npc_behavior(actor=actor, behavior="wanderer")
            if self.target_distance(actor=actor) <= 1:
                self.set_npc_behavior(actor=actor, behavior="obs_avoid")
            if self.target_distance(actor=actor) >= 1:
                self.set_npc_behavior(actor=actor, behavior="path_follow")
            if self.target_distance(actor=actor) > 50:
                self.set_npc_behavior(actor=actor, behavior="path_finding")
            # TODO: Fix the walk request
            # self.request("Walk", actor, action="walk", state="loop")
            return task.done
        return task.cont

    def set_npc_behavior(self, actor, behavior):
        if (actor
                and behavior
                and isinstance(behavior, str)):
            if hasattr(base, "ai_world"):
                if base.ai_world:
                    vect = {"panic_dist": 5,
                            "relax_dist": 5,
                            "wander_radius": 5,
                            "plane_flag": 0,
                            "area_of_effect": 10}
                    speed = 5

                    ai_char = AICharacter(behavior, actor, 100, 0.05, speed)
                    base.ai_world.remove_ai_char(actor.get_name())
                    base.ai_world.add_ai_char(ai_char)
                    behaviors = ai_char.get_ai_behaviors()
                    navmeshes = self.base.navmesh_collector()

                    if actor and not render.find("**/Korlan:BS").is_empty():
                        player = render.find("**/Korlan:BS")

                        if behavior == "obs_avoid":
                            behaviors.obstacle_avoidance(1.0)
                            base.ai_world.add_obstacle(actor)
                            behaviors.initPathFind(navmeshes["lvl_one"])

                        elif behavior == "seek":
                            behaviors.seek(player)
                            behaviors.initPathFind(navmeshes["lvl_one"])
                            behaviors.path_find_to(player, "addPath")
                        elif behavior == "flee":
                            behaviors.flee(actor,
                                           vect['panic_dist'],
                                           vect['relax_dist'])
                            behaviors.initPathFind(navmeshes["lvl_one"])
                            behaviors.path_find_to(player, "addPath")
                        elif behavior == "pursuer":
                            behaviors.pursue(player)
                            behaviors.initPathFind(navmeshes["lvl_one"])
                        elif behavior == "evader":
                            behaviors.evade(player,
                                            vect['panic_dist'],
                                            vect['relax_dist'])
                            behaviors.initPathFind(navmeshes["lvl_one"])
                        elif behavior == "wanderer":
                            behaviors.wander(vect["wander_radius"],
                                             vect["plane_flag"],
                                             vect["area_of_effect"])
                            behaviors.initPathFind(navmeshes["lvl_one"])
                        elif behavior == "path_finding":
                            behaviors.initPathFind(navmeshes["lvl_one"])
                        elif behavior == "path_follow":
                            behaviors.initPathFind(navmeshes["lvl_one"])
                            behaviors.path_follow(1)
                            behaviors.add_to_path(player.get_pos())
                            behaviors.start_follow()
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
