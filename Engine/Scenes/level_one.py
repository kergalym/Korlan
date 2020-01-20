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
from pathlib import Path

from direct.task.TaskManagerGlobal import taskMgr
from panda3d.core import *
from Engine.Actors.Player.korlan import Korlan
from Settings.Player.korlan_settings import Player
from Engine.Scenes.scene_one import SceneOne
from Engine.world import World
from os.path import isfile, exists, join
from os import listdir, walk
import configparser
from sys import exit as sys_exit


class LevelOne:

    def __init__(self):
        self.game_mode = base.game_mode
        self.game_settings = base.game_settings
        self.game_dir = base.game_dir
        self.game_cfg = base.game_cfg
        self.game_cfg_dir = base.game_cfg_dir
        self.game_settings_filename = base.game_settings_filename
        self.cfg_path = {"game_config_path":
                         "{0}/{1}".format(self.game_cfg_dir, self.game_settings_filename)}
        self.base = base
        self.loader = base.loader
        self.node_path = NodePath()
        self.scene_one = SceneOne()
        self.world = World()
        self.korlan = Korlan()
        self.player_settings = Player()
        self.pos_x = None
        self.pos_y = None
        self.pos_z = 0.0
        self.anim = None

    def get_game_assets(self, exclude):
        asset_path = "{0}/Assets".format(Path.cwd())

        asset_paths = []
        asset_names = []

        if exists(asset_path):
            for root, dirs, files in walk(asset_path, topdown=True):
                if exclude in dirs:
                    dirs.remove(exclude)
                for file in files:
                    if '.egg' in file:
                        asset_paths.append(join(root, file))
                        asset_names.append(file.strip('.egg'))

        return {'names': asset_names, 'path': asset_paths}

    def reload_menu_scene(self):
        if self.base.game_mode:
            self.base.game_mode = False
            self.base.menu_mode = True

            taskMgr.remove("player_init")
            taskMgr.remove("mouse-look")

            assets = self.get_game_assets(exclude='Animations')

            render.find("**/Korlan").removeNode()
            render.find("**/Sky").removeNode()
            render.find("**/Grass").removeNode()
            render.find("**/Nomad_house").removeNode()
            render.find("**/Ground").removeNode()
            render.find("**/Mountains").removeNode()

            for path in assets['path']:
                self.loader.unloadModel(path)

            wp = WindowProperties()
            wp.setCursorHidden(False)
            self.base.win.requestProperties(wp)

            # Disable the camera trackball controls.
            self.base.disableMouse()

            # Disable mouse camera
            self.base.mouseMagnitude = 0
            self.base.rotateX = 0
            self.base.lastMouseX = None
            self.base.hideMouse = False
            self.base.manualRecenterMouse = False
            self.base.camera.setPos(0, 0, 0)
            self.base.camera.setHpr(0, 0, 0)
            self.base.cam.setPos(0, 0, 0)
            self.base.cam.setHpr(0, 0, 0)
            self.base.menu_scene_load()
            self.base.frame.show()

    def load_new_game(self):
        self.game_mode = True
        self.base.accept("escape", self.reload_menu_scene)
        assets = self.get_game_assets(exclude='Animations')

        render.find("**/Korlan").removeNode()
        render.find("**/Sky").removeNode()
        render.find("**/Grass").removeNode()
        render.find("**/Nomad_house").removeNode()
        render.find("**/Ground").removeNode()
        render.find("**/Mountains").removeNode()

        for path in assets['path']:
            self.loader.unloadModel(path)

        if isfile("{0}/{1}".format(self.game_cfg_dir,
                                   self.game_settings_filename)):

            try:
                self.game_settings.read("{}/{}".format(self.game_cfg_dir,
                                                       self.game_settings_filename))
                self.player_settings.set_player(self.game_settings['Main']['player'])
            except configparser.MissingSectionHeaderError:
                sys_exit("\nFile contains no section headers. Exiting...")
                sys_exit("\nFile: {0}/{1}".format(self.game_cfg_dir,
                                                  self.game_settings_filename))

        """ Assets """
        self.scene_one.env_load(path='Assets/Levels/Terrain/Sky.egg',
                                mode="game",
                                name="Sky",
                                axis=[0.0, 10.0, self.pos_z],
                                rotation=[0, 0, 0],
                                scale=[1.25, 1.25, 1.25],
                                type='skybox')

        self.scene_one.asset_load(path='Assets/Levels/Terrain/Grass.egg',
                                  mode="game",
                                  name="Grass",
                                  axis=[20.0, 10.0, self.pos_z],
                                  rotation=[0, 0, 0],
                                  scale=[1.25, 1.25, 1.25])

        self.scene_one.asset_load(path='Assets/Levels/Environment/Nomad house/Nomad_house.egg',
                                  mode="game",
                                  name="Nomad_house",
                                  axis=[0.0, 20.0, self.pos_z],
                                  rotation=[65, 0, 0],
                                  scale=[1.25, 1.25, 1.25])

        self.scene_one.env_load(path='Assets/Levels/Terrain/Ground.egg',
                                mode="game",
                                name="Ground",
                                axis=[0.0, 10.0, self.pos_z],
                                rotation=[0, 0, 0],
                                scale=[1.25, 1.25, 1.25],
                                type='ground')

        self.scene_one.env_load(path='Assets/Levels/Terrain/Mountains.egg',
                                mode="game",
                                name="Mountains",
                                axis=[0.0, 20.0, self.pos_z],
                                rotation=[0, 0, 0],
                                scale=[1.25, 1.25, 1.25],
                                type='mountains')

        self.korlan.set_actor(mode="game",
                              name="Korlan",
                              path=self.player_settings.set_player_path(self.game_dir),
                              animation=listdir('{0}/Assets/Actors/Animations/'.format(self.game_dir)),
                              axis=[0, 8.0, self.pos_z],
                              rotation=[0, 0, 0],
                              scale=[1.25, 1.25, 1.25])
