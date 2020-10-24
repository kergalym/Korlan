import json
import logging

from os.path import exists
from pathlib import Path

from direct.gui.DirectGui import *
from direct.gui.OnscreenImage import OnscreenImage, TransparencyAttrib
from direct.showbase.ShowBaseGlobal import aspect2d
from panda3d.core import FontPool
from panda3d.core import TextNode

from Settings.menu_settings import MenuSettings
from Settings.gfx_menu_settings import Graphics


class GraphicsMenuUI(Graphics):
    def __init__(self):
        Graphics.__init__(self)
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
        self.base.frame_int_gfx = None

        """ Frame Sizes """
        # Left, right, bottom, top
        self.base.frame_int_gfx_size = [-0.9, 3, -1, 3]

        """ Frame Colors """
        self.frm_opacity = 1

        """ Logo & Ornament Scaling, Positioning """
        self.logo = None
        self.ornament_right = None
        self.logo_scale = (0.33, 0.30, 0.30)
        self.logo_pos = (-0.3, 0, 0.6)
        self.ornament_scale = (1.40, 0.05, 0.05)
        self.ornament_r_pos = (1.8, 0, -0.1)

        self.ornament_r_gfx_pos = (1.8, 0, -0.1)

        """ Buttons, Label Scaling """
        self.lbl_scale = .04
        self.sli_scale = (.4, 0, .2)
        self.btn_scale = .04

        """ Misc """
        self.m_settings = MenuSettings()

        """ Graphics MenuUI Objects """
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
        self.lbl_ao = None
        self.lbl_bloom = None
        self.lbl_clouds = None
        self.lbl_cc = None
        self.lbl_scattering = None
        self.lbl_sky_ao = None
        self.lbl_ssr = None
        self.lbl_forward_shading = None
        self.lbl_skin_shading = None
        self.lbl_pssm = None
        self.lbl_dof = None
        self.lbl_env_probes = None
        self.lbl_motion_blur = None
        self.lbl_volumetrics = None

        self.lbl_perc_disp_res = None
        self.lbl_perc_details = None
        self.lbl_perc_shadows = None
        self.lbl_perc_postpro = None
        self.lbl_perc_antial = None
        self.lbl_perc_ao = None
        self.lbl_perc_bloom = None
        self.lbl_perc_clouds = None
        self.lbl_perc_cc = None
        self.lbl_perc_scattering = None
        self.lbl_perc_sky_ao = None
        self.lbl_perc_ssr = None
        self.lbl_perc_forward_shading = None
        self.lbl_perc_skin_shading = None
        self.lbl_perc_pssm = None
        self.lbl_perc_dof = None
        self.lbl_perc_env_probes = None
        self.lbl_perc_motion_blur = None
        self.lbl_perc_volumetrics = None

        self.btn_param_accept = None
        self.btn_param_back = None
        self.btn_param_decline = None
        self.btn_param_defaults = None

        self.slider_disp_res = None
        self.slider_details = None
        self.slider_shadows = None
        self.slider_postpro = None
        self.slider_antial = None
        self.slider_ao = None
        self.slider_bloom = None
        self.slider_clouds = None
        self.slider_cc = None
        self.slider_scattering = None
        self.slider_sky_ao = None
        self.slider_ssr = None
        self.slider_forward_shading = None
        self.slider_skin_shading = None
        self.slider_pssm = None
        self.slider_dof = None
        self.slider_env_probes = None
        self.slider_motion_blur = None
        self.slider_volumetrics = None

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

    def load_graphics_menu(self):
        """ Function    : load_graphics_menu

            Description : Load Graphics menu.

            Input       : None

            Output      : None

            Return      : None
        """
        if hasattr(base, "active_frame"):
            base.active_frame.destroy()

        ui_geoms = base.ui_geom_collector()

        maps = base.loader.loadModel(ui_geoms['btn_t_icon'])
        geoms = (maps.find('**/button_any'),
                 maps.find('**/button_pressed'),
                 maps.find('**/button_rollover'))

        self.unload_graphics_menu()

        self.logo = OnscreenImage(image=self.images['display_icon'],
                                  pos=self.logo_pos)
        self.logo.set_transparency(TransparencyAttrib.MAlpha)
        self.ornament_right = OnscreenImage(image=self.images['ornament_kz'],
                                            pos=self.ornament_r_pos, color=(63.9, 63.9, 63.9, 0.5))

        self.base.frame_int_gfx = DirectFrame(frameColor=(0, 0, 0, self.frm_opacity),
                                              frameSize=self.base.frame_int_gfx_size)
        self.base.frame_int_gfx.setPos(self.pos_X, self.pos_Y, self.pos_Z)
        self.base.build_info.reparent_to(self.base.frame_int_gfx)

        self.lbl_gfx_title = DirectLabel(text=self.language['graphics'],
                                         text_fg=(255, 255, 255, 1),
                                         text_font=self.font.load_font(self.menu_font),
                                         frameColor=(255, 255, 255, 0),
                                         scale=.07, borderWidth=(self.w, self.h),
                                         parent=self.base.frame_int_gfx)

        self.lbl_disp_res = DirectLabel(text=self.language['disp_res'],
                                        text_fg=(255, 255, 255, 1),
                                        text_font=self.font.load_font(self.menu_font),
                                        frameColor=(255, 255, 255, 0),
                                        scale=self.lbl_scale, borderWidth=(self.w, self.h),
                                        parent=self.base.frame_int_gfx)

        self.lbl_details = DirectLabel(text=self.language['details'],
                                       text_fg=(255, 255, 255, 1),
                                       text_font=self.font.load_font(self.menu_font),
                                       frameColor=(255, 255, 255, 0),
                                       scale=self.lbl_scale, borderWidth=(self.w, self.h),
                                       parent=self.base.frame_int_gfx)

        self.lbl_shadows = DirectLabel(text=self.language['shadows'],
                                       text_fg=(255, 255, 255, 1),
                                       text_font=self.font.load_font(self.menu_font),
                                       frameColor=(255, 255, 255, 0),
                                       scale=self.lbl_scale, borderWidth=(self.w, self.h),
                                       parent=self.base.frame_int_gfx)

        self.lbl_postprocessing = DirectLabel(text=self.language['postprocessing'],
                                              text_fg=(255, 255, 255, 1),
                                              text_font=self.font.load_font(self.menu_font),
                                              frameColor=(255, 255, 255, 0),
                                              scale=self.lbl_scale, borderWidth=(self.w, self.h),
                                              parent=self.base.frame_int_gfx)

        self.lbl_antialiasing = DirectLabel(text=self.language['antialiasing'],
                                            text_fg=(255, 255, 255, 1),
                                            text_font=self.font.load_font(self.menu_font),
                                            frameColor=(255, 255, 255, 0),
                                            scale=self.lbl_scale, borderWidth=(self.w, self.h),
                                            parent=self.base.frame_int_gfx)

        self.lbl_ao = DirectLabel(text=self.language['ao'],
                                  text_fg=(255, 255, 255, 1),
                                  text_font=self.font.load_font(self.menu_font),
                                  frameColor=(255, 255, 255, 0),
                                  scale=self.lbl_scale, borderWidth=(self.w, self.h),
                                  parent=self.base.frame_int_gfx)

        self.lbl_bloom = DirectLabel(text=self.language['bloom'],
                                     text_fg=(255, 255, 255, 1),
                                     text_font=self.font.load_font(self.menu_font),
                                     frameColor=(255, 255, 255, 0),
                                     scale=self.lbl_scale, borderWidth=(self.w, self.h),
                                     parent=self.base.frame_int_gfx)

        self.lbl_clouds = DirectLabel(text=self.language['clouds'],
                                      text_fg=(255, 255, 255, 1),
                                      text_font=self.font.load_font(self.menu_font),
                                      frameColor=(255, 255, 255, 0),
                                      scale=self.lbl_scale, borderWidth=(self.w, self.h),
                                      parent=self.base.frame_int_gfx)

        self.lbl_cc = DirectLabel(text=self.language['cc'],
                                  text_fg=(255, 255, 255, 1),
                                  text_font=self.font.load_font(self.menu_font),
                                  frameColor=(255, 255, 255, 0),
                                  scale=self.lbl_scale, borderWidth=(self.w, self.h),
                                  parent=self.base.frame_int_gfx)

        self.lbl_scattering = DirectLabel(text=self.language['scattering'],
                                          text_fg=(255, 255, 255, 1),
                                          text_font=self.font.load_font(self.menu_font),
                                          frameColor=(255, 255, 255, 0),
                                          scale=self.lbl_scale, borderWidth=(self.w, self.h),
                                          parent=self.base.frame_int_gfx)

        self.lbl_sky_ao = DirectLabel(text=self.language['sky_ao'],
                                      text_fg=(255, 255, 255, 1),
                                      text_font=self.font.load_font(self.menu_font),
                                      frameColor=(255, 255, 255, 0),
                                      scale=self.lbl_scale, borderWidth=(self.w, self.h),
                                      parent=self.base.frame_int_gfx)

        self.lbl_ssr = DirectLabel(text=self.language['ssr'],
                                   text_fg=(255, 255, 255, 1),
                                   text_font=self.font.load_font(self.menu_font),
                                   frameColor=(255, 255, 255, 0),
                                   scale=self.lbl_scale, borderWidth=(self.w, self.h),
                                   parent=self.base.frame_int_gfx)

        self.lbl_forward_shading = DirectLabel(text=self.language['forward_shading'],
                                               text_fg=(255, 255, 255, 1),
                                               text_font=self.font.load_font(self.menu_font),
                                               frameColor=(255, 255, 255, 0),
                                               scale=self.lbl_scale, borderWidth=(self.w, self.h),
                                               parent=self.base.frame_int_gfx)

        self.lbl_skin_shading = DirectLabel(text=self.language['skin_shading'],
                                            text_fg=(255, 255, 255, 1),
                                            text_font=self.font.load_font(self.menu_font),
                                            frameColor=(255, 255, 255, 0),
                                            scale=self.lbl_scale, borderWidth=(self.w, self.h),
                                            parent=self.base.frame_int_gfx)

        self.lbl_pssm = DirectLabel(text=self.language['pssm'],
                                    text_fg=(255, 255, 255, 1),
                                    text_font=self.font.load_font(self.menu_font),
                                    frameColor=(255, 255, 255, 0),
                                    scale=self.lbl_scale, borderWidth=(self.w, self.h),
                                    parent=self.base.frame_int_gfx)

        self.lbl_dof = DirectLabel(text=self.language['dof'],
                                   text_fg=(255, 255, 255, 1),
                                   text_font=self.font.load_font(self.menu_font),
                                   frameColor=(255, 255, 255, 0),
                                   scale=self.lbl_scale, borderWidth=(self.w, self.h),
                                   parent=self.base.frame_int_gfx)

        self.lbl_env_probes = DirectLabel(text=self.language['env_probes'],
                                          text_fg=(255, 255, 255, 1),
                                          text_font=self.font.load_font(self.menu_font),
                                          frameColor=(255, 255, 255, 0),
                                          scale=self.lbl_scale, borderWidth=(self.w, self.h),
                                          parent=self.base.frame_int_gfx)

        self.lbl_motion_blur = DirectLabel(text=self.language['motion_blur'],
                                           text_fg=(255, 255, 255, 1),
                                           text_font=self.font.load_font(self.menu_font),
                                           frameColor=(255, 255, 255, 0),
                                           scale=self.lbl_scale, borderWidth=(self.w, self.h),
                                           parent=self.base.frame_int_gfx)

        self.lbl_volumetrics = DirectLabel(text=self.language['volumetrics'],
                                           text_fg=(255, 255, 255, 1),
                                           text_font=self.font.load_font(self.menu_font),
                                           frameColor=(255, 255, 255, 0),
                                           scale=self.lbl_scale, borderWidth=(self.w, self.h),
                                           parent=self.base.frame_int_gfx)

        self.slider_disp_res = DirectSlider(frameColor=self.rgba_gray_color,
                                            range=(1, self.load_disp_res_value()),
                                            value=self.get_disp_res_value(),
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

        self.slider_shadows = DirectSlider(frameColor=self.rgba_gray_color,
                                           range=(1, 2),
                                           value=self.get_shadows_value(),
                                           scale=.2, borderWidth=(self.w, self.h),
                                           parent=self.base.frame_int_gfx,
                                           orientation=DGG.HORIZONTAL,
                                           command=self.set_slider_shadows_wrapper)

        self.slider_postpro = DirectSlider(frameColor=self.rgba_gray_color,
                                           range=(1, 2),
                                           value=self.get_postpro_value(),
                                           scale=.2, borderWidth=(self.w, self.h),
                                           parent=self.base.frame_int_gfx,
                                           orientation=DGG.HORIZONTAL,
                                           command=self.set_slider_postpro_wrapper)

        self.slider_antial = DirectSlider(frameColor=self.rgba_gray_color,
                                          range=(1, 2),
                                          value=self.get_antial_value(),
                                          scale=.2, borderWidth=(self.w, self.h),
                                          parent=self.base.frame_int_gfx,
                                          orientation=DGG.HORIZONTAL,
                                          command=self.set_slider_antial_wrapper)

        self.slider_ao = DirectSlider(frameColor=self.rgba_gray_color,
                                      range=(1, 7),
                                      value=self.get_ao_value(),
                                      scale=.2, borderWidth=(self.w, self.h),
                                      parent=self.base.frame_int_gfx,
                                      orientation=DGG.HORIZONTAL,
                                      command=self.set_slider_ao_wrapper)

        self.slider_bloom = DirectSlider(frameColor=self.rgba_gray_color, range=(1, 2),
                                         value=self.get_bloom_value(),
                                         scale=.2, borderWidth=(self.w, self.h),
                                         parent=self.base.frame_int_gfx,
                                         orientation=DGG.HORIZONTAL,
                                         command=self.set_slider_bloom_wrapper)

        self.slider_clouds = DirectSlider(frameColor=self.rgba_gray_color, range=(1, 2),
                                          value=self.get_clouds_value(),
                                          scale=.2, borderWidth=(self.w, self.h),
                                          parent=self.base.frame_int_gfx,
                                          orientation=DGG.HORIZONTAL,
                                          command=self.set_slider_clouds_wrapper)

        self.slider_cc = DirectSlider(frameColor=self.rgba_gray_color, range=(1, 2),
                                      value=self.get_cc_value(),
                                      scale=.2, borderWidth=(self.w, self.h),
                                      parent=self.base.frame_int_gfx,
                                      orientation=DGG.HORIZONTAL,
                                      command=self.set_slider_cc_wrapper)

        self.slider_scattering = DirectSlider(frameColor=self.rgba_gray_color, range=(1, 2),
                                              value=self.get_scattering_value(),
                                              scale=.2, borderWidth=(self.w, self.h),
                                              parent=self.base.frame_int_gfx,
                                              orientation=DGG.HORIZONTAL,
                                              command=self.set_slider_scattering_wrapper)

        self.slider_sky_ao = DirectSlider(frameColor=self.rgba_gray_color, range=(1, 2),
                                          value=self.get_sky_ao_value(),
                                          scale=.2, borderWidth=(self.w, self.h),
                                          parent=self.base.frame_int_gfx,
                                          orientation=DGG.HORIZONTAL,
                                          command=self.set_slider_sky_ao_wrapper)

        self.slider_ssr = DirectSlider(frameColor=self.rgba_gray_color, range=(1, 2),
                                       value=self.get_ssr_value(),
                                       scale=.2, borderWidth=(self.w, self.h),
                                       parent=self.base.frame_int_gfx,
                                       orientation=DGG.HORIZONTAL,
                                       command=self.set_slider_ssr_wrapper)

        self.slider_forward_shading = DirectSlider(frameColor=self.rgba_gray_color, range=(1, 2),
                                                   value=self.get_forward_shading_value(),
                                                   scale=.2, borderWidth=(self.w, self.h),
                                                   parent=self.base.frame_int_gfx,
                                                   orientation=DGG.HORIZONTAL,
                                                   command=self.set_slider_forward_shading_wrapper)

        self.slider_skin_shading = DirectSlider(frameColor=self.rgba_gray_color, range=(1, 2),
                                                value=self.get_skin_shading_value(),
                                                scale=.2, borderWidth=(self.w, self.h),
                                                parent=self.base.frame_int_gfx,
                                                orientation=DGG.HORIZONTAL,
                                                command=self.set_slider_skin_shading_wrapper)

        self.slider_pssm = DirectSlider(frameColor=self.rgba_gray_color, range=(1, 2),
                                        value=self.get_pssm_value(),
                                        scale=.2, borderWidth=(self.w, self.h),
                                        parent=self.base.frame_int_gfx,
                                        orientation=DGG.HORIZONTAL,
                                        command=self.set_slider_pssm_wrapper)

        self.slider_dof = DirectSlider(frameColor=self.rgba_gray_color, range=(1, 2),
                                       value=self.get_dof_value(),
                                       scale=.2, borderWidth=(self.w, self.h),
                                       parent=self.base.frame_int_gfx,
                                       orientation=DGG.HORIZONTAL,
                                       command=self.set_slider_dof_wrapper)

        self.slider_env_probes = DirectSlider(frameColor=self.rgba_gray_color, range=(1, 2),
                                              value=self.get_env_probes_value(),
                                              scale=.2, borderWidth=(self.w, self.h),
                                              parent=self.base.frame_int_gfx,
                                              orientation=DGG.HORIZONTAL,
                                              command=self.set_slider_env_probes_wrapper)

        self.slider_motion_blur = DirectSlider(frameColor=self.rgba_gray_color, range=(1, 2),
                                               value=self.get_motion_blur_value(),
                                               scale=.2, borderWidth=(self.w, self.h),
                                               parent=self.base.frame_int_gfx,
                                               orientation=DGG.HORIZONTAL,
                                               command=self.set_slider_motion_blur_wrapper)

        self.slider_volumetrics = DirectSlider(frameColor=self.rgba_gray_color, range=(1, 2),
                                               value=self.get_volumetrics_value(),
                                               scale=.2, borderWidth=(self.w, self.h),
                                               parent=self.base.frame_int_gfx,
                                               orientation=DGG.HORIZONTAL,
                                               command=self.set_slider_volumetrics_wrapper)

        self.lbl_perc_disp_res = OnscreenText(bg=(0, 0, 0, 0), fg=(255, 255, 255, 1),
                                              font=self.font.load_font(self.menu_font),
                                              scale=self.lbl_scale,
                                              parent=self.base.frame_int_gfx, mayChange=True)

        self.lbl_perc_details = OnscreenText(bg=(0, 0, 0, 0), fg=(255, 255, 255, 1),
                                             font=self.font.load_font(self.menu_font),
                                             scale=self.lbl_scale,
                                             parent=self.base.frame_int_gfx, mayChange=True)

        self.lbl_perc_shadows = OnscreenText(bg=(0, 0, 0, 0), fg=(255, 255, 255, 1),
                                             font=self.font.load_font(self.menu_font),
                                             scale=self.lbl_scale,
                                             parent=self.base.frame_int_gfx, mayChange=True)

        self.lbl_perc_postpro = OnscreenText(bg=(0, 0, 0, 0), fg=(255, 255, 255, 1),
                                             font=self.font.load_font(self.menu_font),
                                             scale=self.lbl_scale,
                                             parent=self.base.frame_int_gfx, mayChange=True)

        self.lbl_perc_antial = OnscreenText(bg=(0, 0, 0, 0), fg=(255, 255, 255, 1),
                                            font=self.font.load_font(self.menu_font),
                                            scale=self.lbl_scale,
                                            parent=self.base.frame_int_gfx, mayChange=True)

        self.lbl_perc_ao = OnscreenText(bg=(0, 0, 0, 0), fg=(255, 255, 255, 1),
                                        font=self.font.load_font(self.menu_font),
                                        scale=self.lbl_scale,
                                        parent=self.base.frame_int_gfx, mayChange=True)

        self.lbl_perc_bloom = OnscreenText(bg=(0, 0, 0, 0), fg=(255, 255, 255, 1),
                                           font=self.font.load_font(self.menu_font),
                                           scale=self.lbl_scale,
                                           parent=self.base.frame_int_gfx, mayChange=True)

        self.lbl_perc_clouds = OnscreenText(bg=(0, 0, 0, 0), fg=(255, 255, 255, 1),
                                            font=self.font.load_font(self.menu_font),
                                            scale=self.lbl_scale,
                                            parent=self.base.frame_int_gfx, mayChange=True)

        self.lbl_perc_cc = OnscreenText(bg=(0, 0, 0, 0), fg=(255, 255, 255, 1),
                                        font=self.font.load_font(self.menu_font),
                                        scale=self.lbl_scale,
                                        parent=self.base.frame_int_gfx, mayChange=True)

        self.lbl_perc_scattering = OnscreenText(bg=(0, 0, 0, 0), fg=(255, 255, 255, 1),
                                                font=self.font.load_font(self.menu_font),
                                                scale=self.lbl_scale,
                                                parent=self.base.frame_int_gfx, mayChange=True)

        self.lbl_perc_sky_ao = OnscreenText(bg=(0, 0, 0, 0), fg=(255, 255, 255, 1),
                                            font=self.font.load_font(self.menu_font),
                                            scale=self.lbl_scale,
                                            parent=self.base.frame_int_gfx, mayChange=True)

        self.lbl_perc_ssr = OnscreenText(bg=(0, 0, 0, 0), fg=(255, 255, 255, 1),
                                         font=self.font.load_font(self.menu_font),
                                         scale=self.lbl_scale,
                                         parent=self.base.frame_int_gfx, mayChange=True)

        self.lbl_perc_forward_shading = OnscreenText(bg=(0, 0, 0, 0), fg=(255, 255, 255, 1),
                                                     font=self.font.load_font(self.menu_font),
                                                     scale=self.lbl_scale,
                                                     parent=self.base.frame_int_gfx, mayChange=True)

        self.lbl_perc_skin_shading = OnscreenText(bg=(0, 0, 0, 0), fg=(255, 255, 255, 1),
                                                  font=self.font.load_font(self.menu_font),
                                                  scale=self.lbl_scale,
                                                  parent=self.base.frame_int_gfx, mayChange=True)

        self.lbl_perc_pssm = OnscreenText(bg=(0, 0, 0, 0), fg=(255, 255, 255, 1),
                                          font=self.font.load_font(self.menu_font),
                                          scale=self.lbl_scale,
                                          parent=self.base.frame_int_gfx, mayChange=True)

        self.lbl_perc_dof = OnscreenText(bg=(0, 0, 0, 0), fg=(255, 255, 255, 1),
                                         font=self.font.load_font(self.menu_font),
                                         scale=self.lbl_scale,
                                         parent=self.base.frame_int_gfx, mayChange=True)

        self.lbl_perc_env_probes = OnscreenText(bg=(0, 0, 0, 0), fg=(255, 255, 255, 1),
                                                font=self.font.load_font(self.menu_font),
                                                scale=self.lbl_scale,
                                                parent=self.base.frame_int_gfx, mayChange=True)

        self.lbl_perc_motion_blur = OnscreenText(bg=(0, 0, 0, 0), fg=(255, 255, 255, 1),
                                                 font=self.font.load_font(self.menu_font),
                                                 scale=self.lbl_scale,
                                                 parent=self.base.frame_int_gfx, mayChange=True)

        self.lbl_perc_volumetrics = OnscreenText(bg=(0, 0, 0, 0), fg=(255, 255, 255, 1),
                                                 font=self.font.load_font(self.menu_font),
                                                 scale=self.lbl_scale,
                                                 parent=self.base.frame_int_gfx, mayChange=True)

        self.btn_param_defaults = DirectButton(text="Load defaults",
                                               text_fg=(255, 255, 255, 1),
                                               text_font=self.font.load_font(self.menu_font),
                                               frameColor=(255, 255, 255, 0),
                                               scale=self.btn_scale, borderWidth=(self.w, self.h),
                                               parent=self.base.frame_int_gfx,
                                               geom=geoms, geom_scale=(8.1, 0, 2),
                                               clickSound=self.base.sound_gui_click,
                                               command=self.set_default_gfx)

        self.btn_param_accept = DirectButton(text="OK",
                                             text_fg=(255, 255, 255, 1),
                                             text_font=self.font.load_font(self.menu_font),
                                             frameColor=(255, 255, 255, 0),
                                             scale=self.btn_scale, borderWidth=(self.w, self.h),
                                             parent=self.base.frame_int_gfx,
                                             geom=geoms, geom_scale=(5.1, 0, 2),
                                             clickSound=self.base.sound_gui_click,
                                             command=self.unload_graphics_menu)

        """ Positioning objects of the keymapping menu:
            for two blocks
        """
        self.logo.reparent_to(self.base.frame_int_gfx)
        self.logo.set_scale(0.35, 0.20, 0.20)

        self.ornament_right.reparent_to(self.base.frame_int_gfx)
        self.ornament_right.set_scale(self.ornament_scale)
        self.ornament_right.set_hpr(0.0, 0.0, -90.0)
        self.ornament_right.set_pos(self.ornament_r_gfx_pos)
        self.ornament_right.set_transparency(TransparencyAttrib.MAlpha)

        self.lbl_gfx_title.set_pos(0.6, 0, 0.6)

        self.lbl_disp_res.set_pos(-0.5, 0, 0.3)
        self.lbl_details.set_pos(-0.5, 0, 0.2)
        self.lbl_shadows.set_pos(-0.5, 0, 0.1)
        self.lbl_postprocessing.set_pos(-0.5, 0, 0)
        self.lbl_antialiasing.set_pos(-0.5, 0, -0.1)
        self.lbl_ao.set_pos(-0.5, 0, -0.2)
        self.lbl_bloom.set_pos(-0.5, 0, -0.3)
        self.lbl_clouds.set_pos(-0.5, 0, -0.4)
        self.lbl_cc.set_pos(-0.5, 0, -0.5)

        self.slider_disp_res.set_pos(-0.0, 0, 0.3)
        self.slider_details.set_pos(-0.0, 0, 0.2)
        self.slider_shadows.set_pos(-0.0, 0, 0.1)
        self.slider_postpro.set_pos(-0.0, 0, 0)
        self.slider_antial.set_pos(-0.0, 0, -0.1)
        self.slider_ao.set_pos(-0.0, 0, -0.2)
        self.slider_bloom.set_pos(-0.0, 0, -0.3)
        self.slider_clouds.set_pos(-0.0, 0, -0.4)
        self.slider_cc.set_pos(-0.0, 0, -0.5)

        OnscreenImage(image=self.images['ui_slider_button'],
                      scale=(.07, .07, .08)).reparent_to(self.slider_disp_res.thumb)
        OnscreenImage(image=self.images['ui_slider_button'],
                      scale=(.07, .07, .08)).reparent_to(self.slider_details.thumb)
        OnscreenImage(image=self.images['ui_slider_button'],
                      scale=(.07, .07, .08)).reparent_to(self.slider_shadows.thumb)
        OnscreenImage(image=self.images['ui_slider_button'],
                      scale=(.07, .07, .08)).reparent_to(self.slider_postpro.thumb)
        OnscreenImage(image=self.images['ui_slider_button'],
                      scale=(.07, .07, .08)).reparent_to(self.slider_antial.thumb)
        OnscreenImage(image=self.images['ui_slider_button'],
                      scale=(.07, .07, .08)).reparent_to(self.slider_ao.thumb)
        OnscreenImage(image=self.images['ui_slider_button'],
                      scale=(.07, .07, .08)).reparent_to(self.slider_bloom.thumb)
        OnscreenImage(image=self.images['ui_slider_button'],
                      scale=(.07, .07, .08)).reparent_to(self.slider_clouds.thumb)
        OnscreenImage(image=self.images['ui_slider_button'],
                      scale=(.07, .07, .08)).reparent_to(self.slider_cc.thumb)

        self.lbl_perc_disp_res.set_pos(0.4, 0, 0.3)
        self.lbl_perc_details.set_pos(0.4, 0, 0.2)
        self.lbl_perc_shadows.set_pos(0.4, 0, 0.1)
        self.lbl_perc_postpro.set_pos(0.4, 0, 0)
        self.lbl_perc_antial.set_pos(0.4, 0, -0.1)
        self.lbl_perc_ao.set_pos(0.4, 0, -0.2)
        self.lbl_perc_bloom.set_pos(0.4, 0, -0.3)
        self.lbl_perc_clouds.set_pos(0.4, 0, -0.4)
        self.lbl_perc_cc.set_pos(0.4, 0, -0.5)

        self.lbl_scattering.set_pos(0.8, 0, 0.3)
        self.lbl_sky_ao.set_pos(0.8, 0, 0.2)
        self.lbl_ssr.set_pos(0.8, 0, 0.1)
        self.lbl_forward_shading.set_pos(0.8, 0, 0)
        self.lbl_skin_shading.set_pos(0.8, 0, -0.1)
        self.lbl_pssm.set_pos(0.8, 0, -0.2)
        self.lbl_dof.set_pos(0.8, 0, -0.3)
        self.lbl_env_probes.set_pos(0.8, 0, -0.4)
        self.lbl_motion_blur.set_pos(0.8, 0, -0.5)
        self.lbl_volumetrics.set_pos(0.8, 0, -0.6)

        self.slider_scattering.set_pos(1.3, 0, 0.3)
        self.slider_sky_ao.set_pos(1.3, 0, 0.2)
        self.slider_ssr.set_pos(1.3, 0, 0.1)
        self.slider_forward_shading.set_pos(1.3, 0, 0)
        self.slider_skin_shading.set_pos(1.3, 0, -0.1)
        self.slider_pssm.set_pos(1.3, 0, -0.2)
        self.slider_dof.set_pos(1.3, 0, -0.3)
        self.slider_env_probes.set_pos(1.3, 0, -0.4)
        self.slider_motion_blur.set_pos(1.3, 0, -0.5)
        self.slider_volumetrics.set_pos(1.3, 0, -0.6)

        OnscreenImage(image=self.images['ui_slider_button'],
                      scale=(.07, .07, .08)).reparent_to(self.slider_scattering.thumb)
        OnscreenImage(image=self.images['ui_slider_button'],
                      scale=(.07, .07, .08)).reparent_to(self.slider_sky_ao.thumb)
        OnscreenImage(image=self.images['ui_slider_button'],
                      scale=(.07, .07, .08)).reparent_to(self.slider_ssr.thumb)
        OnscreenImage(image=self.images['ui_slider_button'],
                      scale=(.07, .07, .08)).reparent_to(self.slider_forward_shading.thumb)
        OnscreenImage(image=self.images['ui_slider_button'],
                      scale=(.07, .07, .08)).reparent_to(self.slider_skin_shading.thumb)
        OnscreenImage(image=self.images['ui_slider_button'],
                      scale=(.07, .07, .08)).reparent_to(self.slider_pssm.thumb)
        OnscreenImage(image=self.images['ui_slider_button'],
                      scale=(.07, .07, .08)).reparent_to(self.slider_dof.thumb)
        OnscreenImage(image=self.images['ui_slider_button'],
                      scale=(.07, .07, .08)).reparent_to(self.slider_env_probes.thumb)
        OnscreenImage(image=self.images['ui_slider_button'],
                      scale=(.07, .07, .08)).reparent_to(self.slider_motion_blur.thumb)
        OnscreenImage(image=self.images['ui_slider_button'],
                      scale=(.07, .07, .08)).reparent_to(self.slider_volumetrics.thumb)

        self.lbl_perc_scattering.set_pos(1.6, 0, 0.3)
        self.lbl_perc_sky_ao.set_pos(1.6, 0, 0.2)
        self.lbl_perc_ssr.set_pos(1.6, 0, 0.1)
        self.lbl_perc_forward_shading.set_pos(1.6, 0, 0)
        self.lbl_perc_skin_shading.set_pos(1.6, 0, -0.1)
        self.lbl_perc_pssm.set_pos(1.6, 0, -0.2)
        self.lbl_perc_dof.set_pos(1.6, 0, -0.3)
        self.lbl_perc_env_probes.set_pos(1.6, 0, -0.4)
        self.lbl_perc_motion_blur.set_pos(1.6, 0, -0.5)
        self.lbl_perc_volumetrics.set_pos(1.6, 0, -0.6)

        self.btn_param_defaults.set_pos(1.5, 0, -0.9)
        self.btn_param_accept.set_pos(-0.6, 0, -0.9)

        self.menu_mode = True
        base.active_frame = self.base.frame_int_gfx

    def unload_graphics_menu(self):
        """ Function    : unload_graphics_menu

            Description : Unload Graphics menu.

            Input       : None

            Output      : None

            Return      : None
        """
        if not self.base.frame_int_gfx:
            return

        if hasattr(base, "active_frame"):
            base.active_frame.destroy()

        self.base.build_info.reparent_to(aspect2d)

        if self.game_mode:
            self.base.frame_int_gfx.destroy()
        self.base.frame_int_gfx.destroy()
        self.logo.destroy()
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
        disp_res_dict = self.load_disp_res()
        string = disp_res_dict[i]
        self.lbl_perc_disp_res.setText(string)
        self.save_disp_res_value(string)

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
        # self.save_details_value(i)

    def set_slider_shadows_wrapper(self):
        """ Function    : set_slider_shadows_wrapper

            Description : Wrapper function.

            Input       : None

            Output      : None

            Return      : None
        """
        # Make it int and then str
        i = int(self.slider_shadows['value'])
        shadows_dict = self.load_shadows_value()
        string = shadows_dict[i]
        self.lbl_perc_shadows.setText(string)
        self.save_shadows_value(string)

    def set_slider_postpro_wrapper(self):
        """ Function    : set_slider_postpro_wrapper

            Description : Wrapper function.

            Input       : None

            Output      : None

            Return      : None
        """
        # Make it int and then str
        i = int(self.slider_postpro['value'])
        postpro_dict = self.load_postpro_value()
        string = postpro_dict[i]
        self.lbl_perc_postpro.setText(string)
        self.save_postpro_value(string)

    def set_slider_antial_wrapper(self):
        """ Function    : set_slider_antial_wrapper

            Description : Wrapper function.

            Input       : None

            Output      : None

            Return      : None
        """
        # Make it int and then str
        i = int(self.slider_antial['value'])
        antial_dict = self.load_antial_value()
        string = antial_dict[i]
        self.lbl_perc_antial.setText(string)
        self.save_antial_value(string)

    def set_slider_ao_wrapper(self):
        """ Function    : set_slider_ao_wrapper

            Description : Wrapper function.

            Input       : None

            Output      : None

            Return      : None
        """
        # Make it int and then str
        i = int(self.slider_ao['value'])
        ao_dict = self.load_ao_value()
        string = ao_dict[i]
        self.lbl_perc_ao.setText(string)
        self.save_ao_value(string)

    def set_slider_bloom_wrapper(self):
        """ Function    : set_slider_bloom_wrapper

            Description : Wrapper function.

            Input       : None

            Output      : None

            Return      : None
        """
        # Make it int and then str
        i = int(self.slider_bloom['value'])
        bloom_dict = self.load_bloom_value()
        string = bloom_dict[i]
        self.lbl_perc_bloom.setText(string)
        self.save_bloom_value(string)

    def set_slider_clouds_wrapper(self):
        """ Function    : set_slider_clouds_wrapper

            Description : Wrapper function.

            Input       : None

            Output      : None

            Return      : None
        """
        # Make it int and then str
        i = int(self.slider_clouds['value'])
        clouds_dict = self.load_clouds_value()
        string = clouds_dict[i]
        self.lbl_perc_clouds.setText(string)
        self.save_clouds_value(string)

    def set_slider_cc_wrapper(self):
        """ Function    : set_slider_cc_wrapper

            Description : Wrapper function.

            Input       : None

            Output      : None

            Return      : None
        """
        # Make it int and then str
        i = int(self.slider_cc['value'])
        cc_dict = self.load_cc_value()
        string = cc_dict[i]
        self.lbl_perc_cc.setText(string)
        self.save_color_correction_value(string)

    def set_slider_scattering_wrapper(self):
        """ Function    : set_slider_scattering_wrapper

            Description : Wrapper function.

            Input       : None

            Output      : None

            Return      : None
        """
        # Make it int and then str
        i = int(self.slider_scattering['value'])
        scattering_dict = self.load_scattering_value()
        string = scattering_dict[i]
        self.lbl_perc_scattering.setText(string)
        self.save_scattering_value(string)

    def set_slider_sky_ao_wrapper(self):
        """ Function    : set_slider_sky_ao_wrapper

            Description : Wrapper function.

            Input       : None

            Output      : None

            Return      : None
        """
        # Make it int and then str
        i = int(self.slider_sky_ao['value'])
        sky_ao_dict = self.load_sky_ao_value()
        string = sky_ao_dict[i]
        self.lbl_perc_sky_ao.setText(string)
        self.save_sky_ao_value(string)

    def set_slider_ssr_wrapper(self):
        """ Function    : set_slider_ssr_wrapper

            Description : Wrapper function.

            Input       : None

            Output      : None

            Return      : None
        """
        # Make it int and then str
        i = int(self.slider_ssr['value'])
        ssr_dict = self.load_ssr_value()
        string = ssr_dict[i]
        self.lbl_perc_ssr.setText(string)
        self.save_ssr_value(string)

    def set_slider_forward_shading_wrapper(self):
        """ Function    : set_slider_forward_shading_wrapper

            Description : Wrapper function.

            Input       : None

            Output      : None

            Return      : None
        """
        # Make it int and then str
        i = int(self.slider_forward_shading['value'])
        forward_shading_dict = self.load_forward_shading_value()
        string = forward_shading_dict[i]
        self.lbl_perc_forward_shading.setText(string)
        self.save_forward_shading_value(string)

    def set_slider_skin_shading_wrapper(self):
        """ Function    : set_slider_skin_shading_wrapper

            Description : Wrapper function.

            Input       : None

            Output      : None

            Return      : None
        """
        # Make it int and then str
        i = int(self.slider_skin_shading['value'])
        skin_shading_dict = self.load_skin_shading_value()
        string = skin_shading_dict[i]
        self.lbl_perc_skin_shading.setText(string)
        self.save_skin_shading_value(string)

    def set_slider_pssm_wrapper(self):
        """ Function    : set_slider_pssm_wrapper

            Description : Wrapper function.

            Input       : None

            Output      : None

            Return      : None
        """
        # Make it int and then str
        i = int(self.slider_pssm['value'])
        pssm_dict = self.load_pssm_value()
        string = pssm_dict[i]
        self.lbl_perc_pssm.setText(string)
        self.save_pssm_value(string)

    def set_slider_dof_wrapper(self):
        """ Function    : set_slider_dof_wrapper

            Description : Wrapper function.

            Input       : None

            Output      : None

            Return      : None
        """
        # Make it int and then str
        i = int(self.slider_dof['value'])
        dof_dict = self.load_dof_value()
        string = dof_dict[i]
        self.lbl_perc_dof.setText(string)
        self.save_dof_value(string)

    def set_slider_env_probes_wrapper(self):
        """ Function    : set_slider_env_probes_wrapper

            Description : Wrapper function.

            Input       : None

            Output      : None

            Return      : None
        """
        # Make it int and then str
        i = int(self.slider_env_probes['value'])
        env_probes_dict = self.load_env_probes_value()
        string = env_probes_dict[i]
        self.lbl_perc_env_probes.setText(string)
        self.save_env_probes_value(string)

    def set_slider_motion_blur_wrapper(self):
        """ Function    : set_slider_motion_blur_wrapper

            Description : Wrapper function.

            Input       : None

            Output      : None

            Return      : None
        """
        # Make it int and then str
        i = int(self.slider_motion_blur['value'])
        motion_blur_dict = self.load_motion_blur_value()
        string = motion_blur_dict[i]
        self.lbl_perc_motion_blur.setText(string)
        self.save_motion_blur_value(string)

    def set_slider_volumetrics_wrapper(self):
        """ Function    : set_slider_volumetrics_wrapper

            Description : Wrapper function.

            Input       : None

            Output      : None

            Return      : None
        """
        # Make it int and then str
        i = int(self.slider_volumetrics['value'])
        volumetrics_dict = self.load_volumetrics_value()
        string = volumetrics_dict[i]
        self.lbl_perc_volumetrics.setText(string)
        self.save_volumetrics_value(string)
