from direct.fsm.FSM import FSM
from direct.interval.MetaInterval import Sequence
from direct.task.TaskManagerGlobal import taskMgr
from panda3d.core import Point3

from Engine.FSM.npc_fsm import NpcFSM


class NpcErnarFSM(FSM):
    def __init__(self):
        FSM.__init__(self, "NpcErnarFSM")
        self.base = base
        self.render = render
        self.taskMgr = taskMgr
        self.npc_fsm = NpcFSM()
        base.fsm = self

    def enterIdle(self, actor, action, task):
        if actor and action and task:
            any_action = actor.get_anim_control(action)

            if isinstance(task, str):
                if task == "play":
                    if not any_action.isPlaying():
                        actor.play(action)
                elif task == "loop":
                    if not any_action.isPlaying():
                        actor.loop(action)
                actor.set_play_rate(self.base.actor_play_rate, action)

    def enterWalk(self, actor, player, ai_behaviors, behavior, action, task):
        if actor and player and ai_behaviors and behavior and action and task:
            any_action = actor.get_anim_control(action)

            if isinstance(task, str):
                if task == "play":
                    if not any_action.isPlaying():
                        actor.play(action)
                elif task == "loop":
                    if not any_action.isPlaying():
                        actor.loop(action)
                actor.set_play_rate(self.base.actor_play_rate, action)

            # Get correct NodePath
            actor = render.find("**/{0}".format(actor.get_name()))
            self.npc_fsm.set_basic_npc_behaviors(actor=actor.get_parent(),
                                                 player=player,
                                                 ai_behaviors=ai_behaviors,
                                                 behavior=behavior)

    def enterWalkAny(self, actor, action, pos_y, task):
        if actor and action and task:
            actor_bs = self.base.get_actor_bullet_shape_node(asset=actor.get_name(), type="NPC")

            any_action = actor.get_anim_control(action)
            any_action_seq = actor.actor_interval(action)
            if isinstance(task, str):
                if task == "play":
                    if not any_action.isPlaying():
                        Sequence(any_action_seq).start()

                elif task == "loop":
                    if not any_action.isPlaying():
                        actor.loop(action)
                actor.set_play_rate(self.base.actor_play_rate, action)

            # Create the four lerp intervals needed for actor_bs to
            # walk in any pos
            if (actor_bs and isinstance(pos_y, int)
                    or isinstance(pos_y, float)):
                posIval1 = actor_bs.posInterval(13,
                                                Point3(0, -pos_y, 0),
                                                startPos=Point3(0, 10, 0))
                posIval2 = actor_bs.posInterval(13,
                                                Point3(0, pos_y, 0),
                                                startPos=Point3(0, -pos_y, 0))
                hprIval1 = actor_bs.hprInterval(3,
                                                Point3(180, 0, 0),
                                                startHpr=Point3(0, 0, 0))
                hprIval2 = actor_bs.hprInterval(3,
                                                Point3(0, 0, 0),
                                                startHpr=Point3(180, 0, 0))

                # Create and play the sequence that coordinates the intervals.
                walk_any = Sequence(posIval1, hprIval1,
                                    posIval2, hprIval2,
                                    name="WalkAny")
                walk_any.loop()

    def enterAttack(self, actor, action, task):
        if actor and action and task:
            any_action = actor.get_anim_control(action)
            any_action_seq = actor.actor_interval(action)

            if isinstance(task, str):
                if task == "play":
                    if not any_action.isPlaying():
                        Sequence(any_action_seq).start()

                elif task == "loop":
                    if not any_action.isPlaying():
                        actor.loop(action)
                actor.set_play_rate(self.base.actor_play_rate, action)

    def enterAttacked(self, actor, action, task):
        if actor and action and task:
            any_action = actor.get_anim_control(action)
            any_action_seq = actor.actor_interval(action)

            if isinstance(task, str):
                if task == "play":
                    if not any_action.isPlaying():
                        Sequence(any_action_seq).start()

                elif task == "loop":
                    if not any_action.isPlaying():
                        actor.loop(action)
                actor.set_play_rate(self.base.actor_play_rate, action)

    def enterHAttack(self):
        pass

    def enterFAttack(self):
        pass

    def enterBlock(self):
        pass

    def enterInteract(self):
        pass

    def enterLife(self):
        pass

    def enterDeath(self):
        pass

    def enterMiscAct(self):
        pass

    def enterCrouch(self):
        pass

    def enterSwim(self):
        pass

    def enterStay(self):
        pass

    def enterJump(self):
        pass

    def enterLay(self):
        pass

    def filterIdle(self, request, args):
        if request not in ['Idle']:
            return (request,) + args
        else:
            return None

    def filterWalk(self, request, args):
        if request not in ['Walk']:
            return (request,) + args
        else:
            return None

    def filterWalkAny(self, request, args):
        if request not in ['Walk']:
            return (request,) + args
        else:
            return None

    def filterAttack(self, request, args):
        if request not in ['Attack']:
            return (request,) + args
        else:
            return None

    def filterAttacked(self, request, args):
        if request not in ['Attacked']:
            return (request,) + args
        else:
            return None
