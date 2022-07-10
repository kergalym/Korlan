import json
from os.path import exists

from direct.showbase.ShowBaseGlobal import aspect2d

from Settings.menu_settings import MenuSettings

from direct.gui.DirectGui import *
from panda3d.core import FontPool
from panda3d.core import TextNode
from panda3d.core import WindowProperties


class CmdDialogusUI:
    def __init__(self):
        self.base = base
        self.game_dir = base.game_dir
        self.images = base.textures_collector(path="Settings/UI")
        self.fonts = base.fonts_collector()
        self.lng_configs = base.cfg_collector(path="{0}/Configs/Language/".format(self.game_dir))
        self.json = json
        # instance of the abstract class
        self.font = FontPool
        self.text = TextNode("TextNode")
        self.sound_gui_click = None
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
        self.base.frame_dlg = None

        """ Frame Sizes """
        # Left, right, bottom, top
        self.base.frame_dlg_size = [-2, 2.5, -1.5, -1]

        """ Frame Colors """
        self.frm_opacity = 0.7

        """ Buttons, Label Scaling """
        self.btn_scale = .04

        self.cfg_path = self.base.game_cfg
        if exists(self.cfg_path):
            lng_to_load = self.m_settings.input_validate(self.cfg_path, 'lng')
            with open(self.lng_configs['lg_{0}'.format(lng_to_load)], 'r') as json_file:
                self.language = json.load(json_file)

        """ Buttons & Fonts"""
        self.menu_font = self.fonts['OpenSans-Regular']

    def set_ui_dialog(self, dialog, txt_interval, behaviors, behavior_name):
        if not self.base.game_instance['menu_mode']:
            self.base.win_props.set_cursor_hidden(False)
            self.base.win.request_properties(self.base.win_props)
            self.base.game_instance['ui_mode'] = True
            self.base.game_instance['is_dialog_active'] = False
            if not self.base.frame_dlg:
                self.base.frame_dlg = DirectFrame(frameColor=(0, 0, 0, self.frm_opacity),
                                                  frameSize=self.base.frame_dlg_size)
                self.base.build_info.reparent_to(self.base.frame_dlg)

                self.base.frame_dlg.set_pos(self.pos_X, self.pos_Y, self.pos_Z)
                self.base.frame_dlg.set_pos(self.pos_int_X, self.pos_int_Y, self.pos_int_Z)

                if (dialog and isinstance(dialog, dict)
                        and txt_interval and isinstance(txt_interval, list)):
                    dlg_count = range(len(dialog))
                    for elem, interval, index in zip(dialog, txt_interval, dlg_count):
                        text = "{0}. {1}".format(index + 1, dialog[elem])
                        DirectButton(text=text, parent=self.base.frame_dlg,
                                     pos=(1.1, 0, interval),
                                     text_fg=(255, 255, 255, 0),
                                     text_bg=(0, 0, 0, 0),
                                     text_font=self.font.load_font(self.menu_font),
                                     text_shadow=(255, 255, 255, 1),
                                     frameColor=(255, 255, 255, 0),
                                     scale=self.btn_scale, borderWidth=(self.w, self.h),
                                     clickSound=self.base.sound_gui_click,
                                     command=self.btn_cmd_wrapper,
                                     extraArgs=[index, behaviors, behavior_name])

                        # Show actor perspective from player camera
                        self.base.camera.set_pos(6, 9, 2)
                        self.base.camera.set_hpr(-90, 0, 0)
                        self.base.cam.set_y(5.5)
            else:
                if self.base.frame_dlg.is_hidden():
                    self.base.frame_dlg.show()
                    # Show actor perspective from player camera
                    self.base.camera.set_pos(6, 9, 2)
                    self.base.camera.set_hpr(-90, 0, 0)
                    self.base.cam.set_y(5.5)

        self.base.game_instance['is_dialog_active'] = True

    def clear_ui_dialog(self):
        self.base.build_info.reparent_to(aspect2d)
        self.base.win_props.set_cursor_hidden(True)
        self.base.win.request_properties(self.base.win_props)
        base.game_instance['ui_mode'] = False

        if self.base.frame_dlg:
            self.base.frame_dlg.hide()
            self.base.game_instance['is_dialog_active'] = False
            self.base.cam.set_y(0)

    def btn_cmd_wrapper(self, index, behaviors, behavior_name):
        if behaviors and behavior_name:
            if index == 0:
                self.clear_ui_dialog()
                behaviors.resume_ai(behavior_name)
            elif index == 1:
                self.clear_ui_dialog()
                behaviors.pause_ai(behavior_name)
            else:
                self.clear_ui_dialog()
