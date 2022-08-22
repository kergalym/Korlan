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

    def enterForwardRoll(self, actor, action, task):
        if actor and action and task:
            if isinstance(task, str):
                if task == "play":
                    any_action = actor.get_anim_control(action)
                    any_action_seq = actor.actor_interval(action)
                    if not any_action.is_playing():
                        Sequence(Func(self.fsm_state_wrapper, "is_busy", True),
                                 any_action_seq,
                                 Func(self.fsm_state_wrapper, "is_busy", False)).start()

    def enterAttacked(self, actor, action, task):
        if actor and action and task:
            if isinstance(task, str):
                if task == "play":
                    any_action = actor.get_anim_control(action)
                    any_action_seq = actor.actor_interval(action)
                    if not any_action.is_playing():
                        Sequence(Func(self.fsm_state_wrapper, "is_attacked", True),
                                 any_action_seq,
                                 Func(self.fsm_state_wrapper, "is_attacked", False)).start()

    def enterLay(self, actor, action, task):
        if actor and action and task:
            if isinstance(task, str):
                if task == "play":
                    any_action = actor.get_anim_control(action)
                    any_action_seq = actor.actor_interval(action)
                    if not any_action.is_playing():
                        Sequence(Func(self.fsm_state_wrapper, "is_busy", True),
                                 any_action_seq,
                                 Func(self.fsm_state_wrapper, "is_busy", False)).start()

    def enterLife(self, actor, action, task):
        if actor and action and task:
            if isinstance(task, str):
                if task == "play":
                    any_action = actor.get_anim_control(action)
                    any_action_seq = actor.actor_interval(action)
                    if not any_action.is_playing():
                        Sequence(Func(self.fsm_state_wrapper, "is_busy", True),
                                 any_action_seq,
                                 Func(self.fsm_state_wrapper, "is_busy", False)).start()

    def enterDeath(self, actor, action, task):
        if actor and action and task:
            if isinstance(task, str):
                if task == "play":
                    actor_bs = self.base.game_instance["player_np"]
                    if actor_bs:
                        if hasattr(actor_bs, "set_collision_response"):
                            actor_bs.node().set_collision_response(False)
                    any_action_seq = actor.actor_interval(action)
                    Sequence(Func(self.fsm_state_wrapper, "is_alive", False),
                             Func(self.fsm_state_wrapper, "is_busy", True),
                             any_action_seq,
                             Func(self.fsm_state_wrapper, "is_busy", False)).start()
