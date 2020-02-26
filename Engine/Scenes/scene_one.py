import re

from panda3d.core import *

from Engine.Collisions.collisions import Collisions
from Engine.Actors.Player.korlan import Korlan
from Engine import set_tex_transparency
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
        self.col = Collisions()
        self.render_attr = RenderAttr()
        self.korlan = Korlan()
        self.base = base
        self.render = render
        self.game_settings = base.game_settings
        self.game_dir = base.game_dir
        self.game_cfg = base.game_cfg
        self.game_cfg_dir = base.game_cfg_dir
        self.game_settings_filename = base.game_settings_filename
        self.cfg_path = {"game_config_path":
                         "{0}/{1}".format(self.game_cfg_dir, self.game_settings_filename)}

    def asset_load(self, path, mode, name, axis, rotation, scale):
        if isinstance(mode, str) and mode == "menu":
            if (isinstance(path, str)
                    and isinstance(name, str)
                    and isinstance(axis, list)
                    and isinstance(rotation, list)
                    and isinstance(scale, list)):

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
                scene = self.base.loader.load_model(path)
                scene.set_name(name)
                scene.reparent_to(self.render)
                scene.set_scale(self.scale_x, self.scale_y, self.scale_z)
                scene.set_pos(pos_x, pos_y, pos_z)
                scene.set_hpr(scene, rot_h, 0, 0)

                if name == 'Grass':
                    scene.flatten_strong()

                # Panda3D 1.10 doesn't enable alpha blending for textures by default
                set_tex_transparency(scene)

                render.set_attrib(LightRampAttrib.make_hdr1())

                if self.game_settings['Main']['postprocessing'] == 'off':
                    # Set Lights and Shadows
                    self.render_attr.set_shadows(scene, render)
                    # self.render_attr.set_ssao(scene)

                return scene

        elif isinstance(mode, str) and mode == "game":
            if (isinstance(path, str)
                    and isinstance(name, str)
                    and isinstance(axis, list)
                    and isinstance(rotation, list)
                    and isinstance(scale, list)):

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
                scene = self.base.loader.load_model(path)
                scene.set_name(name)
                scene.reparent_to(self.render)
                scene.set_scale(self.scale_x, self.scale_y, self.scale_z)
                scene.set_pos(pos_x, pos_y, pos_z)
                scene.set_hpr(scene, rot_h, 0, 0)

                if name == 'Grass':
                    scene.flatten_strong()

                # Panda3D 1.10 doesn't enable alpha blending for textures by default
                set_tex_transparency(scene)

                render.set_attrib(LightRampAttrib.make_hdr1())

                if self.game_settings['Main']['postprocessing'] == 'off':
                    # Set Shaders and Shadows
                    self.render_attr.set_shadows(scene, render)
                    # self.render_attr.set_ssao(scene)

                return scene

    def env_load(self, path, mode, name, axis, rotation, scale, type):
        if isinstance(mode, str) and mode == "menu":
            if (isinstance(path, str)
                    and isinstance(name, str)
                    and isinstance(axis, list)
                    and isinstance(rotation, list)
                    and isinstance(scale, list)
                    and isinstance(type, str)):

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
                    scene = self.base.loader.load_model(path)
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
                    scene = self.base.loader.load_model(path)
                    scene.set_name(name)
                    scene.reparent_to(self.render)
                    scene.set_scale(self.scale_x, self.scale_y, self.scale_z)
                    scene.set_pos(pos_x, pos_y, pos_z)
                    scene.set_hpr(scene, rot_h, 0, 0)
                elif self.type == 'mountains':

                    # Load the scene.
                    scene = self.base.loader.load_model(path)
                    scene.set_name(name)
                    scene.reparent_to(self.render)
                    scene.set_scale(self.scale_x, self.scale_y, self.scale_z)
                    scene.set_pos(pos_x, pos_y, pos_z)
                    scene.set_hpr(scene, rot_h, 0, 0)
                else:

                    # Load the scene.
                    scene = self.base.loader.load_model(path)
                    scene.set_name(name)
                    scene.reparent_to(self.render)
                    scene.set_scale(self.scale_x, self.scale_y, self.scale_z)
                    scene.set_pos(pos_x, pos_y, pos_z)
                    scene.set_hpr(scene, rot_h, 0, 0)

                # Panda3D 1.10 doesn't enable alpha blending for textures by default
                set_tex_transparency(scene)

                render.set_attrib(LightRampAttrib.make_hdr1())

                if self.game_settings['Main']['postprocessing'] == 'off':
                    # If you don't do this, none of the features
                    # listed above will have any effect. Panda will
                    # simply ignore normal maps, HDR, and so forth if
                    # shader generation is not enabled. It would be reasonable
                    # to enable shader generation for the entire game, using this call:
                    scene.set_shader_auto()

                return scene

        elif isinstance(mode, str) and mode == "game":
            if (isinstance(path, str)
                    and isinstance(name, str)
                    and isinstance(axis, list)
                    and isinstance(rotation, list)
                    and isinstance(scale, list)
                    and isinstance(type, str)):
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
                    scene = self.base.loader.load_model(path)
                    scene.set_bin('background', 1)
                    scene.set_depth_write(0)
                    scene.set_light_off()
                    scene.reparent_to(self.render)
                    scene.set_scale(self.scale_x, self.scale_y, self.scale_z)
                    scene.set_pos(pos_x, pos_y, pos_z)
                    scene.set_pos(self.base.camera, 0, 0, 0)
                    scene.set_hpr(scene, rot_h, 0, 0)
                else:

                    # Load the scene.
                    scene = self.base.loader.load_model(path)
                    scene.set_name(name)
                    scene.reparent_to(self.render)
                    scene.set_scale(self.scale_x, self.scale_y, self.scale_z)
                    scene.set_pos(pos_x, pos_y, pos_z)
                    scene.set_hpr(scene, rot_h, 0, 0)

                # Panda3D 1.10 doesn't enable alpha blending for textures by default
                set_tex_transparency(scene)

                render.set_attrib(LightRampAttrib.make_hdr1())

                if self.game_settings['Main']['postprocessing'] == 'off':
                    # If you don't do this, none of the features
                    # listed above will have any effect. Panda will
                    # simply ignore normal maps, HDR, and so forth if
                    # shader generation is not enabled. It would be reasonable
                    # to enable shader generation for the entire game, using this call:
                    scene.set_shader_auto()

                return scene
