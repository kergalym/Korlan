#!/usr/bin/env python3.6
import logging
import re

import panda3d.core as p3d
from panda3d.core import Filename
from panda3d.core import WindowProperties
from direct.showbase.ShowBase import ShowBase
from panda3d.core import TextNode
from pathlib import Path, PurePath
from Engine.Actors.Player.korlan import Korlan
from Engine.Scenes.scene_one import SceneOne
from Settings.Sound.sound import Sound
from Settings.UI.menu import Menu
from Settings.menu_settings import Graphics

import json
import configparser
from sys import exit as sys_exit
from os import mkdir, listdir, walk
from os.path import isdir, isfile, exists

game_cfg = '{0}/Korlan - Daughter of the Steppes/settings.ini'.format(str(Path.home()))

game_settings = configparser.ConfigParser()
game_settings['Main'] = {'disp_res': '1024x768',
                         'fullscreen': 'off',
                         'antialiasing': 'on',
                         'postprocessing': 'on',
                         'shadows': 'off',
                         'sound': 'on',
                         'music': 'on',
                         'sfx': 'on',
                         'language': 'english',
                         'player': 'Korlan'
                         }

game_settings['Keymap'] = {'forward': 'W',
                           'backward': 'S',
                           'left': 'A',
                           'right': 'D',
                           'crouch': 'C',
                           'jump': 'space',
                           'use': 'E',
                           'attack': 'MOUSE1',
                           'h_attack': 'H',
                           'f_attack': 'F',
                           'block': 'MOUSE3',
                           'sword': '1',
                           'bow': '2',
                           'tengri': '3',
                           'umai': '4'
                           }

game_settings['Debug'] = {}
game_settings['Debug'] = {'set_debug_mode': 'NO',
                          'player_pos_x': '0.0',
                          'player_pos_y': '8.0',
                          'player_pos_z': '-1.09',
                          'player_rot_h': '0.0',
                          'player_rot_p': '0.0',
                          'player_rot_r': '-0.0'
                          }

game_settings.read(game_cfg)
disp_res = game_settings['Main']['disp_res']
disp_res = disp_res.split("x")

p3d.load_prc_file_data(
    '',
    'win-size {0} {1}\n'.format(disp_res[0], disp_res[1])
)

p3d.load_prc_file_data(
    '',
    'window-title Korlan - Daughter of the Steppes\n'
    'show-frame-rate-meter  t\n'
    'audio-library-name p3openal_audio\n'
    'model-cache-dir Cache\n'
    'model-cache-textures t\n'
)


