from direct.interval.LerpInterval import LerpPosInterval
from direct.task.TaskManagerGlobal import taskMgr
from panda3d.bullet import BulletSphereShape, BulletGhostNode
from panda3d.core import BitMask32, Point3


class PlayerCamera:

    def __init__(self):
        self.base = base
        self.render = render
        self._speed = 5
        self._trig_radius = 1.75 - 2 * 0.3
        self._is_close = False

        self.cam_includes = {}

    def _collect_colliding_objects(self):
        children = self.render.find_all_matches("**/*:BS")

        if children:
            for np in children:
                if "Ground" in np.get_name():
                    continue

                elif "Player" in np.get_name():
                    continue

                self.cam_includes[np.get_name()] = True

    def set_camera_trigger(self, task):
        if self.base.game_instance["loading_is_done"] == 1:
            if (self.render.find("**/World")
                    and self.base.game_instance["physics_world_np"]):

                ph_world = self.base.game_instance["physics_world_np"]
                player_bs = self.base.get_actor_bullet_shape_node(asset="Player", type="Player")

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
            trigger_np.set_pos(0, 0, 1)

            self._collect_colliding_objects()

            taskMgr.add(self._camera_collider_task,
                        "camera_collider_task",
                        extraArgs=[trigger_np, actor],
                        appendTask=True)

    def _camera_collider_task(self, trigger_np, player_bs, task):
        if self.base.game_instance['menu_mode']:
            self.base.camera.set_z(0.0)
            return task.done

        if not self.base.game_instance["ui_mode"]:
            if not self.base.game_instance['is_aiming']:
                trigger = player_bs.find("**/player_cam_trigger").node()
                if trigger:
                    for node in trigger.get_overlapping_nodes():

                        # Indoor triggering
                        if "indoor" in node.get_name():

                            close_y = -2.0
                            def_y = self.base.game_instance["mouse_y_cam"]

                            node_np = render.find("**/{0}".format(node.get_name()))
                            if (round(trigger_np.get_distance(node_np)) >= 1
                                    and round(trigger_np.get_distance(node_np)) < 4):
                                if not self.base.game_instance["is_indoor"]:
                                    self._interpolate_to(target_y=close_y, start_y=def_y)
                                    self.base.game_instance["is_indoor"] = True

                            elif (round(trigger_np.get_distance(node_np)) >= 4
                                  and round(trigger_np.get_distance(node_np)) < 7):
                                if self.base.game_instance["is_indoor"]:
                                    self._interpolate_to(target_y=def_y, start_y=close_y)
                                    self.base.game_instance["is_indoor"] = False

                        # Outdoor triggering
                        if (not self.base.game_instance["is_indoor"]
                                and not self.base.player_states['is_mounted']):
                            self._camera_raycaster_collision(trigger_np=trigger_np,
                                                             node=node,
                                                             player_bs=player_bs)

        return task.cont

    def _interpolate_to(self, target_y, start_y):
        LerpPosInterval(self.base.camera,
                        duration=1.0,
                        pos=Point3(0, target_y, 0),
                        startPos=Point3(0, start_y, 0)).start()

    def _camera_raycaster_collision(self, trigger_np, node, player_bs):
        if self.cam_includes.get(node.get_name()):
            if self.base.game_instance['physics_world_np']:
                mouse_watch = base.mouseWatcherNode
                if mouse_watch.has_mouse():
                    pos_mouse = base.mouseWatcherNode.get_mouse()
                    pos_from = Point3(0, 1, 0)
                    pos_to = Point3(0, 1000, 0)
                    base.camLens.extrude(pos_mouse, pos_from, pos_to)

                    node_np = render.find("**/{0}".format(node.get_name()))
                    pivot = player_bs.find("**/pivot")

                    def_y = self.base.game_instance["mouse_y_cam"]
                    close_y = -2.0

                    if "Horse" in node_np.get_name():
                        close_y = def_y

                    pos_from = self.render.get_relative_point(base.camera, pos_from)
                    pos_to = self.render.get_relative_point(base.camera, pos_to)
                    physics_world_np = self.base.game_instance['physics_world_np']
                    raytest_result = physics_world_np.ray_test_closest(pos_from, pos_to)

                    # Check if collided object at the center of the screen
                    # and is close to player
                    if raytest_result:
                        if raytest_result.get_node():
                            direction = node_np.get_pos() - pivot.get_pos()
                            direction.normalize()
                            pos = raytest_result.getHitPos() + direction

                            if abs(round(pos[1])) > 2:
                                if not self._is_close:
                                    self._is_close = True
                            elif abs(round(pos[1])) > 4:
                                if not self._is_close:
                                    self._is_close = True
                            elif abs(round(pos[1])) < 4:
                                if self._is_close:
                                    self._is_close = False

                    if round(trigger_np.get_distance(node_np)) < 2:
                        if not self._is_close:
                            self._interpolate_to(target_y=close_y, start_y=def_y)
                        if self._is_close:
                            self._interpolate_to(target_y=def_y, start_y=close_y)
                    # We don't have colliding object, reverting camera view back
                    if round(trigger_np.get_distance(node_np)) > 1:
                        if self._is_close:
                            self._interpolate_to(target_y=def_y, start_y=close_y)
