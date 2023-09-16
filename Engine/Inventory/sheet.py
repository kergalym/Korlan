import json
from os.path import exists

from direct.interval.FunctionInterval import Func
from direct.interval.LerpInterval import LerpPosInterval
from direct.interval.MetaInterval import Sequence
from direct.showbase.ShowBaseGlobal import aspect2d
from direct.gui.DirectGui import *
from direct.gui.OnscreenImage import OnscreenImage
from panda3d.core import TransparencyAttrib
from panda3d.core import Vec3, PGButton, MouseButton, Point3

from Engine.Inventory.inventory import Inventory
from panda3d.core import TextNode


class Sheet(Inventory):

    def __init__(self):
        Inventory.__init__(self)
        self.char_sheet_bg = None

        """ Frame Sizes """
        # Left, right, bottom, top
        self.frame_scrolled_size = [0.0, 0.7, -0.05, 0.40]
        self.frame_scrolled_inner_size = [-0.2, 0.2, -0.00, 0.00]
        self.frame_journal_size = [-3, 0.7, -1, 3]
        self.frame_player_prop_size = [-1.15, 0.5, -0.7, 0]

        """ Frame Colors """
        self.frm_opacity = 1

        """ Buttons, Label Scaling """
        self.lbl_scale = .03
        self.btn_scale = .03

        self.frame_journal = None

        """ Sheet Params """
        self.sound_gui_click = None

        self.btn_select_inv = None
        self.btn_select_journal = None

        self.btn_close_inv = None
        self.btn_close_journal = None

        self.quests_selector = None

        self.journal_grid_frame = None
        self.journal_grid_cap = None

        self.quest_desc_frame = None
        self.quest_desc_frame_img = None

        self.quest_frame_map_img = None

        self.player_camera_default = None
        self.player_hpr_saved = None

        self.frame_player_prop = None
        self.frame_player_prop_img = None

        # object click n move
        self.base.is_inventory_active = False
        self.is_inventory_items_loaded = False
        self.player_camera_default = {
            "pos": Vec3(0, 0, 0),
            "hpr": Vec3(0, 0, 0),
            "pivot_hpr": Vec3(0, 0, 0)
        }
        self.player_hpr_saved = Vec3(0, 0, 0)

    def sheet_init(self):
        self.base.build_info.reparent_to(self.frame_inv)

        self.frame_journal = DirectFrame(frameColor=(0, 0, 0, 1.0),
                                         frameSize=self.frame_journal_size,
                                         pos=(0, 0, 0))
        self.frame_journal.hide()

        maps = base.loader.load_model(self.ui_geoms['btn_t_close_icon'])
        geoms = (maps.find('**/button_close_ready'),
                 maps.find('**/button_close_clicked'),
                 maps.find('**/button_close_rollover'))
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
                                          parent=self.frame_inv)
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
                                              parent=self.frame_journal)

        # inventory & journal geoms
        inv_maps_scrolled_dec = base.loader.load_model(self.ui_geoms['btn_inv_icon_dec'])
        inv_geoms_scrolled_dec = (inv_maps_scrolled_dec.find('**/button_any_dec'),
                                  inv_maps_scrolled_dec.find('**/button_pressed_dec'),
                                  inv_maps_scrolled_dec.find('**/button_rollover_dec'),
                                  inv_maps_scrolled_dec.find('**/button_disabled_dec'))

        inv_maps_scrolled_inc = base.loader.load_model(self.ui_geoms['btn_inv_icon_inc'])
        inv_geoms_scrolled_inc = (inv_maps_scrolled_inc.find('**/button_any_inc'),
                                  inv_maps_scrolled_inc.find('**/button_pressed_inc'),
                                  inv_maps_scrolled_inc.find('**/button_rollover_inc'),
                                  inv_maps_scrolled_inc.find('**/button_disabled_inc'))
        inv_maps_scrolled_inc.set_transparency(TransparencyAttrib.MAlpha)
        inv_maps_scrolled_dec.set_transparency(TransparencyAttrib.MAlpha)

        self.btn_select_inv = DirectButton(text="<|",
                                           text_fg=(0.7, 0.7, 0.7, 1),
                                           text_font=self.font.load_font(self.menu_font),
                                           frameColor=(0, 0, 0, 1),
                                           scale=.03, borderWidth=(self.w, self.h),
                                           geom=inv_geoms_scrolled_dec, geom_scale=(15.3, 0, 2),
                                           hpr=(0, 0, -90),
                                           clickSound=self.sound_gui_click,
                                           command=self.hide_journal,
                                           pos=(-1.70, 0, 0.3))
        self.btn_select_journal = DirectButton(text="|>",
                                               text_fg=(0.7, 0.7, 0.7, 1),
                                               text_font=self.font.load_font(self.menu_font),
                                               frameColor=(0, 0, 0, 1),
                                               scale=.03, borderWidth=(self.w, self.h),
                                               geom=inv_geoms_scrolled_inc, geom_scale=(15.3, 0, 2),
                                               hpr=(0, 0, -90),
                                               clickSound=self.sound_gui_click,
                                               command=self.show_journal,
                                               pos=(0.06, 0, 0.3))

        self.btn_select_inv.set_transparency(True)
        self.btn_select_inv.hide()
        self.btn_select_journal.set_transparency(True)
        self.btn_select_journal.hide()

        """ Set Inventory Modules """
        self.set_quest_journal()
        self.set_inventory()
        self.set_player_properties()
        self.set_character_sheet_background()

    def set_quest_journal(self):
        """ QUESTS """
        # quest selector geoms
        q_maps_scrolled_dbtn = base.loader.load_model(self.ui_geoms['btn_t_icon'])
        q_geoms_scrolled_dbtn = (q_maps_scrolled_dbtn.find('**/button_any'),
                                 q_maps_scrolled_dbtn.find('**/button_pressed'),
                                 q_maps_scrolled_dbtn.find('**/button_rollover'))

        q_maps_scrolled_dec = base.loader.load_model(self.ui_geoms['btn_t_icon_dec'])
        q_geoms_scrolled_dec = (q_maps_scrolled_dec.find('**/button_any_dec'),
                                q_maps_scrolled_dec.find('**/button_pressed_dec'),
                                q_maps_scrolled_dec.find('**/button_rollover_dec'))

        q_maps_scrolled_inc = base.loader.load_model(self.ui_geoms['btn_t_icon_inc'])
        q_geoms_scrolled_inc = (q_maps_scrolled_inc.find('**/button_any_inc'),
                                q_maps_scrolled_inc.find('**/button_pressed_inc'),
                                q_maps_scrolled_inc.find('**/button_rollover_inc'))
        q_maps_scrolled_dec.set_transparency(TransparencyAttrib.MAlpha)
        q_maps_scrolled_inc.set_transparency(TransparencyAttrib.MAlpha)

        quests_btn_list = []
        btn_inc_pos = 0.49
        for i in range(9):
            btn_quest = DirectButton(text="Quest {0}".format(i),
                                     text_fg=(255, 255, 255, 1), relief=2,
                                     text_font=self.font.load_font(self.menu_font),
                                     frameColor=(0, 0, 0, 1),
                                     scale=.03, borderWidth=(self.w, self.h),
                                     geom=q_geoms_scrolled_dbtn, geom_scale=(15.3, 0, 2),
                                     clickSound=self.sound_gui_click,
                                     command=self.frame_journal.show)
            btn_inc_pos += -0.12
            quests_btn_list.append(btn_quest)

        self.quests_selector = DirectScrolledList(
            decButton_pos=(0.35, 0, 0.49),
            decButton_scale=(5, 1, 0.5),
            decButton_text="Dec",
            decButton_text_scale=0.04,
            decButton_borderWidth=(0, 0),
            decButton_geom=q_geoms_scrolled_dec,
            decButton_geom_scale=0.09,

            incButton_pos=(0.35, 0, btn_inc_pos),
            incButton_scale=(5, 1, 0.5),
            incButton_text="Inc",
            incButton_text_scale=0.04,
            incButton_borderWidth=(0, 0),
            incButton_geom=q_geoms_scrolled_inc,
            incButton_geom_scale=0.09,

            frameSize=self.frame_scrolled_size,
            frameColor=(0, 0, 0, 0),
            numItemsVisible=9,
            forceHeight=0.11,
            items=quests_btn_list,
            itemFrame_frameSize=self.frame_scrolled_inner_size,
            itemFrame_pos=(0.35, 0, 0.4),

            pos=(0.0, 0, 0.32),
            parent=self.frame_journal

        )

        self.journal_grid_frame = OnscreenImage(image=self.images['grid_frame'],
                                                pos=(-0.82, 0, 0.37),
                                                scale=(0.86, 0, 0.40),
                                                parent=self.frame_journal)
        self.journal_grid_cap = OnscreenImage(image=self.images['grid_cap_j'],
                                              pos=(-0.82, 0, 0.82),
                                              scale=(0.92, 0, 0.08),
                                              parent=self.frame_journal)
        self.journal_grid_cap.set_transparency(TransparencyAttrib.MAlpha)
        self.journal_grid_frame.set_transparency(TransparencyAttrib.MAlpha)

        # Left, right, bottom, top
        self.quest_desc_frame = DirectScrolledFrame(frameColor=(0.0, 0.0, 0.0, 1.0),
                                                    canvasSize=(-0.5, 0.5, -0.3, 0.3),
                                                    frameSize=(-0.7, 0.7, -0.35, 0.34),
                                                    scrollBarWidth=0.02,
                                                    autoHideScrollBars=True,
                                                    pos=(-0.82, 0, 0.39),
                                                    verticalScroll_frameColor=(0, 0, 0, 1.0),
                                                    horizontalScroll_frameColor=(0, 0, 0, 1.0),
                                                    verticalScroll_incButton_frameColor=(0, 0, 0, 1.0),
                                                    verticalScroll_decButton_frameColor=(0, 0, 0, 1.0),
                                                    horizontalScroll_incButton_frameColor=(0, 0, 0, 1.0),
                                                    horizontalScroll_decButton_frameColor=(0, 0, 0, 1.0),
                                                    verticalScroll_thumb_frameColor=(0.4, 0.3, 0.2, 1.0),
                                                    horizontalScroll_thumb_frameColor=(0.4, 0.3, 0.2, 1.0),
                                                    parent=self.frame_journal)

        self.quest_desc_frame_img = OnscreenImage(image=self.images['journal_quest_desc'],
                                                  scale=(0.7, 1, 0.4),
                                                  pos=(0.2, 0, -0.1),
                                                  parent=self.quest_desc_frame.getCanvas())
        self.quest_desc_frame_img.set_transparency(TransparencyAttrib.MAlpha)

        self.quest_frame_map_img = OnscreenImage(image=self.images['journal_ancient_map_sm'],
                                                 scale=(0.7, 0, 0.4),
                                                 pos=(-0.82, 0, -0.45),
                                                 parent=self.frame_journal)
        self.quest_frame_map_img.set_transparency(TransparencyAttrib.MAlpha)

    def set_player_properties(self):
        """ DEFINE PLAYER PROPERTIES """
        # player properties (health, stamina, etc)
        self.frame_player_prop = DirectFrame(frameColor=(0.0, 0.0, 0.0, 0.0),
                                             frameSize=self.frame_player_prop_size,
                                             pos=(-0.5, 0, -0.31),
                                             parent=self.frame_inv)
        self.frame_player_prop_img = OnscreenImage(image=self.images['inv_frm_player_props'],
                                                   pos=(-0.3, 0, -0.34),
                                                   scale=(0.9, 0, 0.3),
                                                   parent=self.frame_player_prop)

        self.frame_player_prop_img.set_transparency(TransparencyAttrib.MAlpha)
        player_props_icons = [
            self.images['prop_name'],
            self.images['prop_age'],
            self.images['prop_sex'],
            self.images['prop_height'],
            self.images['prop_weight'],
            self.images['prop_specialty'],
            self.images['prop_health'],
            self.images['prop_stamina'],
            self.images['prop_courage']
        ]
        prop_icon_pos_x = -0.9
        key_label_pos_x = -0.85
        value_label_pos_x = -0.65
        pos_z = -0.15
        for idx, key in enumerate(self.base.game_instance['player_props']):

            if idx == 5:
                # reset z position for second column
                pos_z = -0.15
            if idx >= 5:
                # make second column
                prop_icon_pos_x = -0.3
                key_label_pos_x = -0.25
                value_label_pos_x = 0.0

            prop_txt = str(self.base.game_instance['player_props'][key])
            pos_z += -0.07
            prop_icon = OnscreenImage(image=player_props_icons[idx],
                                      pos=(prop_icon_pos_x, 0, pos_z + 0.01),
                                      scale=.03,
                                      parent=self.frame_player_prop)
            prop_icon.set_transparency(TransparencyAttrib.MAlpha)

            DirectLabel(text="{0}:".format(key),
                        text_fg=(0.1, 0.1, 0.1, 1),
                        text_font=self.font.load_font(self.menu_font),
                        text_align=TextNode.ALeft,
                        frameColor=(255, 255, 255, 0),
                        scale=.04, borderWidth=(self.w, self.h),
                        pos=(key_label_pos_x, 0, pos_z),
                        parent=self.frame_player_prop)
            DirectLabel(text=prop_txt,
                        text_fg=(0.1, 0.1, 0.1, 1),
                        text_font=self.font.load_font(self.menu_font),
                        text_align=TextNode.ALeft,
                        frameColor=(255, 255, 255, 0),
                        scale=.04, borderWidth=(self.w, self.h),
                        pos=(value_label_pos_x, 0, pos_z),
                        parent=self.frame_player_prop)

    def refresh_player_properties(self):
        if self.frame_player_prop:
            self.frame_player_prop.destroy()

            # player properties (health, stamina, etc)
            self.frame_player_prop = DirectFrame(frameColor=(0.0, 0.0, 0.0, 0.0),
                                                 frameSize=self.frame_player_prop_size,
                                                 pos=(-0.5, 0, -0.31),
                                                 parent=self.frame_inv)
            self.frame_player_prop_img = OnscreenImage(image=self.images['inv_frm_player_props'],
                                                       pos=(-0.3, 0, -0.34),
                                                       scale=(0.9, 0, 0.3),
                                                       parent=self.frame_player_prop)

            self.frame_player_prop_img.set_transparency(TransparencyAttrib.MAlpha)
            player_props_icons = [
                self.images['prop_name'],
                self.images['prop_age'],
                self.images['prop_sex'],
                self.images['prop_height'],
                self.images['prop_weight'],
                self.images['prop_specialty'],
                self.images['prop_health'],
                self.images['prop_stamina'],
                self.images['prop_courage']
            ]
            prop_icon_pos_x = -0.9
            key_label_pos_x = -0.85
            value_label_pos_x = -0.65
            pos_z = -0.15
            for idx, key in enumerate(self.base.game_instance['player_props']):

                if idx == 5:
                    # reset z position for second column
                    pos_z = -0.15
                if idx >= 5:
                    # make second column
                    prop_icon_pos_x = -0.3
                    key_label_pos_x = -0.25
                    value_label_pos_x = 0.0

                prop_txt = str(self.base.game_instance['player_props'][key])
                pos_z += -0.07
                prop_icon = OnscreenImage(image=player_props_icons[idx],
                                          pos=(prop_icon_pos_x, 0, pos_z + 0.01),
                                          scale=.03,
                                          parent=self.frame_player_prop)
                prop_icon.set_transparency(TransparencyAttrib.MAlpha)

                DirectLabel(text="{0}:".format(key),
                            text_fg=(0.1, 0.1, 0.1, 1),
                            text_font=self.font.load_font(self.menu_font),
                            text_align=TextNode.ALeft,
                            frameColor=(255, 255, 255, 0),
                            scale=.04, borderWidth=(self.w, self.h),
                            pos=(key_label_pos_x, 0, pos_z),
                            parent=self.frame_player_prop)
                DirectLabel(text=prop_txt,
                            text_fg=(0.1, 0.1, 0.1, 1),
                            text_font=self.font.load_font(self.menu_font),
                            text_align=TextNode.ALeft,
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
        self.frame_journal.show()
        WHEEL_UP = PGButton.get_release_prefix() + MouseButton.wheel_up().get_name() + "-"
        WHEEL_DOWN = PGButton.get_release_prefix() + MouseButton.wheel_down().get_name() + "-"
        self.quest_desc_frame.bind(WHEEL_UP, self._handle_mouse_scroll, [self.quest_desc_frame, 1])
        self.quest_desc_frame.bind(WHEEL_DOWN, self._handle_mouse_scroll, [self.quest_desc_frame, -1])
        self.quest_desc_frame.horizontalScroll.thumb.bind(WHEEL_UP, self._handle_mouse_scroll,
                                                          [self.quest_desc_frame, 1])
        self.quest_desc_frame.horizontalScroll.thumb.bind(WHEEL_DOWN, self._handle_mouse_scroll,
                                                          [self.quest_desc_frame, -1])

        self.btn_select_inv.set_pos(-1.70, 0, 0.3)
        self.btn_select_journal.set_pos(0.06, 0, 0.3)

        self.btn_select_inv["state"] = DGG.NORMAL
        self.btn_select_journal["state"] = DGG.DISABLED

    def hide_journal(self):
        self.frame_journal.hide()
        WHEEL_UP = PGButton.get_release_prefix() + MouseButton.wheel_up().get_name() + "-"
        WHEEL_DOWN = PGButton.get_release_prefix() + MouseButton.wheel_down().get_name() + "-"
        self.quest_desc_frame.unbind(WHEEL_UP)
        self.quest_desc_frame.unbind(WHEEL_DOWN)
        self.quest_desc_frame.horizontalScroll.thumb.unbind(WHEEL_UP)
        self.quest_desc_frame.horizontalScroll.thumb.unbind(WHEEL_DOWN)

        self.btn_select_inv.set_pos(-1.70, 0, 0.3)
        self.btn_select_journal.set_pos(0.06, 0, 0.3)

        self.btn_select_journal["state"] = DGG.NORMAL
        self.btn_select_inv["state"] = DGG.DISABLED

    def is_player_ready(self):
        """ Checks if player ready to be rendered on the character sheet
        """
        player = self.base.game_instance['player_ref']
        if (player
                and base.player_states["is_alive"]
                and base.player_states["is_idle"]
                and not base.player_states["is_moving"]
                and not base.player_states["is_running"]
                and not base.player_states["is_crouch_moving"]
                and not base.player_states["is_crouching"]
                and not base.player_states["is_standing"]
                and not base.player_states["is_jumping"]
                and not base.player_states["is_h_kicking"]
                and not base.player_states["is_f_kicking"]
                and not base.player_states["is_using"]
                and not base.player_states["is_attacked"]
                and not base.player_states["is_busy"]
                and not base.player_states["is_turning"]
                and not base.player_states["is_mounted"]
                and not base.player_states["horse_riding"]
                and not self.base.game_instance["is_player_sitting"]
                and not player.get_python_tag("is_on_horse")
        ):
            return True
        else:
            return False

    def set_sheet(self):
        """ Sets inventory ui """
        if (not self.base.game_instance['menu_mode']
                and not self.base.game_instance["item_menu_mode"]
                and not self.base.game_instance['esc_mode']
                and not self.base.game_instance["chest_ui_mode"]
                and self.is_player_ready()):
            if self.frame_inv:
                if self.frame_inv.is_hidden():

                    if self.base.game_instance['hud_np']:
                        self.base.game_instance['hud_np'].toggle_all_hud(state="hidden")
                    base.game_instance['render_attr_cls'].time_text_ui.hide()

                    self.reset_camera_params()

                    self.frame_inv.show()
                    self.btn_select_inv.show()
                    self.btn_select_journal.show()

                    self.btn_select_inv["state"] = DGG.DISABLED
                    self.btn_select_journal["state"] = DGG.NORMAL

                    self.base.win_props.set_cursor_hidden(False)
                    self.base.win.request_properties(self.base.win_props)

                    self.base.game_instance['ui_mode'] = True
                    self.base.is_inventory_active = True
                    self.prepare_character()

                    self.toggle()

                    # Stop item dragging on right mouse
                    base.accept('mouse3-up', self.stop_drag)

                    # 'on item move' event processing
                    # in this case we are delete item, which has been placed into the 'TRASH'
                    base.accept('inventory-item-move', self.on_item_move)
                    self.refresh_items()
                    self.update_counters()
                    self.refresh_player_properties()
                else:
                    self.clear_sheet()

    def clear_sheet(self):
        self.base.build_info.reparent_to(aspect2d)
        self.frame_inv.hide()

        self.btn_select_inv.hide()
        self.btn_select_journal.hide()

        self.frame_journal.hide()

        self.toggle()

        self.base.win_props.set_cursor_hidden(True)
        self.base.win.request_properties(self.base.win_props)
        self.base.game_instance['ui_mode'] = False

        self.revert_character()

        if render.find("**/bg_black_char_sheet"):
            bg_black = render.find("**/bg_black_char_sheet")
            bg_black.hide()

        # Show world after inventory
        if render.find("**/World"):
            render.find("**/World").show()

        # Show foliage after inventory
        for np in self.base.game_instance['foliage_np'].get_children():
            np.show()

        self.base.is_inventory_active = False

    def reset_camera_params(self):
        player = self.base.game_instance["player_ref"]

        player_pos = player.get_pos()
        target_x = player_pos[0] + -1.05
        target_y = player_pos[1] + -4.5
        target_z = player_pos[2] + 0.25

        player.hide()

        lerp_pos_inv = LerpPosInterval(base.camera,
                                       duration=1.1,
                                       pos=Point3(target_x, target_y, target_z),
                                       startPos=base.camera.get_pos()
                                       )
        Sequence(lerp_pos_inv,
                 Func(player.show)
                 ).start()

        base.camera.set_hpr(0, 0, 0)

    def set_character_sheet_background(self):
        geoms = self.base.inventory_geoms_collector()
        if geoms:
            self.char_sheet_bg = self.base.loader.load_model(geoms["bg_black_char_sheet"])
            self.char_sheet_bg.set_name("bg_black_char_sheet")
            player_rb_np = self.base.game_instance["player_np"]
            if player_rb_np:
                self.char_sheet_bg.reparent_to(player_rb_np)
                # self.char_sheet_bg.set_pos(0, 0, 0)
                self.char_sheet_bg.set_h(player_rb_np.get_h())
                self.char_sheet_bg.set_two_sided(True)
                self.char_sheet_bg.hide()

    def prepare_character(self):
        self.base.game_instance['inv_mode'] = True
        if self.base.is_inventory_active:
            self.base.game_instance["lens"].set_fov(self.base.game_instance["fov_outdoor"])

            # Hide world from inventory
            if render.find("**/World"):
                render.find("**/World").hide()

            # Hide foliage from inventory
            for np in self.base.game_instance['foliage_np'].get_children():
                np.hide()

            # keep default state of player camera
            self.player_camera_default["pos"] = base.camera.get_pos()
            self.player_camera_default["hpr"] = base.camera.get_hpr()

            if render.find("**/pivot"):
                self.player_camera_default["pivot_hpr"] = render.find("**/pivot").get_hpr()

            player = self.base.game_instance["player_ref"]
            if player:
                # set character view
                player_pos = player.get_pos()
                base.camera.set_x(player_pos[0] + -1.05)
                base.camera.set_y(player_pos[1] + -4.5)
                base.camera.set_z(player_pos[2] + 0.25)

                base.camera.set_hpr(0, 0, 0)
                if render.find("**/pivot"):
                    render.find("**/pivot").set_hpr(24.6, -0.999999, 0)

                # Show character sheet background
                self.char_sheet_bg.show()

                # set light
                player_rb_np = self.base.game_instance["player_np"]
                if player_rb_np:
                    # keep previous player hpr states
                    self.player_hpr_saved = player_rb_np.get_hpr()

                    # face player to light
                    player_rb_np.set_h(0)

                    light_pos = [player_rb_np.get_x(), player_rb_np.get_y() - 4.0, 8.0]
                    base.game_instance['render_attr_cls'].set_inv_lighting(name='slight',
                                                                           render=render,
                                                                           pos=light_pos,
                                                                           hpr=[0, 0.4, -1],
                                                                           color=[2.0],
                                                                           task="attach")

    def revert_character(self):
        self.base.game_instance['inv_mode'] = False
        self.base.game_instance["lens"].set_fov(self.base.game_instance["fov_indoor"])

        # Revert character view
        player_rb_np = self.base.game_instance["player_np"]
        if player_rb_np:
            player_rb_np.set_hpr(self.player_hpr_saved)

        player_cam_pos = self.player_camera_default["pos"]
        player_cam_hpr = self.player_camera_default["hpr"]
        pivot_hpr = self.player_camera_default["pivot_hpr"]
        base.camera.set_pos(player_cam_pos)
        base.camera.set_hpr(player_cam_hpr)
        if render.find("**/pivot"):
            render.find("**/pivot").set_hpr(pivot_hpr)

        # Hide character sheet background
        self.char_sheet_bg.hide()

        # Show world again
        if render.find("**/World"):
            render.find("**/World").show()

        base.game_instance['render_attr_cls'].clear_inv_lighting()
