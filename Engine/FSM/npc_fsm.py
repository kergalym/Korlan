from direct.fsm.FSM import FSM
from direct.interval.FunctionInterval import Func, Wait
from direct.interval.MetaInterval import Sequence, Parallel
from direct.task.TaskManagerGlobal import taskMgr
from panda3d.core import BitMask32, Vec3
from Engine.Actors.NPC.archery import Archery

""" ANIMATIONS"""
from Engine import anim_names


class NpcFSM(FSM):
    def __init__(self, npc_name):
        FSM.__init__(self, "NpcFSM")
        self.base = base
        self.render = render
        base.fsm = self
        self.archery = None
        self.npc_name = npc_name
        self.mount_sequence = {npc_name: Sequence()}
        self.unmount_sequence = {npc_name: Sequence()}

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

    def fsm_state_wrapper(self, actor, stack_name, state_name, bool_):
        if actor and stack_name and state_name and isinstance(bool_, bool):
            actor.get_python_tag(stack_name)[state_name] = bool_

    def filterIdle(self, request, args):
        if request not in ['Idle']:
            return (request,) + args
        else:
            return None

    def enterIdle(self, actor, action, task):
        if actor and action and task:
            any_action = actor.get_anim_control(action)
            actor.set_play_rate(self.base.game_instance["current_play_rate"], action)

            self.base.sound.stop_walking()
            if isinstance(task, str):
                if task == "play":
                    if not any_action.is_playing():
                        actor.play(action)
                elif task == "loop":
                    if not any_action.is_playing():
                        actor.loop(action)

    def filterWalk(self, request, args):
        if request not in ['Walk']:
            return (request,) + args
        else:
            return None

    def enterWalk(self, actor, action, task):
        if actor and action and task:
            any_action = actor.get_anim_control(action)
            actor.set_play_rate(self.base.game_instance["current_play_rate"], action)

            self.base.sound.play_walking()
            if isinstance(task, str):
                if task == "play":
                    if not any_action.is_playing():
                        actor.play(action)
                elif task == "loop":
                    if not any_action.is_playing():
                        actor.loop(action)

    def enterTurn(self, actor, action, task):
        if actor and action and task:

            self.base.sound.play_walking()
            if isinstance(task, str):
                if task == "play":
                    any_action_seq = actor.actor_interval(action, playRate=self.base.game_instance["current_play_rate"])
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

                        self.base.sound.play_picking()
                        has_weapon = "has_{0}".format(weapon_name)
                        any_action_seq = actor.actor_interval(action, 
                                                              playRate=self.base.game_instance["current_play_rate"])
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

                        self.base.sound.play_picking()
                        has_weapon = "has_{0}".format(weapon_name)
                        any_action_seq = actor.actor_interval(action, 
                                                              playRate=self.base.game_instance["current_play_rate"])
                        npc_state = self.base.game_instance["npc_state_cls"]
                        Sequence(Func(self.fsm_state_wrapper, actor, "generic_states", "is_busy", True),
                                 Func(npc_state.remove_weapon, actor, weapon_name, bone_name),
                                 any_action_seq,
                                 Func(self.fsm_state_wrapper, actor, "generic_states", "is_busy", False),
                                 Func(self.fsm_state_wrapper, actor, "human_states", has_weapon, False)).start()

    def filterGetWeapon(self, request, args):
        if request not in ['HorseMount']:
            return (request,) + args
        else:
            return None

    def filterRemoveWeapon(self, request, args):
        if request not in ['HorseUnmount']:
            return (request,) + args
        else:
            return None

    def _actor_mount_helper_task(self, actor, child, parent, saddle_pos, task):
        if self.base.game_instance['menu_mode']:
            return task.done
        if actor.get_python_tag("human_states")["is_on_horse"]:
            if child:
                child.set_x(saddle_pos[0])
                child.set_y(saddle_pos[1])
                actor.set_z(saddle_pos[2])
                child.set_h(parent.get_h())

        return task.cont

    def enterHorseMount(self, actor, child, parent, parent_rb_np):
        if actor and parent and parent_rb_np and child:
            actor_name = actor.get_name()
            if not self.mount_sequence[actor_name].is_playing():
                physics_attr = self.base.game_instance["physics_attr_cls"]
                self.mount_sequence[actor_name] = Sequence()

                if int(child.get_distance(parent_rb_np)) > 1:
                    actor.set_h(-180)
                else:
                    actor.set_h(0)

                mounting_pos = Vec3(0.6, -0.16, 1.45)
                saddle_pos = Vec3(0, -0.32, 1)
                mount_action_seq = actor.actor_interval(anim_names.a_anim_horse_mounting, 
                                                        playRate=self.base.game_instance["current_play_rate"])
                horse_riding_action_seq = actor.actor_interval(anim_names.a_anim_horse_rider_idle, 
                                                               playRate=self.base.game_instance["current_play_rate"])
                actor.set_python_tag("mounted_horse", parent_rb_np)

                # Horse mounting consists of few intervals
                # bullet shape has impact of gravity
                # so make rider geom stay higher instead
                taskMgr.add(self._actor_mount_helper_task,
                            "actor_mount_helper_task",
                            extraArgs=[actor, child, parent, saddle_pos],
                            appendTask=True)

                set_use_true = Func(self.fsm_state_wrapper, actor, "generic_states", "is_using", True)
                remove_rigid_body = Func(physics_attr.remove_rigid_body_node, child)
                play_mount_anim = Parallel(mount_action_seq,
                                           Func(child.reparent_to, parent),
                                           Func(child.set_x, mounting_pos[0]),
                                           Func(child.set_y, mounting_pos[1]),
                                           Func(child.set_z, mounting_pos[2]),
                                           Func(child.set_h, 0))
                set_saddle_pos = Parallel(Func(child.set_x, saddle_pos[0]),
                                          Func(child.set_y, saddle_pos[1]),
                                          # bullet shape has impact of gravity
                                          # so make player geom stay higher instead
                                          Func(child.set_z, 0),
                                          Func(actor.set_z, saddle_pos[2]),
                                          Func(actor.set_h, 0))

                set_mounting_states = Parallel(Func(self.fsm_state_wrapper, actor, "generic_states", "is_using", False),
                                               Func(self.fsm_state_wrapper, actor, "human_states", "horse_riding",
                                                    True),
                                               Func(self.fsm_state_wrapper, actor, "human_states", "is_on_horse", True),
                                               Func(parent.set_python_tag, "is_mounted", True),
                                               Func(actor.set_python_tag, "current_task", None))
                play_riding_anim = horse_riding_action_seq

                self.mount_sequence[actor_name].append(set_use_true)
                self.mount_sequence[actor_name].append(remove_rigid_body)
                self.mount_sequence[actor_name].append(play_mount_anim)
                self.mount_sequence[actor_name].append(set_saddle_pos)
                self.mount_sequence[actor_name].append(set_mounting_states)
                self.mount_sequence[actor_name].append(play_riding_anim)
                self.mount_sequence[actor_name].start()

    def enterHorseUnmount(self, actor, child):
        parent_rb_np = actor.get_python_tag("mounted_horse")
        if parent_rb_np and parent_rb_np and child:
            actor_name = actor.get_name()
            if not self.unmount_sequence[actor_name].is_playing():
                physics_attr = self.base.game_instance["physics_attr_cls"]
                self.unmount_sequence[actor_name] = Sequence()
                unmounting_pos = Vec3(0.6, -0.16, child.get_z()-0.45)
                unmount_action_seq = actor.actor_interval(anim_names.a_anim_horse_unmounting, 
                                                          playRate=self.base.game_instance["current_play_rate"])
                mesh_default_z_pos = actor.get_python_tag("mesh_z_pos")
                horse_near_pos = Vec3(parent_rb_np.get_x(), parent_rb_np.get_y(),
                                      parent_rb_np.get_z()) + Vec3(0.6, -0.16, 0)

                taskMgr.remove("actor_mount_helper_task"),

                set_use_false = Func(self.fsm_state_wrapper, actor, "generic_states", "is_using", True)
                play_unmount_anim = Parallel(unmount_action_seq,
                                             Func(child.set_x, unmounting_pos[0]),
                                             Func(child.set_y, unmounting_pos[1]),
                                             Func(child.set_z, unmounting_pos[2])
                                             )
                # revert rider collider back
                reparent_to_render = Func(child.reparent_to, render)
                set_rigid_body = Func(physics_attr.set_rigid_body_nodepath_with_shape, actor, child)
                # Set player near of previous state
                set_near_pos = Parallel(Func(child.set_x, horse_near_pos[0]),
                                        Func(child.set_y, horse_near_pos[1]),
                                        Func(actor.set_z, mesh_default_z_pos),
                                        Func(child.set_z, parent_rb_np.get_z()+2))
                # Finalize unmounting
                set_unmounting_states = Parallel(
                    Func(self.fsm_state_wrapper, actor, "generic_states", "is_using", False),
                    Func(self.fsm_state_wrapper, actor, "human_states", "horse_riding", False),
                    Func(self.fsm_state_wrapper, actor, "human_states", "is_on_horse", False),
                    Func(parent_rb_np.get_child(0).set_python_tag, "is_mounted", False),
                    Func(actor.set_python_tag, "current_task", None),
                    Func(actor.set_python_tag, "mounted_horse", None))

                self.unmount_sequence[actor_name].append(set_use_false)
                self.unmount_sequence[actor_name].append(play_unmount_anim)
                self.unmount_sequence[actor_name].append(reparent_to_render)
                self.unmount_sequence[actor_name].append(set_rigid_body)
                self.unmount_sequence[actor_name].append(set_near_pos)
                self.unmount_sequence[actor_name].append(set_unmounting_states)

                self.unmount_sequence[actor_name].start()

    def filterHorseMount(self, request, args):
        if request not in ['HorseMount']:
            return (request,) + args
        else:
            return None

    def filterHorseUnmount(self, request, args):
        if request not in ['HorseUnmount']:
            return (request,) + args
        else:
            return None

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
                        any_action_seq = actor.actor_interval(action,
                                                              playRate=self.base.game_instance["current_play_rate"])
                        Sequence(Func(self.fsm_state_wrapper, actor, "generic_states", "is_busy", True),
                                 Func(hitbox_np.set_collide_mask, BitMask32.bit(1)),
                                 any_action_seq,
                                 Func(hitbox_np.set_collide_mask, BitMask32.allOff()),
                                 Func(self.fsm_state_wrapper, actor, "generic_states", "is_busy", False)).start()

    def enterArchery(self, actor, action, task):
        if actor and action and task:
            if isinstance(task, str) and len(self.archery.arrows) > 0:
                if task == "play":
                    crouched_to_standing = actor.get_anim_control(anim_names.a_anim_crouching_stand)

                    if self.archery.arrow_ref:
                        if self.archery.arrow_ref.get_python_tag("power") > 0:
                            self.archery.arrow_ref.set_python_tag("power", 0)

                    if (crouched_to_standing.is_playing() is False
                            and base.player_states['is_crouching'] is True):
                        # TODO: Use blending for smooth transition between animations
                        # Do an animation sequence if player is crouched.
                        crouch_to_stand_seq = actor.actor_interval(anim_names.a_anim_crouching_stand,
                                                                   playRate=self.base.game_instance["current_play_rate"])
                        any_action_seq = actor.actor_interval(action,
                                                              playRate=self.base.game_instance["current_play_rate"])

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
                                                              playRate=self.base.game_instance["current_play_rate"])
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
                    actor.set_play_rate(1.0, action)
                    any_action_seq = actor.actor_interval(action,
                                                          playRate=self.base.game_instance["current_play_rate"])
                    Sequence(Func(self.fsm_state_wrapper, actor, "generic_states", "is_busy", True),
                             any_action_seq,
                             Func(self.fsm_state_wrapper, actor, "generic_states", "is_busy", False)).start()

    def enterBackwardRoll(self, actor, action, task):
        if actor and action and task:
            if isinstance(task, str):
                if task == "play":
                    actor.set_play_rate(-1.0, action)
                    any_action_seq = actor.actor_interval(action,
                                                          playRate=self.base.game_instance["current_play_rate"])
                    Sequence(Func(self.fsm_state_wrapper, actor, "generic_states", "is_busy", True),
                             any_action_seq,
                             Func(self.fsm_state_wrapper, actor, "generic_states", "is_busy", False)).start()

    def enterForwardStep(self, actor, action, task):
        if actor and action and task:
            if isinstance(task, str):
                if task == "play":
                    any_action_seq = actor.actor_interval(action,
                                                          playRate=self.base.game_instance["current_play_rate"])
                    Sequence(Func(self.fsm_state_wrapper, actor, "generic_states", "is_busy", True),
                             any_action_seq,
                             Func(self.fsm_state_wrapper, actor, "generic_states", "is_busy", False)).start()

    def enterBackwardStep(self, actor, action, task):
        if actor and action and task:
            if isinstance(task, str):
                if task == "play":
                    any_action_seq = actor.actor_interval(action,
                                                          playRate=-self.base.game_instance["current_play_rate"])
                    Sequence(Func(self.fsm_state_wrapper, actor, "generic_states", "is_busy", True),
                             any_action_seq,
                             Func(self.fsm_state_wrapper, actor, "generic_states", "is_busy", False)).start()

    def enterHAttack(self, actor, action, task):
        if actor and action and task and isinstance(action, str):
            if isinstance(task, str):
                if task == "play":

                    self.base.sound.play_kicking()

                    any_action_seq = actor.actor_interval(action,
                                                          playRate=self.base.game_instance["current_play_rate"])
                    Sequence(Func(self.fsm_state_wrapper, actor, "generic_states", "is_busy", True),
                             any_action_seq,
                             Func(self.fsm_state_wrapper, actor, "generic_states", "is_busy", False)).start()

    def enterFAttack(self, actor, action, task):
        if actor and action and task and isinstance(action, str):
            if isinstance(task, str):
                if task == "play":

                    self.base.sound.play_punching()

                    any_action_seq = actor.actor_interval(action,
                                                          playRate=self.base.game_instance["current_play_rate"])
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
                        any_action_seq = actor.actor_interval(action,
                                                              playRate=self.base.game_instance["current_play_rate"])
                        Sequence(Func(self.fsm_state_wrapper, actor, "generic_states", "is_blocking", True),
                                 Func(hitbox_np.set_collide_mask, BitMask32.bit(1)),
                                 any_action_seq,
                                 Func(hitbox_np.set_collide_mask, BitMask32.allOff()),
                                 Func(self.fsm_state_wrapper, actor, "generic_states", "is_blocking", False)).start()

    def enterDodge(self, actor, action, task):
        if actor and action and task and isinstance(action, str):
            if isinstance(task, str):
                if task == "play":
                    any_action_seq = actor.actor_interval(action,
                                                          playRate=self.base.game_instance["current_play_rate"])
                    Sequence(Func(self.fsm_state_wrapper, actor, "generic_states", "is_busy", True),
                             any_action_seq,
                             Func(self.fsm_state_wrapper, actor, "generic_states", "is_busy", False)).start()

    def enterInteract(self, actor, action, task):
        if actor and action and task and isinstance(action, str):
            if isinstance(task, str):
                if task == "play":
                    any_action_seq = actor.actor_interval(action,
                                                          playRate=self.base.game_instance["current_play_rate"])
                    Sequence(Func(self.fsm_state_wrapper, actor, "generic_states", "is_busy", True),
                             any_action_seq,
                             Func(self.fsm_state_wrapper, actor, "generic_states", "is_busy", False)).start()

    def enterAttacked(self, actor, task):
        if actor and task:
            if isinstance(task, str):
                if task == "play":

                    if actor.get_python_tag("npc_type") == "npc":
                        if not actor.get_python_tag("human_states")["is_on_horse"]:
                            action = anim_names.a_anim_damage_1
                        else:
                            action = anim_names.a_anim_damage_rider
                    else:
                        name = "{0}_{1}".format(anim_names.a_anim_damage_any, actor.get_name())
                        action = name

                    if action != '':
                        self.base.sound.play_male_hurting()
                        any_action_seq = actor.actor_interval(action,
                                                              playRate=self.base.game_instance["current_play_rate"])
                        Sequence(Func(self.fsm_state_wrapper, actor, "generic_states", "is_attacked", True),
                                 any_action_seq,
                                 Func(self.fsm_state_wrapper, actor, "generic_states", "is_attacked", False)).start()

    def enterLife(self, actor, action, task):
        if actor and action and task and isinstance(action, str):
            if isinstance(task, str):
                if task == "play":
                    any_action_seq = actor.actor_interval(action,
                                                          playRate=self.base.game_instance["current_play_rate"])
                    Sequence(Func(self.fsm_state_wrapper, actor, "generic_states", "is_busy", True),
                             any_action_seq,
                             Func(self.fsm_state_wrapper, actor, "generic_states", "is_busy", False)).start()

    def enterDeath(self, actor, action, task):
        if actor and action and task:
            if isinstance(task, str):
                if task == "play":
                    self.base.sound.play_male_dying()
                    actor.get_parent().set_collide_mask(BitMask32.bit(0))
                    any_action_seq = actor.actor_interval(action,
                                                          playRate=self.base.game_instance["current_play_rate"])
                    Sequence(Func(self.fsm_state_wrapper, actor, "generic_states", "is_alive", False),
                             Func(self.fsm_state_wrapper, actor, "generic_states", "is_busy", True),
                             any_action_seq,
                             Func(self.fsm_state_wrapper, actor, "generic_states", "is_busy", False)).start()

    def enterCrouch(self, actor, actor_rb_np, task):
        if actor and task:
            if isinstance(task, str):
                if task == "play":
                    ph_ = self.base.game_instance["physics_attr_cls"]

                    if not actor.get_python_tag("generic_states")["is_crouch_moving"]:

                        # ph_.remove_character_controller_node(actor_rb_np)
                        # ph_.set_character_controller_nodepath_half_height_shape(actor, actor_rb_np)

                        any_action_seq = actor.actor_interval(anim_names.a_anim_standing_crouch,
                                                              playRate=self.base.game_instance["current_play_rate"])
                        Sequence(Func(self.fsm_state_wrapper, actor, "generic_states", "is_crouching", True),
                                 any_action_seq,
                                 Func(self.fsm_state_wrapper, actor, "generic_states", "is_crouching", False),
                                 Func(self.fsm_state_wrapper, actor, "generic_states", "is_crouch_moving",
                                      True)).start()
                    elif actor.get_python_tag("generic_states")["is_crouch_moving"]:

                        ph_.remove_character_controller_node(actor_rb_np)
                        # ph_.set_character_controller_nodepath_with_shape(actor, actor_rb_np)

                        any_action_seq = actor.actor_interval(anim_names.a_anim_crouching_stand,
                                                              playRate=self.base.game_instance["current_play_rate"])
                        Sequence(Func(self.fsm_state_wrapper, actor, "generic_states", "is_crouching", True),
                                 any_action_seq,
                                 Func(self.fsm_state_wrapper, actor, "generic_states", "is_crouching", False),
                                 Func(self.fsm_state_wrapper, actor, "generic_states", "is_crouch_moving",
                                      False)).start()

    def filterCrouch(self, request, args):
        if request not in ['Crouch']:
            return (request,) + args
        else:
            return None

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

    def _player_bullet_jump_helper(self, actor, actor_rb_np, action):
        name = "{0}:BS".format(actor.get_name())
        if self.base.game_instance['actors_np'].get(name):
            # if self.base.game_instance['actor_controllers_np'][name].is_on_ground():
            #    self.base.game_instance['actor_controllers_np'][name].set_max_jump_height(3.0)
            #    self.base.game_instance['actor_controllers_np'][name].set_jump_speed(8.0)
            #    self.base.game_instance['actor_controllers_np'][name].do_jump()

            if taskMgr.hasTaskNamed("player_jump_move_task"):
                taskMgr.remove("player_jump_move_task")

            taskMgr.add(self._player_jump_move_task,
                        "player_jump_move_task",
                        extraArgs=[actor, actor_rb_np, action],
                        appendTask=True)

    def enterJump(self, actor, actor_rb_np, action, task):
        if actor and action and task and isinstance(action, str):
            if isinstance(task, str):
                if task == "play":
                    self.base.sound.play_jump()
                    any_action_seq = actor.actor_interval(action,
                                                          playRate=self.base.game_instance["current_play_rate"])
                    Sequence(Func(self.fsm_state_wrapper, actor, "generic_states", "is_jumping", True),
                             Func(self._player_bullet_jump_helper, actor, actor_rb_np, action),
                             any_action_seq,
                             Func(self.fsm_state_wrapper, actor, "generic_states", "is_jumping", False)).start()

    def filterJump(self, request, args):
        if request not in ['Jump']:
            return (request,) + args
        else:
            return None

    def enterLay(self, actor, action, task):
        if actor and action and task and isinstance(action, str):
            if isinstance(task, str):
                if task == "play":
                    any_action_seq = actor.actor_interval(action,
                                                          playRate=self.base.game_instance["current_play_rate"])
                    Sequence(Func(self.fsm_state_wrapper, actor, "generic_states", "is_busy", True),
                             any_action_seq,
                             Func(self.fsm_state_wrapper, actor, "generic_states", "is_busy", False)).start()
