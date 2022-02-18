
import re
from os import walk
from os.path import exists

import panda3d.core as p3d
from direct.actor.Actor import Actor
from direct.gui.DirectButton import DirectButton
from direct.gui.DirectEntry import DirectEntry
from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectLabel import DirectLabel
from direct.gui.DirectRadioButton import DirectRadioButton
from direct.gui.DirectScrolledList import DirectScrolledList
from direct.gui.OnscreenText import OnscreenText
from direct.task.TaskManagerGlobal import taskMgr
from direct.showbase.ShowBase import ShowBase
from direct.stdpy import threading
from code import InteractiveConsole
from panda3d.core import *
from pathlib import Path, PurePath

from Engine.Renderer.rpcore import RenderPipeline, PointLight
from Engine.Renderer.rpcore.util.movement_controller import MovementController

import json

p3d.load_prc_file_data("", """
win-size 1920 1080
window-title Renderer Pipeline compatible Yet Another Level Editor
""")

p3d.load_prc_file_data('',
                       'win-origin -1 -2\n'
                       'show-frame-rate-meter  t\n'
                       'audio-library-name p3openal_audio\n'
                       'model-cache-dir Cache\n'
                       'model-cache-textures t\n'
                       'compressed-textures 0\n'
                       'bullet-filter-algorithm groups-mask\n'
                       'hardware-animated-vertices false\n'
                       'basic-shaders-only false\n'
                       'texture-compression f\n'
                       'driver-compress-textures f\n'
                       'want-pstats 0\n'
                       'gl-force-mipmaps t\n'
                       'hardware-animated-vertices t\n'
                       'basic-shaders-only f\n'
                       )