class Main(ShowBase):
    """ Game Parent Directory Path """

    def __init__(self):

        self.cfg_path = None

        self.manualRecenterMouse = None

        self.gfx = Graphics()

        ShowBase.__init__(self)

        self.logging = logging
        self.logging.basicConfig(filename="critical.log", level=logging.CRITICAL)
        self.backfaceCullingOff()
        self.props = WindowProperties()

        self.game_dir = str(Path.cwd())
        self.game_cfg = game_cfg
        self.cfg_warn_text = "# THIS FILE IS AUTOGENERATED. DO NOT EDIT\n\n"
        self.game_cfg_dir = '{}/Korlan - Daughter of the Steppes'.format(str(Path.home()))
        self.game_settings = game_settings
        self.game_settings_filename = 'settings.ini'
        self.cfg_path = {"game_config_path": "{0}/{1}".format(self.game_cfg_dir, self.game_settings_filename)}
        self.game_mode = False
        self.menu_mode = True

        # Notice that you must not call ShowBase.__init__ (or super), the
        # render pipeline does that for you. If this is unconvenient for you,
        # have a look at the other initialization possibilities.

        # Insert the pipeline path to the system path, this is required to be
        # pipeline in a subfolder of your project, you have to adjust this.

        # Commented to prevent using it by deploying system
        """sys.path.insert(0, ".")
        sys.path.insert(0, "RenderPipeline")

        # Import the main render pipeline class
        from rpcore import RenderPipeline
        from rpcore import PointLight

        # Construct and create the pipeline
        self.render_pipeline = RenderPipeline()"""

        self.game_settings.read("{0}/{1}".format(self.game_cfg_dir, self.game_settings_filename))

        # Commented to prevent using it by deploying system
        """if self.game_settings['Main']['postprocessing'] == 'on':
            self.render_pipeline.pre_showbase_init()
            self.render_pipeline.create(self)

            my_light = PointLight()
            # set desired properties, see below
            self.render_pipeline.add_light(my_light)"""

        # Game scene loading definitions
        self.scene_one = SceneOne()
        self.korlan = Korlan()
        self.sound = Sound()
        self.text = TextNode("TextNode")

        """ Create game config first! """
        if self.check_cfg():
            self.menu = Menu()
        elif self.check_cfg() and self.game_mode is False:
            self.menu = Menu()
        else:
            sys_exit("\nNo game configuration file created. Please check your game log")

        self.render_type = "menu"
        self.rotateY = 0
        self.rotateX = 0
        self.scene_mode = None

        """ Sounds """
        self.sound.openal_mgr()

        """ Menu """
        if self.menu_mode:
            self.menu.load_main_menu()

    """ Creating same Game Directory"""

    def check_cfg(self):
        if exists('Settings/UI/cfg_path.json'):
            self.cfg_path = json.dumps({'game_config_path': '{0}/{1}'.format(
                self.game_cfg_dir,
                self.game_settings_filename),
                'game_dir': '{0}'.format(self.game_dir)})

            with open('Settings/UI/cfg_path.json', 'w') as f:
                f.write(str(self.cfg_path))

            if exists("{0}/{1}".format(self.game_cfg_dir,
                                       self.game_settings_filename)) is False:

                self.do_cfg()

                if (isfile('Settings/UI/cfg_path.json') and
                        isfile("{0}/{1}".format(self.game_cfg_dir,
                                                self.game_settings_filename))):

                    with open('Settings/UI/cfg_path.json', 'w') as f:
                        f.write(str(self.cfg_path))

                    try:
                        self.game_settings.read("{0}/{1}".format(self.game_cfg_dir,
                                                                 self.game_settings_filename))
                    except configparser.MissingSectionHeaderError:
                        sys_exit("\nFile contains no section headers. I'm bumping file again...")
                        sys_exit("\nFile: {0}/{1}".format(self.game_cfg_dir,
                                                          self.game_settings_filename))

                        self.force_do_cfg()

            else:

                try:
                    self.game_settings.read("{0}/{1}".format(self.game_cfg_dir, self.game_settings_filename))
                except configparser.MissingSectionHeaderError:
                    sys_exit("\nFile contains no section headers. I'm bumping file again...")
                    sys_exit("\nFile: {0}/{1}".format(self.game_cfg_dir, self.game_settings_filename))

                    self.force_do_cfg()

            if isdir(self.game_dir) is False:
                mkdir(self.game_dir)
                self.do_cfg()
                return True
            else:
                self.do_cfg()
                return True
        else:
            sys_exit("\nGame data is broken. Please, reinstall it")

    def do_cfg(self):
        if exists('{0}/{1}'.format(self.game_cfg_dir, self.game_settings_filename)) is False:
            if exists(self.game_cfg_dir) is False and isdir(self.game_cfg_dir) is False:
                mkdir(self.game_cfg_dir)
            with open('{0}/{1}'.format(self.game_cfg_dir, self.game_settings_filename), 'w') as config_ini:
                # Turn that setting dict to pass it further
                config_ini.write(self.cfg_warn_text)
                self.game_settings.write(config_ini)

    def force_do_cfg(self):
        if exists('{0}/{1}'.format(self.game_cfg_dir, self.game_settings_filename)) is False:
            if exists(self.game_cfg_dir) is False and isdir(self.game_cfg_dir) is False:
                mkdir(self.game_cfg_dir)
            with open('{0}/{1}'.format(self.game_cfg_dir, self.game_settings_filename), 'w') as config_ini:
                # Turn that setting dict to pass it further
                self.game_settings.write(config_ini)
        else:

            with open('{0}/{1}'.format(self.game_cfg_dir, self.game_settings_filename), 'w') as config_ini:
                # Turn that setting dict to pass it further
                self.game_settings.write(config_ini)

    def collect_assets(self):
        asset_path = str(PurePath(self.game_dir, "Assets"))
        asset_path = Filename.from_os_specific("{0}/".format(asset_path))
        assets = {}
        exclude_anims = 'Animations'
        exclude_tex = 'tex'
        key = None
        if exists(asset_path):
            for root, dirs, files in walk(asset_path, topdown=True):
                if exclude_anims in dirs:
                    dirs.remove(exclude_anims)
                if exclude_tex in dirs:
                    dirs.remove(exclude_tex)
                for file in files:
                    if '.egg' and '.egg.bam' not in file:
                        key = re.sub('.egg', '', file)
                    elif '.egg.bam' in file:
                        key = re.sub('.egg.bam', '', file)
                    path = str(PurePath("{0}/".format(root), file))
                    assets[key] = Filename.from_os_specific(path).getFullpath()

            return assets

        else:
            logging.critical("\nI'm trying to load assets, but there aren't suitable assets. "
                             "\nCurrent path: {0}".format(asset_path))
            sys_exit("\nSomething is getting wrong. Please, check the game log first")

    def collect_anims(self):
        anims_path = str(PurePath(self.game_dir, "Assets", "Animations"))
        anims_path = Filename.from_os_specific("{0}/".format(anims_path))
        collected = listdir(anims_path)
        path = {}
        anims = {}
        if exists(anims_path):
            for a in collected:
                key = re.sub('Korlan-', '', a)
                if '.egg' and '.egg.bam' not in key:
                    key = re.sub('.egg', '', key)
                elif '.egg.bam' in key:
                    key = re.sub('.egg.bam', '', key)
                anims[key] = key
                anim_path = str(PurePath("{0}/".format(anims_path), a))
                path[key] = Filename.from_os_specific(anim_path).getFullpath()

            return [anims, path]

        else:
            logging.critical("\nI'm trying to load Korlan player, but there is no suitable player asset. "
                             "\nNo suitable player asset found!"
                             "\nPlayer path: {0}".format(anims_path))
            sys_exit("\nSomething is getting wrong. Please, check the game log first")

    def asset_nodes_collector(self):
        # make pattern list from assets dict
        pattern = [key for key in self.collect_assets()]
        # use pattern to get all nodes corresponding to asset names
        nodes_cleaned = []
        for node in [render.find("**/{0}".format(node)) for node in pattern]:
            if str(node) != '**not found**':
                nodes_cleaned.append(node)

        return nodes_cleaned

    def asset_nodes_assoc_collector(self):
        # make pattern list from assets dict
        pattern = [key for key in self.collect_assets()]
        parents = {}
        # use pattern to get all nodes corresponding to associated asset names
        for node in pattern:
            value = render.find("**/{0}".format(node))
            if str(value) != '**not found**':
                parents[node] = value
        return parents

    def asset_node_children_collector(self, nodes, assoc_key):
        if nodes and isinstance(nodes, list):
            if assoc_key:
                children = {}
                for node in nodes:
                    for inner in node.getChildren():
                        for num in range(len(inner.getChildren())):
                            name = inner.getChildren().getPath(num).getName()
                            node_path = inner.getChildren().getPath(num)
                            children[name] = node_path
                # Remove empty name key
                children.pop('')
                return children
            if assoc_key is False:
                children = []
                for node in nodes:
                    for inner in node.getChildren():
                        for num in range(len(inner.getChildren())):
                            name = inner.getChildren().getPath(num).getName()
                            node_path = inner.getChildren().getPath(num)
                            if name != '':
                                children.append(node_path)
                return children

    def asset_pos_collector(self, nodes):
        if isinstance(nodes, list):
            asset_names = {}
            asset_pos = {}
            for node in nodes:
                asset_pos['X'] = node.getX()
                asset_pos['Y'] = node.getY()
                asset_pos['Z'] = node.getZ()
                asset_names[node.getName()] = asset_pos
            return asset_names

    def collect_sounds(self):
        sound_path = str(PurePath(self.game_dir, "Assets", "Sounds"))
        sound_path = Filename.from_os_specific("{0}/".format(sound_path))
        sounds = {}
        key = None
        if exists(sound_path):
            for root, dirs, files in walk(sound_path, topdown=True):
                for file in files:
                    if '.ogg' in file:
                        key = re.sub('.ogg', '', file)
                    path = str(PurePath("{0}/".format(root), file))
                    sounds[key] = Filename.from_os_specific(path).getFullpath()

            return sounds

        """ Enable this when game will be ready for distribution
        else:
            logging.critical("\nI'm trying to load sound assets, but there aren't suitable sound assets. "
                             "\nCurrent path: {0}".format(sound_path))
            sys_exit("\nSomething is getting wrong. Please, check the game log first")
        """

    def menu_scene_load(self):
        # Commented to prevent using it by deploying system
        """"# Set time of day
        if self.game_settings['Main']['postprocessing'] == 'on':
            self.render_pipeline.daytime_mgr.time = "15:25
        """

        """ Assets """
        # assets is a dict containing paths + models
        # anims is a list containing two dicts.
        # anims[0] is a dict containing names of animations
        # anims[1] is a dict containing paths + animations
        assets = self.collect_assets()
        anims = self.collect_anims()

        # Test scene
        if self.game_mode is False and self.menu_mode is True:
            self.scene_one.env_load(path=assets['Sky'],
                                    mode="menu",
                                    name="Sky",
                                    axis=[0.0, 10.0, -1.09],
                                    rotation=[0, 0, 0],
                                    scale=[1.25, 1.25, 1.25],
                                    type='skybox')

            self.scene_one.asset_load(path=assets['Grass'],
                                      mode="menu",
                                      name="Grass",
                                      axis=[20.0, 10.0, -1.09],
                                      rotation=[0, 0, 0],
                                      scale=[1.25, 1.25, 1.25])

            self.scene_one.asset_load(path=assets['Nomad_house'],
                                      mode="menu",
                                      name="Nomad_house",
                                      axis=[1.0, 20.0, -1.09],
                                      rotation=[65, 0, 0],
                                      scale=[1.25, 1.25, 1.25])

            self.scene_one.env_load(path=assets['Ground'],
                                    mode="menu",
                                    name="Ground",
                                    axis=[0.0, 10.0, -1.09],
                                    rotation=[0, 0, 0],
                                    scale=[1.25, 1.25, 1.25],
                                    type='ground')

            self.scene_one.env_load(path=assets['Mountains'],
                                    mode="menu",
                                    name="Mountains",
                                    axis=[0.0, 20.0, -1.09],
                                    rotation=[0, 0, 0],
                                    scale=[1.25, 1.25, 1.25],
                                    type='mountains')

            self.korlan.set_actor(mode="menu",
                                  name="Korlan",
                                  path=assets['Korlan'],
                                  animation=[anims[0]['LookingAround'], anims[1]['LookingAround']],
                                  axis=[0, 8.0, -1.09],
                                  rotation=[0, 0, 0],
                                  scale=[1.25, 1.25, 1.25])


app = Main()
app.menu_scene_load()

if __name__ == '__main__':
    app.run()
