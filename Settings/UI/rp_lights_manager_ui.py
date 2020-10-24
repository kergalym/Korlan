import json
from os.path import exists

from direct.showbase.ShowBaseGlobal import aspect2d

from Settings.menu_settings import MenuSettings

from direct.gui.DirectGui import *
from panda3d.core import FontPool
from panda3d.core import TextNode
from panda3d.core import WindowProperties


class RPLightsMgrUI:
    def __init__(self):
        self.base = base
        self.game_dir = base.game_dir
        self.images = base.textures_collector(path="{0}/Settings/UI".format(self.game_dir))
        self.fonts = base.fonts_collector()
        self.configs = base.cfg_collector(path="{0}/Settings/UI".format(self.game_dir))
        self.lng_configs = base.cfg_collector(path="{0}/Configs/Language/".format(self.game_dir))
        self.json = json
        # instance of the abstract class
        self.font = FontPool
        self.text = TextNode("TextNode")
        self.sound_gui_click = None
        self.m_settings = MenuSettings()
        self.menu_font = None
        self.cfg_path = None

        """ RP Lights Manager Objects """
        self.base.frame_rpmgr = None
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

        """ Frame Positions """
        self.pos_X = 0
        self.pos_Y = 0
        self.pos_Z = 0
        self.pos_int_X = -0.5
        self.pos_int_Y = 0
        self.pos_int_Z = 0.5
        self.w = 0
        self.h = 0

        """ Frame Sizes """
        # Left, right, bottom, top
        self.base.frame_rpmgr_size = [-2, 2.5, -1.5, -1]

        """ Frame Colors """
        self.frm_opacity = 0.7

        """ Buttons, Label Scaling """
        self.btn_scale = .04

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

    def set_ui_rpmgr(self):
        if base.game_mode and base.menu_mode is False:
            props = WindowProperties()
            props.set_cursor_hidden(False)
            self.base.win.request_properties(props)
            base.is_ui_active = True
            self.base.is_dialog_active = False
            if not self.base.frame_rpmgr:
                self.base.frame_rpmgr = DirectFrame(frameColor=(0, 0, 0, self.frm_opacity),
                                                  frameSize=self.base.frame_rpmgr_size)
                self.base.build_info.reparent_to(self.base.frame_rpmgr)

                self.base.frame_rpmgr.set_pos(self.pos_X, self.pos_Y, self.pos_Z)
                self.base.frame_rpmgr.set_pos(self.pos_int_X, self.pos_int_Y, self.pos_int_Z)

                self.lbl_pos_x = DirectLabel(text=self.language['pos_x'], text_bg=(0, 0, 0, 1),
                                             text_fg=(255, 255, 255, 0.9),
                                             text_font=self.font.load_font(self.menu_font),
                                             frameColor=(255, 255, 255, self.frm_opacity),
                                             scale=.03, borderWidth=(self.w, self.h),
                                             parent=self.base.frame_rpmgr)

                self.lbl_pos_y = DirectLabel(text=self.language['pos_y'], text_bg=(0, 0, 0, 1),
                                             text_fg=(255, 255, 255, 0.9),
                                             text_font=self.font.load_font(self.menu_font),
                                             frameColor=(255, 255, 255, self.frm_opacity),
                                             scale=.03, borderWidth=(self.w, self.h),
                                             parent=self.base.frame_rpmgr)

                self.lbl_pos_z = DirectLabel(text=self.language['pos_z'], text_bg=(0, 0, 0, 1),
                                             text_fg=(255, 255, 255, 0.9),
                                             text_font=self.font.load_font(self.menu_font),
                                             frameColor=(255, 255, 255, self.frm_opacity),
                                             scale=.03, borderWidth=(self.w, self.h),
                                             parent=self.base.frame_rpmgr)

                self.lbl_rot_h = DirectLabel(text=self.language['rot_h'], text_bg=(0, 0, 0, 1),
                                             text_fg=(255, 255, 255, 0.9),
                                             text_font=self.font.load_font(self.menu_font),
                                             frameColor=(255, 255, 255, self.frm_opacity),
                                             scale=.03, borderWidth=(self.w, self.h),
                                             parent=self.base.frame_rpmgr)

                self.lbl_rot_p = DirectLabel(text=self.language['rot_p'], text_bg=(0, 0, 0, 1),
                                             text_fg=(255, 255, 255, 0.9),
                                             text_font=self.font.load_font(self.menu_font),
                                             frameColor=(255, 255, 255, self.frm_opacity),
                                             scale=.03, borderWidth=(self.w, self.h),
                                             parent=self.base.frame_rpmgr)

                self.lbl_rot_r = DirectLabel(text=self.language['rot_r'], text_bg=(0, 0, 0, 1),
                                             text_fg=(255, 255, 255, 0.9),
                                             text_font=self.font.load_font(self.menu_font),
                                             frameColor=(255, 255, 255, self.frm_opacity),
                                             scale=.03, borderWidth=(self.w, self.h),
                                             parent=self.base.frame_rpmgr)

                dev = self.m_settings.input_validate(self.cfg_path, 'dev')
                self.inp_pos_x = DirectEntry(initialText=dev['Debug']['player_pos_x'],
                                             text_bg=(0, 0, 0, 1),
                                             entryFont=self.font.load_font(self.menu_font),
                                             text_align=TextNode.A_center,
                                             scale=.03, width=7, borderWidth=(self.w, self.h),
                                             parent=self.base.frame_rpmgr,
                                             command=self.set_node_pos_x)

                self.inp_pos_y = DirectEntry(initialText=dev['Debug']['player_pos_y'],
                                             text_bg=(0, 0, 0, 1),
                                             entryFont=self.font.load_font(self.menu_font),
                                             text_align=TextNode.A_center,
                                             scale=.03, width=7, borderWidth=(self.w, self.h),
                                             parent=self.base.frame_rpmgr,
                                             command=self.set_node_pos_y)

                self.inp_pos_z = DirectEntry(initialText=dev['Debug']['player_pos_z'],
                                             text_bg=(0, 0, 0, 1),
                                             entryFont=self.font.load_font(self.menu_font),
                                             text_align=TextNode.A_center,
                                             scale=.03, width=7, borderWidth=(self.w, self.h),
                                             parent=self.base.frame_rpmgr,
                                             command=self.set_node_pos_z)

                self.inp_rot_h = DirectEntry(initialText=dev['Debug']['player_rot_h'],
                                             text_bg=(0, 0, 0, 1),
                                             entryFont=self.font.load_font(self.menu_font),
                                             text_align=TextNode.A_center,
                                             scale=.03, width=7, borderWidth=(self.w, self.h),
                                             parent=self.base.frame_rpmgr,
                                             command=self.set_node_rot_h)

                self.inp_rot_p = DirectEntry(initialText=dev['Debug']['player_rot_p'],
                                             text_bg=(0, 0, 0, 1),
                                             entryFont=self.font.load_font(self.menu_font),
                                             text_align=TextNode.A_center,
                                             scale=.03, width=7, borderWidth=(self.w, self.h),
                                             parent=self.base.frame_rpmgr,
                                             command=self.set_node_rot_p)

                self.inp_rot_r = DirectEntry(initialText=dev['Debug']['player_rot_r'],
                                             text_bg=(0, 0, 0, 1),
                                             entryFont=self.font.load_font(self.menu_font),
                                             text_align=TextNode.A_center,
                                             scale=.03, width=7, borderWidth=(self.w, self.h),
                                             parent=self.base.frame_rpmgr,
                                             command=self.set_node_rot_r)

                # Show actor perspective from player camera
                self.base.camera.set_pos(6, 9, 2)
                self.base.camera.set_hpr(-90, 0, 0)
                self.base.cam.set_y(5.5)

            else:
                if self.base.frame_rpmgr.is_hidden():
                    self.base.frame_rpmgr.show()

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

            self.base.is_dialog_active = True

    def clear_ui_rpmgr(self):
        self.base.build_info.reparent_to(aspect2d)
        props = WindowProperties()
        props.set_cursor_hidden(True)
        self.base.win.request_properties(props)
        base.is_ui_active = False

        if self.base.frame_rpmgr:
            self.base.frame_rpmgr.hide()
            self.base.is_dialog_active = False
            self.base.cam.set_y(0)

    def btn_wrapper(self, index, behaviors, behavior_name):
        if behaviors and behavior_name:
            if index == 0:
                self.clear_ui_rpmgr()
            elif index == 1:
                self.clear_ui_rpmgr()
            else:
                self.clear_ui_rpmgr()

    def set_node_pos_x(self):
        pass

    def set_node_pos_y(self):
        pass

    def set_node_pos_z(self):
        pass

    def set_node_rot_h(self):
        pass

    def set_node_rot_p(self):
        pass

    def set_node_rot_r(self):
        pass
