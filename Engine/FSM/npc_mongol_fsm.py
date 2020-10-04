from direct.fsm.FSM import FSM
from direct.interval.FunctionInterval import Func
from direct.interval.MetaInterval import Sequence
from direct.task.TaskManagerGlobal import taskMgr
from Engine.FSM.npc_fsm import NpcFSM


class NpcMongolFSM(FSM):
    def __init__(self):
        FSM.__init__(self, "NpcErnarFSM")
        self.base = base
        self.render = render
        self.taskMgr = taskMgr
        self.npc_fsm = NpcFSM()
        base.fsm = self

    def fsm_state_wrapper(self, state, boolean):
        if (state and isinstance(state, str)
                and isinstance(boolean, bool)):
            base.states[state] = boolean

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

            self.npc_fsm.set_basic_npc_behaviors(actor=actor,
                                                 player=player,
                                                 ai_behaviors=ai_behaviors,
                                                 behavior=behavior)

    def enterAttack(self, actor, action, task):
        if actor and action and task:
            any_action = actor.get_anim_control(action)
            any_action_seq = actor.actor_interval(action)

            if isinstance(task, str):
                if task == "play":
                    if not any_action.isPlaying():
                        Sequence(any_action_seq, Func(self.fsm_state_wrapper, "is_attacked", False)).start()

                elif task == "loop":
                    if not any_action.isPlaying():
                        actor.loop(action)
                actor.set_play_rate(self.base.actor_play_rate, action)


    def exitSwim(self):
        pass

    def exitStay(self):
        pass

    def exitCrouch(self):
        pass

    def exitJump(self):
        pass

    def exitLay(self):
        pass

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

    def exitHAttack(self):
        pass

    def exitFAttack(self):
        pass

    def exitBlock(self):
        pass

    def exitInteract(self):
        pass

    def exitLife(self):
        pass

    def exitDeath(self):
        pass

    def exitMiscAct(self):
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
