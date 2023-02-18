import json
import logging

from os.path import exists
from pathlib import Path

from direct.gui.DirectGui import *
from direct.gui.OnscreenImage import OnscreenImage
from panda3d.core import TransparencyAttrib
from direct.showbase.ShowBaseGlobal import aspect2d
from panda3d.core import FontPool
from panda3d.core import TextNode

from Settings.menu_settings import MenuSettings
from Settings.exit_menu_settings import ExitGame


class ExitMenuUI(ExitGame):
    def __init__(self):
        ExitGame.__init__(self)
        self.base = base
        self.game_dir = base.game_dir
        self.images = base.textures_collector(path="Settings/UI")
        self.fonts = base.fonts_collector()
        self.lng_configs = base.cfg_collector(path="{0}/Configs/Language/".format(self.game_dir))
        self.json = json
        self.pos_X = 0
        self.pos_Y = 0
        self.pos_Z = 0

        self.w = 1
        self.h = 1

        self.node_frame_item = None

        self.rgba_gray_color = (.3, .3, .3, 1.)

        """ Frames """
        self.base.frame_int_exit = None

        """ Frame Sizes """
        # Left, right, bottom, top
        self.base.frame_int_exit_size = [-0.9, 3, -1, 3]

        """ Frame Colors """
        self.frm_opacity = 1

        """ Logo & Ornament Scaling, Positioning """
        self.logo = None
        self.ornament_left = None
        self.ornament_right = None
        self.logo_scale = (0.30, 0.30, 0.30)
        self.logo_pos = (0.3, 0, 0.1)
        self.ornament_scale = (1.40, 0.05, 0.05)
        self.ornament_r_pos = (1.8, 0, -0.1)

        self.ornament_r_snd_pos = (1.8, 0, -0.1)

        """ Buttons, Label Scaling """
        self.lbl_scale = .04
        self.sli_scale = (.4, 0, .2)
        self.btn_scale = .07

        """ Misc """
        self.m_settings = MenuSettings()

        """ Sound MenuUI Objects """
        self.lbl_exit_title = None

        self.btn_param_accept = None
        self.btn_param_back = None
        self.btn_param_decline = None

        # instance of the abstract class
        self.font = FontPool
        self.text = TextNode("TextNode")

        self.logging = logging
        self.logging.basicConfig(filename="{0}/critical.log".format(Path.home()), level=logging.CRITICAL)

        self.cfg_path = self.base.game_cfg
        if exists(self.cfg_path):
            lng_to_load = self.m_settings.input_validate(self.cfg_path, 'lng')
            with open(self.lng_configs['lg_{0}'.format(lng_to_load)], 'r') as json_file:
                self.language = json.load(json_file)

        """ Buttons & Fonts"""
        self.menu_font = self.fonts['OpenSans-Regular']
        self.menu_font_color = (0.8, 0.4, 0, 1)

    def load_exit_menu(self):
        """ Function    : load_exit_menu

            Description : Load Exit menu.

            Input       : None

            Output      : None

            Return      : None
        """
        if self.base.game_instance['current_active_frame']:
            self.base.game_instance['current_active_frame'].destroy()

        self.unload_exit_menu()

        ui_geoms = base.ui_geom_collector()

        maps = base.loader.loadModel(ui_geoms['btn_t_icon'])
        geoms = (maps.find('**/button_any'),
                 maps.find('**/button_pressed'),
                 maps.find('**/button_rollover'))

        self.logo = OnscreenImage(image=self.images['got_upsetting'],
                                  pos=self.logo_pos)
        self.logo.set_transparency(TransparencyAttrib.MAlpha)

        self.ornament_right = OnscreenImage(image=self.images['ornament_kz'],
                                            pos=self.ornament_r_pos, color=(63.9, 63.9, 63.9, 0.5))

        self.base.frame_int_exit = DirectFrame(frameColor=(0, 0, 0, self.frm_opacity),
                                               frameSize=self.base.frame_int_exit_size)
        self.base.frame_int_exit.setPos(self.pos_X, self.pos_Y, self.pos_Z)
        self.base.build_info.reparent_to(self.base.frame_int_exit)

        self.lbl_exit_title = DirectLabel(text=self.language['game_exit_title'],
                                          text_fg=self.menu_font_color,
                                          text_font=self.font.load_font(self.menu_font),
                                          frameColor=(255, 255, 255, 0),
                                          scale=.07, borderWidth=(self.w, self.h),
                                          parent=self.base.frame_int_exit)

        self.btn_param_decline = DirectButton(text=self.language['no_exit_game'],
                                              text_fg=self.menu_font_color,
                                              text_font=self.font.load_font(self.menu_font),
                                              frameColor=(255, 255, 255, 0),
                                              scale=self.btn_scale, borderWidth=(self.w, self.h),
                                              parent=self.base.frame_int_exit,
                                              geom=geoms, geom_scale=(2.5, 0, 2),
                                              clickSound=self.base.sound_gui_click,
                                              command=self.unload_exit_menu)

        self.btn_param_accept = DirectButton(text=self.language['yes_exit_game'],
                                             text_fg=self.menu_font_color,
                                             text_font=self.font.load_font(self.menu_font),
                                             frameColor=(255, 255, 255, 0),
                                             scale=self.btn_scale, borderWidth=(self.w, self.h),
                                             parent=self.base.frame_int_exit,
                                             geom=geoms, geom_scale=(2.5, 0, 2),
                                             clickSound=self.base.sound_gui_click,
                                             command=self.do_accepted_event_wrapper)

        self.logo.reparent_to(self.base.frame_int_exit)
        self.logo.set_scale(0.35, 0.20, 0.20)

        self.ornament_right.reparent_to(self.base.frame_int_exit)
        self.ornament_right.set_scale(self.ornament_scale)
        self.ornament_right.set_hpr(0.0, 0.0, -90.0)
        self.ornament_right.set_transparency(TransparencyAttrib.MAlpha)

        self.ornament_right.set_pos(self.ornament_r_snd_pos)

        self.lbl_exit_title.set_pos(0.3, 0, 0.4)

        self.btn_param_accept.set_pos(0.4, 0, -0.2)
        self.btn_param_decline.set_pos(0.22, 0, -0.2)

        self.base.game_instance['current_active_frame'] = self.base.frame_int_exit

    def unload_exit_menu(self):
        """ Function    : unload_exit_menu

            Description : Unload Exit menu.

            Input       : None

            Output      : None

            Return      : None
        """
        if not self.base.frame_int_exit:
            return

        if self.base.game_instance['current_active_frame']:
            self.base.game_instance['current_active_frame'].destroy()

        self.base.build_info.reparent_to(aspect2d)

        self.base.frame_int_exit.destroy()
        self.logo.destroy()
        self.ornament_right.destroy()

    """ Wrapper functions """
    """ Direct* object doesn't allow passing it's instance directly before it created.
        So, we pass it through wrapper methods
    """
    def do_accepted_event_wrapper(self):
        """ Function    : do_accepted_event_wrapper

            Description : Wrapper function.

            Input       : None

            Output      : None

            Return      : None
        """
        self.unload_exit_menu()
        self.do_accepted_event()
