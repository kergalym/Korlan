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

    def update_ai_behavior_task(self, player, actor, behavior, behaviors, vect, task):
        if (player and actor
                and behavior
                and isinstance(behavior, str)
                and behaviors and
                isinstance(vect, dict)):
            if behavior == "seek":
                behaviors.seek(player)
            elif behavior == "flee":
                behaviors.flee(player,
                               vect['panic_dist'],
                               vect['relax_dist'])
            elif behavior == "pursuer":
                behaviors.pursue(player)
            elif behavior == "evader":
                behaviors.evade(player,
                                vect['panic_dist'],
                                vect['relax_dist'])
            elif behavior == "wanderer":
                behaviors.wander(vect["wander_radius"],
                                 vect["plane_flag"],
                                 vect["area_of_effect"])
            elif behavior == "path_follow":
                behaviors.path_follow(1)
                behaviors.add_to_path(player.get_pos())
                behaviors.start_follow()
            base.behaviors['walk'] = True
            base.behaviors['idle'] = False

            actor.set_p(0)
            actor.set_z(0)

            if base.game_mode is False and base.menu_mode:
                return task.done
        return task.cont

    def get_npc(self, actor):
        if actor and isinstance(actor, str):
            if not render.find("**/{}".format(actor)).is_empty():
                avatar = render.find("**/{}".format(actor))
                return avatar

    def set_npc_ai(self, actor, behavior):
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
                    speed = 4
                    player = None

                    ai_char = AICharacter(behavior, actor, 100, 0.05, speed)
                    base.ai_world.remove_ai_char(actor.get_name())
                    base.ai_world.add_ai_char(ai_char)
                    ai_behaviors = ai_char.get_ai_behaviors()

                    if behavior == "obs_avoid":
                        ai_behaviors.obstacle_avoidance(1.0)
                        base.ai_world.add_obstacle(player)

                    if not render.find("**/Korlan:BS").is_empty():
                        player = render.find("**/Korlan:BS")

                    taskMgr.add(self.update_ai_behavior_task,
                                "update_ai_behavior",
                                extraArgs=[player, actor, behavior,
                                           ai_behaviors, vect],
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
