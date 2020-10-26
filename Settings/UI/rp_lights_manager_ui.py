import json
from os.path import exists

from direct.showbase.ShowBaseGlobal import aspect2d

from Settings.menu_settings import MenuSettings

from direct.gui.DirectGui import *
from panda3d.core import FontPool, LVecBase3f
from panda3d.core import TextNode
from panda3d.core import WindowProperties
from direct.task.TaskManagerGlobal import taskMgr


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
        self.lbl_pos = None
        self.lbl_hpr = None
        self.inp_pos = None
        self.inp_hpr = None
        self.scrolled_list = None
        self.picked_light_num = None
        self.active_light = None

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
        self.base.frame_scrolled_size = [0.0, 0.7, -0.05, 0.40]
        self.base.frame_scrolled_inner_size = [-0.2, 0.2, -0.20, 0.11]

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

    def update_rp_mgr_task(self, task):
        if base.game_mode is False and base.menu_mode:
            self.clear_ui_rpmgr()
            return task.done

        return task.cont

    def set_ui_rpmgr(self):
        if base.game_mode and base.menu_mode is False:
            props = WindowProperties()
            props.set_cursor_hidden(False)
            self.base.win.request_properties(props)
            self.base.enable_mouse()
            base.is_ui_active = True
            base.is_dev_ui_active = True

            if not self.base.frame_rpmgr:
                self.base.frame_rpmgr = DirectFrame(frameColor=(0, 0, 0, self.frm_opacity),
                                                    frameSize=self.base.frame_rpmgr_size)
                self.base.build_info.reparent_to(self.base.frame_rpmgr)

                self.base.frame_rpmgr.set_pos(self.pos_X, self.pos_Y, self.pos_Z)
                self.base.frame_rpmgr.set_pos(self.pos_int_X, self.pos_int_Y, self.pos_int_Z)

                self.lbl_pos = DirectLabel(text="Position",
                                           text_fg=(255, 255, 255, 0.9),
                                           text_font=self.font.load_font(self.menu_font),
                                           frameColor=(255, 255, 255, 0),
                                           scale=.03, borderWidth=(self.w, self.h),
                                           parent=self.base.frame_rpmgr)

                self.lbl_hpr = DirectLabel(text="Rotation",
                                           text_fg=(255, 255, 255, 0.9),
                                           text_font=self.font.load_font(self.menu_font),
                                           frameColor=(255, 255, 255, 0),
                                           scale=.03, borderWidth=(self.w, self.h),
                                           parent=self.base.frame_rpmgr)

                self.inp_pos = DirectEntry(initialText="Position",
                                           text_bg=(0, 0, 0, 1),
                                           entryFont=self.font.load_font(self.menu_font),
                                           text_align=TextNode.A_center,
                                           scale=.03, width=7, borderWidth=(self.w, self.h),
                                           parent=self.base.frame_rpmgr,
                                           command=self.set_node_pos)

                self.inp_hpr = DirectEntry(initialText="HPR",
                                           text_bg=(0, 0, 0, 1),
                                           entryFont=self.font.load_font(self.menu_font),
                                           text_align=TextNode.A_center,
                                           scale=.03, width=7, borderWidth=(self.w, self.h),
                                           parent=self.base.frame_rpmgr,
                                           command=self.set_node_hpr)

                if hasattr(base, 'rp_lights') and base.rp_lights:
                    lights_num = len(base.rp_lights)
                    btn_list = []
                    for index, light in enumerate(base.rp_lights, 1):
                        btn = DirectButton(text="Light {0}".format(index),
                                           text_fg=(0, 0, 0, 1), relief=2,
                                           text_font=self.font.load_font(self.menu_font),
                                           text_shadow=(255, 255, 255, 1),
                                           frameColor=(255, 255, 255, 0),
                                           scale=self.btn_scale, borderWidth=(self.w, self.h),
                                           clickSound=self.base.sound_gui_click,
                                           command=self.pickup_light,
                                           extraArgs=[light])
                        btn_list.append(btn)

                    self.scrolled_list = DirectScrolledList(
                        decButton_pos=(0.35, 0, 0.53),
                        decButton_text="Dec",
                        decButton_text_scale=0.04,
                        decButton_borderWidth=(0.005, 0.005),

                        incButton_pos=(0.35, 0, 0.15),
                        incButton_text="Inc",
                        incButton_text_scale=0.04,
                        incButton_borderWidth=(0.005, 0.005),

                        frameSize=self.base.frame_scrolled_size,
                        frameColor=(0, 0, 0, 0),
                        numItemsVisible=lights_num,
                        forceHeight=0.11,
                        items=btn_list,
                        itemFrame_frameSize=self.base.frame_scrolled_inner_size,
                        itemFrame_pos=(0.35, 0, 0.4),
                        parent=self.base.frame_rpmgr
                    )

            else:
                if self.base.frame_rpmgr.is_hidden():
                    self.base.frame_rpmgr.show()

            self.lbl_pos.set_pos(-1.0, 0, -1.1)

            self.lbl_hpr.set_pos(0.5, 0, -1.1)

            self.inp_pos.set_pos(-0.5, 0, -1.1)

            self.inp_hpr.set_pos(1.0, 0, -1.1)

            self.scrolled_list.set_pos(1.5, 0, -1.6)

            taskMgr.add(self.update_rp_mgr_task,
                        "update_rp_mgr_task",
                        appendTask=True)

    def clear_ui_rpmgr(self):
        self.base.build_info.reparent_to(aspect2d)
        props = WindowProperties()
        props.set_cursor_hidden(True)
        self.base.disable_mouse()
        self.base.win.request_properties(props)

        base.is_ui_active = False
        base.is_dev_ui_active = False

        if self.base.frame_rpmgr:
            self.base.frame_rpmgr.hide()

    def get_node_pos(self, light):
        if light:
            return "{0}, {1}, {2}".format(light.pos[0], light.pos[1], light.pos[2])

    def get_node_hpr(self):
        pass

    def set_node_pos(self, pos):
        if (pos
                and isinstance(pos, str)):
            if self.active_light:
                # We convert pos strings which we get from DirectEntry to integers
                pos_list = pos.split(",")
                x, y, z = pos_list
                int_x = float(x)
                int_y = float(y)
                int_z = float(z)
                self.active_light.pos = LVecBase3f(int_x, int_y, int_z)

    def set_node_hpr(self):
        pass

    def pickup_light(self, light):
        if light:
            self.active_light = light
            if self.inp_pos:
                pos = self.get_node_pos(light=self.active_light)

                if pos:
                    self.inp_pos.enterText(pos)
