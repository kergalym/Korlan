import json
from os.path import exists

from direct.gui.DirectGui import *
from direct.gui.DirectButton import DirectButton
from direct.gui.DirectFrame import DirectFrame
from direct.gui.OnscreenText import OnscreenText
from direct.showbase.ShowBaseGlobal import globalClock
from direct.task.TaskManagerGlobal import taskMgr
from panda3d.core import TextNode, FontPool, TransparencyAttrib

from Engine.Inventory.item import Item
from Engine.Inventory.slot import Slot
from Engine.Inventory.popup import Popup
from Engine.Inventory.equip import Equip
from Settings.menu_settings import MenuSettings


class Inventory:

    def __init__(self):
        self.base = base
        self.game_dir = base.game_dir
        self.ui_geoms = base.ui_geom_collector()
        self.images = base.textures_collector(path="Settings/UI")
        self.fonts = base.fonts_collector()
        self.lng_configs = base.cfg_collector(path="{0}/Configs/Language/".format(self.game_dir))
        # instance of the abstract class
        self.font = FontPool
        self.text = TextNode("TextNode")
        self.m_settings = MenuSettings()

        self.cfg_path = self.base.game_cfg
        if exists(self.cfg_path):
            lng_to_load = self.m_settings.input_validate(self.cfg_path, 'lng')
            with open(self.lng_configs['lg_{0}'.format(lng_to_load)], 'r') as json_file:
                self.language = json.load(json_file)

        """ Global Border Width """
        self.w = 0
        self.h = 0

        """ Frame Sizes """
        # Left, right, bottom, top
        self.frame_inv_size = [-3, 3, -1, 3]
        self.frame_inv_black_bg_size = [-3, 0.7, -1, 3]

        """ Frames, Buttons & Fonts"""
        # Transparent background
        self.frame_inv = DirectFrame(frameColor=(0, 0, 0, 0.0),
                                     frameSize=self.frame_inv_size,
                                     pos=(0, 0, 0))
        self.frame_inv.hide()

        self.sheet_items = None

        self.inv_misc_grid_cap = None
        self.inv_weapons_grid_cap = None
        self.inv_magic_grid_cap = None

        self.menu_font = self.fonts['OpenSans-Regular']

        """ Inventory attributes"""
        self.bg_size = [-3, 3, -1, 3]

        self.default_slot_ico = self.images["default_slot"]
        self.slot_half_size_x = 0.18 * 0.5
        self.slot_half_size_y = 0.18 * 0.5
        self.slot_margin = 0.001 * 0.5
        self.item_half_size_x = 0.16 * 0.5
        self.item_half_size_y = 0.16 * 0.5
        self.frame_slot_size = (-self.slot_half_size_x,
                                self.slot_half_size_x,
                                -self.slot_half_size_y,
                                self.slot_half_size_y)

        self.popup_delay = 0.5
        self.popup_bg = (0, 0, 0, 0.92)
        self.popup_fg = (1, 1, 1, 1)
        self.popup_font = self.fonts['OpenSans-Regular']

        self.use_transparency = True

        self.states = {
            "HIDDEN": False,
            "VISIBLE": True
        }
        self.current_state = None  # VISIBLE or HIDDEN
        self.current_target = ''
        self.drag_item = -1  # if >=0 then we drag item with this id
        self.slots = []  # list of InvSlot (data)
        self._slots_vis = []

        self.items = []  # list of items (data)
        self._items_vis = []

        self._counters = {}
        self.old_mp = (0, 0)

        self.slot_under_mouse = -1  # slot id under mouse cursor
        self.item_under_mouse = -1  # item id under mouse cursor

        self.popup_timer = 0.0  # hint popup time
        self.popup = Popup(self.popup_bg, self.popup_fg, self.popup_font)
        self.equip = Equip()

        self.is_inventory_items_loaded = False

    def set_inventory(self):
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
                                            parent=self.frame_inv)
        hand_l_styled_frame.set_transparency(TransparencyAttrib.MAlpha)

        hand_r_styled_frame = OnscreenImage(image=sheet_slot_frame_img,
                                            pos=(1.7, 0, -0.01),
                                            scale=sheet_slot_frame_scale,
                                            parent=self.frame_inv)
        hand_r_styled_frame.set_transparency(TransparencyAttrib.MAlpha)

        tengri_pwr_styled_frame = OnscreenImage(image=sheet_slot_frame_img,
                                                pos=(1.7, 0, -0.35),
                                                scale=sheet_slot_frame_scale,
                                                parent=self.frame_inv)
        tengri_pwr_styled_frame.set_transparency(TransparencyAttrib.MAlpha)

        umai_pwr_styled_frame = OnscreenImage(image=sheet_slot_frame_img,
                                              pos=(1.7, 0, -0.67),
                                              scale=sheet_slot_frame_scale,
                                              parent=self.frame_inv)
        umai_pwr_styled_frame.set_transparency(TransparencyAttrib.MAlpha)

        head_styled_frame = OnscreenImage(image=sheet_slot_frame_img,
                                          pos=(0.9, 0, 0.7),
                                          scale=sheet_slot_frame_scale,
                                          parent=self.frame_inv)
        head_styled_frame.set_transparency(TransparencyAttrib.MAlpha)

        body_styled_frame = OnscreenImage(image=sheet_slot_frame_img,
                                          pos=(1.7, 0, 0.32),
                                          scale=sheet_slot_frame_scale,
                                          parent=self.frame_inv)
        body_styled_frame.set_transparency(TransparencyAttrib.MAlpha)

        feet_styled_frame = OnscreenImage(image=sheet_slot_frame_img,
                                          pos=(0.9, 0, -0.43),
                                          scale=sheet_slot_frame_scale,
                                          parent=self.frame_inv)
        feet_styled_frame.set_transparency(TransparencyAttrib.MAlpha)

        legs_styled_frame = OnscreenImage(image=sheet_slot_frame_img,
                                          pos=(0.9, 0, -0.76),
                                          scale=sheet_slot_frame_scale,
                                          parent=self.frame_inv)
        legs_styled_frame.set_transparency(TransparencyAttrib.MAlpha)

        trash_styled_frame = OnscreenImage(image=sheet_slot_frame_img,
                                           pos=(0.4, 0, -0.6),
                                           scale=sheet_slot_frame_scale,
                                           parent=self.frame_inv)
        trash_styled_frame.set_transparency(TransparencyAttrib.MAlpha)

        """(('INVENTORY_1', 'TRASH'), 'item',
            self.images['slot_item_qymyran'], 'Qymyran', 1, 1, 0, 8),
           (('INVENTORY_1', 'TRASH'), 'item',
            self.images['slot_item_torsyk'], 'Torsyk', 1, 1, 0, 8),"""

        # Inventory row, slots, inventory_type, icon, txt_pieces, int_pieces, 0, damage
        self.sheet_items = [
            [['INVENTORY_2', 'TRASH', 'HAND_L'], 'weapon',
             self.images['slot_item_sword'], 'Sword', 1, 1, 0, 38],
            [['INVENTORY_2', 'TRASH', 'HAND_R'], 'weapon',
             self.images['slot_item_bow'], 'Bow', 1, 1, 0, 9],
            [['INVENTORY_2', 'TRASH', 'BODY'], 'armor',
             self.images['slot_item_armor'], 'Light armor', 1, 1, 10],
            [['INVENTORY_2', 'TRASH', 'HEAD'], 'armor',
             self.images['slot_item_helmet'], 'Helmet', 1, 1, 5],
            [['INVENTORY_2', 'TRASH', 'FEET'], 'armor',
             self.images['slot_item_feet'], 'Pants', 1, 1, 2],
            [['INVENTORY_2', 'TRASH', 'LEGS'], 'armor',
             self.images['slot_item_boots'], 'Boots', 1, 1, 2],
            [['INVENTORY_3', 'TENGRI_PWR'], 'weapon',
             self.images['slot_item_tengri'], 'Tengri Power', 1, 1, 0, 8],
            [['INVENTORY_3', 'UMAI_PWR'], 'weapon',
             self.images['slot_item_umai'], 'Umai Power', 1, 1, 0, 8]
        ]

        # sheet slots init
        self.custom_inv_slots(sheet_slot_info)

        # Field of slots 3х5,        positions: x, y
        self.fill_up_inv_slots(3, 5, -1.55, 0.66, 'INVENTORY_1')
        self.fill_up_inv_slots(3, 5, -1.0, 0.66, 'INVENTORY_2')
        self.fill_up_inv_slots(3, 5, -0.45, 0.66, 'INVENTORY_3')

        for item in self.sheet_items:
            inventory_type = item[0][0]
            self.add_item(Item(item), inventory_type)

        # Inventory init
        self.init()

        self.inv_misc_grid_cap = OnscreenImage(image=self.images['misc_grid_cap'],
                                               pos=(-1.4, 0, -0.25),
                                               scale=(0.32, 0, 0.1),
                                               parent=self.frame_inv)
        self.inv_misc_grid_cap.set_transparency(TransparencyAttrib.MAlpha)
        self.inv_weapons_grid_cap = OnscreenImage(image=self.images['weapons_grid_cap'],
                                                  pos=(-0.82, 0, -0.25),
                                                  scale=(0.32, 0, 0.1),
                                                  parent=self.frame_inv)
        self.inv_weapons_grid_cap.set_transparency(TransparencyAttrib.MAlpha)
        self.inv_magic_grid_cap = OnscreenImage(image=self.images['magic_grid_cap'],
                                                pos=(-0.24, 0, -0.25),
                                                scale=(0.32, 0, 0.1),
                                                parent=self.frame_inv)
        self.inv_magic_grid_cap.set_transparency(TransparencyAttrib.MAlpha)

        # left is item index, right is slot index
        self.on_start_assign_item_to_sheet_slot(3, 4)  # helmet
        self.on_start_assign_item_to_sheet_slot(2, 5)  # armor
        self.on_start_assign_item_to_sheet_slot(4, 6)  # pants
        self.on_start_assign_item_to_sheet_slot(5, 7)  # boots
        self.on_start_assign_item_to_sheet_slot(0, 0)  # sword
        self.on_start_assign_item_to_sheet_slot(1, 1)  # bow

    def add_item_to_inventory(self, item, count, inventory, inventory_type):
        if (item and isinstance(item, str)
                and inventory and isinstance(inventory, str)
                and inventory_type and isinstance(inventory_type, str)
                and count and isinstance(count, int)):
            item_is_matched = 0
            matched_item = None
            for sheet_item in self.sheet_items:
                if item == sheet_item[3]:
                    item_is_matched = 1
                    matched_item = sheet_item

            if item_is_matched == 0:
                item_row = [[inventory, 'TRASH'], inventory_type,
                            self.images['slot_item_{0}'.format(item.lower())],
                            item, count, count, 0, 5
                            ]
                inventory_type = item_row[0][0]
                self.sheet_items.append(item_row)
                self.add_item(Item(item_row), inventory_type)
                self.refresh_items()
                self.base.game_instance['arrow_count'] = count
            elif item_is_matched == 1:
                new_count = matched_item[4] + count
                item_row = [[inventory, 'TRASH'], inventory_type,
                            self.images['slot_item_{0}'.format(item.lower())],
                            item, new_count, new_count, 0, 5
                            ]
                inventory_type = item_row[0][0]
                self.sheet_items.append(item_row)
                self.add_item(Item(item_row), inventory_type)
                self.refresh_items()
                self.base.game_instance['arrow_count'] = new_count

    def init(self):
        self._visualize_slots()
        self._visualize_items()
        self._make_counters()
        self.hide()

    def show(self):
        """ Show inventory
        """
        taskMgr.add(self.drag_task, 'Drag task')
        taskMgr.add(self.popup_task, 'Inventory popup task')
        self.current_state = self.states["VISIBLE"]

    def hide(self):
        """ Hide all and stop tasks
        """
        self.stop_drag()
        taskMgr.remove('Drag task')
        taskMgr.remove('Inventory popup task')
        self.current_state = self.states["HIDDEN"]

    def toggle(self):
        """ Switch inventory visibility
        """
        if self.current_state == self.states["VISIBLE"]:
            self.hide()
        else:
            self.show()

    def _visualize_slots(self):
        """ Make background and slots visualization from prepared data
        """
        self.inv_grid_frame = OnscreenImage(image=self.images['grid_frame'],
                                            pos=(-0.82, 0, 0.30),
                                            scale=(0.86, 0, 0.48),
                                            parent=self.frame_inv)
        self.inv_grid_cap = OnscreenImage(image=self.images['grid_cap_i'],
                                          pos=(-0.82, 0, 0.82),
                                          scale=(0.92, 0, 0.08),
                                          parent=self.frame_inv)
        if self.use_transparency:
            self.inv_grid_cap.set_transparency(TransparencyAttrib.MAlpha)
            self.inv_grid_frame.set_transparency(TransparencyAttrib.MAlpha)

        for id, slot in enumerate(self.slots):
            self._slots_vis.append(DirectButton(frameTexture=slot.get_icon(),
                                                pos=slot.pos,
                                                frameSize=self.frame_slot_size,
                                                pad=(0.5, 0.5),
                                                relief=1,
                                                rolloverSound=None,
                                                command=self.on_slot_click,
                                                extraArgs=[id]))
            self._slots_vis[id].bind(DGG.ENTER, self.on_slot_enter, [id])
            self._slots_vis[id].bind(DGG.EXIT, self.on_slot_exit, [id])
            self._slots_vis[id].reparent_to(self.frame_inv)
            if self.use_transparency:
                self._slots_vis[id].set_transparency(TransparencyAttrib.MAlpha)

    def _visualize_items(self):
        """ Inventory items visualization
        """
        for id, item in enumerate(self.items):
            i_pos = self.slots[item.slot_id].pos
            self._items_vis.append(DirectButton(frameTexture=item.get_icon(),
                                                pos=i_pos,
                                                frameSize=(-self.item_half_size_x,
                                                           self.item_half_size_x,
                                                           -self.item_half_size_y,
                                                           self.item_half_size_y),
                                                pad=(0.5, 0.5), relief=1,
                                                rolloverSound=None,
                                                command=self.on_item_click,
                                                extraArgs=[id]))
            self._items_vis[id].bind(DGG.ENTER, self.on_item_enter, [id])
            self._items_vis[id].bind(DGG.EXIT, self.on_item_exit, [id])
            self._items_vis[id].reparent_to(self.frame_inv)
            if self.use_transparency:
                self._items_vis[id].set_transparency(TransparencyAttrib.MAlpha)

    def _make_counters(self):
        """ Make counter text for multiple items
        """
        for id, item in enumerate(self.items):
            if item.get_max_count() > 1:
                self._counters[id] = OnscreenText(text=str(item.count),
                                                  pos=(0, 0, 0),
                                                  fg=(1, 0.2, 0.2, 1),
                                                  scale=0.04,
                                                  mayChange=True)
                self._counters[id].reparent_to(self._items_vis[id])
                self._counters[id].setPos(self.item_half_size_x * 0.5,
                                          -self.item_half_size_x * 0.8)

    def update_counters(self):
        for id, item in enumerate(self.items):
            if item.get_max_count() > 1:
                self._counters[id]['text'] = str(item.count)
                # update arrow count
                if id == 8 and self.base.game_instance['arrow_count'] > 1:
                    count = self.base.game_instance['arrow_count']
                    self._counters[id]['text'] = str(count)

    def refresh_items(self):
        """ Remove old items vis. and create new
        """
        for iv in self._items_vis:
            iv.destroy()
        for c in self._counters.values():
            c.destroy()
        self._items_vis = []
        self._counters = {}
        self._visualize_items()
        self._make_counters()

    def add_item(self, item, target):
        """ Add new item data. To make it visible needs to call refresh_items
        """
        id = self.find_first_empty_slot(target)
        old_id = item.slot_id

        # merge item if equal
        if (self.items and self.items[old_id].get_type() == item.get_type()
                and self.items[old_id].get_max_count() > 1
                and item.get_max_count() > 1):
            self.items[old_id].count = item.count
            self.update_counters()
            self.current_target = target
            return True
        else:
            if id >= 0:
                item.slot_id = id
                self.items.append(item)
                self.current_target = target
                return True
        return False

    def drop_item_to(self, iid, target):
        """ Move item to first empty slot with type of 'target' if
        possible, otherwise - remove item
        """
        id = self.find_first_empty_slot(target)
        if id >= 0:
            self.move_item_to_slot(iid, id)
        else:
            self.remove_item(iid)

    def move_item_to_slot(self, iid, sid, force=False):
        """ Move item with id 'iid' to slot with id 'sid'
        """
        if not self.is_slot_busy(sid, [iid]) or force:
            if self.slots[sid].type in self.items[iid].get_slots():
                old_sid = self.items[iid].slot_id
                self.items[iid].slot_id = sid
                self._items_vis[iid].setPos(self.slots[sid].pos)
                base.messenger.send('inventory-item-move', [iid, old_sid, sid])
                return True
        self.stop_drag()
        return False

    def remove_item(self, id):
        """ Fully remove item
        """
        if self._counters.get(id):
            self._counters[id].destroy()
            del self._counters[id]
        if self.item_under_mouse == id:
            self.item_under_mouse = -1
        if self.drag_item == id:
            self.stop_drag()
        self._items_vis[id].destroy()
        del self._items_vis[id]
        del self.items[id]
        self.refresh_items()

    def stop_drag(self):
        """ Stop item dragging and return it to the slot
        """
        if self.drag_item >= 0:
            item = self.items[self.drag_item]
            self._items_vis[self.drag_item].setPos(self.slots[item.slot_id].pos)
            self._items_vis[self.drag_item].setBin('unsorted', 1000)
            self.drag_item = -1

    def get_slots_by_type(self, s_type):
        """ Return slot's IDs list, which type is 's_type'
        """
        slots = []
        for id, slot in enumerate(self.slots):
            if slot.type == s_type:
                slots.append(id)
        return slots

    def on_slot_click(self, *args):
        """ Slot click callback. Try to drop item into the clicked slot.
        """
        if self.drag_item >= 0:
            if self.move_item_to_slot(self.drag_item, args[0]):
                self.stop_drag()

                # toggle player clothes visibility
                if self.slots[args[0]].type == "HEAD":
                    self.equip.toggle_cloth_visibility(item="helmet")
                elif self.slots[args[0]].type == "BODY":
                    self.equip.toggle_cloth_visibility(item="armor")
                elif self.slots[args[0]].type == "FEET":
                    self.equip.toggle_cloth_visibility(item="pants")
                elif self.slots[args[0]].type == "LEGS":
                    self.equip.toggle_cloth_visibility(item="boots")
                # switch weapon
                if self.slots[args[0]].type == "HAND_R":
                    self.equip.toggle_weapon(item="bow_kazakh", bone="Korlan:Spine1")
                elif self.slots[args[0]].type == "HAND_L":
                    self.equip.toggle_weapon(item="sword", bone="Korlan:Spine1")

    def on_item_click(self, *args):
        """ Item click callback. Try to capture the item or replace
        item in the slot
        """
        # Capture clicked item
        if self.drag_item < 0:
            # toggle player clothes visibility
            if self.items[args[0]].slot_id == 4:
                self.equip.toggle_cloth_visibility(item="helmet")
            elif self.items[args[0]].slot_id == 5:
                self.equip.toggle_cloth_visibility(item="armor")
            elif self.items[args[0]].slot_id == 6:
                self.equip.toggle_cloth_visibility(item="pants")
            elif self.items[args[0]].slot_id == 7:
                self.equip.toggle_cloth_visibility(item="boots")
            # switch weapon
            if self.items[args[0]].slot_id == 1:
                self.equip.toggle_weapon(item="bow_kazakh", bone="Korlan:Spine1")
            elif self.items[args[0]].slot_id == 0:
                self.equip.toggle_weapon(item="sword", bone="Korlan:Spine1")

            self.drag_item = args[0]
            self._items_vis[self.drag_item].setBin('gui-popup', 9999)
        # Merge items if possible
        elif (self.items[args[0]].get_type() == self.items[self.drag_item].get_type()
              and self.items[args[0]].get_max_count() > 1
              and self.items[self.drag_item].get_max_count() > 1):
            diff = self.items[args[0]].get_max_count() - self.items[args[0]].count
            if diff < self.items[self.drag_item].count:
                self.items[args[0]].count += diff
                self.items[self.drag_item].count -= diff
            else:
                self.items[args[0]].count += self.items[self.drag_item].count
                self.remove_item(self.drag_item)
            self.stop_drag()
            self.update_counters()
        # otherwise replace an item in the slot and drop or remove old item to the inventory
        elif self.move_item_to_slot(self.drag_item, self.items[args[0]].slot_id, force=True):
            self.drop_item_to(args[0], self.current_target)
            self.stop_drag()

    def on_slot_enter(self, *args):
        """ Slot mouse entering callback
        """
        self.slot_under_mouse = args[0]

    def on_slot_exit(self, *args):
        """ Slot mouse exiting callback
        """
        if self.slot_under_mouse == args[0]:
            self.slot_under_mouse = -1

    def on_item_enter(self, *args):
        """ Item mouse entering callback
        """
        self.item_under_mouse = args[0]

    def on_item_exit(self, *args):
        """ Item mouse exiting callback
        """
        if self.item_under_mouse == args[0]:
            self.item_under_mouse = -1

    def drag_task(self, task):
        """ Follow captured item to the mouse cursor
        """
        if self.drag_item >= 0:
            if base.mouseWatcherNode.hasMouse():
                x = base.mouseWatcherNode.getMouseX() * base.getAspectRatio() + (self.item_half_size_x + 0.01)
                y = base.mouseWatcherNode.getMouseY() - (self.item_half_size_y + 0.01)
                self._items_vis[self.drag_item].setPos(x, 0, y)
        return task.cont

    def popup_task(self, task):
        """ Popup hint task
        """
        if base.mouseWatcherNode.hasMouse():
            x = base.mouseWatcherNode.getMouseX() * base.getAspectRatio()
            y = base.mouseWatcherNode.getMouseY()
            if self.old_mp == (x, y):
                self.popup_timer += globalClock.getDt()
            else:
                self.popup_timer = 0
                if self.popup.current_state == self.states["VISIBLE"]:
                    self.popup.hide()
            if self.popup_timer > self.popup_delay and \
                    self.popup.current_state == self.states["HIDDEN"]:
                if self.item_under_mouse >= 0 and self.drag_item < 0:
                    txt = self.items[self.item_under_mouse].get_info()
                    self.popup.show(txt, (x + 0.01, 0, y + 0.01), bound=self.bg_size)
                elif self.slot_under_mouse >= 0:
                    txt = self.slots[self.slot_under_mouse].get_info()
                    self.popup.show(txt, (x + 0.01, 0, y + 0.01), bound=self.bg_size)
            self.old_mp = (x, y)
        return task.cont

    def on_item_move(self, *args):
        iid, s_from, s_to = args
        if self.slots[s_to].type == 'TRASH':
            self.remove_item(iid)

    def is_slot_busy(self, id, except_id=[]):
        """ Check whether the slot is busy. """
        for i, item in enumerate(self.items):
            if item.slot_id == id and i not in except_id:
                return True
        return False

    def fill_up_inv_slots(self, sx, sy, dx, dy, sltype):
        """ Add (sx,sy) array of slots with (dx,dy) displace """
        for y in range(sy):
            for x in range(sx):
                fx = self.slot_half_size_x * 2 + self.slot_margin * 2
                fy = self.slot_half_size_y * 2 + self.slot_margin * 2
                pos = (fx * x + dx, 0, -fy * y + dy)
                slot_args = (sltype, pos, '', self.default_slot_ico)
                self.slots.append(Slot(slot_args))

    def on_start_assign_item_to_sheet_slot(self, iid, sid):
        """ Startup assign sheet slot """
        self.items[iid].slot_id = sid
        self._items_vis[iid].setPos(self.slots[sid].pos)
        self.refresh_items()

    def custom_inv_slots(self, slots_data):
        """ Make slots from list
        """
        for si in slots_data:
            self.slots.append(Slot(si))

    def find_first_empty_slot(self, sltype):
        """ Find first empty slots with type of 'sltype' and return id
        """
        for id, slot in enumerate(self.slots):
            if slot.type == sltype:
                if not self.is_slot_busy(id):
                    return id
        return -1
