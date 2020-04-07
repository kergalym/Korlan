from os.path import exists
from pathlib import Path, PurePath
from os import walk

from panda3d.core import *


class RenderAttr:

    def __init__(self):
        self.game_dir = str(Path.cwd())
        self.world = None
        self.set_color = 0.2
        self.shadow_size = 1024
        self.render = None

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
            obj.set_shader_auto()
            base.shaderenable = 1

            # TODO Fix me!
            # ready_shaders = self.get_all_shaders(self.shader_collector())
            # obj.set_shader(ready_shaders['Shadows'])

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
                # Directional light 01
                point_light = PointLight(name)
                point_light.set_color((color[0], color[0], color[0], 1))
                point_light_np = self.render.attach_new_node(point_light)
                # This light is facing backwards, towards the camera.
                point_light_np.set_hpr(hpr[0], hpr[1], hpr[2])
                point_light_np.set_z(pos[2])
                self.render.set_light(point_light_np)

            if task == 'attach':
                # Add an ambient light
                alight = PointLight('ambientLight')
                alight.set_color((self.set_color, self.set_color, self.set_color, 1))
                alnp = self.render.attach_new_node(alight)
                self.render.set_light(alnp)
                if task == 'detach':
                    self.render.set_light_off(alnp)

    def set_ssao(self, obj):
        if obj:
            # TODO Fix me!
            ready_shaders = self.get_all_shaders(self.shader_collector())
            obj.set_shader(ready_shaders['SSAO'])
