import math
import json
import struct
from os.path import exists
from random import random

from direct.task.TaskManagerGlobal import taskMgr
from panda3d.bullet import BulletCapsuleShape
from panda3d.bullet import BulletRigidBodyNode
from panda3d.bullet import ZUp
from panda3d.core import NodePath
from panda3d.core import LODNode
from panda3d.core import Texture, GeomEnums, OmniBoundingVolume


class GPUInstancing:
    """
    This class implements GPU Instancing for foliage assets
    """

    def __init__(self):
        self.base = base
        self.render = render
        self.base.game_instance["gpu_instancing_cls"] = self
        self._is_tree = False
        self._total_instances = 0
        self._instances = []
        self._instances_pos = []

        self._json_trees_plh = None
        self._json_grass_plh = None
        self._json_cat_tails_plh = None
        self._json_daisies_plh = None
        self._json_papavers_plh = None
        self._json_tulips_plh = None
        self._json_wild_blue_phloxs_plh = None

        self._trees_plh_json_path = "Assets/Placeholders/trees_plh.json"
        self._grass_plh_json_path = "Assets/Placeholders/grass_plh.json"
        self._cat_tails_plh_json_path = "Assets/Placeholders/cat_tails_plh.json"
        self._daisies_plh_json_path = "Assets/Placeholders/daisies_plh.json"
        self._papavers_plh_json_path = "Assets/Placeholders/papavers_plh.json"
        self._tulips_plh_json_path = "Assets/Placeholders/tulips_plh.json"
        self._wild_blue_phloxs_plh_path = "Assets/Placeholders/wild_blue_phloxs_plh.json"

    def construct_prefab_lod(self, pattern):
        prefab_lod = LODNode("{0}_LODNode".format(pattern))
        prefab_lod_np = NodePath(prefab_lod)
        prefab_lod_np.reparent_to(self.base.game_instance['foliage_np'])
        return prefab_lod, prefab_lod_np

    def setup_prefab_lod(self, prefab, prefab_lod_np, prefab_lod):
        if "LOD0" in prefab.get_name():
            prefab_lod.add_switch(50.0, 0.0)
        elif "LOD1" in prefab.get_name():
            prefab_lod.add_switch(500.0, 50.0)
        elif "LOD2" in prefab.get_name():
            prefab_lod.add_switch(1000.0, 500.0)
        elif "LOD3" in prefab.get_name():
            prefab_lod.add_switch(1500.0, 1000.0)
        elif "LOD4" in prefab.get_name():
            prefab_lod.add_switch(2000.0, 1500.0)

    def _populate_instances(self, scene, placeholder, prefab, asset_type):
        if self.base.game_settings['Main']['pbr_renderer'] == 'on':
            matrices = []
            floats = []
            for i, node_path in enumerate(scene.find_all_matches("**/{0}*".format(placeholder))):
                if asset_type == "tree":
                    prefab.set_scale(0.5)
                    node_path.set_scale(0.5)
                matrices.append(node_path.get_mat(render))

                pos = node_path.get_pos(render)
                self._instances_pos.append(pos)
                self._instances.append(node_path)

                self._add_colliders(prefab=prefab,
                                    node_path=node_path,
                                    asset_type=asset_type,
                                    limit=None,
                                    index=i)

            if self.base.game_settings['Debug']['set_debug_mode'] == 'YES':
                self._total_instances += len(matrices)
                print("Loaded", self._total_instances, "instances!")

            buffer_texture = self._allocate_texture_storage(matrices, floats)
            self._visualize(prefab, matrices, buffer_texture)

    def populate_instances_with_brush(self, prefab, pos, count, density):
        if self.base.game_settings['Main']['pbr_renderer'] == 'on':
            matrices = []
            floats = []

            for i in range(count):
                node_path = NodePath("{0}_instance".format(prefab.get_name()))
                node_path.set_x(render, pos[0] + random() * int(density))
                node_path.set_y(render, pos[1] + random() * int(density))
                matrices.append(node_path.get_mat(render))

                if "LOD0" in node_path.get_name():
                    self.add_collider(prefab=prefab,
                                      node_path=node_path)

            buffer_texture = self._allocate_texture_storage(matrices, floats)
            self._visualize(prefab, matrices, buffer_texture)

    def _add_colliders(self, prefab, node_path, asset_type, limit, index):
        if asset_type == "tree":
            if limit is not None and index < limit or limit is None:
                # calculate trunk's width and height
                min, max = prefab.get_tight_bounds()
                size = max - min
                actual_width = size[1] / size[1]
                trunk_width = actual_width / 2
                width = trunk_width
                height = size[2]

                # Add rigidbodies to place them physically
                physics_world_np = self.base.game_instance['physics_world_np']
                name = "{0}:BS".format(prefab.get_name())
                node_path_rb = node_path.attach_new_node(BulletRigidBodyNode(name))
                capsule = BulletCapsuleShape(width, height, ZUp)
                node_path_rb.node().set_mass(0.0)
                node_path_rb.node().add_shape(capsule)
                physics_world_np.attach(node_path_rb.node())
                node_path.set_pos(0, 0, -1)
                node_path_rb.set_collide_mask(1)

    def add_collider(self, prefab, node_path):
        # calculate trunk's width and height
        min, max = prefab.get_tight_bounds()
        size = max - min
        actual_width = size[1] / size[1]
        trunk_width = actual_width / 2
        width = trunk_width
        height = size[2]

        # Add rigidbodies to place them physically
        physics_world_np = self.base.game_instance['physics_world_np']
        name = "{0}:BS".format(prefab.get_name())
        node_path_rb = node_path.attach_new_node(BulletRigidBodyNode(name))
        capsule = BulletCapsuleShape(width, height, ZUp)
        node_path_rb.node().set_mass(0.0)
        node_path_rb.node().add_shape(capsule)
        physics_world_np.attach(node_path_rb.node())
        node_path.set_pos(0, 0, -1)
        node_path_rb.set_collide_mask(1)

    def _allocate_texture_storage(self, matrices, floats):
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

        return buffer_texture

    def _visualize(self, prefab, matrices, buffer_texture):
        # Load the effect
        if self._is_tree:
            is_render_shadow = True
        else:
            is_render_shadow = False

        renderpipeline_np = self.base.game_instance["renderpipeline_np"]
        renderpipeline_np.set_effect(prefab,
                                     "{0}/Engine/Renderer/effects/basic_instancing.yaml".format(
                                         self.base.game_dir),
                                     {"render_gbuffer": True,
                                      "render_forward": False,
                                      "render_shadow": is_render_shadow,
                                      "alpha_testing": True,
                                      "normal_mapping": True})
        prefab.set_shader_input("InstancingData", buffer_texture)
        prefab.set_instance_count(len(matrices))
        prefab.node().set_bounds(OmniBoundingVolume())
        prefab.node().set_final(True)

    def set_gpu_instancing_to(self, scene, asset_type, pattern, placeholder):
        """
        Sets GPU instancing for particular foliage asset
        :param scene:
        :param asset_type:
        :param pattern:
        :param placeholder:
        :return:
        """
        if (scene and isinstance(scene, NodePath)
                and isinstance(asset_type, str)
                and isinstance(pattern, str)
                and isinstance(placeholder, str)):

            if asset_type == "tree":
                self._is_tree = True
            else:
                self._is_tree = False

            # Define prefab LOD and reparent to render node
            prefab_lod, prefab_lod_np = self.construct_prefab_lod(pattern=pattern)

            # Find the asset object, we are going to in instance this object
            # multiple times
            if self.base.game_settings['Debug']['set_editor_mode'] == 'NO':
                prefabs = scene.find_all_matches("**/{0}*".format(pattern))
                if prefabs is not None:
                    for prefab in prefabs:
                        if "LODNode" not in prefab.get_name():
                            prefab.reparent_to(prefab_lod_np)
                            self.setup_prefab_lod(prefab=prefab,
                                                  prefab_lod_np=prefab_lod_np,
                                                  prefab_lod=prefab_lod)

                if prefab_lod_np.get_num_children() > 0:
                    self._populate_instances(scene, placeholder, prefab_lod_np, asset_type)

    def load_foliage(self):
        """ Load foliage set-up data for GPU instancing
        """

        self.base.game_instance['foliage_np'] = render.attach_new_node("LODs_Tree")

        self._json_trees_plh = None
        if exists(self._trees_plh_json_path):
            with open(self._trees_plh_json_path, "r") as file:
                self._json_trees_plh = json.load(file)

        self._json_grass_plh = None
        if exists(self._grass_plh_json_path):
            with open(self._grass_plh_json_path, "r") as file:
                self._json_grass_plh = json.load(file)

        self._json_cat_tails_plh = None
        if exists(self._cat_tails_plh_json_path):
            with open(self._cat_tails_plh_json_path, "r") as file:
                self._json_cat_tails_plh = json.load(file)

        self._json_daisies_plh = None
        if exists(self._daisies_plh_json_path):
            with open(self._daisies_plh_json_path, "r") as file:
                self._json_daisies_plh = json.load(file)

        self._json_papavers_plh = None
        if exists(self._papavers_plh_json_path):
            with open(self._papavers_plh_json_path, "r") as file:
                self._json_papavers_plh = json.load(file)

        self._json_tulips_plh = None
        if exists(self._tulips_plh_json_path):
            with open(self._tulips_plh_json_path, "r") as file:
                self._json_tulips_plh = json.load(file)

        self._json_wild_blue_phloxs_plh = None
        if exists(self._wild_blue_phloxs_plh_path):
            with open(self._wild_blue_phloxs_plh_path, "r") as file:
                self._json_wild_blue_phloxs_plh = json.load(file)

    def _set_placeholder_nodepath(self, current_json_plh, scene_pos, gaps):
        if current_json_plh is not None:
            for key, values in zip(current_json_plh.keys(), current_json_plh.values()):
                np = NodePath(key)
                np.reparent_to(self.base.game_instance["world_np"])
                np.set_pos(scene_pos.x + values[0], scene_pos.y + values[1], scene_pos.z + values[2] - gaps)

    def setup_foliage(self):
        """ Set up foliage with GPU instancing
        """

        # Enable camera frustum culling
        base.cam.node().setCullBounds(base.cam.node().getLens().makeBounds())
        base.cam.node().setFinal(True)

        render.setDepthTest(True)
        render.setDepthWrite(True)

        self._instances_pos = []
        self._instances = []
        self.load_foliage()

        scene_pos = self.base.game_instance["scene_np"].get_pos()
        json_placeholders = [self._json_trees_plh,
                             self._json_grass_plh,
                             self._json_cat_tails_plh,
                             self._json_daisies_plh,
                             self._json_papavers_plh,
                             self._json_tulips_plh,
                             self._json_wild_blue_phloxs_plh]

        for json_placeholder in json_placeholders:
            self._set_placeholder_nodepath(current_json_plh=json_placeholder,
                                           scene_pos=scene_pos,
                                           gaps=0.1)

        for landscape_chunk in self.base.game_instance["scenes_np"]:
            chunk_scene_pos = landscape_chunk.get_pos()
            for json_placeholder in json_placeholders:
                self._set_placeholder_nodepath(current_json_plh=json_placeholder,
                                               scene_pos=chunk_scene_pos,
                                               gaps=0.1)

        # Trees Instancing
        self.set_gpu_instancing_to(scene=render,
                                   asset_type="tree",
                                   pattern="AlaskaCedar_1",
                                   placeholder="tree_empty")
        # Grass Instancing
        self.set_gpu_instancing_to(scene=render,
                                   pattern="Grass_1",
                                   asset_type="foliage",
                                   placeholder="grass_1_empty")
        self.set_gpu_instancing_to(scene=render,
                                   pattern="Grass_2",
                                   asset_type="foliage",
                                   placeholder="grass_2_empty")
        self.set_gpu_instancing_to(scene=render,
                                   pattern="Grass_3",
                                   asset_type="foliage",
                                   placeholder="grass_3_empty")
        self.set_gpu_instancing_to(scene=render,
                                   pattern="Daisy_1",
                                   asset_type="foliage",
                                   placeholder="daisy_1_empty")
        self.set_gpu_instancing_to(scene=render,
                                   pattern="Daisy_2",
                                   asset_type="foliage",
                                   placeholder="daisy_2_empty")
        self.set_gpu_instancing_to(scene=render,
                                   pattern="Daisy_3",
                                   asset_type="foliage",
                                   placeholder="daisy_3_empty")
        self.set_gpu_instancing_to(scene=render,
                                   pattern="Cattail_1",
                                   asset_type="foliage",
                                   placeholder="cat_tail_1_empty")
        self.set_gpu_instancing_to(scene=render,
                                   pattern="Cattail_2",
                                   asset_type="foliage",
                                   placeholder="cat_tail_2_empty")
        self.set_gpu_instancing_to(scene=render,
                                   pattern="Cattail_3",
                                   asset_type="foliage",
                                   placeholder="cat_tail_3_empty")
        self.set_gpu_instancing_to(scene=render,
                                   pattern="Papaver_1",
                                   asset_type="foliage",
                                   placeholder="papaver_1_empty")
        self.set_gpu_instancing_to(scene=render,
                                   pattern="Papaver_2",
                                   asset_type="foliage",
                                   placeholder="papaver_2_empty")
        self.set_gpu_instancing_to(scene=render,
                                   pattern="Papaver_3",
                                   asset_type="foliage",
                                   placeholder="papaver_3_empty")
        self.set_gpu_instancing_to(scene=render,
                                   pattern="Tulip_1",
                                   asset_type="foliage",
                                   placeholder="tulip_1_empty")
        self.set_gpu_instancing_to(scene=render,
                                   pattern="Tulip_2",
                                   asset_type="foliage",
                                   placeholder="tulip_2_empty")
        self.set_gpu_instancing_to(scene=render,
                                   pattern="Tulip_3",
                                   asset_type="foliage",
                                   placeholder="tulip_3_empty")
        self.set_gpu_instancing_to(scene=render,
                                   pattern="WildBluePhlox_1",
                                   asset_type="foliage",
                                   placeholder="wild_blue_phlox_1_empty")

        self.set_gpu_instancing_to(scene=render,
                                   pattern="WildBluePhlox_2",
                                   asset_type="foliage",
                                   placeholder="wild_blue_phlox_2_empty")

        self.set_gpu_instancing_to(scene=render,
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

        # Add a task to update the culling
        # taskMgr.add(self.update_culling, "update_culling")

    def update_culling(self, task):
        # Check if the model is in the camera's view frustum
        for model in self._instances:
            if self.IsInView(model):
                model.show()
            else:
                model.hide()

            return task.cont

    def IsInView(self, object):
        lensBounds = base.cam.node().getLens().makeBounds()
        bounds = object.getBounds()
        bounds.xform(object.getParent().getMat(base.cam))
        return lensBounds.contains(bounds)

