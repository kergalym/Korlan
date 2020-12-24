from direct.fsm.FSM import FSM


class NpcErnarFSM(FSM):
    def __init__(self):
        FSM.__init__(self, "NpcErnarFSM")
        self.base = base
        self.render = render

    def enterIdle(self, actor, action, task):
        if actor and action and task:
            any_action = actor.get_anim_control(action)
            self.base.debug_any_action = any_action

            if isinstance(task, str):
                if task == "play":
                    if not any_action.isPlaying():
                        actor.play(action)
                elif task == "loop":
                    if not any_action.isPlaying():
                        actor.loop(action)
                actor.set_play_rate(self.base.actor_play_rate, action)

    def enterWalk(self, actor, action, task):
        if actor and action and task:
            any_action = actor.get_anim_control(action)
            self.base.debug_any_action = any_action

            if isinstance(task, str):
                if task == "play":
                    if not any_action.isPlaying():
                        actor.play(action)
                elif task == "loop":
                    if not any_action.isPlaying():
                        actor.loop(action)
                actor.set_play_rate(self.base.actor_play_rate, action)

    def enterAttack(self, actor, action, task):
        if actor and action and task:
            any_action = actor.get_anim_control(action)
            self.base.debug_any_action = any_action

            if isinstance(task, str):
                if task == "play":
                    if not any_action.isPlaying():
                        actor.play(action)
                elif task == "loop":
                    if not any_action.isPlaying():
                        actor.loop(action)
                actor.set_play_rate(self.base.actor_play_rate, action)

    def enterAttacked(self, actor, action, task):
        if actor and action and task:
            any_action = actor.get_anim_control(action)
            self.base.debug_any_action = any_action

            if isinstance(task, str):
                if task == "play":
                    if not any_action.isPlaying():
                        actor.play(action)
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

    def enterBow(self, actor, action, task):
        if actor and action and task:
            any_action = actor.get_anim_control(action)
            self.base.debug_any_action = any_action

            if isinstance(task, str):
                if task == "play":
                    if not any_action.isPlaying():
                        actor.play(action)
                elif task == "loop":
                    if not any_action.isPlaying():
                        actor.loop(action)
                actor.set_play_rate(self.base.actor_play_rate, action)

    def enterSword(self, actor, action, task):
        if actor and action and task:
            any_action = actor.get_anim_control(action)
            self.base.debug_any_action = any_action

            if isinstance(task, str):
                if task == "play":
                    if not any_action.isPlaying():
                        actor.play(action)
                elif task == "loop":
                    if not any_action.isPlaying():
                        actor.loop(action)
                actor.set_play_rate(self.base.actor_play_rate, action)

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
        if request not in ['WalkAny']:
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
