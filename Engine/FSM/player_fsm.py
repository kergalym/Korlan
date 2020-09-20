from direct.fsm.FSM import FSM
from direct.showbase.DirectObject import DirectObject
from configparser import ConfigParser
from direct.task.TaskManagerGlobal import taskMgr


class PlayerFSM(FSM):
    def __init__(self):
        FSM.__init__(self, 'PlayerFSM')
        self.d_object = DirectObject()
        self.cfg_parser = ConfigParser()
        self.is_moving = False
        self.is_crouching = False
        self.is_jumping = False
        self.is_hitting = False
        self.is_using = False
        self.is_blocking = False
        self.is_has_sword = False
        self.is_has_bow = False
        self.is_has_tengri = False
        self.is_has_umai = False
        self.base = base
        self.render = render
        self.player = None
        self.taskMgr = taskMgr

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

    # TODO: code review
    def enterWalk(self, actor, action, state):
        if actor and action and state:
            any_action = actor.getAnimControl(action)
            if (isinstance(state, str)
                    and any_action.isPlaying() is False
                    and self.is_moving):
                if state == "play":
                    actor.play(action)
                elif state == "loop":
                    actor.loop(action)
                actor.set_play_rate(self.base.actor_play_rate, action)

    def exitWalk(self):
        self.is_moving = False

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
