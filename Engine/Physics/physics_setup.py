from panda3d.bullet import BulletCharacterControllerNode, BulletBoxShape, BulletSoftBodyConfig, BulletSoftBodyNode
from direct.task.TaskManagerGlobal import taskMgr
from panda3d.core import Vec3, BitMask32, NodePath, GeomNode
from panda3d.bullet import BulletWorld, BulletDebugNode, BulletRigidBodyNode, BulletPlaneShape

from Engine.Physics.collision_solids import BulletCollisionSolids
from Engine.Physics.player_physics import PlayerPhysics
from Engine.Physics.npc_triggers import NpcTriggers


class PhysicsAttr:

    def __init__(self):
        self.base = base
        self.world = None
        self.soft_world = None
        self.world_nodepath = render.find("**/World")
        self.debug_nodepath = None
        self.soft_debug_nodepath = None
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
        self.player_physics = PlayerPhysics()
        self.npc_triggers = NpcTriggers()

        self.no_mask = BitMask32.allOff()
        self.mask = BitMask32.allOn()
        self.mask0 = BitMask32.bit(0)
        self.mask1 = BitMask32.bit(1)
        self.mask2 = BitMask32.bit(2)
        self.mask3 = BitMask32.bit(3)
        self.mask5 = BitMask32.bit(5)
        self.ghost_mask = BitMask32.bit(1)
        self.npcs_fsm_states = None
        self.coll_collection = None
        self.cloth_pins = {}
        self.spine_bones = {}
        self.info = None

    def set_actor_collider(self, actor, col_name, shape, mask, type):
        if (actor
                and col_name
                and shape
                and mask
                and type
                and isinstance(col_name, str)
                and isinstance(shape, str)
                and isinstance(type, str)):
            if not self.base.game_instance['menu_mode'] and self.world_nodepath:
                actor_bs = None
                actor_bs_np = None
                if shape == 'capsule':
                    actor_bs = self.bullet_solids.get_bs_capsule()
                if shape == 'sphere':
                    actor_bs = self.bullet_solids.get_bs_sphere()
                if type == 'player':
                    self.base.game_instance['player_controller_np'] = BulletCharacterControllerNode(actor_bs,
                                                                                                    0.4,
                                                                                                    col_name)
                    actor_bs_np = render.attach_new_node(self.base.game_instance['player_controller_np'])
                    actor_bs_np.set_collide_mask(mask)
                    self.world.attach_character(actor_bs_np.node())

                    if self.game_settings['Debug']['set_editor_mode'] == 'NO':
                        if render.find("**/floater"):
                            render.find("**/floater").reparent_to(actor_bs_np)
                    elif self.game_settings['Debug']['set_editor_mode'] == 'YES':
                        actor.reparent_to(actor_bs_np)

                    self.base.game_instance["player_np"] = actor_bs_np
                    self.base.game_instance["player_np_mask"] = mask

                    # Set actor down to make it
                    # at the same point as bullet shape
                    actor.set_z(-1)
                    # Set the bullet shape position same as actor position
                    actor_bs_np.set_x(actor.get_x())
                    actor_bs_np.set_y(actor.get_y())

                    # Box rigid body for using in crouch state
                    z_scale = actor_bs.height / 2
                    axis = Vec3(0.5, 0.6, z_scale)
                    rectangle = BulletBoxShape(axis)
                    crouch_bs = rectangle
                    crouch_bs_np = actor_bs_np.attach_new_node(BulletRigidBodyNode("Crouch:BS"))
                    crouch_bs_np.node().add_shape(crouch_bs)
                    crouch_bs_np.node().set_mass(1.0)
                    crouch_bs_np.set_collide_mask(mask)
                    self.world.attach_rigid_body(crouch_bs_np.node())
                    crouch_bs_np.node().set_kinematic(True)
                    crouch_bs_np.set_scale(0.5)
                    crouch_bs_np.set_pos(0, -0.1, -0.5)
                    self.base.game_instance["player_crouch_bs_np"] = crouch_bs_np
                    self.base.game_instance["player_crouch_bs_np_mask"] = mask

                    # Set actor position to zero
                    # after actor becomes a child of bullet shape.
                    # It should not get own position values.
                    actor.set_y(0)
                    actor.set_x(0)

                    # Setup for soft bodies
                    self._set_cloth_physics(actor)

                    # attach hitboxes and weapons
                    self.bullet_solids.get_bs_hitbox(actor=actor,
                                                     joints=["LeftHand", "RightHand", "Hips"],
                                                     mask=self.mask0,
                                                     world=self.world)
                    # hitboxes task
                    request = self.base.game_instance["player_fsm_cls"]
                    self.player_physics.player_hips[actor.get_name()] = actor.find("**/**Hips:HB")
                    taskMgr.add(self.player_physics.player_hitbox_trace_task,
                                "player_hitbox_trace_task",
                                extraArgs=[actor, request], appendTask=True)

                elif type == 'npc':
                    actor_node = BulletRigidBodyNode(col_name)
                    actor_node.set_mass(1.0)
                    actor_node.add_shape(actor_bs)
                    actor_bs_np = self.world_nodepath.attach_new_node(actor_node)
                    actor_bs_np.set_collide_mask(mask)
                    self.world.attach_rigid_body(actor_bs_np.node())

                    actor.reparent_to(actor_bs_np)
                    self.base.game_instance['actors_np'][col_name] = actor_bs_np
                    self.base.game_instance['actor_controllers_np'][col_name] = actor_node
                    self.base.game_instance["actors_np_mask"][col_name] = mask

                    # Set actor down to make it
                    # at the same point as bullet shape
                    actor.set_z(-1)
                    # Set the bullet shape position same as actor position
                    actor_bs_np.set_x(actor.get_x())
                    actor_bs_np.set_y(actor.get_y())

                    # Box rigid body for using in crouch state
                    z_scale = actor_bs.height / 2
                    axis = Vec3(0.5, 0.6, z_scale)
                    rectangle = BulletBoxShape(axis)
                    crouch_bs = rectangle
                    crouch_bs_np = actor_bs_np.attach_new_node(BulletRigidBodyNode("Crouch:BS"))
                    crouch_bs_np.node().add_shape(crouch_bs)
                    crouch_bs_np.node().set_mass(1.0)
                    crouch_bs_np.set_collide_mask(mask)
                    self.world.attach_rigid_body(crouch_bs_np.node())
                    crouch_bs_np.node().set_kinematic(True)
                    crouch_bs_np.set_scale(0.5)
                    crouch_bs_np.set_pos(0, -0.1, -0.5)
                    self.base.game_instance["actors_crouch_bs_np"][col_name] = crouch_bs_np
                    self.base.game_instance["actors_crouch_bs_np_mask"][col_name] = mask

                    # Set actor position to zero
                    # after actor becomes a child of bullet shape.
                    # It should not get own position values.
                    actor.set_y(0)
                    actor.set_x(0)

                    # Setup for soft bodies
                    self._set_cloth_physics(actor)

                    # attach hitboxes and weapons
                    self.bullet_solids.get_bs_hitbox(actor=actor,
                                                     joints=["LeftHand", "RightHand", "Hips"],
                                                     mask=self.mask1,
                                                     world=self.world)

                    actor_bs_np.node().set_kinematic(True)
                    # actor_bs_np.node().set_collision_response(True)

                    # reparent bullet-shaped actor to LOD node
                    actor_bs_np.reparent_to(self.base.game_instance['lod_np'])

                    # attach trigger sphere
                    self.npc_triggers.set_ghost_trigger(actor, self.world)
                    taskMgr.add(self.npc_triggers.actor_area_trigger_task,
                                "{0}_area_trigger_task".format(col_name.lower()),
                                extraArgs=[actor], appendTask=True)

                elif type == 'npc_animal':
                    actor_bs_box = BulletBoxShape(Vec3(0.3, 1.5, 1))
                    actor_node = BulletRigidBodyNode(col_name)
                    actor_node.set_mass(1.0)
                    actor_node.add_shape(actor_bs_box)
                    actor_bs_np = self.world_nodepath.attach_new_node(actor_node)
                    actor_bs_np.set_collide_mask(mask)
                    self.world.attach_rigid_body(actor_bs_np.node())

                    actor.reparent_to(actor_bs_np)

                    self.base.game_instance['actors_np'][col_name] = actor_bs_np
                    self.base.game_instance['actor_controllers_np'][col_name] = actor_node

                    # Set actor down to make it
                    # at the same point as bullet shape
                    actor.set_z(-1)
                    # Set the bullet shape position same as actor position
                    actor_bs_np.set_x(actor.get_x())
                    actor_bs_np.set_y(actor.get_y())
                    # Set actor position to zero
                    # after actor becomes a child of bullet shape.
                    # It should not get own position values.
                    actor.set_y(0)
                    actor.set_x(0)

                    actor_bs_np.node().set_kinematic(True)
                    # actor_bs_np.node().set_collision_response(True)

                    # reparent bullet-shaped actor to LOD node
                    actor_bs_np.reparent_to(self.base.game_instance['lod_np'])

                    if "NPC_Horse" in col_name:
                        # attach mount place nodepath
                        mountplace = NodePath("Mountplace_{0}".format(actor.get_name()))
                        mountplace.reparent_to(actor_bs_np)
                        pos = actor_bs_np.get_pos() + Vec3(0.5, -0.15, 0)
                        mountplace.set_pos(pos)
                        actor.set_python_tag("mount_place", mountplace)

                    if "Horse" in col_name:
                        # attach trigger sphere
                        self.npc_triggers.set_ghost_trigger(actor, self.world)
                        taskMgr.add(self.npc_triggers.mountable_animal_area_trigger_task,
                                    "{0}_area_trigger_task".format(col_name.lower()),
                                    extraArgs=[actor], appendTask=True)
                    else:
                        self.npc_triggers.set_ghost_trigger(actor, self.world)
                        taskMgr.add(self.npc_triggers.actor_area_trigger_task,
                                    "{0}_area_trigger_task".format(col_name.lower()),
                                    extraArgs=[actor], appendTask=True)

    def set_static_object_colliders(self, scene, mask):
        if scene and mask and self.world:

            if not self.coll_collection:
                self.coll_collection = render.find("**/Collisions/lvl*coll")

            for coll in self.coll_collection.get_children():
                # Cut coll suffix from collider mesh name
                name = coll.get_name()
                if name.endswith(".coll.001"):
                    name = name.split(".coll.001")[0]

                # Find asset to attach it to rigidbody collider
                if scene.find("**/{0}".format(name)):
                    child = scene.find("**/{0}".format(name))

                    # Find asset to attach it to rigidbody collider
                    if child:
                        shape = self.bullet_solids.get_bs_auto(obj=coll, type_="static")
                        if shape:
                            child_bs_name = "{0}:BS".format(child.get_name())
                            child_bs_np = child.attach_new_node(BulletRigidBodyNode(child_bs_name))
                            child_bs_np.node().set_mass(0.0)
                            child_bs_np.node().add_shape(shape)
                            child_bs_np.node().set_into_collide_mask(mask)

                            self.world.attach(child_bs_np.node())
                            child_bs_np.set_hpr(child.get_hpr())

    def set_dynamic_object_colliders(self, scene, mask):
        if scene and mask and self.world:

            if not self.coll_collection:
                self.coll_collection = render.find("**/Collisions/lvl*coll")

            for coll in self.coll_collection.get_children():
                # Cut coll suffix from collider mesh name
                name = coll.get_name()
                if name.endswith(".coll.001"):
                    name = name.split(".coll.001")[0]

                # Find asset to attach it to rigidbody collider
                if scene.find("**/{0}".format(name)):
                    child = scene.find("**/{0}".format(name))

                    # Find asset to attach it to rigidbody collider
                    if child:
                        shape = self.bullet_solids.get_bs_auto(obj=coll, type_="dynamic")
                        if shape:
                            child_bs_name = "{0}:BS".format(child.get_name())
                            child_bs_np = child.attach_new_node(BulletRigidBodyNode(child_bs_name))
                            child_bs_np.node().set_mass(2.0)
                            child_bs_np.node().add_shape(shape)
                            child_bs_np.node().set_into_collide_mask(mask)

                            self.world.attach(child_bs_np.node())
                            child_bs_np.set_hpr(child.get_hpr())

    def toggle_physics_debug(self):
        if self.debug_nodepath:
            if self.debug_nodepath.is_hidden():
                self.debug_nodepath.show()
                # self.debug_nodepath.node().showBoundingBoxes(True)
            else:
                self.debug_nodepath.hide()
                # self.debug_nodepath.node().showBoundingBoxes(False)

        if self.soft_debug_nodepath:
            if self.soft_debug_nodepath.is_hidden():
                self.soft_debug_nodepath.show()
                # self.soft_debug_nodepath.node().showBoundingBoxes(True)
            else:
                self.soft_debug_nodepath.hide()
                # self.soft_debug_nodepath.node().showBoundingBoxes(False)

    def update_rigid_physics_task(self, task):
        """ Function    : update_rigid_physics_task

            Description : Update Rigid Body Physics

            Input       : Task

            Output      : None

            Return      : Task event
        """
        if self.base.game_instance["physics_is_activated"] == 1:
            if self.world:
                # Get the time that elapsed since last frame.
                dt = globalClock.getDt()
                self.world.do_physics(dt, 20, 1. / 30)

                # Do update RigidBodyNode parent node's position for every frame
                if hasattr(base, "close_item_name"):
                    name = base.close_item_name
                    if not render.find("**/{0}".format(name)).is_empty():
                        item = render.find("**/{0}".format(name))
                        if 'BS' in item.get_parent().get_name():
                            item.get_parent().node().set_transform_dirty()
        return task.cont

    def update_soft_physics_task(self, task):
        """ Function    : update_soft_physics_task

            Description : Update Soft Body Physics

            Input       : Task

            Output      : None

            Return      : Task event
        """
        if self.base.game_instance["physics_is_activated"] == 1:
            if self.soft_world:
                # Get the time that elapsed since last frame.
                dt = globalClock.getDt()
                self.soft_world.do_physics(dt, 5, 0.004)

                # Update clothes pin
                if self.cloth_pins:
                    for name in self.cloth_pins:
                        if self.cloth_pins.get(name) and self.spine_bones.get(name):
                            self.cloth_pins[name].set_pos(render, self.spine_bones[name].get_pos(render))
                            self.cloth_pins[name].set_hpr(render, self.spine_bones[name].get_hpr(render))
        return task.cont

    def set_physics_world(self, npcs_fsm_states):
        """ Function    : set_physics_world

            Description : Enable Physics

            Input       : None

            Output      : None

            Return      : None
        """
        self.world_nodepath = render.find("**/World")
        if self.world_nodepath:
            # Show a visual representation of the collisions occuring
            self.debug_nodepath = self.world_nodepath.attach_new_node(BulletDebugNode('Debug'))

            base.accept("f1", self.toggle_physics_debug)

            self.world = BulletWorld()
            self.world.set_gravity(Vec3(0, 0, -9.81))
            self.base.game_instance['physics_world_np'] = self.world

            if self.game_settings['Debug']['set_debug_mode'] == "YES":
                if hasattr(self.debug_nodepath, "node"):
                    self.world.set_debug_node(self.debug_nodepath.node())

            ground_shape = BulletPlaneShape(Vec3(0, 0, 1), 0)
            ground_nodepath = self.world_nodepath.attach_new_node(BulletRigidBodyNode('Ground'))
            ground_nodepath.node().add_shape(ground_shape)
            ground_nodepath.set_pos(0, 0, 0.10)
            ground_nodepath.node().set_into_collide_mask(self.mask)
            self.world.attach_rigid_body(ground_nodepath.node())

            # todo: remove archery test box soon
            shape = BulletBoxShape(Vec3(1, 1, 1))
            node = BulletRigidBodyNode('Box')
            node.set_mass(50.0)
            node.add_shape(shape)
            np = render.attach_new_node(node)
            np.set_pos(4, 2, 0)
            self.world.attach_rigid_body(node)
            assets = self.base.assets_collector()
            model = base.loader.load_model(assets['Box'])
            model.reparent_to(np)
            model.set_name('box')
            model.set_pos(0, 0, 0)
            model.set_hpr(np.get_hpr())

            # todo: test
            self.base.box_np = np

            # Disable colliding
            self.world.set_group_collision_flag(0, 0, False)
            # Enable colliding: player (0), static (1) and npc (2)
            self.world.set_group_collision_flag(0, 1, True)
            self.world.set_group_collision_flag(0, 2, True)

            self.npcs_fsm_states = npcs_fsm_states

            self.base.game_instance['physics_is_activated'] = 1

            taskMgr.add(self.update_rigid_physics_task,
                        "update_rigid_physics_task",
                        appendTask=True)

    def set_soft_physics_world(self, _bool):
        if _bool and isinstance(_bool, bool):
            # Cloth Physics Setup
            self.soft_world = BulletWorld()
            self.soft_world.set_gravity(Vec3(0, 0, -9.81))

            # Show a visual representation of the collisions occuring
            self.soft_debug_nodepath = self.world_nodepath.attachNewNode(BulletDebugNode('SoftDebug'))
            self.soft_debug_nodepath.hide()
            # self.soft_debug_nodepath.node().showWireframe(True)
            # self.soft_debug_nodepath.node().showConstraints(True)
            # self.soft_debug_nodepath.node().showBoundingBoxes(False)
            # self.soft_debug_nodepath.node().showNormals(True)

            if self.game_settings['Debug']['set_debug_mode'] == "YES":
                self.soft_world.set_debug_node(self.soft_debug_nodepath.node())

            # Get Soft body world information
            self.info = self.soft_world.getWorldInfo()
            self.info.setAirDensity(0.2)
            self.info.setWaterDensity(0)
            self.info.setWaterOffset(0)
            self.info.setWaterNormal(Vec3(0, 0, 0))

            self.soft_world.set_group_collision_flag(0, 0, False)

            self.base.game_instance['physics_is_activated'] = 1

            taskMgr.add(self.update_soft_physics_task,
                        "update_soft_physics_task",
                        appendTask=True)

    def _set_cloth_physics(self, actor):
        # TODO: TEST
        if self.game_settings['Debug']['set_debug_mode'] == 'YES':
            if self.soft_world and actor:
                for name in self.base.game_instance["actors_clothes"]:
                    if name in actor.get_name():
                        clothes = self.base.game_instance["actors_clothes"][name]
                        for cloth in clothes:
                            if cloth:
                                geom = cloth.find_all_matches('**/+GeomNode').getPath(0).node().modifyGeom(0)
                                geom_node = GeomNode('')
                                geom_node.addGeom(geom)
                                node = BulletSoftBodyNode.makeTriMesh(self.info, geom)
                                node.linkGeom(geom_node.modifyGeom(0))

                                # material and properties setup
                                node.getMaterial(0).setAngularStiffness(0.5)
                                node.getMaterial(0).setLinearStiffness(0.5)
                                # node.getMaterial(0).setVolumePreservation(0.001)

                                # node.generateBendingConstraints(10)

                                # node.getCfg().setAeroModel(BulletSoftBodyConfig.AMFaceTwoSided  )
                                node.getCfg().setDampingCoefficient(0.1)
                                # node.getCfg().setDragCoefficient(0.0)
                                # node.getCfg().setDriftSolverIterations(0.2)
                                # node.getCfg().setDynamicFrictionCoefficient(0.002)
                                # node.getCfg().setKineticContactsHardness(0.2)
                                # node.getCfg().setLiftCoefficient(0.0)
                                # node.getCfg().setMaxvolume(0.2)
                                node.getCfg().setPoseMatchingCoefficient(0.2)
                                # node.getCfg().setPositionsSolverIterations(0.2)
                                # node.getCfg().setPressureCoefficient(0)
                                # node.getCfg().setRigidContactsHardness(0.2)
                                # node.getCfg().setSoftContactsHardness(0.2)
                                # node.getCfg().setSoftVsKineticHardness(0.2)
                                # node.getCfg().setSoftVsKineticImpulseSplit(0.2)
                                # node.getCfg().setSoftVsRigidHardness(0.2)
                                # node.getCfg().setSoftVsRigidImpulseSplit(0.2)
                                # node.getCfg().setSoftVsSoftHardness(0.2)
                                # node.getCfg().setSoftVsSoftImpulseSplit(0.2)
                                # node.getCfg().setTimescale(0.2)
                                # node.getCfg().setVelocitiesCorrectionFactor(0.1)
                                # node.getCfg().setVelocitiesSolverIterations(0.2)
                                # node.getCfg().setVolumeConversationCoefficient(0.1)
                                # node.getCfg().setCollisionFlag(BulletSoftBodyConfig.CFVertexFaceSoftSoft, True)
                                node.setPose(True, True)
                                # node.setTotalDensity(1.0)
                                node.setTotalMass(1, True)
                                node.getShape(0).setMargin(0.5)
                                # node.setVolumeDensity(1.0)
                                # node.setVolumeMass(100)
                                soft_np = self.world_nodepath.attachNewNode(node)
                                soft_np.setCollideMask(BitMask32.bit(0))
                                self.soft_world.attachSoftBody(node)
                                geom_np = soft_np.attachNewNode(geom_node)
                                geom_np.set_two_sided(True)

                                for tex in cloth.find_all_textures():
                                    rp = self.base.game_instance['renderpipeline_np']
                                    if rp:
                                        rp.set_effect(soft_np, "{0}/Engine/Renderer"
                                                               "/effects/cloth.yaml".format(self.game_dir),
                                                      {"render_gbuffer": True,
                                                       "render_shadow": False,
                                                       "alpha_testing": True,
                                                       "normal_mapping": True})
                                        soft_np.set_shader_input("cloak_tex", tex)

                                # pin it down
                                spine_bone = actor.expose_joint(None, 'modelRoot', 'Korlan:Spine2')
                                self.spine_bones[name] = spine_bone

                                pin = spine_bone.attachNewNode(BulletRigidBodyNode('pin'))
                                self.cloth_pins[name] = pin

                                # The position of the cloak get's shifted, fix it
                                pin.set_z(0)

                                raw_txt = cloth.find('**/=ClothPin').getTag('ClothPin')
                                raw_list = raw_txt.strip().split()
                                vtx_list = []
                                # vec3_list = []

                                # Make nested list with 3-indexed inner list to use as Vec3 component
                                """for elem in raw_list:
                                        if len(vec3_list) < 3:
                                            vec3_list.append(int(elem))
                                        elif len(vec3_list) == 3:
                                            vtx_list.append(vec3_list)
                                            vec3_list = []"""

                                for elem in raw_list:
                                    vtx_list.append(int(elem))

                                for idx in range(300):
                                    soft_np.node().append_anchor(idx, pin.node())
                                    # soft_np.node().append_anchor(soft_np.node().get_closest_node_index(Vec3(*idx),
                                    # True),
                                    # self.pin.node())
