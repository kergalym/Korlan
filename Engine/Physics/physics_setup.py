from direct.gui.OnscreenText import OnscreenText
from direct.interval.FunctionInterval import Wait
from direct.interval.ProjectileInterval import ProjectileInterval

from Engine.Collisions.collision_solids import BulletCollisionSolids
from panda3d.bullet import BulletCharacterControllerNode, BulletBoxShape
from direct.task.TaskManagerGlobal import taskMgr
from panda3d.core import Vec3, BitMask32, Point3, TextNode, NodePath
from panda3d.bullet import BulletWorld, BulletDebugNode, BulletRigidBodyNode, BulletPlaneShape
from direct.showbase.PhysicsManagerGlobal import physicsMgr


class PhysicsAttr:

    def __init__(self):
        self.physics_mgr = physicsMgr
        self.base = base
        self.world = None
        self.world_nodepath = None
        self.debug_nodepath = None
        self.render = render
        self.game_settings = base.game_settings
        self.game_dir = base.game_dir
        self.game_cfg = base.game_cfg
        self.game_cfg_dir = base.game_cfg_dir
        self.game_settings_filename = base.game_settings_filename
        self.cfg_path = self.game_cfg

        self.cam_cs = None
        self.cam_bs_nodepath = None
        self.cam_collider = None
        self.bullet_solids = BulletCollisionSolids()
        self.aimed_target_np = None
        self.aimed_target_pos = None
        self.archery_target_list = {"player": None}
        self.archery_arrows_list = {"player": None}
        self.target_test_ui = OnscreenText(text="",
                                           pos=(-1.8, 0.8),
                                           scale=0.03,
                                           fg=(255, 255, 255, 0.9),
                                           align=TextNode.ALeft,
                                           mayChange=True)
        self.korlan = None

        self.no_mask = BitMask32.allOff()
        self.mask = BitMask32.allOn()
        self.mask0 = BitMask32.bit(0)
        self.mask1 = BitMask32.bit(1)
        self.mask2 = BitMask32.bit(2)
        self.mask3 = BitMask32.bit(3)
        self.mask5 = BitMask32.bit(5)
        self.ghost_mask = BitMask32.bit(1)

        base.accept("bow_shoot", self.bow_shoot, ["Player", "bow_arrow_kazakh", "bow_kazakh"])
        # base.accept("bow_shoot", self.bow_shoot, [actor, "bow_arrow", "bow"])

    def collision_info(self, player, item):
        if player and item and hasattr(base, "bullet_world"):

            query_all = base.bullet_world.ray_test_all(player.get_pos(),
                                                       item.get_pos())

            collision_info = {"hits": query_all.has_hits(),
                              "fraction": query_all.get_closest_hit_fraction(),
                              "num_hits": query_all.get_num_hits()}

            for query in query_all.get_hits():
                collision_info["hit_pos"] = query.get_hit_pos()
                collision_info["hit_normal"] = query.get_hit_normal()
                collision_info["hit_fraction"] = query.get_hit_fraction()
                collision_info["node"] = query.get_node()

            return collision_info

    def set_collision(self, obj, type, shape):
        if (obj and type and shape
                and isinstance(type, str)
                and isinstance(shape, str)):

            if type == "env":
                self.set_static_object_colliders(obj=obj,
                                                 mask=self.mask1,
                                                 automatic=False)

            elif type == "item":
                self.set_dynamic_object_colliders(obj=obj,
                                                  mask=self.mask1,
                                                  automatic=False)

            elif type == "player":
                self.korlan = obj
                if hasattr(self.korlan, "set_tag"):
                    self.korlan.set_tag(key=obj.get_name(), value='1')
                self.set_actor_collider(actor=self.korlan,
                                        col_name='{0}:BS'.format(self.korlan.get_name()),
                                        shape=shape,
                                        mask=self.mask0,
                                        type="player")

            else:
                if hasattr(obj, "set_tag"):
                    obj.set_tag(key=obj.get_name(), value='1')
                self.set_actor_collider(actor=obj,
                                        col_name='{0}:BS'.format(obj.get_name()),
                                        shape=shape,
                                        mask=self.mask0,
                                        type=type)

    def set_physics_world(self, assets):
        """ Function    : set_physics_world

            Description : Enable Physics

            Input       : None

            Output      : None

            Return      : None
        """
        self.base.physics_is_active = 0

        world = render.find("**/World")
        if world:
            # Show a visual representation of the collisions occuring
            self.debug_nodepath = world.attach_new_node(BulletDebugNode('Debug'))

            base.accept("f1", self.toggle_physics_debug)

            self.world = BulletWorld()
            self.world.set_gravity(Vec3(0, 0, -9.81))

            if self.game_settings['Debug']['set_debug_mode'] == "NO":
                if hasattr(self.debug_nodepath, "node"):
                    self.world.set_debug_node(self.debug_nodepath.node())

            ground_shape = BulletPlaneShape(Vec3(0, 0, 1), 0)
            ground_nodepath = world.attachNewNode(BulletRigidBodyNode('Ground'))
            ground_nodepath.node().addShape(ground_shape)
            ground_nodepath.set_pos(0, 0, 0.10)
            ground_nodepath.node().set_into_collide_mask(self.mask)
            self.world.attach_rigid_body(ground_nodepath.node())

            # Box
            shape = BulletBoxShape(Vec3(1, 1, 1))
            node = BulletRigidBodyNode('Box')
            node.setMass(50.0)
            node.addShape(shape)
            np = render.attachNewNode(node)
            np.setPos(4, 2, 0)
            self.world.attachRigidBody(node)
            model = base.loader.loadModel('/home/galym/Korlan/tmp/box.egg')
            model.reparentTo(np)
            model.setName('box')
            model.setPos(0, 0, 0)
            model.setHpr(np.getHpr())

            # Disable colliding
            self.world.set_group_collision_flag(0, 0, False)
            # Enable colliding: player (0), static (1) and npc (2)
            self.world.set_group_collision_flag(0, 1, True)
            self.world.set_group_collision_flag(0, 2, True)

            taskMgr.add(self.add_asset_collision_task,
                        "add_asset_collision_task",
                        extraArgs=[assets],
                        appendTask=True)

            taskMgr.add(self.update_physics_task,
                        "update_physics_task",
                        appendTask=True)

            self.base.physics_is_active = 1

    def toggle_physics_debug(self):
        if self.debug_nodepath:
            if self.debug_nodepath.is_hidden():
                self.debug_nodepath.show()
                self.debug_nodepath.node().showBoundingBoxes(True)
            else:
                self.debug_nodepath.hide()
                self.debug_nodepath.node().showBoundingBoxes(False)

    def add_asset_collision_task(self, assets, task):
        """ Function    : add_asset_collision_task

            Description : Add asset collision

            Input       : Task

            Output      : None

            Return      : Task event
        """
        if (hasattr(self.base, "loading_is_done")
                and self.base.loading_is_done == 1):
            if isinstance(assets, dict):

                for name, type, shape in zip(assets['name'],
                                             assets['type'],
                                             assets['shape']):

                    if (not render.find("**/{0}".format(name)).is_empty()
                            and render.find("**/{0}:BS".format(name)).is_empty()):
                        if type == 'player' or 'actor':
                            self.set_collision(obj=render.find("**/{0}".format(name)),
                                               type=type,
                                               shape=shape)
                        else:
                            self.set_collision(obj=render.find("**/{0}".format(name)),
                                               type=type,
                                               shape=shape)

                return task.done

        return task.cont

    def update_physics_task(self, task):
        """ Function    : update_physics_task

            Description : Update Physics

            Input       : Task

            Output      : None

            Return      : Task event
        """
        if (hasattr(self.base, "loading_is_done")
                and self.base.loading_is_done == 1):
            if self.world:
                # Get the time that elapsed since last frame.
                dt = globalClock.getDt()
                self.world.do_physics(dt, 10, 1. / 30)

                # Do update RigidBodyNode parent node's position for every frame
                if hasattr(base, "close_item_name"):
                    name = base.close_item_name
                    if not render.find("**/{0}".format(name)).is_empty():
                        item = render.find("**/{0}".format(name))
                        if 'BS' in item.get_parent().get_name():
                            item.get_parent().node().set_transform_dirty()

        if base.game_mode is False and base.menu_mode:
            return task.done

        return task.cont

    def set_actor_collider(self, actor, col_name, shape, mask, type):
        if (actor
                and col_name
                and shape
                and mask
                and type
                and isinstance(col_name, str)
                and isinstance(shape, str)
                and isinstance(type, str)):
            if not base.menu_mode and base.game_mode:
                actor_bs = None
                actor_bs_np = None
                if shape == 'capsule':
                    actor_bs = self.bullet_solids.get_bs_capsule()
                if shape == 'sphere':
                    actor_bs = self.bullet_solids.get_bs_sphere()
                if type == 'player':
                    base.bullet_char_contr_node = BulletCharacterControllerNode(actor_bs,
                                                                                0.4,
                                                                                col_name)
                    actor_bs_np = render.attach_new_node(base.bullet_char_contr_node)
                    actor_bs_np.set_collide_mask(mask)
                    self.world.attach(base.bullet_char_contr_node)

                    if self.game_settings['Debug']['set_editor_mode'] == 'NO':
                        if render.find("**/floater"):
                            render.find("**/floater").reparent_to(actor_bs_np)
                    elif self.game_settings['Debug']['set_editor_mode'] == 'YES':
                        actor.reparent_to(actor_bs_np)

                elif type == 'npc':
                    actor_node = BulletCharacterControllerNode(actor_bs,
                                                               0.4,
                                                               col_name)
                    world = render.find("**/World")
                    if world:
                        actor_bs_np = world.attach_new_node(actor_node)
                        actor_bs_np.set_collide_mask(mask)
                        self.world.attach(actor_node)
                        actor.reparent_to(actor_bs_np)

                elif type == 'npc_animal':
                    actor_node = BulletCharacterControllerNode(actor_bs,
                                                               0.4,
                                                               col_name)
                    world = render.find("**/World")
                    if world:
                        actor_bs_np = world.attach_new_node(actor_node)
                        actor_bs_np.set_collide_mask(mask)
                        self.world.attach(actor_node)
                        actor.reparent_to(actor_bs_np)

                # Set actor down to make it
                # at the same point as bullet shape
                actor.set_z(-1)
                # Set the bullet shape position same as actor position
                if actor_bs_np:
                    actor_bs_np.set_x(actor.get_x())
                    actor_bs_np.set_y(actor.get_y())
                # Set actor position to zero
                # after actor becomes a child of bullet shape.
                # It should not get own position values.
                actor.set_y(0)
                actor.set_x(0)

                # attach hitboxes and weapons
                if type == "npc":
                    self.bullet_solids.get_bs_hitbox(actor=actor,
                                                     joints=["LeftHand", "RightHand", "Hips"],
                                                     world=self.world)

                    taskMgr.add(self.calculate_arrow_trajectory_task,
                                "{0}_bow_hit_check".format(actor.get_name()),
                                extraArgs=[actor],
                                appendTask=True)

                elif type == "player":
                    self.bullet_solids.get_bs_hitbox(actor=actor,
                                                     joints=["LeftHand", "RightHand", "Hips"],
                                                     world=self.world)

                    taskMgr.add(self.calculate_arrow_trajectory_task,
                                "{0}_bow_hit_check".format(actor.get_name()),
                                extraArgs=[actor],
                                appendTask=True)

                # reparent bullet-shaped actor to LOD node
                if type != "player":
                    actor_bs_np.reparent_to(self.base.lod_np)
                    self.base.lod.addSwitch(50.0, 0.0)

    def set_static_object_colliders(self, obj, mask, automatic):
        if obj and mask and self.world:
            shape = None
            for child in obj.get_children():
                # Skip child which already has Bullet shape
                if "BS" in child.get_name() or "BS" in child.get_parent().get_name():
                    continue
                # Skip unused mesh
                if "Ground" in child.get_name():
                    continue

                if "ground" in child.get_name():
                    continue

                if "Grass" in child.get_name():
                    continue

                if "tree" in child.get_name():
                    continue

                if "mountain" in child.get_name():
                    continue

                if automatic:
                    shape = self.bullet_solids.get_bs_auto(obj=child, type_="static")
                elif not automatic:
                    shape = self.bullet_solids.get_bs_predefined(obj=child, type_="static")

                if child.get_num_children() == 0:
                    if shape:
                        child_bs_name = "{0}:BS".format(child.get_name())
                        child_bs_np = obj.attach_new_node(BulletRigidBodyNode(child_bs_name))
                        child_bs_np.node().set_mass(0.0)
                        child_bs_np.node().add_shape(shape)
                        child_bs_np.node().set_into_collide_mask(self.mask1)

                        self.world.attach(child_bs_np.node())
                        child.reparent_to(child_bs_np)

                        child_bs_np.set_pos(child.get_pos())
                        child_bs_np.set_hpr(child.get_hpr())
                        child_bs_np.set_scale(child.get_scale())

                        # Make item position zero because now it's a child of bullet shape
                        child.set_pos(0, 0, 0)

                elif child.get_num_children() > 0:
                    self.set_static_object_colliders(child, mask, automatic)

    def set_dynamic_object_colliders(self, obj, mask, automatic):
        if obj and mask and self.world:
            shape = None
            for child in obj.get_children():
                # Skip child which already has Bullet shape
                if "BS" in child.get_name() or "BS" in child.get_parent().get_name():
                    continue

                if automatic:
                    shape = self.bullet_solids.get_bs_auto(obj=child, type_="dynamic")
                elif not automatic:
                    shape = self.bullet_solids.get_bs_predefined(obj=child, type_="dynamic")

                if child.get_num_children() == 0:
                    if shape:
                        child_bs_name = "{0}:BS".format(child.get_name())
                        child_bs_np = obj.attach_new_node(BulletRigidBodyNode(child_bs_name))
                        child_bs_np.node().set_mass(2.0)
                        child_bs_np.node().add_shape(shape)
                        child_bs_np.node().set_into_collide_mask(self.mask1)

                        self.world.attach(child_bs_np.node())
                        child.reparent_to(child_bs_np)

                        child_bs_np.set_pos(child.get_pos())
                        child_bs_np.set_hpr(child.get_hpr())
                        child_bs_np.set_scale(child.get_scale())

                        # Make item position zero because now it's a child of bullet shape
                        child.set_pos(0, 0, 0)

                elif child.get_num_children() > 0:
                    self.set_dynamic_object_colliders(child, mask, automatic)

    def bow_shoot(self, actor_name, arrow_name, bow_name):
        """ Function    : bow_shoot

            Description : Performs enhanced bow shooting.

            Input       : Strings, Nodepath

            Output      : None

            Return      : None
        """
        if actor_name and arrow_name and bow_name and self.world:
            # Find actor which should do bow shoot
            if render.find("**/{0}".format(actor_name)):
                actor = render.find("**/{0}".format(actor_name))

                # Find arrow from that actor
                if actor.find("**/{0}".format(arrow_name)):
                    arrow = actor.find("**/{0}".format(arrow_name))

                    # Construct arrow and start its trajectory
                    if arrow and self.aimed_target_pos and self.aimed_target_np:

                        # Calculate initial velocity
                        velocity = self.aimed_target_pos - arrow.get_pos() + Vec3(0, 0.4, 0)
                        # velocity = self.aimed_target_pos - self.bow.get_pos()
                        velocity.normalize()
                        velocity *= 100.0

                        # Create Bullet collider for an arrow
                        shape = BulletBoxShape(Vec3(0.5, 0.5, 0.5))
                        body = BulletRigidBodyNode('Arrow_BRB')
                        body_np = render.attachNewNode(body)
                        body_np.node().addShape(shape)
                        body_np.node().setMass(2.0)
                        body_np.node().setLinearVelocity(velocity)
                        body_np.setPos(actor.get_pos())
                        body_np.setCollideMask(BitMask32.allOn())
                        arrow.reparent_to(body_np)
                        arrow.set_pos(0, 0, 0)
                        # arrow.set_hpr(velocity)

                        # Enable Bullet Continuous Collision Detection
                        body_np.node().setCcdMotionThreshold(1e-7)
                        body_np.node().setCcdSweptSphereRadius(0.50)

                        # Add collider to physics world
                        self.world.attachRigidBody(body_np.node())
                        arrow.setCollideMask(BitMask32.allOff())

                        name = self.aimed_target_np.get_name()
                        self.archery_arrows_list[actor_name] = body_np
                        self.archery_target_list[actor_name] = render.find("**/{0}".format(name))

                        if self.archery_target_list[actor_name]:
                            # self.world.removeRigidBody(body_np.node())
                            pass

    def calculate_arrow_trajectory_task(self, actor, task):
        """ Function    : calculate_arrow_trajectory_task

            Description : Task calculating arrow trajectory.

            Input       : Strings, Nodepath

            Output      : None

            Return      : Task status
        """
        if not actor:
            return task.done
        elif actor:
            arrow_name = "bow_arrow"
            bow_name = "bow"
            if "Player" in actor.get_name():
                arrow_name = "bow_arrow_kazakh"
                bow_name = "bow_kazakh"
            bow = actor.find("**/{0}".format(bow_name))
            arrow = actor.find("**/{0}".format(arrow_name))
            if bow and arrow:
                mouse_watch = base.mouseWatcherNode
                if mouse_watch.has_mouse():
                    pos_mouse = base.mouseWatcherNode.get_mouse()
                    pos_from = Point3()
                    pos_to = Point3()
                    base.camLens.extrude(pos_mouse, pos_from, pos_to)

                    pos_from = self.render.get_relative_point(actor, pos_from)
                    pos_to = self.render.get_relative_point(base.camera, pos_to)

                    raytest_result = self.world.rayTestClosest(pos_from, pos_to)

                    # print(raytest_result.hasHit())
                    if (raytest_result.get_node()
                            and "Ground" not in str(raytest_result.get_node())):
                        self.aimed_target_np = raytest_result.get_node()
                        self.aimed_target_pos = raytest_result.get_hit_pos()
                        actor_name = actor.get_name()

                        if self.archery_arrows_list[actor_name]:
                            self.world.contactTest(self.aimed_target_np)
                            if self.world.contactTest(self.aimed_target_np).getNumContacts() > 0:
                                self.archery_arrows_list[actor_name].setLinearVelocity(0)
                                arrow.reparent_to(base.target_np)
                                arrow.set_scale(2)
                                self.archery_arrows_list[actor_name].setCollideMask(BitMask32.allOff())

                        # Leave this here for testing purposes
                        if self.aimed_target_pos:
                            self.target_test_ui.setText("")
                            name = self.aimed_target_np.get_name()
                            self.target_test_ui.setText("Target hit: {0}".format(name))
                        elif not self.aimed_target_np:
                            self.target_test_ui.setText("")
                        else:
                            self.target_test_ui.setText("")

        return task.cont
