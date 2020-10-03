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

    def enterBigHitToHead(self, actor, action, task):
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

    def exitBigHitToHead(self):
        pass

    def enterBigHitToBody(self):
        pass

    def exitBigHitToBody(self):
        pass

    def enterSwim(self):
        pass

    def exitSwim(self):
        pass

    def enterLay(self):
        pass

    def exitLay(self):
        pass

    def enterLife(self):
        pass

    def exitLife(self):
        pass

    def enterDeath(self):
        pass

    def exitDeath(self):
        pass

    def filterBigHitToHead(self, request, args):
        if (base.states['is_attacked'] is False
                and request in ['BigHitToHead']):
            base.states['is_attacked'] = True
            return (request,) + args

        # Prevent per-frame calling the request
        else:
            # import pdb; pdb.set_trace()
            # base.states['is_attacked'] = False
            return None

    def filterBigHitToBody(self, request, args):
        if request not in ['BigHitToBody']:
            base.states['is_attacked'] = True
            return (request,) + args
        else:
            base.states['is_attacked'] = False
            return None

    def filterLay(self, request, args):
        if request not in ['Lay']:
            return (request,) + args
        else:
            return None

    def filterLife(self, request, args):
        if request not in ['Life']:
            return (request,) + args
        else:
            return None

    def filterDeath(self, request, args):
        if request not in ['Death']:
            return (request,) + args
        else:
            return None