class Editor(ShowBase):

    def __init__(self):
        self.render_pipeline = RenderPipeline()
        self.render_pipeline.create(self)
        # Set time of day
        self.render_pipeline.daytime_mgr.time = "13:00"

        """ic_thread = threading.Thread(target=InteractiveConsole(globals()).interact)
        ic_thread.start()"""

        self.controller = MovementController(self)
        self.controller.set_initial_position_hpr(
            Vec3(-17.2912578583, -13.290019989, 6.88211250305),
            Vec3(-39.7285499573, -14.6770210266, 0.0))
        self.controller.setup()
        self.disable_mouse()

        self.game_dir = str(Path.cwd())

        """ Frame Sizes """
        # Left, right, bottom, top
        self.frame_size = [-3, -1.3, -1, 3]
        self.frame_size = [-2, 2.5, -1.5, -0.5]
        self.frame_scrolled_size = [0.0, 0.7, -0.05, 0.40]
        self.frame_scrolled_inner_size = [-0.2, 0.2, -0.00, 0.00]

        """ Frame Positions """
        self.pos_X = 0
        self.pos_Y = 0
        self.pos_Z = 0
        self.pos_int_X = -0.5
        self.pos_int_Y = 0
        self.pos_int_Z = 0.5
        self.w = 0
        self.h = 0

        """ Frames """
        self.frame = None
        self.active_asset_text = None
        self.mouse_in_asset_text = None

        """ Classes """
        # instance of the abstract class
        self.font = FontPool
        self.text = TextNode("TextNode")
        self.sound_gui_click = None
        self.menu_font = None

        """ Geoms"""
        self.menu_geom = "{0}/Editor/UI/menu_level_editor.egg".format(self.game_dir)

        """ Buttons & Fonts"""
        self.menu_font = "{0}/Settings/UI/JetBrainsMono-1.0.2/ttf/JetBrainsMono-Regular.ttf".format(self.game_dir)

        self.active_asset = None
        self.active_item = None
        self.active_asset_from_list = None
        self.active_joint_from_list = None
        self.actor_refs = {}

        self.is_asset_picked_up = False
        self.is_asset_selected = False
        self.is_asset_selected_from_list = False

        self.is_joints_list_ui_active = False

        self.asset_manipulation_modes = {
            "Positioning": True,
            "Rotation": False
        }

        self.rotation_modes = {
            "H": False,
            "P": False,
            "R": False,
        }

        self.is_item_attached_to_joint = False

        self.cur_x_dist = None
        self.cur_y_dist = None

        self.heading = 180
        self.pitch = 0
        self.rotation = 0

        self.asset_management_title = None

        self.lbl_pos_x = None
        self.lbl_pos_y = None
        self.lbl_pos_z = None

        self.lbl_rot_h = None
        self.lbl_rot_p = None
        self.lbl_rot_r = None

        self.lbl_scale_x = None
        self.lbl_scale_y = None
        self.lbl_scale_z = None

        self.inp_pos_x = None
        self.inp_pos_y = None
        self.inp_pos_z = None

        self.inp_rot_h = None
        self.inp_rot_p = None
        self.inp_rot_r = None

        self.inp_scale_x = None
        self.inp_scale_y = None
        self.inp_scale_z = None

        self.rad_scale = .025

        self.asset_management_desc = None

        self.scrolled_list_lbl_na = None
        self.scrolled_list_lbl = None
        self.scrolled_list = None
        self.scrolled_list_actor_joints_lbl = None
        self.scrolled_list_actor_joints_empty = None
        self.scrolled_list_actor_joints = None
        self.scrolled_list_lbl_desc = None
        self.scrolled_list_actor_joints_lbl_desc = None
        self.scrolled_list_actor_joints_lbl_desc_empty = None
        self.joint_item_management_title = None

        self.lbl_joint_item_pos_x = None
        self.lbl_joint_item_pos_y = None
        self.lbl_joint_item_pos_z = None

        self.lbl_joint_item_rot_h = None
        self.lbl_joint_item_rot_p = None
        self.lbl_joint_item_rot_r = None

        self.lbl_joint_item_scale_x = None
        self.lbl_joint_item_scale_y = None
        self.lbl_joint_item_scale_z = None

        self.inp_joint_item_pos_x = None
        self.inp_joint_item_pos_y = None
        self.inp_joint_item_pos_z = None

        self.inp_joint_item_rot_h = None
        self.inp_joint_item_rot_p = None
        self.inp_joint_item_rot_r = None

        self.inp_joint_item_scale_x = None
        self.inp_joint_item_scale_y = None
        self.inp_joint_item_scale_z = None

        self.joint_item_management_desc = None

        self.save_asset_pos = None
        self.save_joint_item_pos = None

        self.flame_np = None

        self.anims = {}

        self.ui_bg_np_side = None
        self.ui_bg_np_down = None

        self.assets = self.get_assets(path="/Assets/Menu")
        self.asset_load(assets=self.assets)

        """ History """
        self.history_names = {}
        self.history_steps = []
        self.history_pos_steps = []
        self.history_hpr_steps = []
        self.history_scale_steps = []

        """ Meshes """
        self.collider_plane = Plane(Vec3(0, 0, 1), Point3(0, 0, 0))
        self.mpos = None
        self.axis_arrows = self.loader.load_model("{0}/Editor/UI/axis_arrows.egg".format(self.game_dir),
                                                  noCache=True)
        self.axis_arrows.set_scale(0.5)
        self.axis_arrows.reparent_to(render)
        self.axis_arrows.hide()

        self.gizmo_mesh = self.loader.load_model("{0}/Editor/UI/gizmo_mesh.egg".format(self.game_dir),
                                                 noCache=True)
        self.gizmo_mesh.set_scale(0.5)
        self.gizmo_mesh.reparent_to(render)
        self.gizmo_mesh.hide()

        self.traverser = CollisionTraverser('traverser')
        self.col_handler = CollisionHandlerQueue()
        self.picker_node = CollisionNode('mouseRay')
        self.picker_np = self.camera.attachNewNode(self.picker_node)
        self.picker_node.set_from_collide_mask(GeomNode.get_default_collide_mask())
        self.picker_ray = CollisionRay()
        self.picker_node.add_solid(self.picker_ray)
        self.traverser.add_collider(self.picker_np, self.col_handler)

        taskMgr.add(self.update_scene, "update_scene")

        self.set_shader(name="flame")

        # base.messenger.toggleVerbose()

    def set_ui(self):
        if not self.frame:
            self.frame = DirectFrame(frameColor=(0, 0, 0, 0.6), pos=(0, 0, 0),
                                     frameSize=self.frame_size, geom=self.menu_geom)
            self.active_asset_text = OnscreenText(text="",
                                                  scale=0.04,
                                                  fg=(255, 255, 255, 0.9),
                                                  font=self.font.load_font(self.menu_font),
                                                  align=TextNode.ALeft,
                                                  mayChange=True)

            self.mouse_in_asset_text = OnscreenText(text="",
                                                    scale=0.03,
                                                    fg=(255, 255, 255, 0.9),
                                                    font=self.font.load_font(self.menu_font),
                                                    align=TextNode.ALeft,
                                                    mayChange=True)

            self.scrolled_list_lbl = DirectLabel(text="Assets Overview",
                                                 text_fg=(255, 255, 255, 0.9),
                                                 text_font=self.font.load_font(self.menu_font),
                                                 frameColor=(255, 255, 255, 0),
                                                 scale=.05, borderWidth=(self.w, self.h),
                                                 parent=self.frame)

            ui_geoms = self.ui_geom_collector()
            if ui_geoms:
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
                if not self.assets:
                    self.scrolled_list_lbl_na = DirectLabel(text="N/A",
                                                            text_fg=(255, 255, 255, 0.9),
                                                            text_font=self.font.load_font(self.menu_font),
                                                            frameColor=(255, 255, 255, 0),
                                                            scale=.04, borderWidth=(self.w, self.h),
                                                            parent=self.frame)
                if self.assets:
                    for index, asset in enumerate(self.assets, 1):
                        btn = DirectButton(text="{0}".format(asset),
                                           text_fg=(255, 255, 255, 1), relief=2,
                                           text_font=self.font.load_font(self.menu_font),
                                           frameColor=(0, 0, 0, 1),
                                           scale=.03, borderWidth=(self.w, self.h),
                                           geom=geoms_scrolled_dbtn, geom_scale=(15.3, 0, 2),
                                           clickSound="",
                                           command=self.select_asset_from_list,
                                           extraArgs=[asset])
                        btn_list.append(btn)

                    self.scrolled_list = DirectScrolledList(
                        decButton_pos=(0.35, 0, 0.46),
                        decButton_scale=(5, 1, 0.5),
                        decButton_text="",
                        decButton_text_scale=0.04,
                        decButton_borderWidth=(0, 0),
                        decButton_geom=geoms_scrolled_dec,
                        decButton_geom_scale=0.08,

                        incButton_pos=(0.35, 0, -0.65),
                        incButton_scale=(5, 1, 0.5),
                        incButton_text="",
                        incButton_text_scale=0.04,
                        incButton_borderWidth=(0, 0),
                        incButton_geom=geoms_scrolled_inc,
                        incButton_geom_scale=0.08,

                        frameSize=self.frame_scrolled_size,
                        frameColor=(0, 0, 0, 0),
                        numItemsVisible=10,
                        forceHeight=0.11,
                        items=btn_list,
                        itemFrame_frameSize=self.frame_scrolled_inner_size,
                        itemFrame_pos=(0.35, 0, 0.4),
                        parent=self.frame
                    )

                self.scrolled_list_lbl_desc = DirectLabel(text="Select asset \nfor manipulations on the scene",
                                                          text_fg=(255, 255, 255, 0.9),
                                                          text_font=self.font.load_font(self.menu_font),
                                                          frameColor=(255, 255, 255, 0),
                                                          scale=.025, borderWidth=(self.w, self.h),
                                                          parent=self.frame)

                self.asset_management_title = DirectLabel(text="Assets Management",
                                                          text_fg=(255, 255, 255, 0.9),
                                                          text_font=self.font.load_font(self.menu_font),
                                                          frameColor=(255, 255, 255, 0),
                                                          scale=.05, borderWidth=(self.w, self.h),
                                                          parent=self.frame)

                self.asset_management_desc = DirectLabel(text="Use these fields to move or rotate geometry",
                                                         text_fg=(255, 255, 255, 0.9),
                                                         text_font=self.font.load_font(self.menu_font),
                                                         frameColor=(255, 255, 255, 0),
                                                         scale=.025, borderWidth=(self.w, self.h),
                                                         parent=self.frame)

                self.lbl_pos_x = DirectLabel(text="X Axis",
                                             text_fg=(255, 255, 255, 0.9),
                                             text_font=self.font.load_font(self.menu_font),
                                             frameColor=(255, 255, 255, 0),
                                             scale=.03, borderWidth=(self.w, self.h),
                                             parent=self.frame)

                self.lbl_pos_y = DirectLabel(text="Y Axis",
                                             text_fg=(255, 255, 255, 0.9),
                                             text_font=self.font.load_font(self.menu_font),
                                             frameColor=(255, 255, 255, 0),
                                             scale=.03, borderWidth=(self.w, self.h),
                                             parent=self.frame)

                self.lbl_pos_z = DirectLabel(text="Z Axis",
                                             text_fg=(255, 255, 255, 0.9),
                                             text_font=self.font.load_font(self.menu_font),
                                             frameColor=(255, 255, 255, 0),
                                             scale=.03, borderWidth=(self.w, self.h),
                                             parent=self.frame)

                self.lbl_rot_h = DirectLabel(text="Heading",
                                             text_fg=(255, 255, 255, 0.9),
                                             text_font=self.font.load_font(self.menu_font),
                                             frameColor=(255, 255, 255, 0),
                                             scale=.03, borderWidth=(self.w, self.h),
                                             parent=self.frame)

                self.lbl_rot_p = DirectLabel(text="Pitch",
                                             text_fg=(255, 255, 255, 0.9),
                                             text_font=self.font.load_font(self.menu_font),
                                             frameColor=(255, 255, 255, 0),
                                             scale=.03, borderWidth=(self.w, self.h),
                                             parent=self.frame)

                self.lbl_rot_r = DirectLabel(text="Rotation",
                                             text_fg=(255, 255, 255, 0.9),
                                             text_font=self.font.load_font(self.menu_font),
                                             frameColor=(255, 255, 255, 0),
                                             scale=.03, borderWidth=(self.w, self.h),
                                             parent=self.frame)

                self.lbl_scale_x = DirectLabel(text="X Scale",
                                               text_fg=(255, 255, 255, 0.9),
                                               text_font=self.font.load_font(self.menu_font),
                                               frameColor=(255, 255, 255, 0),
                                               scale=.03, borderWidth=(self.w, self.h),
                                               parent=self.frame)

                self.lbl_scale_y = DirectLabel(text="Y Scale",
                                               text_fg=(255, 255, 255, 0.9),
                                               text_font=self.font.load_font(self.menu_font),
                                               frameColor=(255, 255, 255, 0),
                                               scale=.03, borderWidth=(self.w, self.h),
                                               parent=self.frame)

                self.lbl_scale_z = DirectLabel(text="Z Scale",
                                               text_fg=(255, 255, 255, 0.9),
                                               text_font=self.font.load_font(self.menu_font),
                                               frameColor=(255, 255, 255, 0),
                                               scale=.03, borderWidth=(self.w, self.h),
                                               parent=self.frame)

                self.inp_pos_x = DirectEntry(initialText="",
                                             text_bg=(0, 0, 0, 1),
                                             entryFont=self.font.load_font(self.menu_font),
                                             text_align=TextNode.A_center,
                                             scale=.03, width=7, borderWidth=(self.w, self.h),
                                             parent=self.frame, cursorKeys=1,
                                             command=self.set_node_pos_x,
                                             focusInCommand=self.input_clear_pos_x)

                self.inp_pos_y = DirectEntry(initialText="",
                                             text_bg=(0, 0, 0, 1),
                                             entryFont=self.font.load_font(self.menu_font),
                                             text_align=TextNode.A_center,
                                             scale=.03, width=7, borderWidth=(self.w, self.h),
                                             parent=self.frame, cursorKeys=1,
                                             command=self.set_node_pos_y,
                                             focusInCommand=self.input_clear_pos_y)

                self.inp_pos_z = DirectEntry(initialText="",
                                             text_bg=(0, 0, 0, 1),
                                             entryFont=self.font.load_font(self.menu_font),
                                             text_align=TextNode.A_center,
                                             scale=.03, width=7, borderWidth=(self.w, self.h),
                                             parent=self.frame, cursorKeys=1,
                                             command=self.set_node_pos_z,
                                             focusInCommand=self.input_clear_pos_z)

                self.inp_rot_h = DirectEntry(initialText="",
                                             text_bg=(0, 0, 0, 1),
                                             entryFont=self.font.load_font(self.menu_font),
                                             text_align=TextNode.A_center,
                                             scale=.03, width=7, borderWidth=(self.w, self.h),
                                             parent=self.frame, cursorKeys=1,
                                             command=self.set_node_h,
                                             focusInCommand=self.input_clear_rot_h)

                self.inp_rot_p = DirectEntry(initialText="",
                                             text_bg=(0, 0, 0, 1),
                                             entryFont=self.font.load_font(self.menu_font),
                                             text_align=TextNode.A_center,
                                             scale=.03, width=7, borderWidth=(self.w, self.h),
                                             parent=self.frame, cursorKeys=1,
                                             command=self.set_node_p,
                                             focusInCommand=self.input_clear_rot_p)

                self.inp_rot_r = DirectEntry(initialText="",
                                             text_bg=(0, 0, 0, 1),
                                             entryFont=self.font.load_font(self.menu_font),
                                             text_align=TextNode.A_center,
                                             scale=.03, width=7, borderWidth=(self.w, self.h),
                                             parent=self.frame, cursorKeys=1,
                                             command=self.set_node_r,
                                             focusInCommand=self.input_clear_rot_r)

                self.inp_scale_x = DirectEntry(initialText="",
                                               text_bg=(0, 0, 0, 1),
                                               entryFont=self.font.load_font(self.menu_font),
                                               text_align=TextNode.A_center,
                                               scale=.03, width=7, borderWidth=(self.w, self.h),
                                               parent=self.frame, cursorKeys=1,
                                               command=self.set_node_scale_x,
                                               focusInCommand=self.input_clear_scale_x)

                self.inp_scale_y = DirectEntry(initialText="",
                                               text_bg=(0, 0, 0, 1),
                                               entryFont=self.font.load_font(self.menu_font),
                                               text_align=TextNode.A_center,
                                               scale=.03, width=7, borderWidth=(self.w, self.h),
                                               parent=self.frame, cursorKeys=1,
                                               command=self.set_node_scale_y,
                                               focusInCommand=self.input_clear_scale_y)

                self.inp_scale_z = DirectEntry(initialText="",
                                               text_bg=(0, 0, 0, 1),
                                               entryFont=self.font.load_font(self.menu_font),
                                               text_align=TextNode.A_center,
                                               scale=.03, width=7, borderWidth=(self.w, self.h),
                                               parent=self.frame, cursorKeys=1,
                                               command=self.set_node_scale_z,
                                               focusInCommand=self.input_clear_scale_z)

                self.save_asset_pos = DirectButton(text="Save Asset Pos",
                                                   text_fg=(255, 255, 255, 1), relief=2,
                                                   text_font=self.font.load_font(self.menu_font),
                                                   frameColor=(0, 0, 0, 1),
                                                   scale=.03, borderWidth=(self.w, self.h),
                                                   geom=geoms_scrolled_dbtn, geom_scale=(11.3, 0, 2),
                                                   clickSound="",
                                                   command=self.save_asset_orientation)

                self.joint_item_management_title = DirectLabel(text="Joint Child Management",
                                                               text_fg=(255, 255, 255, 0.9),
                                                               text_font=self.font.load_font(self.menu_font),
                                                               frameColor=(255, 255, 255, 0),
                                                               scale=.05, borderWidth=(self.w, self.h),
                                                               parent=self.frame)

                self.joint_item_management_desc = DirectLabel(text="Use these fields to move or rotate child geometry",
                                                              text_fg=(255, 255, 255, 0.9),
                                                              text_font=self.font.load_font(self.menu_font),
                                                              frameColor=(255, 255, 255, 0),
                                                              scale=.025, borderWidth=(self.w, self.h),
                                                              parent=self.frame)

                self.lbl_joint_item_pos_x = DirectLabel(text="X Axis",
                                                        text_fg=(255, 255, 255, 0.9),
                                                        text_font=self.font.load_font(self.menu_font),
                                                        frameColor=(255, 255, 255, 0),
                                                        scale=.03, borderWidth=(self.w, self.h),
                                                        parent=self.frame)

                self.lbl_joint_item_pos_y = DirectLabel(text="Y Axis",
                                                        text_fg=(255, 255, 255, 0.9),
                                                        text_font=self.font.load_font(self.menu_font),
                                                        frameColor=(255, 255, 255, 0),
                                                        scale=.03, borderWidth=(self.w, self.h),
                                                        parent=self.frame)

                self.lbl_joint_item_pos_z = DirectLabel(text="Z Axis",
                                                        text_fg=(255, 255, 255, 0.9),
                                                        text_font=self.font.load_font(self.menu_font),
                                                        frameColor=(255, 255, 255, 0),
                                                        scale=.03, borderWidth=(self.w, self.h),
                                                        parent=self.frame)

                self.lbl_joint_item_rot_h = DirectLabel(text="Heading",
                                                        text_fg=(255, 255, 255, 0.9),
                                                        text_font=self.font.load_font(self.menu_font),
                                                        frameColor=(255, 255, 255, 0),
                                                        scale=.03, borderWidth=(self.w, self.h),
                                                        parent=self.frame)

                self.lbl_joint_item_rot_p = DirectLabel(text="Pitch",
                                                        text_fg=(255, 255, 255, 0.9),
                                                        text_font=self.font.load_font(self.menu_font),
                                                        frameColor=(255, 255, 255, 0),
                                                        scale=.03, borderWidth=(self.w, self.h),
                                                        parent=self.frame)

                self.lbl_joint_item_rot_r = DirectLabel(text="Rotation",
                                                        text_fg=(255, 255, 255, 0.9),
                                                        text_font=self.font.load_font(self.menu_font),
                                                        frameColor=(255, 255, 255, 0),
                                                        scale=.03, borderWidth=(self.w, self.h),
                                                        parent=self.frame)

                self.lbl_joint_item_scale_x = DirectLabel(text="X Scale",
                                                          text_fg=(255, 255, 255, 0.9),
                                                          text_font=self.font.load_font(self.menu_font),
                                                          frameColor=(255, 255, 255, 0),
                                                          scale=.03, borderWidth=(self.w, self.h),
                                                          parent=self.frame)

                self.lbl_joint_item_scale_y = DirectLabel(text="Y Scale",
                                                          text_fg=(255, 255, 255, 0.9),
                                                          text_font=self.font.load_font(self.menu_font),
                                                          frameColor=(255, 255, 255, 0),
                                                          scale=.03, borderWidth=(self.w, self.h),
                                                          parent=self.frame)

                self.lbl_joint_item_scale_z = DirectLabel(text="Z Scale",
                                                          text_fg=(255, 255, 255, 0.9),
                                                          text_font=self.font.load_font(self.menu_font),
                                                          frameColor=(255, 255, 255, 0),
                                                          scale=.03, borderWidth=(self.w, self.h),
                                                          parent=self.frame)

                self.inp_joint_item_pos_x = DirectEntry(initialText="",
                                                        text_bg=(0, 0, 0, 1),
                                                        entryFont=self.font.load_font(self.menu_font),
                                                        text_align=TextNode.A_center,
                                                        scale=.03, width=7, borderWidth=(self.w, self.h),
                                                        parent=self.frame, cursorKeys=1,
                                                        command=self.set_joint_pos_x,
                                                        focusInCommand=self.input_joint_item_clear_pos_x)

                self.inp_joint_item_pos_y = DirectEntry(initialText="",
                                                        text_bg=(0, 0, 0, 1),
                                                        entryFont=self.font.load_font(self.menu_font),
                                                        text_align=TextNode.A_center,
                                                        scale=.03, width=7, borderWidth=(self.w, self.h),
                                                        parent=self.frame, cursorKeys=1,
                                                        command=self.set_joint_pos_y,
                                                        focusInCommand=self.input_joint_item_clear_pos_y)

                self.inp_joint_item_pos_z = DirectEntry(initialText="",
                                                        text_bg=(0, 0, 0, 1),
                                                        entryFont=self.font.load_font(self.menu_font),
                                                        text_align=TextNode.A_center,
                                                        scale=.03, width=7, borderWidth=(self.w, self.h),
                                                        parent=self.frame, cursorKeys=1,
                                                        command=self.set_joint_pos_z,
                                                        focusInCommand=self.input_joint_item_clear_pos_z)

                self.inp_joint_item_rot_h = DirectEntry(initialText="",
                                                        text_bg=(0, 0, 0, 1),
                                                        entryFont=self.font.load_font(self.menu_font),
                                                        text_align=TextNode.A_center,
                                                        scale=.03, width=7, borderWidth=(self.w, self.h),
                                                        parent=self.frame, cursorKeys=1,
                                                        command=self.set_joint_h,
                                                        focusInCommand=self.input_joint_item_clear_rot_h)

                self.inp_joint_item_rot_p = DirectEntry(initialText="",
                                                        text_bg=(0, 0, 0, 1),
                                                        entryFont=self.font.load_font(self.menu_font),
                                                        text_align=TextNode.A_center,
                                                        scale=.03, width=7, borderWidth=(self.w, self.h),
                                                        parent=self.frame, cursorKeys=1,
                                                        command=self.set_joint_p,
                                                        focusInCommand=self.input_joint_item_clear_rot_p)

                self.inp_joint_item_rot_r = DirectEntry(initialText="",
                                                        text_bg=(0, 0, 0, 1),
                                                        entryFont=self.font.load_font(self.menu_font),
                                                        text_align=TextNode.A_center,
                                                        scale=.03, width=7, borderWidth=(self.w, self.h),
                                                        parent=self.frame, cursorKeys=1,
                                                        command=self.set_joint_r,
                                                        focusInCommand=self.input_joint_item_clear_rot_r)

                self.inp_joint_item_scale_x = DirectEntry(initialText="",
                                                          text_bg=(0, 0, 0, 1),
                                                          entryFont=self.font.load_font(self.menu_font),
                                                          text_align=TextNode.A_center,
                                                          scale=.03, width=7, borderWidth=(self.w, self.h),
                                                          parent=self.frame, cursorKeys=1,
                                                          command=self.set_joint_scale_x,
                                                          focusInCommand=self.input_joint_item_clear_scale_x)

                self.inp_joint_item_scale_y = DirectEntry(initialText="",
                                                          text_bg=(0, 0, 0, 1),
                                                          entryFont=self.font.load_font(self.menu_font),
                                                          text_align=TextNode.A_center,
                                                          scale=.03, width=7, borderWidth=(self.w, self.h),
                                                          parent=self.frame, cursorKeys=1,
                                                          command=self.set_joint_scale_y,
                                                          focusInCommand=self.input_joint_item_clear_scale_y)

                self.inp_joint_item_scale_z = DirectEntry(initialText="",
                                                          text_bg=(0, 0, 0, 1),
                                                          entryFont=self.font.load_font(self.menu_font),
                                                          text_align=TextNode.A_center,
                                                          scale=.03, width=7, borderWidth=(self.w, self.h),
                                                          parent=self.frame, cursorKeys=1,
                                                          command=self.set_joint_scale_z,
                                                          focusInCommand=self.input_joint_item_clear_scale_z)

                self.save_joint_item_pos = DirectButton(text="Save Item Pos",
                                                        text_fg=(255, 255, 255, 1), relief=2,
                                                        text_font=self.font.load_font(self.menu_font),
                                                        frameColor=(0, 0, 0, 1),
                                                        scale=.03, borderWidth=(self.w, self.h),
                                                        geom=geoms_scrolled_dbtn, geom_scale=(11.3, 0, 2),
                                                        clickSound="",
                                                        command=self.save_joint_item_orientation)

                self.scrolled_list_actor_joints_lbl = DirectLabel(text="Actor Joints",
                                                                  text_fg=(255, 255, 255, 0.9),
                                                                  text_font=self.font.load_font(self.menu_font),
                                                                  frameColor=(255, 255, 255, 0),
                                                                  scale=.05, borderWidth=(self.w, self.h),
                                                                  parent=self.frame)

                btn2_list = []
                joints = self.get_actor_joints()
                if not joints:
                    btn = DirectButton(text="Where joints, Johnny?",
                                       text_fg=(255, 255, 255, 1), relief=2,
                                       text_font=self.font.load_font(self.menu_font),
                                       frameColor=(0, 0, 0, 1),
                                       scale=.03, borderWidth=(self.w, self.h),
                                       geom=geoms_scrolled_dbtn, geom_scale=(15.3, 0, 2),
                                       clickSound="",
                                       command="")

                    btn2_list.append(btn)
                    self.scrolled_list_actor_joints_empty = DirectScrolledList(
                        decButton_pos=(0.35, 0, 0.46),
                        decButton_scale=(5, 1, 0.5),
                        decButton_text="",
                        decButton_text_scale=0.04,
                        decButton_borderWidth=(0, 0),
                        decButton_geom=geoms_scrolled_dec,
                        decButton_geom_scale=0.08,

                        incButton_pos=(0.35, 0, 0.34),
                        incButton_scale=(5, 1, 0.5),
                        incButton_text="",
                        incButton_text_scale=0.04,
                        incButton_borderWidth=(0, 0),
                        incButton_geom=geoms_scrolled_inc,
                        incButton_geom_scale=0.08,

                        frameSize=self.frame_scrolled_size,
                        frameColor=(0, 0, 0, 0),
                        numItemsVisible=1,
                        forceHeight=0.11,
                        items=btn2_list,
                        itemFrame_frameSize=self.frame_scrolled_inner_size,
                        itemFrame_pos=(0.35, 0, 0.4),
                        parent=self.frame,
                    )

                    self.scrolled_list_actor_joints_lbl_desc_empty = DirectLabel(
                        text="No actor is selected",
                        text_fg=(255, 255, 255, 0.9),
                        text_font=self.font.load_font(self.menu_font),
                        frameColor=(255, 255, 255, 0),
                        scale=.025, borderWidth=(self.w, self.h),
                        parent=self.frame)

        if self.scrolled_list_lbl:
            self.scrolled_list_lbl.set_pos(-1.65, 0, 0.85)
        if self.scrolled_list_lbl_na:
            self.scrolled_list_lbl_na.set_pos(-1.65, 0, 0.32)
        if self.scrolled_list:
            self.scrolled_list.set_pos(-2.0, 0, 0.32)
        if self.scrolled_list_lbl_desc:
            self.scrolled_list_lbl_desc.set_pos(-1.65, 0, -0.40)

        self.active_asset_text.set_pos(1.3, 0, 0.85)
        self.mouse_in_asset_text.set_pos(-1.2, 0, -0.3)

        self.asset_management_title.set_pos(-1.0, 0, -0.59)
        self.asset_management_desc.set_pos(-0.92, 0, -0.63)

        self.lbl_pos_x.set_pos(-1.2, 0, -0.7)
        self.lbl_pos_y.set_pos(-1.2, 0, -0.8)
        self.lbl_pos_z.set_pos(-1.2, 0, -0.9)

        self.inp_pos_x.set_pos(-1.0, 0, -0.7)
        self.inp_pos_y.set_pos(-1.0, 0, -0.8)
        self.inp_pos_z.set_pos(-1.0, 0, -0.9)

        self.lbl_rot_h.set_pos(-0.75, 0, -0.7)
        self.lbl_rot_p.set_pos(-0.75, 0, -0.8)
        self.lbl_rot_r.set_pos(-0.75, 0, -0.9)

        self.inp_rot_h.set_pos(-0.51, 0, -0.7)
        self.inp_rot_p.set_pos(-0.51, 0, -0.8)
        self.inp_rot_r.set_pos(-0.51, 0, -0.9)

        self.lbl_scale_x.set_pos(-0.25, 0, -0.7)
        self.lbl_scale_y.set_pos(-0.25, 0, -0.8)
        self.lbl_scale_z.set_pos(-0.25, 0, -0.9)

        self.inp_scale_x.set_pos(-0.01, 0, -0.7)
        self.inp_scale_y.set_pos(-0.01, 0, -0.8)
        self.inp_scale_z.set_pos(-0.01, 0, -0.9)

        if self.scrolled_list_actor_joints_lbl:
            self.scrolled_list_actor_joints_lbl.set_pos(-1.65, 0, -0.60)
        if self.scrolled_list_actor_joints_empty:
            self.scrolled_list_actor_joints_empty.set_pos(-2.0, 0, -1.12)
        if self.scrolled_list_actor_joints_lbl_desc_empty:
            self.scrolled_list_actor_joints_lbl_desc_empty.set_pos(-1.65, 0, -0.87)

        self.joint_item_management_title.set_pos(0.6, 0, -0.59)
        self.joint_item_management_desc.set_pos(0.65, 0, -0.63)

        self.lbl_joint_item_pos_x.set_pos(0.35, 0, -0.7)
        self.lbl_joint_item_pos_y.set_pos(0.35, 0, -0.8)
        self.lbl_joint_item_pos_z.set_pos(0.35, 0, -0.9)

        self.inp_joint_item_pos_x.set_pos(0.55, 0, -0.7)
        self.inp_joint_item_pos_y.set_pos(0.55, 0, -0.8)
        self.inp_joint_item_pos_z.set_pos(0.55, 0, -0.9)

        self.lbl_joint_item_rot_h.set_pos(0.75, 0, -0.7)
        self.lbl_joint_item_rot_p.set_pos(0.75, 0, -0.8)
        self.lbl_joint_item_rot_r.set_pos(0.75, 0, -0.9)

        self.inp_joint_item_rot_h.set_pos(0.95, 0, -0.7)
        self.inp_joint_item_rot_p.set_pos(0.95, 0, -0.8)
        self.inp_joint_item_rot_r.set_pos(0.95, 0, -0.9)

        self.lbl_joint_item_scale_x.set_pos(1.15, 0, -0.7)
        self.lbl_joint_item_scale_y.set_pos(1.15, 0, -0.8)
        self.lbl_joint_item_scale_z.set_pos(1.15, 0, -0.9)

        self.inp_joint_item_scale_x.set_pos(1.35, 0, -0.7)
        self.inp_joint_item_scale_y.set_pos(1.35, 0, -0.8)
        self.inp_joint_item_scale_z.set_pos(1.35, 0, -0.9)

        self.save_asset_pos.set_pos(1.7, 0, -0.8)
        self.save_joint_item_pos.set_pos(1.7, 0, -0.9)

        self.inp_pos_x.setText("Axis X")
        self.inp_pos_y.setText("Axis Y")
        self.inp_pos_z.setText("Axis Z")

        self.inp_rot_h.setText("Heading")
        self.inp_rot_p.setText("Pitch")
        self.inp_rot_r.setText("Rotation")

        self.inp_scale_x.setText("Scale X")
        self.inp_scale_y.setText("Scale Y")
        self.inp_scale_z.setText("Scale Z")

        self.inp_joint_item_pos_x.setText("Axis X")
        self.inp_joint_item_pos_y.setText("Axis Y")
        self.inp_joint_item_pos_z.setText("Axis Z")

        self.inp_joint_item_rot_h.setText("Heading")
        self.inp_joint_item_rot_p.setText("Pitch")
        self.inp_joint_item_rot_r.setText("Rotation")

        self.inp_joint_item_scale_x.setText("Scale X")
        self.inp_joint_item_scale_y.setText("Scale Y")
        self.inp_joint_item_scale_z.setText("Scale Z")

    def set_ui_rotation(self):
        ui_geoms = self.ui_geom_collector()
        axis_h_maps = self.loader.loadModel(ui_geoms['axis_h_icon'])
        axis_h_geoms = (axis_h_maps.find('**/axis_h_any'), axis_h_maps.find('**/axis_h_pressed'))

        axis_p_maps = self.loader.loadModel(ui_geoms['axis_p_icon'])
        axis_p_geoms = (axis_p_maps.find('**/axis_p_any'), axis_p_maps.find('**/axis_p_pressed'))

        axis_r_maps = self.loader.loadModel(ui_geoms['axis_r_icon'])
        axis_r_geoms = (axis_r_maps.find('**/axis_r_any'), axis_r_maps.find('**/axis_r_pressed'))

        radbuttons = [

            DirectRadioButton(text='', variable=[0], value=[1], pos=(-1.2, 0, 0.85),
                              parent=self.frame, scale=self.rad_scale,
                              clickSound='',
                              command=self.set_rotation_mode, extraArgs=[1],
                              boxGeom=axis_h_geoms, boxPlacement='Center', frameColor=(255, 255, 255, 0)),

            DirectRadioButton(text='', variable=[0], value=[2], pos=(-1.1, 0, 0.85),
                              parent=self.frame, scale=self.rad_scale,
                              clickSound='',
                              command=self.set_rotation_mode, extraArgs=[2],
                              boxGeom=axis_p_geoms, boxPlacement='Center', frameColor=(255, 255, 255, 0)),

            DirectRadioButton(text='', variable=[0], value=[3], pos=(-1.0, 0, 0.85),
                              parent=self.frame, scale=self.rad_scale,
                              clickSound='',
                              command=self.set_rotation_mode, extraArgs=[3],
                              boxGeom=axis_r_geoms, boxPlacement='Center', frameColor=(255, 255, 255, 0))

        ]

        for radbutton in radbuttons:
            radbutton.setOthers(radbuttons)

    def set_ui_manipulation_modes(self):
        ui_geoms = self.ui_geom_collector()
        pos_mode_maps = self.loader.loadModel(ui_geoms['pos_mode_icon'])
        pos_mode_geoms = (pos_mode_maps.find('**/pos_mode_any'), pos_mode_maps.find('**/pos_mode_pressed'))

        rot_mode_maps = self.loader.loadModel(ui_geoms['rot_mode_icon'])
        rot_mode_geoms = (rot_mode_maps.find('**/rot_mode_any'), rot_mode_maps.find('**/rot_mode_pressed'))

        radbuttons = [

            DirectRadioButton(text='', variable=[0], value=[1], pos=(-0.8, 0, 0.85),
                              parent=self.frame, scale=self.rad_scale,
                              clickSound='',
                              command=self.set_manipulation_mode, extraArgs=[1],
                              boxGeom=pos_mode_geoms, boxPlacement='Center', frameColor=(255, 255, 255, 0)),

            DirectRadioButton(text='', variable=[0], value=[2], pos=(-0.7, 0, 0.85),
                              parent=self.frame, scale=self.rad_scale,
                              clickSound='',
                              command=self.set_manipulation_mode, extraArgs=[2],
                              boxGeom=rot_mode_geoms, boxPlacement='Center', frameColor=(255, 255, 255, 0)),

        ]

        for radbutton in radbuttons:
            radbutton.setOthers(radbuttons)

    def get_assets(self, path):
        if path:
            newpath = self.transform_path(path="{0}/{1}".format(self.game_dir, path),
                                          style='compat')
            assets = {}
            if exists(newpath):
                for root, dirs, files in walk(newpath, topdown=True):
                    for file in files:
                        if file.endswith(".egg"):
                            key = re.sub('.egg$', '', file)
                            newpath = str(PurePath("{0}/".format(root), file))
                            assets[key] = Filename.from_os_specific(newpath).getFullpath()
                        elif file.endswith(".egg.bam"):
                            key = re.sub('.egg.bam$', '', file)
                            newpath = str(PurePath("{0}/".format(root), file))
                            assets[key] = Filename.from_os_specific(newpath).getFullpath()

                if assets:
                    return assets

    def get_actor_joints(self):
        if self.active_asset:
            if self.is_asset_actor(asset=self.active_asset):
                name = self.active_asset.get_name()
                if name in self.actor_refs:
                    joints = self.actor_refs[name].get_joints()
                    if joints:
                        return joints

        if self.active_asset_from_list:
            if self.is_asset_actor(asset=self.active_asset_from_list):
                name = self.active_asset_from_list.get_name()
                if name in self.actor_refs:
                    joints = self.actor_refs[name].get_joints()
                    if joints:
                        return joints

    def set_joints_list_ui(self):
        if not self.scrolled_list_actor_joints_lbl_desc:
            ui_geoms = self.ui_geom_collector()
            if ui_geoms:
                maps_scrolled_dbtn = self.loader.loadModel(ui_geoms['btn_t_icon'])
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

                btn2_list = []
                for index, joint in enumerate(self.get_actor_joints(), 1):
                    btn = DirectButton(text="{0}".format(joint.get_name()),
                                       text_fg=(255, 255, 255, 1), relief=2,
                                       text_font=self.font.load_font(self.menu_font),
                                       frameColor=(0, 0, 0, 1),
                                       scale=.03, borderWidth=(self.w, self.h),
                                       geom=geoms_scrolled_dbtn, geom_scale=(15.3, 0, 2),
                                       clickSound="",
                                       command=self.select_joint_from_list,
                                       extraArgs=[joint.get_name()])
                    btn2_list.append(btn)

                if not self.scrolled_list_actor_joints_lbl_desc:
                    self.scrolled_list_actor_joints = DirectScrolledList(
                        decButton_pos=(0.35, 0, 0.46),
                        decButton_scale=(5, 1, 0.5),
                        decButton_text="<",
                        decButton_text_scale=0.04,
                        decButton_borderWidth=(0, 0),
                        decButton_geom=geoms_scrolled_dec,
                        decButton_geom_scale=0.08,

                        incButton_pos=(0.35, 0, 0.34),
                        incButton_scale=(5, 1, 0.5),
                        incButton_text=">",
                        incButton_text_scale=0.04,
                        incButton_borderWidth=(0, 0),
                        incButton_geom=geoms_scrolled_inc,
                        incButton_geom_scale=0.08,

                        frameSize=self.frame_scrolled_size,
                        frameColor=(0, 0, 0, 0),
                        numItemsVisible=1,
                        forceHeight=0.11,
                        items=btn2_list,
                        itemFrame_frameSize=self.frame_scrolled_inner_size,
                        itemFrame_pos=(0.35, 0, 0.4),
                        parent=self.frame,
                    )

                if not self.scrolled_list_actor_joints_lbl_desc:
                    self.scrolled_list_actor_joints_lbl_desc = DirectLabel(
                        text="Select joint \nfor manipulations on the scene",
                        text_fg=(255, 255, 255, 0.9),
                        text_font=self.font.load_font(self.menu_font),
                        frameColor=(255, 255, 255, 0),
                        scale=.025, borderWidth=(self.w, self.h),
                        parent=self.frame)

                if self.scrolled_list_actor_joints_lbl:
                    self.scrolled_list_actor_joints_lbl.set_pos(-1.65, 0, -0.60)
                if self.scrolled_list_actor_joints:
                    self.scrolled_list_actor_joints.set_pos(-2.0, 0, -1.12)
                if self.scrolled_list_actor_joints_lbl_desc:
                    self.scrolled_list_actor_joints_lbl_desc.set_pos(-1.65, 0, -0.87)

    def is_asset_actor(self, asset):
        if asset:
            for node in render.findAllMatches("**/+Character"):
                if not node.is_empty():
                    if asset.get_name() in node.get_parent().get_name():
                        return True
                    else:
                        self.active_item = asset
                        return False

    def is_actor_joint_busy(self, joint):
        if joint:
            if joint.find("**/*").is_empty():
                return False
            else:
                return True

    def asset_load(self, assets):
        if assets:
            for index, asset in enumerate(assets, 1):
                if "flame" in asset:
                    # exclude it
                    continue

                if "-" in asset or "Action" in asset:
                    self.anims[asset] = assets[asset]
                    continue

                if "flame" not in asset \
                        or "fire" not in asset \
                        or "water" not in asset:
                    model = self.loader.load_model(assets[asset],
                                                   noCache=True)
                    if not model.find("**/+Character").is_empty():
                        model = Actor(model)
                        model.set_two_sided(True)
                        model.set_name(asset)
                        self.actor_refs[asset] = model

                    model.set_name(asset)

                    # automatic positioning
                    model.set_pos(model.get_pos() + (index * 2, index * 2, 0))
                    model.reparent_to(render)
                    model.setPythonTag(model.get_name(), '1')

                    self.render_pipeline.prepare_scene(model)

            for tex in self.render.findAllTextures():
                if tex.getNumComponents() == 4:
                    tex.setFormat(Texture.F_srgb_alpha)
                elif tex.getNumComponents() == 3:
                    tex.setFormat(Texture.F_srgb)

            self.set_ui()
            self.set_ui_rotation()
            self.set_ui_manipulation_modes()

    def attach_to_joint(self, actor, item, joint, wrt):
        if actor and item and joint:
            if self.is_asset_actor(asset=actor) and not self.is_actor_joint_busy(joint=joint):
                if wrt:
                    item.wrt_reparent_to(joint)
                else:
                    item.reparent_to(joint)
                item.set_pos(joint.get_pos())
                item.set_scale(10)
            elif self.is_asset_actor(asset=actor) and self.is_actor_joint_busy(joint=joint):
                joint.get_child(0).reparent_to(render)
                if wrt:
                    item.wrt_reparent_to(joint)
                else:
                    item.reparent_to(joint)
                item.set_pos(joint.get_pos())
                item.set_scale(10)

    def pick_up(self):
        if not self.is_asset_picked_up:
            self.is_asset_picked_up = True
        elif not self.is_asset_selected_from_list:
            self.is_asset_picked_up = True

    def drop_down(self):
        if self.is_asset_picked_up:
            self.is_asset_picked_up = False
            if self.active_asset:
                if (len(self.history_names) < 200
                        and len(self.history_pos_steps) < 11
                        and len(self.history_hpr_steps) < 11
                        and len(self.history_scale_steps) < 11):
                    self.history_pos_steps = []
                    self.history_hpr_steps = []
                    self.history_scale_steps = []
                    name = "{0}".format(self.active_asset.get_name())
                    if not self.history_names or not self.history_names.get(name):
                        self.history_pos_steps.append(self.active_asset.get_pos())
                        self.history_hpr_steps.append(self.active_asset.get_hpr())
                        self.history_scale_steps.append(self.active_asset.get_scale())
                        self.history_names[name] = self.history_steps
                        self.history_names[name].append([])
                        self.history_names[name].append([])
                        self.history_names[name].append([])
                        self.history_names[name][0].append(self.history_pos_steps)
                        self.history_names[name][1].append(self.history_hpr_steps)
                        self.history_names[name][2].append(self.history_scale_steps)

                    elif self.history_names.get(name) and len(self.history_names[name]) == 3:
                        self.history_names[name][0][0].append(self.active_asset.get_pos())
                        self.history_names[name][1][0].append(self.active_asset.get_hpr())
                        self.history_names[name][2][0].append(self.active_asset.get_scale())

                    elif (self.history_names.get(name)
                          and not self.history_names[name][0][0]
                          and not self.history_names[name][1][0]
                          and not self.history_names[name][2][0]):
                        self.history_names[name][0][0].append(self.active_asset.get_pos())
                        self.history_names[name][1][0].append(self.active_asset.get_hpr())
                        self.history_names[name][2][0].append(self.active_asset.get_scale())

                    elif (self.history_names.get(name)
                          and len(self.history_names[name][0][0]) == 1
                          and len(self.history_names[name][1][0]) == 1
                          and len(self.history_names[name][2][0]) == 1):
                        self.history_names[name][0][0].append(self.active_asset.get_pos())
                        self.history_names[name][1][0].append(self.active_asset.get_hpr())
                        self.history_names[name][2][0].append(self.active_asset.get_scale())

                    else:
                        self.history_names[name][0][0].append(self.active_asset.get_pos())
                        self.history_names[name][1][0].append(self.active_asset.get_hpr())
                        self.history_names[name][2][0].append(self.active_asset.get_scale())

            if self.active_asset_from_list:
                if (len(self.history_names) < 200
                        and len(self.history_pos_steps) < 11
                        and len(self.history_hpr_steps) < 11
                        and len(self.history_scale_steps) < 11):
                    self.history_pos_steps = []
                    self.history_hpr_steps = []
                    self.history_scale_steps = []
                    name = "{0}".format(self.active_asset_from_list.get_name())
                    if not self.history_names or not self.history_names.get(name):
                        self.history_pos_steps.append(self.active_asset_from_list.get_pos())
                        self.history_hpr_steps.append(self.active_asset_from_list.get_hpr())
                        self.history_scale_steps.append(self.active_asset_from_list.get_scale())
                        self.history_names[name] = self.history_steps
                        self.history_names[name].append([])
                        self.history_names[name].append([])
                        self.history_names[name].append([])
                        self.history_names[name][0].append(self.history_pos_steps)
                        self.history_names[name][1].append(self.history_hpr_steps)
                        self.history_names[name][2].append(self.history_scale_steps)

                    elif self.history_names.get(name) and len(self.history_names[name]) == 3:
                        self.history_names[name][0][0].append(self.active_asset_from_list.get_pos())
                        self.history_names[name][1][0].append(self.active_asset_from_list.get_hpr())
                        self.history_names[name][2][0].append(self.active_asset_from_list.get_scale())

                    elif (self.history_names.get(name)
                          and not self.history_names[name][0][0]
                          and not self.history_names[name][1][0]
                          and not self.history_names[name][2][0]):
                        self.history_names[name][0][0].append(self.active_asset_from_list.get_pos())
                        self.history_names[name][1][0].append(self.active_asset_from_list.get_hpr())
                        self.history_names[name][2][0].append(self.active_asset_from_list.get_scale())

                    elif (self.history_names.get(name)
                          and len(self.history_names[name][0][0]) == 1
                          and len(self.history_names[name][1][0]) == 1
                          and len(self.history_names[name][2][0]) == 1):
                        self.history_names[name][0][0].append(self.active_asset_from_list.get_pos())
                        self.history_names[name][1][0].append(self.active_asset_from_list.get_hpr())
                        self.history_names[name][2][0].append(self.active_asset_from_list.get_scale())

                    else:
                        self.history_names[name][0][0].append(self.active_asset_from_list.get_pos())
                        self.history_names[name][1][0].append(self.active_asset_from_list.get_hpr())
                        self.history_names[name][2][0].append(self.active_asset_from_list.get_scale())

    def undo_positioning(self):
        if self.active_asset:
            name = self.active_asset.get_name()
            if self.history_names.get(name) and self.history_names[name][0][0]:

                if len(self.history_names[name][0][0]) > 1:
                    pos = self.history_names[name][0][0][-2]
                    self.active_asset.set_pos(pos)
                    self.history_names[name][0][0].pop()

    def undo_rotation(self):
        if self.active_asset:
            name = self.active_asset.get_name()
            if self.history_names.get(name) and self.history_names[name][1][0]:

                if len(self.history_names[name][1][0]) > 1:
                    rot = self.history_names[name][1][0][-2]
                    self.active_asset.set_hpr(rot)
                    self.history_names[name][1][0].pop()

    def undo_scaling(self):
        if self.active_asset:
            name = self.active_asset.get_name()
            if self.history_names.get(name) and self.history_names[name][2][0]:

                if len(self.history_names[name][2][0]) > 2:
                    scale = self.history_names[name][2][0][-2]
                    self.active_asset.set_scale(scale)
                    self.history_names[name][2][0].pop()

    def select(self):
        if not self.is_asset_picked_up:
            self.is_asset_selected = True
            self.pick_up()

    def unselect(self):
        if not self.is_asset_picked_up:
            self.is_asset_selected = False
            if self.active_asset_text:
                self.active_asset_text.setText("")
                self.active_asset = None
                self.active_asset_from_list = None

        if self.is_asset_selected_from_list:
            self.is_asset_selected_from_list = False
            if self.active_asset_text:
                self.active_asset_text.setText("")
                self.active_asset = None
                self.active_asset_from_list = None

    def mouse_click_handler(self):
        if base.mouseWatcherNode.hasMouse():
            self.mpos = base.mouseWatcherNode.getMouse()
            self.picker_ray.setFromLens(base.camNode, self.mpos.get_x(), self.mpos.get_y())
            self.traverser.traverse(render)
            # Assume for simplicity's sake that col_handler is a CollisionHandlerQueue.
            if self.col_handler.getNumEntries() > 0:
                # This is so we get the closest object.
                self.col_handler.sortEntries()
                # Get new asset only when previous is unselected

                if not self.col_handler.get_entry(0).get_into_node_path().is_empty():
                    if self.is_asset_actor(asset=self.col_handler.get_entry(0).get_into_node_path()):
                        name = self.col_handler.get_entry(0).get_into_node_path().get_parent().get_parent().get_name()
                    else:
                        name = self.col_handler.get_entry(0).get_into_node_path().get_name()
                    name = "Mouse-in asset: {0}".format(name)
                    self.mouse_in_asset_text.setText(name)

                if (not self.col_handler.get_entry(0).get_into_node_path().is_empty()
                        and not self.is_asset_picked_up
                        and not self.active_asset
                        and not self.active_asset_from_list):
                    if self.is_asset_actor(asset=self.col_handler.get_entry(0).get_into_node_path()):
                        self.active_asset = self.col_handler.get_entry(0).get_into_node_path().get_parent().get_parent()
                    else:
                        self.active_asset = self.col_handler.get_entry(0).get_into_node_path()

        if self.active_asset and self.is_asset_selected:
            if self.axis_arrows:
                self.axis_arrows.set_pos(self.active_asset.get_pos())
                self.axis_arrows.set_hpr(self.active_asset.get_hpr())
                self.axis_arrows.show()
            if self.gizmo_mesh:
                self.gizmo_mesh.set_pos(self.active_asset.get_pos())
                self.gizmo_mesh.set_hpr(self.active_asset.get_hpr())
                self.gizmo_mesh.hide()
        else:
            if self.axis_arrows:
                self.axis_arrows.hide()
            if self.gizmo_mesh:
                self.gizmo_mesh.hide()

        if (self.active_asset_from_list
                and self.is_asset_selected_from_list):
            if self.axis_arrows:
                self.axis_arrows.set_pos(self.active_asset_from_list.get_pos())
                self.axis_arrows.set_hpr(self.active_asset_from_list.get_hpr())
                self.axis_arrows.show()
            if self.gizmo_mesh:
                self.gizmo_mesh.set_pos(self.active_asset_from_list.get_pos())
                self.gizmo_mesh.set_hpr(self.active_asset_from_list.get_hpr())
                self.gizmo_mesh.hide()
        else:
            if self.axis_arrows:
                self.axis_arrows.hide()
            if self.gizmo_mesh:
                self.gizmo_mesh.hide()

    def move_with_cursor(self):
        if base.mouseWatcherNode.hasMouse():
            mpos = base.mouseWatcherNode.getMouse()
            pos3d = Point3()
            near_point = Point3()
            far_point = Point3()
            base.camLens.extrude(mpos, near_point, far_point)
            if (self.active_asset
                    and not self.active_asset_from_list
                    and self.is_asset_picked_up
                    and self.collider_plane.intersects_line(pos3d,
                                                            render.getRelativePoint(base.camera, near_point),
                                                            render.getRelativePoint(base.camera, far_point))):
                self.active_asset.set_x(render, pos3d[0])
                self.active_asset.set_y(render, pos3d[1])

            elif (self.active_asset
                  and self.active_asset_from_list
                  and self.is_asset_picked_up
                  and self.collider_plane.intersects_line(pos3d,
                                                          render.getRelativePoint(base.camera, near_point),
                                                          render.getRelativePoint(base.camera, far_point))):
                self.active_asset_from_list.set_x(render, pos3d[0])
                self.active_asset_from_list.set_y(render, pos3d[1])

    def input_wheel_up(self):
        if self.asset_manipulation_modes["Positioning"]:
            if self.active_asset and self.is_asset_selected:
                pos_z = self.active_asset.get_z()
                self.active_asset.set_z(pos_z + 0.5)
        elif self.asset_manipulation_modes["Rotation"]:
            if self.active_asset and self.is_asset_selected:
                if self.rotation_modes["H"]:
                    pos_h = self.active_asset.get_h()
                    self.active_asset.set_h(pos_h + 1.5)
                elif self.rotation_modes["P"]:
                    pos_p = self.active_asset.get_p()
                    self.active_asset.set_p(pos_p + 1.5)
                elif self.rotation_modes["R"]:
                    pos_r = self.active_asset.get_r()
                    self.active_asset.set_r(pos_r + 1.5)

    def input_wheel_down(self):
        if self.asset_manipulation_modes["Positioning"]:
            if self.active_asset and self.is_asset_selected:
                pos_z = self.active_asset.get_z()
                self.active_asset.set_z(pos_z - 0.5)
        elif self.asset_manipulation_modes["Rotation"]:
            if self.active_asset and self.is_asset_selected:
                if self.rotation_modes["H"]:
                    pos_h = self.active_asset.get_h()
                    self.active_asset.set_h(pos_h - 1.5)
                elif self.rotation_modes["P"]:
                    pos_p = self.active_asset.get_p()
                    self.active_asset.set_p(pos_p - 1.5)
                elif self.rotation_modes["R"]:
                    pos_r = self.active_asset.get_r()
                    self.active_asset.set_r(pos_r - 1.5)

    def update_fields(self):
        if (self.active_asset
                and self.is_asset_picked_up
                and not self.is_item_attached_to_joint
                and self.is_asset_selected):
            pos_x = self.get_node_pos_x(asset=self.active_asset)
            pos_y = self.get_node_pos_y(asset=self.active_asset)
            pos_z = self.get_node_pos_z(asset=self.active_asset)
            rot_h = self.get_node_h(asset=self.active_asset)
            rot_p = self.get_node_p(asset=self.active_asset)
            rot_r = self.get_node_r(asset=self.active_asset)
            scale_x = self.get_node_scale_x(asset=self.active_asset)
            scale_y = self.get_node_scale_y(asset=self.active_asset)
            scale_z = self.get_node_scale_z(asset=self.active_asset)

            self.inp_pos_x.setText(pos_x)
            self.inp_pos_y.setText(pos_y)
            self.inp_pos_z.setText(pos_z)

            self.inp_rot_h.setText(rot_h)
            self.inp_rot_p.setText(rot_p)
            self.inp_rot_r.setText(rot_r)

            self.inp_scale_x.setText(scale_x)
            self.inp_scale_y.setText(scale_y)
            self.inp_scale_z.setText(scale_z)

        elif (self.active_asset
                and self.is_asset_picked_up
                and self.is_item_attached_to_joint
                and self.is_asset_selected):
            pos_x = self.get_node_pos_x(asset=self.active_asset)
            pos_y = self.get_node_pos_y(asset=self.active_asset)
            pos_z = self.get_node_pos_z(asset=self.active_asset)
            rot_h = self.get_node_h(asset=self.active_asset)
            rot_p = self.get_node_p(asset=self.active_asset)
            rot_r = self.get_node_r(asset=self.active_asset)
            scale_x = self.get_node_scale_x(asset=self.active_asset)
            scale_y = self.get_node_scale_y(asset=self.active_asset)
            scale_z = self.get_node_scale_z(asset=self.active_asset)

            self.inp_joint_item_pos_x.setText(pos_x)
            self.inp_joint_item_pos_y.setText(pos_y)
            self.inp_joint_item_pos_z.setText(pos_z)

            self.inp_joint_item_rot_h.setText(rot_h)
            self.inp_joint_item_rot_p.setText(rot_p)
            self.inp_joint_item_rot_r.setText(rot_r)

            self.inp_joint_item_scale_x.setText(scale_x)
            self.inp_joint_item_scale_y.setText(scale_y)
            self.inp_joint_item_scale_z.setText(scale_z)

    def get_node_pos_x(self, asset):
        if asset:
            if hasattr(asset, "pos"):
                return "{0}".format(asset.pos[0])
            else:
                x = round(asset.get_x(), 1)
                return "{0}".format(x)

    def get_node_pos_y(self, asset):
        if asset:
            if hasattr(asset, "pos"):
                return "{0}".format(asset.pos[1])
            else:
                y = round(asset.get_y(), 1)
                return "{0}".format(y)

    def get_node_pos_z(self, asset):
        if asset:
            if hasattr(asset, "pos"):
                return "{0}".format(asset.pos[2])
            else:
                z = round(asset.get_z(), 1)
                return "{0}".format(z)

    def get_node_h(self, asset):
        if asset:
            if hasattr(asset, "direction"):
                return "{0}".format(asset.direction[0])
            else:
                return "{0}".format(asset.get_h())

    def get_node_p(self, asset):
        if asset:
            if hasattr(asset, "direction"):
                return "{0}".format(asset.direction[1])
            else:
                return "{0}".format(asset.get_p())

    def get_node_r(self, asset):
        if asset:
            if hasattr(asset, "direction"):
                return "{0}".format(asset.direction[2])
            else:
                return "{0}".format(asset.get_r())

    def get_node_scale_x(self, asset):
        if asset:
            scale = asset.get_scale()
            return "{0}".format(round(scale[0], 1))

    def get_node_scale_y(self, asset):
        if asset:
            scale = asset.get_scale()
            return "{0}".format(round(scale[1], 1))

    def get_node_scale_z(self, asset):
        if asset:
            scale = asset.get_scale()
            return "{0}".format(round(scale[2], 1))

    def input_clear_pos_x(self):
        self.inp_pos_x.clearText()

    def input_clear_pos_y(self):
        self.inp_pos_y.clearText()

    def input_clear_pos_z(self):
        self.inp_pos_z.clearText()

    def input_clear_rot_h(self):
        self.inp_rot_h.clearText()

    def input_clear_rot_p(self):
        self.inp_rot_p.clearText()

    def input_clear_rot_r(self):
        self.inp_rot_r.clearText()

    def input_clear_scale_x(self):
        self.inp_scale_x.clearText()

    def input_clear_scale_y(self):
        self.inp_scale_y.clearText()

    def input_clear_scale_z(self):
        self.inp_scale_z.clearText()

    def input_joint_item_clear_pos_x(self):
        self.inp_joint_item_pos_x.clearText()

    def input_joint_item_clear_pos_y(self):
        self.inp_joint_item_pos_y.clearText()

    def input_joint_item_clear_pos_z(self):
        self.inp_joint_item_pos_z.clearText()

    def input_joint_item_clear_rot_h(self):
        self.inp_joint_item_rot_h.clearText()

    def input_joint_item_clear_rot_p(self):
        self.inp_joint_item_rot_p.clearText()

    def input_joint_item_clear_rot_r(self):
        self.inp_joint_item_rot_r.clearText()

    def input_joint_item_clear_scale_x(self):
        self.inp_joint_item_scale_x.clearText()

    def input_joint_item_clear_scale_y(self):
        self.inp_joint_item_scale_y.clearText()

    def input_joint_item_clear_scale_z(self):
        self.inp_joint_item_scale_z.clearText()

    def set_node_pos_x(self, pos):
        if pos and isinstance(pos, str):
            if self.active_asset:
                self.inp_pos_x.clearText()
                int_x = float(pos)
                if hasattr(self.active_asset, "pos") and self.active_asset:
                    self.active_asset.pos[0] = int_x
                else:
                    if self.active_asset:
                        self.active_asset.set_x(int_x)

    def set_node_pos_y(self, pos):
        if pos and isinstance(pos, str):
            if self.active_asset:
                self.inp_pos_y.clearText()
                int_y = float(pos)
                if hasattr(self.active_asset, "pos") and self.active_asset:
                    self.active_asset.pos[1] = int_y
                else:
                    if self.active_asset:
                        self.active_asset.set_y(int_y)

    def set_node_pos_z(self, pos):
        if pos and isinstance(pos, str):
            if self.active_asset:
                self.inp_pos_z.clearText()
                int_z = float(pos)
                if hasattr(self.active_asset, "pos") and self.active_asset:
                    self.active_asset.pos[2] = int_z
                else:
                    if self.active_asset:
                        self.active_asset.set_z(int_z)

    def set_node_h(self, h):
        if h and isinstance(h, str):
            if self.active_asset:
                self.inp_rot_h.clearText()
                int_x = float(h)
                if hasattr(self.active_asset, "direction") and self.active_asset:
                    self.active_asset.direction[0] = int_x
                else:
                    if self.active_asset:
                        self.active_asset.set_h(int_x)

    def set_node_p(self, p):
        if p and isinstance(p, str):
            if self.active_asset:
                self.inp_rot_p.clearText()
                int_y = float(p)
                if hasattr(self.active_asset, "direction") and self.active_asset:
                    self.active_asset.direction[1] = int_y
                else:
                    if self.active_asset:
                        self.active_asset.set_p(int_y)

    def set_node_r(self, r):
        if r and isinstance(r, str):
            if self.active_asset:
                self.inp_rot_r.clearText()
                int_z = float(r)
                if hasattr(self.active_asset, "direction") and self.active_asset:
                    self.active_asset.direction[2] = int_z
                else:
                    if self.active_asset:
                        self.active_asset.set_r(int_z)

    def set_node_scale_x(self, unit):
        if unit and isinstance(unit, str):
            if self.active_asset:
                self.inp_scale_x.clearText()
                int_x = float(unit)
                if hasattr(self.active_asset, "pos") and self.active_asset:
                    self.active_asset.pos[0] = int_x
                else:
                    if self.active_asset:
                        self.active_asset.set_x(int_x)

    def set_node_scale_y(self, unit):
        if unit and isinstance(unit, str):
            if self.active_asset:
                self.inp_scale_y.clearText()
                int_y = float(unit)
                if hasattr(self.active_asset, "pos") and self.active_asset:
                    self.active_asset.pos[1] = int_y
                else:
                    if self.active_asset:
                        self.active_asset.set_y(int_y)

    def set_node_scale_z(self, unit):
        if unit and isinstance(unit, str):
            if self.active_asset:
                self.inp_scale_z.clearText()
                int_z = float(unit)
                if hasattr(self.active_asset, "pos") and self.active_asset:
                    self.active_asset.pos[2] = int_z
                else:
                    if self.active_asset:
                        self.active_asset.set_z(int_z)

    def set_joint_pos_x(self, pos):
        if pos and isinstance(pos, str):
            if self.active_asset:
                self.inp_pos_x.clearText()
                int_x = float(pos)
                self.active_asset.set_x(int_x)

    def set_joint_pos_y(self, pos):
        if pos and isinstance(pos, str):
            if self.active_asset:
                self.inp_pos_y.clearText()
                int_y = float(pos)
                self.active_asset.set_y(int_y)

    def set_joint_pos_z(self, pos):
        if pos and isinstance(pos, str):
            if self.active_asset:
                self.inp_pos_z.clearText()
                int_z = float(pos)
                self.active_asset.set_z(int_z)

    def set_joint_h(self, h):
        if h and isinstance(h, str):
            if self.active_asset:
                self.inp_rot_h.clearText()
                int_x = float(h)
                self.active_asset.set_h(int_x)

    def set_joint_p(self, p):
        if p and isinstance(p, str):
            if self.active_asset:
                self.inp_rot_p.clearText()
                int_y = float(p)
                self.active_asset.set_p(int_y)

    def set_joint_r(self, r):
        if r and isinstance(r, str):
            if self.active_asset:
                self.inp_rot_r.clearText()
                int_z = float(r)
                self.active_asset.set_r(int_z)

    def set_joint_scale_x(self, unit):
        if unit and isinstance(unit, str):
            if self.active_asset:
                self.inp_scale_x.clearText()
                int_x = float(unit)
                self.active_asset.set_x(int_x)

    def set_joint_scale_y(self, unit):
        if unit and isinstance(unit, str):
            if self.active_asset:
                self.inp_scale_y.clearText()
                int_y = float(unit)
                self.active_asset.set_y(int_y)

    def set_joint_scale_z(self, unit):
        if unit and isinstance(unit, str):
            if self.active_asset:
                self.inp_scale_z.clearText()
                int_z = float(unit)
                self.active_asset.set_z(int_z)

    def set_manipulation_mode(self, mode):
        if mode and mode == 1:
            self.asset_manipulation_modes["Positioning"] = True
            self.asset_manipulation_modes["Rotation"] = False
        elif mode and mode == 2:
            self.asset_manipulation_modes["Positioning"] = False
            self.asset_manipulation_modes["Rotation"] = True

    def set_rotation_mode(self, mode):
        if mode and mode == 1:
            self.rotation_modes["H"] = True
            self.rotation_modes["P"] = False
            self.rotation_modes["R"] = False

        if mode and mode == 2:
            self.rotation_modes["H"] = False
            self.rotation_modes["P"] = True
            self.rotation_modes["R"] = False

        if mode and mode == 3:
            self.rotation_modes["H"] = False
            self.rotation_modes["P"] = False
            self.rotation_modes["R"] = True

    def save_asset_orientation(self):
        if exists("{0}/Editor/Saves".format(self.game_dir)):
            if self.assets:
                asset_json = {}
                for asset in self.assets:
                    if not render.find("**/{0}".format(asset)).is_empty():
                        name = render.find("**/{0}".format(asset)).get_name()
                        pos = render.find("**/{0}".format(asset)).get_pos()
                        hpr = render.find("**/{0}".format(asset)).get_hpr()
                        scale = render.find("**/{0}".format(asset)).get_scale()
                        asset_json[name] = [(pos[0], pos[1], pos[2]),
                                            (hpr[0], hpr[1], hpr[2]),
                                            (scale[0], scale[1], scale[2])]

                asset_json_dump = json.dumps(asset_json, indent = 4)
                with open('{0}/Editor/Saves/assets_pos.json'.format(self.game_dir), 'w') as f:
                    f.write(str(asset_json_dump))

    def save_joint_item_orientation(self):
        if exists("{0}/Editor/Saves".format(self.game_dir)):
            if self.active_item:
                asset_json = {}
                name = self.active_item.get_name()
                pos = self.active_item.get_pos()
                hpr = self.active_item.get_hpr()
                scale = self.active_item.get_scale()
                asset_json[name] = [(pos[0], pos[1], pos[2]),
                                    (hpr[0], hpr[1], hpr[2]),
                                    (scale[0], scale[1], scale[2])]

                asset_json_dump = json.dumps(asset_json, indent = 4)
                with open('{0}/Editor/Saves/item_pos.json'.format(self.game_dir), 'w') as f:
                    f.write(str(asset_json_dump))

    def select_asset_from_list(self, asset):
        if asset and isinstance(asset, str):
            if not render.find("**/{0}".format(asset)).is_empty():
                self.active_asset_from_list = render.find("**/{0}".format(asset))
                if self.active_joint_from_list:
                    self.attach_to_joint(actor=self.active_asset,
                                         item=self.active_asset_from_list,
                                         joint=self.active_joint_from_list,
                                         wrt=False)
                    self.is_item_attached_to_joint = True
                if (not self.active_joint_from_list
                        and not self.active_joint_from_list):
                    self.is_asset_selected_from_list = True

                """self.active_asset_from_list = render.find("**/{0}".format(asset))
                if (self.active_joint_from_list
                        and self.active_item):
                    import pdb; pdb.set_trace()
                    self.attach_to_joint(actor=self.active_asset_from_list,
                                         item=self.active_item,
                                         joint=self.active_joint_from_list,
                                         wrt=False)
                    self.is_item_attached_to_joint = True
                if (not self.active_joint_from_list
                        and not self.active_joint_from_list):
                    self.is_asset_selected_from_list = True"""

    def select_joint_from_list(self, joint):
        if joint and isinstance(joint, str):
            # if asset is an actor
            if self.active_asset and self.active_asset.get_name():
                name = self.active_asset.get_name()
                if self.actor_refs.get(name):
                    self.active_joint_from_list = self.actor_refs[name].expose_joint(None, "modelRoot", joint)

    def ui_geom_collector(self):
        """ Function    : ui_geom_collector

            Description : Collect textures.

            Input       : None

            Output      : None

            Return      : Dictionary
        """
        tex_path = self.transform_path(path="{0}/Editor/UI/".format(self.game_dir),
                                       style='compat')
        ui_geoms = {}
        if exists(tex_path):
            for root, dirs, files in walk(tex_path, topdown=True):
                for file in files:
                    if file.endswith(".egg"):
                        key = re.sub('.egg$', '', file)
                        path = str(PurePath("{0}/".format(root), file))
                        ui_geoms[key] = Filename.from_os_specific(path).getFullpath()
                    elif file.endswith(".egg.bam"):
                        key = re.sub('.egg.bam$', '', file)
                        path = str(PurePath("{0}/".format(root), file))
                        ui_geoms[key] = Filename.from_os_specific(path).getFullpath()
            return ui_geoms

    def transform_path(self, path, style):
        if isinstance(path, str):
            if style == 'unix':
                transformed_path = str(PurePath(path))
                transformed_path = Filename.from_os_specific(transformed_path)
                return transformed_path
            elif style == 'compat':
                transformed_path = Filename(path).to_os_specific()
                return transformed_path

    def update_flame(self, task):
        if self.flame_np:
            time = task.time
            self.flame_np.set_shader_input("iTime", time)

        return task.cont

    def set_shader(self, name):
        if name:
            if not render.find("**/flame").is_empty():
                # self.render_pipeline.reload_shaders()
                self.flame_np = render.find("**/flame")
                self.flame_np.set_name("flame")
                scale = self.flame_np.get_scale()
                self.flame_np.set_scale(2, scale[1], scale[2])
                self.render_pipeline.set_effect(self.flame_np,
                                                "{0}/Engine/Renderer/effects/{1}.yaml".format(self.game_dir, name),
                                                {"render_gbuffer": True,
                                                 "render_shadow": True,
                                                 "alpha_testing": True,
                                                 "normal_mapping": True})
                self.flame_np.setBillboardPointEye()

                taskMgr.add(self.update_flame, "update_flame")

    def update_scene(self, task):
        self.accept("mouse1", self.select)
        self.accept("mouse1-up", self.drop_down)
        self.accept("mouse3-up", self.unselect)
        self.accept("wheel_up", self.input_wheel_up)
        self.accept("wheel_down", self.input_wheel_down)
        self.accept("z", self.undo_positioning)
        self.accept("x", self.undo_rotation)
        self.accept("c", self.undo_scaling)

        self.mouse_click_handler()
        self.move_with_cursor()

        if (self.active_asset
                and self.is_asset_picked_up
                and not self.is_joints_list_ui_active):
            if self.is_asset_actor(asset=self.active_asset):
                self.scrolled_list_actor_joints_empty.hide()
                self.scrolled_list_actor_joints_lbl_desc_empty.hide()
                self.is_joints_list_ui_active = True
                self.messenger.send("set_joints_list_ui")
                name = self.active_asset.get_name()
            else:
                name = self.active_asset.get_name()
            self.active_asset_text.setText(name)

        if (self.active_asset_from_list
                and self.is_asset_picked_up
                and not self.is_joints_list_ui_active):
            if self.is_asset_actor(asset=self.active_asset_from_list):
                self.scrolled_list_actor_joints_empty.hide()
                self.scrolled_list_actor_joints_lbl_desc_empty.hide()
                self.is_joints_list_ui_active = True
                self.messenger.send("set_joints_list_ui")
                name = self.active_asset_from_list.get_name()
            else:
                name = self.active_asset_from_list.get_name()
            self.active_asset_text.setText(name)

        if (not self.is_asset_picked_up
                and not self.is_asset_selected):
            self.is_joints_list_ui_active = False
            self.scrolled_list_actor_joints_empty.show()
            self.scrolled_list_actor_joints_lbl_desc_empty.show()
            if (self.scrolled_list_actor_joints
                    and self.scrolled_list_actor_joints_lbl_desc):
                self.scrolled_list_actor_joints.remove_node()
                self.scrolled_list_actor_joints_lbl_desc.remove_node()

        self.accept("set_joints_list_ui", self.set_joints_list_ui)
        self.update_fields()
        return task.cont


editor = Editor()
editor.run()
