from direct.task.TaskManagerGlobal import taskMgr
from panda3d.bullet import BulletSphereShape, BulletGhostNode
from panda3d.core import BitMask32


class PlayerCamera:

    def __init__(self):
        self.base = base
        self.render = render
        self.speed = 5
        self.trig_radius = 1.75 - 2 * 0.3

    def set_ghost_trigger(self, actor, world):
        if actor and world:
            sphere = BulletSphereShape(self.trig_radius)
            trigger_bg = BulletGhostNode('player_cam_trigger')
            trigger_bg.add_shape(sphere)
            trigger_np = self.render.attach_new_node(trigger_bg)
            trigger_np.set_collide_mask(BitMask32(0x0f))
            world.attach_ghost(trigger_bg)
            trigger_np.reparent_to(actor)
            trigger_np.set_pos(0, 0, 1)

            taskMgr.add(self.camera_smooth_zooming_task,
                        "camera_smooth_zooming_task",
                        extraArgs=[trigger_np, actor],
                        appendTask=True)

    def set_camera_trigger(self, task):
        if self.base.game_instance["loading_is_done"] == 1:
            if (self.render.find("**/World")
                    and self.base.game_instance["physics_world_np"]):
                ph_world = self.base.game_instance["physics_world_np"]
                player_bs = self.base.get_actor_bullet_shape_node(asset="Player", type="Player")

                self.set_ghost_trigger(actor=player_bs, world=ph_world)

                return task.done

        return task.cont

    def camera_smooth_zooming_task(self, trigger_np, player_bs, task):
        if self.base.game_instance['menu_mode']:
            self.base.camera.set_z(0.0)
            return task.done

        if not self.base.game_instance["ui_mode"]:
            if not self.base.game_instance['is_aiming']:
                dt = globalClock.getDt()
                trigger = player_bs.find("**/player_cam_trigger").node()
                if trigger:
                    for node in trigger.get_overlapping_nodes():
                        # Indoor triggering
                        if "indoor" in node.get_name():
                            node_np = render.find("**/{0}".format(node.get_name()))
                            if (round(trigger_np.get_distance(node_np)) >= 1
                                    and round(trigger_np.get_distance(node_np)) < 4):
                                if not self.base.game_instance["is_indoor"]:
                                    self.camera_smooth_zoom_in(dt=dt, speed=self.speed, y=-1)
                            elif (round(trigger_np.get_distance(node_np)) >= 4
                                  and round(trigger_np.get_distance(node_np)) < 7):
                                self.camera_smooth_zoom_out(dt=dt, speed=self.speed, y=-5)

                        # Regular triggering
                        elif ("Player" not in node.get_name()
                              and "Ground" not in node.get_name()
                              and "trigger" not in node.get_name()
                              and "HB" not in node.get_name()):
                            # if not self.base.game_instance["is_indoor"]:
                            node_np = render.find("**/{0}".format(node.get_name()))
                            pivot = player_bs.find("**/pivot")
                            print(round(trigger_np.get_distance(node_np)), node_np.get_name())
                            if round(trigger_np.get_distance(node_np)) <= 1:
                                if int(player_bs.get_h()) != int(pivot.get_h()):
                                    self.base.camera.set_y(-2)
                                else:
                                    self.base.camera.set_y(self.base.game_instance["mouse_y_cam"])
                            elif round(trigger_np.get_distance(node_np)) > 1:
                                self.base.camera.set_y(self.base.game_instance["mouse_y_cam"])

        return task.cont

    def camera_smooth_zoom_in(self, dt, speed, y):
        if dt and isinstance(speed, int):
            self.base.camera.set_x(0.3)
            if round(self.base.camera.get_y()) != y:
                self.base.camera.set_y(self.base.camera, speed * dt)
            elif round(self.base.camera.get_y()) == y:
                self.base.game_instance["is_indoor"] = True

    def camera_smooth_zoom_out(self, dt, speed, y):
        if dt and isinstance(speed, int):
            # revert camera view
            self.base.camera.set_x(0.0)
            if round(self.base.camera.get_y()) != y:
                self.base.camera.set_y(self.base.camera, -speed * dt)
            elif round(self.base.camera.get_y()) == y:
                self.base.camera.set_y(self.base.game_instance["mouse_y_cam"])
                self.base.game_instance["is_indoor"] = False
