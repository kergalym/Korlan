from direct.fsm.FSM import FSM
from direct.interval.FunctionInterval import Func, Wait
from direct.interval.MetaInterval import Sequence, Parallel
from direct.task.TaskManagerGlobal import taskMgr
from panda3d.core import BitMask32, Vec3
from Engine.Actors.NPC.archery import Archery


class NpcFSM(FSM):
    def __init__(self, npc_name):
        FSM.__init__(self, "NpcFSM")
        self.base = base
        self.render = render
        base.fsm = self
        self.archery = None
        self.npc_name = npc_name
        taskMgr.add(self.archery_waiting_task, "archery_waiting_task")

    def archery_waiting_task(self, task):
        if (self.base.game_instance['physics_is_activated'] == 1
                and self.base.game_instance['ai_is_activated'] == 1):
            if ("Horse" not in self.npc_name
                    and "Animal" not in self.npc_name):
                self.archery = Archery(self.npc_name)
                self.archery.is_arrow_ready = False
                taskMgr.add(self.archery.prepare_arrows_helper(arrow_name="bow_arrow",
                                                               joint_name="Korlan:Spine1"))
                return task.done

        return task.cont

    def archery_charge_wrapper(self):
        if (len(self.archery.arrows) > 0
                and self.archery.arrow_ref.get_python_tag("ready") == 0):
            if self.archery.arrow_is_prepared:
                if self.archery.target_test_ui:
                    self.archery.target_test_ui.show()
                power = self.archery.arrow_ref.get_python_tag("power")
                if power < self.archery.arrow_charge_units:
                    power = self.archery.arrow_charge_units
                    self.archery.arrow_ref.set_python_tag("power", power)

    def archery_bow_shoot_wrapper(self):
        if (self.archery.arrow_ref
                and self.archery.arrow_ref.get_python_tag("ready") == 0
                and self.archery.arrow_ref.get_python_tag("shot") == 0
                and self.archery.arrow_ref.get_python_tag("power") > 0):

            if (self.archery.arrow_is_prepared
                    and len(self.archery.arrows) > 0):
                self.archery.arrow_ref.set_python_tag("ready", 1)
                self.archery.bow_shoot()

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

    def enterWalkRD(self, actor, action, task):
        if actor and action and task:
            any_action = actor.get_anim_control(action)

            if isinstance(task, str):
                if task == "play":
                    if not any_action.is_playing():
                        actor.play(action)
                elif task == "loop":
                    if not any_action.is_playing():
                        actor.loop(action)
                actor.set_play_rate(1.0, action)

    def enterTurn(self, actor, action, task):
        if actor and action and task:
            if isinstance(task, str):
                if task == "play":
                    any_action_seq = actor.actor_interval(action)
                    Sequence(Func(self.fsm_state_wrapper, actor, "generic_states", "is_busy", True),
                             any_action_seq,
                             Func(self.fsm_state_wrapper, actor, "generic_states", "is_busy", False)).start()

    def enterGetWeapon(self, actor, action, weapon_name, bone_name, task):
        if actor and action and actor and weapon_name and bone_name and task:
            any_action = actor.get_anim_control(action)
            if isinstance(task, str):
                if task == "play":

                    if "bow" in weapon_name:
                        self.archery.start_archery_helper_tasks(),

                    if not any_action.is_playing():
                        has_weapon = "has_{0}".format(weapon_name)
                        any_action_seq = actor.actor_interval(action)
                        npc_state = self.base.game_instance["npc_state_cls"]
                        Sequence(Func(self.fsm_state_wrapper, actor, "generic_states", "is_busy", True),
                                 Func(npc_state.get_weapon, actor, weapon_name, bone_name),
                                 any_action_seq,
                                 Func(self.fsm_state_wrapper, actor, "generic_states", "is_busy", False),
                                 Func(self.fsm_state_wrapper, actor, "human_states", has_weapon, True)).start()

    def enterRemoveWeapon(self, actor, action, weapon_name, bone_name, task):
        if actor and action and actor and weapon_name and bone_name and task:
            any_action = actor.get_anim_control(action)
            if isinstance(task, str):
                if task == "play":

                    if "bow" in weapon_name:
                        self.archery.stop_archery_helper_tasks(),

                    if not any_action.is_playing():
                        has_weapon = "has_{0}".format(weapon_name)
                        any_action_seq = actor.actor_interval(action)
                        npc_state = self.base.game_instance["npc_state_cls"]
                        Sequence(Func(self.fsm_state_wrapper, actor, "generic_states", "is_busy", True),
                                 Func(npc_state.remove_weapon, actor, weapon_name, bone_name),
                                 any_action_seq,
                                 Func(self.fsm_state_wrapper, actor, "generic_states", "is_busy", False),
                                 Func(self.fsm_state_wrapper, actor, "human_states", has_weapon, False)).start()

    def enterHorseMount(self, actor, child, horse_name):
        parent = render.find("**/{0}".format(horse_name))
        if parent and child:
            # with inverted Z -0.5 stands for Up
            # Our horse (un)mounting animations have been made with imperfect positions,
            # so, I had to change child positions to get more satisfactory result
            # with these animations in my game.
            mounting_pos = Vec3(0.5, -0.15, -0.45)
            saddle_pos = Vec3(0, -0.32, 0.16)
            mount_action_seq = actor.actor_interval("horse_mounting",
                                                    playRate=self.base.actor_play_rate)
            horse_riding_action_seq = actor.actor_interval("horse_riding_idle",
                                                           playRate=self.base.actor_play_rate)
            actor.set_python_tag("mounted_horse", horse_name)

            Sequence(Func(child.set_collide_mask, BitMask32.allOff()),
                     Func(self.fsm_state_wrapper, actor, "generic_states", "is_using", True),
                     Parallel(mount_action_seq,
                              Func(child.reparent_to, parent),
                              Func(child.set_x, mounting_pos[0]),
                              Func(child.set_y, mounting_pos[1]),
                              Func(actor.set_z, mounting_pos[2]),
                              Func(child.set_h, 0)),
                     Func(child.set_x, saddle_pos[0]),
                     Func(child.set_y, saddle_pos[1]),
                     # bullet shape has impact of gravity
                     # so make player geom stay higher instead
                     Func(actor.set_z, saddle_pos[2]),
                     Func(self.fsm_state_wrapper, actor, "generic_states", "is_using", False),
                     Func(self.fsm_state_wrapper, actor, "human_states", "horse_riding", True),
                     Func(self.fsm_state_wrapper, actor, "human_states", "is_on_horse", True),
                     Func(parent.set_python_tag, "is_mounted", True),
                     horse_riding_action_seq
                     ).start()

    def enterHorseUnmount(self, actor, child):
        horse_name = actor.get_python_tag("mounted_horse")
        parent = render.find("**/{0}".format(horse_name))
        parent_bs = render.find("**/{0}:BS".format(horse_name))
        if parent and child:
            # with inverted Z -0.7 stands for Up
            # Our horse (un)mounting animations have been made with imperfect positions,
            # so, I had to change child positions to get more satisfactory result
            # with these animations in my game.
            unmounting_pos = Vec3(0.5, -0.15, -0.45)
            # Reparent parent/child node back to its BulletCharacterControllerNode
            unmount_action_seq = actor.actor_interval("horse_unmounting",
                                                      playRate=self.base.actor_play_rate)
            horse_near_pos = Vec3(parent_bs.get_x(), parent_bs.get_y(), child.get_z()) + Vec3(1, 0, 0)

            Sequence(Func(self.fsm_state_wrapper, actor, "generic_states", "is_using", True),
                     Parallel(unmount_action_seq,
                              Func(child.set_x, unmounting_pos[0]),
                              Func(child.set_y, unmounting_pos[1]),
                              Func(actor.set_z, unmounting_pos[2])),
                     # revert player geom height
                     Func(child.reparent_to, render),
                     Func(child.set_x, horse_near_pos[0]),
                     Func(child.set_y, horse_near_pos[1]),
                     Func(actor.set_z, -1),
                     Func(self.fsm_state_wrapper, actor, "generic_states", "is_using", False),
                     Func(self.fsm_state_wrapper, actor, "human_states", "horse_riding", False),
                     Func(self.fsm_state_wrapper, actor, "human_states", "is_on_horse", False),
                     Func(parent.set_python_tag, "is_mounted", False),
                     Func(child.set_collide_mask, BitMask32.allOn())
                     ).start()

    def enterAttack(self, actor, action, task):
        if actor and action and task:
            any_action = actor.get_anim_control(action)

            suffix = ""
            if actor.get_python_tag("human_states")['has_sword']:
                suffix = "sword_BGN"
            elif not actor.get_python_tag("human_states")['has_sword']:
                suffix = "RightHand:HB"

            hitbox_np = actor.find("**/**{0}".format(suffix))

            if isinstance(task, str):
                if task == "play":
                    if not any_action.is_playing():
                        any_action_seq = actor.actor_interval(action)
                        Sequence(Func(self.fsm_state_wrapper, actor, "generic_states", "is_busy", True),
                                 Func(hitbox_np.set_collide_mask, BitMask32.bit(1)),
                                 any_action_seq,
                                 Func(hitbox_np.set_collide_mask, BitMask32.allOff()),
                                 Func(self.fsm_state_wrapper, actor, "generic_states", "is_busy", False)).start()

    def enterArchery(self, actor, action, task):
        if actor and action and task:
            if isinstance(task, str) and len(self.archery.arrows) > 0:
                if task == "play":
                    crouched_to_standing = actor.get_anim_control('crouched_to_standing')

                    if self.archery.arrow_ref:
                        if self.archery.arrow_ref.get_python_tag("power") > 0:
                            self.archery.arrow_ref.set_python_tag("power", 0)

                    if (crouched_to_standing.is_playing() is False
                            and base.player_states['is_crouching'] is True):
                        # TODO: Use blending for smooth transition between animations
                        # Do an animation sequence if player is crouched.
                        crouch_to_stand_seq = actor.actor_interval('crouched_to_standing',
                                                                   playRate=self.base.actor_play_rate)
                        any_action_seq = actor.actor_interval(action,
                                                              playRate=self.base.actor_play_rate)

                        Sequence(crouch_to_stand_seq,
                                 Func(self.fsm_state_wrapper, actor, "generic_states", "is_busy", True),
                                 Func(self.archery.prepare_arrow_for_shoot, "bow"),
                                 any_action_seq,
                                 Func(self.archery_charge_wrapper),
                                 Func(self.archery_bow_shoot_wrapper),
                                 Wait(1),
                                 Func(self.fsm_state_wrapper, actor, "generic_states", "is_busy", False)
                                 ).start()

                    elif (crouched_to_standing.is_playing() is False
                          and base.player_states['is_crouching'] is False):
                        any_action_seq = actor.actor_interval(action,
                                                              playRate=self.base.actor_play_rate)
                        Sequence(Func(self.fsm_state_wrapper, actor, "generic_states", "is_busy", True),
                                 Func(self.archery.prepare_arrow_for_shoot, "bow"),
                                 any_action_seq,
                                 Func(self.archery_charge_wrapper),
                                 Func(self.archery_bow_shoot_wrapper),
                                 Wait(1),
                                 Func(self.fsm_state_wrapper, actor, "generic_states", "is_busy", False)
                                 ).start()

    def enterForwardRoll(self, actor, action, task):
        if actor and action and task:
            if isinstance(task, str):
                if task == "play":
                    any_action_seq = actor.actor_interval(action)
                    Sequence(Func(self.fsm_state_wrapper, actor, "generic_states", "is_busy", True),
                             any_action_seq,
                             Func(self.fsm_state_wrapper, actor, "generic_states", "is_busy", False)).start()

    def enterHAttack(self, actor, action, task):
        if actor and action and task and isinstance(action, str):
            if isinstance(task, str):
                if task == "play":
                    any_action_seq = actor.actor_interval(action)
                    Sequence(Func(self.fsm_state_wrapper, actor, "generic_states", "is_busy", True),
                             any_action_seq,
                             Func(self.fsm_state_wrapper, actor, "generic_states", "is_busy", False)).start()

    def enterFAttack(self, actor, action, task):
        if actor and action and task and isinstance(action, str):
            if isinstance(task, str):
                if task == "play":
                    any_action_seq = actor.actor_interval(action)
                    Sequence(Func(self.fsm_state_wrapper, actor, "generic_states", "is_busy", True),
                             any_action_seq,
                             Func(self.fsm_state_wrapper, actor, "generic_states", "is_busy", False)).start()

    def enterBlock(self, actor, action, task):
        if actor and action and task:
            any_action = actor.get_anim_control(action)

            suffix = ""
            if actor.get_python_tag("human_states")['has_sword']:
                suffix = "sword_BGN"
            elif not actor.get_python_tag("human_states")['has_sword']:
                suffix = "RightHand:HB"

            hitbox_np = actor.find("**/**{0}".format(suffix))

            if isinstance(task, str):
                if task == "play":
                    if not any_action.is_playing():
                        any_action_seq = actor.actor_interval(action)
                        Sequence(Func(self.fsm_state_wrapper, actor, "generic_states", "is_busy", True),
                                 Func(hitbox_np.set_collide_mask, BitMask32.bit(1)),
                                 any_action_seq,
                                 Func(hitbox_np.set_collide_mask, BitMask32.allOff()),
                                 Func(self.fsm_state_wrapper, actor, "generic_states", "is_busy", False)).start()

    def enterDodge(self, actor, action, task):
        if actor and action and task and isinstance(action, str):
            if isinstance(task, str):
                if task == "play":
                    any_action_seq = actor.actor_interval(action)
                    Sequence(Func(self.fsm_state_wrapper, actor, "generic_states", "is_busy", True),
                             any_action_seq,
                             Func(self.fsm_state_wrapper, actor, "generic_states", "is_busy", False)).start()

    def enterInteract(self, actor, action, task):
        if actor and action and task and isinstance(action, str):
            if isinstance(task, str):
                if task == "play":
                    any_action_seq = actor.actor_interval(action)
                    Sequence(Func(self.fsm_state_wrapper, actor, "generic_states", "is_busy", True),
                             any_action_seq,
                             Func(self.fsm_state_wrapper, actor, "generic_states", "is_busy", False)).start()

    def enterAttacked(self, actor, action, task):
        if actor and action and task and isinstance(action, str):
            if isinstance(task, str):
                if task == "play":
                    any_action_seq = actor.actor_interval(action)
                    Sequence(Func(self.fsm_state_wrapper, actor, "generic_states", "is_attacked", True),
                             any_action_seq,
                             Func(self.fsm_state_wrapper, actor, "generic_states", "is_attacked", False)).start()

    def enterLife(self, actor, action, task):
        if actor and action and task and isinstance(action, str):
            if isinstance(task, str):
                if task == "play":
                    any_action_seq = actor.actor_interval(action)
                    Sequence(Func(self.fsm_state_wrapper, actor, "generic_states", "is_busy", True),
                             any_action_seq,
                             Func(self.fsm_state_wrapper, actor, "generic_states", "is_busy", False)).start()

    def enterDeath(self, actor, action, task):
        if actor and action and task:
            if isinstance(task, str):
                if task == "play":
                    name = "{0}:BS".format(actor.get_name())
                    actor_bs = self.base.game_instance['actors_np'][name]
                    if actor_bs:
                        if hasattr(actor_bs, "set_collision_response"):
                            actor_bs.node().set_collision_response(False)
                    any_action_seq = actor.actor_interval(action)
                    Sequence(Func(self.fsm_state_wrapper, actor, "generic_states", "is_alive", False),
                             Func(self.fsm_state_wrapper, actor, "generic_states", "is_busy", True),
                             any_action_seq,
                             Func(self.fsm_state_wrapper, actor, "generic_states", "is_busy", False)).start()

    def enterCrouch(self, actor, task):
        if actor and task:
            if isinstance(task, str):
                if task == "play":
                    if not actor.get_python_tag("generic_states")["is_crouch_moving"]:
                        any_action_seq = actor.actor_interval("standing_to_crouch")
                        Sequence(Func(self.fsm_state_wrapper, actor, "generic_states", "is_crouching", True),
                                 any_action_seq,
                                 Func(self.fsm_state_wrapper, actor, "generic_states", "is_crouching", False),
                                 Func(self.fsm_state_wrapper, actor, "generic_states", "is_crouch_moving",
                                      True)).start()
                    elif actor.get_python_tag("generic_states")["is_crouch_moving"]:
                        any_action_seq = actor.actor_interval("crouched_to_standing")
                        Sequence(Func(self.fsm_state_wrapper, actor, "generic_states", "is_crouching", True),
                                 any_action_seq,
                                 Func(self.fsm_state_wrapper, actor, "generic_states", "is_crouching", False),
                                 Func(self.fsm_state_wrapper, actor, "generic_states", "is_crouch_moving",
                                      False)).start()

    def _player_jump_move_task(self, actor, actor_bs_npc, action, task):
        if actor.getCurrentFrame(action):
            if (actor.getCurrentFrame(action) > 24
                    and actor.getCurrentFrame(action) < 27):
                current_pos = actor_bs_npc.get_pos()
                delta_offset = current_pos + Vec3(0, -2.0, 0)
                pos_interval_seq = actor_bs_npc.posInterval(1.0, delta_offset,
                                                            startPos=current_pos)
                seq = Sequence(pos_interval_seq)
                if not seq.is_playing():
                    seq.start()

                return task.done

        return task.cont

    def _player_bullet_jump_helper(self, actor, action):
        name = "{0}:BS".format(actor.get_name())
        if self.base.game_instance['actors_np'].get(name):
            actor_bs_npc = self.base.game_instance['actors_np'][name]
            # if self.base.game_instance['actor_controllers_np'][name].is_on_ground():
            #    self.base.game_instance['actor_controllers_np'][name].set_max_jump_height(3.0)
            #    self.base.game_instance['actor_controllers_np'][name].set_jump_speed(8.0)
            #    self.base.game_instance['actor_controllers_np'][name].do_jump()

            if taskMgr.hasTaskNamed("player_jump_move_task"):
                taskMgr.remove("player_jump_move_task")

            taskMgr.add(self._player_jump_move_task,
                        "player_jump_move_task",
                        extraArgs=[actor, actor_bs_npc, action],
                        appendTask=True)

    def enterJump(self, actor, action, task):
        if actor and action and task and isinstance(action, str):
            if isinstance(task, str):
                if task == "play":
                    any_action_seq = actor.actor_interval(action)
                    Sequence(Func(self.fsm_state_wrapper, actor, "generic_states", "is_jumping", True),
                             Func(self._player_bullet_jump_helper, actor, action),
                             any_action_seq,
                             Func(self.fsm_state_wrapper, actor, "generic_states", "is_jumping", False)).start()

    def enterLay(self, actor, action, task):
        if actor and action and task and isinstance(action, str):
            if isinstance(task, str):
                if task == "play":
                    any_action_seq = actor.actor_interval(action)
                    Sequence(Func(self.fsm_state_wrapper, actor, "generic_states", "is_busy", True),
                             any_action_seq,
                             Func(self.fsm_state_wrapper, actor, "generic_states", "is_busy", False)).start()
