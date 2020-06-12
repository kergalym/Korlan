from os.path import exists
from pathlib import Path, PurePath
from os import walk

from direct.gui.DirectGui import OnscreenText
from panda3d.core import *
from panda3d.core import FontPool, TextNode
from Engine.Render.rpcore import PointLight


class RenderAttr:

    def __init__(self):
        self.game_dir = str(Path.cwd())
        self.fonts = base.fonts_collector()
        # instance of the abstract class
        self.font = FontPool
        self.texture = None
        self.game_settings = base.game_settings
        if hasattr(base, "render_pipeline") and base.render_pipeline:
            self.render_pipeline = base.render_pipeline
        self.world = None
        self.set_color = 0.2
        self.shadow_size = 1024
        self.render = None

        # Set time of day
        self.elapsed_seconds = 0
        self.minutes = 0
        self.hour = 0

        """ Texts & Fonts"""
        # self.menu_font = self.fonts['OpenSans-Regular']
        self.menu_font = self.fonts['JetBrainsMono-Regular']

        if self.game_settings['Main']['postprocessing'] == 'on':
            if self.render_pipeline:
                # TODO: Remove the time declaration after Menu Scene is constructed
                self.render_pipeline.daytime_mgr.time = "8:45"

        self.time_text_ui = OnscreenText(text="",
                                         pos=(-1.8, -0.7),
                                         scale=0.04,
                                         fg=(255, 255, 255, 0.9),
                                         font=self.font.load_font(self.menu_font),
                                         align=TextNode.ALeft,
                                         mayChange=True)

    def set_daytime_clock_task(self, task):
        if (not base.game_mode
                and base.menu_mode):
            self.time_text_ui.hide()
            return task.done
        else:
            if self.time_text_ui:
                self.time_text_ui.show()

        if self.game_settings['Main']['postprocessing'] == 'on':
            if self.render_pipeline:
                time = str(self.game_settings['Misc']['daytime'])
                self.render_pipeline.daytime_mgr.time = time
                self.elapsed_seconds = round(globalClock.getRealTime())

                self.minutes = self.elapsed_seconds // 60

                hour = time.split(':')
                hour = int(hour[0])
                self.hour = hour
                self.hour += self.minutes // 60

                if self.minutes < 10:
                    self.time_text_ui.setText("{0}:0{1}".format(self.hour, self.minutes))
                    self.render_pipeline.daytime_mgr.time = "{0}:0{1}".format(self.hour, self.minutes)
                elif self.minutes > 9:
                    self.time_text_ui.setText("{0}:{1}".format(self.hour, self.minutes))
                    self.render_pipeline.daytime_mgr.time = "{0}:{1}".format(self.hour, self.minutes)

        return task.cont

    def shader_collector(self):
        """ Function    : shader_collector

            Description : Collect shader set.

            Input       : None

            Output      : None

            Return      : Dictionary
        """
        shader_path = str(PurePath(self.game_dir, "Engine", "Shaders"))
        shader_path = Filename.from_os_specific("{0}/".format(shader_path))
        shader_dirs = []
        shaders = {}

        if exists(shader_path):
            for root, dirs, files in walk(shader_path, topdown=True):
                # Get last directory to make it list key
                d = root.split("/").pop()
                shader_dirs.append(d)

            for root, dirs, files in walk(shader_path, topdown=True):
                for d in shader_dirs:
                    for file in files:
                        path = str(PurePath("{0}/".format(root), file))
                        path = Filename.from_os_specific(path).getFullpath()
                        if d in path:
                            if "frag" in file:
                                key = "{0}_{1}".format(d, "frag")
                                shaders[key] = path
                            if "vert" in file:
                                key = "{0}_{1}".format(d, "vert")
                                shaders[key] = path
            return shaders

    def get_all_shaders(self, shaders):
        """ Function    : get_all_shaders

            Description : Get loaded shader set.

            Input       : dict

            Output      : None

            Return      : Dictionary
        """
        if shaders and isinstance(shaders, dict):
            loaded_shaders = {}
            for k in shaders:
                # Find shader for vert and frag files
                # to construct a dict of the loaded shaders
                name = k.split("_")[0]
                shader = Shader.load(Shader.SL_GLSL,
                                     vertex=shaders["{0}_vert".format(name)],
                                     fragment=shaders["{0}_frag".format(name)])
                # Contains shader memory addresses
                loaded_shaders[name] = shader
            return loaded_shaders

    def set_shadows(self, obj, render):
        if obj and render:
            self.render = render
            # If you don't do this, none of the features
            # listed above will have any effect. Panda will
            # simply ignore normal maps, HDR, and so forth if
            # shader generation is not enabled. It would be reasonable
            # to enable shader generation for the entire game, using this call:
            # obj.set_shader_auto()
            base.shaderenable = 1

            # TODO Fix me!
            ready_shaders = self.get_all_shaders(self.shader_collector())
            obj.set_shader(ready_shaders['Shadows'])

    def set_lighting(self, name, render, pos, hpr, color, task):
        if (render
                and name
                and isinstance(name, str)
                and isinstance(pos, list)
                and isinstance(hpr, list)
                and isinstance(color, list)
                and isinstance(task, str)):

            self.render = render

            if task == 'attach':
                if self.game_settings['Main']['postprocessing'] == 'off':
                    if render.find("**/{0}".format(name)).is_empty():
                        light = DirectionalLight(name)
                        light.set_color((color[0], color[0], color[0], 1))
                        light_np = self.render.attach_new_node(light)
                        # This light is facing backwards, towards the camera.
                        light_np.set_hpr(hpr[0], hpr[1], hpr[2])
                        light_np.set_pos(pos[0], pos[1], pos[2])
                        light_np.set_scale(100)
                        self.render.set_light(light_np)
                    else:
                        render.clearLight()

                if self.game_settings['Main']['postprocessing'] == 'on':
                    # RP doesn't have nodegraph-like structure to find and remove lights,
                    # so we check self.rp_light before adding light
                    light = PointLight()
                    light.pos = (pos[0], pos[1], pos[2])
                    light.color = (color[0], color[0], color[0])
                    light.set_color_from_temperature(3000.0)
                    light.energy = 100
                    light.ies_profile = self.render_pipeline.load_ies_profile("x_arrow.ies")
                    light.casts_shadows = True
                    light.shadow_map_resolution = 512
                    light.near_plane = 0.2
                    base.rp_lights.append(light)
                    self.render_pipeline.add_light(light)

    def clear_lighting(self):
        if base.rp_lights and self.render_pipeline.light_mgr.num_lights > 0:
            for i in range(self.render_pipeline.light_mgr.num_lights):
                for light in base.rp_lights:
                    if light:
                        base.rp_lights.remove(light)
                        self.render_pipeline.remove_light(light)

    def get_light_attributes(self):
        pass

    def set_light_attributes(self):
        pass

    def transform_scene_lights(self):
        pass
