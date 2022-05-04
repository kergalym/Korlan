from direct.fsm.FSM import FSM
from direct.interval.FunctionInterval import Func
from direct.interval.MetaInterval import Sequence
from panda3d.core import BitMask32


class NpcFSM(FSM):
    def __init__(self):
        FSM.__init__(self, "NpcFSM")
        self.base = base
        self.render = render
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
                    ai_behaviors.add_to_path(player)
                    ai_behaviors.start_follow()
                elif behavior == "pathfind":
                    ai_behaviors.path_find_to(player, "addPath")

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

    def fsm_state_wrapper(self, actor, stack_name, state_name, bool_):
        if actor and stack_name and state_name and isinstance(bool_, bool):
            actor.get_python_tag(stack_name)[state_name] = bool_

    def enterIdle(self, actor, action, task):
        if actor and action and task:
            any_action = actor.get_anim_control(action)

            if isinstance(task, str):
                if task == "play":
                    if not any_action.is_playing():
                        actor.play(action)
                elif task == "loop":
                    if not any_action.is_playing():
                        actor.loop(action)

    def enterWalk(self, actor, player, ai_chars_bs, ai_behaviors, behavior, action, vect, task):
        if actor and player and ai_chars_bs and ai_behaviors and behavior and action and task:
            any_action = actor.get_anim_control(action)

            if isinstance(task, str):
                if task == "play":
                    if not any_action.is_playing():
                        actor.play(action)
                elif task == "loop":
                    if not any_action.is_playing():
                        actor.loop(action)
                actor.set_play_rate(1.0, action)

            # Get correct NodePath
            if self.base.game_instance["use_pandai"] and ai_chars_bs:
                name = actor.get_name()
                actor_bs = ai_chars_bs[name]
                self.set_basic_npc_behaviors(actor=actor_bs,
                                             player=player,
                                             ai_behaviors=ai_behaviors,
                                             behavior=behavior,
                                             vect=vect)

    def enterWalkAny(self, actor, path, ai_chars_bs, ai_behaviors, behavior, action, task):
        if actor and path and ai_chars_bs and ai_behaviors and behavior and action and task:
            any_action = actor.get_anim_control(action)

            if isinstance(task, str):
                if task == "play":
                    if not any_action.is_playing():
                        actor.play(action)
                elif task == "loop":
                    if not any_action.is_playing():
                        actor.loop(action)

            # Get correct NodePath
            if ai_chars_bs:
                name = actor.get_name()
                actor = ai_chars_bs[name]
                self.set_pathfollow_static_behavior(actor=actor.get_parent(),
                                                    path=path,
                                                    ai_behaviors=ai_behaviors,
                                                    behavior=behavior)

    def enterAttack(self, actor, action, task):
        if actor and action and task:
            any_action = actor.get_anim_control(action)
            # any_action_seq = actor.actor_interval(action)

            suffix = '**RightHand:HB'
            # suffix = ""
            """if actor.get_python_tag("generic_states")['has_sword']:
                suffix = "sword_BGN"
            elif not actor.get_python_tag("generic_states")['has_sword']:
                suffix = "RightHand:HB"
            """

            hitbox_np = actor.find("**/{0}".format(suffix))

            if isinstance(task, str):
                if task == "play":

                    if not any_action.is_playing():
                        actor.play(action)
                    else:
                        if actor.get_current_frame(action) == 0:
                            self.fsm_state_wrapper(actor, "human_states", "is_hitting", True)
                            self.fsm_state_wrapper(actor, "generic_states", "is_idle", False)
                        elif (actor.get_current_frame(action) > 0
                                and actor.get_current_frame(action) < 2):
                            hitbox_np.set_collide_mask(BitMask32.bit(1))
                        elif (actor.get_current_frame(action) > actor.get_num_frames(action)-6
                              and actor.get_current_frame(action) < actor.get_num_frames(action)-2):
                            hitbox_np.set_collide_mask(BitMask32.allOff())
                        elif actor.get_current_frame(action) == actor.get_num_frames(action):
                            self.fsm_state_wrapper(actor, "human_states", "is_hitting", False)
                            self.fsm_state_wrapper(actor, "generic_states", "is_idle", True)
                            actor.stop(action)

    def enterAttacked(self, actor, action, task):
        if actor and action and task and isinstance(action, str):

            if isinstance(task, str):
                if task == "play":
                    any_action = actor.get_anim_control(action)

                    actor.play(action)

                    if (actor.get_current_frame(action) > 0
                            and actor.get_current_frame(action) < 2):
                        self.fsm_state_wrapper(actor, "generic_states", "is_idle", False)
                        self.fsm_state_wrapper(actor, "generic_states", "is_attacked", True)
                    elif (actor.get_current_frame(action) > actor.get_num_frames(action) - 6
                          and actor.get_current_frame(action) < actor.get_num_frames(action) - 2):
                        self.fsm_state_wrapper(actor, "generic_states", "is_attacked", False)
                        self.fsm_state_wrapper(actor, "generic_states", "is_idle", True)
                        actor.stop(action)

            """if task == "play":
                any_action_seq = actor.actor_interval(action)
                Sequence(Func(self.fsm_state_wrapper, actor, "generic_states", "is_idle", False),
                         Func(self.fsm_state_wrapper, actor, "generic_states", "is_attacked", True),
                         any_action_seq,
                         Func(self.fsm_state_wrapper, actor, "generic_states", "is_attacked", False),
                         Func(self.fsm_state_wrapper, actor, "generic_states", "is_idle", True)).start()"""

    def enterForwardRoll(self, actor, action, task):
        if actor and action and task:
            any_action = actor.get_anim_control(action)

            if isinstance(task, str):
                if task == "play":
                    if not any_action.is_playing():
                        actor.play(action)

                elif task == "loop":
                    if not any_action.is_playing():
                        actor.loop(action)

    def enterHAttack(self):
        pass

    def enterFAttack(self):
        pass

    def enterBlock(self, actor, action, task):
        if actor and action and task:
            any_action = actor.get_anim_control(action)

            if isinstance(task, str):
                if task == "play":
                    if not any_action.is_playing():
                        actor.play(action)

                elif task == "loop":
                    if not any_action.is_playing():
                        actor.loop(action)

    def enterInteract(self):
        pass

    def enterLife(self):
        pass

    def enterDeath(self, actor, action, task):
        if actor and action and task:
            any_action = actor.get_anim_control(action)

            name = "{0}:BS".format(actor.get_name())
            actor_bs = self.base.game_instance['actors_np'][name]
            actor_bs.node().set_collision_response(False)

            if isinstance(task, str):
                if task == "play":
                    if not any_action.is_playing():
                        actor.play(action)

                elif task == "loop":
                    if not any_action.is_playing():
                        actor.loop(action)

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

