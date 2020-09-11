from panda3d.core import *
from Engine.Actors.Player.korlan import Korlan
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
        self.korlan = Korlan()
        self.render_attr = RenderAttr()
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

            if not render.find("**/Grass").is_empty():
                grass = render.find("**/Grass")
                grass.set_two_sided(True)

            # TODO: Get Lightmap from Texture Collector
            """ts = TextureStage("lightmap")
            lightmap = base.loader.load_texture("/tmp/tex/ligtmap.png")
            ts.setTexcoordName("lightmap")

            scene.set_texture(ts, lightmap)"""

            self.base.set_textures_srgb(True)

            # Set two sided, since some model may be broken
            scene.set_two_sided(culling)

            # Panda3D 1.10 doesn't enable alpha blending for textures by default
            scene.set_transparency(True)

            render.set_attrib(LightRampAttrib.make_hdr1())

            if self.game_settings['Main']['postprocessing'] == 'off':
                # Set Lights and Shadows
                # self.render_attr.set_shadows(scene, render)

                # If you don't do this, none of the features
                # listed above will have any effect. Panda will
                # simply ignore normal maps, HDR, and so forth if
                # shader generation is not enabled. It would be reasonable
                # to enable shader generation for the entire game, using this call:
                scene.set_shader_auto()

                # Load the LOD
                self.base.level_of_details(obj=scene)
            else:                # Enable water
                self.render_attr.set_water(True, water_lvl=30.0, adv_render=False)

                # Enable grass
                # self.render_attr.set_grass(True, adv_render=False)

                # Enable flare
                # self.render_attr.set_flare(True, adv_render=False)

            base.level_is_loaded = 1

            # Load collisions for a level
            colliders_dict = base.assets_collider_collector()
            coll_scene_name = '{0}_coll'.format(name)
            coll_path = colliders_dict[coll_scene_name]
            coll_scene = await self.base.loader.load_model(coll_path, blocking=False)
            coll_scene.set_name(coll_scene_name)

            coll_scene_np = NodePath("Collisions")
            coll_scene_np.reparent_to(render)

            coll_scene.reparent_to(coll_scene_np)

            coll_scene.hide()

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

                self.base.set_textures_srgb(True)

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

                self.base.set_textures_srgb(True)

                if name == 'Grass':
                    # scene.flatten_strong()
                    pass

                # Set two sided, since some model may be broken
                scene.set_two_sided(culling)

                # Panda3D 1.10 doesn't enable alpha blending for textures by default
                scene.set_transparency(True)

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

                    self.base.set_textures_srgb(True)

                elif self.type == 'ground':
                    # Load the scene.
                    scene = self.base.loader.load_model(path, blocking=True)
                    scene.set_name(name)
                    scene.reparent_to(self.render)
                    scene.set_scale(self.scale_x, self.scale_y, self.scale_z)
                    scene.set_pos(pos_x, pos_y, pos_z)
                    scene.set_hpr(scene, rot_h, 0, 0)

                    for tex in render.findAllTextures():
                        if tex.getNumComponents() == 4:
                            tex.setFormat(Texture.F_srgb_alpha)
                        elif tex.getNumComponents() == 3:
                            tex.setFormat(Texture.F_srgb)
                elif self.type == 'mountains':
                    # Load the scene.
                    scene = self.base.loader.load_model(path, blocking=True)
                    scene.set_name(name)
                    scene.reparent_to(self.render)
                    scene.set_scale(self.scale_x, self.scale_y, self.scale_z)
                    scene.set_pos(pos_x, pos_y, pos_z)
                    scene.set_hpr(scene, rot_h, 0, 0)

                    self.base.set_textures_srgb(True)

                else:
                    # Load the scene.
                    scene = self.base.loader.load_model(path, blocking=True)
                    scene.set_name(name)
                    scene.reparent_to(self.render)
                    scene.set_scale(self.scale_x, self.scale_y, self.scale_z)
                    scene.set_pos(pos_x, pos_y, pos_z)
                    scene.set_hpr(scene, rot_h, 0, 0)

                    for tex in render.findAllTextures():
                        if tex.getNumComponents() == 4:
                            tex.setFormat(Texture.F_srgb_alpha)
                        elif tex.getNumComponents() == 3:
                            tex.setFormat(Texture.F_srgb)

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

                self.base.set_textures_srgb(True)

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

