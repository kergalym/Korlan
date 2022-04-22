from direct.gui.OnscreenText import OnscreenText
from direct.task.TaskManagerGlobal import taskMgr
from panda3d.bullet import BulletRigidBodyNode, BulletBoxShape
from panda3d.core import BitMask32, NodePath, Vec3, TextNode, Point3


class Archery:
    def __init__(self, actor):
        self.game_settings = base.game_settings
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
        self.aim = None

        if actor == "Player":
            from Settings.Input.aim import Aim
            self.aim = Aim()

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
                arrow.set_pos(-7, 7, -10)
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
                    # Remove arrow from inv and prepare it for use
                    arrow = self.arrows.pop(0)
                    arrow.reparent_to(bow)
                    arrow.set_pos(0.04, -0.01, -0.01)
                    arrow.set_hpr(0, 2.86, 0)
                    arrow.set_scale(1)

                    # Create arrow collider
                    shape = BulletBoxShape(Vec3(0.05, 0.05, 0.05))
                    body = BulletRigidBodyNode('Arrow_BRB')
                    arrow_rb_np = NodePath(body)
                    arrow_rb_np.wrt_reparent_to(bow)
                    arrow_rb_np.set_pos(-0.16, -0.01, -0.02)
                    arrow_rb_np.set_hpr(arrow.get_hpr())
                    arrow_rb_np.set_scale(arrow.get_scale())
                    arrow.wrt_reparent_to(arrow_rb_np)
                    arrow_rb_np.node().add_shape(shape)
                    arrow_rb_np.node().set_mass(2.0)

                    # Player and its owning arrow won't collide with each other
                    arrow_rb_np.set_collide_mask(BitMask32.bit(0))

                    # Enable CCD
                    arrow_rb_np.node().set_ccd_motion_threshold(1e-7)
                    arrow_rb_np.node().set_ccd_swept_sphere_radius(0.50)
                    arrow_rb_np.node().set_kinematic(True)

                    self.base.game_instance['physics_world_np'].attach_rigid_body(arrow_rb_np.node())

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
            taskMgr.do_method_later(700, self.destroy_arrow, 'destroy_arrow')

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
                pos_from = Point3(0, 0, 0)
                pos_to = Point3(0, 1000, 0)
                base.camLens.extrude(pos_mouse, pos_from, pos_to)

                pos_from = self.render.get_relative_point(base.camera, pos_from)
                pos_to = self.render.get_relative_point(base.camera, pos_to)

                self.raytest_result = self.base.game_instance['physics_world_np'].ray_test_closest(pos_from, pos_to)

        return task.cont

    def arrow_hit_check_task(self, task):
        """ Function    : arrow_hit_check_task

            Description : Task checking for arrow hits.

            Input       : None

            Output      : None

            Return      : Task status
        """

        if (self.raytest_result and self.raytest_result.get_node()
                and "Player" not in self.raytest_result.get_node().get_name()
                and "Arrow" not in self.raytest_result.get_node().get_name()):
            self.hit_target = self.raytest_result.get_node()
            self.target_pos = self.raytest_result.get_hit_pos()
            hit_target_name = self.hit_target.get_name()
            hit_target_name = hit_target_name.split("_trigger")[0]

            self.target_test_ui.show()
            self.target_test_ui.setText(self.hit_target.get_name())

            # Show NPC HUD
            if self.hit_target and "NPC" in self.hit_target.get_name():
                if self.base.game_instance['hud_np']:
                    if (self.base.game_instance['actors_ref']
                            and self.base.game_instance['actors_ref'].get(hit_target_name)):
                        actor = self.base.game_instance['actors_ref'][hit_target_name]
                        actor.get_python_tag("npc_hud_np").show()

            if self.base.game_instance['physics_world_np'] and self.arrow_brb_in_use:
                # contact_result = self.base.game_instance['physics_world_np'].contact_test(self.hit_target)

                self.pierce_arrow()

                # Hide NPC HUD
                if (self.base.game_instance['actors_ref']
                        and self.base.game_instance['actors_ref'].get(hit_target_name)):
                    actor = self.base.game_instance['actors_ref'][hit_target_name]
                    actor.get_python_tag("npc_hud_np").hide()

                """for contact in contact_result.get_contacts():
                    mpoint = contact.get_manifold_point()
                    if round(mpoint.get_distance()) == 0.0:
                        # Attach Arrow
                        self.pierce_arrow()

                        # Hide NPC HUD
                        if (self.base.game_instance['actors_ref']
                                and self.base.game_instance['actors_ref'].get(hit_target_name)):
                            actor = self.base.game_instance['actors_ref'][hit_target_name]
                            actor.get_python_tag("npc_hud_np").hide()
                """

        return task.cont

    def pierce_arrow(self):
        if self.arrow_ref and self.arrow_brb_in_use:
            if self.arrow_ref.get_python_tag("ready") == 1:

                name = self.hit_target.get_name()
                self.target_np = render.find("**/{0}".format(name))

                if self.target_np:
                    distance = round(self.arrow_brb_in_use.get_distance(self.target_np), 1)
                    if distance >= 0.8 and distance <= 1.1:
                        self.arrow_brb_in_use.set_collide_mask(BitMask32.allOff())
                        self.arrow_ref.wrt_reparent_to(self.target_np)
                        self.base.game_instance["is_arrow_ready"] = False
                        # self.arrow_brb_in_use.node().set_kinematic(True)
                        self.arrow_ref.set_python_tag("ready", 0)
                        self.reset_arrow_charge()

            else:
                if self.base.game_instance["is_arrow_ready"]:
                    self.arrow_ref.remove_node()

    def reset_arrow_charge(self):
        if self.arrow_brb_in_use:
            self.arrow_ref.set_python_tag("power", 0)

    def destroy_arrow(self, task):
        if len(self.arrows) < 1:
            return False

        if self.base.game_instance['physics_world_np'] and self.dropped_arrows:
            for arrow_rb in self.dropped_arrows:
                if arrow_rb:
                    self.base.game_instance['physics_world_np'].remove_rigid_body(arrow_rb.node())
                    arrow_rb.remove_node()
            return task.done

        return task.cont

    def arrow_fly_task(self, task):
        dt = globalClock.getDt()
        if self.arrow_brb_in_use:
            # power = self.arrow_ref.get_python_tag("power")
            power = 10
            if self.arrow_ref.get_python_tag("ready") == 1:

                self.base.game_instance["is_arrow_ready"] = True

                self.arrow_brb_in_use.set_x(self.arrow_brb_in_use, -power * dt)
                self.base.camera.set_y(self.base.camera, power * dt)
                self.base.camera.set_z(self.arrow_brb_in_use.get_z())

        return task.cont

    def archery_cooldown_task(self, task):
        if self.base.game_instance['menu_mode']:
            self.is_ready_for_cooldown = False
            return task.done

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

        if self.aim:
            taskMgr.add(self.aim.aim_state_task, "aim_state_task")

        self.base.game_instance['hud_np'].set_arrow_charge_ui()

        self.base.game_instance['hud_np'].set_cooldown_bar_ui()

    def stop_archery_helper_tasks(self):
        taskMgr.remove("calculate_arrow_trajectory_task")
        taskMgr.remove("arrow_hit_check_task")
        taskMgr.remove("arrow_fly_task")

        if self.aim:
            taskMgr.remove("aim_state_task")

        self.base.game_instance['hud_np'].clear_arrow_charge_ui()

        taskMgr.remove("archery_cooldown_task")
        self.base.game_instance['hud_np'].clear_cooldown_bar_ui()
