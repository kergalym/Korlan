import json

from panda3d.core import *
from panda3d.core import Vec3
from random import random

from direct.task.TaskManagerGlobal import taskMgr
from panda3d.bullet import BulletSphereShape
from panda3d.bullet import BulletGhostNode
from panda3d.bullet import BulletRigidBodyNode
from panda3d.bullet import BulletTriangleMeshShape
from panda3d.bullet import BulletTriangleMesh
from panda3d.bullet import ZUp
from panda3d.bullet import BulletCapsuleShape

from Engine.Quests.social_quests import SocialQuests

from Engine.Scenes.npc_list_level1 import npc_ids

from direct.actor.Actor import Actor

from Engine.Renderer.gpu_instancing import GPUInstancing

from Engine.Actors.Player.player_controller import PlayerController
from Engine.Actors.Player.state import PlayerState

from Settings.Input.keyboard import Keyboard
from Settings.Input.mouse import Mouse

from Engine.Actors.NPC.state import NpcState

if "1.11" in PandaSystem.get_version_string():
    from panda3d.navigation import NavMeshNode
    from panda3d.navigation import NavMeshQuery
    from panda3d.navigation import NavMeshBuilder


class AsyncLevelLoading:

    def __init__(self):
        self.base = base
        self.render = render
        self.social_quests = None
        self.game_settings = base.game_settings
        self.game_dir = base.game_dir
        self.world_nodepath = None

        # NavMeshBuilder is a class that is responsible
        # for building the polygon meshes and navigation meshes.
        self.builder = None
        self.navmesh = None

        self.navmeshnode = None
        self.navmeshnodepath = None

        # Define the NavMeshQuery instance
        self.navmesh_query = None

        """ Player Params"""
        self.korlan = None
        self.korlan_bs = None
        self.korlan_start_pos = None
        self.korlan_life_perc = None

        self.taskMgr = taskMgr

        self.kbd = Keyboard()
        self.mouse = Mouse()

        self.gpu_instancing = GPUInstancing()

        self.controller = PlayerController()
        self.state = PlayerState()
        self.base.actor_is_dead = False
        self.base.actor_is_alive = False
        self.base.actor_play_rate = 1.0

        """ NPC Params """
        self.npc_state = NpcState()
        self.actor = None

        self.base.accept("setup_foliage", self.setup_foliage)

    def set_level_nav(self, scene_name):
        if scene_name and isinstance(scene_name, str):
            self.builder = NavMeshBuilder()
            # Take NodePath as input. This method only uses
            # the collision nodes that are under this node.
            navmesh_scenes = self.base.navmesh_scene_collector()
            scene_name = "{0}_navmesh".format(scene_name)
            navmesh_scene_np = self.base.loader.load_model(navmesh_scenes[scene_name])
            navmesh_scene_np.reparent_to(render)
            navmesh_scene_np.hide()

            if hasattr(self.builder, "from_coll_node_path"):
                self.builder.from_coll_node_path(navmesh_scene_np)

            self.builder.params.actor_radius = 1
            self.navmesh = self.builder.build()

            # Add an untracked collision mesh.
            self.navmesh.add_coll_node_path(navmesh_scene_np, tracked=False)

            self.navmesh.update()

            self.navmeshnode = NavMeshNode("scene", self.navmesh)
            self.navmeshnodepath: NodePath = navmesh_scene_np.attach_new_node(self.navmeshnode)
            self.base.game_instance["level_navmesh_np"] = self.navmeshnodepath

            # Uncomment the line below to save the generated navmesh to file.
            # self.navmeshnodepath.write_bam_file("scene_navmesh.bam")

            # Uncomment the following section to read the generated navmesh from file.
            # self.navmeshnodepath.remove_node()
            # self.navmeshnodepath = self.loader.load_model("scene_navmesh.bam")
            # self.navmeshnodepath.reparent_to(self.scene)
            # self.navmeshnode: NavMeshNode = self.navmeshnodepath.node()
            # self.navmesh = self.navmeshnode.get_nav_mesh()

            # Initialize the NavMeshQuery that we will use.
            self.navmesh_query = NavMeshQuery(self.navmesh)
            self.base.game_instance["navmesh"] = self.navmesh
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

    def set_cpu_instancing_to(self, scene, asset_type, pattern, placeholder):
        if (scene and isinstance(scene, NodePath)
                and isinstance(asset_type, str)
                and isinstance(pattern, str)
                and isinstance(placeholder, str)):
            # Find the asset object, we are going to in instance this object
            # multiple times
            prefab = scene.find("**/{0}".format(pattern))
            tree_master = scene.attach_new_node('TreeMaster')
            if prefab is not None:

                if asset_type == "tree":
                    # Add rigidbody to place them physically
                    physics_world_np = self.base.game_instance['physics_world_np']
                    np_bs_name = "{0}:BS".format(prefab.get_name())
                    np_rb_np = prefab.attach_new_node(BulletRigidBodyNode(np_bs_name))
                    width = 3
                    height = 1
                    capsule = BulletCapsuleShape(width, height, ZUp)
                    np_rb_np.node().add_shape(capsule)
                    physics_world_np.attach(np_rb_np.node())
                    prefab.set_z(-1)

                for np in scene.find_all_matches("**/{0}*".format(placeholder)):
                    # set random pos for placeholders
                    random_pos = np.get_pos() + Vec3(random(), random(), 0)
                    np.set_pos(random_pos)

                    # make a copy of instance
                    prefab.copy_to(tree_master)
                    if placeholder == "tree_empty":
                        prefab.set_pos(np.get_pos() + Vec3(np.get_x() + 2, np.get_y() + 2, -0))
                    elif placeholder == "foliage_empty":
                        prefab.set_pos(np.get_pos())
                        prefab.set_scale(7)
                    # np.remove_node()
                    np.hide()

                    if asset_type == "tree":
                        # Add rigidbodies to place them physically
                        physics_world_np = self.base.game_instance['physics_world_np']
                        np_bs_name = "{0}:BS".format(prefab.get_name())
                        np_rb_np = prefab.attach_new_node(BulletRigidBodyNode(np_bs_name))
                        width = 3
                        height = 1
                        capsule = BulletCapsuleShape(width, height, ZUp)
                        np_rb_np.node().add_shape(capsule)
                        physics_world_np.attach(np_rb_np.node())
                        prefab.set_z(-1)
            # join tree
            tree_master.flattenStrong()

    def save_player_parts(self, parts):
        if self.korlan and isinstance(self.base.game_instance["player_parts"], list):
            for name in parts:
                self.base.game_instance["player_parts"].append(name)

    def get_bs_auto(self, obj, type_):
        if obj and isinstance(type_, str):
            bool_ = False
            if hasattr(obj.node(), "get_geom"):
                geom = obj.node().get_geom(0)
                mesh = BulletTriangleMesh()
                mesh.add_geom(geom)

                if type_ == 'dynamic':
                    bool_ = True
                if type_ == 'static':
                    bool_ = False

                shape = BulletTriangleMeshShape(mesh, dynamic=bool_)
                return shape

    def setup_foliage(self):
        """ Set up foliage with GPU instancing
        """

        self.base.game_instance['foliage_np'] = render.attach_new_node("LODs_Tree")

        json_trees_plh = None
        with open("Assets/Placeholders/trees_plh.json", "r") as file:
            json_trees_plh = json.load(file)

        json_grass_plh = None
        with open("Assets/Placeholders/grass_plh.json", "r") as file:
            json_grass_plh = json.load(file)

        json_cat_tails_plh = None
        with open("Assets/Placeholders/cat_tails_plh.json", "r") as file:
            json_cat_tails_plh = json.load(file)

        json_daisies_plh = None
        with open("Assets/Placeholders/daisies_plh.json", "r") as file:
            json_daisies_plh = json.load(file)

        json_papavers_plh = None
        with open("Assets/Placeholders/papavers_plh.json", "r") as file:
            json_papavers_plh = json.load(file)

        json_tulips_plh = None
        with open("Assets/Placeholders/tulips_plh.json", "r") as file:
            json_tulips_plh = json.load(file)

        json_wild_blue_phloxs_plh = None
        with open("Assets/Placeholders/wild_blue_phloxs_plh.json", "r") as file:
            json_wild_blue_phloxs_plh = json.load(file)

        for key, values in zip(json_trees_plh.keys(), json_trees_plh.values()):
            np = NodePath(key)
            np.reparent_to(self.base.game_instance["world_np"])
            np.set_pos(values[0], values[1], values[2])

        for key, values in zip(json_grass_plh.keys(), json_grass_plh.values()):
            np = NodePath(key)
            np.reparent_to(self.base.game_instance["world_np"])
            np.set_pos(values[0], values[1], values[2])

        for key, values in zip(json_cat_tails_plh.keys(), json_cat_tails_plh.values()):
            np = NodePath(key)
            np.reparent_to(self.base.game_instance["world_np"])
            np.set_pos(values[0], values[1], values[2])

        for key, values in zip(json_daisies_plh.keys(), json_daisies_plh.values()):
            np = NodePath(key)
            np.reparent_to(self.base.game_instance["world_np"])
            np.set_pos(values[0], values[1], values[2])

        for key, values in zip(json_papavers_plh.keys(), json_papavers_plh.values()):
            np = NodePath(key)
            np.reparent_to(self.base.game_instance["world_np"])
            np.set_pos(values[0], values[1], values[2])

        for key, values in zip(json_tulips_plh.keys(), json_tulips_plh.values()):
            np = NodePath(key)
            np.reparent_to(self.base.game_instance["world_np"])
            np.set_pos(values[0], values[1], values[2])

        for key, values in zip(json_wild_blue_phloxs_plh.keys(), json_wild_blue_phloxs_plh.values()):
            np = NodePath(key)
            np.reparent_to(self.base.game_instance["world_np"])
            np.set_pos(values[0], values[1], values[2])

        # Trees Instancing
        self.gpu_instancing.set_gpu_instancing_to(scene=render,
                                                  asset_type="tree",
                                                  pattern="AlaskaCedar_1",
                                                  placeholder="tree_empty")
        # Grass Instancing
        self.gpu_instancing.set_gpu_instancing_to(scene=render,
                                                  pattern="Grass_1",
                                                  asset_type="foliage",
                                                  placeholder="grass_1_empty")
        self.gpu_instancing.set_gpu_instancing_to(scene=render,
                                                  pattern="Grass_2",
                                                  asset_type="foliage",
                                                  placeholder="grass_2_empty")
        self.gpu_instancing.set_gpu_instancing_to(scene=render,
                                                  pattern="Grass_3",
                                                  asset_type="foliage",
                                                  placeholder="grass_3_empty")
        self.gpu_instancing.set_gpu_instancing_to(scene=render,
                                                  pattern="Daisy_1",
                                                  asset_type="foliage",
                                                  placeholder="daisy_1_empty")
        self.gpu_instancing.set_gpu_instancing_to(scene=render,
                                                  pattern="Daisy_2",
                                                  asset_type="foliage",
                                                  placeholder="daisy_2_empty")
        self.gpu_instancing.set_gpu_instancing_to(scene=render,
                                                  pattern="Daisy_3",
                                                  asset_type="foliage",
                                                  placeholder="daisy_3_empty")
        self.gpu_instancing.set_gpu_instancing_to(scene=render,
                                                  pattern="Cattail_1",
                                                  asset_type="foliage",
                                                  placeholder="cat_tail_1_empty")
        self.gpu_instancing.set_gpu_instancing_to(scene=render,
                                                  pattern="Cattail_2",
                                                  asset_type="foliage",
                                                  placeholder="cat_tail_2_empty")
        self.gpu_instancing.set_gpu_instancing_to(scene=render,
                                                  pattern="Cattail_3",
                                                  asset_type="foliage",
                                                  placeholder="cat_tail_3_empty")
        self.gpu_instancing.set_gpu_instancing_to(scene=render,
                                                  pattern="Papaver_1",
                                                  asset_type="foliage",
                                                  placeholder="papaver_1_empty")
        self.gpu_instancing.set_gpu_instancing_to(scene=render,
                                                  pattern="Papaver_2",
                                                  asset_type="foliage",
                                                  placeholder="papaver_2_empty")
        self.gpu_instancing.set_gpu_instancing_to(scene=render,
                                                  pattern="Papaver_3",
                                                  asset_type="foliage",
                                                  placeholder="papaver_3_empty")
        self.gpu_instancing.set_gpu_instancing_to(scene=render,
                                                  pattern="Tulip_1",
                                                  asset_type="foliage",
                                                  placeholder="tulip_1_empty")
        self.gpu_instancing.set_gpu_instancing_to(scene=render,
                                                  pattern="Tulip_2",
                                                  asset_type="foliage",
                                                  placeholder="tulip_2_empty")
        self.gpu_instancing.set_gpu_instancing_to(scene=render,
                                                  pattern="Tulip_3",
                                                  asset_type="foliage",
                                                  placeholder="tulip_3_empty")
        self.gpu_instancing.set_gpu_instancing_to(scene=render,
                                                  pattern="WildBluePhlox_1",
                                                  asset_type="foliage",
                                                  placeholder="wild_blue_phlox_1_empty")

        self.gpu_instancing.set_gpu_instancing_to(scene=render,
                                                  pattern="WildBluePhlox_2",
                                                  asset_type="foliage",
                                                  placeholder="wild_blue_phlox_2_empty")

        self.gpu_instancing.set_gpu_instancing_to(scene=render,
                                                  pattern="WildBluePhlox_3",
                                                  asset_type="foliage",
                                                  placeholder="wild_blue_phlox_3_empty")

        """ OPTIMIZATIONS """
        for np in render.find_all_matches("**/tree_empty*"):
            np.remove_node()
        for np in render.find_all_matches("**/grass_*_empty*"):
            np.remove_node()
        for np in render.find_all_matches("**/cat_tail_*_empty*"):
            np.remove_node()
        for np in render.find_all_matches("**/papaver_*_empty*"):
            np.remove_node()
        for np in render.find_all_matches("**/tulip_*_empty*"):
            np.remove_node()
        for np in render.find_all_matches("**/daisy_*_empty*"):
            np.remove_node()
        for np in render.find_all_matches("**/wild_blue_phlox_*_empty*"):
            np.remove_node()

        # taskMgr.add(self._occlusion_per_asset, "occl")

    def _occlusion_per_asset(self, task):
        for np in self.base.game_instance['foliage_np'].get_children():
            for child in np.get_children():
                print(child.get_pos(render) - base.camera.get_pos(render))
                if child.get_distance(base.camera) >= 1000.0:
                    # We have do disable culling, so that all instances stay visible
                    child.hide()
                if child.get_distance(base.camera) < 1000.0:
                    child.show()

        return task.cont

    async def async_load_level(self, scene_name, player_name, scale, player_pos, culling,
                               suffix, level_npc_assets, level_npc_axis, assets, animation):
        if (isinstance(scene_name, str)
                and isinstance(player_name, str)
                and isinstance(player_pos, list)
                and isinstance(scale, float)
                and isinstance(culling, bool)
                and isinstance(animation, list)
                and level_npc_assets
                and level_npc_axis
                and assets
                and animation
                and isinstance(culling, bool)):

            """ SCENE """
            self.base.game_instance['scene_is_loaded'] = False
            scene = None

            # ts = TextureStage("lightmap")
            # lightmap = base.loader.load_texture("tex/ligtmap.png")
            # ts.setTexcoordName("lightmap")
            # landscape.set_texture(ts, lightmap)

            # Disable the disk cache
            opts = LoaderOptions()
            opts.flags |= LoaderOptions.LF_no_disk_cache

            self.world_nodepath = render.find("**/World")
            if self.world_nodepath:
                # Load the scene.
                path = assets['{0}_{1}'.format(scene_name, suffix)]
                scene = await self.base.loader.load_model(path, loaderOptions=opts, blocking=False)
                scene.reparent_to(self.base.game_instance['lod_np'])

                # toggle texture compression for textures to compress them
                # before load into VRAM
                # self.base.toggle_texture_compression(scene)

                alaska_cedar = self.base.assets_collector()["alaska_cedar"]
                cat_tails = self.base.assets_collector()["cat_tails"]
                daisies = self.base.assets_collector()["daisies"]
                grass = self.base.assets_collector()["grass"]
                tail_grass = self.base.assets_collector()["tail_grass"]
                papaver = self.base.assets_collector()["papaver"]
                tulips = self.base.assets_collector()["tulips"]
                wild_blue_phlox = self.base.assets_collector()["wild_blue_phlox"]

                trees = [alaska_cedar]

                plants = [
                    cat_tails,
                    daisies,
                    grass,
                    tail_grass,
                    papaver,
                    tulips,
                    wild_blue_phlox
                ]

                for tree_path in trees:
                    tree = await self.base.loader.load_model(tree_path, loaderOptions=opts, blocking=False)
                    tree.reparent_to(self.base.game_instance['lod_np'])

                for plant_path in plants:
                    plant = await self.base.loader.load_model(plant_path, loaderOptions=opts, blocking=False)
                    plant.reparent_to(self.base.game_instance['lod_np'])

                # LOD quality preset
                for lod_qk in self.base.game_instance["lod_quality"]:
                    if self.game_settings['Main']['details'] == lod_qk:
                        lod_qv = self.base.game_instance["lod_quality"][lod_qk]
                        self.base.game_instance['lod_np'].node().add_switch(lod_qv[0],
                                                                            lod_qv[1])

                # Set sRGB
                self.base.set_textures_srgb(scene, True)

                scene.set_name(scene_name)

                # scene.set_pos(0, 0, 0)
                # scene.set_hpr(scene, 0, 0, 0)

                # Make scene global
                self.base.game_instance['scene_np'] = scene

            if self.base.game_instance["renderpipeline_np"]:
                self.base.game_instance['renderpipeline_np'].prepare_scene(scene)

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

            self.base.game_instance['scene_is_loaded'] = True

            # Load colliders for this level
            coll_scene_np = NodePath("Collisions")
            coll_scene_np.reparent_to(self.world_nodepath)
            colliders_dict = base.assets_collider_collector()
            for key in colliders_dict:
                coll_path = base.assets_collider_collector()[key]
                coll_scene = await self.base.loader.load_model(coll_path, loaderOptions=opts, blocking=False)
                coll_scene_name = key
                coll_scene.set_name(coll_scene_name)
                coll_scene.reparent_to(coll_scene_np)
                coll_scene.hide()

            # Add Bullet colliders for this scene
            physics_attr = self.base.game_instance["physics_attr_cls"]
            if hasattr(physics_attr, "set_static_object_colliders"):
                physics_attr.set_static_object_colliders(scene=scene)

            if "1.11" in PandaSystem.get_version_string():
                self.set_level_nav(scene_name)

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

            """ PLAYER """
            if self.game_settings['Debug']['set_editor_mode'] == 'NO':
                self.mouse.set_mouse_mode(mode="absolute")

            self.base.game_instance['player_is_loaded'] = False

            # Korlan_empty is the first asset containing only skeleton (armature).
            # Next ones are Korlan_body, Korlan_armor, Korlan_pants and Korlan_boots,
            # all of them contain armature with weighted meshes.
            # Each of them follows the previous one and assembles in this order.
            # This allows to avoid unwanted shifting of the meshes while playing the animation.
            assets = self.base.assets_collector()

            part_names = ["modelRoot", "body", "helmet", "armor", "pants", "boots"]
            asset_names = ["Korlan_empty", "Korlan_body", "Korlan_helmet",
                           "Korlan_armor", "Korlan_pants", "Korlan_boots"]

            actor_parts_dict = {}

            anims_full_dict = {
                part_names[0]: animation[1],
                part_names[1]: animation[1],
                part_names[2]: animation[1],
                part_names[3]: animation[1],
                part_names[4]: animation[1],
                part_names[5]: animation[1]
            }

            # load player parts separately
            cloak = self.base.loader.load_model(assets["Korlan_cloak"])
            self.base.game_instance["actors_clothes"][player_name] = [cloak]
            self.base.game_instance["actors_clothes_path"][player_name] = assets["Korlan_cloak"]

            empty = self.base.loader.load_model(assets[asset_names[0]])
            body = self.base.loader.load_model(assets[asset_names[1]])
            helmet = self.base.loader.load_model(assets[asset_names[2]])
            armor = self.base.loader.load_model(assets[asset_names[3]])
            pants = self.base.loader.load_model(assets[asset_names[4]])
            boots = self.base.loader.load_model(assets[asset_names[5]])

            actor_parts_dict[part_names[0]] = empty
            actor_parts_dict[part_names[1]] = body
            actor_parts_dict[part_names[2]] = helmet
            actor_parts_dict[part_names[3]] = armor
            actor_parts_dict[part_names[4]] = pants
            actor_parts_dict[part_names[5]] = boots

            # and compose them into one
            self.korlan = Actor(actor_parts_dict, anims_full_dict)

            # toggle texture compression for textures to compress them
            # before load into VRAM
            # self.base.toggle_texture_compression(self.korlan)

            self.korlan.reparent_to(render)

            self.base.game_instance['player_is_loaded'] = True

            self.korlan.set_name(player_name)
            self.korlan.set_scale(scale)
            self.korlan_start_pos = LPoint3f(player_pos[0], player_pos[1], player_pos[2])
            self.korlan.set_pos(self.korlan_start_pos)

            # Save actor parts
            self.save_player_parts(part_names)

            # Save actor joints
            j_bones = []
            for joint in self.korlan.get_joints():
                if joint is not None:
                    bone = self.korlan.exposeJoint(None, "modelRoot", joint.get_name())
                    j_bones.append(bone)
            self.korlan.set_python_tag("joint_bones", j_bones)

            # Enable blending to fix cloth poking
            self.korlan.set_blend(frameBlend=True)

            # Set sRGB
            self.base.set_textures_srgb(self.korlan, True)

            # Set two sided, since some model may be broken
            self.korlan.set_two_sided(culling)

            # Panda3D 1.10 doesn't enable alpha blending for textures by default
            # self.korlan.set_transparency(True)

            # Hardware skinning
            self.base.game_instance['render_attr_cls'].set_hardware_skinning(self.korlan, True)

            # Make actor global
            self.base.game_instance['player_ref'] = self.korlan

            if self.base.game_instance["renderpipeline_np"]:
                self.base.game_instance['renderpipeline_np'].prepare_scene(self.korlan)

            # Set allowed weapons list
            self.base.game_instance["weapons"] = [
                "sword",
                "bow_kazakh",
            ]

            # Usable Items List
            _items = []

            _pos = [Vec3(0.4, 8.0, 5.2),
                    Vec3(0.4, 8.0, 5.2),
                    Vec3(0.4, 8.0, 5.2),
                    Vec3(0.4, 8.0, 5.2)]

            _hpr = [Vec3(0, 0, 0),
                    Vec3(0, 0, 0),
                    Vec3(0, 0, 0),
                    Vec3(0, 0, 0)]

            usable_item_list = {
                "name": _items,
                "pos": _pos,
                "hpr": _hpr
            }

            self.korlan.set_python_tag("usable_item_list", usable_item_list)

            # Set Used Item Record
            self.korlan.set_python_tag("used_item_np", None)
            self.korlan.set_python_tag("is_item_ready", False)
            self.korlan.set_python_tag("is_item_using", False)
            self.korlan.set_python_tag("is_close_to_use_item", False)
            self.korlan.set_python_tag("is_close_to_chest", False)
            self.korlan.set_python_tag("current_item_prop", None)

            self.korlan.set_python_tag("first_attack", False)

            # Keep Player hitboxes here
            self.korlan.set_python_tag("actor_hitboxes", None)

            # Set Player current hitbox
            self.korlan.set_python_tag("current_hitbox", None)

            # Set Player Priority
            self.korlan.set_python_tag("priority", 0)

            # Keep collider shape here
            self.korlan.set_python_tag("collider_shape", None)

            # Set Player Parameters
            self.state.set_state(actor=self.korlan)

            # Initialize Player Controller
            self.controller.player_actions_init(self.korlan, animation[0])

            """ Setup NPC and Physics"""
            for actor, id, _type, _class, axis_actor in zip(level_npc_assets['name'],
                                                            npc_ids,
                                                            level_npc_assets['type'],
                                                            level_npc_assets['class'],
                                                            level_npc_axis):
                if actor == axis_actor:
                    name = actor

                    # TODO: Use same asset for any numbered npc which have same type.
                    #       Keep it until assets become game ready
                    actor = self.base.get_number_stripped_asset_name(actor)

                    path = assets['{0}_{1}'.format(actor, suffix)]
                    axis = level_npc_axis[axis_actor]

                    if (isinstance(path, str)
                            and isinstance(name, str)
                            and isinstance(_type, str)
                            and isinstance(axis, list)
                            and isinstance(animation, list)
                            and isinstance(culling, bool)):

                        pos_x = axis[0]
                        pos_y = axis[1]
                        pos_z = axis[2]

                        cloak = await self.base.loader.load_model(assets["Korlan_cloak"], loaderOptions=opts,
                                                                  blocking=False)
                        self.base.game_instance["actors_clothes"][name] = [cloak]
                        self.base.game_instance["actors_clothes_path"][name] = assets["Korlan_cloak"]

                        self.actor = await self.base.loader.load_model(path, loaderOptions=opts, blocking=False)
                        self.actor = Actor(self.actor, animation[1])

                        self.actor.set_name(name)
                        self.actor.set_scale(scale)
                        self.actor.set_pos(pos_x, pos_y, pos_z)

                        # toggle texture compression for textures to compress them
                        # before load into VRAM
                        # self.base.toggle_texture_compression(self.actor)

                        self.actor.reparent_to(self.base.game_instance['lod_np'])

                        # LOD quality preset
                        for lod_qk in self.base.game_instance["lod_quality"]:
                            if self.game_settings['Main']['details'] == lod_qk:
                                lod_qv = self.base.game_instance["lod_quality"][lod_qk]
                                self.base.game_instance['lod_np'].node().add_switch(lod_qv[0],
                                                                                    lod_qv[1])

                        # Set sRGB
                        self.base.set_textures_srgb(self.actor, True)

                        # Set two sided, since some model may be broken
                        self.actor.set_two_sided(culling)

                        # Panda3D 1.10 doesn't enable alpha blending for textures by default
                        self.actor.set_transparency(True)

                        # Hardware skinning
                        self.base.game_instance['render_attr_cls'].set_hardware_skinning(self.actor, True)

                        # Make actor global
                        self.base.game_instance['actors_ref'][name] = self.actor

                        if self.base.game_instance["renderpipeline_np"]:
                            self.base.game_instance['renderpipeline_np'].prepare_scene(self.actor)

                        # Save actor joints
                        j_bones = []
                        for joint in self.actor.get_joints():
                            if joint is not None:
                                bone = self.actor.exposeJoint(None, "modelRoot", joint.get_name())
                                j_bones.append(bone)
                        self.actor.set_python_tag("joint_bones", j_bones)

                        # Keep my hitboxes here
                        self.actor.set_python_tag("actor_hitboxes", None)

                        # Add Bullet collider for this actor
                        physics_attr = self.base.game_instance["physics_attr_cls"]
                        if hasattr(physics_attr, "set_actor_collider"):
                            physics_attr.set_actor_collider(actor=self.actor,
                                                            col_name='{0}:BS'.format(self.actor.get_name()),
                                                            shape="capsule",
                                                            type=_type)

                        self.base.game_instance["npc_state_cls"] = self.npc_state

                        # Set HUD and tags
                        self.npc_state.set_npc_hud(actor=self.actor)

                        # Set NPC type
                        self.actor.set_python_tag("npc_name", name)
                        self.actor.set_python_tag("npc_type", _type)

                        # Set NPC Movement types: walk or run
                        self.actor.set_python_tag("move_type", "walk")

                        # Set NPC id
                        self.actor.set_python_tag("npc_id", id)

                        # Set NPC class
                        self.actor.set_python_tag("npc_class", _class)

                        # Keep enemy distance here
                        self.actor.set_python_tag("enemy_distance", None)

                        # Keep enemy hitbox distance here
                        self.actor.set_python_tag("enemy_hitbox_distance", None)

                        # Directive number
                        self.actor.set_python_tag("directive_num", 0)

                        # Set Target Nodepath
                        self.actor.set_python_tag("target_np", None)

                        if "Horse" not in name and "Animal" not in name:
                            # Set NPC allowed weapons list
                            a_weapons = [
                                "sword",
                                "bow",
                            ]
                            self.actor.set_python_tag("allowed_weapons", a_weapons)

                            # Set bow arrows count
                            self.actor.set_python_tag("arrow_count", 0)

                            # Usable Items List
                            _items = []

                            _pos = [Vec3(0.4, 8.0, 5.2),
                                    Vec3(0.4, 8.0, 5.2),
                                    Vec3(0.4, 8.0, 5.2),
                                    Vec3(0.4, 8.0, 5.2)]

                            _hpr = [Vec3(0, 0, 0),
                                    Vec3(0, 0, 0),
                                    Vec3(0, 0, 0),
                                    Vec3(0, 0, 0)]

                            usable_item_list = {
                                "name": _items,
                                "pos": _pos,
                                "hpr": _hpr
                            }

                            self.actor.set_python_tag("usable_item_list", usable_item_list)

                            # Set Used Item Record
                            self.actor.set_python_tag("used_item_np", None)
                            self.actor.set_python_tag("is_item_ready", False)
                            self.actor.set_python_tag("is_item_using", False)
                            self.actor.set_python_tag("current_item_prop", None)

                            # Set NPC Horse Tag
                            self.actor.set_python_tag("mounted_horse", None)

                            # Set the current task or quest name keeping tag
                            self.actor.set_python_tag("current_task", None)

                            # Set NPC which potentially could be enemy
                            self.actor.set_python_tag("enemy_npc_ref", None)
                            self.actor.set_python_tag("enemy_npc_bs", None)

                            # Set NPC Priority
                            self.actor.set_python_tag("priority", 0)

                            # Set NPC current hitbox
                            self.actor.set_python_tag("current_hitbox", None)

                        # Set NPC Controller state
                        self.actor.set_python_tag("ai_controller_state", True)

                        # Set NPC Parameters
                        self.npc_state.setup_npc_state(actor=self.actor)

            self.base.game_instance['actors_are_loaded'] = True
