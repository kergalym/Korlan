from direct.interval.FunctionInterval import Func
from direct.interval.LerpInterval import LerpPosInterval
from direct.interval.MetaInterval import Sequence
from direct.showbase.ShowBaseGlobal import aspect2d
from direct.gui.DirectGui import *
from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.OnscreenImage import TransparencyAttrib
from panda3d.core import Vec3, PGButton, MouseButton, Point3

from Engine.ChestInventory.chest_inventory import ChestInventory
from panda3d.core import TextNode


class ChestUI(ChestInventory):

    def __init__(self):
        ChestInventory.__init__(self)
        """ Frame Sizes """
        # Left, right, bottom, top
        self.frame_player_prop_size = [-1.15, 0.5, -0.7, 0]

        """ Frame Colors """
        self.frm_opacity = 1

        """ Buttons, Label Scaling """
        self.lbl_scale = .03
        self.btn_scale = .03

        """ Sheet Params """
        self.sound_gui_click = None

        self.btn_close_inv = None

        self.frame_player_prop = None
        self.frame_player_prop_img = None

        # object click n move
        self.base.is_inventory_active = False
        self.is_inventory_items_loaded = False

    def chest_init(self):
        self.base.build_info.reparent_to(self.frame_inv)

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
                                          command=self.hide_chest,
                                          pos=(-1.8, 0, 0.9),
                                          parent=self.frame_inv)

        self.set_inventory()

    def show_chest(self):
        """ Shows inventory ui """
        if (not self.base.game_instance['menu_mode']
                and not self.base.game_instance["item_menu_mode"]
                and not self.base.game_instance['esc_mode']):

            self.base.game_instance["current_chest"] = self
            self.sheet.bind_chest_slots()

            if self.frame_inv:
                if self.frame_inv.is_hidden():

                    if self.base.game_instance['hud_np']:
                        self.base.game_instance['hud_np'].toggle_all_hud(state="hidden")
                    base.game_instance['render_attr_cls'].time_text_ui.hide()

                    # We don't need World and Player rendering right now
                    if render.find("**/World"):
                        render.find("**/World").hide()
                    player_rb_np = self.base.game_instance["player_np"]
                    if player_rb_np:
                        player_rb_np.hide()

                    self.frame_inv.show()
                    self.sheet.frame_inv.show()
                    self.sheet.toggle()
                    self.sheet._hide_sheet_slots()
                    self.sheet._hide_sheet_items()

                    self.base.win_props.set_cursor_hidden(False)
                    self.base.win.request_properties(self.base.win_props)

                    self.base.game_instance['ui_mode'] = True
                    self.base.game_instance['chest_ui_mode'] = True
                    self.base.is_inventory_active = True

                    self.toggle()

                    # Stop item dragging on right mouse
                    base.accept('mouse3-up', self.stop_drag)

                    # 'on item move' event processing
                    # in this case we are delete item, which has been placed into the 'TRASH'
                    base.accept('inventory-item-move', self.on_item_move)
                    self.refresh_items()
                    self.update_counters()

    def hide_chest(self):
        self.base.build_info.reparent_to(aspect2d)
        self.frame_inv.hide()
        self.sheet.frame_inv.hide()
        self.sheet._show_sheet_slots()
        self.sheet._show_sheet_items()
        self.sheet.toggle()

        # Revert back World and Player rendering
        if render.find("**/World"):
            render.find("**/World").show()
        player_rb_np = self.base.game_instance["player_np"]
        if player_rb_np:
            player_rb_np.show()

        self.toggle()

        self.base.win_props.set_cursor_hidden(True)
        self.base.win.request_properties(self.base.win_props)
        self.base.game_instance['ui_mode'] = False
        self.base.game_instance['chest_ui_mode'] = False

        self.base.is_inventory_active = False


