import json
from os.path import exists

from direct.showbase.ShowBaseGlobal import render2d

from Engine.Actors.Player.inventory import Inventory
from Settings.menu_settings import MenuSettings

from direct.gui.DirectGui import *
from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.OnscreenImage import TransparencyAttrib
from panda3d.core import FontPool
from panda3d.core import TextNode
from panda3d.core import WindowProperties


class PlayerMenuUI(Inventory):

    def __init__(self):
        Inventory.__init__(self)
        self.base = base
        self.game_dir = base.game_dir
        self.images = base.textures_collector(path="{0}/Settings/UI".format(self.game_dir))
        self.inv_images = base.textures_collector(path="{0}/Assets".format(self.game_dir))
        self.fonts = base.fonts_collector()
        self.configs = base.cfg_collector(path="{0}/Settings/UI".format(self.game_dir))
        self.lng_configs = base.cfg_collector(path="{0}/Configs/Language/".format(self.game_dir))
        self.json = json
        # instance of the abstract class
        self.font = FontPool
        self.text = TextNode("TextNode")
        self.m_settings = MenuSettings()
        self.menu_font = None
        self.cfg_path = None

        """ Frame """
        self.pos_X = 0
        self.pos_Y = 0
        self.pos_Z = 0
        self.pos_int_X = -0.5
        self.pos_int_Y = 0
        self.pos_int_Z = 0.5
        self.w = 0
        self.h = 0
        self.base.frame_inv_int = None
        self.base.frame_inv = None

        """ Frame Sizes """
        # Left, right, bottom, top
        self.base.frame_inv_int_canvas_size = [-2, 2, -2, 2]
        self.base.frame_inv_int_size = [-.5, .2, -1.3, .5]

        self.base.frame_inv_size = [-3, 0.5, -1, 3]

        """ Frame Colors """
        self.frm_opacity = 1

        self.pic = None
        self.pic_left = None
        self.pic_right = None

        """ Buttons, Label Scaling """
        self.lbl_scale = .03
        self.btn_scale = .03
        self.btn_param_accept = None
        self.btn_param_decline = None

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

        self.base.frame_inv = DirectFrame(frameColor=(0, 0, 0, self.frm_opacity),
                                          frameSize=self.base.frame_inv_size)

        self.base.frame_inv_int = DirectScrolledFrame(frameColor=(0, 0, 0, self.frm_opacity),
                                                      frameSize=self.base.frame_inv_int_size,
                                                      canvasSize=self.base.frame_inv_int_canvas_size,
                                                      scrollBarWidth=0.03,
                                                      autoHideScrollBars=True)
        self.pic_body_inv = OnscreenImage(image=self.images['body_inventory'])
        """
        self.pic_left = OnscreenImage(image='{0}/Settings/UI/ui_tex/ornament_kz.png'.format(self.game_dir),
                                      pos='', color=(63.9, 63.9, 63.9, 0.5))
        self.pic_right = OnscreenImage(image='{0}/Settings/UI/ui_tex/ornament_kz.png'.format(self.game_dir),
                                       pos='', color=(63.9, 63.9, 63.9, 0.5))
        """

        self.btn_param_decline = DirectButton(text="Cancel", text_bg=(0, 0, 0, 1),
                                              text_fg=(255, 255, 255, 0.9),
                                              text_font=self.font.load_font(self.menu_font),
                                              frameColor=(255, 255, 255, self.frm_opacity),
                                              scale=self.btn_scale, borderWidth=(self.w, self.h),
                                              parent=self.base.frame_inv,
                                              command=self.clear_ui_inventory)

        self.btn_param_accept = DirectButton(text="OK", text_bg=(0, 0, 0, 0.9),
                                             text_fg=(255, 255, 255, 0.9),
                                             text_font=self.font.load_font(self.menu_font),
                                             frameColor=(255, 255, 255, self.frm_opacity),
                                             scale=self.btn_scale, borderWidth=(self.w, self.h),
                                             parent=self.base.frame_inv,
                                             command=self.clear_ui_inventory)

        self.base.frame_inv.set_pos(self.pos_X, self.pos_Y, self.pos_Z)
        self.base.frame_inv_int.set_pos(self.pos_int_X, self.pos_int_Y, self.pos_int_Z)
        self.base.frame_inv_int.reparent_to(self.base.frame_inv)
        self.base.frame_inv_int.set_pos(-1.3, 0, 0.5)
        self.base.frame_inv.set_pos(0, 0, 0)

        self.pic_body_inv.reparent_to(self.base.frame_inv)
        self.pic_body_inv.set_transparency(TransparencyAttrib.MAlpha)
        self.pic_body_inv.set_scale(1.5, 1.5, 0.9)
        self.pic_body_inv.set_pos(-0.4, 0, 0)

        # self.pic_right.reparent_to(self.base.frame_inv)
        # self.pic_right.set_scale(0.33, 0.30, 0.30)
        # self.pic_right.set_hpr(0.0, 0.0, -90.0)
        # self.pic_left.reparent_to(self.base.frame_inv)
        # self.pic_left.set_scale(0.33, 0.30, 0.30)
        # self.pic_left.set_hpr(0.0, 0.0, -90.0)
        # self.pic_right.set_transparency(TransparencyAttrib.MAlpha)
        # self.pic_left.set_transparency(TransparencyAttrib.MAlpha)

        self.btn_param_decline.set_pos(0.1, 0, -0.9)
        self.btn_param_accept.set_pos(-1.6, 0, -0.9)

        self.base.frame_inv.hide()

    def clear_ui_inventory(self):
        self.base.frame_inv.hide()
        props = WindowProperties()
        props.set_cursor_hidden(True)
        self.base.win.request_properties(props)
        base.is_ui_active = False

    def set_ui_inventory(self):
        if self.base.frame_inv.is_hidden():
            self.base.frame_inv.show()
            props = WindowProperties()
            props.set_cursor_hidden(False)
            self.base.win.request_properties(props)
            base.is_ui_active = True
        else:
            self.clear_ui_inventory()

    def show_inventory_data_task(self, task):
        if hasattr(base, "in_use_item_name"):
            if (not base.in_use_item_name and
                    not render2d.find("**/{0}".format(self.item)).is_empty()):
                render2d.find("**/{0}".format(self.item)).remove_node()

            item = base.in_use_item_name
            items = self.get_item(item)

            if items and isinstance(items, list):
                for i, item in enumerate(items, 1):
                    if item and render2d.find("**/{0}".format(item)).is_empty():
                        pos_x = 0
                        pos_z = 0
                        if i == 1:
                            pos_x = -1.3
                            pos_z = 0.65
                        elif i == 2:
                            pos_x = -1.0
                            pos_z = 0.65
                        elif i == 3:
                            pos_x = -0.7
                            pos_z = 0.65
                        elif i == 4:
                            pos_x = -1.3
                            pos_z = 0.45
                        elif i == 5:
                            pos_x = -1.0
                            pos_z = 0.45
                        elif i == 6:
                            pos_x = -0.7
                            pos_z = 0.45
                        elif i == 7:
                            pos_x = -1.3
                            pos_z = 0.15
                        elif i == 8:
                            pos_x = -1.0
                            pos_z = 0.15
                        print(self.inv_images)
                        t = OnscreenText(text="",
                                         pos=(pos_x, pos_z),
                                         scale=0.0,
                                         fg=(255, 255, 255, 0.9),
                                         font=self.font.load_font(self.menu_font),
                                         align=TextNode.ALeft,
                                         mayChange=True)
                        t.reparent_to(self.base.frame_inv_int)
                        t.setText(item)
                        t.set_name(item)
                        t.set_scale(0.4)

            if base.game_mode is False and base.menu_mode:
                return task.done

        return task.cont
