from direct.fsm.FSM import FSM


class Husband(FSM):
    def __init__(self):
        FSM.__init__(self, "Husband")
        # TODO: Change the name to Ernar
        self.base = base
        self.name = "NPC_Ernar"
        self.age = 32
        self.iq = 95
        self.health = 100
        self.stamina = 100
        self.power = 40
        self.fearless = 50

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
            # Since it's Bullet shaped actor, we need access the model which is now child of
            if hasattr(base, 'actor_node') and base.actor_node:
                actor_node = base.actor_node
                # Check if node is same as bullet shape node
                if "NPC" in actor_node.get_name():
                    any_action = actor_node.actor_interval(action)
                    if (isinstance(state, str)
                            and any_action.isPlaying() is False
                            and base.behaviors['idle'] is False
                            and base.behaviors['walk']):
                        if state == "play":
                            actor_node.play(action)
                        elif state == "loop":
                            actor_node.loop(action)
                            self.enter_walk = 1
                        actor_node.set_play_rate(self.base.actor_play_rate, action)

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
