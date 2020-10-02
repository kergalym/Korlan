import json
import logging

from os.path import exists
from pathlib import Path

from direct.gui.DirectGui import *
from direct.gui.OnscreenImage import OnscreenImage, TransparencyAttrib
from panda3d.core import FontPool
from panda3d.core import TextNode

from Settings.menu_settings import MenuSettings
from Settings.kmp_menu_settings import Keymap


class KeymapMenuUI(Keymap):
    def __init__(self):
        Keymap.__init__(self)
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
        self.base.frame_int_keymap = None

        """ Frame Sizes """
        # Left, right, bottom, top
        self.base.frame_int_keymap_size = [-0.9, 3, -1, 3]

        """ Frame Colors """
        self.frm_opacity = 0.9

        """ Logo & Ornament Scaling, Positioning """
        self.logo = None
        self.ornament_right = None
        self.logo_scale = (0.33, 0.30, 0.30)
        self.logo_pos = (-0.3, 0, 0.6)
        self.ornament_scale = (1.40, 0.05, 0.05)
        self.ornament_r_pos = (1.8, 0, -0.1)

        self.ornament_r_kmp_pos = (1.8, 0, -0.1)

        """ Buttons, Label Scaling """
        self.lbl_scale = .04
        self.btn_scale = .04
        self.inp_scale = .05

        """ Misc """
        self.m_settings = MenuSettings()

        """ Key mapping MenuUI Objects """
        self.lbl_keymap_title = None
        self.lbl_forward = None
        self.lbl_backward = None
        self.lbl_left = None
        self.lbl_right = None
        self.lbl_run = None
        self.lbl_crouch = None
        self.lbl_jump = None
        self.lbl_use = None
        self.lbl_attack = None
        self.lbl_h_attack = None
        self.lbl_f_attack = None
        self.lbl_block = None
        self.lbl_sword = None
        self.lbl_bow = None
        self.lbl_tengri = None
        self.lbl_umay = None

        self.inp_forward = None
        self.inp_backward = None
        self.inp_left = None
        self.inp_right = None
        self.inp_run = None
        self.inp_crouch = None
        self.inp_jump = None
        self.inp_use = None
        self.inp_attack = None
        self.inp_h_attack = None
        self.inp_f_attack = None
        self.inp_block = None
        self.inp_sword = None
        self.inp_bow = None
        self.inp_tengri = None
        self.inp_umay = None

        self.btn_param_accept = None
        self.btn_param_back = None
        self.btn_param_decline = None
        self.btn_param_defaults = None

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

    def load_keymap_menu(self):
        """ Function    : load_keymap_menu

            Description : Load Keymap menu.

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

        self.unload_keymap_menu()
        
        self.logo = OnscreenImage(image=self.images['kbdm_icon'],
                                  pos=self.logo_pos)
        self.logo.set_transparency(TransparencyAttrib.MAlpha)
        self.ornament_right = OnscreenImage(image=self.images['ornament_kz'],
                                            pos=self.ornament_r_pos, color=(63.9, 63.9, 63.9, 0.5))

        self.base.frame_int_keymap = DirectFrame(frameColor=(0, 0, 0, self.frm_opacity),
                                                 frameSize=self.base.frame_int_keymap_size)
        self.base.frame_int_keymap.setPos(self.pos_X, self.pos_Y, self.pos_Z)

        self.lbl_keymap_title = DirectLabel(text=self.language['keymap'],
                                            text_fg=(255, 255, 255, 1),
                                            text_font=self.font.load_font(self.menu_font),
                                            frameColor=(255, 255, 255, 0),
                                            scale=.07, borderWidth=(self.w, self.h),
                                            parent=self.base.frame_int_keymap)

        self.lbl_forward = DirectLabel(text=self.language['forward'],
                                       text_fg=(255, 255, 255, 1),
                                       text_font=self.font.load_font(self.menu_font),
                                       frameColor=(255, 255, 255, 0),
                                       scale=self.lbl_scale, borderWidth=(self.w, self.h),
                                       parent=self.base.frame_int_keymap)

        self.lbl_backward = DirectLabel(text=self.language['backward'],
                                        text_fg=(255, 255, 255, 1),
                                        text_font=self.font.load_font(self.menu_font),
                                        frameColor=(255, 255, 255, 0),
                                        scale=self.lbl_scale, borderWidth=(self.w, self.h),
                                        parent=self.base.frame_int_keymap)

        self.lbl_left = DirectLabel(text=self.language['left'],
                                    text_fg=(255, 255, 255, 1),
                                    text_font=self.font.load_font(self.menu_font),
                                    frameColor=(255, 255, 255, 0),
                                    scale=self.lbl_scale, borderWidth=(self.w, self.h),
                                    parent=self.base.frame_int_keymap)

        self.lbl_right = DirectLabel(text=self.language['right'],
                                     text_fg=(255, 255, 255, 1),
                                     text_font=self.font.load_font(self.menu_font),
                                     frameColor=(255, 255, 255, 0),
                                     scale=self.lbl_scale, borderWidth=(self.w, self.h),
                                     parent=self.base.frame_int_keymap)

        self.lbl_run = DirectLabel(text=self.language['run'],
                                   text_fg=(255, 255, 255, 1),
                                   text_font=self.font.load_font(self.menu_font),
                                   frameColor=(255, 255, 255, 0),
                                   scale=self.lbl_scale, borderWidth=(self.w, self.h),
                                   parent=self.base.frame_int_keymap)

        self.lbl_crouch = DirectLabel(text=self.language['crouch'],
                                      text_fg=(255, 255, 255, 1),
                                      text_font=self.font.load_font(self.menu_font),
                                      frameColor=(255, 255, 255, 0),
                                      scale=self.lbl_scale, borderWidth=(self.w, self.h),
                                      parent=self.base.frame_int_keymap)

        self.lbl_jump = DirectLabel(text=self.language['jump'],
                                    text_fg=(255, 255, 255, 1),
                                    text_font=self.font.load_font(self.menu_font),
                                    frameColor=(255, 255, 255, 0),
                                    scale=self.lbl_scale, borderWidth=(self.w, self.h),
                                    parent=self.base.frame_int_keymap)

        self.lbl_use = DirectLabel(text=self.language['use'],
                                   text_fg=(255, 255, 255, 1),
                                   text_font=self.font.load_font(self.menu_font),
                                   frameColor=(255, 255, 255, 0),
                                   scale=self.lbl_scale, borderWidth=(self.w, self.h),
                                   parent=self.base.frame_int_keymap)

        self.lbl_attack = DirectLabel(text=self.language['attack'],
                                      text_fg=(255, 255, 255, 1),
                                      text_font=self.font.load_font(self.menu_font),
                                      frameColor=(255, 255, 255, 0),
                                      scale=self.lbl_scale, borderWidth=(self.w, self.h),
                                      parent=self.base.frame_int_keymap)

        self.lbl_h_attack = DirectLabel(text=self.language['h_attack'],
                                        text_fg=(255, 255, 255, 1),
                                        text_font=self.font.load_font(self.menu_font),
                                        frameColor=(255, 255, 255, 0),
                                        scale=self.lbl_scale, borderWidth=(self.w, self.h),
                                        parent=self.base.frame_int_keymap)

        self.lbl_f_attack = DirectLabel(text=self.language['f_attack'],
                                        text_fg=(255, 255, 255, 1),
                                        text_font=self.font.load_font(self.menu_font),
                                        frameColor=(255, 255, 255, 0),
                                        scale=self.lbl_scale, borderWidth=(self.w, self.h),
                                        parent=self.base.frame_int_keymap)

        self.lbl_block = DirectLabel(text=self.language['block'],
                                     text_fg=(255, 255, 255, 1),
                                     text_font=self.font.load_font(self.menu_font),
                                     frameColor=(255, 255, 255, 0),
                                     scale=self.lbl_scale, borderWidth=(self.w, self.h),
                                     parent=self.base.frame_int_keymap)

        self.lbl_sword = DirectLabel(text=self.language['sword'],
                                     text_fg=(255, 255, 255, 1),
                                     text_font=self.font.load_font(self.menu_font),
                                     frameColor=(255, 255, 255, 0),
                                     scale=self.lbl_scale, borderWidth=(self.w, self.h),
                                     parent=self.base.frame_int_keymap)

        self.lbl_bow = DirectLabel(text=self.language['bow'],
                                   text_fg=(255, 255, 255, 1),
                                   text_font=self.font.load_font(self.menu_font),
                                   frameColor=(255, 255, 255, 0),
                                   scale=self.lbl_scale, borderWidth=(self.w, self.h),
                                   parent=self.base.frame_int_keymap)

        self.lbl_tengri = DirectLabel(text=self.language['tengri'],
                                      text_fg=(255, 255, 255, 1),
                                      text_font=self.font.load_font(self.menu_font),
                                      frameColor=(255, 255, 255, 0),
                                      scale=self.lbl_scale, borderWidth=(self.w, self.h),
                                      parent=self.base.frame_int_keymap)

        self.lbl_umay = DirectLabel(text=self.language['umai'],
                                    text_fg=(255, 255, 255, 1),
                                    text_font=self.font.load_font(self.menu_font),
                                    frameColor=(255, 255, 255, 0),
                                    scale=self.lbl_scale, borderWidth=(self.w, self.h),
                                    parent=self.base.frame_int_keymap)

        kmp = self.m_settings.input_validate(self.cfg_path, 'kmp')
        self.inp_forward = DirectEntry(initialText=kmp['Keymap']['forward'],
                                       entryFont=self.font.load_font(self.menu_font),
                                       text_align=TextNode.A_center,
                                       scale=self.lbl_scale, width=7, borderWidth=(self.w, self.h),
                                       parent=self.base.frame_int_keymap,
                                       command=self.set_key_forward)

        self.inp_backward = DirectEntry(initialText=kmp['Keymap']['backward'],
                                        entryFont=self.font.load_font(self.menu_font),
                                        text_align=TextNode.A_center,
                                        scale=self.lbl_scale, width=7, borderWidth=(self.w, self.h),
                                        parent=self.base.frame_int_keymap,
                                        command=self.set_key_backward)

        self.inp_left = DirectEntry(initialText=kmp['Keymap']['left'],
                                    entryFont=self.font.load_font(self.menu_font),
                                    text_align=TextNode.A_center,
                                    scale=self.lbl_scale, width=7, borderWidth=(self.w, self.h),
                                    parent=self.base.frame_int_keymap,
                                    command=self.set_key_left)

        self.inp_right = DirectEntry(initialText=kmp['Keymap']['right'],
                                     entryFont=self.font.load_font(self.menu_font),
                                     text_align=TextNode.A_center,
                                     scale=self.lbl_scale, width=7, borderWidth=(self.w, self.h),
                                     parent=self.base.frame_int_keymap,
                                     command=self.set_key_right)

        self.inp_run = DirectEntry(initialText=kmp['Keymap']['run'],
                                   entryFont=self.font.load_font(self.menu_font),
                                   text_align=TextNode.A_center,
                                   scale=self.lbl_scale, width=7, borderWidth=(self.w, self.h),
                                   parent=self.base.frame_int_keymap,
                                   command=self.set_key_right)

        self.inp_crouch = DirectEntry(initialText=kmp['Keymap']['crouch'],
                                      entryFont=self.font.load_font(self.menu_font),
                                      text_align=TextNode.A_center,
                                      scale=self.lbl_scale, width=7, borderWidth=(self.w, self.h),
                                      parent=self.base.frame_int_keymap,
                                      command=self.set_key_crouch)

        self.inp_jump = DirectEntry(initialText=kmp['Keymap']['jump'],
                                    entryFont=self.font.load_font(self.menu_font),
                                    text_align=TextNode.A_center,
                                    scale=self.lbl_scale, width=7, borderWidth=(self.w, self.h),
                                    parent=self.base.frame_int_keymap,
                                    command=self.set_key_jump)

        self.inp_use = DirectEntry(initialText=kmp['Keymap']['use'],
                                   entryFont=self.font.load_font(self.menu_font),
                                   text_align=TextNode.A_center,
                                   scale=self.lbl_scale, width=7, borderWidth=(self.w, self.h),
                                   parent=self.base.frame_int_keymap,
                                   command=self.set_key_use)

        self.inp_attack = DirectEntry(initialText=kmp['Keymap']['attack'],
                                      entryFont=self.font.load_font(self.menu_font),
                                      text_align=TextNode.A_center,
                                      scale=self.lbl_scale, width=7, borderWidth=(self.w, self.h),
                                      parent=self.base.frame_int_keymap,
                                      command=self.set_key_attack)

        self.inp_h_attack = DirectEntry(initialText=kmp['Keymap']['h_attack'],
                                        entryFont=self.font.load_font(self.menu_font),
                                        text_align=TextNode.A_center,
                                        scale=self.lbl_scale, width=7, borderWidth=(self.w, self.h),
                                        parent=self.base.frame_int_keymap,
                                        command=self.set_key_h_attack)

        self.inp_f_attack = DirectEntry(initialText=kmp['Keymap']['f_attack'],
                                        entryFont=self.font.load_font(self.menu_font),
                                        text_align=TextNode.A_center,
                                        scale=self.lbl_scale, width=7, borderWidth=(self.w, self.h),
                                        parent=self.base.frame_int_keymap,
                                        command=self.set_key_f_attack)

        self.inp_block = DirectEntry(initialText=kmp['Keymap']['block'],
                                     entryFont=self.font.load_font(self.menu_font),
                                     text_align=TextNode.A_center,
                                     scale=self.lbl_scale, width=7, borderWidth=(self.w, self.h),
                                     parent=self.base.frame_int_keymap,
                                     command=self.set_key_block)

        self.inp_sword = DirectEntry(initialText=kmp['Keymap']['sword'],
                                     entryFont=self.font.load_font(self.menu_font),
                                     text_align=TextNode.A_center,
                                     scale=self.lbl_scale, width=7, borderWidth=(self.w, self.h),
                                     parent=self.base.frame_int_keymap,
                                     command=self.set_key_sword)

        self.inp_bow = DirectEntry(initialText=kmp['Keymap']['bow'], text_bg=(0, 0, 0, 0.9),
                                   entryFont=self.font.load_font(self.menu_font),
                                   text_align=TextNode.A_center,
                                   scale=self.lbl_scale, width=7, borderWidth=(self.w, self.h),
                                   parent=self.base.frame_int_keymap,
                                   command=self.set_key_bow)

        self.inp_tengri = DirectEntry(initialText=kmp['Keymap']['tengri'],
                                      entryFont=self.font.load_font(self.menu_font),
                                      text_align=TextNode.A_center,
                                      scale=self.lbl_scale, width=7, borderWidth=(self.w, self.h),
                                      parent=self.base.frame_int_keymap,
                                      command=self.set_key_tengri)

        self.inp_umay = DirectEntry(initialText=kmp['Keymap']['umai'],
                                    entryFont=self.font.load_font(self.menu_font),
                                    text_align=TextNode.A_center,
                                    scale=self.lbl_scale, width=7, borderWidth=(self.w, self.h),
                                    parent=self.base.frame_int_keymap,
                                    command=self.set_key_umay)

        self.btn_param_decline = DirectButton(text="Back",
                                              text_fg=(255, 255, 255, 1),
                                              text_font=self.font.load_font(self.menu_font),
                                              frameColor=(255, 255, 255, 0),
                                              scale=self.btn_scale, borderWidth=(self.w, self.h),
                                              parent=self.base.frame_int_keymap,
                                              geom=geoms, geom_scale=(5.1, 0, 2),
                                              clickSound=self.base.sound_gui_click,
                                              command=self.unload_keymap_menu)

        self.btn_param_defaults = DirectButton(text="Load defaults",
                                               text_fg=(255, 255, 255, 1),
                                               text_font=self.font.load_font(self.menu_font),
                                               frameColor=(255, 255, 255, 0),
                                               scale=self.btn_scale, borderWidth=(self.w, self.h),
                                               parent=self.base.frame_int_keymap,
                                               geom=geoms, geom_scale=(8.1, 0, 2),
                                               clickSound=self.base.sound_gui_click,
                                               command=self.set_default_keymap)

        """ Positioning objects of the keymapping menu:
            for two blocks
        """
        self.logo.reparent_to(self.base.frame_int_keymap)
        self.logo.set_scale(0.40, 0.20, 0.20)

        self.ornament_right.reparent_to(self.base.frame_int_keymap)
        self.ornament_right.set_scale(self.ornament_scale)
        self.ornament_right.set_hpr(0.0, 0.0, -90.0)
        self.ornament_right.set_transparency(TransparencyAttrib.MAlpha)
        self.ornament_right.set_pos(self.ornament_r_kmp_pos)

        self.lbl_keymap_title.set_pos(0.6, 0, 0.6)

        self.lbl_forward.set_pos(-0.5, 0, 0.3)
        self.lbl_backward.set_pos(-0.5, 0, 0.2)
        self.lbl_left.set_pos(-0.5, 0, 0.1)
        self.lbl_right.set_pos(-0.5, 0, 0)
        self.lbl_run.set_pos(-0.5, 0, -0.1)
        self.lbl_crouch.set_pos(-0.5, 0, -0.2)
        self.lbl_jump.set_pos(-0.5, 0, -0.3)
        self.lbl_use.set_pos(-0.5, 0, -0.4)

        self.inp_forward.set_pos(0, 0, 0.3)
        self.inp_backward.set_pos(0, 0, 0.2)
        self.inp_left.set_pos(0, 0, 0.1)
        self.inp_right.set_pos(0, 0, 0)
        self.inp_run.set_pos(0, 0, -0.1)
        self.inp_crouch.set_pos(0, 0, -0.2)
        self.inp_jump.set_pos(0, 0, -0.3)
        self.inp_use.set_pos(0, 0, -0.4)

        self.lbl_attack.set_pos(0.5, 0, 0.3)
        self.lbl_h_attack.set_pos(0.5, 0, 0.2)
        self.lbl_f_attack.set_pos(0.5, 0, 0.1)
        self.lbl_block.set_pos(0.5, 0, 0)
        self.lbl_sword.set_pos(0.5, 0, -0.1)
        self.lbl_bow.set_pos(0.5, 0, -0.2)
        self.lbl_tengri.set_pos(0.5, 0, -0.3)
        self.lbl_umay.set_pos(0.5, 0, -0.4)

        self.inp_attack.set_pos(1.0, 0, 0.3)
        self.inp_h_attack.set_pos(1.0, 0, 0.2)
        self.inp_f_attack.set_pos(1.0, 0, 0.1)
        self.inp_block.set_pos(1.0, 0, 0)
        self.inp_sword.set_pos(1.0, 0, -0.1)
        self.inp_bow.set_pos(1.0, 0, -0.2)
        self.inp_tengri.set_pos(1.0, 0, -0.3)
        self.inp_umay.set_pos(1.0, 0, -0.4)

        self.btn_param_defaults.set_pos(1.5, 0, -0.8)
        self.btn_param_decline.set_pos(-0.6, 0, -0.8)
        self.menu_mode = True
        base.active_frame = self.base.frame_int_keymap

    def unload_keymap_menu(self):
        """ Function    : unload_keymap_menu

            Description : Unload Keymap menu.

            Input       : None

            Output      : None

            Return      : None
        """
        if not self.base.frame_int_keymap:
            return

        if hasattr(base, "active_frame"):
            base.active_frame.destroy()

        if self.game_mode:
            self.base.frame_int_keymap.destroy()
        self.base.frame_int_keymap.destroy()
        self.logo.destroy()
        self.ornament_right.destroy()

