from direct.interval.FunctionInterval import Func
from direct.interval.MetaInterval import Sequence
from direct.task.TaskManagerGlobal import taskMgr
from panda3d.core import Vec3, Vec2, BitMask32, Point3

from Engine.AI.npc_behavior import NpcBehavior


class NpcAILogic:

    def __init__(self, ai_world, ai_behaviors, ai_chars, ai_chars_bs, player,
                 player_fsm, npcs_fsm_states, npc_classes):
        self.base = base
        self.render = render
        self.ai_world = ai_world
        self.ai_behaviors = ai_behaviors
        self.ai_chars = ai_chars
        self.ai_chars_bs = ai_chars_bs
        self.player = player
        self.player_fsm = player_fsm
        self.npcs_fsm_states = npcs_fsm_states
        self.npc_classes = npc_classes
        self.npc_rotations = {}
        self.activated_npc_count = 0
        self.navmesh = self.base.game_instance["navmesh"]
        self.navmesh_query = self.base.game_instance["navmesh_query"]

        self.base.game_instance["use_pandai"] = True

        self.vect = {"panic_dist": 5,
                     "relax_dist": 5,
                     "wander_radius": 5,
                     "plane_flag": 0,
                     "area_of_effect": 10}

        # Keep this class instance for further usage in NpcBehavior class only
        self.base.game_instance["npc_ai_logic_cls"] = self

        self.npc_behavior = NpcBehavior()

        # R&D
        self.npc_action_seqs = {}
        self.npc_pos = {}

        for name in self.ai_chars_bs:
            actor = self.base.game_instance['actors_ref'][name]
            actor.get_python_tag("generic_states")['is_idle'] = True
            actor.set_python_tag("arrow_count", 20)
            actor.set_blend(frameBlend=True)
            actor_bs = self.ai_chars_bs[name]
            request = self.npcs_fsm_states[name]

            self.npc_action_seqs[name] = Sequence()
            self.npc_pos[name] = Point3(0, 0, 0)

            if "animal" not in actor.get_python_tag("npc_type"):
                self.npc_state = self.base.game_instance["npc_state_cls"]
                self.npc_state.set_npc_equipment(actor, "Korlan:Spine1")

            taskMgr.add(self.actor_hitbox_trace_task,
                        "{0}_hitboxes_task".format(name.lower()),
                        extraArgs=[actor, actor_bs, request], appendTask=True)

        taskMgr.add(self.update_pathfinding_task,
                    "update_pathfinding_task",
                    appendTask=True)

        taskMgr.add(self.npc_behavior_init_task,
                    "npc_behavior_init_task",
                    appendTask=True)

    def update_pathfinding_task(self, task):
        if self.ai_chars_bs and self.ai_world and self.ai_behaviors:
            for actor_name in self.ai_behaviors:
                self.ai_chars[actor_name].set_max_force(5)

                for name in self.ai_chars_bs:
                    if "Horse" not in name:
                        # Add actors as obstacles except actor that avoids them
                        if name != actor_name and "Ernar" in name:
                            ai_char_bs = self.ai_chars_bs[name]
                            if ai_char_bs:
                                # self.ai_behaviors[actor_name].path_find_to(ai_char_bs, "addPath")
                                self.ai_behaviors[actor_name].add_dynamic_obstacle(ai_char_bs)
                                # self.ai_behaviors[actor_name].path_find_to(self.player, "addPath")
                                self.ai_behaviors[actor_name].add_dynamic_obstacle(self.player)
                                # Obstacle avoidance behavior
                                self.ai_behaviors[actor_name].obstacle_avoidance(1.0)
                                self.ai_world.add_obstacle(self.base.box_np)

            return task.done

    def npc_behavior_init_task(self, task):
        if self.base.game_instance['loading_is_done'] == 1:
            if (self.player
                    and self.base.game_instance['actors_ref']):
                for actor_name in self.base.game_instance['actors_ref']:

                    # TODO Remove these lines when horse-related animations become ready
                    if "Horse" in actor_name:
                        continue

                    actor = self.base.game_instance['actors_ref'][actor_name]
                    if actor.get_python_tag("npc_class") == "friend":
                        actor.get_python_tag("generic_states")['is_alive'] = False

                    if actor.get_python_tag("npc_class") == "neutral":
                        actor.get_python_tag("generic_states")['is_alive'] = False

                    request = self.npcs_fsm_states[actor_name]

                    # Add a tracked obstacle which is NPC.
                    """actor_name = "{0}:BS".format(actor_name)
                    actor_npc_bs = self.base.game_instance["actors_np"][actor_name]
                    self.navmesh.add_node_path(actor_npc_bs)
                    self.navmesh.update()"""

                    name = actor_name.lower()
                    # FIXME: Test the directives. Tempo set passive to True
                    taskMgr.add(self.npc_behavior.npc_generic_logic,
                                "{0}_npc_friend_logic_task".format(name),
                                extraArgs=[actor, self.player, request, True],
                                appendTask=True)

                return task.done

        return task.cont

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
                            # Deactivate enemy weapon if we got hit
                            if str(hitbox_np.get_collide_mask()) != " 0000 0000 0000 0000 0000 0000 0000 0000\n":
                                distance = round(hitbox_np.get_distance(parent_np), 1)

                                # Enemy Prediction
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
                                    if actor.get_python_tag("health_np"):
                                        # NPC gets damage if he has health point
                                        if (not actor.get_python_tag("generic_states")['is_busy']
                                                and not actor.get_python_tag("generic_states")['is_using']):
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
                        if round(actor_bs.get_distance(enemy_npc_bs)) < 50:
                            return [enemy_npc_ref, enemy_npc_bs]

    def is_ready_for_staying(self, actor):
        if actor.get_python_tag("human_states"):
            # Only Human NPC has human_states
            if (actor.get_python_tag("generic_states")['is_moving']
                    and not actor.get_python_tag("generic_states")['is_running']
                    and not actor.get_python_tag("generic_states")['is_crouch_moving']
                    and not actor.get_python_tag("generic_states")['is_crouching']
                    and not actor.get_python_tag("generic_states")['is_jumping']
                    and not actor.get_python_tag("generic_states")['is_attacked']
                    and not actor.get_python_tag("generic_states")['is_busy']
                    and not actor.get_python_tag("generic_states")['is_using']
                    and not actor.get_python_tag("generic_states")['is_turning']
                    and not actor.get_python_tag("human_states")['horse_riding']
                    and not actor.get_python_tag("human_states")['is_on_horse']):
                return True
            else:
                return False
        elif not actor.get_python_tag("human_states"):
            # Animal NPC has no human_states
            if (actor.get_python_tag("generic_states")['is_moving']
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
            if self.base.game_instance["use_pandai"]:
                if self.is_ready_for_staying(actor):
                    actor_name = actor.get_name()
                    if (self.ai_behaviors[actor_name].behavior_status("pursue") == "disabled"
                            or self.ai_behaviors[actor_name].behavior_status("pursue") == "done"):
                        if self.ai_behaviors[actor_name].behavior_status("pursue") != "disabled":
                            self.ai_behaviors[actor_name].remove_ai("pursue")
                        actor.get_python_tag("generic_states")['is_moving'] = False
                        actor.get_python_tag("generic_states")['is_idle'] = True
            else:
                if self.is_ready_for_staying(actor):
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
            if self.base.game_instance["use_pandai"]:
                if self.is_ready_for_staying(actor):
                    actor_name = actor.get_name()
                    if (self.ai_behaviors[actor_name].behavior_status("pursue") == "disabled"
                            or self.ai_behaviors[actor_name].behavior_status("pursue") == "done"):
                        if self.ai_behaviors[actor_name].behavior_status("pursue") != "disabled":
                            self.ai_behaviors[actor_name].remove_ai("pursue")

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

    def do_walking_sequence_once(self, actor_npc_bs, oppo_npc_bs, actor_name):
        if not self.npc_action_seqs[actor_name].is_playing():
            if (actor_npc_bs and oppo_npc_bs
                    and actor_name and isinstance(actor_name, str)):

                self.navmesh_query.nearest_point(self.npc_pos[actor_name])

                # Set last pos from opposite actor's world points
                last_pos = self.render.get_relative_vector(oppo_npc_bs.get_parent(),
                                                           oppo_npc_bs.get_pos())
                last_pos = Point3(last_pos[0], last_pos[1], 0)

                self.navmesh.update()

                # Find path
                path = self.navmesh_query.find_path(self.npc_pos[actor_name], last_pos)
                path_points = list(path.points)
                current_dir = actor_npc_bs.get_hpr()

                self.npc_action_seqs[actor_name] = Sequence()

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

                self.npc_action_seqs[actor_name].start()
                self.npc_pos[actor_name] = last_pos

    def npc_in_walking_logic(self, actor, actor_npc_bs, oppo_npc_bs, request):
        if actor and actor_npc_bs and oppo_npc_bs and request:
            actor_name = actor.get_name()

            # Crouch collision states
            crouch_bs_mask = BitMask32.allOff()
            capsule_bs_mask = BitMask32.allOff()
            actor_name_bs = "{0}:BS".format(actor_name)
            if not actor.get_python_tag("generic_states")['is_crouch_moving']:
                crouch_bs_mask = self.base.game_instance['actors_crouch_bs_np_mask'][actor_name_bs]
                capsule_bs_mask = BitMask32.allOff()
            elif actor.get_python_tag("generic_states")['is_crouch_moving']:
                crouch_bs_mask = BitMask32.allOff()
                capsule_bs_mask = self.base.game_instance["actors_np_mask"][actor_name_bs]
            self.base.game_instance['actors_crouch_bs_np'][actor_name_bs].setCollideMask(crouch_bs_mask)
            self.base.game_instance['actors_np'][actor_name_bs].setCollideMask(capsule_bs_mask)

            if self.base.game_instance["use_pandai"]:
                if self.is_ready_for_walking(actor):
                    if self.ai_behaviors[actor_name].behavior_status("pursue") == "disabled":
                        actor.get_python_tag("generic_states")['is_idle'] = False
                        actor.get_python_tag("generic_states")['is_moving'] = True
                    elif self.ai_behaviors[actor_name].behavior_status("pursue") == "done":
                        actor.get_python_tag("generic_states")['is_idle'] = False
                        actor.get_python_tag("generic_states")['is_moving'] = True

                if actor.get_python_tag("generic_states")['is_moving']:

                    if actor.get_python_tag("stamina_np"):
                        if actor.get_python_tag("stamina_np")['value'] > 1:
                            actor.get_python_tag("stamina_np")['value'] -= 1

                    request.request("Walk", actor, oppo_npc_bs,
                                    self.ai_chars_bs,
                                    self.ai_behaviors[actor_name],
                                    "pursuer", "Walking", self.vect, "loop")

            elif not self.base.game_instance["use_pandai"]:
                if self.navmesh_query:
                    if self.is_ready_for_walking(actor):
                        actor.get_python_tag("generic_states")['is_idle'] = False
                        actor.get_python_tag("generic_states")['is_moving'] = True

                    if actor.get_python_tag("stamina_np"):
                        if actor.get_python_tag("stamina_np")['value'] > 1:
                            actor.get_python_tag("stamina_np")['value'] -= 1

                    request.request("WalkRD", actor, "Walking", "loop")

                    if round(actor_npc_bs.get_distance(oppo_npc_bs)) > 1:
                        self.do_walking_sequence_once(actor_npc_bs, oppo_npc_bs, actor_name)
                    else:
                        self.npc_action_seqs[actor_name].finish()

                        actor.get_python_tag("generic_states")['is_idle'] = True
                        actor.get_python_tag("generic_states")['is_moving'] = False

    def npc_in_gathering_logic(self, actor, request):
        if actor and request:
            npc_state_cls = self.base.game_instance["npc_state_cls"]
            if actor.get_python_tag("used_item_np"):
                npc_state_cls.drop_item(actor)
            else:
                npc_state_cls.pick_up_item(actor, "Korlan:RightHand")

    def npc_in_blocking_logic(self, actor, request):
        if (actor.get_python_tag("generic_states")['is_idle']
                and not actor.get_python_tag("generic_states")['is_attacked']
                and not actor.get_python_tag("generic_states")['is_busy']
                and not actor.get_python_tag("generic_states")['is_moving']):
            if actor.get_python_tag("stamina_np"):
                if actor.get_python_tag("stamina_np")['value'] > 5:
                    action = ""
                    if actor.get_python_tag("human_states")['has_sword']:
                        action = "great_sword_blocking"
                    else:
                        action = "center_blocking"
                    request.request("Block", actor, action, "play")

                    if actor.get_python_tag("stamina_np")['value'] > 1:
                        actor.get_python_tag("stamina_np")['value'] -= 6

    def npc_in_attacking_logic(self, actor, request):
        if (actor.get_python_tag("generic_states")['is_idle']
                and not actor.get_python_tag("generic_states")['is_attacked']
                and not actor.get_python_tag("generic_states")['is_busy']
                and not actor.get_python_tag("generic_states")['is_moving']):

            if actor.get_python_tag("stamina_np"):
                if actor.get_python_tag("stamina_np")['value'] > 35:
                    if actor.get_python_tag("human_states")["has_sword"]:
                        action = "great_sword_slash"
                        request.request("Attack", actor, action, "play")
                    elif actor.get_python_tag("human_states")["has_bow"]:
                        action = "archer_standing_draw_arrow"
                        request.request("Archery", actor, action, "play")
                    else:
                        action = "Boxing"
                        request.request("Attack", actor, action, "play")

                    if actor.get_python_tag("stamina_np")['value'] > 1:
                        actor.get_python_tag("stamina_np")['value'] -= 18

    def npc_in_forwardroll_logic(self, actor, actor_npc_bs, request):
        dt = globalClock.getDt()
        if actor.get_python_tag("stamina_np"):
            if actor.get_python_tag("stamina_np")['value'] > 15:
                if actor_npc_bs.get_x() != actor_npc_bs.get_x() - 2:
                    actor_npc_bs.set_x(actor_npc_bs, -2 * dt)
                    request.request("ForwardRoll", actor, "forward_roll", "play")
                elif actor_npc_bs.get_x() != actor_npc_bs.get_x() + 2:
                    actor_npc_bs.set_x(actor_npc_bs, 2 * dt)
                    request.request("ForwardRoll", actor, "forward_roll", "play")
                elif actor_npc_bs.get_y() != actor_npc_bs.get_y() - 2:
                    actor_npc_bs.set_y(actor_npc_bs, -2 * dt)
                    request.request("ForwardRoll", actor, "forward_roll", "play")
                elif actor_npc_bs.get_y() != actor_npc_bs.get_y() + 2:
                    actor_npc_bs.set_y(actor_npc_bs, 2 * dt)
                    request.request("ForwardRoll", actor, "forward_roll", "play")

                if actor.get_python_tag("stamina_np")['value'] > 1:
                    actor.get_python_tag("stamina_np")['value'] -= 15

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

    def actor_rotate(self, actor_npc_bs, path_points):
        current_dir = actor_npc_bs.get_hpr()

        for i in range(len(path_points) - 1):
            new_hpr = Vec3(Vec2(0, -1).signed_angle_deg(path_points[i + 1].xy - path_points[i].xy), current_dir[1],
                           current_dir[2])
            actor_npc_bs.set_hpr(new_hpr)
            # actor_npc_bs.hprInterval(0, new_hpr)

    def face_actor_to(self, actor, target_np):
        if actor and target_np:
            actor.look_at(target_np.get_pos())
            actor.set_h(target_np, -180)

            # keep target once
            saved_target_np = actor.get_python_tag("target_np")
            if not saved_target_np:
                actor.set_python_tag("target_np", target_np)
            elif saved_target_np:
                if saved_target_np.get_name() != target_np.get_name():
                    actor.set_python_tag("target_np", target_np)

    def get_hit_distance(self, actor):
        if actor and actor.find("**/**Hips:HB"):
            parent_node = actor.find("**/**Hips:HB").node()
            parent_np = actor.find("**/**Hips:HB")

            for node in parent_node.get_overlapping_nodes():
                damage_weapons = actor.get_python_tag("damage_weapons")
                for weapon in damage_weapons:
                    # Exclude our own weapon hits
                    if (weapon in node.get_name()
                            and actor.get_name() not in node.get_name()):
                        hitbox_np = self.render.find("**/{0}".format(node.get_name()))
                        if hitbox_np:
                            distance = round(hitbox_np.get_distance(parent_np), 1)
                            return distance

    def do_defensive_prediction(self, actor, actor_npc_bs, request, hitbox_dist):
        if actor and actor_npc_bs and request and hitbox_dist:
            if (not actor.get_python_tag("generic_states")["is_attacked"]
                    or not actor.get_python_tag("generic_states")["is_busy"]):
                if hitbox_dist >= 0.5 and hitbox_dist <= 2.2:
                    if actor.get_python_tag("stamina_np")['value'] > 5:
                        self.npc_in_blocking_logic(actor, request)
                elif hitbox_dist >= 0.5 and hitbox_dist <= 1.8:
                    if actor.get_python_tag("stamina_np")['value'] > 15:
                        self.npc_in_forwardroll_logic(actor, actor_npc_bs, request)
                else:
                    if actor.get_python_tag("stamina_np")['value'] > 35:
                        self.npc_in_attacking_logic(actor, request)
                    if actor.get_python_tag("stamina_np")['value'] > 5:
                        self.npc_in_blocking_logic(actor, request)
