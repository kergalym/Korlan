from direct.task.TaskManagerGlobal import taskMgr
from panda3d.bullet import BulletSphereShape, BulletGhostNode
from panda3d.core import BitMask32


class CameraModes:

    def __init__(self):
        self.base = base
        self.render = render
        self.is_at_home = False
        self.player_cam_y = 0.0

    def set_camera_trigger(self, scene, task):
        if self.base.game_instance["loading_is_done"] == 1:
            self.player_cam_y = self.base.camera.get_y()

            if (self.render.find("**/World")
                    and self.base.game_instance["physics_world_np"]):
                self.is_at_home = False
                world_np = self.render.find("**/World")
                ph_world = self.base.game_instance["physics_world_np"]
                radius = 1.75 - 2 * 0.3

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

                        taskMgr.add(self.camera_smooth_adjust_task,
                                    "camera_smooth_adjust_task",
                                    extraArgs=[trigger_np, actor],
                                    appendTask=True)

                        return task.done

        return task.cont

    def camera_smooth_adjust_task(self, trigger_np, actor, task):
        if self.base.game_instance['menu_mode']:
            return task.done

        dt = globalClock.getDt()
        for node in trigger_np.node().get_overlapping_nodes():
            if "Player" in node.get_name():
                player_bs = self.render.find("**/{0}".format(node.get_name()))
                if player_bs and int(actor.get_distance(player_bs)) == 1:
                    self.camera_smooth_close(dt)
                else:
                    self.camera_smooth_far(dt)

        return task.cont

    def camera_smooth_close(self, dt):
        if dt:
            y = -2
            z = -0.1
            if round(self.base.camera.get_y()) != y and not self.is_at_home:
                self.base.camera.set_y(self.base.camera, 1 * dt)
            if self.base.camera.get_z() != z and not self.is_at_home:
                # import pdb; pdb.set_trace()
                # self.base.camera.set_z(self.base.camera, -2 * dt)
                pass

            if self.base.camera.get_y() == y and self.base.camera.get_z() == z:
                if not self.is_at_home:
                    self.is_at_home = True

    def camera_smooth_far(self, dt):
        if dt:
            y = -5
            if round(self.base.camera.get_y()) != y and self.is_at_home:
                self.base.camera.set_y(self.base.camera, -1 * dt)
            if self.base.camera.get_z() != 0.0 and self.is_at_home:
                self.base.camera.set_z(self.base.camera, 1 * dt)

            if self.base.camera.get_y() == y and self.base.camera.get_z() == 0.0:
                self.base.camera.set_y(self.player_cam_y)
                if self.is_at_home:
                    self.is_at_home = False
