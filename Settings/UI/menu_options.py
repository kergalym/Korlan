import json
import logging

from os.path import exists
from pathlib import Path

from direct.gui.DirectGui import *
from direct.gui.OnscreenImage import OnscreenImage, TransparencyAttrib
from panda3d.core import FontPool
from panda3d.core import TextNode

from Settings.menu_settings import MenuSettings
from Settings.UI.menu_graphics import MenuGraphics
from Settings.UI.menu_sound import MenuSound
from Settings.UI.menu_keymap import MenuKeymap
from Settings.UI.menu_lang import MenuLanguage


class MenuOptions:
    def __init__(self):
        self.base = base
        self.game_dir = base.game_dir
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
        self.base.frame_int = None

        """ Frame Sizes """
        self.base.frame_int_size = [-3, -0.9, -1, 3]

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

        """ Buttons, Label Scaling """
        self.lbl_scale = .03
        self.btn_scale = .03
        self.inp_scale = .04

        """ Misc """
        self.m_settings = MenuSettings()
        self.ui_gfx = MenuGraphics()
        self.ui_snd = MenuSound()
        self.ui_kmp = MenuKeymap()
        self.ui_lng = MenuLanguage()

        """ Options Menu Objects """
        self.btn_gfx = None
        self.btn_sound = None
        self.btn_language = None
        self.btn_keymap = None
        self.btn_back_options = None

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

    def load_options_menu(self):
        self.logo = OnscreenImage(image='{0}/Settings/UI/ui_tex/korlan_logo_tengri.png'.format(self.game_dir),
                                  pos=self.logo_pos)
        self.ornament_left = OnscreenImage(image='{0}/Settings/UI/ui_tex/ornament_kz.png'.format(self.game_dir),
                                           pos=self.ornament_l_pos, color=(63.9, 63.9, 63.9, 0.5))
        self.ornament_right = OnscreenImage(image='{0}/Settings/UI/ui_tex/ornament_kz.png'.format(self.game_dir),
                                            pos=self.ornament_r_pos, color=(63.9, 63.9, 63.9, 0.5))

        self.base.frame_int = DirectFrame(frameColor=(0, 0, 0, self.frm_opacity),
                                          frameSize=self.base.frame_int_size)
        self.base.frame_int.setPos(self.pos_X, self.pos_Y, self.pos_Z)

        self.btn_gfx = DirectButton(text=self.language['graphics'], text_bg=(0, 0, 0, 1),
                                    text_fg=(255, 255, 255, 0.9),
                                    text_font=self.font.load_font(self.menu_font),
                                    frameColor=(255, 255, 255, self.frm_opacity),
                                    scale=self.btn_scale, borderWidth=(self.w, self.h),
                                    parent=self.base.frame_int,
                                    command=self.ui_gfx.load_graphics_menu)

        self.btn_sound = DirectButton(text=self.language['sound'], text_bg=(0, 0, 0, 1),
                                      text_fg=(255, 255, 255, 0.9),
                                      text_font=self.font.load_font(self.menu_font),
                                      frameColor=(255, 255, 255, self.frm_opacity),
                                      scale=self.btn_scale, borderWidth=(self.w, self.h),
                                      parent=self.base.frame_int,
                                      command=self.ui_snd.load_sound_menu)

        self.btn_language = DirectButton(text=self.language['language'], text_bg=(0, 0, 0, 1),
                                         text_fg=(255, 255, 255, 0.9),
                                         text_font=self.font.load_font(self.menu_font),
                                         frameColor=(255, 255, 255, self.frm_opacity),
                                         scale=self.btn_scale, borderWidth=(self.w, self.h),
                                         parent=self.base.frame_int,
                                         command=self.ui_lng.load_language_menu)

        self.btn_keymap = DirectButton(text=self.language['keymap'], text_bg=(0, 0, 0, 1),
                                       text_fg=(255, 255, 255, 0.9),
                                       text_font=self.font.load_font(self.menu_font),
                                       frameColor=(255, 255, 255, self.frm_opacity),
                                       scale=self.btn_scale, borderWidth=(self.w, self.h),
                                       parent=self.base.frame_int,
                                       command=self.ui_kmp.load_keymap_menu)

        self.btn_back_options = DirectButton(text=self.language['back'], text_bg=(0, 0, 0, 1),
                                             text_fg=(255, 255, 255, 0.9),
                                             text_font=self.font.load_font(self.menu_font),
                                             frameColor=(255, 255, 255, self.frm_opacity),
                                             scale=self.btn_scale, borderWidth=(self.w, self.h),
                                             parent=self.base.frame_int,
                                             command=self.options_menu_unload)

        self.btn_gfx.set_pos(-1.4, 0, 0)
        self.btn_sound.set_pos(-1.4, 0, -0.1)
        self.btn_language.set_pos(-1.4, 0, -0.2)
        self.btn_keymap.set_pos(-1.4, 0, -0.3)
        self.btn_back_options.set_pos(-1.4, 0, -0.4)
        self.logo.reparent_to(self.base.frame_int)
        self.logo.set_scale(self.logo_scale)

        self.ornament_right.reparent_to(self.base.frame_int)
        self.ornament_right.set_scale(self.ornament_scale)
        self.ornament_right.set_hpr(0.0, 0.0, -90.0)
        self.ornament_left.reparent_to(self.base.frame_int)
        self.ornament_left.set_scale(self.ornament_scale)
        self.ornament_left.set_hpr(0.0, 0.0, -90.0)
        self.ornament_right.set_transparency(TransparencyAttrib.MAlpha)
        self.ornament_left.set_transparency(TransparencyAttrib.MAlpha)
        self.menu_mode = True

    def options_menu_unload(self):
        if self.game_mode:
            self.base.frame_int.destroy()
        self.base.frame_int.destroy()
        """Reattach the destroyed logo to previous frame"""
        # self.logo.reparent_to(self.base.frame)
        # self.logo.set_scale(self.logo_scale)
        # self.ornament_left.reparent_to(self.base.frame)
        # self.ornament_right.reparent_to(self.base.frame)
        # self.ornament_left.set_pos(self.ornament_l_pos)
        # self.ornament_right.set_pos(self.ornament_r_pos)
        self.logo.destroy()
        self.ornament_left.destroy()
        self.ornament_right.destroy()

