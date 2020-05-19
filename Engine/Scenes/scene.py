from panda3d.core import *
from Engine.Actors.Player.korlan import Korlan
from Engine.Physics.physics import PhysicsAttr
from Engine.Render.render import RenderAttr


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
        self.task_mgr = None
        self.node_path = NodePath()
        self.render_attr = RenderAttr()
        self.korlan = Korlan()
        self.physics_attr = PhysicsAttr()
        self.base = base
        self.render = render
        self.game_settings = base.game_settings
        self.game_dir = base.game_dir
        self.game_cfg = base.game_cfg
        self.game_cfg_dir = base.game_cfg_dir
        self.game_settings_filename = base.game_settings_filename
        self.cfg_path = {"game_config_path": "{0}/{1}".format(self.game_cfg_dir,
                                                              self.game_settings_filename)}

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

            base.level_is_loaded = 0

            # Load the scene.
            scene = await self.base.loader.load_model(path, blocking=False)
            scene.set_name(name)
            scene.reparent_to(self.render)
            scene.set_scale(self.scale_x, self.scale_y, self.scale_z)
            scene.set_pos(pos_x, pos_y, pos_z)
            scene.set_hpr(scene, rot_h, 0, 0)

            # Set two sided, since some model may be broken
            scene.set_two_sided(culling)

            # Panda3D 1.10 doesn't enable alpha blending for textures by default
            scene.set_transparency(True)

            # Add collision for everything in level except sky because it's sphere we inside in
            for child in scene.get_children():
                if child.get_name() != 'Sky':
                    self.physics_attr.set_collision(obj=child, type="child", shape="auto")
                if child.get_name() != 'Grass':
                    self.physics_attr.set_collision(obj=child, type="child", shape="auto")
                if child.get_name() != 'Ground':
                    self.physics_attr.set_collision(obj=child, type="child", shape="auto")

            render.set_attrib(LightRampAttrib.make_hdr1())

            if self.game_settings['Main']['postprocessing'] == 'off':
                # Set Lights and Shadows
                # self.render_attr.set_shadows(scene, render)
                pass

            # If you don't do this, none of the features
            # listed above will have any effect. Panda will
            # simply ignore normal maps, HDR, and so forth if
            # shader generation is not enabled. It would be reasonable
            # to enable shader generation for the entire game, using this call:
            # scene.set_shader_auto()

            base.level_is_loaded = 1

    # TODO: Remove set_asset async call block further
    async def set_asset(self, path, mode, name, axis, rotation, scale, culling):
        if isinstance(mode, str) and mode == "menu":
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

                # Load the scene.
                scene = await self.base.loader.load_model(path, blocking=False)
                scene.set_name(name)
                scene.reparent_to(self.render)
                scene.set_scale(self.scale_x, self.scale_y, self.scale_z)
                scene.set_pos(pos_x, pos_y, pos_z)
                scene.set_hpr(scene, rot_h, 0, 0)

                if name == 'Grass':
                    # scene.flatten_strong()
                    pass

                # Set two sided, since some model may be broken
                scene.set_two_sided(culling)

                # Panda3D 1.10 doesn't enable alpha blending for textures by default
                scene.set_transparency(True)

                render.set_attrib(LightRampAttrib.make_hdr1())

                if self.game_settings['Main']['postprocessing'] == 'off':
                    # Set Lights and Shadows
                    # self.render_attr.set_shadows(scene, render)
                    pass

                # If you don't do this, none of the features
                # listed above will have any effect. Panda will
                # simply ignore normal maps, HDR, and so forth if
                # shader generation is not enabled. It would be reasonable
                # to enable shader generation for the entire game, using this call:
                # scene.set_shader_auto()

        elif isinstance(mode, str) and mode == "game":
            if (isinstance(path, str)
                    and isinstance(name, str)
                    and isinstance(axis, list)
                    and isinstance(rotation, list)
                    and isinstance(scale, list)
                    and isinstance(culling, bool)):

                self.path = "{0}{1}".format(self.game_dir, path)
                self.render = render
                self.model = name
                pos_x = axis[0]
                pos_y = axis[1]
                pos_z = axis[2]
                rot_h = rotation[0]
                self.scale_x = scale[0]
                self.scale_y = scale[1]
                self.scale_z = scale[2]

                # Load the scene.
                scene = await self.base.loader.load_model(path, blocking=False)
                scene.set_name(name)
                scene.reparent_to(self.render)
                scene.set_scale(self.scale_x, self.scale_y, self.scale_z)
                scene.set_pos(pos_x, pos_y, pos_z)
                scene.set_hpr(scene, rot_h, 0, 0)

                if name == 'Grass':
                    # scene.flatten_strong()
                    pass

                # Set two sided, since some model may be broken
                scene.set_two_sided(culling)

                # Panda3D 1.10 doesn't enable alpha blending for textures by default
                scene.set_transparency(True)

                # Add collision for everything in level except sky because it's sphere we inside in
                if scene.get_name() == "Nomad_house" and not render.find('**/yurt').is_empty():
                    self.physics_attr.set_collision(obj=render.find('**/yurt'), type="child", shape="auto")
                    self.physics_attr.set_collision(obj=render.find('**/asadal'), type="child", shape="auto")

                if scene.get_name() == "Box":
                    self.physics_attr.set_collision(obj=scene, type="item", shape="cube")

                render.set_attrib(LightRampAttrib.make_hdr1())

                if self.game_settings['Main']['postprocessing'] == 'off':
                    # Set Shaders and Shadows
                    # self.render_attr.set_shadows(scene, render)
                    pass

    async def set_env(self, path, mode, name, axis, rotation, scale, type, culling):
        if isinstance(mode, str) and mode == "menu":
            if (isinstance(path, str)
                    and isinstance(name, str)
                    and isinstance(axis, list)
                    and isinstance(rotation, list)
                    and isinstance(scale, list)
                    and isinstance(type, str)
                    and isinstance(culling, bool)):

                self.path = "{}{}".format(self.game_dir, path)
                self.render = render
                self.model = name
                pos_x = axis[0]
                pos_y = axis[1]
                pos_z = axis[2]
                rot_h = rotation[0]
                self.scale_x = scale[0]
                self.scale_y = scale[1]
                self.scale_z = scale[2]
                self.type = type

                if self.type == 'skybox':
                    # Load the scene.
                    scene = self.base.loader.load_model(path, blocking=True)
                    scene.set_name(name)
                    scene.set_bin('background', 1)
                    scene.set_depth_write(0)
                    scene.set_light_off()
                    scene.reparent_to(self.render)
                    scene.set_scale(self.scale_x, self.scale_y, self.scale_z)
                    scene.set_pos(pos_x, pos_y, pos_z)
                    scene.set_pos(self.base.camera, 0, 0, 0)
                    scene.set_hpr(scene, rot_h, 0, 0)
                elif self.type == 'ground':
                    # Load the scene.
                    scene = self.base.loader.load_model(path, blocking=True)
                    scene.set_name(name)
                    scene.reparent_to(self.render)
                    scene.set_scale(self.scale_x, self.scale_y, self.scale_z)
                    scene.set_pos(pos_x, pos_y, pos_z)
                    scene.set_hpr(scene, rot_h, 0, 0)
                elif self.type == 'mountains':
                    # Load the scene.
                    scene = self.base.loader.load_model(path, blocking=True)
                    scene.set_name(name)
                    scene.reparent_to(self.render)
                    scene.set_scale(self.scale_x, self.scale_y, self.scale_z)
                    scene.set_pos(pos_x, pos_y, pos_z)
                    scene.set_hpr(scene, rot_h, 0, 0)
                else:
                    # Load the scene.
                    scene = self.base.loader.load_model(path, blocking=True)
                    scene.set_name(name)
                    scene.reparent_to(self.render)
                    scene.set_scale(self.scale_x, self.scale_y, self.scale_z)
                    scene.set_pos(pos_x, pos_y, pos_z)
                    scene.set_hpr(scene, rot_h, 0, 0)

                # Set two sided, since some model may be broken
                scene.set_two_sided(culling)

                # Panda3D 1.10 doesn't enable alpha blending for textures by default
                scene.set_transparency(True)

                render.set_attrib(LightRampAttrib.make_hdr1())

                # If you don't do this, none of the features
                # listed above will have any effect. Panda will
                # simply ignore normal maps, HDR, and so forth if
                # shader generation is not enabled. It would be reasonable
                # to enable shader generation for the entire game, using this call:
                # scene.set_shader_auto()
                # self.render_attr.set_shadows(scene, render)

        elif isinstance(mode, str) and mode == "game":
            if (isinstance(path, str)
                    and isinstance(name, str)
                    and isinstance(axis, list)
                    and isinstance(rotation, list)
                    and isinstance(scale, list)
                    and isinstance(type, str)
                    and isinstance(culling, bool)):
                # Make them visible for other class members
                self.path = "{0}{1}".format(self.game_dir, path)
                self.render = render
                self.model = name
                pos_x = axis[0]
                pos_y = axis[1]
                pos_z = axis[2]
                rot_h = rotation[0]
                self.scale_x = scale[0]
                self.scale_y = scale[1]
                self.scale_z = scale[2]
                self.type = type

                if self.type == 'skybox':
                    # Load the scene.
                    scene = await self.base.loader.load_model(path, blocking=False)
                    scene.set_name(name)
                    scene.set_bin('background', 1)
                    scene.set_depth_write(0)
                    scene.set_light_off()
                    scene.reparent_to(self.render)
                    scene.set_scale(self.scale_x, self.scale_y, self.scale_z)
                    scene.set_pos(pos_x, pos_y, pos_z)
                    scene.set_pos(self.base.camera, 0, 0, 0)
                    scene.set_hpr(scene, rot_h, 0, 0)
                elif self.type == 'ground':
                    # Load the scene.
                    scene = await self.base.loader.load_model(path, blocking=False)
                    scene.set_name(name)
                    scene.reparent_to(self.render)
                    scene.set_scale(self.scale_x, self.scale_y, self.scale_z)
                    scene.set_pos(pos_x, pos_y, pos_z)
                    scene.set_hpr(scene, rot_h, 0, 0)
                elif self.type == 'mountains':
                    # Load the scene.
                    scene = await self.base.loader.load_model(path, blocking=False)
                    scene.set_name(name)
                    scene.reparent_to(self.render)
                    scene.set_scale(self.scale_x, self.scale_y, self.scale_z)
                    scene.set_pos(pos_x, pos_y, pos_z)
                    scene.set_hpr(scene, rot_h, 0, 0)
                else:
                    # Load the scene.
                    scene = await self.base.loader.load_model(path, blocking=False)
                    scene.set_name(name)
                    scene.reparent_to(self.render)
                    scene.set_scale(self.scale_x, self.scale_y, self.scale_z)
                    scene.set_pos(pos_x, pos_y, pos_z)
                    scene.set_hpr(scene, rot_h, 0, 0)

                # Set two sided, since some model may be broken
                scene.set_two_sided(culling)

                # Panda3D 1.10 doesn't enable alpha blending for textures by default
                scene.set_transparency(True)

                render.set_attrib(LightRampAttrib.make_hdr1())

                # If you don't do this, none of the features
                # listed above will have any effect. Panda will
                # simply ignore normal maps, HDR, and so forth if
                # shader generation is not enabled. It would be reasonable
                # to enable shader generation for the entire game, using this call:
                # scene.set_shader_auto()
                # self.render_attr.set_shadows(scene, render)

                return scene
