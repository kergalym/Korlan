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
from Engine.Models.Player.korlan import Korlan
from Settings.Player.korlan_settings import Player
from Engine.Scenes.scene_01 import SceneOne
from Engine.World import World
from pathlib import Path
from os.path import isfile
import configparser
from sys import exit as sys_exit

""" Engine Built-in Objects"""

GAME_DIR = str(Path.cwd())
GAME_CFG = '{0}/Korlan - Daughter of the Steppes/settings.ini'.format(str(Path.home()))

GAME_SETTINGS = configparser.ConfigParser()
GAME_CFG_DIR = '{0}/Korlan - Daughter of the Steppes'.format(str(Path.home()))
GAME_SETTINGS_FILENAME = 'settings.ini'

""" Create game config first! """
CFG_PATH = {"game_config_path": "{0}/{1}".format(GAME_CFG_DIR, GAME_SETTINGS_FILENAME)}


class LevelOne:

    def __init__(self):
        self.loader = base.loader
        self.node_path = NodePath()
        self.scene_one = SceneOne()
        self.world = World()
        self.korlan = Korlan()
        self.player_settings = Player()
        self.pos_x = None
        self.pos_y = None
        self.pos_z = 0.0

    def load_new_game(self):

        render.find("**/Korlan").removeNode()
        render.find("**/Sky").removeNode()
        render.find("**/Grass").removeNode()
        render.find("**/Nomad_house").removeNode()
        render.find("**/Ground").removeNode()
        render.find("**/Mountains").removeNode()

        self.loader.unloadModel('{0}/Assets/Models/Korlan/Korlan.egg'.format(GAME_DIR))
        self.loader.unloadModel('{0}/Assets/Levels/Terrain/sky.egg'.format(GAME_DIR))
        self.loader.unloadModel('{0}/Assets/Levels/Terrain/tress_grass.egg'.format(GAME_DIR))
        self.loader.unloadModel('{0}/Assets/Levels/Environment/Nomad house/Nomad_house.egg'.format(GAME_DIR))
        self.loader.unloadModel('{0}/Assets/Levels/Terrain/ground.egg'.format(GAME_DIR))
        self.loader.unloadModel('{0}/Assets/Levels/Terrain/mountains.egg'.format(GAME_DIR))

        if isfile("{0}/{1}".format(GAME_CFG_DIR,
                                   GAME_SETTINGS_FILENAME)):

            try:
                GAME_SETTINGS.read("{}/{}".format(GAME_CFG_DIR,
                                                  GAME_SETTINGS_FILENAME))
                self.player_settings.set_player(GAME_SETTINGS['Main']['player'])
            except configparser.MissingSectionHeaderError:
                sys_exit("\nFile contains no section headers. Exiting...")
                sys_exit("\nFile: {0}/{1}".format(GAME_CFG_DIR,
                                                  GAME_SETTINGS_FILENAME))

        """ Assets """
        self.scene_one.env_load('Assets/Levels/Terrain/sky.egg',
                                GAME_DIR,
                                GAME_SETTINGS,
                                "GAME_MODE",
                                render,
                                "Sky",
                                [0.0, 10.0, self.pos_z], [0, 0, 0], [1.25, 1.25, 1.25], 'skybox')

        self.scene_one.asset_load('Assets/Levels/Terrain/tress_grass.egg',
                                  GAME_DIR,
                                  "GAME_MODE",
                                  GAME_SETTINGS,
                                  render,
                                  "Grass",
                                  [20.0, 10.0, self.pos_z], [0, 0, 0], [1.25, 1.25, 1.25])

        self.scene_one.asset_load('Assets/Levels/Environment/Nomad house/Nomad_house.egg',
                                  GAME_DIR,
                                  "GAME_MODE",
                                  GAME_SETTINGS,
                                  render,
                                  "Nomad_house",
                                  [0.0, 20.0, self.pos_z], [65, 0, 0], [1.25, 1.25, 1.25])

        self.scene_one.env_load('Assets/Levels/Terrain/ground.egg',
                                GAME_DIR,
                                "GAME_MODE",
                                GAME_SETTINGS,
                                render,
                                "Ground",
                                [0.0, 10.0, self.pos_z], [0, 0, 0], [1.25, 1.25, 1.25], 'ground')

        self.scene_one.env_load('Assets/Levels/Terrain/mountains.egg',
                                GAME_DIR,
                                "GAME_MODE",
                                GAME_SETTINGS,
                                render,
                                "Mountains",
                                [0.0, 20.0, self.pos_z], [0, 0, 0], [1.25, 1.25, 1.25], 'mountains')

        self.korlan.set_character_game("game",
                                       GAME_SETTINGS,
                                       "Korlan",
                                       [0.0, 8.0, self.pos_z], [270.0, 0, 0], [1.25, 1.25, 1.25],
                                       GAME_DIR,
                                       self.player_settings.set_player_path(GAME_DIR),
                                       CFG_PATH,
                                       render,
                                       "Korlan-Walking.egg")

