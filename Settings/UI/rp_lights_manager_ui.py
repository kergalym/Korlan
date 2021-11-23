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
        self.base.frame_rpmgr_size = [-2, 2.5, -1.5, -1.1]
        self.base.frame_scrolled_size = [0.0, 0.7, -0.05, 0.40]
        self.base.frame_scrolled_inner_size = [-0.2, 0.2, -0.00, 0.00]

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
                                           parent=self.base.frame_rpmgr, cursorKeys=1,
                                           command=self.set_node_pos)

                self.inp_hpr = DirectEntry(initialText="HPR",
                                           text_bg=(0, 0, 0, 1),
                                           entryFont=self.font.load_font(self.menu_font),
                                           text_align=TextNode.A_center,
                                           scale=.03, width=7, borderWidth=(self.w, self.h),
                                           parent=self.base.frame_rpmgr, cursorKeys=1,
                                           command=self.set_node_hpr)

                ui_geoms = base.ui_geom_collector()
                if hasattr(base, 'rp_lights') and base.rp_lights and ui_geoms:
                    lights_num = len(base.rp_lights)

                    maps_scrolled_dbtn = base.loader.loadModel(ui_geoms['btn_t_icon'])
                    geoms_scrolled_dbtn = (maps_scrolled_dbtn.find('**/button_any'),
                                           maps_scrolled_dbtn.find('**/button_pressed'),
                                           maps_scrolled_dbtn.find('**/button_rollover'))

                    maps_scrolled_dec = base.loader.loadModel(ui_geoms['btn_t_icon_dec'])
                    geoms_scrolled_dec = (maps_scrolled_dec.find('**/button_any_dec'),
                                          maps_scrolled_dec.find('**/button_pressed_dec'),
                                          maps_scrolled_dec.find('**/button_rollover_dec'))

                    maps_scrolled_inc = base.loader.loadModel(ui_geoms['btn_t_icon_inc'])
                    geoms_scrolled_inc = (maps_scrolled_inc.find('**/button_any_inc'),
                                          maps_scrolled_inc.find('**/button_pressed_inc'),
                                          maps_scrolled_inc.find('**/button_rollover_inc'))

                    btn_list = []
                    for index, light in enumerate(base.rp_lights, 1):
                        btn = DirectButton(text="Light {0}".format(index),
                                           text_fg=(255, 255, 255, 1), relief=2,
                                           text_font=self.font.load_font(self.menu_font),
                                           frameColor=(0, 0, 0, 1),
                                           scale=.03, borderWidth=(self.w, self.h),
                                           geom=geoms_scrolled_dbtn, geom_scale=(15.3, 0, 2),
                                           clickSound=self.base.sound_gui_click,
                                           command=self.pickup_light,
                                           extraArgs=[light])
                        btn_list.append(btn)

                    self.scrolled_list = DirectScrolledList(
                        decButton_pos=(0.35, 0, 0.49),
                        decButton_scale=(5, 1, 0.5),
                        decButton_text="Dec",
                        decButton_text_scale=0.04,
                        decButton_borderWidth=(0, 0),
                        decButton_geom=geoms_scrolled_dec,
                        decButton_geom_scale=0.08,

                        incButton_pos=(0.35, 0, 0.31),
                        incButton_scale=(5, 1, 0.5),
                        incButton_text="Inc",
                        incButton_text_scale=0.04,
                        incButton_borderWidth=(0, 0),
                        incButton_geom=geoms_scrolled_inc,
                        incButton_geom_scale=0.08,

                        frameSize=self.base.frame_scrolled_size,
                        frameColor=(0, 0, 0, 0),
                        numItemsVisible=1,
                        forceHeight=0.11,
                        items=btn_list,
                        itemFrame_frameSize=self.base.frame_scrolled_inner_size,
                        itemFrame_pos=(0.35, 0, 0.4),
                        parent=self.base.frame_rpmgr
                    )

            else:
                if self.base.frame_rpmgr.is_hidden():
                    self.base.frame_rpmgr.show()

            self.lbl_pos.set_pos(-1.0, 0, -1.4)
            self.lbl_hpr.set_pos(0.5, 0, -1.4)
            self.inp_pos.set_pos(-0.5, 0, -1.4)
            self.inp_hpr.set_pos(1.0, 0, -1.4)
            if self.scrolled_list:
                self.scrolled_list.set_pos(1.5, 0, -1.75)

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
            if hasattr(light, "pos"):
                return "{0}, {1}, {2}".format(light.pos[0], light.pos[1], light.pos[2])

    def get_node_hpr(self, light):
        if light:
            if hasattr(light, "direction"):
                return "{0}, {1}, {2}".format(light.direction[0], light.direction[1], light.direction[2])
            else:
                return "HPR"

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
                if hasattr(self.active_light, "pos"):
                    self.active_light.pos = LVecBase3f(int_x, int_y, int_z)

    def set_node_hpr(self, hpr):
        if (hpr
                and isinstance(hpr, str)):
            if self.active_light:
                # We convert pos strings which we get from DirectEntry to integers
                hpr_list = hpr.split(",")
                x, y, z = hpr_list
                int_x = float(x)
                int_y = float(y)
                int_z = float(z)
                if hasattr(self.active_light, "direction"):
                    self.active_light.direction = LVecBase3f(int_x, int_y, int_z)

    def pickup_light(self, light):
        if light:
            self.active_light = light
            if self.inp_pos:
                pos = self.get_node_pos(light=self.active_light)
                hpr = self.get_node_hpr(light=self.active_light)

                if pos:
                    self.inp_pos.enterText(pos)
                if hpr:
                    self.inp_hpr.enterText(hpr)
