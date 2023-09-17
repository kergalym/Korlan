from panda3d.bullet import BulletCharacterControllerNode, BulletBoxShape, BulletSoftBodyConfig, BulletSoftBodyNode, \
    BulletHelper, BulletHeightfieldShape, ZUp
from direct.task.TaskManagerGlobal import taskMgr
from panda3d.core import Vec3, BitMask32, NodePath, GeomNode, GeomVertexFormat, Point3, PNMImage, Filename, \
    ShaderTerrainMesh, SamplerState
from panda3d.bullet import BulletWorld, BulletDebugNode, BulletRigidBodyNode, BulletPlaneShape

from Engine.Physics.collision_solids import BulletCollisionSolids
from Engine.Physics.player_damages import PlayerDamages
from Engine.Physics.npc_triggers import NpcTriggers
from Engine.Physics.player_trigger import PlayerTrigger

import json


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

        self.ground_rb_np = None
        self.landscape_rb_np = None
        self.cam_cs = None
        self.cam_bs_nodepath = None
        self.cam_collider = None
        self.bullet_solids = BulletCollisionSolids()
        self.player_damages = None
        self.player_trigger = PlayerTrigger()
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
        self.actor_parents = {}
        self.info = None
        self.item_bs = None

    def _get_character_controller_nodepath(self, shape, node_name, mask):
        rigid_body_node = BulletCharacterControllerNode(shape,
                                                        0.4,
                                                        node_name)
        if "Player" in node_name:
            rigid_body_np = self.render.attach_new_node(rigid_body_node)
        else:
            rigid_body_np = self.world_nodepath.attach_new_node(rigid_body_node)
        rigid_body_np.set_collide_mask(mask)
        self.world.attach_character(rigid_body_np.node())
        return rigid_body_np

    def _get_rigid_body_nodepath(self, shape, node_name, mass, mask):
        rigid_body_node = BulletRigidBodyNode(node_name)
        rigid_body_node.set_mass(mass)
        rigid_body_node.add_shape(shape)
        if "Player" in node_name:
            rigid_body_np = self.render.attach_new_node(rigid_body_node)
        else:
            rigid_body_np = self.world_nodepath.attach_new_node(rigid_body_node)
        rigid_body_np.set_collide_mask(mask)
        self.world.attach(rigid_body_np.node())
        return rigid_body_np

    def set_character_controller_nodepath_with_shape(self, actor, rigid_body_np):
        if actor and rigid_body_np:
            # get collision name
            node_name = actor.get_python_tag("col_name")

            shape = self.bullet_solids.get_bs_capsule(width=0.3, height=1.3, geometry=None)
            rigid_body_node = BulletCharacterControllerNode(shape,
                                                            0.4,
                                                            node_name)
            rigid_body_np.attach_new_node(rigid_body_node)
            rigid_body_np.set_collide_mask(self.mask)
            self.world.attach_character(rigid_body_np.node())

    def set_rigid_body_nodepath_with_shape(self, actor, rigid_body_np):
        if actor and rigid_body_np:
            shape = self.bullet_solids.get_bs_capsule(width=0.3, height=1.3, geometry=None)

            # get collision name and mass
            node_name = actor.get_python_tag("col_name")
            mass = actor.get_python_tag("col_mass")

            rigid_body_node = BulletRigidBodyNode(node_name)
            rigid_body_node.set_mass(mass)
            rigid_body_node.add_shape(shape)
            rigid_body_np.attach_new_node(rigid_body_node)
            rigid_body_np.set_collide_mask(self.mask)

            # Removed rigid body added before
            if len(self.world.get_rigid_bodies()) > 0:
                for body in self.world.get_rigid_bodies():
                    if body.name == rigid_body_np.get_name():
                        self.world.remove(rigid_body_np.node())

            self.world.attach(rigid_body_np.node())

    def set_character_controller_nodepath_half_height_shape(self, actor, rigid_body_np):
        if actor and rigid_body_np:
            # get collision name
            node_name = actor.get_python_tag("col_name")

            shape = self.bullet_solids.get_bs_capsule(width=0.3, height=0.3, geometry=None)
            rigid_body_node = BulletCharacterControllerNode(shape,
                                                            0.4,
                                                            node_name)
            rigid_body_np.attach_new_node(rigid_body_node)
            rigid_body_np.set_collide_mask(self.mask)
            self.world.attach_character(rigid_body_np.node())

    def set_rigid_body_nodepath_half_height_shape(self, actor, rigid_body_np):
        if actor and rigid_body_np:
            shape = self.bullet_solids.get_bs_capsule(width=0.3, height=0.3, geometry=None)

            # get collision name and mass
            node_name = actor.get_python_tag("col_name")
            mass = actor.get_python_tag("col_mass")

            rigid_body_node = BulletRigidBodyNode(node_name)
            rigid_body_node.set_mass(mass)
            rigid_body_node.add_shape(shape)
            rigid_body_np.attach_new_node(rigid_body_node)
            rigid_body_np.set_collide_mask(self.mask)
            self.world.attach(rigid_body_np.node())

    def remove_character_controller_node(self, rigid_body_np):
        if rigid_body_np:
            self.world.remove(rigid_body_np.node())

    def remove_rigid_body_node(self, rigid_body_np):
        if rigid_body_np:
            self.world.remove(rigid_body_np.node())

    def _get_crouch_rigidbody_nodepath(self, actor_rb_np, shape, mask):
        # Box rigid body for using in crouch state
        z_scale = shape.height / 2
        axis = Vec3(0.5, 0.6, z_scale)
        rectangle_shape = BulletBoxShape(axis)
        crouch_rb_np = actor_rb_np.attach_new_node(BulletRigidBodyNode("Crouch:BS"))
        crouch_rb_np.node().add_shape(rectangle_shape)
        crouch_rb_np.node().set_mass(9999)
        crouch_rb_np.set_collide_mask(mask)
        self.world.attach(crouch_rb_np.node())
        crouch_rb_np.node().set_kinematic(True)
        crouch_rb_np.set_scale(0.5)
        crouch_rb_np.set_pos(0, -0.1, -0.5)
        return crouch_rb_np

    def _set_player_rigidbody(self, actor, shape, col_name, mask):
        actor_rb_np = self._get_rigid_body_nodepath(shape=shape,
                                                    node_name=col_name,
                                                    mass=9999,
                                                    mask=mask)
        self.base.game_instance['player_controller'] = actor_rb_np.node()

        if self.game_settings['Debug']['set_editor_mode'] == 'NO':
            if render.find("**/floater"):
                render.find("**/floater").reparent_to(actor_rb_np)
        elif self.game_settings['Debug']['set_editor_mode'] == 'YES':
            actor.reparent_to(actor_rb_np)

        self.base.game_instance["player_np"] = actor_rb_np
        self.base.game_instance["player_np_mask"] = mask

        # keep collision name and mass
        actor.set_python_tag("col_name", col_name)

        actor.set_python_tag("col_mass", 9999)

        # Set actor down to make it
        # at the same point as bullet shape
        actor.set_z(-0.9)
        actor.set_python_tag("mesh_z_pos", actor.get_z())
        # Set the bullet shape position same as actor position
        actor_rb_np.set_x(0)
        actor_rb_np.set_y(0)

        # Set actor position to zero
        # after actor becomes a child of bullet shape.
        # It should not get own position values.
        actor.set_y(0)
        actor.set_x(0)

        # reload actor if it's dynamic
        actor_rb_np.set_z(4)

        # Box rigid body for using in crouch state
        """crouch_rb_np = self._get_crouch_rigidbody_nodepath(actor_rb_np=actor_rb_np,
                                                           shape=shape,
                                                           mask=mask)
        self.base.game_instance["player_crouch_bs_np"] = crouch_rb_np
        self.base.game_instance["player_crouch_bs_np_mask"] = self.mask0"""

        actor_rb_np.node().set_linear_damping(0.5)  # Linear damping for smoother acceleration
        actor_rb_np.node().set_deactivation_enabled(True)

        # Setup for soft bodies
        # self._set_cloth_physics(actor)

        # Attach hitboxes
        joints = ["Head",
                  "Hips",
                  "LeftHand", "RightHand",
                  "LeftArm", "RightArm",
                  "LeftForeArm", "RightForeArm",
                  "LeftUpLeg", "RightUpLeg",
                  "LeftLeg", "RightLeg",
                  "LeftFoot", "RightFoot"
                  ]
        self.bullet_solids.set_bs_hitbox(actor=actor,
                                         joints=joints,
                                         mask=self.mask,
                                         world=self.world)
        # hitboxes task
        request = self.base.game_instance["player_fsm_cls"]
        self.player_damages = PlayerDamages(actor, request)
        self.player_damages.player_hips[actor.get_name()] = actor.find("**/**Hips:HB")
        taskMgr.add(self.player_damages.player_hitbox_trace_task,
                    "player_hitbox_trace_task",
                    extraArgs=[actor, actor_rb_np, request], appendTask=True)

        # attach trigger sphere
        self.base.game_instance["player_trigger_cls"] = self.player_trigger
        self.player_trigger.set_ghost_trigger(actor, self.world)

        # self.make_cloth()

    def _set_npc_rigidbody(self, actor, shape, col_name, mask):
        actor_rb_np = self._get_rigid_body_nodepath(shape=shape,
                                                    node_name=col_name,
                                                    mass=9999,
                                                    mask=mask)
        actor.reparent_to(actor_rb_np)
        self.base.game_instance['actors_np'][col_name] = actor_rb_np
        self.base.game_instance['actor_controllers_np'][col_name] = actor_rb_np.node()
        self.base.game_instance["actors_np_mask"][col_name] = mask

        # keep collision name and mass
        actor.set_python_tag("col_name", col_name)

        actor.set_python_tag("col_mass", 9999)

        # Set actor down to make it
        # at the same point as bullet shape
        actor.set_python_tag("mesh_z_pos", actor.get_z())
        # Set the bullet shape position same as actor position
        actor_rb_np.set_x(0)
        actor_rb_np.set_y(0)
        actor_rb_np.node().set_deactivation_enabled(True)
        # reload actor if it's dynamic
        actor_rb_np.set_z(4)

        # Set actor position to zero
        # after actor becomes a child of bullet shape.
        # It should not get own position values.
        actor.set_y(0)
        actor.set_x(0)
        actor.set_z(-0.9)

        # Box rigid body for using in crouch state
        """crouch_rb_np = self._get_crouch_rigidbody_nodepath(actor_rb_np=actor_rb_np,
                                                           shape=shape,
                                                           mask=mask)
        self.base.game_instance["actors_crouch_bs_np"][col_name] = crouch_rb_np
        self.base.game_instance["actors_crouch_bs_np_mask"][col_name] = self.mask0"""

        # Setup for soft bodies
        # self._set_cloth_physics(actor)

        # attach hitboxes
        joints = ["Head",
                  "Hips",
                  "LeftHand", "RightHand",
                  "LeftArm", "RightArm",
                  "LeftForeArm", "RightForeArm",
                  "LeftUpLeg", "RightUpLeg",
                  "LeftLeg", "RightLeg",
                  "LeftFoot", "RightFoot"
                  ]
        self.bullet_solids.set_bs_hitbox(actor=actor,
                                         joints=joints,
                                         mask=self.mask,
                                         world=self.world)

        # reparent bullet-shaped actor to LOD node
        actor_rb_np.reparent_to(self.base.game_instance['lod_np'])

        # LOD quality preset
        for lod_qk in self.base.game_instance["lod_quality"]:
            if self.game_settings['Main']['details'] == lod_qk:
                lod_qv = self.base.game_instance["lod_quality"][lod_qk]
                self.base.game_instance['lod_np'].node().add_switch(lod_qv[0],
                                                                    lod_qv[1])

        # attach trigger sphere
        self.npc_triggers.set_ghost_trigger(actor, self.world)
        taskMgr.add(self.npc_triggers.actor_area_trigger_task,
                    "{0}_area_trigger_task".format(col_name.lower()),
                    extraArgs=[actor], appendTask=True)

    def _set_npc_animal_rigidbody(self, actor, col_name, mask):
        shape = self.bullet_solids.get_bs_capsule(width=0.5, height=1.1, geometry=None)
        actor_rb_np = self._get_rigid_body_nodepath(shape=shape,
                                                    node_name=col_name,
                                                    mass=9999,
                                                    mask=mask)
        actor.reparent_to(actor_rb_np)

        self.base.game_instance['actors_np'][col_name] = actor_rb_np
        self.base.game_instance['actor_controllers_np'][col_name] = actor_rb_np.node()
        self.base.game_instance["actors_np_mask"][col_name] = mask

        # Set actor down to make it
        # at the same point as bullet shape
        actor.set_z(-1.1)
        # Set the bullet shape position same as actor position
        actor_rb_np.set_x(actor.get_x())
        actor_rb_np.set_y(actor.get_y())
        # after actor becomes a child of bullet shape.
        # It should not get own position values.
        actor.set_y(0)
        actor.set_x(0)

        # reparent bullet-shaped actor to LOD node
        actor_rb_np.reparent_to(self.base.game_instance['lod_np'])
        actor_rb_np.node().set_linear_damping(0.5)  # Linear damping for smoother acceleration
        actor_rb_np.node().set_deactivation_enabled(True)

        # LOD quality preset
        for lod_qk in self.base.game_instance["lod_quality"]:
            if self.game_settings['Main']['details'] == lod_qk:
                lod_qv = self.base.game_instance["lod_quality"][lod_qk]
                self.base.game_instance['lod_np'].node().add_switch(lod_qv[0],
                                                                    lod_qv[1])

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

    def set_actor_collider(self, actor, col_name, shape, type):
        if (actor
                and col_name
                and shape
                and type
                and isinstance(col_name, str)
                and isinstance(shape, str)
                and isinstance(type, str)):
            if not self.base.game_instance['menu_mode'] and self.world_nodepath:
                bullet_shape = None
                if shape == 'capsule':
                    bullet_shape = self.bullet_solids.get_bs_capsule(width=0.3, height=1.1, geometry=None)
                if shape == 'sphere':
                    bullet_shape = self.bullet_solids.get_bs_sphere(radius=1)

                # Set Player and NPC colliders
                if type == 'player':
                    self._set_player_rigidbody(actor, bullet_shape, col_name, self.mask)
                elif type == 'npc':
                    self._set_npc_rigidbody(actor, bullet_shape, col_name, self.mask)
                elif type == 'npc_animal':
                    self._set_npc_animal_rigidbody(actor, col_name, self.mask)

    def set_static_object_colliders(self, scene):
        if scene and self.world:

            self.coll_collection = render.find("**/Collisions/lvl*collider")

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
                        shape = self.bullet_solids.get_bs_auto(mesh=coll, type_="static")
                        if shape:
                            child_bs_name = "{0}:BS".format(child.get_name())
                            child_rb_np = child.attach_new_node(BulletRigidBodyNode(child_bs_name))
                            child_rb_np.node().add_shape(shape)
                            self.world.attach(child_rb_np.node())
                            child_rb_np.set_hpr(child.get_hpr())

                            # Remove collider meshes, not needed anymore
                            coll.remove_node()

    def set_dynamic_object_colliders(self, scene):
        if scene and self.world:

            if not self.coll_collection:
                self.coll_collection = render.find("**/Collisions/lvl*collider")

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
                        shape = self.bullet_solids.get_bs_auto(mesh=coll, type_="dynamic")
                        if shape:
                            child_bs_name = "{0}:BS".format(child.get_name())
                            child_rb_np = child.attach_new_node(BulletRigidBodyNode(child_bs_name))
                            child_rb_np.node().set_mass(2.0)
                            child_rb_np.node().add_shape(shape)
                            self.world.attach(child_rb_np.node())
                            child_rb_np.set_hpr(child.get_hpr())

                            # Remove collider meshes, not needed anymore
                            coll.remove_node()

    def toggle_physics_debug(self):
        renderpipeline_np = self.base.game_instance["renderpipeline_np"]
        if self.debug_nodepath:
            if self.debug_nodepath.is_hidden():
                renderpipeline_np.set_effect(render,
                                             "{0}/Engine/Renderer/effects/default.yaml".format(
                                                 self.base.game_dir),
                                             {"render_gbuffer": False,
                                              "render_forward": True,
                                              "render_shadow": True,
                                              "alpha_testing": True,
                                              "normal_mapping": True})
                self.debug_nodepath.show()
                # self.debug_nodepath.node().showBoundingBoxes(True)
            else:
                renderpipeline_np.set_effect(render,
                                             "{0}/Engine/Renderer/effects/default.yaml".format(
                                                 self.base.game_dir),
                                             {"render_gbuffer": True,
                                              "render_forward": False,
                                              "render_shadow": True,
                                              "alpha_testing": True,
                                              "normal_mapping": True})
                self.debug_nodepath.hide()
                # self.debug_nodepath.node().showBoundingBoxes(False)

        if self.soft_debug_nodepath:
            if self.soft_debug_nodepath.is_hidden():
                self.soft_debug_nodepath.show()
                # self.soft_debug_nodepath.node().showBoundingBoxes(True)
            else:
                self.soft_debug_nodepath.hide()
                # self.soft_debug_nodepath.node().showBoundingBoxes(False)

        if self.base.game_instance["level_navmesh_np"]:
            navmesh_scene_np = self.base.game_instance["level_navmesh_np"]
            if navmesh_scene_np.is_hidden():
                navmesh_scene_np.show()
            else:
                navmesh_scene_np.hide()

    def _construct_landscape_terrain(self):
        terrain_master_np = self.base.game_instance["world_np"].attach_new_node("terrain")
        images = base.textures_collector(path="Assets/Heightmaps")
        terrain_np_scale = Vec3(8192, 8192, 600)

        # Construct terrain from large heightfield texture with size 8192x8192
        heightfield = self.base.loader.load_texture(images["heightfield"])
        terrain_node = ShaderTerrainMesh()
        terrain_node.heightfield = heightfield
        terrain_node.target_triangle_width = 1.0
        terrain_node.generate()
        terrain_np = terrain_master_np.attach_new_node(terrain_node)
        terrain_np.set_scale(terrain_np_scale)

        # Construct collision shape for terrain from small heightfield texture with size 256x256
        heightmap_sm = PNMImage(Filename(images["heightfield_sm"]))
        shape = BulletHeightfieldShape(heightmap_sm, 10, ZUp)
        shape.set_use_diamond_subdivision(True)

        node = BulletRigidBodyNode('Ground')
        node.add_shape(shape)

        terrain_bs_np = terrain_master_np.attach_new_node(node)
        self.world.attach(node)
        terrain_bs_np.set_pos(0, 0, 0)

        # ShaderTerrainMesh and BulletHeightfieldShape have different origins.
        # The BulletHeightfieldShape is centered around the origin,
        # while the ShaderTerrainMesh uses the lower left corner as its origin.
        # This can be corrected by positioning the ShaderTerrainMesh with an left offset based on its half size.
        offset = terrain_np.get_scale() / 2
        terrain_np.set_pos(-offset.x, -offset.y, -offset.z)

        # Calculate same scale for BulletHeightfieldShape
        terrain_bs_np.set_scale(32.5, 32.5, 62)
        terrain_bs_np.set_z(terrain_bs_np.get_z() + 5)

        # Add shader to terrain
        render_pipeline = self.base.game_instance["renderpipeline_np"]
        render_pipeline.set_effect(terrain_np,
                                   "{0}/Engine/Renderer/effects/terrain-effect.yaml".format(self.base.game_dir),
                                   {}, 101)

        # Set land texture
        landscape_tex_path = "{0}/Assets/Levels/tex/T_OuterLandscape_1_B.txo".format(self.base.game_dir)
        landscape_tex = self.base.loader.load_texture(landscape_tex_path)
        terrain_np.set_shader_input("heightfield_diffuse", landscape_tex)

    def _construct_landscape_colision_mesh(self, landscape):
        shape = self.bullet_solids.get_bs_auto(mesh=landscape, type_="static")
        if shape is not None:
            self.landscape_rb_np = landscape.attach_new_node(BulletRigidBodyNode("Landscape_BN"))
            self.landscape_rb_np.node().add_shape(shape)
            self.landscape_rb_np.set_collide_mask(self.mask)
            self.world.attach(self.landscape_rb_np.node())
            self.landscape_rb_np.set_pos(0, 0, 0)

    def waiting_for_landscape_task(self, name, task):
        landscapes = render.find_all_matches("**/{0}_*_LOD0".format(name))
        if landscapes is not None and len(landscapes) > 0:
            # Remove Pre-loading Stage Ground since we're going to load the landscape
            if self.ground_rb_np:
                self.world.remove_rigid_body(self.ground_rb_np.node())

            for landscape in landscapes:
                self._construct_landscape_colision_mesh(landscape=landscape)

            """
            if landscape is not None:
                landscape.remove_node()

            self._construct_landscape_terrain()
            """

            return task.done

        return task.cont

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
                self.world.do_physics(dt, 5, 1.0/60.0)

                # Do update RigidBodyNode parent node's position for every frame
                if hasattr(base, "close_item_name"):
                    if self.item_bs is not None:
                        self.item_bs.node().set_transform_dirty()

                    elif self.item_bs is None:
                        name = base.close_item_name
                        if not render.find("**/{0}".format(name)).is_empty():
                            item = render.find("**/{0}".format(name))
                            if 'BS' in item.get_parent().get_name():
                                item.get_parent().node().set_transform_dirty()
                                self.item_bs = item.get_parent()
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
                self.soft_world.do_physics(dt, 5, 1.0/60.0)

                # Update clothes pin
                if self.cloth_pins:
                    for name in self.cloth_pins:
                        if self.cloth_pins.get(name) and self.spine_bones.get(name):
                            self.cloth_pins[name].set_z(self.spine_bones[name].get_z() + 2.9)

        return task.cont

    def set_physics_world(self, level_mesh, npcs_fsm_states):
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

            if self.game_settings['Debug']['set_debug_mode'] == "NO":
                base.accept("f1", self.toggle_physics_debug)

            self.world = BulletWorld()
            self.world.set_gravity(Vec3(0, 0, -9.81))
            self.base.game_instance['physics_world_np'] = self.world

            # Setup collision filtering
            # self.world.set_group_collision_flag(0, 0, False)
            self.world.set_group_collision_flag(0, 1, False)

            self.world.set_debug_node(self.debug_nodepath.node())

            # Set Pre-loading Stage Ground
            ground_shape = BulletPlaneShape(Vec3(0, 0, 1), 0)
            self.ground_rb_np = self.world_nodepath.attach_new_node(BulletRigidBodyNode('Ground'))
            self.ground_rb_np.node().add_shape(ground_shape)
            self.ground_rb_np.set_pos(0, 0, 0)
            self.ground_rb_np.set_collide_mask(self.mask)
            self.world.attach(self.ground_rb_np.node())

            # Set Landscape Collision
            # Wait until landscape is loaded
            taskMgr.add(self.waiting_for_landscape_task,
                        "waiting_for_landscape_task",
                        extraArgs=[level_mesh],
                        appendTask=True)

            # todo: remove archery test box soon
            shape = BulletBoxShape(Vec3(1, 1, 1))
            node = BulletRigidBodyNode('Box:BS')
            node.set_mass(50.0)
            node.add_shape(shape)
            np = render.attach_new_node(node)
            np.set_pos(3, 2, 0)
            self.world.attach(node)
            assets = self.base.assets_collector()
            model = base.loader.load_model(assets['Box'])
            model.reparent_to(np)
            model.set_name('box')
            model.set_pos(0, 0, 0)
            model.set_hpr(np.get_hpr())

            self.npcs_fsm_states = npcs_fsm_states

            self.base.game_instance['physics_is_activated'] = 1

            self.item_bs = None
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

    def find_all_cloth_pin_vertexes(self, input, look_for):
        input_egg = open(input, 'r')
        last_vertex = None
        is_vertex_pos = False
        found_list = []
        for line in input_egg.readlines():
            if is_vertex_pos:
                # remove first matched pattern
                vertex_raw = line.split()
                last_vertex = (float(vertex_raw[0]), float(vertex_raw[1]), float(vertex_raw[2]))
                is_vertex_pos = False
            else:
                if line.strip().startswith('<Vertex>'):
                    is_vertex_pos = True
                elif line.strip().startswith(look_for):
                    found_list.append(last_vertex)
        input_egg.close()
        return found_list

    def make_cloth(self):
        player_np = self.base.game_instance["player_ref"]
        for name in self.base.game_instance["actors_clothes"]:
            clothes = self.base.game_instance["actors_clothes"][name]
            for cloth in clothes:
                soft_body_node = BulletSoftBodyNode.makeTriMesh(self.info, cloth.node().modifyGeom(0))
                soft_body_node.setTotalMass(0.5)  # Set the total mass of the soft body
                soft_body_node.appendAnchor(1, self.base.game_instance["player_np"].node())  # Attach the soft body to a specific node (e.g., the mesh)
                player_np.attach_new_node(soft_body_node)

                # Add the soft body to the Bullet world
                self.world.attachSoftBody(soft_body_node)

    def _set_cloth_physics(self, actor):
        if self.soft_world and actor:
            for name in self.base.game_instance["actors_clothes"]:
                if name in actor.get_name():
                    clothes = self.base.game_instance["actors_clothes"][name]
                    cloth_path = self.base.game_instance["actors_clothes_path"][name]
                    for cloth in clothes:
                        if cloth:
                            geom = cloth.find_all_matches('**/+GeomNode').getPath(0).node().modifyGeom(0)
                            geom_node = cloth.find_all_matches('**/+GeomNode').getPath(0).node()
                            node = BulletSoftBodyNode.makeTriMesh(self.info, geom)
                            node.linkGeom(geom_node.modifyGeom(0))

                            # material and properties setup
                            node.getMaterial(0).setAngularStiffness(0.5)
                            # node.getMaterial(0).setLinearStiffness(0.1)
                            # node.getMaterial(0).setVolumePreservation(0.001)

                            # node.generateBendingConstraints(10)

                            # node.getCfg().setAeroModel(BulletSoftBodyConfig.AMFaceTwoSided  )
                            node.getCfg().setDampingCoefficient(0.01)
                            # node.getCfg().setDragCoefficient(0.0)
                            # node.getCfg().setDriftSolverIterations(0.2)
                            # node.getCfg().setDynamicFrictionCoefficient(0.0)
                            # node.getCfg().setKineticContactsHardness(0.2)
                            # node.getCfg().setLiftCoefficient(0.0)
                            # node.getCfg().setMaxvolume(0.2)
                            node.getCfg().setPoseMatchingCoefficient(0.7)
                            # node.getCfg().setPositionsSolverIterations(0.2)
                            # node.getCfg().setPressureCoefficient(0.0)
                            # node.getCfg().setRigidContactsHardness(0.2)
                            # node.getCfg().setSoftContactsHardness(0.2)
                            # node.getCfg().setSoftVsKineticHardness(0.2)
                            # node.getCfg().setSoftVsKineticImpulseSplit(0.2)
                            # node.getCfg().setSoftVsRigidHardness(0.2)
                            # node.getCfg().setSoftVsRigidImpulseSplit(0.2)
                            # node.getCfg().setSoftVsSoftHardness(0.2)
                            node.getCfg().setSoftVsSoftImpulseSplit(0)
                            # node.getCfg().setTimescale(0.2)
                            # node.getCfg().setVelocitiesCorrectionFactor(0.0)
                            # node.getCfg().setVelocitiesSolverIterations(0.2)
                            # node.getCfg().setVolumeConversationCoefficient(0.0)
                            node.getCfg().setCollisionFlag(BulletSoftBodyConfig.CFVertexFaceSoftSoft, False)
                            node.setPose(False, False)
                            # node.setTotalDensity(1.0)
                            node.setTotalMass(10)
                            # node.getShape(0).setMargin(0.5)
                            # node.setVolumeDensity(1.0)
                            # node.setVolumeMass(100)

                            base.nodesoft = node

                            soft_np = self.world_nodepath.attachNewNode(node)
                            self.soft_world.attachSoftBody(node)
                            geom_np = soft_np.attachNewNode(geom_node)
                            # geom_np.set_two_sided(True)

                            # Pin the cloak down
                            spine_bone = actor.expose_joint(None, 'modelRoot', 'Korlan:Spine2')
                            actor_rb_np = actor.get_parent()
                            self.spine_bones[name] = spine_bone
                            self.actor_parents[name] = actor_rb_np

                            pin = actor_rb_np.attach_new_node(BulletRigidBodyNode('pin'))
                            pin.set_pos(0, -0.02, 0.9)

                            self.cloth_pins[name] = pin

                            # Append fixed (non-movable) part of the cloak to the pin node (egg file)
                            # cloth_path = cloth_path[:-4]
                            pin_verts = self.find_all_cloth_pin_vertexes(cloth_path,
                                                                         '<RGBA> { 1 1 1 1 }')

                            pins = json.dumps(pin_verts)
                            for vertex in json.loads(pins):
                                soft_np.node().append_anchor(
                                    soft_np.node().get_closest_node_index(Vec3(*vertex), True), pin.node(), False)

    def set_problemus_room_physics(self):
        if not self.ground_rb_np:
            ground_shape = BulletPlaneShape(Vec3(0, 0, 1), 0)
            self.ground_rb_np = self.world_nodepath.attach_new_node(BulletRigidBodyNode('Ground'))
            self.ground_rb_np.node().add_shape(ground_shape)
            self.ground_rb_np.set_pos(0, 0, 0)
            self.ground_rb_np.set_collide_mask(self.mask)
            self.world.attach(self.ground_rb_np.node())

        if self.landscape_rb_np:
            self.world.remove_rigid_body(self.landscape_rb_np.node())
            self.landscape_rb_np.get_child(0).reparent_to(self.world_nodepath)
            self.landscape_rb_np.remove_node()

        self.world_nodepath.hide()

        # Reparent actors to Render nodepath if they start with complex task
        for actor_k,  actor_rb_np_k in zip(self.base.game_instance["actors_ref"],
                                           self.base.game_instance["actors_np"]):
            actor = self.base.game_instance["actors_ref"][actor_k]
            actor_rb_np = self.base.game_instance["actors_np"][actor_rb_np_k]
            if actor.get_python_tag("current_task") == "horse_riding":
                name_rb = actor_rb_np.get_name().split(":")[0]
                if actor.get_name() == name_rb:
                    if actor.has_python_tag("mounted_horse"):
                        if actor.get_python_tag("mounted_horse"):
                            actor.get_python_tag("mounted_horse").reparent_to(render)
                    actor_rb_np.reparent_to(render)

    def remove_problemus_room_physics(self):
        if self.world_nodepath.find("lvl_landscape"):

            if self.ground_rb_np:
                self.world.remove_rigid_body(self.ground_rb_np.node())
                self.ground_rb_np.remove_node()

            landscape = self.world_nodepath.find("lvl_landscape")
            shape = self.bullet_solids.get_bs_auto(mesh=landscape, type_="static")
            if shape is not None:
                self.landscape_rb_np = landscape.attach_new_node(BulletRigidBodyNode("Landscape_BN"))
                self.landscape_rb_np.node().add_shape(shape)
                self.landscape_rb_np.set_collide_mask(self.mask)
                self.world.attach(self.landscape_rb_np.node())
                self.landscape_rb_np.set_pos(0, 0, 0)

        # Reparent actors back to World nodepath if they done with complex tasks
        for actor_k, actor_rb_np_k in zip(self.base.game_instance["actors_ref"],
                                          self.base.game_instance["actors_np"]):
            actor = self.base.game_instance["actors_ref"][actor_k]
            actor_rb_np = self.base.game_instance["actors_np"][actor_rb_np_k]
            if actor.get_python_tag("current_task") is None:
                name_rb = actor_rb_np.get_name().split(":")[0]
                if actor.get_name() == name_rb:
                    if actor.has_python_tag("mounted_horse"):
                        if actor.get_python_tag("mounted_horse"):
                            actor.get_python_tag("mounted_horse").reparent_to(self.world_nodepath)
                    actor_rb_np.reparent_to(self.world_nodepath)

        self.world_nodepath.show()

