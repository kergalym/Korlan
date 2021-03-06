#!/usr/bin/env python3.7

import logging
import re
import json
import configparser
from shutil import rmtree
from sys import exit as sys_exit
from os import mkdir, listdir, walk
from os.path import isdir, isfile, exists

import panda3d.core as p3d
from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.OnscreenText import OnscreenText
from direct.showbase.ShowBaseGlobal import render2d
from panda3d.core import Filename, LODNode, Texture, Vec3
from panda3d.core import WindowProperties
from direct.showbase.ShowBase import ShowBase
from direct.showbase.ShowBase import MovieTexture
from direct.showbase.ShowBase import CardMaker
from direct.showbase.ShowBase import NodePath
from direct.showbase.ShowBase import AudioSound

from panda3d.core import TextNode
from panda3d.core import FontPool
from pathlib import Path, PurePath

from Engine.Actors.Player.korlan import Korlan
from Engine.Scenes.scene import SceneOne
from Engine.Render.render import RenderAttr
from Settings.Sound.sound import Sound
from Settings.UI.menu_ui import MenuUI
from Settings.gfx_menu_settings import Graphics
from panda3d.core import Thread
from direct.stdpy import threading
from code import InteractiveConsole
from direct.task.TaskManagerGlobal import taskMgr
from Engine.Render.rpcore.render_pipeline import RenderPipeline
from Engine.Render.rpcore.util.movement_controller import MovementController

build_info_txt = "Build 0.2. 12/2020"

game_settings = configparser.ConfigParser()
game_settings['Main'] = {'disp_res': '1920x1080',
                         'fullscreen': 'off',
                         'antialiasing': 'on',
                         'postprocessing': 'on',
                         'shadows': 'on',
                         'sound': 'on',
                         'music': 'on',
                         'sfx': 'on',
                         'language': 'english',
                         'player': 'Korlan',
                         'person_look_mode': 'third',
                         'gameplay_mode': 'simple',
                         'show_blood': 'on',
                         'camera_distance': '4',
                         }

