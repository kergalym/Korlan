from direct.interval.FunctionInterval import Func, Wait
from direct.interval.MetaInterval import Sequence, Parallel
from direct.task.TaskManagerGlobal import taskMgr
from panda3d.core import Vec3, Vec2, Point3, BitMask32

from Engine.AI.npc_behavior import NpcBehavior


class NpcController:

    def __init__(self, actor):
        self.base = base
        self.render = render
        self.player = self.base.game_instance["player_ref"]
        self.player_bs = self.base.game_instance["player_np"]
        self.player_fsm = self.base.game_instance["player_fsm_cls"]
        self.npcs_fsm_states = self.base.game_instance["npcs_fsm_states"]
        self.npc_rotations = {}
        self.activated_npc_count = 0
        self.current_seq = None
        self.current_step_action = None
        self.navmesh = self.base.game_instance["navmesh"]
        self.navmesh_query = self.base.game_instance["navmesh_query"]

        # Keep this class instance for further usage in NpcBehavior class only
        self.base.game_instance["npc_controller_cls"] = self

        self.npc_behavior = NpcBehavior()

        name = actor.get_name()

        actor.get_python_tag("generic_states")['is_idle'] = True
        actor.set_python_tag("arrow_count", 20)
        # actor.set_blend(frameBlend=True)
        actor_bs = self.base.game_instance["actors_np"]
        request = self.npcs_fsm_states[name]

        # R&D
        self.npc_action_seqs = {}

        self.npc_action_seqs[name] = Sequence()

        if "animal" not in actor.get_python_tag("npc_type"):
            self.npc_state = self.base.game_instance["npc_state_cls"]
            self.npc_state.set_npc_equipment(actor, "Korlan:Spine1")

            taskMgr.add(self.actor_hitbox_trace_task,
                        "{0}_hitboxes_task".format(name.lower()),
                        extraArgs=[actor, actor_bs, request], appendTask=True)

            # TODO KEEP HERE UNTILL HORSE ANIMS BECOME READY
        if actor:
            if "Horse" not in actor.get_name():
                # FIXME: Test the directives. Tempo set passive to True

                # Add a tracked obstacle which is NPC.
                """actor_name = "{0}:BS".format(actor_name)
                actor_npc_bs = self.base.game_instance["actors_np"][actor_name]
                self.navmesh.add_node_path(actor_npc_bs)
                self.navmesh.update()"""

                taskMgr.add(self.npc_behavior.npc_generic_logic,
                            "{0}_npc_generic_logic_task".format(name),
                            extraArgs=[actor, self.player_bs, request, False],
                            appendTask=True)

    def actor_hitbox_trace_task(self, actor, actor_bs, request, task):
        if self.base.game_instance['menu_mode']:
            return task.done

        if actor and actor_bs and actor.find("**/**Hips:HB") and request:
            parent_node = actor.find("**/**Hips:HB").node()
            parent_np = actor.find("**/**Hips:HB")

            for node in parent_node.get_overlapping_nodes():
                damage_weapons = actor.get_python_tag("damage_weapons")
                for weapon in damage_weapons:
                    # Exclude our own weapon hits
                    if (weapon in node.get_name()
                            and actor.get_name() not in node.get_name()):
                        hitbox_np = render.find("**/{0}".format(node.get_name()))
                        if hitbox_np:
                            actor.set_python_tag("enemy_hitbox_distance", 0)
                            # Deactivate enemy weapon if we got hit
                            if str(hitbox_np.get_collide_mask()) != " 0000 0000 0000 0000 0000 0000 0000 0000\n":
                                distance = round(hitbox_np.get_distance(parent_np), 1)
                                actor.set_python_tag("enemy_hitbox_distance", distance)

                                # Enemy Prediction for facing
                                if distance >= 0.5 and distance <= 2.5:
                                    if node:
                                        name = node.get_name()
                                        for ref, bs in zip(self.base.game_instance["actors_ref"],
                                                           self.base.game_instance["actors_np"]):
                                            if name in ref:
                                                npc_ref = self.base.game_instance["actors_np"][ref]
                                                npc_bs = self.base.game_instance["actors_np"][ref]
                                                if npc_ref:
                                                    if not actor.get_python_tag("enemy_npc_ref"):
                                                        actor.set_python_tag("enemy_npc_ref", npc_ref)
                                                    if not actor.get_python_tag("enemy_npc_bs"):
                                                        actor.set_python_tag("enemy_npc_bs", npc_bs)
                                                    self.face_actor_to(actor_bs, npc_bs)

                                if distance >= 0.5 and distance <= 1.8:
                                    hitbox_np.set_collide_mask(BitMask32.allOff())
                                    if (actor.get_python_tag("health_np")
                                            and not actor.get_python_tag("generic_states")['is_blocking']):
                                        # NPC gets damage if he has health point
                                        if actor.get_python_tag("health_np")['value'] > 1:
                                            request.request("Attacked", actor, "HitToBody", "play")
                                            actor.get_python_tag("health_np")['value'] -= 6

                                        if actor.get_python_tag("stamina_np")['value'] > 1:
                                            actor.get_python_tag("stamina_np")['value'] -= 3

                                        if actor.get_python_tag("courage_np")['value'] > 1:
                                            actor.get_python_tag("courage_np")['value'] -= 3

            # NPC dies if he has no health point
            if (actor.get_python_tag("health_np")['value'] < 2
                    or actor.get_python_tag("health_np")['value'] < 1):
                if actor.get_python_tag("stamina_np")['value'] > 1:
                    actor.get_python_tag("stamina_np")['value'] = 0

                if actor.get_python_tag("generic_states")['is_alive']:
                    if actor.get_python_tag("generic_states")['is_idle']:
                        request.request("Death", actor, "Dying", "play")

        return task.cont

    def _reset_current_sequence(self):
        if self.current_seq:
            self.current_seq = None

    def get_enemy(self, actor):
        if actor:
            my_cls = actor.get_python_tag("npc_class")
            for name, type, cls in zip(self.base.game_instance["level_assets_np"]["name"],
                                       self.base.game_instance["level_assets_np"]["type"],
                                       self.base.game_instance["level_assets_np"]["class"]):
                if my_cls != cls and "animal" not in type and "npc" in type:
                    enemy_npc_ref = self.base.game_instance['actors_ref'][name]
                    if enemy_npc_ref and enemy_npc_ref.get_python_tag("generic_states")['is_alive']:
                        name_bs = "{0}:BS".format(name)
                        enemy_npc_bs = self.base.game_instance['actors_np'][name_bs]
                        actor_bs_name = "{0}:BS".format(actor.get_name())
                        actor_bs = self.base.game_instance["actors_np"][actor_bs_name]
                        if int(actor_bs.get_distance(enemy_npc_bs)) < 50:
                            return [enemy_npc_ref, enemy_npc_bs]

    def is_ready_for_walking(self, actor):
        if actor.get_python_tag("human_states"):
            # Only Human NPC has human_states
            if (actor.get_python_tag("generic_states")['is_idle']
                    and not actor.get_python_tag("generic_states")['is_running']
                    and not actor.get_python_tag("generic_states")['is_crouch_moving']
                    and not actor.get_python_tag("generic_states")['is_crouching']
                    and not actor.get_python_tag("generic_states")['is_jumping']
                    and not actor.get_python_tag("generic_states")['is_attacked']
                    and not actor.get_python_tag("generic_states")['is_busy']
                    and not actor.get_python_tag("generic_states")['is_blocking']
                    and not actor.get_python_tag("generic_states")['is_using']
                    and not actor.get_python_tag("generic_states")['is_turning']
                    and not actor.get_python_tag("generic_states")['is_laying']
                    and not actor.get_python_tag("human_states")['horse_riding']
                    and not actor.get_python_tag("human_states")['is_on_horse']):
                return True
            else:
                return False
        elif not actor.get_python_tag("human_states"):
            # Animal NPC has no human_states
            if (actor.get_python_tag("generic_states")['is_idle']
                    and not actor.get_python_tag("generic_states")['is_running']
                    and not actor.get_python_tag("generic_states")['is_crouch_moving']
                    and not actor.get_python_tag("generic_states")['is_crouching']
                    and not actor.get_python_tag("generic_states")['is_jumping']
                    and not actor.get_python_tag("generic_states")['is_attacked']
                    and not actor.get_python_tag("generic_states")['is_busy']
                    and not actor.get_python_tag("generic_states")['is_using']
                    and not actor.get_python_tag("generic_states")['is_turning']
                    and not actor.get_python_tag("generic_states")['is_laying']):
                return True
            else:
                return False

    def npc_in_staying_logic(self, actor, request):
        if actor and request:
            actor.get_python_tag("generic_states")['is_moving'] = False
            actor.get_python_tag("generic_states")['is_idle'] = True

            if actor.get_python_tag("generic_states")['is_idle']:
                if actor.get_python_tag("generic_states")['is_crouch_moving']:
                    request.request("Idle", actor, "standing_to_crouch", "loop")
                elif not actor.get_python_tag("generic_states")['is_crouch_moving']:
                    request.request("Idle", actor, "Standing_idle_male", "loop")

                if actor.get_python_tag("stamina_np"):
                    if actor.get_python_tag("stamina_np")['value'] < 100:
                        actor.get_python_tag("stamina_np")['value'] += 0.5

    def npc_in_dying_logic(self, actor, request):
        if actor and request:
            actor.get_python_tag("generic_states")['is_moving'] = False
            actor.get_python_tag("generic_states")['is_alive'] = False

            if actor.get_python_tag("stamina_np"):
                if actor.get_python_tag("stamina_np")['value'] > 1:
                    actor.get_python_tag("stamina_np")['value'] -= 100

            if actor.get_python_tag("courage_np"):
                if actor.get_python_tag("courage_np")['value'] > 1:
                    actor.get_python_tag("courage_np")['value'] -= 100

            if not (actor.get_python_tag("generic_states")['is_alive']):
                if actor.get_python_tag("generic_states")['is_idle']:
                    request.request("Death", actor, "Dying", "play")
                    actor.get_python_tag("generic_states")['is_idle'] = False

    def do_walking_sequence_once(self, actor, actor_npc_bs, target, actor_name, request):
        if not self.npc_action_seqs[actor_name].is_playing():
            if (actor, actor_npc_bs and target
                       and actor_name
                       and isinstance(actor_name, str)
                       and request):

                self.navmesh_query.nearest_point(actor_npc_bs.get_pos())

                # Set last pos from opposite actor's world points
                last_pos = self.render.get_relative_vector(target.get_parent(),
                                                           target.get_pos())
                last_pos = Point3(last_pos[0], last_pos[1], 0)

                self.navmesh.update()

                # Find path
                path = self.navmesh_query.find_path(actor_npc_bs.get_pos(), last_pos)
                path_points = list(path.points)
                current_dir = actor_npc_bs.get_hpr()

                self.npc_action_seqs[actor_name] = Sequence()

                func_interval = Func(request.request, "Walk", actor, "Walking", "loop")
                self.npc_action_seqs[actor_name].append(func_interval)

                for i in range(len(path_points) - 1):
                    speed = 2

                    # Heading
                    new_hpr = Vec3(Vec2(0, -1).signed_angle_deg(path_points[i + 1].xy - path_points[i].xy),
                                   current_dir[1],
                                   current_dir[2])
                    hpr_interval = actor_npc_bs.hprInterval(0, new_hpr)

                    # Movement
                    dist = (path_points[i + 1] - path_points[i]).length()

                    # Workaround for shifted down actor's rigid body nodepath z pos,
                    # which in posInterval interpreted like -1, not 0
                    pp = Point3(path_points[i + 1][0], path_points[i + 1][1], 1)
                    pp_start = Point3(path_points[i][0], path_points[i][1], 1)
                    pos_interval = actor_npc_bs.posInterval(dist / speed, pp, pp_start)

                    # Append sequence tasks in that order
                    self.npc_action_seqs[actor_name].append(hpr_interval)
                    self.npc_action_seqs[actor_name].append(pos_interval)

                    current_dir = new_hpr

                func_interval = Func(self.npc_in_staying_logic, actor, request)
                self.npc_action_seqs[actor_name].append(func_interval)
                self.npc_action_seqs[actor_name].start()

    def npc_in_walking_logic(self, actor, actor_npc_bs, target, request):
        if actor and actor_npc_bs and target and request:
            if self.is_ready_for_walking(actor):
                actor_name = actor.get_name()

                # Crouch collision states
                if not actor.get_python_tag("generic_states")['is_crouch_moving']:
                    actor_name_bs = "{0}:BS".format(actor_name)
                    crouch_bs_mask = BitMask32.allOff()
                    capsule_bs_mask = self.base.game_instance["actors_np_mask"][actor_name_bs]

                    self.base.game_instance['actors_crouch_bs_np'][actor_name_bs].setCollideMask(crouch_bs_mask)
                    self.base.game_instance['actors_np'][actor_name_bs].setCollideMask(capsule_bs_mask)

                elif actor.get_python_tag("generic_states")['is_crouch_moving']:
                    actor_name_bs = "{0}:BS".format(actor_name)
                    crouch_bs_mask = self.base.game_instance['actors_crouch_bs_np_mask'][actor_name_bs]
                    capsule_bs_mask = BitMask32.allOff()

                    self.base.game_instance['actors_crouch_bs_np'][actor_name_bs].setCollideMask(crouch_bs_mask)
                    self.base.game_instance['actors_np'][actor_name_bs].setCollideMask(capsule_bs_mask)

                actor.get_python_tag("generic_states")['is_idle'] = False
                actor.get_python_tag("generic_states")['is_moving'] = True

                if actor.get_python_tag("stamina_np"):
                    if actor.get_python_tag("stamina_np")['value'] > 1:
                        actor.get_python_tag("stamina_np")['value'] -= 1

                self.do_walking_sequence_once(actor, actor_npc_bs, target, actor_name, request)

    def seq_pick_item_wrapper_task(self, actor, action, joint_name, task):
        if actor and action and joint_name:
            npc_state_cls = self.base.game_instance["npc_state_cls"]
            if actor.getCurrentFrame(action):
                if (actor.getCurrentFrame(action) > 67
                        and actor.getCurrentFrame(action) < 72):
                    npc_state_cls.pick_up_item(actor, joint_name)
        return task.cont

    def seq_drop_item_wrapper_task(self, actor, action, task):
        if actor and action:
            npc_state_cls = self.base.game_instance["npc_state_cls"]
            if actor.getCurrentFrame(action):
                if (actor.getCurrentFrame(action) > 67
                        and actor.getCurrentFrame(action) < 72):
                    npc_state_cls.drop_item(actor)
        return task.cont

    def remove_seq_pick_item_wrapper_task(self):
        taskMgr.remove("seq_pick_item_wrapper_task")

    def remove_seq_drop_item_wrapper_task(self):
        taskMgr.remove("seq_drop_item_wrapper_task")

    def npc_in_gathering_logic(self, actor, action, request, parent, item):
        if actor and action and request and parent and item and isinstance(item, str):
            if not actor.get_python_tag("used_item_np"):
                item_np = parent.find("**/{0}".format(item))
                if item_np:
                    actor.set_python_tag("used_item_np", item_np)

                    # Usable Items List
                    _items = []
                    _pos = []
                    _hpr = []

                    for child in parent.get_children():
                        _items.append(child.get_name())
                        _pos.append(child.get_pos())
                        _hpr.append(child.get_hpr())

                    usable_item_list = {
                        "name": _items,
                        "pos": _pos,
                        "hpr": _hpr
                    }

                    actor.set_python_tag("usable_item_list", usable_item_list)

                if not actor.get_python_tag("is_item_using"):
                    # just take item
                    taskMgr.add(self.seq_pick_item_wrapper_task,
                                "seq_pick_item_wrapper_task",
                                extraArgs=[actor, action, "Korlan:RightHand"],
                                appendTask=True)

                    any_action_seq = actor.actor_interval(action,
                                                          playRate=self.base.actor_play_rate)
                    Sequence(any_action_seq,
                             Func(self.remove_seq_pick_item_wrapper_task),
                             ).start()

    def npc_in_dropping_logic(self, actor, action, request):
        if actor and action and request:
            if actor.get_python_tag("used_item_np"):
                if actor.get_python_tag("is_item_using"):
                    # Just drop item
                    taskMgr.add(self.seq_drop_item_wrapper_task,
                                "seq_drop_item_wrapper_task",
                                extraArgs=[actor, action],
                                appendTask=True)
                    any_action_seq = actor.actor_interval(action,
                                                          playRate=self.base.actor_play_rate)
                    Sequence(any_action_seq,
                             Func(self.remove_seq_drop_item_wrapper_task),
                             ).start()

    def npc_in_blocking_logic(self, actor, request):
        if (actor.get_python_tag("generic_states")['is_idle']
                and not actor.get_python_tag("generic_states")['is_attacked']
                and not actor.get_python_tag("generic_states")['is_busy']
                and not actor.get_python_tag("generic_states")['is_moving']):
            action = ""
            if actor.get_python_tag("human_states")['has_sword']:
                action = "great_sword_blocking"
            else:
                action = "center_blocking"
            request.request("Block", actor, action, "play")

    def _npc_in_attacking_logic(self, actor, actor_npc_bs, request):
        dt = globalClock.getDt()
        if (actor.get_python_tag("generic_states")['is_idle']
                and not actor.get_python_tag("generic_states")['is_busy']
                and not actor.get_python_tag("generic_states")['is_moving']):

            if actor.get_python_tag("human_states")["has_sword"]:
                action = "great_sword_slash"
                request.request("Attack", actor, action, "play")
            elif actor.get_python_tag("human_states")["has_bow"]:
                action = "archer_standing_draw_arrow"
                request.request("Archery", actor, action, "play")
            elif (not actor.get_python_tag("human_states")["has_sword"]
                  and not actor.get_python_tag("human_states")["has_bow"]):
                action = "Boxing"
                request.request("Attack", actor, action, "play")

            if (actor.get_python_tag("stamina_np")['value'] > 3
                    and actor.get_python_tag("enemy_distance") >= 1):
                if actor_npc_bs.get_y() != actor_npc_bs.get_y() - 2:
                    actor_npc_bs.set_y(actor_npc_bs, -2 * dt)

            if actor.get_python_tag("stamina_np")['value'] > 1:
                actor.get_python_tag("stamina_np")['value'] -= 18

    def npc_in_forwardroll_logic(self, actor, actor_npc_bs, request):
        dt = globalClock.getDt()
        if actor.get_python_tag("stamina_np"):
            if actor.get_python_tag("stamina_np")['value'] > 15:
                if actor_npc_bs.get_y() != actor_npc_bs.get_y() - 2:
                    actor_npc_bs.set_y(actor_npc_bs, -2 * dt)
                    request.request("ForwardRoll", actor, "forward_roll", "play")

                if actor.get_python_tag("stamina_np")['value'] > 1:
                    actor.get_python_tag("stamina_np")['value'] -= 15

    def npc_in_backwardroll_logic(self, actor, actor_npc_bs, request):
        dt = globalClock.getDt()
        if actor.get_python_tag("stamina_np"):
            if actor.get_python_tag("stamina_np")['value'] > 15:
                if actor_npc_bs.get_y() != actor_npc_bs.get_y() + 2:
                    actor_npc_bs.set_y(actor_npc_bs, 2 * dt)
                    request.request("BackwardRoll", actor, "forward_roll", "play")

                if actor.get_python_tag("stamina_np")['value'] > 1:
                    actor.get_python_tag("stamina_np")['value'] -= 15

    def npc_in_forwardstep_logic(self, actor, actor_npc_bs, request):
        dt = globalClock.getDt()
        if actor.get_python_tag("stamina_np"):
            if (actor.get_python_tag("stamina_np")['value'] > 3
                    and actor.get_python_tag("enemy_distance") >= 2):
                if actor_npc_bs.get_y() != actor_npc_bs.get_y() - 2:
                    actor_npc_bs.set_y(actor_npc_bs, -2 * dt)
                    request.request("ForwardStep", actor, "Walking", "play")

                if actor.get_python_tag("stamina_np")['value'] > 1:
                    actor.get_python_tag("stamina_np")['value'] -= 3

    def npc_in_backwardstep_logic(self, actor, actor_npc_bs, request):
        dt = globalClock.getDt()
        if actor.get_python_tag("stamina_np"):
            if (actor.get_python_tag("stamina_np")['value'] > 3
                    and actor.get_python_tag("enemy_distance") <= 1):
                if actor_npc_bs.get_y() != actor_npc_bs.get_y() + 2:
                    actor_npc_bs.set_y(actor_npc_bs, 2 * dt)
                    request.request("BackwardStep", actor, "Walking", "play")

                if actor.get_python_tag("stamina_np")['value'] > 1:
                    actor.get_python_tag("stamina_np")['value'] -= 3

    def npc_in_crouching_logic(self, actor, request):
        if (actor.get_python_tag("generic_states")['is_idle']
                and not actor.get_python_tag("generic_states")['is_attacked']
                and not actor.get_python_tag("generic_states")['is_busy']
                and not actor.get_python_tag("generic_states")['is_moving']):
            if (actor.get_python_tag("generic_states")
                    and not actor.get_python_tag("generic_states")['is_crouch_moving']):
                request.request("Crouch", actor)

    def npc_in_jumping_logic(self, actor, request):
        if (actor.get_python_tag("generic_states")['is_idle']
                and not actor.get_python_tag("generic_states")['is_attacked']
                and not actor.get_python_tag("generic_states")['is_busy']
                and not actor.get_python_tag("generic_states")['is_moving']):
            if (actor.get_python_tag("generic_states")
                    and not actor.get_python_tag("generic_states")['is_crouch_moving']):
                request.request("Jump", actor, "Jumping", "play")

            if actor.get_python_tag("stamina_np"):
                if actor.get_python_tag("stamina_np")['value'] > 1:
                    actor.get_python_tag("stamina_np")['value'] -= 1

            if actor.get_python_tag("courage_np"):
                if actor.get_python_tag("courage_np")['value'] > 1:
                    actor.get_python_tag("courage_np")['value'] -= 1

    def npc_in_mounting_logic(self, actor, actor_npc_bs, request):
        if (actor.get_python_tag("human_states")
                and not actor.get_python_tag("human_states")['is_on_horse']):
            horse = render.find("**/NPC_Horse")
            if horse:
                if not horse.get_python_tag("horse_spec_states")["is_mounted"]:
                    horse_bs = render.find("**/NPC_Horse:BS")
                    mountplace = horse.get_python_tag("mount_place")
                    if mountplace:
                        horse_dist = int(actor_npc_bs.get_distance(mountplace))
                        if horse_dist > 1:
                            self.npc_in_walking_logic(actor, actor_npc_bs, mountplace, request)
                        elif horse_dist <= 1:
                            self.npc_in_staying_logic(actor, request)
                            if (actor.get_python_tag("generic_states")['is_idle']
                                    and not actor.get_python_tag("generic_states")['is_attacked']
                                    and not actor.get_python_tag("generic_states")['is_busy']
                                    and not actor.get_python_tag("generic_states")['is_moving']):
                                horse_name = horse.get_name()
                                request.request("HorseMount", actor, actor_npc_bs, horse_name)

    def npc_in_unmounting_logic(self, actor, actor_npc_bs, request):
        if (actor.get_python_tag("human_states")
                and actor.get_python_tag("human_states")['is_on_horse']):
            if (actor.get_python_tag("generic_states")['is_idle']
                    and not actor.get_python_tag("generic_states")['is_attacked']
                    and not actor.get_python_tag("generic_states")['is_busy']
                    and not actor.get_python_tag("generic_states")['is_moving']):
                request.request("HorseUnmount", actor, actor_npc_bs)

    def npc_get_weapon(self, actor, request, weapon_name, bone_name):
        if (actor.get_python_tag("generic_states")['is_idle']
                and not actor.get_python_tag("generic_states")['is_attacked']
                and not actor.get_python_tag("generic_states")['is_busy']
                and not actor.get_python_tag("generic_states")['is_moving']):
            if "sword" in weapon_name:
                if (actor.get_python_tag("human_states")
                        and not actor.get_python_tag("human_states")['has_sword']):
                    request.request("GetWeapon", actor, "sword_disarm_over_shoulder",
                                    weapon_name, bone_name, "play")
            elif "bow" in weapon_name:
                if (actor.get_python_tag("human_states")
                        and not actor.get_python_tag("human_states")['has_bow']):
                    request.request("GetWeapon", actor, "archer_standing_disarm_bow",
                                    weapon_name, bone_name, "play")

    def npc_remove_weapon(self, actor, request, weapon_name, bone_name):
        if (actor.get_python_tag("generic_states")['is_idle']
                and not actor.get_python_tag("generic_states")['is_attacked']
                and not actor.get_python_tag("generic_states")['is_busy']
                and not actor.get_python_tag("generic_states")['is_moving']):
            if "sword" in weapon_name:
                if (actor.get_python_tag("human_states")
                        and actor.get_python_tag("human_states")['has_sword']):
                    request.request("RemoveWeapon", actor, "sword_disarm_over_shoulder",
                                    weapon_name, bone_name, "play")
            elif "bow" in weapon_name:
                if (actor.get_python_tag("human_states")
                        and actor.get_python_tag("human_states")['has_bow']):
                    request.request("RemoveWeapon", actor, "archer_standing_disarm_bow",
                                    weapon_name, bone_name, "play")

    def face_actor_to(self, actor, target_np):
        if actor and target_np:
            # Calculate NPC rotation vector
            rot_vector = Vec3(actor.get_pos() - target_np.get_pos())
            rot_vector_2d = rot_vector.get_xy()
            rot_vector_2d.normalize()
            new_hpr = Vec3(Vec2(0, -1).signed_angle_deg(rot_vector_2d), 0)
            target_heading = target_np.get_h()
            heading = actor.get_h()

            # If NPC faced to target actor and target actor is faced to NPC,
            # then continue heading
            # If NPC is not faced to target actor and target actor is not faced to NPC,
            # then do reversed heading
            if int(heading) < 0 and int(target_heading) > 0:
                actor.set_h(-new_hpr[0])
            # If NPC is not faced to target actor and target actor is faced to NPC,
            # then do reversed heading 3
            elif int(heading) > 0 and int(target_heading) < 0:
                actor.set_h(-new_hpr[0])

    def do_defensive_prediction(self, actor, actor_npc_bs, request, hitbox_dist):
        if actor and actor_npc_bs and request:
            if hitbox_dist >= 0.5 and hitbox_dist <= 1.8:
                if actor.get_python_tag("stamina_np")['value'] > 5:
                    if not self.current_seq:
                        self.current_seq = Sequence(
                            Parallel(
                                Wait(1),
                                Func(self.npc_in_backwardstep_logic, actor,
                                     actor_npc_bs, request)),
                            Parallel(
                                Wait(1),
                                Func(self.npc_in_forwardstep_logic, actor,
                                     actor_npc_bs, request)),
                            Parallel(
                                Wait(1),
                                Func(self.npc_in_backwardroll_logic, actor,
                                     actor_npc_bs, request)),
                            Parallel(
                                Wait(1),
                                Func(self.npc_in_blocking_logic, actor, request)),
                            Func(self._reset_current_sequence)
                        )
                        self.current_seq.sort()
                    if self.current_seq and not self.current_seq.is_playing():
                        self.current_seq.start()

            if actor.get_python_tag("stamina_np")['value'] > 50:
                if actor.get_python_tag("enemy_distance") <= 1:
                    target_np = actor.get_python_tag("target_np")
                    self.face_actor_to(actor_npc_bs, target_np)
                    self._npc_in_attacking_logic(actor, actor_npc_bs, request)
                elif (actor.get_python_tag("enemy_distance") > 1
                      and actor.get_python_tag("enemy_distance") < 3):
                    self.npc_in_forwardstep_logic(actor, actor_npc_bs, request)
