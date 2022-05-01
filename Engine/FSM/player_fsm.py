from direct.fsm.FSM import FSM
from direct.interval.FunctionInterval import Func
from direct.interval.MetaInterval import Sequence


class PlayerFSM(FSM):
    def __init__(self):
        FSM.__init__(self, 'PlayerFSM')
        self.base = base
        self.render = render

    def fsm_state_wrapper(self, state, boolean):
        if (state and isinstance(state, str)
                and isinstance(boolean, bool)):
            base.player_states[state] = boolean

    def enterIdle(self, actor, action, state):
        if actor and action:
            any_action = actor.get_anim_control(action)

            if isinstance(state, str):
                if state == "play":
                    if not any_action.is_playing():
                        actor.play(action)
                elif state == "loop":
                    if not any_action.is_playing():
                        actor.loop(action)

    def enterForwardRoll(self, actor, action, action_next, task):
        if actor and action and action_next and task:
            any_action = actor.get_anim_control(action)
            any_action_seq = actor.actor_interval(action)
            action_next_seq = actor.actor_interval(action_next)

            if isinstance(task, str):
                if task == "play":
                    if not any_action.is_playing():
                        Sequence(any_action_seq, action_next_seq).start()

                elif task == "loop":
                    if not any_action.is_playing():
                        actor.loop(action)

    def enterAttacked(self, actor, action, task):
        if actor and action and task:
            any_action = actor.get_anim_control(action)
            any_action_seq = actor.actor_interval(action)

            if isinstance(task, str):
                if task == "play":
                    if not any_action.is_playing():
                        Sequence(Func(self.fsm_state_wrapper, "is_attacked", True),
                                 any_action_seq,
                                 Func(self.fsm_state_wrapper, "is_attacked", False)).start()

    def enterSwim(self, actor, action, task):
        if actor and action and task:
            any_action = actor.get_anim_control(action)
            any_action_seq = actor.actor_interval(action)

            if isinstance(task, str):
                if task == "play":
                    if not any_action.is_playing():
                        Sequence(any_action_seq, Func(self.fsm_state_wrapper, "is_busy", False)).start()

                elif task == "loop":
                    if not any_action.is_playing():
                        actor.loop(action)

    def enterLay(self, actor, action, task):
        if actor and action and task:
            any_action = actor.get_anim_control(action)
            any_action_seq = actor.actor_interval(action)

            if isinstance(task, str):
                if task == "play":
                    if not any_action.is_playing():
                        Sequence(any_action_seq, Func(self.fsm_state_wrapper, "is_busy", False)).start()

                elif task == "loop":
                    if not any_action.is_playing():
                        actor.loop(action)

    def enterLife(self, actor, action, task):
        if actor and action and task:
            any_action = actor.get_anim_control(action)
            any_action_seq = actor.actor_interval(action)

            if isinstance(task, str):
                if task == "play":
                    if not any_action.is_playing():
                        Sequence(any_action_seq, Func(self.fsm_state_wrapper, "is_busy", False)).start()

                elif task == "loop":
                    if not any_action.is_playing():
                        actor.loop(action)

    def enterDeath(self, actor, action, task):
        if actor and action and task:
            any_action = actor.get_anim_control(action)
            any_action_seq = actor.actor_interval(action)

            actor_bs = self.base.get_actor_bullet_shape_node(asset="Player", type="Player")
            actor_bs.node().set_collision_response(False)

            if isinstance(task, str):
                if task == "play":
                    if not any_action.is_playing():
                        Sequence(any_action_seq,
                                 Func(self.fsm_state_wrapper, "is_busy", False)).start()

                elif task == "loop":
                    if not any_action.is_playing():
                        actor.loop(action)

    def filterForwardRoll(self, request, args):
        if request not in ['Attacked']:
            return (request,) + args
        else:
            return None

    """def filterAttacked(self, request, args):
        if request not in ['Attacked']:
            any_action = args[0].get_anim_control(args[1])
            if not any_action.is_playing():
                return (request,) + args"""

    def filterSwim(self, request, args):
        if (hasattr(self.base, 'player_ref')
                and self.base.player_ref):
            any_action = self.base.player_ref.get_anim_control('Swim')
            if (any_action.is_playing() is False
                    and request in ['Swim']):
                base.player_states['is_busy'] = True
                return (request,) + args
            elif (any_action.is_playing()
                  and request in ['Swim']):
                base.player_states['is_busy'] = False
                return None

    def filterLay(self, request, args):
        if (hasattr(self.base, 'player_ref')
                and self.base.player_ref):
            any_action = self.base.player_ref.get_anim_control('Lay')
            if (any_action.is_playing() is False
                    and request in ['Lay']):
                base.player_states['is_attacked'] = True
                return (request,) + args
            elif (any_action.is_playing()
                  and request in ['Lay']):
                base.player_states['is_attacked'] = False
                return None

    def filterLife(self, request, args):
        if (hasattr(self.base, 'player_ref')
                and self.base.player_ref):
            any_action = self.base.player_ref.get_anim_control('Life')
            if (any_action.is_playing() is False
                    and request in ['Life']):
                base.player_states['is_attacked'] = True
                return (request,) + args
            elif (any_action.is_playing()
                  and request in ['Life']):
                base.player_states['is_attacked'] = False
                return None

    def filterDeath(self, request, args):
        if request not in ['Death']:
            any_action = args[0].get_anim_control(args[1])
            if not any_action.is_playing():
                return (request,) + args
