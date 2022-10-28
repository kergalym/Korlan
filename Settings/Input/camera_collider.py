from direct.interval.FunctionInterval import Func
from direct.interval.LerpInterval import LerpPosInterval
from direct.interval.MetaInterval import Sequence
from direct.task.TaskManagerGlobal import taskMgr
from panda3d.bullet import BulletSphereShape, BulletGhostNode
from panda3d.core import BitMask32, Point3


class CameraCollider:

    def __init__(self):
        self.base = base
        self.render = render
        self._trig_radius = 1.75 - 2 * 0.3
        self.base.game_instance["cam_obstacle_is_close"] = False
        self.cam_lerp = Sequence()

    def set_camera_trigger(self, task):
        if self.base.game_instance["loading_is_done"] == 1:
            if (self.render.find("**/World")
                    and self.base.game_instance["physics_world_np"]):
                ph_world = self.base.game_instance["physics_world_np"]
                player_bs = self.base.game_instance["player_np"]
                self._set_ghost_trigger(actor=player_bs, world=ph_world)

                return task.done

        return task.cont

    def _set_ghost_trigger(self, actor, world):
        if actor and world:
            sphere = BulletSphereShape(self._trig_radius)
            trigger_bg = BulletGhostNode('player_cam_trigger')
            trigger_bg.add_shape(sphere)
            trigger_np = self.render.attach_new_node(trigger_bg)
            trigger_np.set_collide_mask(BitMask32(0x0f))
            world.attach_ghost(trigger_bg)
            trigger_np.reparent_to(actor)

            taskMgr.add(self._camera_collider_task,
                        "camera_collider_task",
                        extraArgs=[trigger_np, actor],
                        appendTask=True)

    def _set_camera_collider_stat(self, player_bs, node_np, node):
        if node:
            name = node.get_name()
        else:
            name = "N/A"
        d = {"name": player_bs.get_name(),
             "player_to_obstacle": int(player_bs.get_distance(node_np)),
             "camera_to_obstacle": int(base.camera.get_distance(node_np)),
             "object_name": name
             }
        self.base.game_instance["cam_coll_dist_stat"] = d

    def _camera_collider_task(self, trigger_np, player_rb_np, task):
        if self.base.game_instance['menu_mode']:
            self.base.camera.set_z(0.0)
            return task.done

        if (not self.base.game_instance["ui_mode"]
                and not self.base.game_instance["inv_mode"]
                and base.player_states["is_alive"]):

            close_y = -2.0
            def_y = self.base.game_instance["mouse_y_cam"]

            if not self.base.game_instance['is_aiming']:

                # Self collision
                player = self.base.game_instance['player_ref']
                if (not self.base.game_instance["is_indoor"]
                        and not player.get_python_tag("is_on_horse")):
                    pv_pitch = self.base.game_instance["player_pivot"].get_p()
                    if not self.base.game_instance["cam_obstacle_is_close"]:
                        if pv_pitch > 6.0:
                            self._interpolate_to(target_y=close_y, start_y=def_y,
                                                 target_z=-0.3, start_z=0)
                    if self.base.game_instance["cam_obstacle_is_close"]:
                        if pv_pitch < -49.0:
                            self._interpolate_to(target_y=def_y, start_y=close_y,
                                                 target_z=0, start_z=-0.3)

                trigger = player_rb_np.find("**/player_cam_trigger").node()
                if trigger:
                    for node in trigger.get_overlapping_nodes():

                        # Indoor triggering
                        if "indoor" in node.get_name():

                            node_np = render.find("**/{0}".format(node.get_name()))
                            if (int(trigger_np.get_distance(node_np)) >= 1
                                    and int(trigger_np.get_distance(node_np)) < 4):
                                if not self.base.game_instance["is_indoor"]:
                                    self._interpolate_to(target_y=close_y, start_y=def_y,
                                                         target_z=0, start_z=0)
                                    self.base.game_instance["is_indoor"] = True

                            elif (int(trigger_np.get_distance(node_np)) >= 4
                                  and int(trigger_np.get_distance(node_np)) < 7):
                                if self.base.game_instance["is_indoor"]:
                                    self._interpolate_to(target_y=def_y, start_y=close_y,
                                                         target_z=0, start_z=0)
                                    self.base.game_instance["is_indoor"] = False

                        # Outdoor triggering
                        if (not self.base.game_instance["is_indoor"]
                                and not self.base.player_states['is_mounted']):
                            if node:

                                # Filtering for rigid bodies and regular meshes
                                if "HB" in node.get_name():
                                    continue

                                if "BGN" in node.get_name():
                                    continue

                                if "Crouch" in node.get_name():
                                    continue

                                if "Player" in node.get_name():
                                    continue

                                if "trigger" in node.get_name():
                                    continue

                                if "Ground" in node.get_name():
                                    continue

                                name = node.get_name()
                                node_np = render.find("**/{0}".format(name))
                                if node_np:
                                    if self.base.game_settings['Debug']['set_debug_mode'] == "YES":
                                        self._set_camera_collider_stat(player_rb_np, node_np, None)

                                    # zoom in If obstacle is close and is not in the field of view
                                    if int(base.camera.get_distance(node_np)) > 1:
                                        if (int(base.camera.get_distance(player_rb_np)) < 3
                                                and int(base.camera.get_distance(player_rb_np)) > 1):
                                            if self.base.game_instance["cam_obstacle_is_close"]:
                                                self._interpolate_to(target_y=def_y, start_y=close_y,
                                                                     target_z=0, start_z=0)

                                self._camera_raycaster_collision(node=node,
                                                                 player_rb_np=player_rb_np)

        return task.cont

    def _toggle_npc_hud(self, player_rb_np, node_np):
        if base.player_states["has_bow"]:
            if round(player_rb_np.get_distance(node_np) < 6):
                # Show NPC HUD if it's close
                for k in self.base.game_instance["actors_ref"]:
                    if k not in node_np.get_name():
                        _actor = self.base.game_instance["actors_ref"][k]
                        if _actor.has_python_tag("npc_hud_np"):
                            if _actor.get_python_tag("npc_hud_np") is not None:
                                if not _actor.get_python_tag("npc_hud_np").is_hidden():
                                    _actor.get_python_tag("npc_hud_np").hide()
                    else:
                        _actor = self.base.game_instance["actors_ref"][k]
                        if _actor.has_python_tag("npc_hud_np"):
                            if _actor.get_python_tag("npc_hud_np") is not None:
                                _actor.get_python_tag("npc_hud_np").show()
            else:
                # Hide NPCs HUD if it's far
                for k in self.base.game_instance["actors_ref"]:
                    _actor = self.base.game_instance["actors_ref"][k]
                    if _actor.has_python_tag("npc_hud_np"):
                        if _actor.get_python_tag("npc_hud_np") is not None:
                            if not _actor.get_python_tag("npc_hud_np").is_hidden():
                                _actor.get_python_tag("npc_hud_np").hide()

        # If I have any melee weapon instead of bow
        elif not base.player_states["has_bow"]:
            if round(player_rb_np.get_distance(node_np) > 1):
                # Hide NPCs HUD if it's far
                for k in self.base.game_instance["actors_ref"]:
                    _actor = self.base.game_instance["actors_ref"][k]
                    if _actor.has_python_tag("npc_hud_np"):
                        if _actor.get_python_tag("npc_hud_np") is not None:
                            if not _actor.get_python_tag("npc_hud_np").is_hidden():
                                _actor.get_python_tag("npc_hud_np").hide()

            else:
                # Show NPCs HUD if it's close
                for k in self.base.game_instance["actors_ref"]:
                    if k not in node_np.get_name():
                        _actor = self.base.game_instance["actors_ref"][k]
                        if _actor.has_python_tag("npc_hud_np"):
                            if _actor.get_python_tag("npc_hud_np") is not None:
                                if not _actor.get_python_tag("npc_hud_np").is_hidden():
                                    _actor.get_python_tag("npc_hud_np").hide()
                    else:
                        _actor = self.base.game_instance["actors_ref"][k]
                        if _actor.has_python_tag("npc_hud_np"):
                            if _actor.get_python_tag("npc_hud_np") is not None:
                                _actor.get_python_tag("npc_hud_np").show()

    def _camera_raycaster_collision(self, node, player_rb_np):
        if self.base.game_instance['physics_world_np']:
            mouse_watch = base.mouseWatcherNode
            if mouse_watch.has_mouse():
                pos_mouse = base.mouseWatcherNode.get_mouse()
                pos_from = Point3(0, 1, 0)
                pos_to = Point3(0, 1000, 0)
                base.camLens.extrude(pos_mouse, pos_from, pos_to)

                def_y = self.base.game_instance["mouse_y_cam"]
                close_y = -2.0

                if "Horse" in node.get_name():
                    close_y = def_y

                pos_from = self.render.get_relative_point(base.camera, pos_from)
                pos_to = self.render.get_relative_point(base.camera, pos_to)
                physics_world_np = self.base.game_instance['physics_world_np']
                raytest_all_result = physics_world_np.ray_test_all(pos_from, pos_to)

                if raytest_all_result:
                    for hit in raytest_all_result.get_hits():
                        if hit.get_node():
                            # Filtering for rigid bodies
                            if ("BS" in hit.get_node().get_name()
                                    and "Player:BS" not in hit.get_node().get_name()):
                                name = hit.get_node().get_name()
                                node_np = self.base.game_instance["actors_np"].get(name)
                                if node_np is not None:
                                    if self.base.game_settings['Debug']['set_debug_mode'] == "YES":
                                        self._set_camera_collider_stat(player_rb_np, node_np, node)

                                    if int(player_rb_np.get_distance(node_np)) < 2:
                                        # zoom in If obstacle is close and is in the field of view
                                        if (int(base.camera.get_distance(node_np)) > 1
                                                and int(base.camera.get_distance(node_np)) < 4):
                                            if not self.base.game_instance["cam_obstacle_is_close"]:
                                                self._interpolate_to(target_y=close_y, start_y=def_y,
                                                                     target_z=0, start_z=0)

                                    # Toggling NPC HUD
                                    self._toggle_npc_hud(player_rb_np, node_np)

                name = node.get_name()
                node_np = self.base.game_instance["actors_np"].get(name)
                if node_np is not None:
                    if int(player_rb_np.get_distance(node_np)) > 1:
                        # zoom out if obstacle is far from the player
                        if (int(base.camera.get_distance(player_rb_np)) < 4
                                and int(base.camera.get_distance(player_rb_np)) > 0):
                            self._interpolate_to(target_y=def_y, start_y=close_y,
                                                 target_z=0, start_z=0)

    def _toggle_camera_zooming_state(self):
        if not self.base.game_instance["cam_obstacle_is_close"]:
            self.base.game_instance["cam_obstacle_is_close"] = True
        elif self.base.game_instance["cam_obstacle_is_close"]:
            self.base.game_instance["cam_obstacle_is_close"] = False

    def _interpolate_to(self, target_y, target_z, start_y, start_z):
        if not self.cam_lerp.is_playing():
            self.cam_lerp = Sequence()
            lerp = LerpPosInterval(base.camera,
                                   duration=0.3,
                                   pos=Point3(0, target_y, target_z),
                                   startPos=Point3(0, start_y, start_z))
            func = Func(self._toggle_camera_zooming_state)
            self.cam_lerp.append(lerp)
            self.cam_lerp.append(func)
            self.cam_lerp.start()
