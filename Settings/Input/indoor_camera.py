from direct.task.TaskManagerGlobal import taskMgr
from panda3d.bullet import BulletSphereShape, BulletGhostNode
from panda3d.core import BitMask32


class IndoorCamera:

    def __init__(self):
        self.base = base
        self.render = render
        self.is_at_home = False
        self.base.game_instance["is_indoor"] = self.is_at_home
        self.player_cam_y = 0.0
        self.speed = 5

    def set_camera_trigger(self, scene, task):
        if self.base.game_instance["loading_is_done"] == 1:
            self.player_cam_y = self.base.camera.get_y()

            if (self.render.find("**/World")
                    and self.base.game_instance["physics_world_np"]):
                self.is_at_home = False
                self.base.game_instance["is_indoor"] = self.is_at_home
                world_np = self.render.find("**/World")
                ph_world = self.base.game_instance["physics_world_np"]
                # radius = 1.75 - 2 * 0.3
                radius = 4

                player_bs = self.base.get_actor_bullet_shape_node(asset="Player", type="Player")

                for actor in scene.get_children():
                    if "cam_close" in actor.get_name():  # cam_close
                        sphere = BulletSphereShape(radius)
                        trigger_bg = BulletGhostNode('{0}_trigger'.format(actor.get_name()))
                        trigger_bg.add_shape(sphere)
                        trigger_np = world_np.attach_new_node(trigger_bg)
                        trigger_np.set_collide_mask(BitMask32(0x0f))
                        ph_world.attach_ghost(trigger_bg)
                        trigger_np.reparent_to(actor)
                        trigger_np.set_pos(0, 0, 1)

                        taskMgr.add(self.camera_smooth_zooming_task,
                                    "camera_smooth_zooming_task",
                                    extraArgs=[actor, player_bs, radius],
                                    appendTask=True)

                        return task.done

        return task.cont

    def camera_smooth_zooming_task(self, actor, player_bs, radius, task):
        if self.base.game_instance['menu_mode']:
            self.base.camera.set_z(0.0)
            return task.done

        dt = globalClock.getDt()
        radius += 1
        if not self.base.game_instance["ui_mode"]:
            if (round(actor.get_distance(player_bs)) >= 1
                    and round(actor.get_distance(player_bs)) < radius):
                self.base.game_instance["is_indoor"] = True
                self.camera_smooth_zoom_in(dt=dt, speed=self.speed)

                # TODO: Refactoring
                """if (self.base.game_instance["is_player_sitting"]
                        or self.base.game_instance["is_player_laying"]):
                    self.camera_smooth_move_down(dt=dt, speed=self.speed)
                else:
                    self.camera_smooth_move_up(dt=dt, speed=self.speed)"""

            elif (round(actor.get_distance(player_bs)) >= radius
                    and round(actor.get_distance(player_bs)) < 7):
                self.base.game_instance["is_indoor"] = False
                self.camera_smooth_zoom_out(dt=dt, speed=self.speed)

        return task.cont

    def camera_smooth_zoom_in(self, dt, speed):
        if dt and isinstance(speed, int):
            y = -1

            self.base.camera.set_x(0.3)

            if (round(self.base.camera.get_y()) != y
                    and not self.is_at_home):
                self.base.camera.set_y(self.base.camera, speed * dt)

            elif round(self.base.camera.get_y()) == y:
                if not self.is_at_home:
                    self.is_at_home = True

    def camera_smooth_zoom_out(self, dt, speed):
        if dt and isinstance(speed, int):
            y = -5
            # revert camera view
            self.base.camera.set_x(0.0)

            if (round(self.base.camera.get_y()) != y
                    and self.is_at_home):
                self.base.camera.set_y(self.base.camera, -speed * dt)

            elif round(self.base.camera.get_y()) == y:
                self.base.camera.set_y(self.player_cam_y)
                if self.is_at_home:
                    self.is_at_home = False

            if not self.base.game_instance["is_player_sitting"]:
                self.base.camera.set_z(0.0)

    def camera_smooth_move_up(self, dt, speed):
        if round(self.base.camera.get_z(), 1) != 0.0:
            self.base.camera.set_z(self.base.camera, speed * dt)

    def camera_smooth_move_down(self, dt, speed):
        z = -0.5
        if round(self.base.camera.get_z(), 1) != z:
            self.base.camera.set_z(self.base.camera, -speed * dt)

