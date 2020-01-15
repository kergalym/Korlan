"""
BSD 3-Clause License

Copyright (c) 2019, Galym Kerimbekov
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its
   contributors may be used to endorse or promote products derived from
   this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""
from panda3d.core import *
from Engine.Collisions import Collisions
from Engine.Actors.Player.korlan import Korlan
from Settings.Player.korlan_settings import Player
from Engine import set_tex_transparency
from Engine.World import World


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
        self.world = World()
        self.korlan = Korlan()
        self.player_settings = Player()
        self.base = base
        self.render = render
        self.game_settings = base.game_settings
        self.game_dir = base.game_dir
        self.game_cfg = base.game_cfg
        self.game_cfg_dir = base.game_cfg_dir
        self.game_settings_filename = base.game_settings_filename
        self.cfg_path = {"game_config_path": "{0}/{1}".format(self.game_cfg_dir, self.game_settings_filename)}

    def asset_load(self, path, mode, model, axis, rotation, scale):
        if isinstance(mode, str) and mode == "MENU_MODE":
            if (isinstance(path, str)
                    and isinstance(model, str)
                    and isinstance(axis, list)
                    and isinstance(rotation, list)
                    and isinstance(scale, list)):

                self.path = "{0}{1}".format(self.game_dir, path)
                self.game_settings = self.game_settings
                self.model = model
                pos_x = axis[0]
                pos_y = axis[1]
                pos_z = axis[2]
                rot_h = rotation[0]
                self.scale_x = scale[0]
                self.scale_y = scale[1]
                self.scale_z = scale[2]

                # Load the scene.
                scene = self.base.loader.loadModel(path)
                scene.setName(model)
                scene.reparentTo(self.render)
                scene.setScale(self.scale_x, self.scale_y, self.scale_z)
                scene.setPos(pos_x, pos_y, pos_z)
                scene.setHpr(scene, rot_h, 0, 0)

                if model == 'Grass':
                    scene.flattenStrong()

                # Panda3D 1.10 doesn't enable alpha blending for textures by default
                set_tex_transparency(scene)

                render.setAttrib(LightRampAttrib.makeHdr1())

                if self.game_settings['Main']['postprocessing'] == 'off':
                    # Set Lights and Shadows
                    self.world.set_shadows(scene, render)
                    # self.world.set_ssao(scene)
                    self.world.set_lighting(render, scene)

                return scene

        elif isinstance(mode, str) and mode == "GAME_MODE":
            if (isinstance(path, str)
                    and isinstance(model, str)
                    and isinstance(axis, list)
                    and isinstance(rotation, list)
                    and isinstance(scale, list)):

                self.path = "{0}{1}".format(self.game_dir, path)
                self.render = render
                self.model = model
                pos_x = axis[0]
                pos_y = axis[1]
                pos_z = axis[2]
                rot_h = rotation[0]
                self.scale_x = scale[0]
                self.scale_y = scale[1]
                self.scale_z = scale[2]

                # Load the scene.
                scene = self.base.loader.loadModel(path)
                scene.setName(model)
                scene.reparentTo(self.render)
                scene.setScale(self.scale_x, self.scale_y, self.scale_z)
                scene.setPos(pos_x, pos_y, pos_z)
                scene.setHpr(scene, rot_h, 0, 0)

                if model == 'Grass':
                    scene.flattenStrong()

                # Panda3D 1.10 doesn't enable alpha blending for textures by default
                set_tex_transparency(scene)

                render.setAttrib(LightRampAttrib.makeHdr1())

                if self.game_settings['Main']['postprocessing'] == 'off':
                    # Set Lights and Shadows
                    self.world.set_shadows(scene, render)
                    # self.world.set_ssao(scene)
                    self.world.set_lighting(render, scene)

                return scene

    def env_load(self, path, mode, model, axis, rotation, scale, type):
        if isinstance(mode, str) and mode == "MENU_MODE":
            if (isinstance(path, str)
                    and isinstance(model, str)
                    and isinstance(axis, list)
                    and isinstance(rotation, list)
                    and isinstance(scale, list)
                    and isinstance(type, str)):

                self.path = "{}{}".format(self.game_dir, path)
                self.render = render
                self.model = model
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
                    scene = self.base.loader.loadModel(path)
                    scene.setBin('background', 1)
                    scene.setDepthWrite(0)
                    scene.setLightOff()
                    scene.reparentTo(self.render)
                    scene.setScale(self.scale_x, self.scale_y, self.scale_z)
                    scene.setPos(pos_x, pos_y, pos_z)
                    scene.setPos(self.base.camera, 0, 0, 0)
                    scene.setHpr(scene, rot_h, 0, 0)
                elif self.type == 'ground':
                    # Load the scene.
                    scene = self.base.loader.loadModel(path)
                    scene.setName(model)
                    scene.reparentTo(self.render)
                    scene.setScale(self.scale_x, self.scale_y, self.scale_z)
                    scene.setPos(pos_x, pos_y, pos_z)
                    scene.setHpr(scene, rot_h, 0, 0)
                else:
                    # Load the scene.
                    scene = self.base.loader.loadModel(path)
                    scene.setName(model)
                    scene.reparentTo(self.render)
                    scene.setScale(self.scale_x, self.scale_y, self.scale_z)
                    scene.setPos(pos_x, pos_y, pos_z)
                    scene.setHpr(scene, rot_h, 0, 0)

                # Panda3D 1.10 doesn't enable alpha blending for textures by default
                set_tex_transparency(scene)

                render.setAttrib(LightRampAttrib.makeHdr1())

                if self.game_settings['Main']['postprocessing'] == 'off':
                    # Set the lights
                    self.world.set_lighting(self.render, scene)

                    # If you don't do this, none of the features
                    # listed above will have any effect. Panda will
                    # simply ignore normal maps, HDR, and so forth if
                    # shader generation is not enabled. It would be reasonable
                    # to enable shader generation for the entire game, using this call:
                    scene.setShaderAuto()

                return scene

        elif isinstance(mode, str) and mode == "GAME_MODE":
            if (isinstance(path, str)
                    and isinstance(model, str)
                    and isinstance(axis, list)
                    and isinstance(rotation, list)
                    and isinstance(scale, list)
                    and isinstance(type, str)):
                # Make them visible for other class members
                self.path = "{0}{1}".format(self.game_dir, path)
                self.render = render
                self.model = model
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
                    scene = self.base.loader.loadModel(path)
                    scene.setBin('background', 1)
                    scene.setDepthWrite(0)
                    scene.setLightOff()
                    scene.reparentTo(self.render)
                    scene.setScale(self.scale_x, self.scale_y, self.scale_z)
                    scene.setPos(pos_x, pos_y, pos_z)
                    scene.setPos(self.base.camera, 0, 0, 0)
                    scene.setHpr(scene, rot_h, 0, 0)
                else:
                    # Load the scene.
                    scene = self.base.loader.loadModel(path)
                    scene.setName(model)
                    scene.reparentTo(self.render)
                    scene.setScale(self.scale_x, self.scale_y, self.scale_z)
                    scene.setPos(pos_x, pos_y, pos_z)
                    scene.setHpr(scene, rot_h, 0, 0)

                # Panda3D 1.10 doesn't enable alpha blending for textures by default
                set_tex_transparency(scene)

                render.setAttrib(LightRampAttrib.makeHdr1())

                if self.game_settings['Main']['postprocessing'] == 'off':
                    # Set the lights
                    self.world.set_lighting(self.render, scene)

                    # If you don't do this, none of the features
                    # listed above will have any effect. Panda will
                    # simply ignore normal maps, HDR, and so forth if
                    # shader generation is not enabled. It would be reasonable
                    # to enable shader generation for the entire game, using this call:
                    scene.setShaderAuto()

                return scene
