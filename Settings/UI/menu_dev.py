import json
import logging

from os.path import exists
from pathlib import Path

from direct.gui.DirectGui import *
from direct.gui.OnscreenImage import OnscreenImage, TransparencyAttrib
from panda3d.core import FontPool
from panda3d.core import TextNode

# from Settings.UI.menu import Menu
from Settings.menu_settings import MenuSettings
from Settings.menu_settings import DevMode


class MenuDev:
    def __init__(self):
        self.base = base
        self.game_dir = base.game_dir
        self.images = base.textures_collector()
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
        self.base.frame_int_dev = None

        """ Frame Sizes """
        # Left, right, bottom, top
        self.base.frame_int_dev_size = [-3, -0.2, -1, 3]

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

        self.ornament_l_dev_pos = (-1.8, 0, -0.1)
        self.ornament_r_dev_pos = (-0.3, 0, -0.1)

        """ Buttons, Label Scaling """
        self.lbl_scale = .03
        self.btn_scale = .03
        self.inp_scale = .04

        """ Misc """
        self.m_settings = MenuSettings()
        self.dev_mode = DevMode()

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
        # self.menu_font = self.fonts['OpenSans-Regular']
        self.menu_font = self.fonts['JetBrainsMono-Regular']

    def load_dev_mode_menu(self):
        """ Function    : load_dev_mode_menu

            Description : Load Developer Mode menu.

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
                                             command=self.unload_dev_mode_menu)

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

    def unload_dev_mode_menu(self):
        """ Function    : unload_dev_mode_menu

            Description : Unload Developer Mode menu.

            Input       : None

            Output      : None

            Return      : None
        """
        if self.game_mode:
            self.base.frame_int_dev.destroy()
        self.base.frame_int_dev.destroy()
        self.logo.destroy()
        self.ornament_left.destroy()
        self.ornament_right.destroy()

    """ Wrapper functions """
    """ Direct* object doesn't allow passing it's instance directly before it created.
        So, we pass it through wrapper methods
    """

    def get_active_node_wrapper(self):
        """ Function    : get_active_node_wrapper

            Description : Wrapper function.

            Input       : None

            Output      : None

            Return      : None
        """
        self.dev_mode.get_active_node(self.node_frame.getSelectedText())

    def dev_mode_menu_save_changes(self):
        """ Function    : dev_mode_menu_save_changes

            Description : Wrapper function.

            Input       : None

            Output      : None

            Return      : None
        """
        self.dev_mode.save_node_pos()
        self.unload_dev_mode_menu()

    def set_slider_node_exp_wrapper(self):
        """ Function    : set_slider_node_exp_wrapper

            Description : Wrapper function.

            Input       : None

            Output      : None

            Return      : None
        """
        # Make it int and then str
        i = int(self.slider_node_exp['value'])
        node_exp_dict = self.dev_mode.load_node_exp_value()
        string = node_exp_dict[i]
        self.lbl_perc_node_exp.setText(string)
        self.dev_mode.save_node_exp_value(string)

