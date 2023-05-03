import struct

from panda3d.bullet import BulletCapsuleShape, BulletRigidBodyNode, ZUp
from panda3d.core import NodePath, LODNode
from panda3d.core import Texture, GeomEnums, OmniBoundingVolume


class GPUInstancing:
    """
    This class implements GPU Instancing for foliage assets
    """
    def __init__(self):
        self.base = base
        self.matrices = []
        self.floats = []
        self.base.game_instance["gpu_instancing_cls"] = self

    def construct_prefab_lod(self, pattern):
        prefab_lod = LODNode("{0}_LODNode".format(pattern))
        prefab_lod_np = NodePath(prefab_lod)
        prefab_lod_np.reparent_to(self.base.game_instance['foliage_np'])
        return prefab_lod, prefab_lod_np

    def setup_prefab_lod(self, prefab, prefab_lod_np, prefab_lod):
        prefab.reparent_to(prefab_lod_np)

        if "LOD0" in prefab.get_name():
            prefab_lod.add_switch(50, 0.0)
        elif "LOD1" in prefab.get_name():
            prefab_lod.add_switch(500.0, 50.0)
        elif "LOD2" in prefab.get_name():
            prefab_lod.add_switch(1000.0, 500.0)
        elif "LOD3" in prefab.get_name():
            prefab_lod.add_switch(1500.0, 1000.0)
        elif "LOD4" in prefab.get_name():
            prefab_lod.add_switch(999999.0, 1500.0)

    def _populate_instances(self, scene, placeholder, prefab, asset_type):
        if self.base.game_settings['Main']['pbr_renderer'] == 'on':
            matrices = []
            floats = []
            for i, node_path in enumerate(scene.find_all_matches("**/{0}*".format(placeholder))):
                matrices.append(node_path.get_mat(render))
                self._add_colliders(prefab=prefab,
                                    node_path=node_path,
                                    asset_type=asset_type,
                                    limit=100,
                                    index=i)

            buffer_texture = self._allocate_texture_storage(matrices, floats)
            self._visualize(prefab, matrices, buffer_texture)

    def populate_instance(self, prefab):
        if self.base.game_settings['Main']['pbr_renderer'] == 'on':
            if len(self.matrices) > 0:
                del self.matrices
                self.matrices = []
            if len(self.floats) > 0:
                del self.floats
                self.floats = []

            node_path = NodePath("{0}_instance".format(prefab.get_name()))
            self.matrices.append(node_path.get_mat(render))

            self.add_collider(prefab=prefab,
                              node_path=node_path)

            buffer_texture = self._allocate_texture_storage(self.matrices, self.floats)
            self._visualize(prefab, self.matrices, buffer_texture)

    def _add_colliders(self, prefab, node_path, asset_type, limit, index):
        if asset_type == "tree":
            if limit is not None and index < limit or limit is None:
                # calculate trunk's width and height
                min, max = prefab.get_tight_bounds()
                size = max - min
                actual_width = size[1]/size[1]
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
        renderpipeline_np = self.base.game_instance["renderpipeline_np"]
        renderpipeline_np.set_effect(prefab,
                                     "{0}/Engine/Renderer/effects/basic_instancing.yaml".format(
                                         self.base.game_dir),
                                     {"render_gbuffer": True,
                                      "render_forward": False,
                                      "render_shadow": True,
                                      "alpha_testing": True,
                                      "normal_mapping": True})
        prefab.set_shader_input("InstancingData", buffer_texture)
        prefab.flatten_light()
        prefab.set_instance_count(len(matrices))
        # We have do disable culling, so that all instances stay visible
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

            # Define prefab LOD and reparent to render node
            prefab_lod, prefab_lod_np = self.construct_prefab_lod(pattern=pattern)

            # Find the asset object, we are going to in instance this object
            # multiple times
            prefabs = scene.find_all_matches("**/{0}*".format(pattern))
            if prefabs is not None:
                for prefab in prefabs:
                    if "LODNode" not in prefab.get_name():
                        self.setup_prefab_lod(prefab=prefab,
                                               prefab_lod_np=prefab_lod_np,
                                               prefab_lod=prefab_lod)

                        self._populate_instances(scene, placeholder, prefab, asset_type)"""
