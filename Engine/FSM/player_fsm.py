from direct.fsm.FSM import FSM
from direct.interval.FunctionInterval import Func
from direct.interval.MetaInterval import Sequence


class PlayerFSM(FSM):
    def __init__(self):
        FSM.__init__(self, 'PlayerFSM')
        self.base = base
        self.render = render
        self.player = None

    def fsm_state_wrapper(self, state, boolean):
        if (state and isinstance(state, str)
                and isinstance(boolean, bool)):
            base.player_states[state] = boolean

    def get_player(self, actor):
        if actor and isinstance(actor, str):
            if not render.find("**/{0}:BS").is_empty():
                self.player = render.find("**/{0}:BS")
                return self.player

    def enterIdle(self, player, action, state):
        if player and action:
            self.player = player
            if isinstance(state, str):
                if state == "play":
                    self.player.play(action)
                elif state == "loop":
                    self.player.loop(action)
                self.player.setPlayRate(self.base.actor_play_rate, action)

    def enterForwardRoll(self, actor, action, action_next, task):
        if actor and action and action_next and task:
            any_action = actor.get_anim_control(action)
            any_action_seq = actor.actor_interval(action)
            action_next_seq = actor.actor_interval(action_next)

            if isinstance(task, str):
                if task == "play":
                    if not any_action.isPlaying():
                        Sequence(any_action_seq, action_next_seq).start()

                elif task == "loop":
                    if not any_action.isPlaying():
                        actor.loop(action)
                actor.set_play_rate(self.base.actor_play_rate, action)

    def enterAttacked(self, actor, action, action_next, task):
        if actor and action and action_next and task:
            any_action = actor.get_anim_control(action)
            any_action_seq = actor.actor_interval(action)
            action_next_seq = actor.actor_interval(action)

            if isinstance(task, str):
                if task == "play":
                    if not any_action.isPlaying():
                        Sequence(Func(self.fsm_state_wrapper, "is_attacked", True),
                                 any_action_seq,
                                 Func(self.fsm_state_wrapper, "is_attacked", False),
                                 action_next_seq).start()

                elif task == "loop":
                    if not any_action.isPlaying():
                        actor.loop(action)
                actor.set_play_rate(self.base.actor_play_rate, action)

    def enterSwim(self, actor, action, task):
        if actor and action and task:
            any_action = actor.get_anim_control(action)
            any_action_seq = actor.actor_interval(action)

            if isinstance(task, str):
                if task == "play":
                    if not any_action.isPlaying():
                        Sequence(any_action_seq, Func(self.fsm_state_wrapper, "is_busy", False)).start()

                elif task == "loop":
                    if not any_action.isPlaying():
                        actor.loop(action)
                actor.set_play_rate(self.base.actor_play_rate, action)

    def enterLay(self, actor, action, task):
        if actor and action and task:
            any_action = actor.get_anim_control(action)
            any_action_seq = actor.actor_interval(action)

            if isinstance(task, str):
                if task == "play":
                    if not any_action.isPlaying():
                        Sequence(any_action_seq, Func(self.fsm_state_wrapper, "is_busy", False)).start()

                elif task == "loop":
                    if not any_action.isPlaying():
                        actor.loop(action)
                actor.set_play_rate(self.base.actor_play_rate, action)

    def enterLife(self, actor, action, task):
        if actor and action and task:
            any_action = actor.get_anim_control(action)
            any_action_seq = actor.actor_interval(action)

            if isinstance(task, str):
                if task == "play":
                    if not any_action.isPlaying():
                        Sequence(any_action_seq, Func(self.fsm_state_wrapper, "is_busy", False)).start()

                elif task == "loop":
                    if not any_action.isPlaying():
                        actor.loop(action)
                actor.set_play_rate(self.base.actor_play_rate, action)

    def enterDeath(self, actor, action, task):
        if actor and action and task:
            any_action = actor.get_anim_control(action)
            any_action_seq = actor.actor_interval(action)

            if isinstance(task, str):
                if task == "play":
                    if not any_action.isPlaying():
                        Sequence(any_action_seq, Func(self.fsm_state_wrapper, "is_busy", False)).start()

                elif task == "loop":
                    if not any_action.isPlaying():
                        actor.loop(action)
                actor.set_play_rate(self.base.actor_play_rate, action)

    def filterForwardRoll(self, request, args):
        if request not in ['Attacked']:
            return (request,) + args
        else:
            return None

    def filterAttacked(self, request, args):
        if (hasattr(self.base, 'player_ref')
                and self.base.player_ref):
            any_action = self.base.player_ref.get_anim_control('BigHitToHead')
            if (any_action.isPlaying() is False
                    and request in ['Attacked']):
                base.player_states['is_attacked'] = True
                return (request,) + args
            elif (any_action.isPlaying()
                    and request in ['Attacked']):
                base.player_states['is_attacked'] = False
                return None

    def filterSwim(self, request, args):
        if (hasattr(self.base, 'player_ref')
                and self.base.player_ref):
            any_action = self.base.player_ref.get_anim_control('Swim')
            if (any_action.isPlaying() is False
                    and request in ['Swim']):
                base.player_states['is_busy'] = True
                return (request,) + args
            elif (any_action.isPlaying()
                    and request in ['Swim']):
                base.player_states['is_busy'] = False
                return None

    def filterLay(self, request, args):
        if (hasattr(self.base, 'player_ref')
                and self.base.player_ref):
            any_action = self.base.player_ref.get_anim_control('Lay')
            if (any_action.isPlaying() is False
                    and request in ['Lay']):
                base.player_states['is_attacked'] = True
                return (request,) + args
            elif (any_action.isPlaying()
                    and request in ['Lay']):
                base.player_states['is_attacked'] = False
                return None

    def filterLife(self, request, args):
        if (hasattr(self.base, 'player_ref')
                and self.base.player_ref):
            any_action = self.base.player_ref.get_anim_control('Life')
            if (any_action.isPlaying() is False
                    and request in ['Life']):
                base.player_states['is_attacked'] = True
                return (request,) + args
            elif (any_action.isPlaying()
                    and request in ['Life']):
                base.player_states['is_attacked'] = False
                return None

    def filterDeath(self, request, args):
        if (hasattr(self.base, 'player_ref')
                and self.base.player_ref):
            any_action = self.base.player_ref.get_anim_control('Death')
            if (any_action.isPlaying() is False
                    and request in ['Death']):
                base.player_states['is_attacked'] = True
                return (request,) + args
            elif (any_action.isPlaying()
                    and request in ['Death']):
                base.player_states['is_attacked'] = False
                return None
