import json
import logging

from os.path import exists
from pathlib import Path

from direct.gui.DirectGui import *
from direct.gui.OnscreenImage import OnscreenImage, TransparencyAttrib
from panda3d.core import FontPool
from panda3d.core import TextNode

from Settings.menu_settings import MenuSettings
from Settings.lng_menu_settings import Language


class LangMenuUI(Language):
    def __init__(self):
        Language.__init__(self)
        self.base = base
        self.game_dir = base.game_dir
        self.images = base.textures_collector(path="{0}/Settings/UI".format(self.game_dir))
        self.fonts = base.fonts_collector()
        self.configs = base.cfg_collector(path="{0}/Settings/UI".format(self.game_dir))
        self_configs = base.cfg_collector(path="{0}/Configs/Language/".format(self.game_dir))
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
        # Left, right, bottom, top
        self.base.frame_int_lang_size = [-0.9, 3, -1, 3]

        """ Frame Colors """
        self.frm_opacity = 0.9

        """ Logo & Ornament Scaling, Positioning """
        self.logo = None
        self.ornament_right = None
        self.logo_scale = (0.33, 0.30, 0.30)
        self.logo_pos = (-0.3, 0, 0.6)
        self.ornament_scale = (1.40, 0.05, 0.05)
        self.ornament_r_pos = (1.8, 0, -0.1)

        self.ornament_r_lng_pos = (1.8, 0, -0.1)

        """ Buttons, Label Scaling """
        self.lbl_scale = .04
        self.btn_scale = .04
        self.rad_scale = .03

        """ Misc """
        self.m_settings = MenuSettings()

        """ Language MenuUI Objects """
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

        if exists(self.configs['cfg_path']):
            with open(self.configs['cfg_path']) as json_file:
                self.json = json.load(json_file)

        self.language = None

        if self.json["game_config_path"]:
            self.cfg_path = self.json["game_config_path"]

            if exists(self.cfg_path):
                lng_to_load = self.m_settings.input_validate(self.cfg_path, 'lng')
                with open(self_configs['lg_{0}'.format(lng_to_load)], 'r') as json_file:
                    self.language = json.load(json_file)

        """ Buttons & Fonts"""
        self.menu_font = self.fonts['OpenSans-Regular']

    def load_language_menu(self):
        """ Function    : load_language_menu

            Description : Load Language menu.

            Input       : None

            Output      : None

            Return      : None
        """
        self.logo = OnscreenImage(image=self.images['lang_icon'],
                                  pos=self.logo_pos)
        self.logo.set_transparency(TransparencyAttrib.MAlpha)
        self.ornament_right = OnscreenImage(image=self.images['ornament_kz'],
                                            pos=self.ornament_r_pos, color=(63.9, 63.9, 63.9, 0.5))

        self.base.frame_int_lang = DirectFrame(frameColor=(0, 0, 0, self.frm_opacity),
                                               frameSize=self.base.frame_int_lang_size)
        self.base.frame_int_lang.setPos(self.pos_X, self.pos_Y, self.pos_Z)

        self.lbl_lang_title = DirectLabel(text=self.language['language'],
                                          text_fg=(255, 255, 255, 1),
                                          text_font=self.font.load_font(self.menu_font),
                                          frameColor=(255, 255, 255, 0),
                                          scale=.07, borderWidth=(self.w, self.h),
                                          parent=self.base.frame_int_lang)

        self.lbl_english = DirectLabel(text=self.language['english'],
                                       text_fg=(255, 255, 255, 1),
                                       text_font=self.font.load_font(self.menu_font),
                                       frameColor=(255, 255, 255, 0),
                                       scale=self.lbl_scale, borderWidth=(self.w, self.h),
                                       parent=self.base.frame_int_lang)

        self.lbl_kazakh = DirectLabel(text=self.language['kazakh'],
                                      text_fg=(255, 255, 255, 1),
                                      text_font=self.font.load_font(self.menu_font),
                                      frameColor=(255, 255, 255, 0),
                                      scale=self.lbl_scale, borderWidth=(self.w, self.h),
                                      parent=self.base.frame_int_lang)

        self.lbl_russian = DirectLabel(text=self.language['russian'],
                                       text_fg=(255, 255, 255, 1),
                                       text_font=self.font.load_font(self.menu_font),
                                       frameColor=(255, 255, 255, 0),
                                       scale=self.lbl_scale, borderWidth=(self.w, self.h),
                                       parent=self.base.frame_int_lang)

        self.btn_param_defaults = DirectButton(text="Load defaults",
                                               text_fg=(255, 255, 255, 1),
                                               text_font=self.font.load_font(self.menu_font),
                                               frameColor=(255, 255, 255, 0),
                                               scale=self.btn_scale, borderWidth=(self.w, self.h),
                                               parent=self.base.frame_int_lang,
                                               command=self.set_default_language)

        self.btn_param_back = DirectButton(text="Back",
                                           text_fg=(255, 255, 255, 1),
                                           text_font=self.font.load_font(self.menu_font),
                                           frameColor=(255, 255, 255, 0),
                                           scale=self.btn_scale, borderWidth=(self.w, self.h),
                                           parent=self.base.frame_int_lang,
                                           command=self.unload_language_menu)

        lang_values = self.get_selected_language()
        rad_btn_geom_path = 1  # non-active element

        lang_geoms_dict = {'english': rad_btn_geom_path,
                            'kazakh': rad_btn_geom_path,
                            'russian': rad_btn_geom_path}

        ui_geoms = base.ui_geom_collector()

        if (lang_values['english'] == 0
                and ui_geoms['radbtn_icon_pressed']):
            lang_geoms_dict['english'] = ui_geoms['radbtn_icon_pressed']
        elif (lang_values['english'] > 0
              and ui_geoms['radbtn_icon']):
            lang_geoms_dict['english'] = ui_geoms['radbtn_icon']

        if (lang_values['kazakh'] == 0
                and ui_geoms['radbtn_icon_pressed']):
            lang_geoms_dict['kazakh'] = ui_geoms['radbtn_icon_pressed']
        elif (lang_values['kazakh'] > 0
              and ui_geoms['radbtn_icon']):
            lang_geoms_dict['kazakh'] = ui_geoms['radbtn_icon']

        if (lang_values['russian'] == 0
                and ui_geoms['radbtn_icon_pressed']):
            lang_geoms_dict['russian'] = ui_geoms['radbtn_icon_pressed']
        elif (lang_values['russian'] > 0
              and ui_geoms['radbtn_icon']):
            lang_geoms_dict['russian'] = ui_geoms['radbtn_icon']

        radbuttons = [

            DirectRadioButton(text='', variable=[0], value=[lang_values['english']], pos=(0.6, 0, -0.0),
                              parent=self.base.frame_int_lang, scale=self.rad_scale,
                              command=self.set_language_english, color=(63.9, 63.9, 63.9, 1),
                              boxGeom=lang_geoms_dict['english']),

            DirectRadioButton(text='', variable=[0], value=[lang_values['kazakh']], pos=(0.6, 0, -0.1),
                              parent=self.base.frame_int_lang, scale=self.rad_scale,
                              command=self.set_language_kazakh, color=(63.9, 63.9, 63.9, 1),
                              boxGeom=lang_geoms_dict['kazakh']),

            DirectRadioButton(text='', variable=[0], value=[lang_values['russian']], pos=(0.6, 0, -0.2),
                              parent=self.base.frame_int_lang, scale=self.rad_scale,
                              command=self.set_language_russian, color=(63.9, 63.9, 63.9, 1),
                              boxGeomScale=3, boxGeom=lang_geoms_dict['russian'])

        ]

        for radbutton in radbuttons:
            radbutton.setOthers(radbuttons)

        """ Positioning objects of the language menu:
            for two blocks
        """
        self.logo.reparent_to(self.base.frame_int_lang)
        self.logo.set_scale(0.20, 0.20, 0.20)

        self.ornament_right.reparent_to(self.base.frame_int_lang)
        self.ornament_right.set_scale(self.ornament_scale)
        self.ornament_right.set_hpr(0.0, 0.0, -90.0)
        self.ornament_right.set_transparency(TransparencyAttrib.MAlpha)
        self.ornament_right.set_pos(self.ornament_r_lng_pos)

        self.lbl_lang_title.set_pos(0.6, 0, 0.6)

        self.lbl_english.set_pos(0.0, 0, 0)
        self.lbl_kazakh.set_pos(0.0, 0, -0.1)
        self.lbl_russian.set_pos(0.0, 0, -0.2)

        self.btn_param_defaults.set_pos(1.5, 0, -0.9)
        self.btn_param_back.set_pos(-0.6, 0, -0.9)

        self.menu_mode = True
        base.active_frame = self.base.frame_int_lang

    def unload_language_menu(self):
        """ Function    : unload_language_menu

            Description : Unload Language menu.

            Input       : None

            Output      : None

            Return      : None
        """
        if not self.base.frame_int_lang:
            return

        if hasattr(base, "active_frame"):
            base.active_frame.destroy()

        if self.game_mode:
            self.base.frame_int_lang.destroy()
        self.base.frame_int_lang.destroy()
        self.logo.destroy()
        self.ornament_right.destroy()

