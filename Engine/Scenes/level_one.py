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
from Engine.Actors.Player.korlan import Korlan
from Settings.Player.korlan_settings import Player
from Engine.Scenes.scene_one import SceneOne
from Engine.World import World
from os.path import isfile
from os import listdir
import configparser
from sys import exit as sys_exit


class LevelOne:

    def __init__(self):
        self.game_settings = base.game_settings
        self.game_dir = base.game_dir
        self.game_cfg = base.game_cfg
        self.game_cfg_dir = base.game_cfg_dir
        self.game_settings_filename = base.game_settings_filename
        self.cfg_path = {"game_config_path": "{0}/{1}".format(self.game_cfg_dir, self.game_settings_filename)}
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

    def load_new_game(self):
        render.find("**/Korlan").removeNode()
        render.find("**/Sky").removeNode()
        render.find("**/Grass").removeNode()
        render.find("**/Nomad_house").removeNode()
        render.find("**/Ground").removeNode()
        render.find("**/Mountains").removeNode()

        self.loader.unloadModel('{0}/Assets/Actors/Korlan/Korlan.egg'.format(self.game_dir))
        self.loader.unloadModel('{0}/Assets/Levels/Terrain/sky.egg'.format(self.game_dir))
        self.loader.unloadModel('{0}/Assets/Levels/Terrain/tress_grass.egg'.format(self.game_dir))
        self.loader.unloadModel('{0}/Assets/Levels/Environment/Nomad house/Nomad_house.egg'.format(self.game_dir))
        self.loader.unloadModel('{0}/Assets/Levels/Terrain/ground.egg'.format(self.game_dir))
        self.loader.unloadModel('{0}/Assets/Levels/Terrain/mountains.egg'.format(self.game_dir))

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
        self.scene_one.env_load('Assets/Levels/Terrain/sky.egg',
                                "GAME_MODE",
                                "Sky",
                                [0.0, 10.0, self.pos_z], [0, 0, 0], [1.25, 1.25, 1.25], 'skybox')

        self.scene_one.asset_load('Assets/Levels/Terrain/tress_grass.egg',
                                  "GAME_MODE",
                                  "Grass",
                                  [20.0, 10.0, self.pos_z], [0, 0, 0], [1.25, 1.25, 1.25])

        self.scene_one.asset_load('Assets/Levels/Environment/Nomad house/Nomad_house.egg',
                                  "GAME_MODE",
                                  "Nomad_house",
                                  [0.0, 20.0, self.pos_z], [65, 0, 0], [1.25, 1.25, 1.25])

        self.scene_one.env_load('Assets/Levels/Terrain/ground.egg',
                                "GAME_MODE",
                                "Ground",
                                [0.0, 10.0, self.pos_z], [0, 0, 0], [1.25, 1.25, 1.25], 'ground')

        self.scene_one.env_load('Assets/Levels/Terrain/mountains.egg',
                                "GAME_MODE",
                                "Mountains",
                                [0.0, 20.0, self.pos_z], [0, 0, 0], [1.25, 1.25, 1.25], 'mountains')

        self.anim = listdir('{0}/Assets/Actors/Animations/'.format(self.game_dir))

        self.korlan.set_character_game("game",
                                       "Korlan",
                                       [0.0, 8.0, self.pos_z], [0, 0, 0], [1.25, 1.25, 1.25],
                                       self.player_settings.set_player_path(self.game_dir),
                                       self.anim)
