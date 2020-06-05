import json
import logging

from os.path import exists
from pathlib import Path

from direct.gui.DirectGui import *
from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.OnscreenImage import TransparencyAttrib
from panda3d.core import FontPool
from panda3d.core import TextNode

from Settings.menu_settings import MenuSettings
from Settings.game_menu_settings import Game


class GameMenuUI(Game):
    def __init__(self):
        Game.__init__(self)
        self.base = base
        self.game_dir = base.game_dir
        self.images = base.textures_collector(path="{0}/Settings/UI".format(self.game_dir))
        self.fonts = base.fonts_collector()
        self.configs = base.cfg_collector(path="{0}/Settings/UI".format(self.game_dir))
        self.lng_configs = base.cfg_collector(path="{0}/Configs/Language/".format(self.game_dir))
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
        self.base.frame_int_game = None

        """ Frame Sizes """
        # Left, right, bottom, top
        self.base.frame_int_game_size = [-3, 0.7, -1, 3]

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
        self.ornament_r_pos = (-0.2, 0, -0.1)

        self.ornament_l_game_pos = (-1.8, 0, -0.1)
        self.ornament_r_game_pos = (0.6, 0.2, -0.1)

        """ Buttons, Label Scaling """
        self.lbl_scale = .03
        self.btn_scale = .03
        self.inp_scale = .04

        """ Misc """
        self.m_settings = MenuSettings()

        """ Sound MenuUI Objects """
        self.lbl_game_title = None
        self.lbl_person_look_mode = None
        self.lbl_gameplay_mode = None
        self.lbl_show_blood = None

        self.slider_person_look_mode = None
        self.slider_gameplay_mode = None
        self.slider_show_blood = None

        self.lbl_perc_person_look_mode = None
        self.lbl_perc_gameplay_mode = None
        self.lbl_perc_show_blood = None

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
                with open(self.lng_configs['lg_{0}'.format(lng_to_load)], 'r') as json_file:
                    self.language = json.load(json_file)

        """ Buttons & Fonts"""
        self.menu_font = self.fonts['OpenSans-Regular']

    def load_game_menu(self):
        """ Function    : load_sound_menu

            Description : Load Sound menu.

            Input       : None

            Output      : None

            Return      : None
        """
        self.logo = OnscreenImage(image=self.images['korlan_logo_tengri'],
                                  pos=self.logo_pos)
        self.ornament_left = OnscreenImage(image=self.images['ornament_kz'],
                                           pos=self.ornament_l_pos, color=(63.9, 63.9, 63.9, 0.5))
        self.ornament_right = OnscreenImage(image=self.images['ornament_kz'],
                                            pos=self.ornament_r_pos, color=(63.9, 63.9, 63.9, 0.5))

        self.base.frame_int_game = DirectFrame(frameColor=(0, 0, 0, self.frm_opacity),
                                               frameSize=self.base.frame_int_game_size)
        self.base.frame_int_game.setPos(self.pos_X, self.pos_Y, self.pos_Z)

        self.lbl_game_title = DirectLabel(text=self.language['game'], text_bg=(0, 0, 0, 1),
                                          text_fg=(255, 255, 255, 0.9),
                                          text_font=self.font.load_font(self.menu_font),
                                          frameColor=(255, 255, 255, self.frm_opacity),
                                          scale=.05, borderWidth=(self.w, self.h),
                                          parent=self.base.frame_int_game)

        self.lbl_person_look_mode = DirectLabel(text=self.language['person_look_mode'], text_bg=(0, 0, 0, 1),
                                                text_fg=(255, 255, 255, 0.9),
                                                text_font=self.font.load_font(self.menu_font),
                                                frameColor=(255, 255, 255, self.frm_opacity),
                                                scale=self.lbl_scale, borderWidth=(self.w, self.h),
                                                parent=self.base.frame_int_game)

        self.lbl_gameplay_mode = DirectLabel(text=self.language['gameplay_mode'], text_bg=(0, 0, 0, 1),
                                             text_fg=(255, 255, 255, 0.9),
                                             text_font=self.font.load_font(self.menu_font),
                                             frameColor=(255, 255, 255, self.frm_opacity),
                                             scale=self.lbl_scale, borderWidth=(self.w, self.h),
                                             parent=self.base.frame_int_game)

        self.lbl_show_blood = DirectLabel(text=self.language['show_blood'], text_bg=(0, 0, 0, 1),
                                          text_fg=(255, 255, 255, 0.9),
                                          text_font=self.font.load_font(self.menu_font),
                                          frameColor=(255, 255, 255, self.frm_opacity),
                                          scale=self.lbl_scale, borderWidth=(self.w, self.h),
                                          parent=self.base.frame_int_game)

        self.slider_person_look_mode = DirectSlider(frameColor=self.rgba_gray_color, range=(1, 2),
                                                    value=self.get_person_look_mode_value(),
                                                    scale=.2, borderWidth=(self.w, self.h),
                                                    parent=self.base.frame_int_game,
                                                    command=self.set_slider_person_look_mode_wrapper)
        self.slider_gameplay_mode = DirectSlider(frameColor=self.rgba_gray_color, range=(1, 2),
                                                 value=self.get_gameplay_mode_value(),
                                                 scale=.2, borderWidth=(self.w, self.h),
                                                 parent=self.base.frame_int_game,
                                                 command=self.set_slider_gameplay_mode_wrapper)
        self.slider_show_blood = DirectSlider(frameColor=self.rgba_gray_color, range=(1, 2),
                                              value=self.get_show_blood_value(),
                                              scale=.2, borderWidth=(self.w, self.h),
                                              parent=self.base.frame_int_game,
                                              command=self.set_slider_show_blood_wrapper)

        self.lbl_perc_person_look_mode = OnscreenText(bg=(0, 0, 0, 1), fg=(255, 255, 255, 0.9),
                                                      font=self.font.load_font(self.menu_font),
                                                      scale=self.lbl_scale,
                                                      parent=self.base.frame_int_game, mayChange=True)

        self.lbl_perc_gameplay_mode = OnscreenText(bg=(0, 0, 0, 1), fg=(255, 255, 255, 0.9),
                                                   font=self.font.load_font(self.menu_font),
                                                   scale=self.lbl_scale,
                                                   parent=self.base.frame_int_game, mayChange=True)

        self.lbl_perc_show_blood = OnscreenText(bg=(0, 0, 0, 1), fg=(255, 255, 255, 0.9),
                                                font=self.font.load_font(self.menu_font),
                                                scale=self.lbl_scale,
                                                parent=self.base.frame_int_game, mayChange=True)

        self.btn_param_defaults = DirectButton(text="Load defaults", text_bg=(0, 0, 0, 1),
                                               text_fg=(255, 255, 255, 0.9),
                                               text_font=self.font.load_font(self.menu_font),
                                               frameColor=(255, 255, 255, self.frm_opacity),
                                               scale=self.btn_scale, borderWidth=(self.w, self.h),
                                               parent=self.base.frame_int_game,
                                               command=self.set_default_game)

        self.btn_param_accept = DirectButton(text="OK", text_bg=(0, 0, 0, 0.9),
                                             text_fg=(255, 255, 255, 0.9),
                                             text_font=self.font.load_font(self.menu_font),
                                             frameColor=(255, 255, 255, self.frm_opacity),
                                             scale=self.btn_scale, borderWidth=(self.w, self.h),
                                             parent=self.base.frame_int_game,
                                             command=self.unload_game_menu)

        self.logo.reparent_to(self.base.frame_int_game)
        self.logo.set_scale(self.logo_scale)

        self.ornament_right.reparent_to(self.base.frame_int_game)
        self.ornament_right.set_scale(self.ornament_scale)
        self.ornament_right.set_hpr(0.0, 0.0, -90.0)
        self.ornament_left.reparent_to(self.base.frame_int_game)
        self.ornament_left.set_scale(self.ornament_scale)
        self.ornament_left.set_hpr(0.0, 0.0, -90.0)
        self.ornament_right.set_transparency(TransparencyAttrib.MAlpha)
        self.ornament_left.set_transparency(TransparencyAttrib.MAlpha)

        self.ornament_left.set_pos(self.ornament_l_game_pos)
        self.ornament_right.set_pos(self.ornament_r_game_pos)

        self.lbl_game_title.set_pos(-0.6, 0, 0.5)
        self.lbl_person_look_mode.set_pos(-1.4, 0, 0)
        self.lbl_gameplay_mode.set_pos(-1.4, 0, -0.1)
        self.lbl_show_blood.set_pos(-1.4, 0, -0.2)

        self.slider_person_look_mode.set_pos(-0.8, 0, 0)
        self.slider_gameplay_mode.set_pos(-0.8, 0, -0.1)
        self.slider_show_blood.set_pos(-0.8, 0, -0.2)

        self.lbl_perc_person_look_mode.set_pos(-0.5, 0, 0)
        self.lbl_perc_gameplay_mode.set_pos(-0.5, 0, -0.1)
        self.lbl_perc_show_blood.set_pos(-0.5, 0, -0.2)

        self.btn_param_defaults.set_pos(0.3, 0, -0.9)
        self.btn_param_accept.set_pos(-1.6, 0, -0.9)
        self.menu_mode = True

    def unload_game_menu(self):
        """ Function    : unload_sound_menu

            Description : Unload Sound menu.

            Input       : None

            Output      : None

            Return      : None
        """
        if self.game_mode:
            self.base.frame_int_game.destroy()
        self.base.frame_int_game.destroy()
        self.logo.destroy()
        self.ornament_left.destroy()
        self.ornament_right.destroy()

    """ Wrapper functions """
    """ Direct* object doesn't allow passing it's instance directly before it created.
        So, we pass it through wrapper methods
    """

    def set_slider_person_look_mode_wrapper(self):
        """ Function    : set_slider_person_look_mode_wrapper

            Description : Wrapper function.

            Input       : None

            Output      : None

            Return      : None
        """
        # Make it int and then str
        i = int(self.slider_person_look_mode['value'])
        person_look_mode_dict = self.load_person_look_mode_value()
        string = person_look_mode_dict[i]
        self.lbl_perc_person_look_mode.setText(string)
        self.save_person_look_mode_value(string)

    def set_slider_gameplay_mode_wrapper(self):
        """ Function    : set_slider_gameplay_mode_wrapper

            Description : Wrapper function.

            Input       : None

            Output      : None

            Return      : None
        """
        # Make it int and then str
        i = int(self.slider_gameplay_mode['value'])
        gameplay_mode_dict = self.load_gameplay_mode_value()
        string = gameplay_mode_dict[i]
        self.lbl_perc_gameplay_mode.setText(string)
        self.save_gameplay_mode_value(string)

    def set_slider_show_blood_wrapper(self):
        """ Function    : set_slider_show_blood_wrapper

            Description : Wrapper function.

            Input       : None

            Output      : None

            Return      : None
        """
        # Make it int and then str
        i = int(self.slider_show_blood['value'])
        show_blood_dict = self.load_show_blood_value()
        string = show_blood_dict[i]
        self.lbl_perc_show_blood.setText(string)
        self.save_show_blood_value(string)
