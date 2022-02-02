from direct.fsm.FSM import FSM
from direct.interval.MetaInterval import Sequence
from direct.task.TaskManagerGlobal import taskMgr


class NpcFSM(FSM):
    def __init__(self):
        FSM.__init__(self, "NpcFSM")
        self.base = base
        self.render = render
        self.taskMgr = taskMgr
        base.fsm = self

    def set_basic_npc_behaviors(self, actor, player, ai_behaviors, behavior, vect):
        if (actor and player
                and not actor.is_empty()
                and not player.is_empty()
                and behavior
                and isinstance(behavior, str)
                and isinstance(vect, dict)
                and ai_behaviors):
            if ai_behaviors and vect:
                # player could be another npc actor instead
                if behavior == "seek":
                    ai_behaviors.seek(player)
                    # if player is static object do flee
                elif behavior == "flee":
                    ai_behaviors.flee(player,
                                      vect['panic_dist'],
                                      vect['relax_dist'])
                    # if player is dynamic object do evade
                elif behavior == "evader":
                    ai_behaviors.evade(player,
                                       vect['panic_dist'],
                                       vect['relax_dist'])
                elif behavior == "pursuer":
                    ai_behaviors.pursue(player)
                elif behavior == "wanderer":
                    ai_behaviors.path_find_to(player, "addPath")
                    ai_behaviors.wander(vect["wander_radius"],
                                        vect["plane_flag"],
                                        vect["area_of_effect"])
                elif behavior == "pathfollow":
                    ai_behaviors.path_follow(1)
                    ai_behaviors.add_to_path(player())
                    ai_behaviors.start_follow()
                elif behavior == "pathfind":
                    ai_behaviors.path_find_to(player, "addPath")
                    # ai_behaviors.add_dynamic_obstacle(player)

    def set_pathfollow_static_behavior(self, actor, path, ai_behaviors, behavior):
        if (actor and path, not actor.is_empty()
            and behavior
            and isinstance(behavior, str)
            and isinstance(path, list)
            or isinstance(path, int)
            or isinstance(path, float)
                            and ai_behaviors):
            if behavior == "pathfollow":
                ai_behaviors.path_follow(1)
                ai_behaviors.add_to_path(path)
                ai_behaviors.start_follow()

    def set_state(self, actor, stack_name, state_name, bool_):
        if actor and stack_name and state_name and isinstance(bool_, bool):
            actor.get_python_tag(stack_name)[state_name] = bool_

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

    def enterWalk(self, actor, player, ai_behaviors, behavior, action, vect, task):
        if actor and player and ai_behaviors and behavior and action and task:
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

            # Get correct NodePath
            # actor = render.find("**/{0}".format(actor.get_name()))
            if hasattr(self.base, "ai_chars_bs") and self.base.ai_chars_bs:
                name = actor.get_name()
                actor = self.base.ai_chars_bs[name]
                self.set_basic_npc_behaviors(actor=actor,
                                             player=player,
                                             ai_behaviors=ai_behaviors,
                                             behavior=behavior,
                                             vect=vect)

    def enterWalkAny(self, actor, path, ai_behaviors, behavior, action, task):
        if actor and path and ai_behaviors and behavior and action and task:
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
            self.set_pathfollow_static_behavior(actor=actor.get_parent(),
                                                path=path,
                                                ai_behaviors=ai_behaviors,
                                                behavior=behavior)

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
                                 actor.actor_interval(action_next, loop=1),
                                 self.set_state(self, actor, "generic_states", "is_attacked", False)).start()

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
