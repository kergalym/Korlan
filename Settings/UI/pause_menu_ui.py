import json
import logging

from os.path import exists
from pathlib import Path

from direct.gui.DirectGui import *
from direct.gui.OnscreenImage import OnscreenImage, TransparencyAttrib
from direct.showbase.ShowBaseGlobal import aspect2d
from panda3d.core import FontPool, WindowProperties
from panda3d.core import TextNode

from Settings.menu_settings import MenuSettings
from Settings.UI.game_menu_ui import GameMenuUI
from Settings.UI.graphics_menu_ui import GraphicsMenuUI
from Settings.UI.sound_menu_ui import SoundMenuUI
from Settings.UI.keymap_menu_ui import KeymapMenuUI
from Settings.UI.lang_menu_ui import LangMenuUI
from Settings.UI.exit_menu_ui import ExitMenuUI


class PauseMenuUI(MenuSettings):
    def __init__(self):
        MenuSettings.__init__(self)
        self.base = base
        self.game_dir = base.game_dir
        self.images = base.textures_collector(path="Settings/UI")
        self.fonts = base.fonts_collector()
        self.lng_configs = base.cfg_collector(path="{0}/Configs/Language/".format(self.game_dir))
        self.json = json
        self.pos_X = 0
        self.pos_Y = 0
        self.pos_Z = 0

        self.w = 0
        self.h = 0

        self.node_frame_item = None

        self.rgba_gray_color = (.3, .3, .3, 1.)
        self.pause_mode = 0

        """ Frames """
        self.base.frame_int_pause = None

        """ Frame Sizes """
        # Left, right, bottom, top
        self.base.frame_int_pause_size = [-3, -0.9, -1, 3]

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

        """ Buttons, Label Scaling """
        self.lbl_scale = .03
        self.btn_scale = .04
        self.inp_scale = .04

        """ Misc """
        self.ui_game = GameMenuUI()
        self.ui_gfx = GraphicsMenuUI()
        self.ui_snd = SoundMenuUI()
        self.ui_kmp = KeymapMenuUI()
        self.ui_lng = LangMenuUI()
        self.ui_exit_game = ExitMenuUI()

        """ Options MenuUI Objects """
        self.btn_game = None
        self.btn_gfx = None
        self.btn_sound = None
        self.btn_language = None
        self.btn_exit_game = None
        self.btn_keymap = None
        self.btn_continue = None

        # instance of the abstract class
        self.font = FontPool
        self.text = TextNode("TextNode")

        self.logging = logging
        self.logging.basicConfig(filename="{0}/critical.log".format(Path.home()), level=logging.CRITICAL)

        self.cfg_path = self.base.game_cfg
        if exists(self.cfg_path):
            lng_to_load = self.input_validate(self.cfg_path, 'lng')
            with open(self.lng_configs['lg_{0}'.format(lng_to_load)], 'r') as json_file:
                self.language = json.load(json_file)

        self.base.game_instance['esc_mode'] = False

        """ Buttons & Fonts"""
        self.menu_font = self.fonts['OpenSans-Regular']

    def load_pause_menu(self):
        """ Function    : load_pause_menu

            Description : Load Pause menu.

            Input       : None

            Output      : None

            Return      : None
        """
        if self.base.game_instance['loading_is_done'] == 1:
            if self.pause_mode == 1:
                return False

            if self.base.game_instance['is_dialog_active']:
                return False

            if self.base.game_instance['current_active_frame']:
                self.base.game_instance['current_active_frame'].destroy()

            ui_geoms = base.ui_geom_collector()
            maps = base.loader.loadModel(ui_geoms['btn_t_icon'])
            geoms = (maps.find('**/button_any'),
                     maps.find('**/button_pressed'),
                     maps.find('**/button_rollover'))

            # close inventory
            if self.base.game_instance['ui_mode']:
                base.messenger.send("close_sheet")

            self.base.game_instance['ui_mode'] = True
            self.pause_mode = 1
            self.base.game_instance['esc_mode'] = True
            win_props = WindowProperties()
            win_props.set_cursor_hidden(False)
            self.base.win.request_properties(win_props)

            self.logo = OnscreenImage(image=self.images['korlan_logo_tengri'],
                                      pos=self.logo_pos)
            self.ornament_left = OnscreenImage(image=self.images['ornament_kz'],
                                               pos=self.ornament_l_pos, color=(63.9, 63.9, 63.9, 0.5))
            self.ornament_right = OnscreenImage(image=self.images['ornament_kz'],
                                                pos=self.ornament_r_pos, color=(63.9, 63.9, 63.9, 0.5))

            self.base.frame_int_pause = DirectFrame(frameColor=(0, 0, 0, self.frm_opacity),
                                                    frameSize=self.base.frame_int_pause_size)
            self.base.frame_int_pause.setPos(self.pos_X, self.pos_Y, self.pos_Z)
            self.base.build_info.reparent_to(self.base.frame_int_pause)

            self.btn_continue = DirectButton(text=self.language['continue'],
                                             text_fg=(255, 255, 255, 0.9),
                                             text_font=self.font.load_font(self.menu_font),
                                             frameColor=(0, 0, 0, self.frm_opacity),
                                             scale=self.btn_scale, borderWidth=(self.w, self.h),
                                             parent=self.base.frame_int_pause,
                                             geom=geoms, geom_scale=(15.3, 0, 2),
                                             clickSound=self.base.sound_gui_click,
                                             command=self.unload_pause_menu)

            self.btn_game = DirectButton(text=self.language['game'],
                                         text_fg=(255, 255, 255, 0.9),
                                         text_font=self.font.load_font(self.menu_font),
                                         frameColor=(0, 0, 0, self.frm_opacity),
                                         scale=self.btn_scale, borderWidth=(self.w, self.h),
                                         parent=self.base.frame_int_pause,
                                         geom=geoms, geom_scale=(15.3, 0, 2),
                                         clickSound=self.base.sound_gui_click,
                                         command=self.ui_game.load_game_menu)

            self.btn_gfx = DirectButton(text=self.language['graphics'],
                                        text_fg=(255, 255, 255, 0.9),
                                        text_font=self.font.load_font(self.menu_font),
                                        frameColor=(0, 0, 0, self.frm_opacity),
                                        scale=self.btn_scale, borderWidth=(self.w, self.h),
                                        parent=self.base.frame_int_pause,
                                        geom=geoms, geom_scale=(15.3, 0, 2),
                                        clickSound=self.base.sound_gui_click,
                                        command=self.ui_gfx.load_graphics_menu)

            self.btn_sound = DirectButton(text=self.language['sound'],
                                          text_fg=(255, 255, 255, 0.9),
                                          text_font=self.font.load_font(self.menu_font),
                                          frameColor=(0, 0, 0, self.frm_opacity),
                                          scale=self.btn_scale, borderWidth=(self.w, self.h),
                                          parent=self.base.frame_int_pause,
                                          geom=geoms, geom_scale=(15.3, 0, 2),
                                          clickSound=self.base.sound_gui_click,
                                          command=self.ui_snd.load_sound_menu)

            self.btn_language = DirectButton(text=self.language['language'],
                                             text_fg=(255, 255, 255, 0.9),
                                             text_font=self.font.load_font(self.menu_font),
                                             frameColor=(0, 0, 0, self.frm_opacity),
                                             scale=self.btn_scale, borderWidth=(self.w, self.h),
                                             parent=self.base.frame_int_pause,
                                             geom=geoms, geom_scale=(15.3, 0, 2),
                                             clickSound=self.base.sound_gui_click,
                                             command=self.ui_lng.load_language_menu)

            self.btn_keymap = DirectButton(text=self.language['keymap'],
                                           text_fg=(255, 255, 255, 0.9),
                                           text_font=self.font.load_font(self.menu_font),
                                           frameColor=(0, 0, 0, self.frm_opacity),
                                           scale=self.btn_scale, borderWidth=(self.w, self.h),
                                           parent=self.base.frame_int_pause,
                                           geom=geoms, geom_scale=(15.3, 0, 2),
                                           clickSound=self.base.sound_gui_click,
                                           command=self.ui_kmp.load_keymap_menu)

            self.btn_exit_game = DirectButton(text=self.language['exit_game'],
                                              text_fg=(255, 255, 255, 0.9),
                                              text_font=self.font.load_font(self.menu_font),
                                              frameColor=(0, 0, 0, self.frm_opacity),
                                              scale=self.btn_scale, borderWidth=(self.w, self.h),
                                              parent=self.base.frame_int_pause,
                                              geom=geoms, geom_scale=(15.3, 0, 2),
                                              clickSound=self.base.sound_gui_click,
                                              command=self.ui_exit_game.load_exit_menu)

            self.btn_continue.set_pos(-1.4, 0, 0)
            self.btn_game.set_pos(-1.4, 0, -0.1)
            self.btn_gfx.set_pos(-1.4, 0, -0.2)
            self.btn_sound.set_pos(-1.4, 0, -0.3)
            self.btn_language.set_pos(-1.4, 0, -0.4)
            self.btn_keymap.set_pos(-1.4, 0, -0.5)
            self.btn_exit_game.set_pos(-1.4, 0, -0.6)
            self.logo.reparent_to(self.base.frame_int_pause)
            self.logo.set_scale(self.logo_scale)

            self.ornament_right.reparent_to(self.base.frame_int_pause)
            self.ornament_right.set_scale(self.ornament_scale)
            self.ornament_right.set_hpr(0.0, 0.0, -90.0)
            self.ornament_left.reparent_to(self.base.frame_int_pause)
            self.ornament_left.set_scale(self.ornament_scale)
            self.ornament_left.set_hpr(0.0, 0.0, -90.0)
            self.ornament_right.set_transparency(TransparencyAttrib.MAlpha)
            self.ornament_left.set_transparency(TransparencyAttrib.MAlpha)

            # We make unload_pause_menu() method accessible
            # to unload via ExitGame.do_accepted_event()
            self.base.shared_functions['unload_pause_menu'] = self.unload_pause_menu

    def unload_pause_menu(self):
        """ Function    : unload_pause_menu

            Description : Unload Pause menu.

            Input       : None

            Output      : None

            Return      : None
        """
        if not self.base.frame_int_pause:
            return False

        self.base.build_info.reparent_to(aspect2d)

        if self.base.game_instance['current_active_frame']:
            self.base.game_instance['current_active_frame'].destroy()

            if self.base.game_instance['dev_ui_mode']:
                self.base.game_instance['ui_mode'] = True
            else:
                self.base.game_instance['ui_mode'] = False

        self.base.frame_int_pause.destroy()
        self.logo.destroy()
        self.ornament_left.destroy()
        self.ornament_right.destroy()

        win_props = WindowProperties()
        win_props.set_cursor_hidden(True)
        self.base.win.request_properties(win_props)

        if self.base.game_instance['dev_ui_mode']:
            win_props.set_cursor_hidden(False)
            self.base.win.request_properties(win_props)
            self.base.game_instance['ui_mode'] = True
        else:
            win_props.set_cursor_hidden(True)
            self.base.win.request_properties(win_props)
            self.base.game_instance['ui_mode'] = False

        self.pause_mode = 0
        self.base.game_instance['esc_mode'] = False
        self.base.game_instance['ui_mode'] = False
        self.base.game_instance['menu_mode'] = False
