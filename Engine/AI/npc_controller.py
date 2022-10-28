from direct.interval.FunctionInterval import Func, Wait
from direct.interval.MetaInterval import Sequence, Parallel
from direct.task.TaskManagerGlobal import taskMgr
from panda3d.core import Vec3, Vec2, Point3, BitMask32, NodePath

from Engine.Physics.npc_damages import NpcDamages
from Engine.AI.npc_behavior import NpcBehavior
from Engine.Actors.animator import Animator

from Engine.AI import ai_declaratives

""" ANIMATIONS"""
from Engine import anim_names


class NpcController:

    def __init__(self, actor):
        self.base = base  # pylint: disable=undefined-variable
        self.render = render  # pylint: disable=undefined-variable
        self.player = self.base.game_instance["player_ref"]
        self.player_rb_np = self.base.game_instance["player_np"]
        self.player_fsm = self.base.game_instance["player_fsm_cls"]
        self.npcs_fsm_states = self.base.game_instance["npcs_fsm_states"]
        self.npc_hips = {}
        self.npc_rotations = {}
        self.activated_npc_count = 0
        self.current_seq = None
        self.current_step_action = None
        self.navmesh = self.base.game_instance["navmesh"]
        self.navmesh_query = self.base.game_instance["navmesh_query"]

        # Keep this class instance for further usage in NpcBehavior class only
        self.base.game_instance["npc_controller_cls"] = self

        self.npc_physics = NpcDamages()
        self.npc_behavior = NpcBehavior()

        name = actor.get_name()
        name_bs = "{0}:BS".format(name)
        actor.get_python_tag("generic_states")['is_idle'] = True
        actor.set_python_tag("arrow_count", 20)
        # actor.set_blend(frameBlend=True)
        actor_rb_np = self.base.game_instance["actors_np"].get(name_bs)
        request = self.npcs_fsm_states.get(name)
        self.npc_hips[name] = actor.find("**/**Hips:HB")
        hips = self.npc_hips.get(name)

        # R&D
        self.walking_sequence = {}
        self.mounting_sequence = {}
        self.unmounting_sequence = {}

        self.walking_sequence[name] = Sequence()
        self.mounting_sequence[name] = Sequence()
        self.unmounting_sequence[name] = Sequence()

        if actor and actor_rb_np and request and "animal" not in actor.get_python_tag("npc_type"):
            self.npc_state = self.base.game_instance["npc_state_cls"]
            self.npc_state.set_npc_equipment(actor, "Korlan:Spine1")

            taskMgr.add(self.npc_physics.actor_hitbox_trace_task,
                        "{0}_hitbox_trace_task".format(name.lower()),
                        extraArgs=[actor, actor_rb_np, hips, request],
                        appendTask=True)

        if actor:
            # Add a tracked obstacle which is NPC.
            for actor_name in self.base.game_instance["actors_np"]:
                if actor.get_name() not in actor_name:
                    actor_npc_bs = self.base.game_instance["actors_np"][actor_name]
                    self.navmesh.add_node_path(actor_npc_bs)
            # self.navmesh.update()

            # TODO KEEP HERE UNTILL HORSE ANIMS BECOME READY
            if "Horse" not in actor.get_name():
                taskMgr.add(self.npc_behavior.npc_generic_logic,
                            "{0}_npc_generic_logic_task".format(name),
                            extraArgs=[actor, self.player_rb_np, request, False],
                            appendTask=True)

            """ Animator class handles Idle/Walk/Run/Jump states based on actor's velocity"""
            Animator(actor, actor_rb_np, request)

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
                        enemy_rb_np = self.base.game_instance['actors_np'][name_bs]
                        actor_bs_name = "{0}:BS".format(actor.get_name())
                        actor_rb_np = self.base.game_instance["actors_np"][actor_bs_name]
                        if int(actor_rb_np.get_distance(enemy_rb_np)) < 50:
                            return [enemy_npc_ref, enemy_rb_np]

    def get_enemy_distance(self, actor, actor_npc_rb, opponent):
        if actor.get_python_tag("human_states")['is_on_horse']:
            if "Horse" in opponent.get_parent().get_name():
                rider_opponent = opponent.get_parent().get_parent()
                return int(actor_npc_rb.get_distance(rider_opponent))
        else:
            return int(actor_npc_rb.get_distance(opponent))

    def get_target_npc_in_state(self, target_np):
        if "Horse" in target_np.get_parent().get_name():
            return target_np.get_parent().get_parent()
        else:
            return target_np

    def face_actor_to(self, actor_rb_np, target_np):
        if actor_rb_np and target_np:
            if actor_rb_np.get_child(0).get_python_tag("human_states")['is_on_horse']:
                parent_rb_np = actor_rb_np.get_child(0).get_python_tag("mounted_horse")
                # Calculate NPC rotation vector
                new_target_np = self.get_target_npc_in_state(target_np)
                rot_vector = Vec3(parent_rb_np.get_pos() - new_target_np.get_pos())
                rot_vector_2d = rot_vector.get_xy()
                rot_vector_2d.normalize()
                heading = Vec3(Vec2(0, 1).signed_angle_deg(rot_vector_2d), 0).x
                parent_rb_np.set_h(heading)
            else:
                if not actor_rb_np.get_child(0).get_python_tag("human_states")["has_bow"]:
                    if int(actor_rb_np.get_distance(target_np)) < 1:
                        # Calculate NPC rotation vector
                        new_target_np = self.get_target_npc_in_state(target_np)
                        rot_vector = Vec3(actor_rb_np.get_pos() - new_target_np.get_pos())
                        rot_vector_2d = rot_vector.get_xy()
                        rot_vector_2d.normalize()
                        heading = Vec3(Vec2(0, 1).signed_angle_deg(rot_vector_2d), 0).x
                        actor_rb_np.set_h(heading)
                    else:
                        # Calculate NPC rotation vector
                        new_target_np = self.get_target_npc_in_state(target_np)
                        rot_vector = Vec3(actor_rb_np.get_pos() - new_target_np.get_pos())
                        rot_vector_2d = rot_vector.get_xy()
                        rot_vector_2d.normalize()
                        heading = Vec3(Vec2(0, 1).signed_angle_deg(rot_vector_2d), 0).x
                        actor_rb_np.set_h(heading)

                elif actor_rb_np.get_child(0).get_python_tag("human_states")["has_bow"]:
                    # Calculate NPC rotation vector
                    new_target_np = self.get_target_npc_in_state(target_np)
                    rot_vector = Vec3(actor_rb_np.get_pos() - new_target_np.get_pos())
                    rot_vector_2d = rot_vector.get_xy()
                    rot_vector_2d.normalize()
                    heading = Vec3(Vec2(0, 1).signed_angle_deg(rot_vector_2d), 0).x
                    actor_rb_np.set_h(heading)

    def is_ready_for_walking(self, actor):
        if actor.get_python_tag("human_states"):
            if not actor.get_python_tag("human_states")['is_on_horse']:
                # Only Human or NPC has human_states
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
                        and not actor.get_python_tag("generic_states")['is_laying']):
                    return True
                else:
                    return False
            elif actor.get_python_tag("human_states")['is_on_horse']:
                parent_rb_np = actor.get_python_tag("mounted_horse")
                parent = parent_rb_np.get_child(0)
                # Only Human or NPC has human_states which is on horse
                if (parent.get_python_tag("generic_states")['is_idle']
                        and not parent.get_python_tag("generic_states")['is_running']
                        and not parent.get_python_tag("generic_states")['is_crouch_moving']
                        and not parent.get_python_tag("generic_states")['is_crouching']
                        and not parent.get_python_tag("generic_states")['is_jumping']
                        and not parent.get_python_tag("generic_states")['is_attacked']
                        and not parent.get_python_tag("generic_states")['is_busy']
                        and not parent.get_python_tag("generic_states")['is_blocking']
                        and not parent.get_python_tag("generic_states")['is_using']
                        and not parent.get_python_tag("generic_states")['is_turning']
                        and not parent.get_python_tag("generic_states")['is_laying']):
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

    def npc_in_idle_logic(self, actor, request):
        if actor and request:
            if actor.get_python_tag("npc_type") == "npc":
                if not actor.get_python_tag("human_states")['is_on_horse']:
                    actor.get_python_tag("generic_states")['is_moving'] = False
                    actor.get_python_tag("generic_states")['is_idle'] = True

                elif actor.get_python_tag("human_states")['is_on_horse']:
                    parent_rb_np = actor.get_python_tag("mounted_horse")
                    parent_name = parent_rb_np.get_child(0).get_name()
                    parent = self.base.game_instance["actors_ref"][parent_name]

                    parent.get_python_tag("generic_states")['is_moving'] = False
                    parent.get_python_tag("generic_states")['is_idle'] = True

            elif actor.get_python_tag("npc_type") == "npc_animal":
                actor.get_python_tag("generic_states")['is_moving'] = False
                actor.get_python_tag("generic_states")['is_idle'] = True

    def npc_in_dying_logic(self, actor, request):
        if actor and request:
            if actor.get_python_tag("npc_type") == "npc":
                if not actor.get_python_tag("human_states")['is_on_horse']:
                    anim_action = anim_names.a_anim_dying
                    if not (actor.get_python_tag("generic_states")['is_alive']):
                        if actor.get_python_tag("generic_states")['is_idle']:
                            request.request("Death", actor, anim_action, "play")
                            actor.get_python_tag("generic_states")['is_idle'] = False
                else:
                    anim_action = anim_names.a_anim_horse_dying
                    npc = actor.get_python_tag("mounted_horse")
                    npc_ref = self.base.game_instance["actors_ref"][npc.get_name()]
                    if not (actor.get_python_tag("generic_states")['is_alive']):
                        if actor.get_python_tag("generic_states")['is_idle']:
                            request.request("Death", npc_ref, anim_action, "play")
                            actor.get_python_tag("generic_states")['is_idle'] = False

            elif actor.get_python_tag("npc_type") == "npc_animal":
                anim_action = anim_names.a_anim_horse_dying
                if not (actor.get_python_tag("generic_states")['is_alive']):
                    if actor.get_python_tag("generic_states")['is_idle']:
                        request.request("Death", actor, anim_action, "play")
                        actor.get_python_tag("generic_states")['is_idle'] = False

            actor.get_python_tag("generic_states")['is_moving'] = False
            actor.get_python_tag("generic_states")['is_alive'] = False

            if actor.get_python_tag("stamina_np"):
                if actor.get_python_tag("stamina_np")['value'] > 1:
                    actor.get_python_tag("stamina_np")['value'] -= 100

            if actor.get_python_tag("courage_np"):
                if actor.get_python_tag("courage_np")['value'] > 1:
                    actor.get_python_tag("courage_np")['value'] -= 100

    def _get_target_last_pos(self, target, actor_name):
        # Make target nodepath with defined margins for NPC actors
        if "NPC" in target.get_name():
            if target.get_child(0).has_python_tag("human_states"):
                if target.get_child(0).get_python_tag("human_states")["is_on_horse"]:
                    pos = target.get_parent().get_parent().get_pos() + Vec3(ai_declaratives.distance_to_animal,
                                                                            ai_declaratives.distance_to_animal,
                                                                            0)
                else:
                    pos = target.get_pos() + Point3(ai_declaratives.distance_to_target,
                                                    ai_declaratives.distance_to_target,
                                                    0)
            else:
                pos = target.get_pos() + Point3(ai_declaratives.distance_to_target,
                                                ai_declaratives.distance_to_target,
                                                0)

            name = "{0}_margins".format(target.get_name())
            m_target = NodePath(name)
            m_target.set_pos(pos)
            # Set last pos from opposite actor's world points
            last_pos = self.render.get_relative_vector(m_target.get_parent(),
                                                       m_target.get_pos())
        elif "Player" in target.get_name():
            if base.player_states["is_mounted"]:
                pos = target.get_parent().get_parent().get_pos() + Point3(ai_declaratives.distance_to_animal,
                                                                          ai_declaratives.distance_to_animal,
                                                                          0)
                name = "{0}_margins".format(target.get_parent().get_parent().get_name())
                m_target = NodePath(name)
                m_target.set_pos(pos)
            else:
                pos = target.get_pos() + Point3(ai_declaratives.distance_to_target,
                                                ai_declaratives.distance_to_target,
                                                0)
                name = "{0}_margins".format(target.get_name())
                m_target = NodePath(name)
                m_target.set_pos(pos)

            # Set last pos from opposite actor's world points
            last_pos = self.render.get_relative_vector(m_target.get_parent(),
                                                       m_target.get_pos())
        else:
            # Set last pos from opposite actor's world points
            last_pos = self.render.get_relative_vector(target.get_parent(),
                                                       target.get_pos())
        return Point3(last_pos[0], last_pos[1], 0)

    def do_walking_sequence_once(self, actor, actor_rb_np, target, actor_name, request):
        if not self.walking_sequence[actor_name].is_playing():
            if (actor, actor_rb_np and target
                       and actor_name
                       and isinstance(actor_name, str)
                       and request):

                self.navmesh_query.nearest_point(actor_rb_np.get_pos())

                # get target's last pos
                last_pos = self._get_target_last_pos(target, actor_name)

                # self.navmesh.update()

                # Find path
                path = self.navmesh_query.find_path(actor_rb_np.get_pos(), last_pos)
                path_points = list(path.points)
                current_dir = actor_rb_np.get_hpr()

                self.walking_sequence[actor_name] = Sequence()

                # Change animation and speed
                speed = 2
                if actor.get_python_tag("move_type") == "walk":
                    speed = 2
                elif actor.get_python_tag("move_type") == "run":
                    speed = 5

                for i in range(len(path_points) - 1):
                    # Heading
                    new_hpr = Vec3(Vec2(0, -1).signed_angle_deg(path_points[i + 1].xy - path_points[i].xy),
                                   current_dir[1],
                                   current_dir[2])
                    hpr_interval = actor_rb_np.hprInterval(0, new_hpr)

                    # Movement
                    dist = (path_points[i + 1] - path_points[i]).length()

                    # Workaround for shifted down actor's rigid body nodepath z pos,
                    # which in posInterval interpreted like -1, not 0
                    pp = Point3(path_points[i + 1][0], path_points[i + 1][1], actor_rb_np.get_z())
                    pp_start = Point3(path_points[i][0], path_points[i][1], actor_rb_np.get_z())
                    pos_interval = actor_rb_np.posInterval(dist / speed, pp, pp_start)

                    # Append sequence tasks in that order
                    self.walking_sequence[actor_name].append(hpr_interval)
                    self.walking_sequence[actor_name].append(pos_interval)

                    current_dir = new_hpr

                idle_interval = Func(self.npc_in_idle_logic, actor, request)
                self.walking_sequence[actor_name].append(idle_interval)
                self.walking_sequence[actor_name].start()

    def _do_dynamic_obstacle_avoidance(self, actor_rb_np, target_rb_np, delta_time, acceleration=2.0):
        for name in self.base.game_instance["actors_np"]:
            if name not in actor_rb_np.get_name():
                obstacle_rb_np = self.base.game_instance["actors_np"][name]
                distance = obstacle_rb_np.get_distance(actor_rb_np)
                max_avoid_force = acceleration
                obstacle_radius = 0.7
                obstacle_center = obstacle_rb_np.get_pos()
                velocity = Vec3(0, 0, 0)
                velocity += actor_rb_np.get_pos() - obstacle_center * acceleration * delta_time

                # Calculate avoidance force
                avoidance_force = actor_rb_np.get_pos() - obstacle_center
                avoidance_force = avoidance_force.normalize() * max_avoid_force

                if distance < obstacle_radius:
                    # Actor got collision with obstacle on it's way,
                    # We turn away from obstacle
                    heading = obstacle_rb_np.get_h() + actor_rb_np.get_h()

                    if actor_rb_np.get_h() < heading:
                        actor_rb_np.set_h(actor_rb_np.get_h() + 200 * delta_time)

                    # Now we decide where we should look to get closer path to the target
                    rot_vector = Vec3(actor_rb_np.get_pos() - target_rb_np.get_pos())
                    rot_vector_2d = rot_vector.get_xy()
                    rot_vector_2d.normalize()
                    heading = Vec3(Vec2(0, 1).signed_angle_deg(rot_vector_2d), 0).x
                    actor_rb_np.set_h(heading)

                    # Do push for our actor
                    actor_rb_np.set_pos(avoidance_force, avoidance_force, actor_rb_np.get_z())
                    actor_rb_np.set_y(actor_rb_np, -acceleration * delta_time)

                else:
                    actor_rb_np.set_y(actor_rb_np, -acceleration * delta_time)

    def do_any_walking(self, actor, actor_rb_np, target, request):
        if actor and actor_rb_np and target and request:
            delta_time = globalClock.getDt()

            # Change speed
            speed = 2
            # Do actual movement
            actor.get_python_tag("generic_states")['is_idle'] = False
            actor.get_python_tag("generic_states")['is_moving'] = True
            self._do_dynamic_obstacle_avoidance(actor_rb_np, target, delta_time, speed)
            # actor_rb_np.set_y(actor_rb_np, -speed * delta_time)

    def npc_in_walking_rd_logic(self, actor, actor_rb_np, target, request):
        if actor and actor_rb_np and target and request:
            actor_name = actor.get_name()
            if not actor.get_python_tag("human_states")['is_on_horse']:
                if self.is_ready_for_walking(actor):

                    self._toggle_crouch_collision(actor, actor_rb_np)

                    actor.get_python_tag("generic_states")['is_idle'] = False
                    actor.get_python_tag("generic_states")['is_moving'] = True

                    self.do_walking_sequence_once(actor, actor_rb_np, target, actor_name, request)
            else:
                if actor.get_python_tag("human_states")['is_on_horse']:
                    parent_rb_np = actor.get_python_tag("mounted_horse")
                    parent = parent_rb_np.get_child(0)

                    if self.is_ready_for_walking(actor):
                        actor_name = actor.get_name()

                        parent.get_python_tag("generic_states")['is_idle'] = False
                        parent.get_python_tag("generic_states")['is_moving'] = True

                        self.do_walking_sequence_once(parent, parent_rb_np, target, actor_name, request)

    def _toggle_crouch_collision(self, actor, actor_npc_bs):
        actor_name = actor.get_name()
        if not actor.get_python_tag("generic_states")['is_crouch_moving']:
            actor_name_bs = "{0}:BS".format(actor_name)
            crouch_bs_mask = BitMask32.allOff()
            capsule_bs_mask = self.base.game_instance["actors_np_mask"].get(actor_name_bs)
            crouch_rb_np = self.base.game_instance['actors_crouch_bs_np'].get(actor_name_bs)
            if crouch_bs_mask is not None and crouch_rb_np is not None:
                crouch_rb_np.set_collide_mask(crouch_bs_mask)
                actor_npc_bs.set_collide_mask(capsule_bs_mask)

        elif actor.get_python_tag("generic_states")['is_crouch_moving']:
            actor_name_bs = "{0}:BS".format(actor_name)
            crouch_bs_mask = self.base.game_instance['actors_crouch_bs_np_mask'].get(actor_name_bs)
            crouch_rb_np = self.base.game_instance['actors_crouch_bs_np'][actor_name_bs]
            if crouch_bs_mask is not None and crouch_rb_np is not None:
                capsule_bs_mask = BitMask32.allOff()
                crouch_rb_np.set_collide_mask(crouch_bs_mask)
                actor_npc_bs.set_collide_mask(capsule_bs_mask)

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
            # Change animation
            action = ""
            if actor.get_python_tag("human_states")['has_sword']:
                action = anim_names.a_anim_parring
            else:
                action = anim_names.a_anim_blocking
            request.request("Block", actor, action, "play")

    def _npc_in_attacking_logic(self, actor, actor_npc_bs, request):
        dt = globalClock.getDt()
        if (actor.get_python_tag("generic_states")['is_idle']
                and not actor.get_python_tag("generic_states")['is_busy']
                and not actor.get_python_tag("generic_states")['is_moving']):

            # Change animation
            if actor.get_python_tag("human_states")["has_sword"]:
                action = anim_names.a_anim_melee_attack
                request.request("Attack", actor, action, "play")
            elif actor.get_python_tag("human_states")["has_bow"]:
                action = anim_names.a_anim_archery
                request.request("Archery", actor, action, "play")
            elif (not actor.get_python_tag("human_states")["has_sword"]
                  and not actor.get_python_tag("human_states")["has_bow"]):
                action = anim_names.a_anim_attack
                request.request("Attack", actor, action, "play")

            # Slightly move for closer attack
            if not actor.get_python_tag("human_states")["has_bow"]:
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
                    request.request("ForwardRoll", actor,
                                    anim_names.a_anim_rolling, "play")

                if actor.get_python_tag("stamina_np")['value'] > 1:
                    actor.get_python_tag("stamina_np")['value'] -= 15

    def npc_in_backwardroll_logic(self, actor, actor_npc_bs, request):
        dt = globalClock.getDt()
        if actor.get_python_tag("stamina_np"):
            if actor.get_python_tag("stamina_np")['value'] > 15:
                if actor_npc_bs.get_y() != actor_npc_bs.get_y() + 2:
                    actor_npc_bs.set_y(actor_npc_bs, 2 * dt)
                    request.request("BackwardRoll", actor,
                                    anim_names.a_anim_rolling, "play")

                if actor.get_python_tag("stamina_np")['value'] > 1:
                    actor.get_python_tag("stamina_np")['value'] -= 15

    def npc_in_forwardstep_logic(self, actor, actor_npc_bs, request):
        dt = globalClock.getDt()
        if actor.get_python_tag("stamina_np"):
            if (actor.get_python_tag("stamina_np")['value'] > 3
                    and actor.get_python_tag("enemy_distance") >= 2):
                if actor_npc_bs.get_y() != actor_npc_bs.get_y() - 2:
                    actor_npc_bs.set_y(actor_npc_bs, -2 * dt)
                    request.request("ForwardStep", actor,
                                    anim_names.a_anim_walking, "play")

                if actor.get_python_tag("stamina_np")['value'] > 1:
                    actor.get_python_tag("stamina_np")['value'] -= 3

    def npc_in_backwardstep_logic(self, actor, actor_npc_bs, request):
        dt = globalClock.getDt()
        if actor.get_python_tag("stamina_np"):
            if (actor.get_python_tag("stamina_np")['value'] > 3
                    and actor.get_python_tag("enemy_distance") <= 1):
                if actor_npc_bs.get_y() != actor_npc_bs.get_y() + 2:
                    actor_npc_bs.set_y(actor_npc_bs, 2 * dt)
                    request.request("BackwardStep", actor,
                                    anim_names.a_anim_walking, "play")

                if actor.get_python_tag("stamina_np")['value'] > 1:
                    actor.get_python_tag("stamina_np")['value'] -= 3

    def npc_in_crouching_logic(self, actor, actor_rb_np, request):
        if (actor.get_python_tag("generic_states")['is_idle']
                and not actor.get_python_tag("generic_states")['is_attacked']
                and not actor.get_python_tag("generic_states")['is_busy']
                and not actor.get_python_tag("generic_states")['is_moving']):
            if (actor.get_python_tag("generic_states")
                    and not actor.get_python_tag("generic_states")['is_crouch_moving']):
                request.request("Crouch", actor, actor_rb_np)

    def npc_in_mounting_logic(self, actor, actor_npc_bs, request):
        if (actor.get_python_tag("human_states")
                and not actor.get_python_tag("generic_states")['is_busy']
                and not actor.get_python_tag("human_states")['is_on_horse']
                and actor.get_python_tag("current_task") is None):
            horses = self.base.game_instance["actors_np"]
            if horses is not None:
                for k in horses:
                    if "NPC_Horse" in k:
                        horse_rb_np = horses[k]
                        if not horse_rb_np.get_child(0).get_python_tag("horse_spec_states")["is_mounted"]:
                            horse = horse_rb_np.get_child(0)
                            if horse.get_python_tag("npc_id") == actor.get_python_tag("npc_id"):
                                if horse_rb_np:
                                    horse_dist = round(actor_npc_bs.get_distance(horse_rb_np))

                                    # Walk to horse
                                    if horse_dist > 1:

                                        if actor.get_python_tag("detour_nav") is False:
                                            actor.set_python_tag("detour_nav", True)

                                        if actor.get_python_tag("detour_nav"):
                                            self.npc_in_walking_rd_logic(actor, actor_npc_bs,
                                                                         horse_rb_np, request)

                                    # Stop walking and start horse mounting task
                                    elif horse_dist <= 1:
                                        if actor.has_python_tag("mounted_horse") is False:
                                            actor.set_python_tag("mounted_horse", horse_rb_np)

                                        if actor.get_python_tag("current_task") != "horse_mounting":
                                            actor.set_python_tag("current_task", "horse_mounting")
                                            # self.base.set_problemus_room()

                                        # Do advanced obstacle avoidance against the horse
                                        # to get another side of the horse
                                        if (actor.get_python_tag("generic_states")['is_idle']
                                                and not actor.get_python_tag("generic_states")['is_attacked']
                                                and not actor.get_python_tag("generic_states")['is_moving']):
                                            name = actor.get_name()
                                            if not self.mounting_sequence[name].is_playing():
                                                self.mounting_sequence[name] = Sequence()

                                                self.face_actor_to(actor_npc_bs, horse_rb_np)

                                                # Wait for 1 second
                                                self.mounting_sequence[name].append(Wait(1))

                                                # Construct Horse Mount Request
                                                mount_func = Func(request.request, "HorseMount",
                                                                  actor, actor_npc_bs, horse, horse_rb_np)

                                                # Append the horse mount interval
                                                self.mounting_sequence[name].append(mount_func)
                                                self.mounting_sequence[name].start()

    def npc_in_unmounting_logic(self, actor, actor_npc_bs, request):
        if (actor.get_python_tag("human_states")
                and actor.get_python_tag("human_states")['is_on_horse']):
            if (actor.get_python_tag("generic_states")['is_idle']
                    and not actor.get_python_tag("generic_states")['is_attacked']
                    and not actor.get_python_tag("generic_states")['is_busy']
                    and not actor.get_python_tag("generic_states")['is_moving']):
                name = actor.get_name()
                if not self.unmounting_sequence[name].is_playing():
                    actor.set_python_tag("current_task", "horse_unmounting")
                    self.unmounting_sequence[name] = Sequence()
                    unmount_func = Func(request.request, "HorseUnmount",
                                        actor, actor_npc_bs)
                    self.unmounting_sequence[name].append(unmount_func)
                    self.unmounting_sequence[name].start()

    def npc_get_weapon(self, actor, request, weapon_name, bone_name):
        if (actor.get_python_tag("generic_states")['is_idle']
                and not actor.get_python_tag("generic_states")['is_attacked']
                and not actor.get_python_tag("generic_states")['is_busy']
                and not actor.get_python_tag("generic_states")['is_moving']):
            if "sword" in weapon_name:
                if (actor.get_python_tag("human_states")
                        and not actor.get_python_tag("human_states")['has_sword']):
                    if actor.get_python_tag("human_states")['is_on_horse']:
                        request.request("GetWeapon", actor, anim_names.a_anim_horse_rider_arm_sword,
                                        weapon_name, bone_name, "play")
                    else:
                        request.request("GetWeapon", actor, anim_names.a_anim_arm_sword,
                                        weapon_name, bone_name, "play")
            elif "bow" in weapon_name:
                if (actor.get_python_tag("human_states")
                        and not actor.get_python_tag("human_states")['has_bow']):
                    if actor.get_python_tag("human_states")['is_on_horse']:
                        request.request("GetWeapon", actor, anim_names.a_anim_horse_rider_arm_bow,
                                        weapon_name, bone_name, "play")
                    else:
                        request.request("GetWeapon", actor, anim_names.a_anim_arm_bow,
                                        weapon_name, bone_name, "play")

    def npc_remove_weapon(self, actor, request, weapon_name, bone_name):
        if (actor.get_python_tag("generic_states")['is_idle']
                and not actor.get_python_tag("generic_states")['is_attacked']
                and not actor.get_python_tag("generic_states")['is_busy']
                and not actor.get_python_tag("generic_states")['is_moving']):
            if "sword" in weapon_name:
                if (actor.get_python_tag("human_states")
                        and actor.get_python_tag("human_states")['has_sword']):
                    if actor.get_python_tag("human_states")['is_on_horse']:
                        request.request("RemoveWeapon", actor, anim_names.a_anim_horse_rider_disarm_sword,
                                        weapon_name, bone_name, "play")
                    else:
                        request.request("RemoveWeapon", actor, anim_names.a_anim_disarm_sword,
                                        weapon_name, bone_name, "play")
            elif "bow" in weapon_name:
                if (actor.get_python_tag("human_states")
                        and actor.get_python_tag("human_states")['has_bow']):
                    if actor.get_python_tag("human_states")['is_on_horse']:
                        request.request("RemoveWeapon", actor, anim_names.a_anim_horse_rider_disarm_bow,
                                        weapon_name, bone_name, "play")
                    else:
                        request.request("RemoveWeapon", actor, anim_names.a_anim_disarm_bow,
                                        weapon_name, bone_name, "play")

    def do_defensive_prediction(self, actor, actor_npc_bs, request, hitbox_dist):
        if actor and actor_npc_bs and request:
            if actor.get_python_tag("priority") is not None and actor.get_python_tag("priority") > 0:
                if hitbox_dist is not None:
                    if hitbox_dist >= 0.5 and hitbox_dist <= 1.8:
                        if actor.get_python_tag("stamina_np")['value'] > 5:
                            if actor.has_python_tag("human_states"):
                                if not actor.get_python_tag("human_states")["has_bow"]:
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
                    if actor.has_python_tag("human_states"):
                        if not actor.get_python_tag("human_states")["has_bow"]:
                            if actor.get_python_tag("enemy_distance") <= 1:
                                target_np = actor.get_python_tag("target_np")
                                self.face_actor_to(actor_npc_bs, target_np)
                                self._npc_in_attacking_logic(actor, actor_npc_bs, request)
                            elif (actor.get_python_tag("enemy_distance") > 1
                                  and actor.get_python_tag("enemy_distance") < 3):
                                self.npc_in_forwardstep_logic(actor, actor_npc_bs, request)

            if (actor.has_python_tag("human_states")
                    and actor.get_python_tag("human_states")["has_bow"]):
                target_np = actor.get_python_tag("target_np")
                # todo thange face_to() to heads_up()
                self.face_actor_to(actor_npc_bs, target_np)
                self._npc_in_attacking_logic(actor, actor_npc_bs, request)
