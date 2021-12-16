import json
from os.path import exists

from direct.showbase.ShowBaseGlobal import aspect2d
from direct.gui.DirectGui import *
from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.OnscreenImage import TransparencyAttrib
from panda3d.core import FontPool, Vec3, PGButton, MouseButton

from Engine.Inventory.inventory import Inventory
from Engine.Inventory.item import Item
from panda3d.core import TextNode
from panda3d.core import WindowProperties
from Engine.Render.render import RenderAttr


class Sheet(Inventory):

    def __init__(self):
        Inventory.__init__(self)
        self.props = WindowProperties()
        self.base = base
        self.game_settings = base.game_settings
        self.game_dir = base.game_dir
        self.fonts = base.fonts_collector()
        self.configs = base.cfg_collector(path="{0}/Settings/UI".format(self.game_dir))
        self.lng_configs = base.cfg_collector(path="{0}/Configs/Language/".format(self.game_dir))
        self.json = json
        # instance of the abstract class
        self.font = FontPool
        self.text = TextNode("TextNode")
        self.render_attr = RenderAttr()
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
        self.base.frame_scrolled_size = [0.0, 0.7, -0.05, 0.40]
        self.base.frame_scrolled_inner_size = [-0.2, 0.2, -0.00, 0.00]
        self.base.frame_journal_size = [-3, 0.7, -1, 3]
        self.base.frame_player_prop_size = [-1.15, 0.5, -0.7, 0]

        """ Frame Colors """
        self.frm_opacity = 1

        """ Buttons, Label Scaling """
        self.lbl_scale = .03
        self.btn_scale = .03

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
        self.base.build_info.reparent_to(self.base.frame_inv)
        self.base.frame_inv.hide()

        self.base.frame_journal = DirectFrame(frameColor=(0, 0, 0, 1.0),
                                              frameSize=self.base.frame_journal_size,
                                              pos=(0, 0, 0))
        self.base.frame_journal.hide()

        ui_geoms = base.ui_geom_collector()
        maps = base.loader.loadModel(ui_geoms['x_btn'])
        geoms = (maps.find('**/x_btn_ready'),
                 maps.find('**/x_btn_clicked'),
                 maps.find('**/x_btn_rollover'))
        sounds = self.base.sounds_collector()
        self.sound_gui_click = self.base.loader.load_sfx(sounds.get('zapsplat_button_click'))
        self.btn_close_inv = DirectButton(text="",
                                          text_fg=(255, 255, 255, 0.9),
                                          text_font=self.font.load_font(self.menu_font),
                                          frameColor=(0, 0, 0, self.frm_opacity),
                                          scale=self.btn_scale, borderWidth=(self.w, self.h),
                                          geom=geoms, geom_scale=(0.13, 0, 0.16),
                                          clickSound=self.sound_gui_click,
                                          command=base.messenger.send,
                                          extraArgs=["close_sheet"],
                                          pos=(-1.8, 0, 0.9),
                                          parent=self.base.frame_inv)
        self.btn_close_journal = DirectButton(text="",
                                              text_fg=(255, 255, 255, 0.9),
                                              text_font=self.font.load_font(self.menu_font),
                                              frameColor=(0, 0, 0, self.frm_opacity),
                                              scale=self.btn_scale, borderWidth=(self.w, self.h),
                                              geom=geoms, geom_scale=(0.13, 0, 0.15),
                                              clickSound=self.sound_gui_click,
                                              command=base.messenger.send,
                                              extraArgs=["close_sheet"],
                                              pos=(-1.8, 0, 0.9),
                                              parent=self.base.frame_journal)

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
        btn_select_inv = DirectButton(text="Inventory",
                                      text_fg=(255, 255, 255, 1), relief=2,
                                      text_font=self.font.load_font(self.menu_font),
                                      frameColor=(0, 0, 0, 1),
                                      scale=.03, borderWidth=(self.w, self.h),
                                      geom=geoms_scrolled_dbtn, geom_scale=(15.3, 0, 2),
                                      clickSound=self.sound_gui_click,
                                      command=self.hide_journal)
        btn_select_journal = DirectButton(text="Journal",
                                          text_fg=(255, 255, 255, 1), relief=2,
                                          text_font=self.font.load_font(self.menu_font),
                                          frameColor=(0, 0, 0, 1),
                                          scale=.03, borderWidth=(self.w, self.h),
                                          geom=geoms_scrolled_dbtn, geom_scale=(15.3, 0, 2),
                                          clickSound=self.sound_gui_click,
                                          command=self.show_journal)
        btn_list.append(btn_select_inv)
        btn_list.append(btn_select_journal)

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

            pos=(0.1, -0.9, 0.4)
        )
        self.base.menu_selector.hide()

        """ QUESTS """
        quests_btn_list = []

        btn_inc_pos = 0.49
        for i in range(9):
            btn_quest = DirectButton(text="Quest {0}".format(i),
                                     text_fg=(255, 255, 255, 1), relief=2,
                                     text_font=self.font.load_font(self.menu_font),
                                     frameColor=(0, 0, 0, 1),
                                     scale=.03, borderWidth=(self.w, self.h),
                                     geom=geoms_scrolled_dbtn, geom_scale=(15.3, 0, 2),
                                     clickSound=self.sound_gui_click,
                                     command=self.base.frame_journal.show)
            btn_inc_pos += -0.12
            quests_btn_list.append(btn_quest)

        self.quests_selector = DirectScrolledList(
            decButton_pos=(0.35, 0, 0.49),
            decButton_scale=(5, 1, 0.5),
            decButton_text="Dec",
            decButton_text_scale=0.04,
            decButton_borderWidth=(0, 0),
            decButton_geom=geoms_scrolled_dec,
            decButton_geom_scale=0.08,

            incButton_pos=(0.35, 0, btn_inc_pos),
            incButton_scale=(5, 1, 0.5),
            incButton_text="Inc",
            incButton_text_scale=0.04,
            incButton_borderWidth=(0, 0),
            incButton_geom=geoms_scrolled_inc,
            incButton_geom_scale=0.08,

            frameSize=self.base.frame_scrolled_size,
            frameColor=(0, 0, 0, 0),
            numItemsVisible=9,
            forceHeight=0.11,
            items=quests_btn_list,
            itemFrame_frameSize=self.base.frame_scrolled_inner_size,
            itemFrame_pos=(0.35, 0, 0.4),

            pos=(-1.8, 0, 0.32),
            parent=self.base.frame_journal

        )

        self.quest_desc_frame_title_img = OnscreenImage(image=self.images['journal_title'],
                                                        scale=(0.7, 0, 0.15),
                                                        pos=(-0.5, 0, 0.80),
                                                        parent=self.base.frame_journal)

        # Left, right, bottom, top
        self.quest_desc_frame = DirectScrolledFrame(frameColor=(0, 0, 0, 1.0),
                                                    canvasSize=(-0.5, 0.5, -0.3, 0.3),
                                                    frameSize=(-0.7, 0.7, -0.35, 0.34),
                                                    scrollBarWidth=0.02,
                                                    autoHideScrollBars=True,
                                                    pos=(-0.5, 0, 0.32),
                                                    verticalScroll_frameColor=(0, 0, 0, 1.0),
                                                    horizontalScroll_frameColor=(0, 0, 0, 1.0),
                                                    verticalScroll_incButton_frameColor=(0, 0, 0, 1.0),
                                                    verticalScroll_decButton_frameColor=(0, 0, 0, 1.0),
                                                    horizontalScroll_incButton_frameColor=(0, 0, 0, 1.0),
                                                    horizontalScroll_decButton_frameColor=(0, 0, 0, 1.0),
                                                    verticalScroll_thumb_frameColor=(0.4, 0.3, 0.2, 1.0),
                                                    horizontalScroll_thumb_frameColor=(0.4, 0.3, 0.2, 1.0),
                                                    parent=self.base.frame_journal)

        self.quest_desc_frame_img = OnscreenImage(image=self.images['journal_quest_desc'],
                                                  scale=(0.7, 0, 0.4),
                                                  pos=(0.2, 0, -0.1),
                                                  parent=self.quest_desc_frame.getCanvas())
        self.quest_desc_frame_img.setTransparency(TransparencyAttrib.MAlpha)

        self.quest_frame_map_img = OnscreenImage(image=self.images['journal_ancient_map_sm'],
                                                 scale=(0.7, 0, 0.4),
                                                 pos=(-0.5, 0, -0.45),
                                                 parent=self.base.frame_journal)
        self.quest_frame_map_img.setTransparency(TransparencyAttrib.MAlpha)

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
            (('INVENTORY_2', 'TRASH', 'HAND_L'), 'weapon',
             self.images['slot_item_sword'], 'Sword', 1, 1, 0, 38),
            (('INVENTORY_2', 'TRASH', 'HAND_R'), 'weapon',
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
            (('INVENTORY_3', 'TENGRI_PWR'), 'weapon',
             self.images['slot_item_tengri'], 'Tengri Power', 1, 1, 0, 8),
            (('INVENTORY_3', 'UMAI_PWR'), 'weapon',
             self.images['slot_item_umai'], 'Umai Power', 1, 1, 0, 8)
        ]

        # sheet slots init
        self.custom_inv_slots(sheet_slot_info)

        # Field of slots 3х5,        positions: x, y
        self.fill_up_inv_slots(3, 5, -1.55, 0.66, 'INVENTORY_1')
        self.fill_up_inv_slots(3, 5, -1.0, 0.66, 'INVENTORY_2')
        self.fill_up_inv_slots(3, 5, -0.45, 0.66, 'INVENTORY_3')

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

        """ DEFINE PLAYER PROPERTIES """

        # player properties (health, stamina, etc)
        self.frame_player_prop = DirectFrame(frameColor=(0.0, 0.0, 0.0, 0.0),
                                             frameSize=self.base.frame_player_prop_size,
                                             pos=(-0.5, 0, -0.15),
                                             parent=self.base.frame_inv)
        self.frame_player_prop_img = OnscreenImage(image=self.images['inv_frm_player_props'],
                                                   pos=(-0.3, 0, -0.34),
                                                   scale=(0.9, 0, 0.3),
                                                   parent=self.frame_player_prop)

        self.frame_player_prop_img.setTransparency(TransparencyAttrib.MAlpha)
        # todo: move player_prop to player's state.py
        player_props = {
            'name:': 'Korlan',
            'age:': 25,
            'sex:': 'female',
            'height:': "1.7 m",
            'weight:': "57 kg",
            'specialty:': 'warrior',
            'health:': 100,
            'stamina:': 100,
            'courage:': 100,
        }
        prop_icon_pos_x = -0.9
        key_label_pos_x = -0.8
        value_label_pos_x = -0.65
        pos_z = -0.55
        for idx, key in enumerate(player_props):

            if idx == 5:
                # reset z position for second column
                pos_z = -0.55
            if idx >= 5:
                # make second column
                prop_icon_pos_x = -0.3
                key_label_pos_x = -0.18
                value_label_pos_x = 0.0

            prop_txt = str(player_props[key])
            pos_z += 0.07
            prop_icon = OnscreenImage(image=self.images['prop_def_c'],
                                      pos=(prop_icon_pos_x, 0, pos_z),
                                      scale=.02,
                                      parent=self.frame_player_prop)
            prop_icon.setTransparency(TransparencyAttrib.MAlpha)

            DirectLabel(text=key,
                        text_fg=(0.1, 0.1, 0.1, 1),
                        text_font=self.font.load_font(self.menu_font),
                        frameColor=(255, 255, 255, 0),
                        scale=.04, borderWidth=(self.w, self.h),
                        pos=(key_label_pos_x, 0, pos_z),
                        parent=self.frame_player_prop)
            DirectLabel(text=prop_txt,
                        text_fg=(0.1, 0.1, 0.1, 1),
                        text_font=self.font.load_font(self.menu_font),
                        frameColor=(255, 255, 255, 0),
                        scale=.04, borderWidth=(self.w, self.h),
                        pos=(value_label_pos_x, 0, pos_z),
                        parent=self.frame_player_prop)

    @staticmethod
    def _handle_mouse_scroll(obj, direction):
        if (isinstance(obj, DirectSlider)
                or isinstance(obj, DirectScrollBar)
                or isinstance(obj, DirectScrolledFrame)):
            obj.setValue(obj.getValue() + direction * obj["pageSize"])

    def show_journal(self):
        self.base.frame_journal.show()
        WHEEL_UP = PGButton.get_release_prefix() + MouseButton.wheel_up().get_name() + "-"
        WHEEL_DOWN = PGButton.get_release_prefix() + MouseButton.wheel_down().get_name() + "-"
        self.quest_desc_frame.bind(WHEEL_UP, self._handle_mouse_scroll, [self.quest_desc_frame, 1])
        self.quest_desc_frame.bind(WHEEL_DOWN, self._handle_mouse_scroll, [self.quest_desc_frame, -1])
        self.quest_desc_frame.horizontalScroll.thumb.bind(WHEEL_UP, self._handle_mouse_scroll,
                                                          [self.quest_desc_frame, 1])
        self.quest_desc_frame.horizontalScroll.thumb.bind(WHEEL_DOWN, self._handle_mouse_scroll,
                                                          [self.quest_desc_frame, -1])

    def hide_journal(self):
        self.base.frame_journal.hide()
        WHEEL_UP = PGButton.get_release_prefix() + MouseButton.wheel_up().get_name() + "-"
        WHEEL_DOWN = PGButton.get_release_prefix() + MouseButton.wheel_down().get_name() + "-"
        self.quest_desc_frame.unbind(WHEEL_UP)
        self.quest_desc_frame.unbind(WHEEL_DOWN)
        self.quest_desc_frame.horizontalScroll.thumb.unbind(WHEEL_UP)
        self.quest_desc_frame.horizontalScroll.thumb.unbind(WHEEL_DOWN)

    def set_sheet(self):
        """ Sets inventory ui """
        if base.game_mode and base.menu_mode is False:
            if self.base.frame_inv:
                if self.base.frame_inv.is_hidden():

                    if hasattr(base, "hud") and base.hud:
                        base.hud.toggle_all_hud(state="hidden")

                    self.base.frame_inv.show()
                    self.base.menu_selector.show()
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

    def clear_sheet(self):
        self.base.build_info.reparent_to(aspect2d)
        self.base.frame_inv.hide()
        if not self.base.menu_selector.is_hidden():
            self.base.menu_selector.hide()
        self.base.frame_journal.hide()

        if hasattr(base, "hud") and base.hud:
            base.hud.toggle_all_hud(state="visible")

        self.toggle()

        props = WindowProperties()
        props.set_cursor_hidden(True)
        self.base.win.request_properties(props)
        base.is_ui_active = False

        self.revert_character()

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
                if self.game_settings['Main']['postprocessing'] == 'on':
                    # set character view
                    player_pos = player.get_pos()
                    base.camera.set_x(player_pos[0] + -0.9)
                    base.camera.set_y(player_pos[1] + -4)
                    base.camera.set_z(player_pos[2] + 0.7)
                else:
                    # set character view
                    player_pos = player.get_pos()
                    base.camera.set_x(player_pos[0] + -1.3)
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

                # set light
                player_bs = self.base.get_actor_bullet_shape_node(asset="Player", type="Player")
                if player_bs:
                    if self.game_settings['Main']['postprocessing'] == 'on':
                        light_pos = [player_bs.get_x(), player_bs.get_y() - 4.0, 7.0]
                        self.render_attr.set_inv_lighting(name='slight',
                                                          render=render,
                                                          pos=light_pos,
                                                          hpr=[0, 0.4, -1],
                                                          color=[1.0],
                                                          task="attach")
                        self.render_attr.render_pipeline.prepare_scene(bg_black)
                    else:
                        light_pos = [player_bs.get_x(), player_bs.get_y(), player_bs.get_z() + 0.7]
                        self.render_attr.set_inv_lighting(name='slight',
                                                          render=render,
                                                          pos=light_pos,
                                                          hpr=[0, 14, 0],
                                                          color=[0.4],
                                                          task="attach")

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

        self.render_attr.clear_inv_lighting()
