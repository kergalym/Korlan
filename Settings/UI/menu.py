import json
import sys
import logging

from os.path import exists
from pathlib import Path

from direct.gui.DirectGui import *
from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.OnscreenImage import TransparencyAttrib
from panda3d.core import FontPool
from panda3d.core import TextNode

from Engine.Scenes.playworker import PlayWorker
from Settings.menu_settings import MenuSettings
from Settings.menu_settings import DevMode
from Settings.menu_settings import Graphics
from Settings.menu_settings import Sound
from Settings.menu_settings import Keymap
from Settings.menu_settings import Language
from Engine.Scenes.level_one import LevelOne

from Settings.UI.menu_dev import MenuDev
from Settings.UI.menu_options import MenuOptions


class Menu:
    def __init__(self):

        """ Imports, Variables, etc """
        self.base = base
        self.game_dir = base.game_dir
        self.level_one = LevelOne()
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
        self.btn_scale = .03
        self.inp_scale = .04

        """ Misc """
        self.playworker = PlayWorker()
        self.m_settings = MenuSettings()
        self.dev_mode = DevMode()
        self.gfx = Graphics()
        self.snd = Sound()
        self.kmp = Keymap()
        self.lng = Language()

        self.menu_options = MenuOptions()
        self.menu_dev = MenuDev()

        # instance of the abstract class
        self.font = FontPool
        self.text = TextNode("TextNode")

        self.logging = logging
        self.logging.basicConfig(filename="{0}/critical.log".format(Path.home()), level=logging.CRITICAL)

        self.menu_font = None

        self.cfg_path = None

        if exists('{0}/Settings/UI/cfg_path.json'.format(self.game_dir)):
            with open('{0}/Settings/UI/cfg_path.json'.format(self.game_dir)) as json_file:
                self.json = json.load(json_file)

        self.language = None

        if self.json["game_config_path"]:
            self.cfg_path = self.json["game_config_path"]

            if exists(self.cfg_path):
                lng_to_load = self.m_settings.input_validate(self.cfg_path, 'lng')
                with open('{0}/Configs/Language/lg_{1}.json'.format(self.game_dir, lng_to_load), 'r') as json_file:
                    self.language = json.load(json_file)

        """ Buttons & Fonts"""
        # self.menu_font = 'Settings/UI/Open_Sans/OpenSans-Regular.ttf'
        self.menu_font = '{0}/Settings/UI/JetBrainsMono-1.0.2/ttf/JetBrainsMono-Regular.ttf'.format(self.game_dir)

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
        self.base.frame = DirectFrame(frameColor=(0, 0, 0, self.frm_opacity),
                                      frameSize=self.base.frame_size)

        self.logo = OnscreenImage(image='{0}/Settings/UI/ui_tex/korlan_logo_tengri.png'.format(self.game_dir),
                                  pos=self.logo_pos)
        self.ornament_left = OnscreenImage(image='{0}/Settings/UI/ui_tex/ornament_kz.png'.format(self.game_dir),
                                           pos=self.ornament_l_pos, color=(63.9, 63.9, 63.9, 0.5))
        self.ornament_right = OnscreenImage(image='{0}/Settings/UI/ui_tex/ornament_kz.png'.format(self.game_dir),
                                            pos=self.ornament_r_pos, color=(63.9, 63.9, 63.9, 0.5))

        self.btn_new_game = DirectButton(text=self.language['new_game'], text_bg=(0, 0, 0, 1),
                                         text_fg=(255, 255, 255, 0.9),
                                         text_font=self.font.load_font(self.menu_font),
                                         frameColor=(255, 255, 255, self.frm_opacity),
                                         scale=self.btn_scale, borderWidth=(self.w, self.h),
                                         parent=self.base.frame,
                                         command=self.load_new_game_wrapper)

        self.btn_load_game = DirectButton(text=self.language['load_game'], text_bg=(0, 0, 0, 1),
                                          text_fg=(255, 255, 255, 0.9),
                                          text_font=self.font.load_font(self.menu_font),
                                          frameColor=(255, 255, 255, self.frm_opacity),
                                          scale=self.btn_scale, borderWidth=(self.w, self.h),
                                          parent=self.base.frame,
                                          command=self.load_game_wrapper)

        self.btn_save_game = DirectButton(text=self.language['save_game'], text_bg=(0, 0, 0, 1),
                                          text_fg=(255, 255, 255, 0.9),
                                          text_font=self.font.load_font(self.menu_font),
                                          frameColor=(255, 255, 255, self.frm_opacity),
                                          scale=self.btn_scale, borderWidth=(self.w, self.h),
                                          parent=self.base.frame,
                                          command=self.save_game_wrapper)

        self.btn_options = DirectButton(text=self.language['options'], text_bg=(0, 0, 0, 1),
                                        text_fg=(255, 255, 255, 0.9),
                                        text_font=self.font.load_font(self.menu_font),
                                        frameColor=(255, 255, 255, self.frm_opacity),
                                        scale=self.btn_scale, borderWidth=(self.w, self.h),
                                        parent=self.base.frame,
                                        command=self.menu_options.load_options_menu)

        self.btn_credits = DirectButton(text=self.language['credits'], text_bg=(0, 0, 0, 1),
                                        text_fg=(255, 255, 255, 0.9),
                                        text_font=self.font.load_font(self.menu_font),
                                        frameColor=(255, 255, 255, self.frm_opacity),
                                        scale=self.btn_scale, borderWidth=(self.w, self.h),
                                        parent=self.base.frame,
                                        command="")

        self.btn_dev_mode = DirectButton(text=self.language['dev_mode'], text_bg=(0, 0, 0, 1),
                                         text_fg=(255, 255, 255, 0.9),
                                         text_font=self.font.load_font(self.menu_font),
                                         frameColor=(255, 255, 255, self.frm_opacity),
                                         scale=self.btn_scale, borderWidth=(self.w, self.h),
                                         parent=self.base.frame,
                                         command=self.menu_dev.load_dev_mode_menu)

        self.btn_exit = DirectButton(text=self.language['exit'], text_bg=(0, 0, 0, 1),
                                     text_fg=(255, 255, 255, 0.9),
                                     text_font=self.font.load_font(self.menu_font),
                                     frameColor=(255, 255, 255, self.frm_opacity),
                                     scale=self.btn_scale, borderWidth=(self.w, self.h),
                                     parent=self.base.frame,
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
            self.level_one.load_new_game()

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

