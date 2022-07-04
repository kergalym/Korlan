from direct.interval.FunctionInterval import Func
from direct.interval.MetaInterval import Sequence, Parallel
from direct.task.TaskManagerGlobal import taskMgr
from panda3d.core import Vec3, Vec2, Point3, BitMask32

from Engine.AI.npc_behavior import NpcBehavior


class NpcController:

    def __init__(self, actor):
        self.base = base
        self.render = render
        self.player = self.base.game_instance["player_ref"]
        self.player_fsm = self.base.game_instance["player_fsm_cls"]
        self.npcs_fsm_states = self.base.game_instance["npcs_fsm_states"]
        self.npc_rotations = {}
        self.activated_npc_count = 0
        self.navmesh_query = self.base.game_instance["navmesh_query"]

        # Keep this class instance for further usage in NpcBehavior class only
        self.base.game_instance["npc_ai_logic_cls"] = self

        self.npc_behavior = NpcBehavior()

        name = actor.get_name()

        actor.get_python_tag("generic_states")['is_idle'] = True
        actor.set_python_tag("arrow_count", 20)
        # actor.set_blend(frameBlend=True)
        actor_bs = self.base.game_instance["actors_np"]
        request = self.npcs_fsm_states[name]

        # R&D
        self.npc_action_seqs = {}
        self.npc_pos = {}

        self.npc_action_seqs[name] = Sequence()
        self.npc_pos[name] = Point3(0, 0, 0)

        if "animal" not in actor.get_python_tag("npc_type"):
            self.npc_state = self.base.game_instance["npc_state_cls"]
            self.npc_state.set_npc_equipment(actor, "Korlan:Spine1")

            taskMgr.add(self.actor_hitbox_trace_task,
                        "{0}_hitboxes_task".format(name.lower()),
                        extraArgs=[actor, actor_bs, request], appendTask=True)

            # TODO KEEP HERE UNTILL HORSE ANIMS BECOME READY
        if actor:
            if "Horse" not in actor.get_name():
                taskMgr.add(self.npc_behavior.npc_generic_logic,
                            "{0}_npc_generic_logic_task".format(name),
                            extraArgs=[actor, self.player, request, False],
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
                            # Deactivate enemy weapon if we got hit
                            if str(hitbox_np.get_collide_mask()) != " 0000 0000 0000 0000 0000 0000 0000 0000\n":
                                distance = round(hitbox_np.get_distance(parent_np), 1)

                                if distance >= 0.5 and distance <= 1.8:
                                    hitbox_np.set_collide_mask(BitMask32.allOff())
                                    if actor.get_python_tag("health_np"):
                                        # NPC gets damage if he has health point
                                        if actor.get_python_tag("health_np")['value'] > 1:
                                            request.request("Attacked", actor, "HitToBody", "play")
                                            actor.get_python_tag("health_np")['value'] -= 1

            # NPC dies if he has no health point
            if actor.get_python_tag("health_np")['value'] == 0:
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
            if self.is_ready_for_staying(actor):
                actor.get_python_tag("generic_states")['is_moving'] = False
                actor.get_python_tag("generic_states")['is_idle'] = True

            if actor.get_python_tag("generic_states")['is_idle']:
                if actor.get_python_tag("generic_states")['is_crouch_moving']:
                    request.request("Idle", actor, "standing_to_crouch", "loop")
                elif not actor.get_python_tag("generic_states")['is_crouch_moving']:
                    request.request("Idle", actor, "Standing_idle_male", "loop")

    def npc_in_dying_logic(self, actor, request):
        if actor and request:
            actor.get_python_tag("generic_states")['is_moving'] = False
            actor.get_python_tag("generic_states")['is_alive'] = False

            if not (actor.get_python_tag("generic_states")['is_alive']):
                if actor.get_python_tag("generic_states")['is_idle']:
                    request.request("Death", actor, "Dying", "play")
                    actor.get_python_tag("generic_states")['is_idle'] = False

    def update_pathfinding(self, name, path_point):
        if name and isinstance(path_point, Point3):
            self.npc_pos[name] = path_point

    def do_walking_sequence_once(self, actor_npc_bs, oppo_npc_bs, actor_name):
        if (actor_npc_bs and oppo_npc_bs
                and actor_name and isinstance(actor_name, str)):
            current_dir = actor_npc_bs.get_hpr()

            self.navmesh_query.nearest_point(self.npc_pos[actor_name])

            # Set last pos from opposite actor's world points
            last_pos = self.render.get_relative_point(actor_npc_bs, oppo_npc_bs.get_pos())
            last_pos = Point3(last_pos[0], last_pos[1], 0)

            # Find path
            path = self.navmesh_query.find_path(self.npc_pos[actor_name], last_pos)
            path_points = list(path.points)

            for i in range(len(path_points) - 1):
                speed = 2

                # Heading
                new_hpr = Vec3(Vec2(0, -1).signed_angle_deg(path_points[i + 1].xy - path_points[i].xy),
                               current_dir[1],
                               current_dir[2])
                hpr_interval = actor_npc_bs.hprInterval(speed, new_hpr)

                # Movement
                dist = (path_points[i + 1] - path_points[i]).length()
                pos_interval = actor_npc_bs.posInterval(dist / speed, path_points[i + 1], path_points[i])

                # Append sequence tasks in that order
                self.npc_action_seqs[actor_name].append(hpr_interval)
                self.npc_action_seqs[actor_name].append(pos_interval)
                self.npc_action_seqs[actor_name].append(Func(self.update_pathfinding, actor_name, last_pos))

                current_dir = new_hpr

            if not self.npc_action_seqs[actor_name].is_playing():
                self.npc_action_seqs[actor_name].start()

            self.npc_pos[actor_name] = last_pos

    def npc_in_walking_logic(self, actor, actor_npc_bs, oppo_npc_bs, request):
        if actor and actor_npc_bs and oppo_npc_bs and request:
            actor_name = actor.get_name()

            if self.is_ready_for_walking(actor):
                actor.get_python_tag("generic_states")['is_idle'] = False
                actor.get_python_tag("generic_states")['is_moving'] = True

            if actor.get_python_tag("generic_states")['is_moving']:
                request.request("WalkRD", actor, "Walking", "loop")

            if self.navmesh_query:

                self.do_walking_sequence_once(actor_npc_bs, oppo_npc_bs, actor_name)

                if round(actor_npc_bs.get_distance(oppo_npc_bs)) > 4:
                    self.base.messenger.send("do_walking_sequence_once")
                else:
                    if self.npc_action_seqs[actor_name].is_playing():
                        self.npc_action_seqs[actor_name].finish()

                    actor.get_python_tag("generic_states")['is_idle'] = True
                    actor.get_python_tag("generic_states")['is_moving'] = False

    def npc_in_gathering_logic(self, actor, request):
        pass

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

    def npc_in_attacking_logic(self, actor, request):
        if (actor.get_python_tag("generic_states")['is_idle']
                and not actor.get_python_tag("generic_states")['is_attacked']
                and not actor.get_python_tag("generic_states")['is_busy']
                and not actor.get_python_tag("generic_states")['is_moving']):
            if actor.get_python_tag("human_states")["has_sword"]:
                action = "great_sword_slash"
                request.request("Attack", actor, action, "play")
            elif actor.get_python_tag("human_states")["has_bow"]:
                action = "archer_standing_draw_arrow"
                request.request("Archery", actor, action, "play")
            else:
                action = "Boxing"
                request.request("Attack", actor, action, "play")

    def npc_in_forwardroll_logic(self, actor, actor_npc_bs, request):
        dt = globalClock.getDt()
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
