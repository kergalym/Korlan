from direct.task.TaskManagerGlobal import taskMgr
from panda3d.bullet import BulletSphereShape, BulletGhostNode, BulletRigidBodyNode, BulletTriangleMeshShape, \
    BulletTriangleMesh
from panda3d.core import *
from Engine.Quests.social_quests import SocialQuests

from panda3d.navigation import NavMeshNode
from panda3d.navigation import NavMeshQuery
from panda3d.navigation import NavMeshBuilder

from direct.actor.Actor import Actor
from panda3d.core import Vec3

from Engine.Actors.Player.player_controller import PlayerController
from Engine.Actors.Player.state import PlayerState

from Settings.Input.keyboard import Keyboard
from Settings.Input.mouse import Mouse

from Engine.Actors.NPC.state import NpcState

from Engine.Scenes.npc_list_level1 import npc_ids

import struct


class AsyncLevelLoad:

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
        self.controller = PlayerController()
        self.state = PlayerState()
        self.base.actor_is_dead = False
        self.base.actor_is_alive = False
        self.base.actor_play_rate = 1.0

        """ NPC Params """
        self.npc_state = NpcState()
        self.actor = None

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

    def scene_toggle(self, scene):
        if scene.is_hidden():
            scene.show()
        else:
            scene.hide()

    def set_cpu_instancing_to(self, scene, pattern, placeholder):
        if (scene and isinstance(scene, NodePath)
                and isinstance(pattern, str)
                and isinstance(placeholder, str)):
            # Find the asset object, we are going to in instance this object
            # multiple times
            # Collect all instances
            prefab = scene.find("**/{0}".format(pattern))
            if prefab:
                tree_master = scene.attach_new_node('TreeMaster')
                for elem in scene.find_all_matches("**/{0}*".format(placeholder)):
                    pos_z = prefab.get_z()
                    scale = prefab.get_scale()
                    elem.set_z(pos_z)
                    elem.set_scale(scale)

                    cpuinst = tree_master.attach_new_node("treeInstance")
                    cpuinst.set_pos(elem.get_pos())
                    prefab.instance_to(cpuinst)

    def set_gpu_instancing_to(self, scene, pattern, placeholder):
        if (scene and isinstance(scene, NodePath)
                and isinstance(pattern, str)
                and isinstance(placeholder, str)):
            # Find the asset object, we are going to in instance this object
            # multiple times
            # Collect all instances
            prefab = scene.find("**/{0}".format(pattern))
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

            # load testing landscape
            """landscape_path = assets["lvl_landscape"]
            landscape = await self.base.loader.load_model(landscape_path, blocking=False, noCache=True)
            landscape.reparent_to(self.base.game_instance['lod_np'])"""

            # Load the scene.
            path = assets['{0}_{1}'.format(scene_name, suffix)]
            scene = await self.base.loader.load_model(path, blocking=False, noCache=True)

            self.world_nodepath = render.find("**/World")
            if self.world_nodepath:

                # toggle texture compression for textures to compress them
                # before load into VRAM
                # self.base.toggle_texture_compression(scene)

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

                scene.set_name(scene_name)
                # scene.set_scale(scale)
                scene.set_pos(0, 0, 0)
                scene.set_hpr(scene, 0, 0, 0)

                # Make scene global
                self.base.game_instance['scene_np'] = scene

            if self.base.game_instance["renderpipeline_np"]:
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
            self.set_cpu_instancing_to(scene=scene,
                                       pattern="tree_rig",
                                       placeholder="tree_empty")

            """self.set_gpu_instancing_to(scene=scene,
                                       pattern="tree_rig",
                                       placeholder="tree_empty")"""

            self.base.game_instance['scene_is_loaded'] = True

            # Load colliders for this level
            coll_scene_np = NodePath("Collisions")
            coll_scene_np.reparent_to(self.world_nodepath)
            colliders_dict = base.assets_collider_collector()
            for key in colliders_dict:
                coll_path = base.assets_collider_collector()[key]
                coll_scene = await self.base.loader.load_model(coll_path, blocking=False, noCache=True)
                coll_scene_name = key
                coll_scene.set_name(coll_scene_name)
                coll_scene.reparent_to(coll_scene_np)
                coll_scene.hide()

            # Add Bullet colliders for this scene
            physics_attr = self.base.game_instance["physics_attr_cls"]
            if hasattr(physics_attr, "set_static_object_colliders"):
                physics_attr.set_static_object_colliders(scene=scene)

            # Construct navigation system
            if render.find("**/lvl_landscape"):
                scene_name = render.find("**/lvl_landscape").get_name()

            self.set_level_nav(scene_name)

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

                        cloak = await self.base.loader.load_model(assets["Korlan_cloak"], blocking=False, noCache=True)
                        self.base.game_instance["actors_clothes"][name] = [cloak]
                        self.base.game_instance["actors_clothes_path"][name] = assets["Korlan_cloak"]

                        self.actor = await self.base.loader.load_model(path, blocking=False, noCache=True)
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
