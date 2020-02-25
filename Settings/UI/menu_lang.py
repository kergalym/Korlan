import json
import logging

from os.path import exists
from pathlib import Path

from direct.gui.DirectGui import *
from direct.gui.OnscreenImage import OnscreenImage, TransparencyAttrib
from panda3d.core import FontPool
from panda3d.core import TextNode

from Settings.menu_settings import MenuSettings
from Settings.menu_settings import Language


class MenuLanguage:
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
        self.base.frame_int_lang = None

        """ Frame Sizes """
        self.base.frame_int_lang_size = [-3, -0.3, -1, 3]

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
        self.m_settings = MenuSettings()
        self.lng = Language()

        """ Language Menu Objects """
        self.lbl_lang_title = None
        self.lbl_english = None
        self.lbl_kazakh = None
        self.lbl_russian = None

        self.rad_english = None
        self.rad_kazakh = None
        self.rad_russian = None

        self.btn_param_accept = None
        self.btn_param_back = None
        self.btn_param_decline = None
        self.btn_param_defaults = None

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

    def load_language_menu(self):
        self.logo = OnscreenImage(image='{0}/Settings/UI/ui_tex/korlan_logo_tengri.png'.format(self.game_dir),
                                  pos=self.logo_pos)
        self.ornament_left = OnscreenImage(image='{0}/Settings/UI/ui_tex/ornament_kz.png'.format(self.game_dir),
                                           pos=self.ornament_l_pos, color=(63.9, 63.9, 63.9, 0.5))
        self.ornament_right = OnscreenImage(image='{0}/Settings/UI/ui_tex/ornament_kz.png'.format(self.game_dir),
                                            pos=self.ornament_r_pos, color=(63.9, 63.9, 63.9, 0.5))

        self.base.frame_int_lang = DirectFrame(frameColor=(0, 0, 0, self.frm_opacity),
                                               frameSize=self.base.frame_int_lang_size)
        self.base.frame_int_lang.setPos(self.pos_X, self.pos_Y, self.pos_Z)

        self.lbl_lang_title = DirectLabel(text=self.language['language'], text_bg=(0, 0, 0, 1),
                                          text_fg=(155, 155, 255, 0.9),
                                          text_font=self.font.load_font(self.menu_font),
                                          frameColor=(255, 255, 255, self.frm_opacity),
                                          scale=.05, borderWidth=(self.w, self.h),
                                          parent=self.base.frame_int_lang)

        self.lbl_english = DirectLabel(text=self.language['english'], text_bg=(0, 0, 0, 1),
                                       text_fg=(255, 255, 255, 0.9),
                                       text_font=self.font.load_font(self.menu_font),
                                       frameColor=(255, 255, 255, self.frm_opacity),
                                       scale=self.lbl_scale, borderWidth=(self.w, self.h),
                                       parent=self.base.frame_int_lang)

        self.lbl_kazakh = DirectLabel(text=self.language['kazakh'], text_bg=(0, 0, 0, 1),
                                      text_fg=(255, 255, 255, 0.9),
                                      text_font=self.font.load_font(self.menu_font),
                                      frameColor=(255, 255, 255, self.frm_opacity),
                                      scale=self.lbl_scale, borderWidth=(self.w, self.h),
                                      parent=self.base.frame_int_lang)

        self.lbl_russian = DirectLabel(text=self.language['russian'], text_bg=(0, 0, 0, 1),
                                       text_fg=(255, 255, 255, 0.9),
                                       text_font=self.font.load_font(self.menu_font),
                                       frameColor=(255, 255, 255, self.frm_opacity),
                                       scale=self.lbl_scale, borderWidth=(self.w, self.h),
                                       parent=self.base.frame_int_lang)

        self.btn_param_defaults = DirectButton(text="Load defaults", text_bg=(0, 0, 0, 1),
                                               text_fg=(255, 255, 255, 0.9),
                                               text_font=self.font.load_font(self.menu_font),
                                               frameColor=(255, 255, 255, self.frm_opacity),
                                               scale=self.btn_scale, borderWidth=(self.w, self.h),
                                               parent=self.base.frame_int_lang,
                                               command=self.lng.set_default_language)

        self.btn_param_back = DirectButton(text="Back", text_bg=(0, 0, 0, 1),
                                           text_fg=(255, 255, 255, 0.9),
                                           text_font=self.font.load_font(self.menu_font),
                                           frameColor=(255, 255, 255, self.frm_opacity),
                                           scale=self.btn_scale, borderWidth=(self.w, self.h),
                                           parent=self.base.frame_int_lang,
                                           command=self.language_menu_unload)

        lng_value = self.lng.get_selected_language()

        radbuttons = [

            DirectRadioButton(text='', variable=[0], value=[lng_value['english']], pos=(-0.7, 0, -0.0),
                              parent=self.base.frame_int_lang, scale=.04,
                              command=self.lng.set_language_english, color=(63.9, 63.9, 63.9, 1)),

            DirectRadioButton(text='', variable=[0], value=[lng_value['kazakh']], pos=(-0.7, 0, -0.1),
                              parent=self.base.frame_int_lang, scale=.04,
                              command=self.lng.set_language_kazakh, color=(63.9, 63.9, 63.9, 1)),

            DirectRadioButton(text='', variable=[0], value=[lng_value['russian']], pos=(-0.7, 0, -0.2),
                              parent=self.base.frame_int_lang, scale=.04,
                              command=self.lng.set_language_russian, color=(63.9, 63.9, 63.9, 1))

        ]

        for radbutton in radbuttons:
            radbutton.setOthers(radbuttons)

        """ Positioning objects of the language menu:
            for two blocks
        """
        self.logo.reparent_to(self.base.frame_int_lang)
        self.logo.set_scale(self.logo_scale)

        self.ornament_right.reparent_to(self.base.frame_int_lang)
        self.ornament_right.set_scale(self.ornament_scale)
        self.ornament_right.set_hpr(0.0, 0.0, -90.0)
        self.ornament_left.reparent_to(self.base.frame_int_lang)
        self.ornament_left.set_scale(self.ornament_scale)
        self.ornament_left.set_hpr(0.0, 0.0, -90.0)
        self.ornament_right.set_transparency(TransparencyAttrib.MAlpha)
        self.ornament_left.set_transparency(TransparencyAttrib.MAlpha)

        self.ornament_left.set_pos(self.ornament_l_lng_pos)
        self.ornament_right.set_pos(self.ornament_r_lng_pos)

        self.lbl_lang_title.set_pos(-0.8, 0, 0.5)
        self.lbl_english.set_pos(-1.4, 0, 0)
        self.lbl_kazakh.set_pos(-1.4, 0, -0.1)
        self.lbl_russian.set_pos(-1.4, 0, -0.2)

        """ Second block is here """
        self.btn_param_defaults.set_pos(-0.7, 0, -0.9)
        self.btn_param_back.set_pos(-1.6, 0, -0.9)
        self.menu_mode = True

    def language_menu_unload(self):
        if self.game_mode:
            self.base.frame_int_lang.destroy()
        self.base.frame_int_lang.destroy()
        self.logo.destroy()
        self.ornament_left.destroy()
        self.ornament_right.destroy()

