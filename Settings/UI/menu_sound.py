import json
import logging

from os.path import exists
from pathlib import Path

from direct.gui.DirectGui import *
from direct.gui.OnscreenImage import OnscreenImage, TransparencyAttrib
from panda3d.core import FontPool
from panda3d.core import TextNode

from Settings.menu_settings import MenuSettings
from Settings.menu_settings import Sound


class MenuSound:
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
        self.base.frame_int_snd = None

        """ Frame Sizes """
        self.base.frame_int_snd_size = [-3, -0.2, -1, 3]

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

        self.ornament_l_snd_pos = (-1.8, 0, -0.1)
        self.ornament_r_snd_pos = (-0.3, 0, -0.1)

        """ Buttons, Label Scaling """
        self.lbl_scale = .03
        self.btn_scale = .03
        self.inp_scale = .04

        """ Misc """
        self.m_settings = MenuSettings()
        self.snd = Sound()

        """ Sound Menu Objects """
        self.lbl_snd_title = None
        self.lbl_sound = None
        self.lbl_music = None
        self.lbl_effects = None

        self.slider_sound = None
        self.slider_music = None
        self.slider_effects = None

        self.lbl_perc_sound = None
        self.lbl_perc_music = None
        self.lbl_perc_effects = None

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

    def load_sound_menu(self):
        """ Function    : load_sound_menu

            Description : Load Sound menu.

            Input       : None

            Output      : None

            Return      : None
        """
        self.logo = OnscreenImage(image='{0}/Settings/UI/ui_tex/korlan_logo_tengri.png'.format(self.game_dir),
                                  pos=self.logo_pos)
        self.ornament_left = OnscreenImage(image='{0}/Settings/UI/ui_tex/ornament_kz.png'.format(self.game_dir),
                                           pos=self.ornament_l_pos, color=(63.9, 63.9, 63.9, 0.5))
        self.ornament_right = OnscreenImage(image='{0}/Settings/UI/ui_tex/ornament_kz.png'.format(self.game_dir),
                                            pos=self.ornament_r_pos, color=(63.9, 63.9, 63.9, 0.5))

        self.base.frame_int_snd = DirectFrame(frameColor=(0, 0, 0, self.frm_opacity),
                                              frameSize=self.base.frame_int_snd_size)
        self.base.frame_int_snd.setPos(self.pos_X, self.pos_Y, self.pos_Z)

        self.lbl_snd_title = DirectLabel(text=self.language['sound'], text_bg=(0, 0, 0, 1),
                                         text_fg=(255, 255, 255, 0.9),
                                         text_font=self.font.load_font(self.menu_font),
                                         frameColor=(255, 255, 255, self.frm_opacity),
                                         scale=.05, borderWidth=(self.w, self.h),
                                         parent=self.base.frame_int_snd)

        self.lbl_sound = DirectLabel(text=self.language['sound'], text_bg=(0, 0, 0, 1),
                                     text_fg=(255, 255, 255, 0.9),
                                     text_font=self.font.load_font(self.menu_font),
                                     frameColor=(255, 255, 255, self.frm_opacity),
                                     scale=self.lbl_scale, borderWidth=(self.w, self.h),
                                     parent=self.base.frame_int_snd)

        self.lbl_music = DirectLabel(text=self.language['music'], text_bg=(0, 0, 0, 1),
                                     text_fg=(255, 255, 255, 0.9),
                                     text_font=self.font.load_font(self.menu_font),
                                     frameColor=(255, 255, 255, self.frm_opacity),
                                     scale=self.lbl_scale, borderWidth=(self.w, self.h),
                                     parent=self.base.frame_int_snd)

        self.lbl_effects = DirectLabel(text=self.language['effects'], text_bg=(0, 0, 0, 1),
                                       text_fg=(255, 255, 255, 0.9),
                                       text_font=self.font.load_font(self.menu_font),
                                       frameColor=(255, 255, 255, self.frm_opacity),
                                       scale=self.lbl_scale, borderWidth=(self.w, self.h),
                                       parent=self.base.frame_int_snd)

        self.slider_sound = DirectSlider(frameColor=self.rgba_gray_color, range=(1, 2),
                                         value=self.snd.get_sound_value(),
                                         scale=.2, borderWidth=(self.w, self.h),
                                         parent=self.base.frame_int_snd,
                                         command=self.set_slider_sound_wrapper)
        self.slider_music = DirectSlider(frameColor=self.rgba_gray_color, range=(1, 2),
                                         value=self.snd.get_music_value(),
                                         scale=.2, borderWidth=(self.w, self.h),
                                         parent=self.base.frame_int_snd,
                                         command=self.set_slider_music_wrapper)
        self.slider_effects = DirectSlider(frameColor=self.rgba_gray_color, range=(1, 2),
                                           value=self.snd.get_sfx_value(),
                                           scale=.2, borderWidth=(self.w, self.h),
                                           parent=self.base.frame_int_snd,
                                           command=self.set_slider_sfx_wrapper)

        self.lbl_perc_sound = OnscreenText(bg=(0, 0, 0, 1), fg=(255, 255, 255, 0.9),
                                           font=self.font.load_font(self.menu_font),
                                           scale=self.lbl_scale,
                                           parent=self.base.frame_int_snd, mayChange=True)

        self.lbl_perc_music = OnscreenText(bg=(0, 0, 0, 1), fg=(255, 255, 255, 0.9),
                                           font=self.font.load_font(self.menu_font),
                                           scale=self.lbl_scale,
                                           parent=self.base.frame_int_snd, mayChange=True)

        self.lbl_perc_effects = OnscreenText(bg=(0, 0, 0, 1), fg=(255, 255, 255, 0.9),
                                             font=self.font.load_font(self.menu_font),
                                             scale=self.lbl_scale,
                                             parent=self.base.frame_int_snd, mayChange=True)

        self.btn_param_defaults = DirectButton(text="Load defaults", text_bg=(0, 0, 0, 1),
                                               text_fg=(255, 255, 255, 0.9),
                                               text_font=self.font.load_font(self.menu_font),
                                               frameColor=(255, 255, 255, self.frm_opacity),
                                               scale=self.btn_scale, borderWidth=(self.w, self.h),
                                               parent=self.base.frame_int_snd,
                                               command=self.snd.set_default_snd)

        self.btn_param_accept = DirectButton(text="OK", text_bg=(0, 0, 0, 0.9),
                                             text_fg=(255, 255, 255, 0.9),
                                             text_font=self.font.load_font(self.menu_font),
                                             frameColor=(255, 255, 255, self.frm_opacity),
                                             scale=self.btn_scale, borderWidth=(self.w, self.h),
                                             parent=self.base.frame_int_snd,
                                             command=self.unload_sound_menu)

        self.logo.reparent_to(self.base.frame_int_snd)
        self.logo.set_scale(self.logo_scale)

        self.ornament_right.reparent_to(self.base.frame_int_snd)
        self.ornament_right.set_scale(self.ornament_scale)
        self.ornament_right.set_hpr(0.0, 0.0, -90.0)
        self.ornament_left.reparent_to(self.base.frame_int_snd)
        self.ornament_left.set_scale(self.ornament_scale)
        self.ornament_left.set_hpr(0.0, 0.0, -90.0)
        self.ornament_right.set_transparency(TransparencyAttrib.MAlpha)
        self.ornament_left.set_transparency(TransparencyAttrib.MAlpha)

        self.ornament_left.set_pos(self.ornament_l_snd_pos)
        self.ornament_right.set_pos(self.ornament_r_snd_pos)

        self.lbl_snd_title.set_pos(-0.6, 0, 0.5)
        self.lbl_sound.set_pos(-1.4, 0, 0)
        self.lbl_music.set_pos(-1.4, 0, -0.1)
        self.lbl_effects.set_pos(-1.4, 0, -0.2)

        self.slider_sound.set_pos(-0.8, 0, 0)
        self.slider_music.set_pos(-0.8, 0, -0.1)
        self.slider_effects.set_pos(-0.8, 0, -0.2)

        self.lbl_perc_sound.set_pos(-0.5, 0, 0)
        self.lbl_perc_music.set_pos(-0.5, 0, -0.1)
        self.lbl_perc_effects.set_pos(-0.5, 0, -0.2)

        self.btn_param_defaults.set_pos(-0.7, 0, -0.9)
        self.btn_param_accept.set_pos(-1.6, 0, -0.9)
        self.menu_mode = True

    def unload_sound_menu(self):
        """ Function    : unload_sound_menu

            Description : Unload Sound menu.

            Input       : None

            Output      : None

            Return      : None
        """
        if self.game_mode:
            self.base.frame_int_snd.destroy()
        self.base.frame_int_snd.destroy()
        self.logo.destroy()
        self.ornament_left.destroy()
        self.ornament_right.destroy()

    """ Wrapper functions """
    """ Direct* object doesn't allow passing it's instance directly before it created.
        So, we pass it through wrapper methods
    """

    def set_slider_sound_wrapper(self):
        """ Function    : set_slider_sound_wrapper

            Description : Wrapper function.

            Input       : None

            Output      : None

            Return      : None
        """
        # Make it int and then str
        i = int(self.slider_sound['value'])
        sound_dict = self.snd.load_sound_value()
        string = sound_dict[i]
        self.lbl_perc_sound.setText(string)
        self.snd.save_sound_value(string)

    def set_slider_music_wrapper(self):
        """ Function    : set_slider_music_wrapper

            Description : Wrapper function.

            Input       : None

            Output      : None

            Return      : None
        """
        # Make it int and then str
        i = int(self.slider_music['value'])
        music_dict = self.snd.load_music_value()
        string = music_dict[i]
        self.lbl_perc_music.setText(string)
        self.snd.save_music_value(string)

    def set_slider_sfx_wrapper(self):
        """ Function    : set_slider_sfx_wrapper

            Description : Wrapper function.

            Input       : None

            Output      : None

            Return      : None
        """
        # Make it int and then str
        i = int(self.slider_effects['value'])
        sfx_dict = self.snd.load_sfx_value()
        string = sfx_dict[i]
        self.lbl_perc_effects.setText(string)
        self.snd.save_sfx_value(string)

