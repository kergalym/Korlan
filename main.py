#!/usr/bin/env python3.7
import logging
import re
import sys
import json
import configparser
from sys import exit as sys_exit
from os import mkdir, listdir, walk
from os.path import isdir, isfile, exists

import panda3d.core as p3d
from panda3d.core import Filename
from panda3d.core import WindowProperties
from direct.showbase.ShowBase import ShowBase
from panda3d.core import TextNode
from pathlib import Path, PurePath
from Engine.Actors.Player.korlan import Korlan
from Engine.Scenes.scene_one import SceneOne
from Engine.Render.render import RenderAttr
from Settings.Sound.sound import Sound
from Settings.UI.menu import Menu
from Settings.menu_settings import Graphics

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
                           'run': 'LSHIFT',
                           'crouch': 'C',
                           'jump': 'SPACE',
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

game_cfg = '{0}/Korlan - Daughter of the Steppes/settings.ini'.format(str(Path.home()))
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
    'want-pstats 0\n'
)


class Main(ShowBase):

    def __init__(self):
        self.cfg_path = None
        self.manual_recenter_Mouse = None
        self.gfx = Graphics()
        ShowBase.__init__(self)
        self.logging = logging
        self.logging.basicConfig(filename="critical.log", level=logging.CRITICAL)
        self.backfaceCullingOff()
        self.props = WindowProperties()
        self.game_dir = str(Path.cwd())
        self.game_cfg = game_cfg
        self.cfg_warn_text = "# THIS FILE IS AUTOGENERATED. DO NOT EDIT\n\n"
        self.game_cfg_dir = '{0}/Korlan - Daughter of the Steppes'.format(str(Path.home()))
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

        self.menu = Menu()
        self.scene_one = SceneOne()
        self.render_attr = RenderAttr()
        self.korlan = Korlan()
        self.sound = Sound()
        self.text = TextNode("TextNode")

        """ Menu """
        if self.check_and_do_cfg():
            if self.menu_mode:
                self.menu.load_main_menu()
        elif self.check_and_do_cfg() and self.game_mode is False:
            if self.menu_mode:
                self.menu.load_main_menu()
        else:
            sys_exit("\nNo game configuration file created. Please check your game log")

        self.render_type = "menu"
        self.rotateY = 0
        self.rotateX = 0
        self.scene_mode = None

        """ Sounds """
        self.sound.openal_mgr()

    def check_and_do_cfg(self):
        """ Function    : check_and_do_cfg

            Description : Check if game config is exist and create it if not.

            Input       : None

            Output      : None

            Return      : Boolean
        """
        if exists('{0}/Settings/UI/cfg_path.json'.format(self.game_dir)):
            self.cfg_path = json.dumps({'game_config_path': '{0}/{1}'.format(
                self.game_cfg_dir,
                self.game_settings_filename),
                'game_dir': '{0}'.format(self.game_dir)})
            with open('{0}/Settings/UI/cfg_path.json'.format(self.game_dir), 'w') as f:
                f.write(str(self.cfg_path))
            if exists("{0}/{1}".format(self.game_cfg_dir,
                                       self.game_settings_filename)) is False:
                self.do_cfg()
                if (isfile('{0}/Settings/UI/cfg_path.json'.format(self.game_dir)) and
                        isfile("{0}/{1}".format(self.game_cfg_dir,
                                                self.game_settings_filename))):
                    with open('{0}/Settings/UI/cfg_path.json'.format(self.game_dir), 'w') as f:
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
        """ Function    : do_cfg

            Description : Create game config if not exist.

            Input       : None

            Output      : None

            Return      : None
        """
        if exists('{0}/{1}'.format(self.game_cfg_dir, self.game_settings_filename)) is False:
            if exists(self.game_cfg_dir) is False and isdir(self.game_cfg_dir) is False:
                mkdir(self.game_cfg_dir)
            with open('{0}/{1}'.format(self.game_cfg_dir, self.game_settings_filename), 'w') as config_ini:
                # Turn that setting dict to pass it further
                config_ini.write(self.cfg_warn_text)
                self.game_settings.write(config_ini)

    def force_do_cfg(self):
        """ Function    : force_do_cfg

            Description : Force creating game config if not exist.

            Input       : None

            Output      : None

            Return      : None
        """
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

    def assets_collector(self):
        """ Function    : assets_collector

            Description : Collect game assets.

            Input       : None

            Output      : None

            Return      : Dictionary
        """
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
                    # include one of them
                    if '.egg' and '.egg.bam' not in file:
                        key = re.sub('.egg', '', file)
                    elif '.egg.bam' and '.egg' not in file:
                        key = re.sub('.egg.bam', '', file)
                    path = str(PurePath("{0}/".format(root), file))
                    assets[key] = Filename.from_os_specific(path).getFullpath()

            return assets

        else:
            logging.critical("\nI'm trying to load assets, but there aren't suitable assets. "
                             "\nCurrent path: {0}".format(asset_path))
            sys_exit("\nSomething is getting wrong. Please, check the game log first")

    def asset_animations_collector(self):
        """ Function    : asset_animations_collector

            Description : Collect game asset animations.

            Input       : None

            Output      : None

            Return      : List
        """
        anims_path = str(PurePath(self.game_dir, "Assets", "Animations"))
        anims_path = Filename.from_os_specific("{0}/".format(anims_path))
        collected = listdir(anims_path)
        path = {}
        anims = {}
        if exists(anims_path):
            for a in collected:
                key = re.sub('Korlan-', '', a)
                # include one of them
                if '.egg' and '.egg.bam' not in key:
                    key = re.sub('.egg', '', key)
                elif '.egg.bam' and '.egg' not in key:
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
        """ Function    : asset_nodes_collector

            Description : Collect game asset nodes.

            Input       : None

            Output      : None

            Return      : List
        """
        # make pattern list from assets dict
        pattern = [key for key in self.assets_collector()]
        # use pattern to get all nodes corresponding to asset names
        nodes_cleaned = []
        for node in [render.find("**/{0}".format(node)) for node in pattern]:
            if not node.is_empty():
                nodes_cleaned.append(node)
        return nodes_cleaned

    def asset_nodes_assoc_collector(self):
        """ Function    : asset_nodes_assoc_collector

            Description : Collect game asset nodes as associated.

            Input       : None

            Output      : None

            Return      : Dictionary
        """
        # make pattern list from assets dict
        pattern = [key for key in self.assets_collector()]
        parents = {}
        # use pattern to get all nodes corresponding to associated asset names
        for node in pattern:
            value = render.find("**/{0}".format(node))
            if not value.is_empty():
                parents[node] = value
        return parents

    def asset_node_children_collector(self, nodes, assoc_key):
        """ Function    : asset_node_children_collector

            Description : Collect game asset children nodes.

            Input       : List, Boolean

            Output      : None

            Return      : Dictionary
        """
        if nodes and isinstance(nodes, list):
            if assoc_key:
                children = {}
                for node in nodes:
                    for inner in node.get_children():
                        for num in range(len(inner.get_children())):
                            name = inner.get_children().get_path(num).get_name()
                            node_path = inner.get_children().get_path(num)
                            children[name] = node_path
                # Remove empty name key
                children.pop('')
                return children
            if assoc_key is False:
                children = []
                for node in nodes:
                    for inner in node.get_children():
                        for num in range(len(inner.get_children())):
                            name = inner.get_children().get_path(num).get_name()
                            node_path = inner.get_children().get_path(num)
                            if name != '':
                                children.append(node_path)
                return children

    def collect_sounds(self):
        """ Function    : collect_sounds

            Description : Collect game asset sounds.

            Input       : None

            Output      : None

            Return      : Dictionary
        """
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
                    sounds[key] = Filename.from_os_specific(path).get_full_path()
            return sounds

        """ Enable this when game will be ready for distribution
        else:
            logging.critical("\nI'm trying to load sound assets, but there aren't suitable sound assets. "
                             "\nCurrent path: {0}".format(sound_path))
            sys_exit("\nSomething is getting wrong. Please, check the game log first")
        """

    """ Get all assets position including their children """

    def asset_pos_collector(self):
        """ Function    : asset_pos_collector

            Description : Collect game asset positions.

            Input       : None

            Output      : None

            Return      : Dictionary
        """
        assets = self.asset_nodes_collector()
        items = {}
        assets_children = self.asset_node_children_collector(
            assets, assoc_key=True)
        for key in assets_children:
            parent_node = assets_children[key].get_parent().get_parent()
            items[key] = (parent_node.get_pos())
        return items

    def assets_pos_collector_no_actor(self, player, exclude, physics):
        """ Function    : assets_pos_collector_no_actor

            Description : Collect game asset positions except for an actor.

            Input       : Nodepath, List

            Output      : None

            Return      : Dictionary
        """
        if (player and exclude
                and isinstance(physics, str)
                and isinstance(exclude, list)):
            # parse player name to exclude them
            assets = base.asset_nodes_collector()
            t = []
            items = {}
            for asset in assets:
                # We exclude any actor from assets,
                # we need to retrieve the distance
                if asset.get_name() != player.get_name():
                    t.append(asset)
            for n, x in enumerate(exclude, 0):
                # We exclude any item from assets,
                # we need to retrieve the distance
                try:
                    if t[n].get_name() == x:
                        t.pop(n)
                except IndexError:
                    pass
            assets_children = base.asset_node_children_collector(
                t, assoc_key=True)
            for key in assets_children:
                parent_node = assets_children[key].get_parent().get_parent()
                if physics == 'standard':
                    items[key] = (parent_node.get_pos())
                elif physics == 'bullet':
                    # We get bullet node
                    if not parent_node.get_parent().is_empty():
                        parent_node = parent_node.get_parent()
                        items[key] = (parent_node.get_pos())
                    else:
                        items[key] = (parent_node.get_pos())
            return items

    def distance_calculate(self, items, actor):
        """ Function    : distance_calculate

            Description : Calculate a distance between object and actor.

            Input       : Dict, Nodepath

            Output      : None

            Return      : Dictionary
        """

        if (items and actor
                and isinstance(items, dict)):
            # Do some minimum distance calculate here
            remained = {}
            for key in items:
                # Subtract actor vector from item vector.
                vect_x = items[key][0] - actor.get_x()
                vect_y = items[key][1] - actor.get_y()
                vect_z = items[key][2] - actor.get_z()
                remained[key] = (round(vect_x, 1),
                                 round(vect_y, 1),
                                 round(vect_z, 1))
            return remained

    def distance_calculate_precise(self, items, actor):
        """ Function    : distance_calculate_precise

            Description : Calculate a distance between object and actor.

            Input       : Dict, Nodepath

            Output      : None

            Return      : Dictionary
        """
        if (items and actor
                and isinstance(items, dict)):
            # Do some minimum distance calculate here
            remained = {}
            for key in items:
                # Subtract actor vector from item vector.
                vect_x = items[key][0] - actor.get_x()
                vect_y = items[key][1] - actor.get_y()
                vect_z = items[key][2] - actor.get_z()
                remained[key] = (vect_x, vect_y, vect_z)
            return remained

    def menu_scene_load(self):
        """ Function    : menu_scene_load

            Description : Load menu scene.

            Input       : None

            Output      : None

            Return      : None
        """
        # Commented to prevent using it by deploying system
        """"# Set time of day
        if self.game_settings['Main']['postprocessing'] == 'on':
            self.render_pipeline.daytime_mgr.time = "15:25
        """

        """ Assets """
        self.render_attr.set_lighting(name='directionalLight',
                                      render=self.render,
                                      pos=[0, 0, 10],
                                      hpr=[180, -20, 0],
                                      color=[0.2],
                                      task="attach")
        self.render_attr.set_lighting(name='directionalLight',
                                      render=self.render,
                                      pos=[0, 0, 10],
                                      hpr=[0, -20, 0],
                                      color=[0.2],
                                      task="attach")

        # assets is a dict containing paths + models
        # anims is a list containing two dicts.
        # anims[0] is a dict containing names of animations
        # anims[1] is a dict containing paths + animations
        assets = self.assets_collector()
        anims = self.asset_animations_collector()

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
                                  animation=[anims[0]['LookingAround'],
                                             anims[1]['LookingAround']],
                                  axis=[0, 8.0, -1.09],
                                  rotation=[0, 0, 0],
                                  scale=[1.25, 1.25, 1.25])


app = Main()
app.menu_scene_load()

if __name__ == '__main__':
    app.run()