game_settings['Keymap'] = {'forward': 'W',
                           'backward': 'S',
                           'left': 'A',
                           'right': 'D',
                           'run': 'SHIFT',
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

game_settings['Debug'] = {'set_debug_mode': 'NO',
                          'set_editor_mode': 'NO',
                          'render_explore': 'NO',
                          'cache_autoclean': 'NO',
                          'want_pstats': 'NO',
                          'player_pos_x': '0.0',
                          'player_pos_y': '8.0',
                          'player_pos_z': '-1.09',
                          'player_rot_h': '0.0',
                          'player_rot_p': '0.0',
                          'player_rot_r': '-0.0'
                          }

game_settings['Misc'] = {'daytime': '18:00'}

game_cfg = '{0}/Korlan - Daughter of the Steppes/settings.ini'.format(str(Path.home()))
game_settings.read(game_cfg)
disp_res = game_settings['Main']['disp_res']
disp_res = disp_res.split("x")

fscreen = "f"
wintype = "onscreen"

want_pstats_value = "f"

if game_settings['Main']['fullscreen'] == "on":
    fscreen = "t"

if game_settings['Debug']['want_pstats'] == "YES":
    want_pstats_value = "t"

p3d.load_prc_file_data(
    '',
    'fullscreen {0}\n'.format(fscreen)
)

p3d.load_prc_file_data(
    '',
    'win-size {0} {1}\n'.format(disp_res[0], disp_res[1])
)

p3d.load_prc_file_data(
    '',
    'window-type {0}\n'.format(wintype)
)

p3d.load_prc_file_data(
    '',
    'icon-filename icon-16.ico\n'
    'win-origin -1 -2\n'
    'window-title Korlan - Daughter of the Steppes\n'
    'show-frame-rate-meter  t\n'
    'audio-library-name p3openal_audio\n'
    'model-cache-dir Cache\n'
    'model-cache-textures t\n'
    'compressed-textures 0\n'
    'bullet-filter-algorithm groups-mask\n'
    'hardware-animated-vertices t\n'
    'basic-shaders-only f\n'
    'texture-compression f\n'
    'driver-compress-textures f\n'
    'task-timer-verbose 0\n'
    'pstats-tasks 0\n'
)

p3d.load_prc_file_data(
    '',
    'want-pstats {0}\n'.format(want_pstats_value)
)

game_dir = str(Path.cwd())
cfg_is_broken = False
cfg_name = None
if not exists('{0}/Engine/Render/config/plugins_def.yaml'.format(game_dir)):
    cfg_is_broken = True
    cfg_name = "YOUR_GAME/Engine/Render/config/plugins_def.yaml"
else:
    with open("{0}/Engine/Render/config/plugins_def.yaml".format(game_dir), 'r') as f:
        config = f.read()
        if not config:
            cfg_is_broken = True
            cfg_name = "YOUR_GAME/Engine/Render/config/plugins_def.yaml"
        else:
            f.close()

if not exists('{0}/Engine/Render/config/plugins.yaml'.format(game_dir)):
    cfg_is_broken = True
    cfg_name = "YOUR_GAME/Engine/Render/config/plugins.yaml"
else:
    with open("{0}/Engine/Render/config/plugins.yaml".format(game_dir), 'r') as f:
        config = f.read()
        if not config:
            cfg_is_broken = True
            cfg_name = "YOUR_GAME/Engine/Render/config/plugins.yaml"
        else:
            f.close()


class Error(ShowBase):

    def __init__(self):
        ShowBase.__init__(self)
        self.build_info = OnscreenText(text=build_info_txt, pos=(1.6, -0.95),
                                       fg=(255, 255, 255, 1), scale=.025)
        self.props = WindowProperties()
        self.props.setIconFilename("icon-16.ico")
        self.props.set_cursor_hidden(True)
        self.win.request_properties(self.props)
        self.game_dir = str(Path.cwd())
        self.images = self.textures_collector(path="{0}/Settings/UI".format(self.game_dir))
        self.fonts = self.fonts_collector()
        # instance of the abstract class
        self.font = FontPool

        if not self.fonts and self.images:
            exit("Time to reinstall your game")

        """ Texts & Fonts"""
        # self.menu_font = self.fonts['OpenSans-Regular']
        self.menu_font = self.fonts['JetBrainsMono-Regular']

        """ Background Image """
        self.img_bg = OnscreenImage(image=self.images['error_bg'],
                                    pos=(0, 0, 0), scale=(2, 1, 1))

        self.title_msg = OnscreenText(text="",
                                      pos=(-1.8, -0.7),
                                      scale=0.06,
                                      fg=(255, 255, 255, 0.9),
                                      font=self.font.load_font(self.menu_font),
                                      align=TextNode.ALeft,
                                      mayChange=True)

        self.title_sm_msg = OnscreenText(text="",
                                         pos=(-1.8, -0.9),
                                         scale=0.03,
                                         fg=(255, 255, 255, 0.9),
                                         font=self.font.load_font(self.menu_font),
                                         align=TextNode.ALeft,
                                         mayChange=True)
        self.title_msg.setText("Hey, samurai. Your game is broken. Fix and come back")
        self.title_sm_msg.setText("RenderPipeline plugins configuration is broken:\n{}".format(cfg_name))

    def video_status_task(self, media, type, file, task):
        """ Function    : video_status_task

            Description : Task for video wall.

            Input       : Nodepath, String, Task

            Output      : None

            Return      : Task event
        """
        if media and type and isinstance(type, str) and "REDSTUDIO_FHD" in file:
            base.accept("escape", media.stop)

        if AudioSound.status(media) == 1:
            if type == "player_avatar":
                media.play()
            else:
                media.stop()

            if type != "menu_scene":
                if not render2d.find("**/VideoWall").is_empty():
                    render2d.find("**/VideoWall").remove_node()

            if type == "main_menu":
                # Disable the camera trackball controls.
                self.disable_mouse()
                props = WindowProperties()
                props.set_cursor_hidden(False)
                self.win.request_properties(props)
                self.load_video(file="MENU_SCENE_VID", type="menu_scene")
                return task.done

        return task.cont

    def transform_path(self, path, style):
        if isinstance(path, str):
            if style == 'unix':
                transformed_path = str(PurePath(path))
                transformed_path = Filename.from_os_specific(transformed_path)
                return transformed_path
            elif style == 'compat':
                transformed_path = Filename(path).to_os_specific()
                return transformed_path

    def fonts_collector(self):
        """ Function    : fonts_collector

            Description : Collect fonts.

            Input       : None

            Output      : None

            Return      : Dictionary
        """
        font_path = self.transform_path(path="{0}/Settings/UI".format(self.game_dir),
                                        style='compat')
        fonts = {}
        if exists(font_path):
            for root, dirs, files in walk(font_path, topdown=True):
                for file in files:
                    if file.endswith(".ttf"):
                        key = re.sub('.ttf$', '', file)
                        path = str(PurePath("{0}/".format(root), file))
                        fonts[key] = Filename.from_os_specific(path).getFullpath()
            return fonts

    def textures_collector(self, path):
        """ Function    : textures_collector

            Description : Collect textures.

            Input       : None

            Output      : None

            Return      : Dictionary
        """
        tex_path = self.transform_path(path=path, style='compat')
        textures = {}
        if exists(tex_path):
            for root, dirs, files in walk(tex_path, topdown=True):
                for file in files:
                    if file.endswith(".png"):
                        key = re.sub('.png$', '', file)
                        path = str(PurePath("{0}/".format(root), file))
                        textures[key] = Filename.from_os_specific(path).getFullpath()
                    elif file.endswith(".jpg"):
                        key = re.sub('.jpg$', '', file)
                        path = str(PurePath("{0}/".format(root), file))
                        textures[key] = Filename.from_os_specific(path).getFullpath()
            return textures

    def videos_collector(self):
        """ Function    : videos_collector

            Description : Collect game asset videos.

            Input       : None

            Output      : None

            Return      : Dictionary
        """
        sound_path = self.transform_path(path="{0}/Assets/Videos/".format(self.game_dir), style='compat')
        videos = {}
        if exists(sound_path):
            for root, dirs, files in walk(sound_path, topdown=True):
                for file in files:
                    if file.endswith(".mkv"):
                        key = re.sub('.mkv$', '', file)
                        path = str(PurePath("{0}/".format(root), file))
                        videos[key] = Filename.from_os_specific(path).getFullpath()
            return videos

    def load_video(self, file, type):
        """ Function    : load_video

            Description : Loads videofile to screen.

            Input       : String

            Output      : None

            Return      : Dictionary
        """
        if (file and type
                and isinstance(file, str) and isinstance(type, str)):
            videos = self.videos_collector()

            if videos and videos.get(file):
                tex = MovieTexture(file)
                success = tex.read(videos.get(file))
                if success:
                    # Set up a fullscreen card to set the video texture on.
                    cm = CardMaker("VideoWall")
                    cm.set_frame_fullscreen_quad()

                    # Tell the CardMaker to create texture coordinates that take into
                    # account the padding region of the texture.
                    cm.set_uv_range(tex)

                    # Now place the card in the scene graph and apply the texture to it.
                    card = NodePath(cm.generate())

                    if type == "loading_menu":
                        if not render2d.find("**/LoadingScreen").is_empty():
                            loading_screen_np = render2d.find("**/LoadingScreen")
                            card.reparent_to(loading_screen_np)

                    elif type == "main_menu":
                        card.reparent_to(render2d)

                    elif type == "player_avatar":
                        card.reparent_to(render2d)

                    card.set_texture(tex)

                    if type == "loading_menu":
                        card.set_scale(0.3)
                        card.set_pos(0, 0, 0)

                    if type == "menu_scene":
                        card.reparent_to(render2d)

                    if type == "player_avatar":
                        card.set_scale(0.3, 0.3, 0.15)
                        card.set_pos(0, 0, -0.85)

                    media = base.loader.load_sfx(videos[file])

                    if "MENU_SCENE_VID" in media.get_name():
                        base.menu_scene_vid = media

                    # Synchronize the video to the sound.
                    tex.synchronize_to(media)

                    if type == "main_menu":
                        media.play()

                        taskMgr.add(self.video_status_task,
                                    "video_status",
                                    extraArgs=[media, type, file],
                                    appendTask=True)

                    if type == "menu_scene":
                        AudioSound.set_loop(media, loop=True)
                        media.play()

                    if type == "player_avatar":
                        media.play()

                        taskMgr.add(self.video_status_task,
                                    "video_status",
                                    extraArgs=[media, type, file],
                                    appendTask=True)


class Main(ShowBase):

    def __init__(self):
        self.cfg_path = None
        self.gfx = Graphics()
        ShowBase.__init__(self)
        self.build_info = OnscreenText(text=build_info_txt, pos=(1.6, -0.95),
                                       fg=(255, 255, 255, 1), scale=.025)
        self.props = WindowProperties()
        self.props.setIconFilename("icon-16.ico")
        self.props.set_cursor_hidden(True)
        self.win.request_properties(self.props)

        self.backface_culling_on()
        self.logging = logging
        self.logging.basicConfig(filename="critical.log", level=logging.CRITICAL)
        self.game_dir = str(Path.cwd())
        self.game_cfg = game_cfg
        self.cfg_warn_text = "# THIS FILE IS AUTOGENERATED. DO NOT EDIT\n\n"
        self.game_cfg_dir = '{0}/Korlan - Daughter of the Steppes'.format(str(Path.home()))
        self.game_settings = game_settings
        self.game_settings_filename = 'settings.ini'
        self.cfg_path = {"game_config_path": "{0}/{1}".format(self.game_cfg_dir, self.game_settings_filename)}
        self.intro_mode = True
        self.game_mode = False
        self.menu_mode = False

        self.game_settings.read("{0}/{1}".format(self.game_cfg_dir, self.game_settings_filename))

        if self.game_settings['Debug']['cache_autoclean'] == 'YES':
            if (exists("{}/Cache".format(self.game_dir))
                    and isdir("{}/Cache".format(self.game_dir))):
                rmtree("{}/Cache/".format(self.game_dir))

        if self.game_settings['Debug']['set_debug_mode'] == 'YES':
            print("Is threading supported: ", Thread.isThreadingSupported(), "\n")
            ic_thread = threading.Thread(target=InteractiveConsole(globals()).interact)
            ic_thread.start()

        if self.game_settings['Debug']['render_explore'] == 'YES':
            render.explore()

        if self.game_settings['Debug']['set_editor_mode'] == 'YES':
            self.controller = MovementController(self)
            self.controller.set_initial_position_hpr(
                Vec3(-17.2912578583, -13.290019989, 6.88211250305),
                Vec3(-39.7285499573, -14.6770210266, 0.0))
            self.controller.setup()

        # Construct and create the pipeline
        render_bg_tex = self.textures_collector('{0}/Engine/Render'.format(self.game_dir))
        if self.game_settings['Main']['postprocessing'] == 'on':
            self.render_pipeline = RenderPipeline()
            self.render_pipeline.set_loading_screen_image(render_bg_tex['background'])
            self.render_pipeline.pre_showbase_init()
            self.render_pipeline.create(self)

        self.menu = MenuUI()
        self.scene_one = SceneOne()
        self.render_attr = RenderAttr()
        self.korlan = Korlan()
        self.sound = Sound()
        self.text = TextNode("TextNode")

        """ Menu """
        if self.check_and_do_cfg():
            if not self.intro_mode and self.menu_mode:
                self.menu.load_main_menu()
        elif self.check_and_do_cfg() and self.game_mode is False:
            if not self.intro_mode and self.menu_mode:
                self.menu.load_main_menu()
        else:
            sys_exit("\nNo game configuration file created. Please check your game log")

        self.render_type = "menu"
        self.rotateY = 0
        self.rotateX = 0
        self.scene_mode = None

        """ Sounds """
        self.sound.openal_mgr()

        """ Lights Storage """
        self.rp_lights = []

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
            if not exists("{0}/{1}".format(self.game_cfg_dir,
                                           self.game_settings_filename)):
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

    def transform_path(self, path, style):
        if isinstance(path, str):
            if style == 'unix':
                transformed_path = str(PurePath(path))
                transformed_path = Filename.from_os_specific(transformed_path)
                return transformed_path
            elif style == 'compat':
                transformed_path = Filename(path).to_os_specific()
                return transformed_path

    def assets_collector(self):
        """ Function    : assets_collector

            Description : Collect game assets.

            Input       : None

            Output      : None

            Return      : Dictionary
        """
        asset_path = self.transform_path(path="{0}/Assets".format(self.game_dir),
                                         style='compat')
        assets = {}
        exclude_anims = 'Animations'
        exclude_tex = 'tex'
        if not exists(asset_path):
            logging.critical("\nI'm trying to load assets, but there aren't suitable assets. "
                             "\nCurrent path: {0}".format(asset_path))
            sys_exit("\nSomething is getting wrong. Please, check the game log first")

        for root, dirs, files in walk(asset_path, topdown=True):
            if exclude_anims in dirs:
                dirs.remove(exclude_anims)
            if exclude_tex in dirs:
                dirs.remove(exclude_tex)
            for file in files:
                # include one of them
                if (file.endswith(".egg")
                        and not file.endswith(".egg.bam")):
                    key = re.sub('.egg$', '', file)
                    path = str(PurePath("{0}/".format(root), file))
                    assets[key] = Filename.from_os_specific(path).getFullpath()
                elif (file.endswith(".egg.bam")
                      and not file.endswith(".egg")):
                    key = re.sub('.egg.bam$', '', file)
                    path = str(PurePath("{0}/".format(root), file))
                    assets[key] = Filename.from_os_specific(path).getFullpath()
        return assets

    def asset_animations_collector(self):
        """ Function    : asset_animations_collector

            Description : Collect game asset animations.

            Input       : None

            Output      : None

            Return      : List
        """
        anims_path = self.transform_path(path="{0}/Assets/Animations".format(self.game_dir), style='compat')
        collected = listdir(anims_path)
        path = {}
        anims = {}

        if not exists(anims_path):
            logging.critical("\nI'm trying to load assets, but there aren't suitable assets. "
                             "\nCurrent path: {0}".format(anims_path))
            sys_exit("\nSomething is getting wrong. Please, check the game log first")

        for a in collected:
            key = re.sub('Korlan-', '', a)
            # include one of them
            if (key.endswith(".egg")
                    and not key.endswith(".egg.bam")):
                key = re.sub('.egg$', '', key)
                anims[key] = key
                anim_path = str(PurePath("{0}/".format(anims_path), a))
                path[key] = Filename.from_os_specific(anim_path).getFullpath()
            elif (key.endswith(".egg.bam")
                  and not key.endswith(".egg")):
                key = re.sub('.egg.bam$', '', key)
                anims[key] = key
                anim_path = str(PurePath("{0}/".format(anims_path), a))
                path[key] = Filename.from_os_specific(anim_path).getFullpath()
        return [anims, path]

    def assets_collider_collector(self):
        """ Function    : assets_collider_collector

            Description : Collect game asset colliders.

            Input       : None

            Output      : None

            Return      : Dictionary
        """
        asset_coll_path = self.transform_path(path="{0}/Assets/Colliders".format(self.game_dir),
                                              style='compat')
        asset_colls = {}
        exclude_anims = 'Animations'
        exclude_tex = 'tex'
        if not exists(asset_coll_path):
            logging.critical("\nI'm trying to load assets, but there aren't suitable assets. "
                             "\nCurrent path: {0}".format(asset_coll_path))
            sys_exit("\nSomething is getting wrong. Please, check the game log first")

        for root, dirs, files in walk(asset_coll_path, topdown=True):
            if exclude_anims in dirs:
                dirs.remove(exclude_anims)
            if exclude_tex in dirs:
                dirs.remove(exclude_tex)
            for file in files:
                # include one of them
                if (file.endswith(".egg")
                        and not file.endswith(".egg.bam")):
                    key = re.sub('.egg$', '', file)
                    path = str(PurePath("{0}/".format(root), file))
                    asset_colls[key] = Filename.from_os_specific(path).getFullpath()
                elif (file.endswith(".egg.bam")
                      and not file.endswith(".egg")):
                    key = re.sub('.egg.bam$', '', file)
                    path = str(PurePath("{0}/".format(root), file))
                    asset_colls[key] = Filename.from_os_specific(path).getFullpath()

        return asset_colls

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
                    if node.get_num_children() > 0:
                        for inner in node.get_children():
                            for num in range(len(inner.get_children())):
                                parent = inner.get_children().get_path(num).get_parent()
                                name = inner.get_children().get_path(num).get_name()
                                node_path = inner.get_children().get_path(num)

                                if name == '':
                                    if parent.get_name() == '__Actor_modelRoot':
                                        name = parent.get_parent().get_name()
                                    else:
                                        name = parent.get_name()

                                children[name] = node_path

                                self.asset_node_children_collector(inner, assoc_key)
                    else:
                        name = node.get_name()
                        node_path = node
                        children[name] = node_path

                return children

            if assoc_key is False:
                children = []
                for node in nodes:
                    if node.get_num_children() > 0:
                        for inner in node.get_children():
                            for num in range(len(inner.get_children())):
                                node_path = inner.get_children().get_path(num)

                                children.append(node_path)

                                self.asset_node_children_collector(inner, assoc_key)
                    else:
                        name = node.get_name()
                        node_path = node
                        children[name] = node_path

                return children

    def get_actor_bullet_shape_nodes(self, assets, type):
        if (assets and type
                and isinstance(assets, dict)
                and isinstance(type, str)):
            lvl_npcs = []
            for k in assets:
                if k == 'name':
                    if type == "NPC":
                        if "NPC" in assets[k]:
                            name = assets[k]
                            if not render.find("**/{0}:BS".format(name)).is_empty():
                                lvl_npcs = render.find("**/{0}:BS".format(name))

                    elif type == "Player":
                        if "Player" in assets[k]:
                            name = assets[k]
                            if not render.find("**/{0}:BS".format(name)).is_empty():
                                lvl_npcs = render.find("**/{0}:BS".format(name))
            if lvl_npcs:
                return lvl_npcs

    def get_actor_bullet_shape_node(self, asset, type):
        if (asset and type
                and isinstance(asset, str)
                and isinstance(type, str)):
            if type == "NPC":
                if "NPC" in asset:
                    name = asset

                    if not render.find("**/{0}:BS".format(name)).is_empty():
                        return render.find("**/{0}:BS".format(name))

            elif type == "Player":
                if "Player" in asset:
                    name = asset
                    if not render.find("**/{0}:BS".format(name)).is_empty():
                        return render.find("**/{0}:BS".format(name))

    def get_static_bullet_shape_node(self, asset):
        if asset and isinstance(asset, str):
            if "BS" not in asset:
                if not render.find("**/{0}:BS".format(asset)).is_empty():
                    return render.find("**/{0}:BS".format(asset))

    def cfg_collector(self, path):
        """ Function    : cfg_collector

            Description : Collect json config files.

            Input       : None

            Output      : None

            Return      : Dictionary
        """
        cfg_path = self.transform_path(path=path, style='compat')
        configs = {}
        if exists(cfg_path):
            for root, dirs, files in walk(cfg_path, topdown=True):
                for file in files:
                    if file.endswith(".json"):
                        key = re.sub('.json$', '', file)
                        path = str(PurePath("{0}/".format(root), file))
                        configs[key] = Filename(path).to_os_specific()
            return configs

    def fonts_collector(self):
        """ Function    : fonts_collector

            Description : Collect fonts.

            Input       : None

            Output      : None

            Return      : Dictionary
        """
        font_path = self.transform_path(path="{0}/Settings/UI".format(self.game_dir),
                                        style='compat')
        fonts = {}
        if exists(font_path):
            for root, dirs, files in walk(font_path, topdown=True):
                for file in files:
                    if file.endswith(".ttf"):
                        key = re.sub('.ttf$', '', file)
                        path = str(PurePath("{0}/".format(root), file))
                        fonts[key] = Filename.from_os_specific(path).getFullpath()
            return fonts

    def textures_collector(self, path):
        """ Function    : textures_collector

            Description : Collect textures.

            Input       : None

            Output      : None

            Return      : Dictionary
        """
        tex_path = self.transform_path(path=path, style='compat')
        textures = {}
        if exists(tex_path):
            for root, dirs, files in walk(tex_path, topdown=True):
                for file in files:
                    if file.endswith(".png"):
                        key = re.sub('.png$', '', file)
                        path = str(PurePath("{0}/".format(root), file))
                        textures[key] = Filename.from_os_specific(path).getFullpath()
                    elif file.endswith(".jpg"):
                        key = re.sub('.jpg$', '', file)
                        path = str(PurePath("{0}/".format(root), file))
                        textures[key] = Filename.from_os_specific(path).getFullpath()
            return textures

    def ui_geom_collector(self):
        """ Function    : ui_geom_collector

            Description : Collect textures.

            Input       : None

            Output      : None

            Return      : Dictionary
        """
        tex_path = self.transform_path(path="{0}/Settings/UI/ui_tex/menu/".format(self.game_dir),
                                       style='compat')
        ui_geoms = {}
        if exists(tex_path):
            for root, dirs, files in walk(tex_path, topdown=True):
                for file in files:
                    if file.endswith(".egg"):
                        key = re.sub('.egg$', '', file)
                        path = str(PurePath("{0}/".format(root), file))
                        ui_geoms[key] = Filename.from_os_specific(path).getFullpath()
                    elif file.endswith(".egg.bam"):
                        key = re.sub('.egg.bam$', '', file)
                        path = str(PurePath("{0}/".format(root), file))
                        ui_geoms[key] = Filename.from_os_specific(path).getFullpath()
            return ui_geoms

    def videos_collector(self):
        """ Function    : videos_collector

            Description : Collect game asset videos.

            Input       : None

            Output      : None

            Return      : Dictionary
        """
        sound_path = self.transform_path(path="{0}/Assets/Videos/".format(self.game_dir), style='compat')
        videos = {}
        if exists(sound_path):
            for root, dirs, files in walk(sound_path, topdown=True):
                for file in files:
                    if file.endswith(".mkv"):
                        key = re.sub('.mkv$', '', file)
                        path = str(PurePath("{0}/".format(root), file))
                        videos[key] = Filename.from_os_specific(path).getFullpath()
            return videos

        """ Enable this when game will be ready for distribution
        else:
            logging.critical("\nI'm trying to load video assets, but there aren't suitable video assets. "
                             "\nCurrent path: {0}".format(sound_path))
            sys_exit("\nSomething is getting wrong. Please, check the game log first")
        """

    def sounds_collector(self):
        """ Function    : sounds_collector

            Description : Collect game asset sounds.

            Input       : None

            Output      : None

            Return      : Dictionary
        """
        sound_path = self.transform_path(path="{0}/Assets/Sounds".format(self.game_dir), style='compat')
        sounds = {}
        if exists(sound_path):
            for root, dirs, files in walk(sound_path, topdown=True):
                for file in files:
                    if file.endswith(".ogg"):
                        key = re.sub('.ogg$', '', file)
                        path = str(PurePath("{0}/".format(root), file))
                        sounds[key] = Filename.from_os_specific(path).getFullpath()
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

    def assets_pos_collector_no_player(self, player, exclude):
        """ Function    : assets_pos_collector_no_player

            Description : Collect game asset positions except for an actor.

            Input       : Nodepath, List

            Output      : None

            Return      : Dictionary
        """
        if (player and exclude
                and isinstance(exclude, list)):
            assets = base.asset_nodes_collector()
            t = []
            items = {}
            for asset in assets:
                # We exclude player from assets,
                # we need to retrieve the distance
                if asset.get_name() != player.get_name():
                    t.append(asset)

            for n, x in enumerate(exclude, 0):
                # We exclude any item from assets,
                # we need to retrieve the distance
                # TODO: Remove this dirty hack
                try:
                    if t[n].get_name() == x:
                        t.pop(n)
                except IndexError:
                    pass
            assets_children = base.asset_node_children_collector(
                t, assoc_key=True)

            if assets_children:
                for key in assets_children:
                    parent_node = assets_children[key].get_parent().get_parent()
                    # Get bullet shape node path if it's here
                    if (not parent_node.get_parent().is_empty()
                            and 'BS' in parent_node.get_parent().get_name()):
                        bullet_shape_node = parent_node.get_parent()
                        items[key] = (bullet_shape_node.get_pos())
                    elif (not parent_node.get_parent().is_empty()
                          and 'BS' not in parent_node.get_parent().get_name()):
                        items[key] = (parent_node.get_pos())
                return items

    def navmesh_collector(self):
        """ Function    : navmesh_collector

            Description : Collect game navmeshes.

            Input       : None

            Output      : None

            Return      : Dictionary
        """
        sound_path = self.transform_path(path="{0}/Assets/NavMeshes".format(self.game_dir), style='compat')
        sounds = {}
        if exists(sound_path):
            for root, dirs, files in walk(sound_path, topdown=True):
                for file in files:
                    if file.endswith(".csv"):
                        key = re.sub('.csv$', '', file)
                        path = str(PurePath("{0}/".format(root), file))
                        sounds[key] = Filename.from_os_specific(path).getFullpath()
            return sounds

        """ Enable this when game will be ready for distribution
        else:
            logging.critical("\nI'm trying to load navmesh assets, but there aren't suitable navmesh assets. "
                             "\nCurrent path: {0}".format(navmesh_path))
            sys_exit("\nSomething is getting wrong. Please, check the game log first")
        """

    def distance_calculate(self, items, actor):
        """ Function    : distance_calculate

            Description : Calculate a distance between objects and actor.

            Input       : Dict, Nodepath

            Output      : None

            Return      : Dictionary
        """

        if (items and actor
                and isinstance(items, dict)):
            # Do some minimum distance calculate here
            vect_x = None
            vect_y = None
            vect_z = None
            remained = {}
            for key in items:
                # Subtract actor vector from item vector.
                if not actor.get_parent().is_empty():
                    # Get bullet shape node path if it's here
                    if 'BS' in actor.get_parent().get_name():
                        vect_x = items[key].get_x() - actor.get_parent().get_x()
                        vect_y = items[key].get_y() - actor.get_parent().get_y()
                        vect_z = items[key].get_z() - actor.get_parent().get_z()
                    elif 'BS' not in actor.get_parent().get_name():
                        vect_x = items[key].get_x() - actor.get_x()
                        vect_y = items[key].get_y() - actor.get_y()
                        vect_z = items[key].get_z() - actor.get_z()
                    remained[key] = (round(vect_x, 1),
                                     round(vect_y, 1),
                                     round(vect_z, 1))
            return remained

    def npc_distance_calculate(self, player, actor):
        """ Function    : distance_calculate

            Description : Calculate a distance between player and actor.

            Input       : Nodepath

            Output      : None

            Return      : Dictionary
        """

        if player and actor:
            # Do some minimum distance calculate here
            vect_x = None
            vect_y = None
            vect_z = None
            distance = {}
            # Subtract actor vector from item vector.
            if not actor.get_parent().is_empty():
                # Get bullet shape node path if it's here
                if ('BS' in player.get_parent().get_name()
                        and 'BS' in actor.get_parent().get_name()):
                    vect_x = player.get_parent().get_x() - actor.get_parent().get_x()
                    vect_y = player.get_parent().get_y() - actor.get_parent().get_y()
                    vect_z = player.get_parent().get_z() - actor.get_parent().get_z()
                elif ('BS' not in player.get_parent().get_name()
                      and 'BS' not in actor.get_parent().get_name()):
                    vect_x = player.get_x() - actor.get_x()
                    vect_y = player.get_y() - actor.get_y()
                    vect_z = player.get_z() - actor.get_z()
                """distance["vector"] = (round(vect_x, 1),
                                      round(vect_y, 1),
                                      round(vect_z, 1))"""
                distance["vector"] = Vec3(vect_x, vect_y, vect_z)
            return distance

    def level_of_details(self, obj):
        """ Function    : level_of_details

            Description : Set the level of details for scene object.

            Input       : Nodepath

            Output      : None

            Return      : None
        """
        if obj:
            lod = LODNode('{0} LOD node'.format(obj.name))
            scene_lod = NodePath(lod)
            scene_lod.reparent_to(render)
            lod.add_switch(100.0, 0.0)
            obj.reparent_to(scene_lod)

    def set_textures_srgb(self, bool):
        """ Function    : set_textures_srgb

            Description : Set sRGB format for all loaded textures

            Input       : Boolean

            Output      : None

            Return      : False
        """
        if bool:
            for tex in render.findAllTextures():
                if tex.getNumComponents() == 4:
                    tex.setFormat(Texture.F_srgb_alpha)
                elif tex.getNumComponents() == 3:
                    tex.setFormat(Texture.F_srgb)

    def video_status_task(self, media, type, file, task):
        """ Function    : video_status_task

            Description : Task for video wall.

            Input       : Nodepath, String, Task

            Output      : None

            Return      : Task event
        """
        if media and type and isinstance(type, str) and "REDSTUDIO_FHD" in file:
            base.accept("escape", media.stop)

        if AudioSound.status(media) == 1:
            if type == "player_avatar":
                media.play()
            else:
                media.stop()

            if type != "menu_scene":
                if not render2d.find("**/VideoWall").is_empty():
                    render2d.find("**/VideoWall").remove_node()

            if type == "main_menu":
                self.intro_mode = False
                self.menu_mode = True
                self.menu.load_main_menu()
                # Disable the camera trackball controls.
                self.disable_mouse()
                props = WindowProperties()
                props.set_cursor_hidden(False)
                self.win.request_properties(props)
                self.load_video(file="MENU_SCENE_VID", type="menu_scene")
                return task.done

        return task.cont

    def menu_scene_video_status_task(self, task):
        """ Function    : menu_scene_video_status_task

            Description : Task for video wall.

            Input       : Nodepath, String, Task

            Output      : None

            Return      : Task event
        """
        if base.menu_mode is False and base.game_mode:
            if not render2d.find("**/VideoWall").is_empty():
                render2d.find("**/VideoWall").remove_node()
            return task.done

        return task.cont

    def load_video(self, file, type):
        """ Function    : load_video

            Description : Loads videofile to screen.

            Input       : String

            Output      : None

            Return      : Dictionary
        """
        if (file and type
                and isinstance(file, str) and isinstance(type, str)):
            videos = self.videos_collector()

            if videos and videos.get(file):
                tex = MovieTexture(file)
                success = tex.read(videos.get(file))
                if success:
                    # Set up a fullscreen card to set the video texture on.
                    cm = CardMaker("VideoWall")
                    cm.set_frame_fullscreen_quad()

                    # Tell the CardMaker to create texture coordinates that take into
                    # account the padding region of the texture.
                    cm.set_uv_range(tex)

                    # Now place the card in the scene graph and apply the texture to it.
                    card = NodePath(cm.generate())

                    if type == "loading_menu":
                        if not render2d.find("**/LoadingScreen").is_empty():
                            loading_screen_np = render2d.find("**/LoadingScreen")
                            card.reparent_to(loading_screen_np)

                    elif type == "main_menu":
                        card.reparent_to(render2d)

                    elif type == "player_avatar":
                        card.reparent_to(render2d)

                    card.set_texture(tex)

                    if type == "loading_menu":
                        card.set_scale(0.3)
                        card.set_pos(0, 0, 0)

                    if type == "menu_scene":
                        card.reparent_to(render2d)

                    if type == "player_avatar":
                        card.set_scale(0.3, 0.3, 0.15)
                        card.set_pos(0, 0, -0.85)

                    media = base.loader.load_sfx(videos[file])

                    if "MENU_SCENE_VID" in media.get_name():
                        base.menu_scene_vid = media

                    # Synchronize the video to the sound.
                    tex.synchronize_to(media)

                    if type == "main_menu":
                        media.play()

                        taskMgr.add(self.video_status_task,
                                    "video_status",
                                    extraArgs=[media, type, file],
                                    appendTask=True)

                    if type == "loading_menu":
                        return media

                    if type == "menu_scene":
                        AudioSound.set_loop(media, loop=True)
                        media.play()

                        taskMgr.add(self.menu_scene_video_status_task,
                                    "menu_scene_video_status_task",
                                    appendTask=True)

                    if type == "player_avatar":
                        media.play()

                        taskMgr.add(self.video_status_task,
                                    "video_status",
                                    extraArgs=[media, type, file],
                                    appendTask=True)

                else:
                    if type == "main_menu":
                        self.intro_mode = False
                        self.menu_mode = True
                        self.menu.load_main_menu()

    def load_menu_scene(self):
        self.menu_mode = True
        self.menu.load_main_menu()
        self.load_video(file="MENU_SCENE_VID", type="menu_scene")


if not cfg_is_broken:
    app = Main()
    app.load_video(file="REDSTUDIO_FHD", type="main_menu")

    if __name__ == '__main__':
        app.run()
else:
    app = Error()
    # app.load_video(file="MENU_SCENE_VID", type="menu_scene")
    if __name__ == '__main__':
        app.run()
