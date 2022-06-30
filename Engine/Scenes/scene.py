from direct.task.TaskManagerGlobal import taskMgr
from panda3d.bullet import BulletSphereShape, BulletGhostNode
from panda3d.core import *
from Engine.Quests.social_quests import SocialQuests

# TODO UNCOMMENT WHEN R&D BECOMES PRODUCTION-READY
from panda3d.navigation import NavMeshNode, NavMeshQuery
from panda3d.navmeshgen import NavMeshBuilder

import struct


class SceneOne:

    def __init__(self):
        self.base = base
        self.render = render
        self.path = None
        self.game_settings = None
        self.model = None
        self.axis = None
        self.rotation = None
        self.scale_x = None
        self.scale_y = None
        self.scale_z = None
        self.type = None
        self.node_path = NodePath()
        self.social_quests = None
        self.game_settings = base.game_settings
        self.game_dir = base.game_dir
        self.game_cfg = base.game_cfg
        self.game_cfg_dir = base.game_cfg_dir
        self.game_settings_filename = base.game_settings_filename
        self.cfg_path = self.game_cfg
        self.world_nodepath = None

        # NavMeshBuilder is a class that is responsible
        # for building the polygon meshes and navigation meshes.
        self.builder = None
        self.navmesh = None

        self.navmeshnode = None
        self.navmeshnodepath = None

        # Define the NavMeshQuery instance
        self.navmesh_query = None

    def set_level_nav(self, scene_name):
        if scene_name and isinstance(scene_name, str):
            # TODO DROP THIS LINE WHEN R&D BECOMES PRODUCTION-READY
            # NavMeshBuilder is a class that is responsible
            # for building the polygon meshes and navigation meshes.
            self.builder = NavMeshBuilder()
            # Take NodePath as input. This method only uses
            # the collision nodes that are under this node.
            navmesh_scenes = self.base.navmesh_scene_collector()
            scene_name = "{0}_navmesh".format(scene_name)
            navmesh_scene_np = self.base.loader.load_model(navmesh_scenes[scene_name])
            navmesh_scene_np.reparent_to(render)
            self.base.game_instance["level_navmesh_np"] = navmesh_scene_np
            navmesh_scene_np.hide()

            self.builder.from_coll_node_path(navmesh_scene_np)

            self.builder.actor_height = 10
            self.builder.actor_radius = 4
            self.builder.actor_max_climb = 2
            self.navmesh = self.builder.build()

            self.navmeshnode = NavMeshNode("scene", self.navmesh)
            self.navmeshnodepath: NodePath = navmesh_scene_np.attach_new_node(self.navmeshnode)

            # Uncomment the line below to save the generated navmesh to file.
            # self.navmeshnodepath.write_bam_file("scene_navmesh.bam")

            # Uncomment the following section to read the generated navmesh from file.
            # self.navmeshnodepath.remove_node()
            # self.navmeshnodepath = self.loader.loadModel("scene_navmesh.bam")
            # self.navmeshnodepath.reparent_to(self.scene)
            # self.navmeshnode: NavMeshNode = self.navmeshnodepath.node()
            # self.navmesh = self.navmeshnode.get_nav_mesh()

            # Initialize the NavMeshQuery that we will use.
            self.navmesh_query = NavMeshQuery(self.navmesh)
            self.base.game_instance["navmesh_query"] = self.navmesh_query

    def set_water_trigger(self, scene, radius, task):
        if self.base.game_instance["loading_is_done"] == 1:
            if (self.render.find("**/World")
                    and self.base.game_instance["physics_world_np"]):
                world_np = self.render.find("**/World")
                ph_world = self.base.game_instance["physics_world_np"]

                if scene:
                    for actor in scene.get_children():
                        if "water_box" in actor.get_name():
                            sphere = BulletSphereShape(radius)
                            trigger_bg = BulletGhostNode('{0}_trigger'.format(actor.get_name()))
                            trigger_bg.add_shape(sphere)
                            trigger_np = world_np.attach_new_node(trigger_bg)
                            trigger_np.set_collide_mask(BitMask32(0x0f))
                            ph_world.attach_ghost(trigger_bg)
                            trigger_np.reparent_to(actor)
                            trigger_np.set_pos(0, 0, 1)
                            self.base.game_instance['water_trigger_np'] = trigger_np

                            return task.done

        return task.cont

    def set_indoor_trigger(self, scene, radius, task):
        if self.base.game_instance["loading_is_done"] == 1:
            if (self.render.find("**/World")
                    and self.base.game_instance["physics_world_np"]):
                world_np = self.render.find("**/World")
                ph_world = self.base.game_instance["physics_world_np"]

                for actor in scene.get_children():
                    if "indoor" in actor.get_name():
                        sphere = BulletSphereShape(radius)
                        trigger_bg = BulletGhostNode('{0}_trigger'.format(actor.get_name()))
                        trigger_bg.add_shape(sphere)
                        trigger_np = world_np.attach_new_node(trigger_bg)
                        trigger_np.set_collide_mask(BitMask32(0x0f))
                        ph_world.attach_ghost(trigger_bg)
                        trigger_np.reparent_to(actor)
                        trigger_np.set_pos(0, 0, 1)

                        return task.done

        return task.cont

    async def set_level(self, path, name, axis, rotation, scale, culling):
        if (isinstance(path, str)
                and isinstance(name, str)
                and isinstance(axis, list)
                and isinstance(rotation, list)
                and isinstance(scale, list)
                and isinstance(culling, bool)):

            self.path = "{0}{1}".format(self.game_dir, path)
            self.game_settings = self.game_settings
            self.model = name
            pos_x = axis[0]
            pos_y = axis[1]
            pos_z = axis[2]
            rot_h = rotation[0]
            self.scale_x = scale[0]
            self.scale_y = scale[1]
            self.scale_z = scale[2]

            self.base.game_instance['scene_is_loaded'] = False

            # Load the scene.
            scene = await self.base.loader.load_model(path, blocking=False)
            self.world_nodepath = render.find("**/World")
            if self.world_nodepath:

                # toggle texture compression for textures to compress them
                # before load into VRAM
                self.base.toggle_texture_compression(scene)

                scene.reparent_to(self.base.game_instance['lod_np'])
                # scene.reparent_to(self.world_nodepath)

                # LOD quality preset
                for lod_qk in self.base.game_instance["lod_quality"]:
                    if self.game_settings['Main']['details'] == lod_qk:
                        lod_qv = self.base.game_instance["lod_quality"][lod_qk]
                        self.base.game_instance['lod_np'].node().add_switch(lod_qv[0],
                                                                            lod_qv[1])

                # Set sRGB
                self.base.set_textures_srgb(scene, True)

                if self.game_settings['Debug']['set_debug_mode'] == "YES":
                    base.accept("f2", self.scene_toggle, [scene])

                scene.set_name(name)
                scene.set_scale(self.scale_x, self.scale_y, self.scale_z)
                scene.set_pos(pos_x, pos_y, pos_z)
                scene.set_hpr(scene, rot_h, 0, 0)

                # Make scene global
                self.base.game_instance['scene_np'] = scene

            self.base.game_instance['renderpipeline_np'].prepare_scene(scene)

            if render.find("**/Grass"):
                grass = render.find_all_matches("**/Grass*")
                for np in grass:
                    np.set_two_sided(True)
                    np.flatten_strong()

            # Enable lightmapping for this scene
            base.game_instance['render_attr_cls'].apply_lightmap_to_scene(scene=scene,
                                                                          lightmap="lightmap_scene_one")

            # Set two sided, since some model may be broken
            scene.set_two_sided(culling)

            # Enable flame
            base.game_instance['render_attr_cls'].set_flame_hearth(adv_render=True,
                                                                   scene_np=scene,
                                                                   flame_scale=0.1)
            """base.game_instance['render_attr_cls'].set_smoke_hearth(adv_render=True,
                                                                   scene_np=scene,
                                                                   smoke_scale=0.1)"""
            # Enable grass
            base.game_instance['render_attr_cls'].set_grass(adv_render=True,
                                                            fogcenter=Vec3(256, 256, 0),
                                                            uv_offset=Vec2(0, 0))

            # Tree Instancing
            # self.set_tree_instancing(scene=scene, amount=10, offset=7)
            self.set_gpu_instancing_to(scene=scene,
                                       pattern="tree_rig",
                                       placeholder="tree_empty")

            self.base.game_instance['scene_is_loaded'] = True

            # Load collisions for a level
            colliders_dict = base.assets_collider_collector()
            coll_scene_name = '{0}_coll'.format(name)
            coll_path = colliders_dict[coll_scene_name]
            coll_scene = await self.base.loader.load_model(coll_path, blocking=False)
            coll_scene.set_name(coll_scene_name)
            coll_scene_np = NodePath("Collisions")
            coll_scene_np.reparent_to(self.world_nodepath)
            coll_scene.reparent_to(coll_scene_np)
            coll_scene.hide()

            # Add Bullet colliders for this scene
            physics_attr = self.base.game_instance["physics_attr_cls"]
            if hasattr(physics_attr, "set_static_object_colliders"):
                physics_attr.set_static_object_colliders(scene=scene,
                                                         mask=physics_attr.mask)

            # Construct navigation system
            self.set_level_nav(name)

            if self.game_settings['Debug']['set_debug_mode'] == "YES":
                scene.hide()

            # Add indoor trigger
            radius = 4
            taskMgr.add(self.set_indoor_trigger,
                        "set_indoor_trigger",
                        extraArgs=[scene, radius],
                        appendTask=True)

            # Add water trigger
            radius = 7
            taskMgr.add(self.set_water_trigger,
                        "set_water_trigger",
                        extraArgs=[scene, radius],
                        appendTask=True)

            self.social_quests = SocialQuests()
            # Add item triggers
            taskMgr.add(self.social_quests.set_level_triggers,
                        "set_level_triggers",
                        extraArgs=[scene],
                        appendTask=True)

            """base.game_instance['render_attr_cls'].set_lighting(name='alight',
                                                               render=self.render,
                                                               pos=[0, 8.0, 10],
                                                               hpr=[0, -20, 0],
                                                               color=[0.8],
                                                               task="attach")"""

    def scene_toggle(self, scene):
        if scene.is_hidden():
            scene.show()
        else:
            scene.hide()

    def set_tree_instancing(self, scene, amount, offset):
        if (scene and isinstance(scene, NodePath)
                and isinstance(amount, int)
                and isinstance(offset, int)):
            tree = scene.find("**/tree*")
            if tree:
                tree_master = scene.attach_new_node('TreeMaster')
                # We do cruciform offset
                # x row of trees
                for i in range(amount):
                    step = i * offset
                    placeholder = tree_master.attach_new_node("treeInstance")
                    placeholder.set_pos(step, 0, 0)
                    tree.instance_to(placeholder)
                for i in range(amount):
                    step = i * offset
                    placeholder = tree_master.attach_new_node("treeInstance")
                    placeholder.set_pos(-step, 0, 0)
                    tree.instance_to(placeholder)
                # y row of trees
                for i in range(amount):
                    step = i * offset
                    placeholder = tree_master.attach_new_node("treeInstance")
                    placeholder.set_pos(0, step, 0)
                    tree.instance_to(placeholder)
                for i in range(amount):
                    step = i * offset
                    placeholder = tree_master.attach_new_node("treeInstance")
                    placeholder.set_pos(0, -step, 0)
                    tree.instance_to(placeholder)
                tree_master.flatten_light()

    def set_gpu_instancing_to(self, scene, pattern, placeholder):
        if (scene and isinstance(scene, NodePath)
                and isinstance(pattern, str)
                and isinstance(placeholder, str)):
            # Find the asset object, we are going to in instance this object
            # multiple times
            # Collect all instances
            prefab = render.find("**/{0}".format(pattern))
            if prefab:

                matrices = []
                floats = []

                for elem in scene.find_all_matches("**/{0}*".format(placeholder)):

                    pos_z = prefab.get_z()
                    scale = prefab.get_scale()
                    elem.set_z(pos_z)
                    elem.set_scale(scale)

                    matrices.append(elem.get_mat(render))
                    elem.remove_node()

                # Allocate storage for the matrices, each matrix has 16 elements,
                # but because one pixel has four components, we need amount * 4 pixels.
                buffer_texture = Texture()
                buffer_texture.setup_buffer_texture(len(matrices) * 4,
                                                    Texture.T_float,
                                                    Texture.F_rgba32,
                                                    GeomEnums.UH_static)

                # Serialize matrices to floats
                ram_image = buffer_texture.modify_ram_image()
                for idx, mat in enumerate(matrices):
                    for i in range(4):
                        for j in range(4):
                            floats.append(mat.get_cell(i, j))

                # Write the floats to the texture
                data = struct.pack("f" * len(floats), *floats)
                ram_image.set_subdata(0, len(data), data)

                # Load the effect
                renderpipeline_np = self.base.game_instance["renderpipeline_np"]
                renderpipeline_np.set_effect(prefab,
                                             "{0}/Engine/Renderer/effects/basic_instancing.yaml".format(
                                                 self.game_dir), {})
                prefab.set_shader_input("InstancingData", buffer_texture)
                prefab.set_instance_count(len(matrices))
                # We have do disable culling, so that all instances stay visible
                prefab.node().set_bounds(OmniBoundingVolume())
                prefab.node().set_final(True)
