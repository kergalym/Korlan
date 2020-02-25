import json
import logging

from os.path import exists
from pathlib import Path

from direct.gui.DirectGui import *
from direct.gui.OnscreenImage import OnscreenImage, TransparencyAttrib
from panda3d.core import FontPool
from panda3d.core import TextNode

from Settings.menu_settings import MenuSettings
from Settings.menu_settings import Graphics


class MenuGraphics:
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
        self.base.frame_int_gfx = None

        """ Frame Sizes """
        self.base.frame_int_gfx_size = [-3, -0.2, -1, 3]

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

        self.ornament_l_gfx_pos = (-1.8, 0, -0.1)
        self.ornament_r_gfx_pos = (-0.3, 0, -0.1)

        """ Buttons, Label Scaling """
        self.lbl_scale = .03
        self.btn_scale = .03
        self.inp_scale = .04

        """ Misc """
        self.m_settings = MenuSettings()
        self.gfx = Graphics()

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

    def load_graphics_menu(self):
        """ Function    : load_graphics_menu

            Description : Load Graphics menu.

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
                                             command=self.unload_graphics_menu)

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

    def unload_graphics_menu(self):
        """ Function    : unload_graphics_menu

            Description : Unload Graphics menu.

            Input       : None

            Output      : None

            Return      : None
        """
        if self.game_mode:
            self.base.frame_int_gfx.destroy()
        self.base.frame_int_gfx.destroy()
        self.logo.destroy()
        self.ornament_left.destroy()
        self.ornament_right.destroy()

    """ Wrapper functions """
    """ Direct* object doesn't allow passing it's instance directly before it created.
        So, we pass it through wrapper methods
    """

    def set_slider_disp_res_wrapper(self):
        """ Function    : set_slider_disp_res_wrapper

            Description : Wrapper function.

            Input       : None

            Output      : None

            Return      : None
        """
        # Make it int and then str
        i = int(self.slider_disp_res['value'])
        disp_res_dict = self.gfx.load_disp_res()
        string = disp_res_dict[i]
        self.lbl_perc_disp_res.setText(string)
        self.gfx.save_disp_res_value(string)

    def set_slider_details_wrapper(self):
        """ Function    : set_slider_details_wrapper

            Description : Wrapper function.

            Input       : None

            Output      : None

            Return      : None
        """
        # Make it int and then str
        i = int(self.slider_details['value'])
        self.lbl_perc_details.setText(str(i))
        # self.gfx.save_details_value(i)

    def set_slider_shadows_wrapper(self):
        """ Function    : set_slider_shadows_wrapper

            Description : Wrapper function.

            Input       : None

            Output      : None

            Return      : None
        """
        # Make it int and then str
        i = int(self.slider_shadows['value'])
        shadows_dict = self.gfx.load_shadows_value()
        string = shadows_dict[i]
        self.lbl_perc_shadows.setText(string)
        self.gfx.save_shadows_value(string)

    def set_slider_postpro_wrapper(self):
        """ Function    : set_slider_postpro_wrapper

            Description : Wrapper function.

            Input       : None

            Output      : None

            Return      : None
        """
        # Make it int and then str
        i = int(self.slider_postpro['value'])
        postpro_dict = self.gfx.load_postpro_value()
        string = postpro_dict[i]
        self.lbl_perc_postpro.setText(string)
        self.gfx.save_postpro_value(string)

    def set_slider_antial_wrapper(self):
        """ Function    : set_slider_antial_wrapper

            Description : Wrapper function.

            Input       : None

            Output      : None

            Return      : None
        """
        # Make it int and then str
        i = int(self.slider_antial['value'])
        antial_dict = self.gfx.load_antial_value()
        string = antial_dict[i]
        self.lbl_perc_antial.setText(string)
        self.gfx.save_antial_value(string)

