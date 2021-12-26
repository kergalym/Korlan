from direct.fsm.FSM import FSM
from direct.interval.FunctionInterval import Func
from direct.interval.MetaInterval import Sequence
from direct.task.TaskManagerGlobal import taskMgr
from panda3d.core import Point3

from Engine.FSM.npc_fsm import NpcFSM


class NpcHorseFSM(FSM):
    def __init__(self):
        FSM.__init__(self, "NpcHorseFSM")
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

    def enterWalk(self, actor, player, ai_behaviors, behavior, action, vect, task):
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
            # actor = render.find("**/{0}".format(actor.get_name()))
            if hasattr(self.base, "ai_chars_bs") and self.base.ai_chars_bs:
                name = actor.get_name()
                actor = self.base.ai_chars_bs[name]
                self.npc_fsm.set_basic_npc_behaviors(actor=actor,
                                                     player=player,
                                                     ai_behaviors=ai_behaviors,
                                                     behavior=behavior,
                                                     vect=vect)

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

    def enterAttacked(self, actor, action, action_next, task):
        if actor and action and action_next and task:
            any_action = actor.get_anim_control(action)

            if isinstance(task, str):
                if task == "play":
                    if not any_action.isPlaying():
                        Sequence(actor.actor_interval(action, loop=0),
                                 actor.actor_interval(action_next, loop=1)).start()

                elif task == "loop":
                    if not any_action.isPlaying():
                        actor.loop(action)
                actor.set_play_rate(self.base.actor_play_rate, action)

    def enterHAttack(self):
        pass

    def enterFAttack(self):
        pass

    def enterBlock(self, actor, action, action_next, task):
        if actor and action and action_next and task:
            any_action = actor.get_anim_control(action)

            if isinstance(task, str):
                if task == "play":
                    if not any_action.isPlaying():
                        Sequence(actor.actor_interval(action, loop=0),
                                 actor.actor_interval(action_next, loop=1)).start()

                elif task == "loop":
                    if not any_action.isPlaying():
                        actor.loop(action)
                actor.set_play_rate(self.base.actor_play_rate, action)

    def enterInteract(self):
        pass

    def enterLife(self):
        pass

    def enterDeath(self, actor, action, task):
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

    def filterBlock(self, request, args):
        if request not in ['Block']:
            return (request,) + args
        else:
            return None

    def filterDeath(self, request, args):
        if request not in ['Death']:
            return (request,) + args
        else:
            return None
