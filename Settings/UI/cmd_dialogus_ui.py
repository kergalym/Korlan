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
        self.frm_opacity = 0.9

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

    def set_ui_dialog(self, dialog, txt_interval):
        if base.game_mode and base.menu_mode is False:
            props = WindowProperties()
            props.set_cursor_hidden(False)
            self.base.win.request_properties(props)
            base.is_ui_active = True

            if not self.base.frame_dlg:
                self.base.frame_dlg = DirectFrame(frameColor=(0, 0, 0, self.frm_opacity),
                                                  frameSize=self.base.frame_dlg_size)
                self.base.build_info.reparent_to(self.base.frame_dlg)

                self.base.frame_dlg.set_pos(self.pos_X, self.pos_Y, self.pos_Z)
                self.base.frame_dlg.set_pos(self.pos_int_X, self.pos_int_Y, self.pos_int_Z)

                ui_geoms = base.ui_geom_collector()
                maps = self.base.loader.loadModel(ui_geoms['radbtn_t_icon'])
                geoms = (maps.find('**/radbutton'), maps.find('**/radbutton_pressed'))

                if (dialog and isinstance(dialog, dict)
                        and txt_interval and isinstance(txt_interval, list)):
                    radbuttons = []
                    dlg_count = range(len(dialog))
                    for elem, interval, index in zip(dialog, txt_interval, dlg_count):
                        text = dialog[elem]
                        OnscreenText(text=text, pos=(-1.0, interval),
                                     fg=(255, 255, 255, 1), scale=.03,
                                     parent=self.base.frame_dlg)
                        radbuttons.append(DirectRadioButton(text='', variable=[index], value=[index],
                                                            parent=self.base.frame_dlg, scale=.03,
                                                            clickSound=self.base.sound_gui_click,
                                                            pos=(-1.1, 0, interval),
                                                            command=self.rad_cmd_wrapper,
                                                            extraArgs=[index],
                                                            color=(63.9, 63.9, 63.9, 1),
                                                            boxGeom=geoms, boxPlacement='left',
                                                            frameColor=(255, 255, 255, 0)))

                    if radbuttons:
                        for radbutton in radbuttons:
                            radbutton.setOthers(radbuttons)

            else:
                if self.base.frame_dlg.is_hidden():
                    self.base.frame_dlg.show()

    def clear_ui_dialog(self):
        self.base.build_info.reparent_to(aspect2d)
        props = WindowProperties()
        props.set_cursor_hidden(True)
        self.base.win.request_properties(props)
        base.is_ui_active = False

        if self.base.frame_dlg:
            self.base.frame_dlg.hide()

    def rad_cmd_wrapper(self, index):
        if hasattr(self.base, 'npc_commands') and self.base.npc_commands:
            if index == 0:
                self.clear_ui_dialog()
                self.base.npc_commands(command="follow")
            elif index == 1:
                self.clear_ui_dialog()
                self.base.npc_commands(command="stay")
            else:
                self.clear_ui_dialog()
