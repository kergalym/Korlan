import json
import sys
import logging

from os.path import exists
from pathlib import Path

from direct.gui.DirectGui import *
from direct.gui.OnscreenImage import OnscreenImage, TransparencyAttrib
from panda3d.core import FontPool
from panda3d.core import TextNode

from Engine.Scenes.playworker import PlayWorker
from Settings.menu_settings import MenuSettings, DevMode, Graphics, Sound, Keymap, Language

from Engine.Scenes.level_one import LevelOne


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
        self.base.frame_int = None
        self.base.frame_int_dev = None
        self.base.frame_int_gfx = None
        self.base.frame_int_snd = None
        self.base.frame_int_keymap = None
        self.base.frame_int_lang = None

        """ Frame Sizes """
        self.base.frame_size = [-3, -0.9, -1, 3]
        self.base.frame_int_size = [-3, -0.9, -1, 3]
        self.base.frame_int_dev_size = [-3, -0.2, -1, 3]
        self.base.frame_int_gfx_size = [-3, -0.2, -1, 3]
        self.base.frame_int_snd_size = [-3, -0.2, -1, 3]
        self.base.frame_int_keymap_size = [-3, -0.1, -1, 3]
        self.base.frame_int_lang_size = [-3, -0.3, -1, 3]

        """ Frame Colors """
        self.frm_opacity = 1

        """ Logo & Ornament Scaling, Positioning """
        self.logo_scale = (0.33, 0.30, 0.30)
        self.logo_pos = (-1.4, 0, 0.4)
        self.ornament_scale = (1.40, 0.05, 0.05)
        self.ornament_l_pos = (-1.8, 0, -0.1)
        self.ornament_r_pos = (-1.0, 0, -0.1)

        self.ornament_l_gfx_pos = (-1.8, 0, -0.1)
        self.ornament_r_gfx_pos = (-0.3, 0, -0.1)

        self.ornament_l_snd_pos = (-1.8, 0, -0.1)
        self.ornament_r_snd_pos = (-0.3, 0, -0.1)

        self.ornament_l_lng_pos = (-1.8, 0, -0.1)
        self.ornament_r_lng_pos = (-0.4, 0, -0.1)

        self.ornament_l_kmp_pos = (-1.8, 0, -0.1)
        self.ornament_r_kmp_pos = (-0.2, 0, -0.1)

        self.ornament_l_dev_pos = (-1.8, 0, -0.1)
        self.ornament_r_dev_pos = (-0.3, 0, -0.1)

        """ Buttons, Label Scaling """
        self.lbl_scale = .03
        self.btn_scale = .03
        self.inp_scale = .04

        """ Graphics Menu Objects """
        self.lbl_gfx_title = None
        self.btn_gfx = None
        self.btn_sound = None
        self.btn_language = None
        self.btn_keymap = None

        self.lbl_disp_res = None
        self.lbl_details = None
        self.lbl_shadows = None
        self.lbl_postprocessing = None
        self.lbl_antialiasing = None

        self.lbl_perc_disp_res = None
        self.lbl_perc_details = None
        self.lbl_perc_shadows = None
        self.lbl_perc_postpro = None
        self.lbl_perc_antial = None

        self.btn_param_accept = None
        self.btn_param_back = None
        self.btn_param_decline = None
        self.btn_param_defaults = None

        self.slider_disp_res = None
        self.slider_details = None
        self.slider_shadows = None
        self.slider_postpro = None
        self.slider_antial = None

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

        """ Key mapping Menu Objects """
        self.lbl_keymap_title = None
        self.lbl_forward = None
        self.lbl_backward = None
        self.lbl_left = None
        self.lbl_right = None
        self.lbl_crouch = None
        self.lbl_jump = None
        self.lbl_use = None
        self.lbl_attack = None
        self.lbl_h_attack = None
        self.lbl_f_attack = None
        self.lbl_block = None
        self.lbl_sword = None
        self.lbl_bow = None
        self.lbl_tengri = None
        self.lbl_umay = None

        self.inp_forward = None
        self.inp_backward = None
        self.inp_left = None
        self.inp_right = None
        self.inp_crouch = None
        self.inp_jump = None
        self.inp_use = None
        self.inp_attack = None
        self.inp_h_attack = None
        self.inp_f_attack = None
        self.inp_block = None
        self.inp_sword = None
        self.inp_bow = None
        self.inp_tengri = None
        self.inp_umay = None

        """ Language Menu Objects """
        self.lbl_lang_title = None
        self.lbl_english = None
        self.lbl_kazakh = None
        self.lbl_russian = None

        self.rad_english = None
        self.rad_kazakh = None
        self.rad_russian = None

        """ Developer Mode Menu Objects """
        self.lbl_dev_mode_title = None
        self.lbl_dev_mode_title_low = None
        self.lbl_pos_x = None
        self.lbl_pos_y = None
        self.lbl_pos_z = None
        self.lbl_rot_h = None
        self.lbl_rot_p = None
        self.lbl_rot_r = None

        self.inp_pos_x = None
        self.inp_pos_y = None
        self.inp_pos_z = None
        self.inp_rot_h = None
        self.inp_rot_p = None
        self.inp_rot_r = None
        self.node_frame = None
        self.lbl_node_exp = None
        self.lbl_perc_node_exp = None
        self.slider_node_exp = None

        self.btn_back_options = None
        self.btn_save_changes = None

        """ Misc """
        self.playworker = PlayWorker()
        self.m_settings = MenuSettings()
        self.dev_mode = DevMode()
        self.gfx = Graphics()
        self.snd = Sound()
        self.kmp = Keymap()
        self.lng = Language()

        # instance of the abstract class
        self.font = FontPool
        self.text = TextNode("TextNode")

        self.logging = logging
        self.logging.basicConfig(filename="{}/critical.log".format(Path.home()), level=logging.CRITICAL)

        self.base.frame = DirectFrame(frameColor=(0, 0, 0, self.frm_opacity),
                                      frameSize=self.base.frame_size)

        self.logo = OnscreenImage(image='Settings/UI/ui_tex/korlan_logo_tengri.png', pos=self.logo_pos)
        self.ornament_left = OnscreenImage(image='Settings/UI/ui_tex/ornament_kz.png',
                                           pos=self.ornament_l_pos, color=(63.9, 63.9, 63.9, 0.5))
        self.ornament_right = OnscreenImage(image='Settings/UI/ui_tex/ornament_kz.png',
                                            pos=self.ornament_r_pos, color=(63.9, 63.9, 63.9, 0.5))

        self.menu_font = None

        self.cfg_path = None

        if exists('Settings/UI/cfg_path.json'):
            with open('Settings/UI/cfg_path.json') as json_file:
                self.json = json.load(json_file)

        self.language = None

        if self.json["game_config_path"]:
            self.cfg_path = self.json["game_config_path"]

            if exists(self.cfg_path):
                lng_to_load = self.m_settings.input_validate(self.cfg_path, 'lng')
                with open('Configs/Language/lg_{}.json'.format(lng_to_load), 'r') as json_file:
                    self.language = json.load(json_file)

        """ Buttons & Fonts"""
        # self.menu_font = 'Settings/UI/Open_Sans/OpenSans-Regular.ttf'
        self.menu_font = '{0}/Settings/UI/JetBrainsMono-1.0.2/ttf/JetBrainsMono-Regular.ttf'.format(self.game_dir)

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
                                        command=self.load_options_menu)

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
                                         command=self.load_dev_mode_menu)

        self.btn_exit = DirectButton(text=self.language['exit'], text_bg=(0, 0, 0, 1),
                                     text_fg=(255, 255, 255, 0.9),
                                     text_font=self.font.load_font(self.menu_font),
                                     frameColor=(255, 255, 255, self.frm_opacity),
                                     scale=self.btn_scale, borderWidth=(self.w, self.h),
                                     parent=self.base.frame,
                                     command=sys.exit)

    def load_main_menu(self):
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

    def load_options_menu(self):
        self.base.frame_int = DirectFrame(frameColor=(0, 0, 0, self.frm_opacity),
                                          frameSize=self.base.frame_int_size)
        self.base.frame_int.setPos(self.pos_X, self.pos_Y, self.pos_Z)

        self.btn_gfx = DirectButton(text=self.language['graphics'], text_bg=(0, 0, 0, 1),
                                    text_fg=(255, 255, 255, 0.9),
                                    text_font=self.font.load_font(self.menu_font),
                                    frameColor=(255, 255, 255, self.frm_opacity),
                                    scale=self.btn_scale, borderWidth=(self.w, self.h),
                                    parent=self.base.frame_int,
                                    command=self.load_graphics_menu)

        self.btn_sound = DirectButton(text=self.language['sound'], text_bg=(0, 0, 0, 1),
                                      text_fg=(255, 255, 255, 0.9),
                                      text_font=self.font.load_font(self.menu_font),
                                      frameColor=(255, 255, 255, self.frm_opacity),
                                      scale=self.btn_scale, borderWidth=(self.w, self.h),
                                      parent=self.base.frame_int,
                                      command=self.load_sound_menu)

        self.btn_language = DirectButton(text=self.language['language'], text_bg=(0, 0, 0, 1),
                                         text_fg=(255, 255, 255, 0.9),
                                         text_font=self.font.load_font(self.menu_font),
                                         frameColor=(255, 255, 255, self.frm_opacity),
                                         scale=self.btn_scale, borderWidth=(self.w, self.h),
                                         parent=self.base.frame_int,
                                         command=self.load_language_menu)

        self.btn_keymap = DirectButton(text=self.language['keymap'], text_bg=(0, 0, 0, 1),
                                       text_fg=(255, 255, 255, 0.9),
                                       text_font=self.font.load_font(self.menu_font),
                                       frameColor=(255, 255, 255, self.frm_opacity),
                                       scale=self.btn_scale, borderWidth=(self.w, self.h),
                                       parent=self.base.frame_int,
                                       command=self.load_keymap_menu)

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

    def load_graphics_menu(self):
        self.base.frame_int_gfx = DirectFrame(frameColor=(0, 0, 0, self.frm_opacity),
                                              frameSize=self.base.frame_int_gfx_size)
        self.base.frame_int_gfx.setPos(self.pos_X, self.pos_Y, self.pos_Z)

        self.lbl_gfx_title = DirectLabel(text=self.language['graphics'], text_bg=(0, 0, 0, 1),
                                         text_fg=(255, 255, 255, 0.9),
                                         text_font=self.font.load_font(self.menu_font),
                                         frameColor=(255, 255, 255, self.frm_opacity),
                                         scale=.05, borderWidth=(self.w, self.h),
                                         parent=self.base.frame_int_gfx)

        self.lbl_disp_res = DirectLabel(text=self.language['disp_res'], text_bg=(0, 0, 0, 1),
                                        text_fg=(255, 255, 255, 0.9),
                                        text_font=self.font.load_font(self.menu_font),
                                        frameColor=(255, 255, 255, self.frm_opacity),
                                        scale=self.lbl_scale, borderWidth=(self.w, self.h),
                                        parent=self.base.frame_int_gfx)

        self.lbl_details = DirectLabel(text=self.language['details'], text_bg=(0, 0, 0, 1),
                                       text_fg=(255, 255, 255, 0.9),
                                       text_font=self.font.load_font(self.menu_font),
                                       frameColor=(255, 255, 255, self.frm_opacity),
                                       scale=self.lbl_scale, borderWidth=(self.w, self.h),
                                       parent=self.base.frame_int_gfx)

        self.lbl_shadows = DirectLabel(text=self.language['shadows'], text_bg=(0, 0, 0, 1),
                                       text_fg=(255, 255, 255, 0.9),
                                       text_font=self.font.load_font(self.menu_font),
                                       frameColor=(255, 255, 255, self.frm_opacity),
                                       scale=self.lbl_scale, borderWidth=(self.w, self.h),
                                       parent=self.base.frame_int_gfx)

        self.lbl_postprocessing = DirectLabel(text=self.language['postprocessing'], text_bg=(0, 0, 0, 1),
                                              text_fg=(255, 255, 255, 0.9),
                                              text_font=self.font.load_font(self.menu_font),
                                              frameColor=(255, 255, 255, self.frm_opacity),
                                              scale=self.lbl_scale, borderWidth=(self.w, self.h),
                                              parent=self.base.frame_int_gfx)

        self.lbl_antialiasing = DirectLabel(text=self.language['antialiasing'], text_bg=(0, 0, 0, 1),
                                            text_fg=(255, 255, 255, 0.9),
                                            text_font=self.font.load_font(self.menu_font),
                                            frameColor=(255, 255, 255, self.frm_opacity),
                                            scale=self.lbl_scale, borderWidth=(self.w, self.h),
                                            parent=self.base.frame_int_gfx)

        self.slider_disp_res = DirectSlider(frameColor=self.rgba_gray_color,
                                            range=(1, self.gfx.load_disp_res_value()),
                                            value=self.gfx.disp_res_value(),
                                            scale=.2, borderWidth=(self.w, self.h),
                                            parent=self.base.frame_int_gfx,
                                            orientation=DGG.HORIZONTAL,
                                            command=self.set_slider_disp_res_wrapper)

        self.slider_details = DirectSlider(frameColor=self.rgba_gray_color,
                                           range=(1, 100), value=50,
                                           scale=.2, borderWidth=(self.w, self.h),
                                           parent=self.base.frame_int_gfx,
                                           orientation=DGG.HORIZONTAL,
                                           command=self.set_slider_details_wrapper)

        self.slider_shadows = DirectSlider(frameColor=self.rgba_gray_color, range=(1, 2),
                                           value=self.gfx.shadows_value(),
                                           scale=.2, borderWidth=(self.w, self.h),
                                           parent=self.base.frame_int_gfx,
                                           orientation=DGG.HORIZONTAL,
                                           command=self.set_slider_shadows_wrapper)

        self.slider_postpro = DirectSlider(frameColor=self.rgba_gray_color, range=(1, 2),
                                           value=self.gfx.postpro_value(),
                                           scale=.2, borderWidth=(self.w, self.h),
                                           parent=self.base.frame_int_gfx,
                                           orientation=DGG.HORIZONTAL,
                                           command=self.set_slider_postpro_wrapper)

        self.slider_antial = DirectSlider(frameColor=self.rgba_gray_color, range=(1, 2),
                                          value=self.gfx.antial_value(),
                                          scale=.2, borderWidth=(self.w, self.h),
                                          parent=self.base.frame_int_gfx,
                                          orientation=DGG.HORIZONTAL,
                                          command=self.set_slider_antial_wrapper)

        self.lbl_perc_disp_res = OnscreenText(bg=(0, 0, 0, 1), fg=(255, 255, 255, 0.9),
                                              font=self.font.load_font(self.menu_font),
                                              scale=self.lbl_scale,
                                              parent=self.base.frame_int_gfx, mayChange=True)

        self.lbl_perc_details = OnscreenText(bg=(0, 0, 0, 1), fg=(255, 255, 255, 0.9),
                                             font=self.font.load_font(self.menu_font),
                                             scale=self.lbl_scale,
                                             parent=self.base.frame_int_gfx, mayChange=True)

        self.lbl_perc_shadows = OnscreenText(bg=(0, 0, 0, 1), fg=(255, 255, 255, 0.9),
                                             font=self.font.load_font(self.menu_font),
                                             scale=self.lbl_scale,
                                             parent=self.base.frame_int_gfx, mayChange=True)

        self.lbl_perc_postpro = OnscreenText(bg=(0, 0, 0, 1), fg=(255, 255, 255, 0.9),
                                             font=self.font.load_font(self.menu_font),
                                             scale=self.lbl_scale,
                                             parent=self.base.frame_int_gfx, mayChange=True)

        self.lbl_perc_antial = OnscreenText(bg=(0, 0, 0, 1), fg=(255, 255, 255, 0.9),
                                            font=self.font.load_font(self.menu_font),
                                            scale=self.lbl_scale,
                                            parent=self.base.frame_int_gfx, mayChange=True)

        self.btn_param_defaults = DirectButton(text="Load defaults", text_bg=(0, 0, 0, 1),
                                               text_fg=(255, 255, 255, 0.9),
                                               text_font=self.font.load_font(self.menu_font),
                                               frameColor=(255, 255, 255, self.frm_opacity),
                                               scale=self.btn_scale, borderWidth=(self.w, self.h),
                                               parent=self.base.frame_int_gfx,
                                               command=self.gfx.set_default_gfx)

        self.btn_param_accept = DirectButton(text="OK", text_bg=(0, 0, 0, 1),
                                             text_fg=(255, 255, 255, 0.9),
                                             text_font=self.font.load_font(self.menu_font),
                                             frameColor=(255, 255, 255, self.frm_opacity),
                                             scale=self.btn_scale, borderWidth=(self.w, self.h),
                                             parent=self.base.frame_int_gfx,
                                             command=self.gfx_menu_unload)

        self.logo.reparent_to(self.base.frame_int_gfx)
        self.logo.set_scale(self.logo_scale)

        self.ornament_right.reparent_to(self.base.frame_int_gfx)
        self.ornament_right.set_scale(self.ornament_scale)
        self.ornament_right.set_hpr(0.0, 0.0, -90.0)

        self.ornament_left.set_pos(self.ornament_l_gfx_pos)
        self.ornament_right.set_pos(self.ornament_r_gfx_pos)

        self.ornament_left.reparent_to(self.base.frame_int_gfx)
        self.ornament_left.set_scale(self.ornament_scale)
        self.ornament_left.set_hpr(0.0, 0.0, -90.0)
        self.ornament_right.set_transparency(TransparencyAttrib.MAlpha)
        self.ornament_left.set_transparency(TransparencyAttrib.MAlpha)

        self.lbl_gfx_title.set_pos(-0.6, 0, 0.5)

        self.lbl_disp_res.set_pos(-1.4, 0, 0)
        self.lbl_details.set_pos(-1.4, 0, -0.1)
        self.lbl_shadows.set_pos(-1.4, 0, -0.2)
        self.lbl_postprocessing.set_pos(-1.4, 0, -0.3)
        self.lbl_antialiasing.set_pos(-1.4, 0, -0.4)

        self.slider_disp_res.set_pos(-0.8, 0, 0)
        self.slider_details.set_pos(-0.8, 0, -0.1)
        self.slider_shadows.set_pos(-0.8, 0, -0.2)
        self.slider_postpro.set_pos(-0.8, 0, -0.3)
        self.slider_antial.set_pos(-0.8, 0, -0.4)

        self.lbl_perc_disp_res.set_pos(-0.5, 0, 0)
        self.lbl_perc_details.set_pos(-0.5, 0, -0.1)
        self.lbl_perc_shadows.set_pos(-0.5, 0, -0.2)
        self.lbl_perc_postpro.set_pos(-0.5, 0, -0.3)
        self.lbl_perc_antial.set_pos(-0.5, 0, -0.4)

        self.btn_param_defaults.set_pos(-0.6, 0, -0.9)
        self.btn_param_accept.set_pos(-1.6, 0, -0.9)

        self.menu_mode = True

    def load_sound_menu(self):
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
                                         value=self.snd.sound_value(),
                                         scale=.2, borderWidth=(self.w, self.h),
                                         parent=self.base.frame_int_snd,
                                         command=self.set_slider_sound_wrapper)
        self.slider_music = DirectSlider(frameColor=self.rgba_gray_color, range=(1, 2),
                                         value=self.snd.music_value(),
                                         scale=.2, borderWidth=(self.w, self.h),
                                         parent=self.base.frame_int_snd,
                                         command=self.set_slider_music_wrapper)
        self.slider_effects = DirectSlider(frameColor=self.rgba_gray_color, range=(1, 2),
                                           value=self.snd.sfx_value(),
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
                                             command=self.sound_menu_unload)

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

    def load_keymap_menu(self):
        self.base.frame_int_keymap = DirectFrame(frameColor=(0, 0, 0, self.frm_opacity),
                                                 frameSize=self.base.frame_int_keymap_size)
        self.base.frame_int_keymap.setPos(self.pos_X, self.pos_Y, self.pos_Z)

        self.lbl_keymap_title = DirectLabel(text=self.language['keymap'], text_bg=(0, 0, 0, 1),
                                            text_fg=(155, 155, 255, 0.9),
                                            text_font=self.font.load_font(self.menu_font),
                                            scale=.05, borderWidth=(self.w, self.h),
                                            frameColor=(255, 255, 255, self.frm_opacity),
                                            parent=self.base.frame_int_keymap)

        self.lbl_forward = DirectLabel(text=self.language['forward'], text_bg=(0, 0, 0, 1),
                                       text_fg=(255, 255, 255, 0.9),
                                       text_font=self.font.load_font(self.menu_font),
                                       frameColor=(255, 255, 255, self.frm_opacity),
                                       scale=self.lbl_scale, borderWidth=(self.w, self.h),
                                       parent=self.base.frame_int_keymap)

        self.lbl_backward = DirectLabel(text=self.language['backward'], text_bg=(0, 0, 0, 1),
                                        text_fg=(255, 255, 255, 0.9),
                                        text_font=self.font.load_font(self.menu_font),
                                        frameColor=(255, 255, 255, self.frm_opacity),
                                        scale=self.lbl_scale, borderWidth=(self.w, self.h),
                                        parent=self.base.frame_int_keymap)

        self.lbl_left = DirectLabel(text=self.language['left'], text_bg=(0, 0, 0, 1),
                                    text_fg=(255, 255, 255, 0.9),
                                    text_font=self.font.load_font(self.menu_font),
                                    frameColor=(255, 255, 255, self.frm_opacity),
                                    scale=self.lbl_scale, borderWidth=(self.w, self.h),
                                    parent=self.base.frame_int_keymap)

        self.lbl_right = DirectLabel(text=self.language['right'], text_bg=(0, 0, 0, 1),
                                     text_fg=(255, 255, 255, 0.9),
                                     text_font=self.font.load_font(self.menu_font),
                                     frameColor=(255, 255, 255, self.frm_opacity),
                                     scale=self.lbl_scale, borderWidth=(self.w, self.h),
                                     parent=self.base.frame_int_keymap)

        self.lbl_crouch = DirectLabel(text=self.language['crouch'], text_bg=(0, 0, 0, 1),
                                      text_fg=(255, 255, 255, 0.9),
                                      text_font=self.font.load_font(self.menu_font),
                                      frameColor=(255, 255, 255, self.frm_opacity),
                                      scale=self.lbl_scale, borderWidth=(self.w, self.h),
                                      parent=self.base.frame_int_keymap)

        self.lbl_jump = DirectLabel(text=self.language['jump'], text_bg=(0, 0, 0, 1),
                                    text_fg=(255, 255, 255, 0.9),
                                    text_font=self.font.load_font(self.menu_font),
                                    frameColor=(255, 255, 255, self.frm_opacity),
                                    scale=self.lbl_scale, borderWidth=(self.w, self.h),
                                    parent=self.base.frame_int_keymap)

        self.lbl_use = DirectLabel(text=self.language['use'], text_bg=(0, 0, 0, 1),
                                   text_fg=(255, 255, 255, 0.9),
                                   text_font=self.font.load_font(self.menu_font),
                                   frameColor=(255, 255, 255, self.frm_opacity),
                                   scale=self.lbl_scale, borderWidth=(self.w, self.h),
                                   parent=self.base.frame_int_keymap)

        self.lbl_attack = DirectLabel(text=self.language['attack'], text_bg=(0, 0, 0, 1),
                                      text_fg=(255, 255, 255, 0.9),
                                      text_font=self.font.load_font(self.menu_font),
                                      frameColor=(255, 255, 255, self.frm_opacity),
                                      scale=self.lbl_scale, borderWidth=(self.w, self.h),
                                      parent=self.base.frame_int_keymap)

        self.lbl_h_attack = DirectLabel(text=self.language['h_attack'], text_bg=(0, 0, 0, 1),
                                        text_fg=(255, 255, 255, 0.9),
                                        text_font=self.font.load_font(self.menu_font),
                                        frameColor=(255, 255, 255, self.frm_opacity),
                                        scale=self.lbl_scale, borderWidth=(self.w, self.h),
                                        parent=self.base.frame_int_keymap)

        self.lbl_f_attack = DirectLabel(text=self.language['f_attack'], text_bg=(0, 0, 0, 1),
                                        text_fg=(255, 255, 255, 0.9),
                                        text_font=self.font.load_font(self.menu_font),
                                        frameColor=(255, 255, 255, self.frm_opacity),
                                        scale=self.lbl_scale, borderWidth=(self.w, self.h),
                                        parent=self.base.frame_int_keymap)

        self.lbl_block = DirectLabel(text=self.language['block'], text_bg=(0, 0, 0, 1),
                                     text_fg=(255, 255, 255, 0.9),
                                     text_font=self.font.load_font(self.menu_font),
                                     frameColor=(255, 255, 255, self.frm_opacity),
                                     scale=self.lbl_scale, borderWidth=(self.w, self.h),
                                     parent=self.base.frame_int_keymap)

        self.lbl_sword = DirectLabel(text=self.language['sword'], text_bg=(0, 0, 0, 1),
                                     text_fg=(255, 255, 255, 0.9),
                                     text_font=self.font.load_font(self.menu_font),
                                     frameColor=(255, 255, 255, self.frm_opacity),
                                     scale=self.lbl_scale, borderWidth=(self.w, self.h),
                                     parent=self.base.frame_int_keymap)

        self.lbl_bow = DirectLabel(text=self.language['bow'], text_bg=(0, 0, 0, 1),
                                   text_fg=(255, 255, 255, 0.9),
                                   text_font=self.font.load_font(self.menu_font),
                                   frameColor=(255, 255, 255, self.frm_opacity),
                                   scale=self.lbl_scale, borderWidth=(self.w, self.h),
                                   parent=self.base.frame_int_keymap)

        self.lbl_tengri = DirectLabel(text=self.language['tengri'], text_bg=(0, 0, 0, 1),
                                      text_fg=(255, 255, 255, 0.9),
                                      text_font=self.font.load_font(self.menu_font),
                                      frameColor=(255, 255, 255, self.frm_opacity),
                                      scale=self.lbl_scale, borderWidth=(self.w, self.h),
                                      parent=self.base.frame_int_keymap)

        self.lbl_umay = DirectLabel(text=self.language['umai'], text_bg=(0, 0, 0, 1),
                                    text_fg=(255, 255, 255, 0.9),
                                    text_font=self.font.load_font(self.menu_font),
                                    frameColor=(255, 255, 255, self.frm_opacity),
                                    scale=self.lbl_scale, borderWidth=(self.w, self.h),
                                    parent=self.base.frame_int_keymap)

        kmp = self.m_settings.input_validate(self.cfg_path, 'kmp')
        self.inp_forward = DirectEntry(initialText=kmp['Keymap']['forward'], text_bg=(0, 0, 0, 1),
                                       entryFont=self.font.load_font(self.menu_font),
                                       text_align=TextNode.A_center,
                                       scale=.03, width=7, borderWidth=(self.w, self.h),
                                       parent=self.base.frame_int_keymap,
                                       command=self.kmp.set_key_forward)

        self.inp_backward = DirectEntry(initialText=kmp['Keymap']['backward'], text_bg=(0, 0, 0, 1),
                                        entryFont=self.font.load_font(self.menu_font),
                                        text_align=TextNode.A_center,
                                        scale=.03, width=7, borderWidth=(self.w, self.h),
                                        parent=self.base.frame_int_keymap,
                                        command=self.kmp.set_key_backward)

        self.inp_left = DirectEntry(initialText=kmp['Keymap']['left'], text_bg=(0, 0, 0, 1),
                                    entryFont=self.font.load_font(self.menu_font),
                                    text_align=TextNode.A_center,
                                    scale=.03, width=7, borderWidth=(self.w, self.h),
                                    parent=self.base.frame_int_keymap,
                                    command=self.kmp.set_key_left)

        self.inp_right = DirectEntry(initialText=kmp['Keymap']['right'], text_bg=(0, 0, 0, 1),
                                     entryFont=self.font.load_font(self.menu_font),
                                     text_align=TextNode.A_center,
                                     scale=.03, width=7, borderWidth=(self.w, self.h),
                                     parent=self.base.frame_int_keymap,
                                     command=self.kmp.set_key_right)

        self.inp_crouch = DirectEntry(initialText=kmp['Keymap']['crouch'], text_bg=(0, 0, 0, 1),
                                      entryFont=self.font.load_font(self.menu_font),
                                      text_align=TextNode.A_center,
                                      scale=.03, width=7, borderWidth=(self.w, self.h),
                                      parent=self.base.frame_int_keymap,
                                      command=self.kmp.set_key_crouch)

        self.inp_jump = DirectEntry(initialText=kmp['Keymap']['jump'], text_bg=(0, 0, 0, 1),
                                    entryFont=self.font.load_font(self.menu_font),
                                    text_align=TextNode.A_center,
                                    scale=.03, width=7, borderWidth=(self.w, self.h),
                                    parent=self.base.frame_int_keymap,
                                    command=self.kmp.set_key_jump)

        self.inp_use = DirectEntry(initialText=kmp['Keymap']['use'], text_bg=(0, 0, 0, 1),
                                   entryFont=self.font.load_font(self.menu_font),
                                   text_align=TextNode.A_center,
                                   scale=.03, width=7, borderWidth=(self.w, self.h),
                                   parent=self.base.frame_int_keymap,
                                   command=self.kmp.set_key_use)

        self.inp_attack = DirectEntry(initialText=kmp['Keymap']['attack'], text_bg=(0, 0, 0, 1),
                                      entryFont=self.font.load_font(self.menu_font),
                                      text_align=TextNode.A_center,
                                      scale=.03, width=7, borderWidth=(self.w, self.h),
                                      parent=self.base.frame_int_keymap,
                                      command=self.kmp.set_key_attack)

        self.inp_h_attack = DirectEntry(initialText=kmp['Keymap']['h_attack'], text_bg=(0, 0, 0, 1),
                                        entryFont=self.font.load_font(self.menu_font),
                                        text_align=TextNode.A_center,
                                        scale=.03, width=7, borderWidth=(self.w, self.h),
                                        parent=self.base.frame_int_keymap,
                                        command=self.kmp.set_key_h_attack)

        self.inp_f_attack = DirectEntry(initialText=kmp['Keymap']['f_attack'], text_bg=(0, 0, 0, 1),
                                        entryFont=self.font.load_font(self.menu_font),
                                        text_align=TextNode.A_center,
                                        scale=.03, width=7, borderWidth=(self.w, self.h),
                                        parent=self.base.frame_int_keymap,
                                        command=self.kmp.set_key_f_attack)

        self.inp_block = DirectEntry(initialText=kmp['Keymap']['block'], text_bg=(0, 0, 0, 1),
                                     entryFont=self.font.load_font(self.menu_font),
                                     text_align=TextNode.A_center,
                                     scale=.03, width=7, borderWidth=(self.w, self.h),
                                     parent=self.base.frame_int_keymap,
                                     command=self.kmp.set_key_block)

        self.inp_sword = DirectEntry(initialText=kmp['Keymap']['sword'], text_bg=(0, 0, 0, 1),
                                     entryFont=self.font.load_font(self.menu_font),
                                     text_align=TextNode.A_center,
                                     scale=.03, width=7, borderWidth=(self.w, self.h),
                                     parent=self.base.frame_int_keymap,
                                     command=self.kmp.set_key_sword)

        self.inp_bow = DirectEntry(initialText=kmp['Keymap']['bow'], text_bg=(0, 0, 0, 0.9),
                                   entryFont=self.font.load_font(self.menu_font),
                                   text_align=TextNode.A_center,
                                   scale=.03, width=7, borderWidth=(self.w, self.h),
                                   parent=self.base.frame_int_keymap,
                                   command=self.kmp.set_key_bow)

        self.inp_tengri = DirectEntry(initialText=kmp['Keymap']['tengri'], text_bg=(0, 0, 0, 1),
                                      entryFont=self.font.load_font(self.menu_font),
                                      text_align=TextNode.A_center,
                                      scale=.03, width=7, borderWidth=(self.w, self.h),
                                      parent=self.base.frame_int_keymap,
                                      command=self.kmp.set_key_tengri)

        self.inp_umay = DirectEntry(initialText=kmp['Keymap']['umai'], text_bg=(0, 0, 0, 1),
                                    entryFont=self.font.load_font(self.menu_font),
                                    text_align=TextNode.A_center,
                                    scale=.03, width=7, borderWidth=(self.w, self.h),
                                    parent=self.base.frame_int_keymap,
                                    command=self.kmp.set_key_umay)

        self.btn_param_decline = DirectButton(text="Back", text_bg=(0, 0, 0, 1),
                                              text_fg=(255, 255, 255, 0.9),
                                              text_font=self.font.load_font(self.menu_font),
                                              frameColor=(255, 255, 255, self.frm_opacity),
                                              scale=self.btn_scale, borderWidth=(self.w, self.h),
                                              parent=self.base.frame_int_keymap,
                                              command=self.keymap_menu_unload)

        self.btn_param_defaults = DirectButton(text="Load defaults", text_bg=(0, 0, 0, 1),
                                               text_fg=(255, 255, 255, 0.9),
                                               text_font=self.font.load_font(self.menu_font),
                                               frameColor=(255, 255, 255, self.frm_opacity),
                                               scale=self.btn_scale, borderWidth=(self.w, self.h),
                                               parent=self.base.frame_int_keymap,
                                               command=self.kmp.set_default_keymap)

        """ Positioning objects of the keymapping menu:
            for two blocks
        """
        self.logo.reparent_to(self.base.frame_int_keymap)
        self.logo.set_scale(self.logo_scale)

        self.ornament_right.reparent_to(self.base.frame_int_keymap)
        self.ornament_right.set_scale(self.ornament_scale)
        self.ornament_right.set_hpr(0.0, 0.0, -90.0)
        self.ornament_left.reparent_to(self.base.frame_int_keymap)
        self.ornament_left.set_scale(self.ornament_scale)
        self.ornament_left.set_hpr(0.0, 0.0, -90.0)
        self.ornament_right.set_transparency(TransparencyAttrib.MAlpha)
        self.ornament_left.set_transparency(TransparencyAttrib.MAlpha)

        self.ornament_left.set_pos(self.ornament_l_kmp_pos)
        self.ornament_right.set_pos(self.ornament_r_kmp_pos)

        self.lbl_keymap_title.set_pos(-0.6, 0, 0.5)
        self.lbl_forward.set_pos(-1.6, 0, 0)
        self.lbl_backward.set_pos(-1.6, 0, -0.1)
        self.lbl_left.set_pos(-1.6, 0, -0.2)
        self.lbl_right.set_pos(-1.6, 0, -0.3)
        self.lbl_crouch.set_pos(-1.6, 0, -0.4)
        self.lbl_jump.set_pos(-1.6, 0, -0.5)
        self.lbl_use.set_pos(-1.6, 0, -0.6)

        """ Second block is here """
        self.lbl_attack.set_pos(-0.8, 0, -0.0)
        self.lbl_h_attack.set_pos(-0.8, 0, -0.1)
        self.lbl_f_attack.set_pos(-0.8, 0, -0.2)
        self.lbl_block.set_pos(-0.8, 0, -0.3)
        self.lbl_sword.set_pos(-0.8, 0, -0.4)
        self.lbl_bow.set_pos(-0.8, 0, -0.5)
        self.lbl_tengri.set_pos(-0.8, 0, -0.6)
        self.lbl_umay.set_pos(-0.8, 0, -0.7)

        self.inp_forward.set_pos(-1.3, 0, 0)
        self.inp_backward.set_pos(-1.3, 0, -0.1)
        self.inp_left.set_pos(-1.3, 0, -0.2)
        self.inp_right.set_pos(-1.3, 0, -0.3)
        self.inp_crouch.set_pos(-1.3, 0, -0.4)
        self.inp_jump.set_pos(-1.3, 0, -0.5)
        self.inp_use.set_pos(-1.3, 0, -0.6)

        """ Third block is here """
        self.inp_attack.set_pos(-0.5, 0, -0.0)
        self.inp_h_attack.set_pos(-0.5, 0, -0.1)
        self.inp_f_attack.set_pos(-0.5, 0, -0.2)
        self.inp_block.set_pos(-0.5, 0, -0.3)
        self.inp_sword.set_pos(-0.5, 0, -0.4)
        self.inp_bow.set_pos(-0.5, 0, -0.5)
        self.inp_tengri.set_pos(-0.5, 0, -0.6)
        self.inp_umay.set_pos(-0.5, 0, -0.7)

        self.btn_param_defaults.set_pos(-0.5, 0, -0.8)
        self.btn_param_decline.set_pos(-1.6, 0, -0.8)
        self.menu_mode = True

    def load_language_menu(self):
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

    def load_dev_mode_menu(self):
        self.game_mode = True

        self.base.frame_int_dev = DirectFrame(frameColor=(0, 0, 0, self.frm_opacity),
                                              frameSize=self.base.frame_int_dev_size)
        self.base.frame_int_dev.setPos(self.pos_X, self.pos_Y, self.pos_Z)

        self.lbl_dev_mode_title = DirectLabel(text="{}".format(self.language['dev_mode']),
                                              text_bg=(0, 0, 0, 1),
                                              text_fg=(155, 155, 255, 0.9),
                                              text_font=self.font.load_font(self.menu_font),
                                              frameColor=(255, 255, 255, self.frm_opacity),
                                              scale=.05, borderWidth=(self.w, self.h),
                                              parent=self.base.frame_int_dev)

        self.lbl_dev_mode_title_low = DirectLabel(text="{}".format(self.language['set_pos_title']),
                                                  text_bg=(0, 0, 0, 1),
                                                  text_fg=(155, 155, 255, 0.9),
                                                  text_font=self.font.load_font(self.menu_font),
                                                  frameColor=(255, 255, 255, self.frm_opacity),
                                                  scale=.03, borderWidth=(self.w, self.h),
                                                  parent=self.base.frame_int_dev)

        self.lbl_pos_x = DirectLabel(text=self.language['pos_x'], text_bg=(0, 0, 0, 1),
                                     text_fg=(255, 255, 255, 0.9),
                                     text_font=self.font.load_font(self.menu_font),
                                     frameColor=(255, 255, 255, self.frm_opacity),
                                     scale=.03, borderWidth=(self.w, self.h),
                                     parent=self.base.frame_int_dev)

        self.lbl_pos_y = DirectLabel(text=self.language['pos_y'], text_bg=(0, 0, 0, 1),
                                     text_fg=(255, 255, 255, 0.9),
                                     text_font=self.font.load_font(self.menu_font),
                                     frameColor=(255, 255, 255, self.frm_opacity),
                                     scale=.03, borderWidth=(self.w, self.h),
                                     parent=self.base.frame_int_dev)

        self.lbl_pos_z = DirectLabel(text=self.language['pos_z'], text_bg=(0, 0, 0, 1),
                                     text_fg=(255, 255, 255, 0.9),
                                     text_font=self.font.load_font(self.menu_font),
                                     frameColor=(255, 255, 255, self.frm_opacity),
                                     scale=.03, borderWidth=(self.w, self.h),
                                     parent=self.base.frame_int_dev)

        self.lbl_rot_h = DirectLabel(text=self.language['rot_h'], text_bg=(0, 0, 0, 1),
                                     text_fg=(255, 255, 255, 0.9),
                                     text_font=self.font.load_font(self.menu_font),
                                     frameColor=(255, 255, 255, self.frm_opacity),
                                     scale=.03, borderWidth=(self.w, self.h),
                                     parent=self.base.frame_int_dev)

        self.lbl_rot_p = DirectLabel(text=self.language['rot_p'], text_bg=(0, 0, 0, 1),
                                     text_fg=(255, 255, 255, 0.9),
                                     text_font=self.font.load_font(self.menu_font),
                                     frameColor=(255, 255, 255, self.frm_opacity),
                                     scale=.03, borderWidth=(self.w, self.h),
                                     parent=self.base.frame_int_dev)

        self.lbl_rot_r = DirectLabel(text=self.language['rot_r'], text_bg=(0, 0, 0, 1),
                                     text_fg=(255, 255, 255, 0.9),
                                     text_font=self.font.load_font(self.menu_font),
                                     frameColor=(255, 255, 255, self.frm_opacity),
                                     scale=.03, borderWidth=(self.w, self.h),
                                     parent=self.base.frame_int_dev)

        dev = self.m_settings.input_validate(self.cfg_path, 'dev')
        self.inp_pos_x = DirectEntry(initialText=dev['Debug']['player_pos_x'],
                                     text_bg=(0, 0, 0, 1),
                                     entryFont=self.font.load_font(self.menu_font),
                                     text_align=TextNode.A_center,
                                     scale=.03, width=7, borderWidth=(self.w, self.h),
                                     parent=self.base.frame_int_dev,
                                     command=self.dev_mode.set_node_pos_x)

        self.inp_pos_y = DirectEntry(initialText=dev['Debug']['player_pos_y'],
                                     text_bg=(0, 0, 0, 1),
                                     entryFont=self.font.load_font(self.menu_font),
                                     text_align=TextNode.A_center,
                                     scale=.03, width=7, borderWidth=(self.w, self.h),
                                     parent=self.base.frame_int_dev,
                                     command=self.dev_mode.set_node_pos_y)

        self.inp_pos_z = DirectEntry(initialText=dev['Debug']['player_pos_z'],
                                     text_bg=(0, 0, 0, 1),
                                     entryFont=self.font.load_font(self.menu_font),
                                     text_align=TextNode.A_center,
                                     scale=.03, width=7, borderWidth=(self.w, self.h),
                                     parent=self.base.frame_int_dev,
                                     command=self.dev_mode.set_node_pos_z)

        self.inp_rot_h = DirectEntry(initialText=dev['Debug']['player_rot_h'],
                                     text_bg=(0, 0, 0, 1),
                                     entryFont=self.font.load_font(self.menu_font),
                                     text_align=TextNode.A_center,
                                     scale=.03, width=7, borderWidth=(self.w, self.h),
                                     parent=self.base.frame_int_dev,
                                     command=self.dev_mode.set_node_rot_h)

        self.inp_rot_p = DirectEntry(initialText=dev['Debug']['player_rot_p'],
                                     text_bg=(0, 0, 0, 1),
                                     entryFont=self.font.load_font(self.menu_font),
                                     text_align=TextNode.A_center,
                                     scale=.03, width=7, borderWidth=(self.w, self.h),
                                     parent=self.base.frame_int_dev,
                                     command=self.dev_mode.set_node_rot_p)

        self.inp_rot_r = DirectEntry(initialText=dev['Debug']['player_rot_r'],
                                     text_bg=(0, 0, 0, 1),
                                     entryFont=self.font.load_font(self.menu_font),
                                     text_align=TextNode.A_center,
                                     scale=.03, width=7, borderWidth=(self.w, self.h),
                                     parent=self.base.frame_int_dev,
                                     command=self.dev_mode.set_node_rot_r)

        self.node_frame = DirectScrolledList(decButton_pos=(0.35, 0, 0.13),
                                             decButton_text="up",
                                             decButton_text_scale=0.04,
                                             decButton_borderWidth=(0.005, 0.005),

                                             incButton_pos=(0.35, 0, -0.1),
                                             incButton_text="Down",
                                             incButton_text_scale=0.04,
                                             incButton_borderWidth=(0.005, 0.005),

                                             frameSize=(-0.5, 1.2, -0.05, 0.11),
                                             frameColor=(153, 153, 153, 0.5),
                                             numItemsVisible=1,
                                             forceHeight=0.4,
                                             itemFrame_frameSize=(-0.8, 0.8, -0.04, 0.10),
                                             itemFrame_pos=(0.35, 0, 0.0),

                                             scale=.5,
                                             parent=self.base.frame_int_dev,
                                             decButtonCallback=self.get_active_node_wrapper,
                                             incButtonCallback=self.get_active_node_wrapper)

        self.lbl_node_exp = DirectLabel(text=self.language['node_exp'], text_bg=(0, 0, 0, 1),
                                        text_fg=(255, 255, 255, 0.9),
                                        text_font=self.font.load_font(self.menu_font),
                                        frameColor=(255, 255, 255, self.frm_opacity),
                                        scale=self.lbl_scale, borderWidth=(self.w, self.h),
                                        parent=self.base.frame_int_dev)

        self.lbl_perc_node_exp = OnscreenText(bg=(0, 0, 0, 1), fg=(255, 255, 255, 0.9),
                                              font=self.font.load_font(self.menu_font),
                                              scale=self.lbl_scale,
                                              parent=self.base.frame_int_dev, mayChange=True)

        self.slider_node_exp = DirectSlider(frameColor=self.rgba_gray_color, range=(1, 2),
                                            value=self.dev_mode.node_exp_value(),
                                            scale=.2, borderWidth=(self.w, self.h),
                                            parent=self.base.frame_int_dev,
                                            orientation=DGG.HORIZONTAL,
                                            command=self.set_slider_node_exp_wrapper)

        self.btn_back_options = DirectButton(text=self.language['back'], text_bg=(0, 0, 0, 1),
                                             text_fg=(255, 255, 255, 0.9),
                                             text_font=self.font.load_font(self.menu_font),
                                             frameColor=(255, 255, 255, self.frm_opacity),
                                             scale=self.btn_scale, borderWidth=(self.w, self.h),
                                             parent=self.base.frame_int_dev,
                                             command=self.dev_menu_unload)

        self.btn_save_changes = DirectButton(text='OK', text_bg=(0, 0, 0, 1),
                                             text_fg=(255, 255, 255, 0.9),
                                             text_font=self.font.load_font(self.menu_font),
                                             frameColor=(255, 255, 255, self.frm_opacity),
                                             scale=self.btn_scale, borderWidth=(self.w, self.h),
                                             parent=self.base.frame_int_dev,
                                             command=self.dev_mode_menu_save_changes)

        self.ornament_right.reparent_to(self.base.frame_int_dev)
        self.ornament_right.set_scale(self.ornament_scale)
        self.ornament_right.set_hpr(0.0, 0.0, -90.0)
        self.ornament_left.reparent_to(self.base.frame_int_dev)
        self.ornament_left.set_scale(self.ornament_scale)
        self.ornament_left.set_hpr(0.0, 0.0, -90.0)
        self.ornament_right.set_transparency(TransparencyAttrib.MAlpha)
        self.ornament_left.set_transparency(TransparencyAttrib.MAlpha)

        self.ornament_left.set_pos(self.ornament_l_dev_pos)
        self.ornament_right.set_pos(self.ornament_r_dev_pos)

        self.lbl_dev_mode_title.set_pos(-0.7, 0, 0.4)
        self.lbl_dev_mode_title_low.set_pos(-0.7, 0, 0.3)
        self.node_frame.set_pos(-1.3, 0, -0.0)
        self.lbl_pos_x.set_pos(-1.5, 0, -0.1)
        self.lbl_pos_y.set_pos(-1.5, 0, -0.2)
        self.lbl_pos_z.set_pos(-1.5, 0, -0.3)
        self.lbl_rot_h.set_pos(-1.5, 0, -0.4)
        self.lbl_rot_p.set_pos(-1.5, 0, -0.5)
        self.lbl_rot_r.set_pos(-1.5, 0, -0.6)

        self.inp_pos_x.set_pos(-0.5, 0, -0.1)
        self.inp_pos_y.set_pos(-0.5, 0, -0.2)
        self.inp_pos_z.set_pos(-0.5, 0, -0.3)
        self.inp_rot_h.set_pos(-0.5, 0, -0.4)
        self.inp_rot_p.set_pos(-0.5, 0, -0.5)
        self.inp_rot_r.set_pos(-0.5, 0, -0.6)

        self.lbl_node_exp.set_pos(-1.5, 0, -0.7)
        self.slider_node_exp.set_pos(-0.8, 0, -0.7)
        self.lbl_perc_node_exp.set_pos(-0.5, 0, -0.7)

        self.btn_back_options.set_pos(-1.5, 0, -0.9)
        self.btn_save_changes.set_pos(-0.5, 0, -0.9)
        self.logo.reparent_to(self.base.frame_int_dev)
        self.logo.set_scale(self.logo_scale)

        for x in self.dev_mode.check_game_assets_devmode(exclude='Animations'):
            l = DirectLabel(text=x, text_scale=0.2, pos=(1.1, 1.0, -0.7),
                            parent=self.node_frame, scale=.5, )
            self.node_frame.addItem(l)

        self.menu_mode = True

    def get_active_node_wrapper(self):
        self.dev_mode.get_active_node(self.node_frame.getSelectedText())

    def main_menu_unload(self):
        self.base.frame.hide()

    def options_menu_unload(self):
        if self.game_mode:
            self.base.frame_int.destroy()
        self.base.frame_int.destroy()
        """Reattach the destroyed logo to previous frame"""
        self.logo.reparent_to(self.base.frame)
        self.logo.set_scale(self.logo_scale)
        self.ornament_left.reparent_to(self.base.frame)
        self.ornament_right.reparent_to(self.base.frame)
        self.ornament_left.set_pos(self.ornament_l_pos)
        self.ornament_right.set_pos(self.ornament_r_pos)

    def gfx_menu_unload(self):
        if self.game_mode:
            self.base.frame_int_gfx.destroy()
        self.base.frame_int_gfx.destroy()
        """Reattach the destroyed logo to previous frame"""
        self.logo.reparent_to(self.base.frame_int)
        self.logo.set_scale(self.logo_scale)
        self.ornament_left.reparent_to(self.base.frame_int)
        self.ornament_right.reparent_to(self.base.frame_int)
        self.ornament_left.set_pos(self.ornament_l_pos)
        self.ornament_right.set_pos(self.ornament_r_pos)

    def sound_menu_unload(self):
        if self.game_mode:
            self.base.frame_int_snd.destroy()
        self.base.frame_int_snd.destroy()
        """Reattach the destroyed logo to previous frame"""
        self.logo.reparent_to(self.base.frame_int)
        self.logo.set_scale(self.logo_scale)
        self.ornament_left.reparent_to(self.base.frame_int)
        self.ornament_right.reparent_to(self.base.frame_int)
        self.ornament_left.set_pos(self.ornament_l_pos)
        self.ornament_right.set_pos(self.ornament_r_pos)

    def keymap_menu_unload(self):
        if self.game_mode:
            self.base.frame_int_keymap.destroy()
        self.base.frame_int_keymap.destroy()
        """Reattach the destroyed logo to previous frame"""
        self.logo.reparent_to(self.base.frame_int)
        self.logo.set_scale(self.logo_scale)
        self.ornament_left.reparent_to(self.base.frame_int)
        self.ornament_right.reparent_to(self.base.frame_int)
        self.ornament_left.set_pos(self.ornament_l_pos)
        self.ornament_right.set_pos(self.ornament_r_pos)

    def language_menu_unload(self):
        if self.game_mode:
            self.base.frame_int_lang.destroy()
        self.base.frame_int_lang.destroy()
        """Reattach the destroyed logo to previous frame"""
        self.logo.reparent_to(self.base.frame_int)
        self.logo.set_scale(self.logo_scale)
        self.ornament_left.reparent_to(self.base.frame_int)
        self.ornament_right.reparent_to(self.base.frame_int)
        self.ornament_left.set_pos(self.ornament_l_pos)
        self.ornament_right.set_pos(self.ornament_r_pos)

    def dev_mode_menu_save_changes(self):
        self.dev_mode.save_node_pos()
        self.dev_menu_unload()

    def dev_menu_unload(self):
        if self.game_mode:
            self.base.frame_int_dev.destroy()
        self.base.frame_int_dev.destroy()
        """Reattach the destroyed logo to previous frame"""
        self.logo.reparent_to(self.base.frame)
        self.logo.set_scale(self.logo_scale)
        self.ornament_left.reparent_to(self.base.frame)
        self.ornament_right.reparent_to(self.base.frame)
        self.ornament_left.set_pos(self.ornament_l_pos)
        self.ornament_right.set_pos(self.ornament_r_pos)

    """ Wrapper functions """

    # Direct* object doesn't allow passing it's instance directly before it created.
    # So, we pass it through wrapper methods

    def load_new_game_wrapper(self):
        if isinstance(self.game_mode, bool):
            self.main_menu_unload()
            self.game_mode = True
            self.menu_mode = False
            self.level_one.load_new_game()

    def load_game_wrapper(self):
        if isinstance(self.game_mode, bool):
            self.playworker.load_game()

    def save_game_wrapper(self):
        if isinstance(self.game_mode, bool):
            self.playworker.save_game()

    def delete_game_wrapper(self):
        if isinstance(self.game_mode, bool):
            self.playworker.delete_game()

    def set_slider_disp_res_wrapper(self):
        # Make it int and then str
        i = int(self.slider_disp_res['value'])
        disp_res_dict = self.gfx.load_disp_res()
        string = disp_res_dict[i]
        self.lbl_perc_disp_res.setText(string)
        self.gfx.save_disp_res_value(string)

    def set_slider_details_wrapper(self):
        # Make it int and then str
        i = int(self.slider_details['value'])
        self.lbl_perc_details.setText(str(i))
        # self.gfx.save_details_value(i)

    def set_slider_shadows_wrapper(self):
        # Make it int and then str
        i = int(self.slider_shadows['value'])
        shadows_dict = self.gfx.load_shadows_value()
        string = shadows_dict[i]
        self.lbl_perc_shadows.setText(string)
        self.gfx.save_shadows_value(string)

    def set_slider_postpro_wrapper(self):
        # Make it int and then str
        i = int(self.slider_postpro['value'])
        postpro_dict = self.gfx.load_postpro_value()
        string = postpro_dict[i]
        self.lbl_perc_postpro.setText(string)
        self.gfx.save_postpro_value(string)

    def set_slider_antial_wrapper(self):
        # Make it int and then str
        i = int(self.slider_antial['value'])
        antial_dict = self.gfx.load_antial_value()
        string = antial_dict[i]
        self.lbl_perc_antial.setText(string)
        self.gfx.save_antial_value(string)

    def set_slider_sound_wrapper(self):
        # Make it int and then str
        i = int(self.slider_sound['value'])
        sound_dict = self.snd.load_sound_value()
        string = sound_dict[i]
        self.lbl_perc_sound.setText(string)
        self.snd.save_sound_value(string)

    def set_slider_music_wrapper(self):
        # Make it int and then str
        i = int(self.slider_music['value'])
        music_dict = self.snd.load_music_value()
        string = music_dict[i]
        self.lbl_perc_music.setText(string)
        self.snd.save_music_value(string)

    def set_slider_sfx_wrapper(self):
        # Make it int and then str
        i = int(self.slider_effects['value'])
        sfx_dict = self.snd.load_sfx_value()
        string = sfx_dict[i]
        self.lbl_perc_effects.setText(string)
        self.snd.save_sfx_value(string)

    def set_slider_node_exp_wrapper(self):
        # Make it int and then str
        i = int(self.slider_node_exp['value'])
        node_exp_dict = self.dev_mode.load_node_exp_value()
        string = node_exp_dict[i]
        self.lbl_perc_node_exp.setText(string)
        self.dev_mode.save_node_exp_value(string)
