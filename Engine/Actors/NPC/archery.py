import random

from direct.gui.OnscreenText import OnscreenText
from direct.task.TaskManagerGlobal import taskMgr
from panda3d.bullet import BulletRigidBodyNode, BulletBoxShape
from panda3d.core import BitMask32, NodePath, Vec3, TextNode


class Archery:
    def __init__(self, actor_name):
        self.game_settings = base.game_settings
        self.base = base
        self.render = render
        self.actor_name = actor_name
        self.arrow_ref = None
        self.arrows = []
        self.dropped_arrows = []
        self.arrow_ref = None
        self.arrow_is_prepared = False
        self.arrow_charge_units = 100
        self.arrow_brb_in_use = None
        self.raytest_result = None
        self.hit_target = None
        self.target_pos = None
        self.target_np = None

        self.target_test_ui = OnscreenText(text="",
                                           pos=(1.5, 0.8),
                                           scale=0.05,
                                           fg=(255, 255, 255, 0.9),
                                           align=TextNode.ALeft,
                                           mayChange=True)

    async def prepare_arrows_helper(self, arrow_name, joint_name):
        if (arrow_name
                and joint_name
                and isinstance(arrow_name, str)
                and isinstance(joint_name, str)):
            self.arrows = []
            assets = self.base.assets_collector()
            joint = None
            arrow_count = 0
            actor_ref = self.base.game_instance['actors_ref'].get(self.actor_name)
            if actor_ref:
                joint = actor_ref.expose_joint(None, "modelRoot", joint_name)
                arrow_count = actor_ref.get_python_tag("arrow_count")

            for i in range(arrow_count):
                arrow = await self.base.loader.load_model(assets[arrow_name], blocking=False)
                arrow.set_name(arrow_name)
                arrow.reparent_to(joint)
                arrow.set_pos(-7, 7, -10)
                arrow.set_hpr(91.55, 0, 0)
                arrow.set_scale(100)

                arrow.set_python_tag("power", 0)
                arrow.set_python_tag("ready", 0)
                arrow.set_python_tag("shot", 0)
                arrow.set_python_tag("owner", self.actor_name.lower())
                self.arrows.append(arrow)

    def return_arrow_back(self, joint_name):
        if self.arrow_ref and joint_name:
            if self.arrow_ref.get_python_tag("ready") == 0:
                actor_ref = self.base.game_instance['actors_ref'][self.actor_name]
                joint = actor_ref.expose_joint(None, "modelRoot", joint_name)
                if joint:
                    self.arrow_ref.reparent_to(joint)
                    self.arrow_ref.set_pos(-10, 7, -12)
                    self.arrow_ref.set_hpr(91.55, 0, 0)
                    self.arrow_ref.set_scale(100)

                    self.arrow_ref.set_python_tag("power", 0)
                    self.arrow_ref.set_python_tag("ready", 0)
                    self.arrow_ref.set_python_tag("shot", 0)
                    self.arrows.append(self.arrow_ref)
                    actor_ref.set_python_tag("arrow_count", len(self.arrows))

        if self.base.game_instance['physics_world_np'] and self.arrow_brb_in_use:
            self.base.game_instance['physics_world_np'].remove_rigid_body(self.arrow_brb_in_use.node())
            self.arrow_brb_in_use.remove_node()

    def prepare_arrow_for_shoot(self, bow_name):
        if self.arrow_is_prepared:
            return False

        elif not self.arrow_is_prepared:
            actor = render.find("**/{0}".format(self.actor_name))
            if actor:
                bow = actor.find("**/{0}".format(bow_name))
                if bow:
                    if len(self.arrows) < 1:
                        return False

                    if self.base.game_instance['physics_world_np']:
                        # Remove arrow from inv and prepare it for use
                        arrow = self.arrows.pop(0)
                        actor.set_python_tag("arrow_count", len(self.arrows))
                        arrow.reparent_to(bow)
                        arrow.set_pos(0.04, 0.0, -0.01)
                        arrow.set_hpr(6.0, 2.86, 0)
                        arrow.set_scale(1)

                        # Create arrow collider
                        shape = BulletBoxShape(Vec3(0.05, 0.05, 0.05))
                        body = BulletRigidBodyNode('Arrow_BRB_{0}'.format(actor.get_name()))
                        arrow_rb_np = NodePath(body)
                        arrow_rb_np.wrt_reparent_to(bow)
                        arrow_rb_np.set_pos(-0.16, -0.01, -0.02)
                        arrow_rb_np.set_hpr(arrow.get_hpr())
                        arrow_rb_np.set_scale(arrow.get_scale())
                        arrow.wrt_reparent_to(arrow_rb_np)
                        arrow_rb_np.node().add_shape(shape)
                        arrow_rb_np.node().set_mass(2.0)

                        # Player and its owning arrow won't collide with each other
                        arrow_rb_np.set_collide_mask(BitMask32.allOff())

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
            # Get Bullet Rigid Body wrapped arrow
            self.arrow_brb_in_use.node().set_kinematic(False)
            self.arrow_brb_in_use.set_collide_mask(BitMask32.bit(0))
            self.arrow_ref.set_python_tag("shot", 1)
            self.arrow_brb_in_use.wrt_reparent_to(render)

            self.arrow_brb_in_use.node().apply_central_force(Vec3(0, 1, 0))
            self.arrow_brb_in_use.node().set_angular_velocity(Vec3(0, -0.4, 0))

            # We record arrows which have been shot
            self.dropped_arrows.append(self.arrow_brb_in_use)
            self.arrow_is_prepared = False

            # Destroy dropped arrows after 200 seconds which are 3 minutes
            taskMgr.do_method_later(700, self.destroy_arrow, 'destroy_arrow')

    def calculate_arrow_trajectory_task(self, task):
        """ Function    : calculate_arrow_trajectory_task

            Description : Task calculating arrow trajectory.

            Input       : None

            Output      : None

            Return      : Task status
        """
        name_bs = "{0}:BS".format(self.actor_name)
        actor_rb_np = self.base.game_instance['actors_np'][name_bs]

        if actor_rb_np.get_child(0).get_python_tag("target_np"):
            target_np = actor_rb_np.get_child(0).get_python_tag("target_np")
            pos_from = actor_rb_np.get_pos()
            pos_to = target_np.get_pos()

            physics_world_np = self.base.game_instance['physics_world_np']
            result = physics_world_np.ray_test_all(pos_from, pos_to)
            for hit in result.get_hits():
                if (hit and hit.get_node()
                        and self.actor_name not in hit.get_node().get_name()
                        and "Arrow" not in hit.get_node().get_name()
                        and "Ground" not in hit.get_node().get_name()
                        and "trigger" not in hit.get_node().get_name()
                        and "BGN" not in hit.get_node().get_name()
                        and "BRB" not in hit.get_node().get_name()
                ):
                    hit.get_node().get_name()
                    self.raytest_result = hit
                    break

        return task.cont

    def arrow_hit_check_task(self, task):
        """ Function    : arrow_hit_check_task

            Description : Task checking for arrow hits.

            Input       : None

            Output      : None

            Return      : Task status
        """
        if self.raytest_result and self.raytest_result.get_node():
            self.hit_target = self.raytest_result.get_node()
            self.target_pos = self.raytest_result.get_hit_pos()
            physics_world_np = self.base.game_instance['physics_world_np']
            if physics_world_np and self.arrow_brb_in_use:
                self.pierce_arrow()

        return task.cont

    def _on_contact_attach_to_joint(self, actor):
        joint_sorted_ = actor.get_python_tag("joint_bones")
        # sorted_ = sorted(j_bones, key=lambda x: (x.get_pos() - self.base.cam.get_pos()).length())
        random.shuffle(joint_sorted_)
        for bone in joint_sorted_:
            self.arrow_brb_in_use.set_collide_mask(BitMask32.allOff())
            self.arrow_ref.wrt_reparent_to(bone)
            self.arrow_ref.set_scale(100)
            self.arrow_ref.set_pos(bone.get_pos())
            self.arrow_ref.set_python_tag("ready", 0)
            self.reset_arrow_charge()
            break

    def _on_contact_attach_arrow(self):
        physics_world_np = self.base.game_instance['physics_world_np']
        result = physics_world_np.contact_test_pair(self.arrow_brb_in_use.node(), self.target_np.node())
        for contact in result.get_contacts():
            if ("NPC" not in contact.getNode1().name
                    and "Player" not in contact.getNode1().name):
                self.arrow_brb_in_use.set_collide_mask(BitMask32.allOff())
                self.arrow_ref.wrt_reparent_to(self.target_np)
                self.arrow_ref.set_python_tag("ready", 0)
                self.reset_arrow_charge()
            elif "NPC" in contact.getNode1().name:
                name = contact.getNode1().name.split(":")[0]
                actor = self.base.game_instance["actors_ref"][name]
                if actor:
                    self._on_contact_attach_to_joint(actor)
                    actor.get_python_tag("do_any_damage_func")()
            elif "Player" in contact.getNode1().name:
                actor = self.base.game_instance["player_ref"]
                if actor:
                    self._on_contact_attach_to_joint(actor)
                    actor.get_python_tag("do_any_damage_func")()
            break

    def pierce_arrow(self):
        if self.arrow_ref and self.arrow_brb_in_use:
            if self.arrow_ref.get_python_tag("ready") == 1:

                name_bs = self.hit_target.get_name()
                self.target_np = render.find("**/{0}".format(name_bs))

                if self.target_np:
                    self.base.sound.play_arrow_hit()
                    self._on_contact_attach_arrow()

    def reset_arrow_charge(self):
        if self.arrow_brb_in_use:
            self.arrow_ref.set_python_tag("power", 0)

    def destroy_arrow(self, task):
        if len(self.arrows) < 1:
            return False

        if self.base.game_instance['physics_world_np'] and self.dropped_arrows:
            for arrow_rb_np in self.dropped_arrows:
                if arrow_rb_np:
                    self.base.game_instance['physics_world_np'].remove_rigid_body(arrow_rb_np.node())
                    arrow_rb_np.remove_node()
            return task.done

        return task.cont

    def arrow_fly_task(self, task):
        dt = globalClock.getDt()
        if self.arrow_brb_in_use:
            power = 10
            if self.arrow_ref.get_python_tag("ready") == 1:

                # Move forward by x axis
                self.arrow_brb_in_use.set_x(self.arrow_brb_in_use, -power * dt)
                self.arrow_brb_in_use.set_z(self.arrow_brb_in_use, -0.3 * dt)

                # Camera follows by arrow
                # self.base.camera.set_y(self.base.camera, power * dt)
                # self.base.camera.set_z(self.arrow_brb_in_use.get_z())

        return task.cont

    def start_archery_helper_tasks(self):
        taskMgr.add(self.calculate_arrow_trajectory_task, "calculate_arrow_trajectory_task")
        taskMgr.add(self.arrow_hit_check_task, "arrow_hit_check_task")
        taskMgr.add(self.arrow_fly_task, "arrow_fly_task")

    def stop_archery_helper_tasks(self):
        taskMgr.remove("calculate_arrow_trajectory_task")
        taskMgr.remove("arrow_hit_check_task")
        taskMgr.remove("arrow_fly_task")
