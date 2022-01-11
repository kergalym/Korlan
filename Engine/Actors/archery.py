from direct.gui.OnscreenText import OnscreenText
from direct.interval.FunctionInterval import Func, Wait
from direct.interval.MetaInterval import Sequence
from direct.task.TaskManagerGlobal import taskMgr
from panda3d.bullet import BulletRigidBodyNode, BulletBoxShape
from panda3d.core import BitMask32, NodePath, Vec3, TextNode, Point3


class Archery:
    def __init__(self, world, keymap, actor, bow_name, arrow_name, arrow_count, joint_name):
        self.base = base
        self.render = render
        self.world = world
        self.key_map = keymap
        self.actor = actor
        self.joint_name = joint_name
        self.bow = render.find("**/{0}".format(bow_name))
        self.arrow_name = arrow_name
        self.arrow_ref = None
        self.arrows = []
        self.dropped_arrows = []
        self.arrow_count = arrow_count
        self.arrow_brb_in_use = None
        self.draw_bow_is_done = 0
        self.raytest_result = None
        self.hit_target = None
        self.target_pos = None
        self.target_np = None
        self.target_test_ui = OnscreenText(text="",
                                           pos=(-1.8, 0.8),
                                           scale=0.03,
                                           fg=(255, 255, 255, 0.9),
                                           align=TextNode.ALeft,
                                           mayChange=True)

    def start(self):
        taskMgr.add(self.calculate_arrow_trajectory_task, "calculate_arrow_trajectory_task")
        taskMgr.add(self.arrow_hit_check_task, "arrow_hit_check_task")
        taskMgr.add(self.charge_arrow_task, "charge_arrow_task")
        taskMgr.add(self.arrow_fly_task, "arrow_fly_task")
        bow_name = self.bow.get_name()
        taskMgr.add(self.prepare_arrows(bow_name, self.arrow_name))

    def stop(self):
        taskMgr.remove("calculate_arrow_trajectory_task")
        taskMgr.remove("arrow_hit_check_task")
        taskMgr.remove("charge_arrow_task")
        taskMgr.remove("arrow_fly_task")

    def draw_bow_anim_state(self, state, loop):
        if self.actor and isinstance(state, str) and isinstance(loop, int):
            stateControl = self.actor.getAnimControl(state)
            if stateControl and not stateControl.isPlaying():
                if self.draw_bow_is_done == 0:
                    # self.prepare_arrow_for_shoot(self.bow)
                    self.actor.play(state)
                    self.draw_bow_is_done = 1

    async def prepare_arrows(self, bow_name, arrow_name):
        if (self.actor
                and bow_name
                and arrow_name
                and isinstance(bow_name, str)
                and isinstance(arrow_name, str)):
            assets = self.base.assets_collector()
            joint = self.actor.expose_joint(None, "modelRoot", self.joint_name)
            for i in range(self.arrow_count):
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

    def return_arrow_back(self, joint):
        if self.arrow_ref and joint:
            if self.arrow_ref.get_python_tag("ready") == 0:
                self.arrow_ref.reparent_to(joint)
                self.arrow_ref.set_pos(-10, 7, -12)
                self.arrow_ref.set_hpr(91.55, 0, 0)
                self.arrow_ref.set_scale(100)

                self.arrow_ref.set_python_tag("power", 0)
                self.arrow_ref.set_python_tag("ready", 0)
                self.arrow_ref.set_python_tag("shot", 0)
                self.arrows.append(self.arrow_ref)

        if self.arrow_brb_in_use:
            self.world.remove_rigid_body(self.arrow_brb_in_use.node())
            self.arrow_brb_in_use.remove_node()

    def prepare_arrow_for_shoot(self, bow):
        if bow:
            if len(self.arrows) < 1:
                return

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

            self.world.attach_rigid_body(arrow_rb_np.node())

            self.arrow_brb_in_use = arrow_rb_np
            self.arrow_ref = arrow

    def charge_arrow_task(self, task):
        if base.player_states['has_bow'] and self.arrow_brb_in_use:
            if (self.key_map["attack"]
                    and self.key_map["block"]):
                power = self.arrow_ref.get_python_tag("block")
                power += 1
                self.arrow_ref.set_python_tag("power", power)
            if not self.key_map["attack"] and self.key_map["block"]:
                if self.arrow_brb_in_use and self.arrow_ref.get_python_tag("ready") == 0:
                    if self.arrow_ref.get_python_tag("shot") == 0:
                        if self.arrow_ref.get_python_tag("power") > 100:
                            self.arrow_ref.set_python_tag("ready", 1)
                            self.bow_shoot()

            if (not self.key_map["attack"]
                    and not self.key_map["block"]):
                if self.draw_bow_is_done == 1:
                    self.draw_bow_is_done = 0
                    self.actor.stop("draw_bow")

        return task.cont

    def bow_shoot(self):
        if self.arrow_brb_in_use and self.target_pos and self.hit_target:
            name = self.hit_target.get_name()
            self.target_np = render.find("**/{0}".format(name))

            self.arrow_ref.set_python_tag("shot", 1)

            # Calculate initial velocity
            # velocity = self.target_pos - self.arrow_brb_in_use.get_pos()
            # velocity = self.target_pos - self.bow.get_pos()
            # velocity.normalize()
            # velocity *= 100.0

            # Get Bullet Rigid Body wrapped arrow
            self.arrow_brb_in_use.node().set_kinematic(False)
            self.arrow_brb_in_use.wrt_reparent_to(render)

            # self.arrow_brb_in_use.node().setLinearVelocity(velocity)

            # We record arrows which have been shot
            self.dropped_arrows.append(self.arrow_brb_in_use)
            if self.base.game_instance['arrow_count'] > 0:
                self.base.game_instance['arrow_count'] -= 1

            Sequence(Wait(1), Func(self.prepare_arrow_for_shoot, self.bow)).start()

            # Destroy dropped arrows after 200 seconds which are 3 minutes
            taskMgr.do_method_later(200, self.destroy_arrow, 'destroy_arrow')

    def arrow_fly_task(self, task):
        dt = globalClock.getDt()
        if self.arrow_brb_in_use:
            power = self.arrow_ref.get_python_tag("power")
            if power and self.arrow_ref.get_python_tag("shot") == 1:
                self.arrow_brb_in_use.set_x(self.arrow_brb_in_use, -power * dt)
                # pass

        return task.cont

    def calculate_arrow_trajectory_task(self, task):
        """ Function    : calculate_arrow_trajectory_task

            Description : Task calculating arrow trajectory.

            Input       : None

            Output      : None

            Return      : Task status
        """
        mouse_watch = base.mouseWatcherNode
        if mouse_watch.has_mouse():
            pos_mouse = base.mouseWatcherNode.get_mouse()
            pos_from = Point3()
            pos_to = Point3()
            base.camLens.extrude(pos_mouse, pos_from, pos_to)

            pos_from = self.render.get_relative_point(base.camera, pos_from)
            pos_to = self.render.get_relative_point(base.camera, pos_to)

            if self.world:
                self.raytest_result = self.world.ray_test_closest(pos_from, pos_to)

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

            if self.hit_target:
                self.target_test_ui.setText(self.hit_target.get_name())
            else:
                self.target_test_ui.setText("")

            if self.world and self.arrow_brb_in_use:
                self.world.contactTest(self.hit_target)
                if self.world.contactTest(self.hit_target).getNumContacts() > 0:
                    if self.arrow_ref.get_python_tag("ready") == 1:
                        if self.target_np:
                            self.arrow_brb_in_use.set_collide_mask(BitMask32.allOff())
                            self.arrow_brb_in_use.wrt_reparent_to(self.target_np)
                            # self.arrow_brb_in_use.node().set_kinematic(True)
                            self.arrow_ref.set_python_tag("ready", 0)
                            self.reset_arrow_charge()

        return task.cont

    def reset_arrow_charge(self):
        if self.arrow_brb_in_use:
            self.arrow_ref.set_python_tag("power", 0)

    def destroy_arrow(self, task):
        if len(self.arrows) < 1:
            return
        if self.dropped_arrows:
            for arrow_rb in self.dropped_arrows:
                self.world.removeRigidBody(arrow_rb.node())
                arrow_rb.remove_node()
            return task.done
