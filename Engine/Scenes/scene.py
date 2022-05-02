from direct.task.TaskManagerGlobal import taskMgr
from panda3d.core import *
from Engine.Renderer.renderer import RenderAttr
from Settings.Input.indoor_camera import IndoorCamera
from Engine.Quests.quests import Quests

# TODO UNCOMMENT WHEN R&D BECOMES PRODUCTION-READY
# from panda3d.navigation import NavMeshNode, NavMeshQuery
# from panda3d.navmeshgen import NavMeshBuilder


class SceneOne:

    def __init__(self):
        self.path = None
        self.loader = None
        self.game_settings = None
        self.render_type = None
        self.render_pipeline = None
        self.model = None
        self.axis = None
        self.rotation = None
        self.scale_x = None
        self.scale_y = None
        self.scale_z = None
        self.type = None
        self.node_path = NodePath()
        self.render_attr = RenderAttr()
        self.cam_modes = IndoorCamera()
        self.quests = Quests()
        self.base = base
        self.render = render
        self.game_settings = base.game_settings
        self.game_dir = base.game_dir
        self.game_cfg = base.game_cfg
        self.game_cfg_dir = base.game_cfg_dir
        self.game_settings_filename = base.game_settings_filename
        self.cfg_path = self.game_cfg

        # NavMeshBuilder is a class that is responsible
        # for building the polygon meshes and navigation meshes.
        self.builder = None
        self.navmesh = None

        self.navmeshnode = None
        self.navmeshnodepath = None

        # Define the NavMeshQuery instance
        self.navmesh_query = None

    def set_level_nav(self, scene):
        if scene:
            # TODO UNCOMMENT WHEN R&D BECOMES PRODUCTION-READY
            """"# NavMeshBuilder is a class that is responsible
            # for building the polygon meshes and navigation meshes.
            self.builder = NavMeshBuilder()
            # Take NodePath as input. This method only uses
            # the collision nodes that are under this node.
            self.builder.from_coll_node_path(scene)

            self.builder.actor_height = 10
            self.builder.actor_radius = 4
            self.builder.actor_max_climb = 2
            self.navmesh = self.builder.build()

            self.navmeshnode = NavMeshNode("scene", self.navmesh)
            self.navmeshnodepath: NodePath = scene.attach_new_node(self.navmeshnode)

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
            self.base.game_instance["navmesh_query"] = self.navmesh_query"""

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
            world = render.find("**/World")
            if world:

                # toggle texture compression for textures to compress them
                # before load into VRAM
                self.base.toggle_texture_compression(scene)

                scene.reparent_to(self.base.game_instance['lod_np'])

                # LOD quality preset
                for lod_qk in self.base.game_instance["lod_quality"]:
                    if self.game_settings['Main']['details'] == lod_qk:
                        lod_qv = self.base.game_instance["lod_quality"][lod_qk]
                        self.base.game_instance['lod_np'].node().add_switch(lod_qv[0],
                                                                            lod_qv[1])

                # scene.flatten_strong()
                # scene.hide()
                if self.game_settings['Debug']['set_debug_mode'] == "YES":
                    base.accept("f2", self.scene_toggle, [scene])

                scene.set_name(name)
                scene.set_scale(self.scale_x, self.scale_y, self.scale_z)
                scene.set_pos(pos_x, pos_y, pos_z)
                scene.set_hpr(scene, rot_h, 0, 0)

                # Make scene global
                self.base.game_instance['scene_np'] = scene

            if self.game_settings['Main']['postprocessing'] == 'on':
                self.render_attr.render_pipeline.prepare_scene(scene)

            if not render.find("**/Grass").is_empty():
                grass = render.find("**/Grass")
                grass.set_two_sided(True)

            # Enable lightmapping for this scene
            self.render_attr.apply_lightmap_to_scene(scene=scene, lightmap="lightmap_scene_one")

            # Set two sided, since some model may be broken
            scene.set_two_sided(culling)

            # Panda3D 1.10 doesn't enable alpha blending for textures by default
            scene.set_transparency(True)

            if self.game_settings['Main']['postprocessing'] == 'on':
                # Enable water
                self.render_attr.set_projected_water(True)

                # Enable flame
                self.render_attr.set_flame_hearth(adv_render=True, scene_np=scene, flame_scale=0.1)
                self.render_attr.set_smoke_hearth(adv_render=True, scene_np=scene, smoke_scale=0.1)
                # Enable grass
                # self.render_attr.set_grass(adv_render=True, fogcenter=Vec3(256, 256, 0), uv_offset=Vec2(0, 0))

            self.base.game_instance['scene_is_loaded'] = True

            # Add Bullet colliders for this scene
            self.base.messenger.send("add_bullet_collider")

            # Load collisions for a level
            colliders_dict = base.assets_collider_collector()
            coll_scene_name = '{0}_coll'.format(name)
            coll_path = colliders_dict[coll_scene_name]
            coll_scene = await self.base.loader.load_model(coll_path, blocking=False)
            coll_scene.set_name(coll_scene_name)
            coll_scene_np = NodePath("Collisions")
            coll_scene_np.reparent_to(world)
            coll_scene.reparent_to(coll_scene_np)
            coll_scene.hide()

            # Construct navigation system
            # self.set_level_nav(scene)

            if self.game_settings['Debug']['set_debug_mode'] == "YES":
                scene.hide()

            # Add camera triggers
            taskMgr.add(self.cam_modes.set_camera_trigger,
                        "set_camera_trigger",
                        extraArgs=[scene],
                        appendTask=True)

            # Add quest triggers
            taskMgr.add(self.quests.set_quest_trigger,
                        "set_quest_trigger",
                        extraArgs=[scene],
                        appendTask=True)

    def scene_toggle(self, scene):
        if scene.is_hidden():
            scene.show()
        else:
            scene.hide()
