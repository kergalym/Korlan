from direct.gui.OnscreenText import OnscreenText
from direct.task.TaskManagerGlobal import taskMgr
from panda3d.bullet import BulletRigidBodyNode, BulletBoxShape, BulletGhostNode
from panda3d.core import BitMask32, NodePath, Vec3, TextNode, Point3


class Archery:
    def __init__(self):
        self.base = base
        self.render = render
        self.arrow_ref = None
        self.arrows = []
        self.dropped_arrows = []
        self.arrow_ref = None
        self.arrow_brb_in_use = None
        self.arrow_is_prepared = False
        self.arrow_charge_units = 100
        self.arrow_brb_in_use = None
        self.draw_bow_is_done = 0
        self.raytest_result = None
        self.hit_target = None
        self.is_ready_for_cooldown = False
        self.target_pos = None
        self.target_np = None
        self.base.game_instance['is_aiming'] = False

        self.target_test_ui = OnscreenText(text="",
                                           pos=(1.5, 0.8),
                                           scale=0.05,
                                           fg=(255, 255, 255, 0.9),
                                           align=TextNode.ALeft,
                                           mayChange=True)

    async def prepare_arrows_helper(self, arrow_name, joint_name):
        if (self.base.game_instance['player_ref']
                and arrow_name
                and joint_name
                and isinstance(arrow_name, str)
                and isinstance(joint_name, str)):
            self.arrows = []
            assets = self.base.assets_collector()
            joint = self.base.game_instance['player_ref'].expose_joint(None, "modelRoot", joint_name)
            for i in range(self.base.game_instance['arrow_count']):
                arrow = await self.base.loader.load_model(assets[arrow_name], blocking=False)
                arrow.set_name(arrow_name)
                arrow.reparent_to(joint)
                arrow.set_pos(-10, 7, -12)
                arrow.set_hpr(91.55, 0, 0)
                arrow.set_scale(100)

                arrow.set_python_tag("power", 0)
                arrow.set_python_tag("ready", 0)
                arrow.set_python_tag("shot", 0)
                arrow.set_python_tag("owner", "player")
                self.arrows.append(arrow)

    def return_arrow_back(self, joint_name):
        if self.arrow_ref and joint_name:
            if self.arrow_ref.get_python_tag("ready") == 0:
                joint = self.base.game_instance['player_ref'].exposeJoint(None, "modelRoot", joint_name)
                if joint:
                    self.arrow_ref.reparent_to(joint)
                    self.arrow_ref.set_pos(-10, 7, -12)
                    self.arrow_ref.set_hpr(91.55, 0, 0)
                    self.arrow_ref.set_scale(100)

                    self.arrow_ref.set_python_tag("power", 0)
                    self.arrow_ref.set_python_tag("ready", 0)
                    self.arrow_ref.set_python_tag("shot", 0)
                    self.arrows.append(self.arrow_ref)

        if self.base.game_instance['physics_world_np'] and self.arrow_brb_in_use:
            self.base.game_instance['physics_world_np'].remove_rigid_body(self.arrow_brb_in_use.node())
            self.arrow_brb_in_use.remove_node()

    def prepare_arrow_for_shoot(self, bow_name):
        if self.arrow_is_prepared:
            return False

        elif not self.arrow_is_prepared:
            bow = render.find("**/{0}".format(bow_name))
            if bow:
                if len(self.arrows) < 1:
                    return False

                if self.base.game_instance['physics_world_np']:
                    # Remove arrow from inventory and prepare it for use
                    arrow = self.arrows.pop(0)
                    arrow.reparent_to(bow)
                    arrow.set_pos(0.04, -0.01, -0.01)
                    arrow.set_hpr(0, 2.86, 0)
                    arrow.set_scale(1)

                    # Create arrow collider
                    shape = BulletBoxShape(Vec3(0.05, 0.05, 0.05))
                    body = BulletGhostNode('Arrow_BRB')
                    # body = BulletRigidBodyNode('Arrow_BRB')
                    arrow_rb_np = NodePath(body)
                    arrow_rb_np.wrt_reparent_to(bow)
                    arrow_rb_np.set_pos(-0.16, -0.01, -0.02)
                    arrow_rb_np.set_hpr(arrow.get_hpr())
                    arrow_rb_np.set_scale(arrow.get_scale())
                    arrow.wrt_reparent_to(arrow_rb_np)
                    arrow_rb_np.node().add_shape(shape)
                    # arrow_rb_np.node().set_mass(2.0)

                    # Player and its owning arrow won't collide with each other
                    arrow_rb_np.set_collide_mask(BitMask32.bit(0x0f))
                    # arrow_rb_np.set_collide_mask(BitMask32.allOff())

                    # Enable CCD
                    arrow_rb_np.node().set_ccd_motion_threshold(1e-7)
                    arrow_rb_np.node().set_ccd_swept_sphere_radius(0.50)
                    arrow_rb_np.node().set_kinematic(True)

                    self.base.game_instance['physics_world_np'].attach_ghost(arrow_rb_np.node())
                    # self.base.game_instance['physics_world_np'].attach_rigid_body(arrow_rb_np.node())

                    self.arrow_brb_in_use = arrow_rb_np
                    self.arrow_ref = arrow
                    self.arrow_is_prepared = True

    def bow_shoot(self):
        if (self.arrow_brb_in_use
                and self.arrow_ref):
            # Calculate initial velocity
            # velocity = self.target_pos - self.arrow_brb_in_use.get_pos()
            # velocity = self.target_pos - self.bow.get_pos()
            # velocity.normalize()
            # velocity *= 100.0

            # Get Bullet Rigid Body wrapped arrow
            self.arrow_brb_in_use.node().set_kinematic(False)
            self.arrow_ref.set_python_tag("shot", 1)
            self.arrow_brb_in_use.wrt_reparent_to(render)

            # self.arrow_brb_in_use.node().setLinearVelocity(velocity)

            # We record arrows which have been shot
            self.dropped_arrows.append(self.arrow_brb_in_use)
            if self.base.game_instance['arrow_count'] > 0:
                self.base.game_instance['arrow_count'] -= 1

            self.arrow_is_prepared = False

            self.base.game_instance['hud_np'].cooldown_bar_ui['value'] = 100
            taskMgr.do_method_later(0.1, self.archery_cooldown_task, "archery_cooldown_task")

            # Destroy dropped arrows after 200 seconds which are 3 minutes
            taskMgr.do_method_later(600, self.destroy_arrow, 'destroy_arrow')

    def calculate_arrow_trajectory_task(self, task):
        """ Function    : calculate_arrow_trajectory_task

            Description : Task calculating arrow trajectory.

            Input       : None

            Output      : None

            Return      : Task status
        """
        if self.base.game_instance['physics_world_np']:
            mouse_watch = base.mouseWatcherNode
            if mouse_watch.has_mouse():
                pos_mouse = base.mouseWatcherNode.get_mouse()
                pos_from = Point3()
                pos_to = Point3()
                base.camLens.extrude(pos_mouse, pos_from, pos_to)

                pos_from = self.render.get_relative_point(base.camera, pos_from)
                pos_to = self.render.get_relative_point(base.camera, pos_to)

                self.raytest_result = self.base.game_instance['physics_world_np'].ray_test_all(pos_from, pos_to)
                for ray in self.raytest_result.get_hits():
                    if ("Player" not in ray.get_node().get_name()
                            and "Arrow" not in ray.get_node().get_name()):
                        self.hit_target = ray.get_node()
                        name = ray.get_node().get_name()
                        self.target_np = render.find("**/{0}".format(name))
        return task.cont

    def arrow_hit_check_task(self, task):
        """ Function    : arrow_hit_check_task

            Description : Task checking for arrow hits.

            Input       : None

            Output      : None

            Return      : Task status
        """
        if self.hit_target:
            # hit_target_name = self.hit_target.get_name()
            # hit_target_name = hit_target_name.split("_trigger")[0]

            # Toggle hit target hud if it's NPC
            """
            if "NPC" in self.hit_target.get_name():
                if self.base.game_instance['hud_np']:
                    if (self.base.game_instance['actors_ref']
                            and self.base.game_instance['actors_ref'].get(hit_target_name)):
                        actor = self.base.game_instance['actors_ref'][hit_target_name]
                        actor.get_python_tag("npc_hud_np").show()
            else:
                if (self.base.game_instance['actors_ref']
                        and self.base.game_instance['actors_ref'].get(hit_target_name)):
                    actor = self.base.game_instance['actors_ref'][hit_target_name]
                    actor.get_python_tag("npc_hud_np").hide()
            """

            # Contact test
            if self.arrow_brb_in_use:
                # contact_result = self.base.game_instance['physics_world_np'].contact_test(self.hit_target)

                # Show contacted object
                self.target_test_ui.show()
                self.target_test_ui.setText(self.hit_target.get_name())

                # Get Nodepath from hit target
                name = self.hit_target.get_name()
                self.target_np = render.find("**/{0}".format(name))

                """if (contact_result.get_num_contacts() > 0
                        and contact_result.get_num_contacts() < 2):
                    # self.arrow_brb_in_use.set_collide_mask(BitMask32.allOff())
                    self.attach_arrow()
                """

                for node in self.arrow_brb_in_use.node().get_overlapping_nodes():
                    if node:
                        if ("Player" not in node.get_name()
                                and "Arrow" not in node.get_name()):
                            if self.target_np.get_name() == node.get_name():
                                self.attach_arrow()
                            else:
                                name = node.get_name()
                                node_np = render.find("**/{0}".format(name))
                                if node_np:
                                    if (round(node_np.get_distance(self.arrow_brb_in_use), 1) > 0.1
                                            and round(node_np.get_distance(self.arrow_brb_in_use), 1) < 0.9):
                                        self.attach_arrow()
        return task.cont

    def attach_arrow(self):
        if self.arrow_ref and self.arrow_brb_in_use:
            if self.arrow_ref.get_python_tag("ready") == 1:
                if self.target_np:
                    self.arrow_brb_in_use.wrt_reparent_to(self.target_np)
                    # self.arrow_brb_in_use.node().set_kinematic(True)
                    self.arrow_ref.set_python_tag("ready", 0)
                    self.reset_arrow_charge()

    def reset_arrow_charge(self):
        if self.arrow_brb_in_use:
            self.arrow_ref.set_python_tag("power", 0)

    def destroy_arrow(self, task):
        if len(self.arrows) < 1:
            return False

        if self.base.game_instance['physics_world_np'] and self.dropped_arrows:
            for arrow_rb in self.dropped_arrows:
                if arrow_rb:
                    self.base.game_instance['physics_world_np'].remove_ghost(arrow_rb.node())
                    # self.base.game_instance['physics_world_np'].remove_rigid_body(arrow_rb.node())

                    arrow_rb.remove_node()
            return task.done

        return task.cont

    def arrow_fly_task(self, task):
        dt = globalClock.getDt()
        if self.arrow_brb_in_use:
            power = self.arrow_ref.get_python_tag("power")
            if self.arrow_ref.get_python_tag("ready") == 1:
                self.arrow_brb_in_use.set_x(self.arrow_brb_in_use, -power * dt)
            print(self.arrow_ref.get_python_tag("ready"))
        return task.cont

    def cursor_state_task(self, task):
        if self.base.game_instance['menu_mode']:
            return task.done

        if (base.player_states['has_bow']
                and not self.base.game_instance["is_indoor"]
                and not self.base.game_instance['ui_mode']):
            if (self.base.game_instance['kbd_np'].keymap["block"]
                    and self.base.game_instance['kbd_np'].keymap["attack"]):
                if self.base.game_instance['cursor_ui']:
                    self.base.game_instance['cursor_ui'].show()
                if not self.base.game_instance['is_aiming']:
                    self.base.game_instance['is_aiming'] = True
                if (self.base.game_instance['player_ref'].get_python_tag("is_on_horse")
                        and self.base.game_instance['is_aiming']
                        and not self.base.game_instance['free_camera']):
                    pos_y = -4.2
                    pos_z = 0.25
                else:
                    pos_y = -2
                    pos_z = -0.2
                base.camera.set_x(0.5)
                base.camera.set_y(pos_y)
                base.camera.set_z(pos_z)

            elif (self.base.game_instance['kbd_np'].keymap["block"]
                  and not self.base.game_instance['kbd_np'].keymap["attack"]):
                if self.base.game_instance['cursor_ui']:
                    self.base.game_instance['cursor_ui'].show()
                if not self.base.game_instance['is_aiming']:
                    self.base.game_instance['is_aiming'] = True
                if (self.base.game_instance['player_ref'].get_python_tag("is_on_horse")
                        and self.base.game_instance['is_aiming']
                        and not self.base.game_instance['free_camera']):
                    pos_y = -4.2
                    pos_z = 0.25
                else:
                    pos_y = -2
                    pos_z = -0.2
                base.camera.set_x(0.5)

                base.camera.set_y(pos_y)
                base.camera.set_z(pos_z)

            elif (not self.base.game_instance['kbd_np'].keymap["block"]
                  and not self.base.game_instance['kbd_np'].keymap["attack"]):
                if self.base.game_instance['cursor_ui']:
                    self.base.game_instance['cursor_ui'].hide()
                base.camera.set_x(0)
                base.camera.set_y(self.base.game_instance["mouse_y_cam"])
                if self.base.game_instance['player_ref'].get_python_tag("is_on_horse"):
                    base.camera.set_z(0.5)
                elif not self.base.game_instance['player_ref'].get_python_tag("is_on_horse"):
                    base.camera.set_z(0)
                if self.base.game_instance['is_aiming']:
                    self.base.game_instance['is_aiming'] = False

        return task.cont

    def archery_cooldown_task(self, task):
        if self.base.game_instance['menu_mode']:
            self.is_ready_for_cooldown = False
            return task.done

        dt = globalClock.getDt()
        seconds = int(60 * round(dt, 1))
        cooldown_bar = self.base.game_instance['hud_np'].cooldown_bar_ui
        if cooldown_bar.is_hidden():
            cooldown_bar.show()

        if cooldown_bar['value'] > 0:
            cooldown_bar['value'] -= 1
        else:
            if self.is_ready_for_cooldown:
                self.is_ready_for_cooldown = False
            if not cooldown_bar.is_hidden():
                cooldown_bar.hide()

        return task.cont

    def start_archery_helper_tasks(self):
        taskMgr.add(self.calculate_arrow_trajectory_task, "calculate_arrow_trajectory_task")
        taskMgr.add(self.arrow_hit_check_task, "arrow_hit_check_task")
        taskMgr.add(self.arrow_fly_task, "arrow_fly_task")
        taskMgr.add(self.cursor_state_task, "cursor_state_task")

        self.base.game_instance['hud_np'].set_arrow_charge_ui()

        self.base.game_instance['hud_np'].set_cooldown_bar_ui()

    def stop_archery_helper_tasks(self):
        taskMgr.remove("calculate_arrow_trajectory_task")
        taskMgr.remove("arrow_hit_check_task")
        taskMgr.remove("arrow_fly_task")
        taskMgr.remove("cursor_state_task")

        self.base.game_instance['hud_np'].clear_arrow_charge_ui()

        taskMgr.remove("archery_cooldown_task")
        self.base.game_instance['hud_np'].clear_cooldown_bar_ui()
