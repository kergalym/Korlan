import json
import sys
import logging

from os.path import exists
from pathlib import Path

from direct.gui.DirectGui import *
from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.OnscreenImage import TransparencyAttrib
from direct.showbase.ShowBaseGlobal import aspect2d
from panda3d.core import FontPool
from panda3d.core import TextNode

from Engine.Scenes.playworker import PlayWorker
from Settings.menu_settings import MenuSettings
from Settings.dev_menu_settings import DevMode
from Settings.gfx_menu_settings import Graphics
from Settings.sfx_menu_settings import Sound
from Settings.kmp_menu_settings import Keymap
from Settings.lng_menu_settings import Language
from Settings.UI.loading_ui import LoadingUI

from Settings.UI.dev_menu_ui import DevMenuUI
from Settings.UI.options_menu_ui import OptionsMenuUI


class MenuUI(MenuSettings):
    def __init__(self):

        """ Imports, Variables, etc """
        MenuSettings.__init__(self)
        self.base = base
        self.game_dir = base.game_dir
        self.images = base.textures_collector(path="{0}/Settings/UI".format(self.game_dir))
        self.fonts = base.fonts_collector()
        self.configs = base.cfg_collector(path="{0}/Settings/UI".format(self.game_dir))
        self.lng_configs = base.cfg_collector(path="{0}/Configs/Language/".format(self.game_dir))
        self.loading_ui = LoadingUI()
        self.json = json
        self.pos_X = 0
        self.pos_Y = 0
        self.pos_Z = 0

        self.w = 0
        self.h = 0

        self.node_frame_item = None

        self.rgba_gray_color = (.3, .3, .3, 1.)
        self.game_mode = base.game_mode
        self.menu_mode = base.menu_mode

        """ Frames """
        self.base.frame = None

        """ Frame Sizes """
        # Left, right, bottom, top
        self.base.frame_size = [-3, -0.9, -1, 3]

        """ Frame Colors """
        self.frm_opacity = 1

        """ Logo & Ornament Scaling, Positioning """
        self.logo = None
        self.ornament_left = None
        self.ornament_right = None
        self.logo_scale = (0.33, 0.30, 0.30)
        self.logo_pos = (-1.4, 0, 0.4)
        self.ornament_scale = (1.40, 0.05, 0.05)
        self.ornament_l_pos = (-1.8, 0, -0.1)
        self.ornament_r_pos = (-1.0, 0, -0.1)

        self.ornament_l_lng_pos = (-1.8, 0, -0.1)
        self.ornament_r_lng_pos = (-0.4, 0, -0.1)

        """ Buttons, Label Scaling """
        self.lbl_scale = .03
        self.btn_scale = .04
        self.inp_scale = .04

        """ Misc """
        self.playworker = PlayWorker()
        self.dev_mode = DevMode()
        self.gfx = Graphics()
        self.snd = Sound()
        self.kmp = Keymap()
        self.lng = Language()

        self.menu_options = OptionsMenuUI()
        self.menu_dev = DevMenuUI()

        # instance of the abstract class
        self.font = FontPool
        self.text = TextNode("TextNode")

        self.logging = logging
        self.logging.basicConfig(filename="{0}/critical.log".format(Path.home()), level=logging.CRITICAL)

        self.menu_font = None

        self.cfg_path = None

        if exists(self.configs['cfg_path']):
            with open(self.configs['cfg_path']) as json_file:
                self.json = json.load(json_file)

        self.language = None

        if self.json["game_config_path"]:
            self.cfg_path = self.json["game_config_path"]

            if exists(self.cfg_path):
                lng_to_load = self.input_validate(self.cfg_path, 'lng')
                with open(self.lng_configs['lg_{0}'.format(lng_to_load)], 'r') as json_file:
                    self.language = json.load(json_file)

        """ Buttons & Fonts"""
        self.menu_font = self.fonts['OpenSans-Regular']

        self.btn_new_game = None
        self.btn_load_game = None
        self.btn_save_game = None
        self.btn_options = None
        self.btn_credits = None
        self.btn_dev_mode = None
        self.btn_exit = None

    def load_main_menu(self):
        """ Function    : load_main_menu

            Description : Load Main menu.

            Input       : None

            Output      : None

            Return      : None
        """

        ui_geoms = base.ui_geom_collector()

        maps = base.loader.loadModel(ui_geoms['btn_t_icon'])
        geoms = (maps.find('**/button_any'),
                 maps.find('**/button_pressed'),
                 maps.find('**/button_rollover'))

        self.base.frame = DirectFrame(frameColor=(0, 0, 0, self.frm_opacity),
                                      frameSize=self.base.frame_size)
        self.base.build_info.reparent_to(self.base.frame)

        self.logo = OnscreenImage(image=self.images['korlan_logo_tengri'],
                                  pos=self.logo_pos)
        self.ornament_left = OnscreenImage(image=self.images['ornament_kz'],
                                           pos=self.ornament_l_pos, color=(63.9, 63.9, 63.9, 0.5))
        self.ornament_right = OnscreenImage(image=self.images['ornament_kz'],
                                            pos=self.ornament_r_pos, color=(63.9, 63.9, 63.9, 0.5))

        self.btn_new_game = DirectButton(text=self.language['new_game'],
                                         text_fg=(255, 255, 255, 0.9),
                                         text_font=self.font.load_font(self.menu_font),
                                         frameColor=(255, 255, 255, self.frm_opacity),
                                         scale=self.btn_scale, borderWidth=(self.w, self.h),
                                         parent=self.base.frame,
                                         geom=geoms, geom_scale=(15.3, 0, 2),
                                         clickSound=self.base.sound_gui_click,
                                         command=self.load_new_game_wrapper)

        self.btn_load_game = DirectButton(text=self.language['load_game'],
                                          text_fg=(255, 255, 255, 0.9),
                                          text_font=self.font.load_font(self.menu_font),
                                          frameColor=(255, 255, 255, self.frm_opacity),
                                          scale=self.btn_scale, borderWidth=(self.w, self.h),
                                          parent=self.base.frame,
                                          geom=geoms, geom_scale=(15.3, 0, 2),
                                          clickSound=self.base.sound_gui_click,
                                          command=self.load_game_wrapper)

        self.btn_save_game = DirectButton(text=self.language['save_game'],
                                          text_fg=(255, 255, 255, 0.9),
                                          text_font=self.font.load_font(self.menu_font),
                                          frameColor=(255, 255, 255, self.frm_opacity),
                                          scale=self.btn_scale, borderWidth=(self.w, self.h),
                                          parent=self.base.frame,
                                          geom=geoms, geom_scale=(15.3, 0, 2),
                                          clickSound=self.base.sound_gui_click,
                                          command=self.save_game_wrapper)

        self.btn_options = DirectButton(text=self.language['options'],
                                        text_fg=(255, 255, 255, 0.9),
                                        text_font=self.font.load_font(self.menu_font),
                                        frameColor=(255, 255, 255, self.frm_opacity),
                                        scale=self.btn_scale, borderWidth=(self.w, self.h),
                                        parent=self.base.frame,
                                        geom=geoms, geom_scale=(15.3, 0, 2),
                                        clickSound=self.base.sound_gui_click,
                                        command=self.menu_options.load_options_menu)

        self.btn_credits = DirectButton(text=self.language['credits'],
                                        text_fg=(255, 255, 255, 0.9),
                                        text_font=self.font.load_font(self.menu_font),
                                        frameColor=(255, 255, 255, self.frm_opacity),
                                        scale=self.btn_scale, borderWidth=(self.w, self.h),
                                        parent=self.base.frame,
                                        geom=geoms, geom_scale=(15.3, 0, 2),
                                        clickSound=self.base.sound_gui_click,
                                        command="")

        self.btn_dev_mode = DirectButton(text=self.language['dev_mode'],
                                         text_fg=(255, 255, 255, 0.9),
                                         text_font=self.font.load_font(self.menu_font),
                                         frameColor=(255, 255, 255, self.frm_opacity),
                                         scale=self.btn_scale, borderWidth=(self.w, self.h),
                                         parent=self.base.frame,
                                         geom=geoms, geom_scale=(15.3, 0, 2),
                                         clickSound=self.base.sound_gui_click,
                                         command=self.menu_dev.load_dev_mode_menu)

        self.btn_exit = DirectButton(text=self.language['quit_game'],
                                     text_fg=(255, 255, 255, 0.9),
                                     text_font=self.font.load_font(self.menu_font),
                                     frameColor=(255, 255, 255, self.frm_opacity),
                                     scale=self.btn_scale, borderWidth=(self.w, self.h),
                                     parent=self.base.frame,
                                     geom=geoms, geom_scale=(15.3, 0, 2),
                                     clickSound=self.base.sound_gui_click,
                                     command=sys.exit)
        self.base.frame.setPos(self.pos_X, self.pos_Y, self.pos_Z)
        self.logo.reparent_to(self.base.frame)
        self.logo.set_scale(self.logo_scale)

        self.ornament_right.reparent_to(self.base.frame)
        self.ornament_right.set_scale(self.ornament_scale)
        self.ornament_right.set_hpr(0.0, 0.0, -90.0)
        self.ornament_left.reparent_to(self.base.frame)
        self.ornament_left.set_scale(self.ornament_scale)
        self.ornament_left.set_hpr(0.0, 0.0, -90.0)
        self.ornament_right.set_transparency(TransparencyAttrib.MAlpha)
        self.ornament_left.set_transparency(TransparencyAttrib.MAlpha)

        self.btn_new_game.set_pos(-1.4, 0, 0)
        self.btn_load_game.set_pos(-1.4, 0, -0.1)
        self.btn_save_game.set_pos(-1.4, 0, -0.2)
        self.btn_options.set_pos(-1.4, 0, -0.3)
        self.btn_credits.set_pos(-1.4, 0, -0.4)
        self.btn_dev_mode.set_pos(-1.4, 0, -0.5)
        self.btn_exit.set_pos(-1.4, 0, -0.6)

        self.menu_mode = True

    def unload_main_menu(self):
        """ Function    : unload_main_menu

            Description : Unload Main menu.

            Input       : None

            Output      : None

            Return      : None
        """
        self.base.build_info.reparent_to(aspect2d)
        self.base.frame.hide()

    """ Wrapper functions """
    """ Direct* object doesn't allow passing it's instance directly before it created.
        So, we pass it through wrapper methods
    """

    def load_new_game_wrapper(self):
        """ Function    : load_new_game_wrapper

            Description : Wrapper function.

            Input       : None

            Output      : None

            Return      : None
        """
        if isinstance(self.game_mode, bool):
            self.unload_main_menu()
            self.game_mode = True
            self.menu_mode = False

            self.loading_ui.set_parallel_loading(type="new_game")

    def load_game_wrapper(self):
        """ Function    : load_game_wrapper

            Description : Wrapper function.

            Input       : None

            Output      : None

            Return      : None
        """
        if isinstance(self.game_mode, bool):
            self.playworker.load_game()

    def save_game_wrapper(self):
        """ Function    : save_game_wrapper

            Description : Wrapper function.

            Input       : None

            Output      : None

            Return      : None
        """
        if isinstance(self.game_mode, bool):
            self.playworker.save_game()

    def delete_game_wrapper(self):
        """ Function    : delete_game_wrapper

            Description : Wrapper function.

            Input       : None

            Output      : None

            Return      : None
        """
        if isinstance(self.game_mode, bool):
            self.playworker.delete_game()

