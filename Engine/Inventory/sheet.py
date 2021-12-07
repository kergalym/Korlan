import json
from os.path import exists

from direct.showbase.ShowBaseGlobal import render2d, aspect2d
from direct.gui.DirectGui import *
from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.OnscreenImage import TransparencyAttrib

from Engine.Inventory.inventory import Inventory
from panda3d.core import FontPool, Vec3, NodePath
from Engine.Inventory.item import Item
from panda3d.core import TextNode
from panda3d.core import WindowProperties


class Sheet(Inventory):

    def __init__(self):
        Inventory.__init__(self)
        self.props = WindowProperties()
        self.base = base
        self.game_dir = base.game_dir
        # self.images = base.textures_collector(path="{0}/Settings/UI".format(self.game_dir))
        # self.inv_images = base.textures_collector(path="{0}/Assets".format(self.game_dir))
        self.fonts = base.fonts_collector()
        self.configs = base.cfg_collector(path="{0}/Settings/UI".format(self.game_dir))
        self.lng_configs = base.cfg_collector(path="{0}/Configs/Language/".format(self.game_dir))
        self.json = json
        # instance of the abstract class
        self.font = FontPool
        self.text = TextNode("TextNode")
        self.menu_font = None
        self.cfg_path = None

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
        self.base.frame_inv_size = [-3, 3, -1, 3]
        self.base.frame_inv_black_bg_size = [-3, 0.7, -1, 3]
        self.base.frame_inv_int_canvas_size = [-2, 2, -2, 2]
        self.base.frame_inv_int_size = [-.5, .2, -1.3, 0]
        self.base.frame_scrolled_size = [0.0, 0.7, -0.05, 0.40]
        self.base.frame_scrolled_inner_size = [-0.2, 0.2, -0.00, 0.00]

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

        """ Frames, Buttons & Fonts"""
        self.menu_font = self.fonts['OpenSans-Regular']

        self.base.frame_inv = DirectFrame(frameColor=(0, 0, 0, 0),
                                          frameSize=self.base.frame_inv_size,
                                          pos=(0, 0, 0))

        ui_geoms = base.ui_geom_collector()

        maps = base.loader.loadModel(ui_geoms['btn_t_icon'])
        geoms = (maps.find('**/button_any'),
                 maps.find('**/button_pressed'),
                 maps.find('**/button_rollover'))

        sounds = self.base.sounds_collector()

        self.sound_gui_click = self.base.loader.load_sfx(sounds.get('zapsplat_button_click'))

        self.btn_param_decline = DirectButton(text="Cancel",
                                              text_fg=(255, 255, 255, 0.9),
                                              text_font=self.font.load_font(self.menu_font),
                                              frameColor=(255, 255, 255, self.frm_opacity),
                                              scale=self.btn_scale, borderWidth=(self.w, self.h),
                                              geom=geoms, geom_scale=(8.1, 0, 2),
                                              clickSound=self.sound_gui_click,
                                              command=self.clear_sheet,
                                              pos=(0.1, 0, -0.9),
                                              parent=self.base.frame_inv)

        self.btn_param_accept = DirectButton(text="OK",
                                             text_fg=(255, 255, 255, 0.9),
                                             text_font=self.font.load_font(self.menu_font),
                                             frameColor=(255, 255, 255, self.frm_opacity),
                                             scale=self.btn_scale, borderWidth=(self.w, self.h),
                                             geom=geoms, geom_scale=(5.1, 0, 2),
                                             clickSound=self.sound_gui_click,
                                             command=self.clear_sheet,
                                             pos=(-1.6, 0, -0.9),
                                             parent=self.base.frame_inv)

        """maps_scrolled_dbtn = base.loader.loadModel(ui_geoms['btn_t_icon'])
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
        for i in range(3):
            btn = DirectButton(text="Menu selector {0}".format(i),
                               text_fg=(255, 255, 255, 1), relief=2,
                               text_font=self.font.load_font(self.menu_font),
                               frameColor=(0, 0, 0, 1),
                               scale=.03, borderWidth=(self.w, self.h),
                               geom=geoms_scrolled_dbtn, geom_scale=(15.3, 0, 2),
                               clickSound=self.sound_gui_click,
                               command=None,
                               extraArgs=[])
            btn_list.append(btn)

        self.base.menu_selector = DirectScrolledList(
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

            pos=(0.1, -0.9, 0.4),
            parent=self.base.frame_inv
        )"""

        self.base.build_info.reparent_to(self.base.frame_inv)
        self.base.frame_inv.hide()

        # object click n move
        self.base.is_inventory_active = False
        self.is_inventory_items_loaded = False
        self.player_camera_default = {
            "pos": Vec3(0, 0, 0),
            "hpr": Vec3(0, 0, 0),
            "pivot_hpr": Vec3(0, 0, 0)
        }

        """ DEFINE INVENTORY """
        sheet_slot_info = [('HAND_L', (0.9, 0, -0.01), u'Hand', self.images['hand_l_slot']),
                           ('HAND_R', (1.7, 0, -0.01), u'Hand', self.images['hand_r_slot']),
                           ('TENGRI_PWR', (1.7, 0, -0.35), u'Hand', self.images['magic_tengri_slot']),
                           ('UMAI_PWR', (1.7, 0, -0.67), u'Hand', self.images['magic_umai_slot']),
                           ('HEAD', (0.9, 0, 0.7), u'Head', self.images['head_slot']),
                           ('BODY', (1.7, 0, 0.32), u'Body', self.images['body_slot']),
                           ('FEET', (0.9, 0, -0.43), u'Feet', self.images['feet_slot']),
                           ('LEGS', (0.9, 0, -0.76), u'Legs', self.images['toe_slot']),
                           ('TRASH', (0.4, 0, -0.6), u'Trash', self.images['trash_slot'])]

        # styled frames for these sheet slots
        sheet_slot_frame_img = self.images['sheet_default_slot']
        sheet_slot_frame_scale = (0.21, 0, 0.21)
        hand_l_styled_frame = OnscreenImage(image=sheet_slot_frame_img,
                                            pos=(0.9, 0, -0.01),
                                            scale=sheet_slot_frame_scale,
                                            parent=self.base.frame_inv)
        hand_l_styled_frame.setTransparency(TransparencyAttrib.MAlpha)

        hand_r_styled_frame = OnscreenImage(image=sheet_slot_frame_img,
                                            pos=(1.7, 0, -0.01),
                                            scale=sheet_slot_frame_scale,
                                            parent=self.base.frame_inv)
        hand_r_styled_frame.setTransparency(TransparencyAttrib.MAlpha)

        tengri_pwr_styled_frame = OnscreenImage(image=sheet_slot_frame_img,
                                                pos=(1.7, 0, -0.35),
                                                scale=sheet_slot_frame_scale,
                                                parent=self.base.frame_inv)
        tengri_pwr_styled_frame.setTransparency(TransparencyAttrib.MAlpha)

        umai_pwr_styled_frame = OnscreenImage(image=sheet_slot_frame_img,
                                              pos=(1.7, 0, -0.67),
                                              scale=sheet_slot_frame_scale,
                                              parent=self.base.frame_inv)
        umai_pwr_styled_frame.setTransparency(TransparencyAttrib.MAlpha)

        head_styled_frame = OnscreenImage(image=sheet_slot_frame_img,
                                          pos=(0.9, 0, 0.7),
                                          scale=sheet_slot_frame_scale,
                                          parent=self.base.frame_inv)
        head_styled_frame.setTransparency(TransparencyAttrib.MAlpha)

        body_styled_frame = OnscreenImage(image=sheet_slot_frame_img,
                                          pos=(1.7, 0, 0.32),
                                          scale=sheet_slot_frame_scale,
                                          parent=self.base.frame_inv)
        body_styled_frame.setTransparency(TransparencyAttrib.MAlpha)

        feet_styled_frame = OnscreenImage(image=sheet_slot_frame_img,
                                          pos=(0.9, 0, -0.43),
                                          scale=sheet_slot_frame_scale,
                                          parent=self.base.frame_inv)
        feet_styled_frame.setTransparency(TransparencyAttrib.MAlpha)

        legs_styled_frame = OnscreenImage(image=sheet_slot_frame_img,
                                          pos=(0.9, 0, -0.76),
                                          scale=sheet_slot_frame_scale,
                                          parent=self.base.frame_inv)
        legs_styled_frame.setTransparency(TransparencyAttrib.MAlpha)

        trash_styled_frame = OnscreenImage(image=sheet_slot_frame_img,
                                           pos=(0.4, 0, -0.6),
                                           scale=sheet_slot_frame_scale,
                                           parent=self.base.frame_inv)
        trash_styled_frame.setTransparency(TransparencyAttrib.MAlpha)

        """(('INVENTORY_1', 'TRASH'), 'item',
            self.images['slot_item_qymyran'], 'Qymyran', 1, 1, 0, 8),
           (('INVENTORY_1', 'TRASH'), 'item',
            self.images['slot_item_torsyk'], 'Torsyk', 1, 1, 0, 8),"""

        sheet_items = [
            (('INVENTORY_2', 'TRASH', 'HAND_L', 'HAND_R'), 'weapon',
             self.images['slot_item_sword'], 'Sword', 1, 1, 0, 38),
            (('INVENTORY_2', 'TRASH', 'HAND_L', 'HAND_R'), 'weapon',
             self.images['slot_item_bow'], 'Bow', 1, 1, 0, 9),
            (('INVENTORY_2', 'TRASH', 'BODY'), 'armor',
             self.images['slot_item_armor'], 'Light armor', 1, 1, 10),
            (('INVENTORY_2', 'TRASH', 'HEAD'), 'armor',
             self.images['slot_item_helmet'], 'Helmet', 1, 1, 5),
            (('INVENTORY_2', 'TRASH', 'FEET'), 'armor',
             self.images['slot_item_feet'], 'Pants', 1, 1, 2),
            (('INVENTORY_2', 'TRASH', 'LEGS'), 'armor',
             self.images['slot_item_boots'], 'Boots', 1, 1, 2),
            (('INVENTORY_2', 'TRASH'), 'Arrows',
             self.images['slot_item_arrows'], 'Arrows', 20, 30),
            (('INVENTORY_2', 'TRASH'), 'Arrows',
             self.images['slot_item_arrows'], 'Arrows', 15, 30),
            (('INVENTORY_2', 'TRASH'), 'Arrows',
             self.images['slot_item_arrows'], 'Arrows', 6, 30),
            (('INVENTORY_3', 'TENGRI_PWR', 'UMAI_PWR'), 'weapon',
             self.images['slot_item_tengri'], 'Tengri Power', 1, 1, 0, 8),
            (('INVENTORY_3', 'TENGRI_PWR', 'UMAI_PWR'), 'weapon',
             self.images['slot_item_umai'], 'Umai Power', 1, 1, 0, 8)
        ]

        # sheet slots init
        self.custom_inv_slots(sheet_slot_info)

        # Field of slots 6х6,        x, y
        self.fill_up_inv_slots(3, 7, -1.55, 0.5, 'INVENTORY_1')
        self.fill_up_inv_slots(3, 7, -1.0, 0.5, 'INVENTORY_2')
        self.fill_up_inv_slots(3, 7, -0.45, 0.5, 'INVENTORY_3')

        for item in sheet_items:
            inventory_type = item[0][0]
            self.add_item(Item(item), inventory_type)

        # Inventory init
        self.init()

        # left is item index, right is slot index
        self.on_start_assign_item_to_sheet_slot(3, 4)  # helmet
        self.on_start_assign_item_to_sheet_slot(2, 5)  # armor
        self.on_start_assign_item_to_sheet_slot(4, 6)  # pants
        self.on_start_assign_item_to_sheet_slot(5, 7)  # boots
        self.on_start_assign_item_to_sheet_slot(0, 0)  # sword
        self.on_start_assign_item_to_sheet_slot(1, 1)  # bow

    def set_sheet(self):
        """ Sets inventory ui """
        if base.game_mode and base.menu_mode is False:
            if self.base.frame_inv.is_hidden():

                if hasattr(base, "hud") and base.hud:
                    base.hud.toggle_all_hud(state="hidden")

                self.base.frame_inv.show()
                self.props.set_cursor_hidden(False)
                self.base.win.request_properties(self.props)

                base.is_ui_active = True
                self.base.is_inventory_active = True
                self.prepare_character()

                self.toggle()

                # Stop item dragging on right mouse
                base.accept('mouse3-up', self.stop_drag)

                # 'on item move' event processing
                # in this case we are delete item, which has been placed into the 'TRASH'
                base.accept('inventory-item-move', self.on_item_move)

                # Add another item to inventory
                item = (('INVENTORY_2', 'TRASH'), 'Arrows', self.images['slot_item_arrows'], 'Arrows', 15, 30)
                inventory_type = item[0][0]
                self.add_item(Item(item), inventory_type)
                self.refresh_items()
            else:
                self.clear_sheet()
                self.revert_character()
                self.base.is_inventory_active = False

    def clear_sheet(self):
        self.base.build_info.reparent_to(aspect2d)
        self.base.frame_inv.hide()

        if hasattr(base, "hud") and base.hud:
            base.hud.toggle_all_hud(state="visible")

        self.toggle()

        props = WindowProperties()
        props.set_cursor_hidden(True)
        self.base.win.request_properties(props)
        base.is_ui_active = False

        # FIXME revert scene
        player_pos = self.player_camera_default["pos"]
        player_hpr = self.player_camera_default["hpr"]
        base.camera.set_pos(player_pos + Vec3(0, -4.6, 0))
        base.camera.set_hpr(player_hpr)

        if render.find("**/bg_black_char_sheet"):
            bg_black = render.find("**/bg_black_char_sheet")
            bg_black.hide()
        if render.find("**/World"):
            render.find("**/World").show()

        self.base.is_inventory_active = False

    def prepare_character(self):
        if self.base.is_inventory_active:
            # keep default state of player camera
            self.player_camera_default["pos"] = base.camera.get_pos()
            self.player_camera_default["hpr"] = base.camera.get_hpr()

            if render.find("**/pivot"):
                self.player_camera_default["pivot_hpr"] = render.find("**/pivot").get_hpr()

            player = render.find("**/Player")
            if player:
                # set character view
                player_pos = player.get_pos()
                base.camera.set_x(player_pos[0] + -0.9)
                base.camera.set_y(player_pos[1] + -4)
                base.camera.set_z(player_pos[2] + 0.7)
                base.camera.set_hpr(0, 0, 0)
                if render.find("**/pivot"):
                    render.find("**/pivot").set_hpr(24.6, -0.999999, 0)

                # set scene
                bg_black = None
                if not render.find("**/bg_black_char_sheet"):
                    geoms = self.base.inventory_geoms_collector()
                    if geoms:
                        bg_black = base.loader.loadModel(geoms["bg_black_char_sheet"])
                        bg_black.set_name("bg_black_char_sheet")
                        # bg_black.reparent_to(render)
                        player_bs = self.base.get_actor_bullet_shape_node(asset="Player", type="Player")
                        if player_bs:
                            bg_black.reparent_to(player_bs)
                            bg_black.set_pos(0, 0, 0)
                            bg_black.set_two_sided(True)
                else:
                    if render.find("**/bg_black_char_sheet"):
                        bg_black = render.find("**/bg_black_char_sheet")

                if bg_black:
                    bg_black.show()

                if render.find("**/World"):
                    render.find("**/World").hide()

    def revert_character(self):
        # revert character view
        player_pos = self.player_camera_default["pos"]
        player_hpr = self.player_camera_default["hpr"]
        pivot_hpr = self.player_camera_default["pivot_hpr"]
        base.camera.set_pos(player_pos)
        base.camera.set_hpr(player_hpr)
        if render.find("**/pivot"):
            render.find("**/pivot").set_hpr(pivot_hpr)

        # revert scene
        if render.find("**/bg_black_char_sheet"):
            bg_black = render.find("**/bg_black_char_sheet")
            bg_black.hide()
        if render.find("**/World"):
            render.find("**/World").show()
