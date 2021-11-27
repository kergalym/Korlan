import json
import random
from os.path import exists

from direct.showbase.ShowBaseGlobal import render2d, aspect2d
from direct.task.TaskManagerGlobal import taskMgr

from Engine.Actors.Player.inventory import Inventory
from Settings.menu_settings import MenuSettings

from direct.gui.DirectGui import *
from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.OnscreenImage import TransparencyAttrib
from panda3d.core import FontPool, Camera, NodePath, CollisionNode, CollisionRay, GeomNode, CollisionTraverser, \
    CollisionHandlerQueue, Point3
from panda3d.core import TextNode
from panda3d.core import WindowProperties


class PlayerMenuUI(Inventory):

    def __init__(self):
        Inventory.__init__(self)
        self.base = base
        self.game_dir = base.game_dir
        self.images = base.textures_collector(path="{0}/Settings/UI".format(self.game_dir))
        self.inv_images = base.textures_collector(path="{0}/Assets".format(self.game_dir))
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
        self.base.frame_inv_int = None
        self.base.frame_inv = None

        """ Frame Sizes """
        # Left, right, bottom, top
        self.base.frame_inv_size = [-3, 3, -1, 3]
        self.base.frame_inv_int_canvas_size = [-2, 2.3, -2, 2]
        self.base.frame_inv_int_size = [-.5, .2, -1.3, .5]

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

        """ Buttons & Fonts"""
        self.menu_font = self.fonts['OpenSans-Regular']

        self.base.frame_inv = DirectFrame(frameColor=(0, 0, 0, 0.7),
                                          frameSize=self.base.frame_inv_size)

        self.base.build_info.reparent_to(self.base.frame_inv)

        self.base.frame_inv_int = DirectScrolledFrame(frameColor=(0, 0, 0, self.frm_opacity),
                                                      frameSize=self.base.frame_inv_int_size,
                                                      canvasSize=self.base.frame_inv_int_canvas_size,
                                                      scrollBarWidth=0.03,
                                                      autoHideScrollBars=True)

        self.base.frame_inv_int_data = DirectFrame(
            frameColor=(0, 0, 0, self.frm_opacity),
            frameSize=self.base.frame_inv_int_size,
            state=DGG.NORMAL,
            parent=pixel2d)

        ui_geoms = base.ui_geom_collector()

        maps = base.loader.loadModel(ui_geoms['btn_t_icon'])
        geoms = (maps.find('**/button_any'),
                 maps.find('**/button_pressed'),
                 maps.find('**/button_rollover'))

        sounds = self.base.sounds_collector()

        sound_gui_click = self.base.loader.load_sfx(sounds.get('zapsplat_button_click'))

        self.btn_param_decline = DirectButton(text="Cancel",
                                              text_fg=(255, 255, 255, 0.9),
                                              text_font=self.font.load_font(self.menu_font),
                                              frameColor=(255, 255, 255, self.frm_opacity),
                                              scale=self.btn_scale, borderWidth=(self.w, self.h),
                                              parent=self.base.frame_inv,
                                              geom=geoms, geom_scale=(8.1, 0, 2),
                                              clickSound=sound_gui_click,
                                              command=self.clear_ui_inventory)

        self.btn_param_accept = DirectButton(text="OK",
                                             text_fg=(255, 255, 255, 0.9),
                                             text_font=self.font.load_font(self.menu_font),
                                             frameColor=(255, 255, 255, self.frm_opacity),
                                             scale=self.btn_scale, borderWidth=(self.w, self.h),
                                             parent=self.base.frame_inv,
                                             geom=geoms, geom_scale=(5.1, 0, 2),
                                             clickSound=sound_gui_click,
                                             command=self.clear_ui_inventory)

        self.base.frame_inv.set_pos(self.pos_X, self.pos_Y, self.pos_Z)
        self.base.frame_inv_int.set_pos(self.pos_int_X, self.pos_int_Y, self.pos_int_Z)
        self.base.frame_inv_int.reparent_to(self.base.frame_inv)
        self.base.frame_inv_int.set_pos(-1.3, 0, 0.5)
        self.base.frame_inv.set_pos(0, 0, 0)
        self.base.frame_inv_int_data.set_pos(self.pos_2d(55, 32))

        self.pic_body_inv = OnscreenImage(image=self.images['body_inventory'])
        self.pic_body_inv.reparent_to(self.base.frame_inv)
        self.pic_body_inv.set_transparency(TransparencyAttrib.MAlpha)
        self.pic_body_inv.set_scale(1.5, 1.5, 0.9)
        self.pic_body_inv.set_pos(1.3, 0, 0)

        # self.pic_right.reparent_to(self.base.frame_inv)
        # self.pic_right.set_scale(0.33, 0.30, 0.30)
        # self.pic_right.set_hpr(0.0, 0.0, -90.0)
        # self.pic_left.reparent_to(self.base.frame_inv)
        # self.pic_left.set_scale(0.33, 0.30, 0.30)
        # self.pic_left.set_hpr(0.0, 0.0, -90.0)
        # self.pic_right.set_transparency(TransparencyAttrib.MAlpha)
        # self.pic_left.set_transparency(TransparencyAttrib.MAlpha)

        self.btn_param_decline.set_pos(0.1, 0, -0.9)
        self.btn_param_accept.set_pos(-1.6, 0, -0.9)

        self.base.frame_inv.hide()

        # object click n move
        self.current_dragged = None
        self.last_hover_in = None
        self.base.is_inventory_active = False
        self.is_inventory_items_loaded = False

        """self.inventory_items = {
            "head": None,
            "body": None,
            "feet": None,
            "hands": None,
            "toes": None,
            "sword": None,
            "bow": None,
            "tengri": None,
            "umai": None
        }"""
        self.inventory_items = {}

    def drag_and_drop_task(self, task=None):
        """Track the mouse pos and move self.current_dragged to where the cursor is"""
        if self.current_dragged:
            if base.mouseWatcherNode.has_mouse():
                mpos = base.mouseWatcherNode.get_mouse()
                self.current_dragged.set_pos(
                    pixel2d.get_relative_point(render2d, Point3(mpos.get_x(), 0, mpos.get_y())))
        if task:
            return task.again

    def drag(self, widget, mouse_pos=None):
        """Set the widget to be the currently dragged object"""
        if self.base.is_inventory_active:
            widget.reparent_to(self.base.frame_inv_int_data)
            self.current_dragged = widget
            self.drag_and_drop_task()

    def drop(self, mouse_pos=None):
        """Drop the currently dragged object on the last object the cursor hovered over"""
        if self.base.is_inventory_active and self.current_dragged:
            if self.last_hover_in:
                self.current_dragged.wrt_reparent_to(self.last_hover_in)
            self.current_dragged = None

    def hover_in(self, widget, mouse_pos):
        """Set the widget to be the target to drop objects onto"""
        self.last_hover_in = widget

    def hover_out(self, mouse_pos):
        """Clear the target to drop objects onto"""
        self.last_hover_in = None

    def clear_ui_inventory(self):
        """ Clears inventory ui and data """
        self.base.build_info.reparent_to(aspect2d)
        self.base.frame_inv.hide()
        self.base.frame_inv_int.hide()
        self.base.frame_inv_int_data.hide()

        if hasattr(base, "hud") and base.hud:
            base.hud.toggle_all_hud(state="visible")

        props = WindowProperties()
        props.set_cursor_hidden(True)
        self.base.win.request_properties(props)
        base.is_ui_active = False
        for key in self.inventory_items:
            item = self.inventory_items[key]
            if not render2d.find("**/{0}".format(item)).is_empty():
                render2d.find("**/{0}".format(item)).remove_node()
        # Clean inventory objects
        self.inventory_items = []
        self.current_dragged = None
        self.base.is_inventory_active = False

    def set_ui_inventory(self):
        """ Sets inventory ui """
        if base.game_mode and base.menu_mode is False:
            if self.base.frame_inv.is_hidden():

                if hasattr(base, "hud") and base.hud:
                    base.hud.toggle_all_hud(state="hidden")

                self.base.frame_inv.show()
                self.base.frame_inv_int.show()
                self.base.frame_inv_int_data.show()
                props = WindowProperties()
                props.set_cursor_hidden(False)
                self.base.win.request_properties(props)
                base.is_ui_active = True
                self.show_inventory_data()
                self.base.is_inventory_active = True
            else:
                self.clear_ui_inventory()
                self.base.is_inventory_active = False

    def pos_2d(self, x, y):
        return Point3(x, 0, -y)

    def rec_2d(self, width, height):
        return width, 0, 0, -height

    def show_inventory_data(self):
        """ Sets inventory data """
        imgs = self.base.inventory_geom_collector()
        items = []
        row = 0
        for key in imgs:
            item = imgs[key]
            items.append(item)
            row += 1
            frame = DirectFrame(frameColor=(0, 0, 0, 0),
                                frameSize=self.rec_2d(60, 50),
                                state=DGG.NORMAL,
                                image=item,
                                image_scale=(30.0, 30.0, 30.0),
                                parent=self.base.frame_inv_int_data)

            # bind the events
            frame.bind(DGG.B1PRESS, self.drag, [frame])
            frame.bind(DGG.B1RELEASE, self.drop)
            pos_y = row + 1 * 64
            pos_x = row * 64
            if len(items) == len(items) * 2:
                pos_y = row * 64
                pos_x = row + 1 * 64
            frame.set_pos(self.pos_2d(pos_x, pos_y))

            # get image name without extension
            name = item.split("/")[-1].split(".")[0]
            self.inventory_items[name] = frame

            label = OnscreenText(text="",
                                 fg=(255, 255, 255, 0.9),
                                 font=self.font.load_font(self.menu_font),
                                 align=TextNode.ALeft,
                                 mayChange=True)

            label.reparent_to(self.base.frame_inv_int)
            label.setText(name)
            label_name = "label_{0}".format(item)
            label.set_name(label_name)
            label.set_scale(0.4)
            label.set_pos(frame.get_pos())

        self.current_dragged = None
        self.last_hover_in = None
        # run a task tracking the mouse cursor
        taskMgr.add(self.drag_and_drop_task, "drag_and_drop_task", sort=-50)

    # TODO: DELETE UNUSED
    """def clear_character_display(self):
        if not render.find("**/inventory_camera").is_empty():
            render.find("**/inventory_camera").remove_node()

    def set_character_display(self):
        region = base.win.makeDisplayRegion()
        # left, right, bottom, top
        region = base.win.makeDisplayRegion(0.5, 1, 0, 1)
        cam_node = Camera('inventory_camera')
        cam_np = NodePath(cam_node)
        region.set_camera(cam_np)
        cam_np.reparent_to(base.camera)

        # View some other scene, unrelated to render
        render2 = NodePath('render2')  # the string parameter is important
        cam_np.reparentTo(render2)

        # Add player to display
        assets = self.base.assets_collector()
        player = self.base.loader.load_model(assets["Korlan"])
        cam_np.set_x(player.get_x())
        cam_np.set_y(player.get_y())
        cam_np.look_at(player)
        ## self.base.frame_inv.hide()  # test"""
