from direct.task.TaskManagerGlobal import taskMgr
from panda3d.bullet import BulletSphereShape, BulletGhostNode
from panda3d.core import BitMask32


class OutdoorCamera:

    def __init__(self):
        self.base = base
        self.render = render
        self.player_cam_y = 0.0
        self.speed = 5
        self.sm_zoom_in = False
        self.sm_zoom_out = False
        self.sm_zoom_up = False
        self.sm_zoom_down = False

    def add_cam_zoomin_task(self):
        taskMgr.add(self.camera_smooth_zoomin_task,
                    "camera_smooth_zoomin_task")

    def remove_cam_zoom_out_task(self):
        taskMgr.remove("camera_smooth_zoomin_task")

    def camera_smooth_zoomin_task(self, task):
        if self.base.game_instance['menu_mode']:
            self.base.camera.set_z(0.0)
            self.sm_zoom_in = False
            self.sm_zoom_out = False
            self.sm_zoom_up = False
            self.sm_zoom_down = False
            return task.done

        dt = globalClock.getDt()
        if not self.base.game_instance["ui_mode"]:
            if self.sm_zoom_in:
                self.camera_smooth_zoom_in(dt=dt, speed=self.speed)
            elif self.sm_zoom_out:
                self.camera_smooth_zoom_out(dt=dt, speed=self.speed)

            if self.sm_zoom_up:
                self.camera_smooth_move_down(dt=dt, speed=self.speed)
            elif self.sm_zoom_down:
                self.camera_smooth_move_up(dt=dt, speed=self.speed)

        return task.cont

    def camera_smooth_zoom_in(self, dt, speed):
        if dt and isinstance(speed, int):
            y = -1

            self.base.camera.set_x(0.3)

            if (round(self.base.camera.get_y()) != y
                    and self.sm_zoom_in):
                self.base.camera.set_y(self.base.camera, speed * dt)

            elif round(self.base.camera.get_y()) == y:
                if self.sm_zoom_in:
                    self.sm_zoom_in = False

    def camera_smooth_zoom_out(self, dt, speed):
        if dt and isinstance(speed, int):
            y = -5
            # revert camera view
            self.base.camera.set_x(0.0)

            if (round(self.base.camera.get_y()) != y
                    and self.sm_zoom_out):
                self.base.camera.set_y(self.base.camera, -speed * dt)

            elif round(self.base.camera.get_y()) == y:
                self.base.camera.set_y(self.player_cam_y)
                if self.sm_zoom_out:
                    self.sm_zoom_out = False

    def camera_smooth_move_up(self, dt, speed):
        z = 0.5
        if round(self.base.camera.get_z(), 1) != z:
            self.base.camera.set_z(self.base.camera, speed * dt)
        else:
            if self.sm_zoom_up:
                self.sm_zoom_up = False

    def camera_smooth_move_down(self, dt, speed):
        z = 0.0
        if round(self.base.camera.get_z(), 1) != z:
            self.base.camera.set_z(self.base.camera, -speed * dt)
        else:
            if self.sm_zoom_down:
                self.sm_zoom_down = False

