import re
from os import walk
from os.path import exists

from direct.task.TaskManagerGlobal import taskMgr
from panda3d.core import *
from pathlib import Path, PurePath
from Editor.editor_ui import EditorUI

import json


class Editor:
    def __init__(self):
        self.base = base
        self.game_dir = str(Path.cwd())
        self.editor_ui = EditorUI(self)
        self.is_actor = False
        self.is_actor_busy = False
        self.assets = {}

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

        if hasattr(base, "player_ref") \
                and base.player_ref \
                and hasattr(base, "npcs_actor_refs") \
                and base.npcs_actor_refs:
            self.actor_refs = {base.player_ref.get_name(): base.player_ref}
            for name in base.npcs_actor_refs:
                self.actor_refs[name] = base.npcs_actor_refs

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

        """ History """
        self.history_names = {}
        self.history_steps = []
        self.history_pos_steps = []
        self.history_hpr_steps = []
        self.history_scale_steps = []

        """ Meshes """
        self.collider_plane = Plane(Vec3(0, 0, 1), Point3(0, 0, 0))
        self.mpos = None
        self.axis_arrows = self.base.loader.load_model("{0}/Editor/UI/axis_arrows.egg".format(self.game_dir),
                                                       noCache=True)
        self.axis_arrows.set_scale(0.5)
        self.axis_arrows.reparent_to(render)
        self.axis_arrows.hide()

        self.gizmo_mesh = self.base.loader.load_model("{0}/Editor/UI/gizmo_mesh.egg".format(self.game_dir),
                                                      noCache=True)
        self.gizmo_mesh.set_scale(0.5)
        self.gizmo_mesh.reparent_to(render)
        self.gizmo_mesh.hide()

        self.traverser = CollisionTraverser('traverser')
        self.col_handler = CollisionHandlerQueue()
        self.picker_node = CollisionNode('mouseRay')
        self.picker_np = self.base.camera.attachNewNode(self.picker_node)
        self.picker_node.set_from_collide_mask(GeomNode.get_default_collide_mask())
        self.picker_ray = CollisionRay()
        self.picker_node.add_solid(self.picker_ray)
        self.traverser.add_collider(self.picker_np, self.col_handler)

    def set_editor(self):
        if hasattr(base, "level_assets") and base.level_assets:
            self.assets = {}
            for name in base.level_assets['name']:
                if not render.find("**/{0}".format(name)).is_empty():
                    self.assets[name] = render.find("**/{0}:BS".format(name))

        self.editor_ui.set_ui()
        self.editor_ui.set_ui_rotation()
        self.editor_ui.set_ui_manipulation_modes()
        taskMgr.add(self.update_scene, "update_scene")

    def get_actor_joints(self):
        if self.active_asset:
            if self.is_asset_actor(asset=self.active_asset):
                name = self.active_asset.get_name()
                joints = self.actor_refs.get(name).get_joints()
                if joints:
                    return joints

        if self.active_asset_from_list:
            if self.is_asset_actor(asset=self.active_asset_from_list):
                name = self.active_asset_from_list.get_name()
                joints = self.actor_refs.get(name).get_joints()
                if joints:
                    return joints

    def is_asset_actor(self, asset):
        if asset and not asset.find("**/+Character").is_empty():
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
        if self.is_asset_selected_from_list:
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

                asset_json_dump = json.dumps(asset_json, indent=4)
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

                asset_json_dump = json.dumps(asset_json, indent=4)
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

                if self.get_actor_joints():
                    self.is_actor = True
                else:
                    self.is_actor = False

                # Если выбран ассет и он не актер, а также есть выбранный актер,
                # считать этот ассет айтемом для джойнта, иначе: обычным ассетом.
                self.active_asset_from_list = render.find("**/{0}".format(asset))
                if (self.is_actor and not self.is_asset_actor(asset=self.active_asset_from_list)
                        and not self.is_actor_joint_busy(joint=self.active_joint_from_list)):
                    self.active_item = self.active_asset_from_list
                    if (self.active_joint_from_list
                            and self.active_item):
                        # import pdb; pdb.set_trace()
                        self.attach_to_joint(actor=self.active_asset_from_list,
                                             item=self.active_item,
                                             joint=self.active_joint_from_list,
                                             wrt=False)
                        self.is_item_attached_to_joint = True
                    if (not self.active_joint_from_list
                            and not self.active_joint_from_list):
                        self.is_asset_selected_from_list = True

                elif (not self.is_actor and self.is_asset_actor(asset=self.active_asset_from_list)
                      and not self.is_actor_joint_busy(joint=self.active_joint_from_list)):
                    self.is_actor = True
                    if (not self.active_joint_from_list
                            and not self.active_joint_from_list):
                        self.is_asset_selected_from_list = True

                elif (self.is_actor and self.is_asset_actor(asset=self.active_asset_from_list)
                      and self.is_actor_joint_busy(joint=self.active_joint_from_list)):
                    self.is_actor_busy = True
                    if (not self.active_joint_from_list
                            and not self.active_joint_from_list):
                        self.is_asset_selected_from_list = True

    def select_joint_from_list(self, joint):
        if joint and isinstance(joint, str):
            # if asset is an actor
            if self.active_asset and self.active_asset.get_name():
                name = self.active_asset.get_name()
                if self.actor_refs.get(name):
                    self.active_joint_from_list = self.actor_refs[name].expose_joint(None, "modelRoot", joint)

            if self.active_asset_from_list and self.active_asset_from_list.get_name():
                name = self.active_asset_from_list.get_name()
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
                    if self.mouse_in_asset_text:
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

    def update_scene(self, task):
        self.base.accept("mouse1", self.select)
        self.base.accept("mouse1-up", self.drop_down)
        self.base.accept("mouse3-up", self.unselect)
        self.base.accept("wheel_up", self.input_wheel_up)
        self.base.accept("wheel_down", self.input_wheel_down)
        self.base.accept("z", self.undo_positioning)
        self.base.accept("x", self.undo_rotation)
        self.base.accept("c", self.undo_scaling)

        self.mouse_click_handler()
        self.move_with_cursor()

        if (self.active_asset
                and self.is_asset_picked_up
                and not self.is_joints_list_ui_active):
            if self.is_asset_actor(asset=self.active_asset):
                self.scrolled_list_actor_joints_empty.hide()
                self.scrolled_list_actor_joints_lbl_desc_empty.hide()
                self.is_joints_list_ui_active = True
                self.base.messenger.send("set_joints_list_ui")
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
                self.base.messenger.send("set_joints_list_ui")
                name = self.active_asset_from_list.get_name()
            else:
                name = self.active_asset_from_list.get_name()
            self.active_asset_text.setText(name)

        if (not self.is_asset_picked_up
                and not self.is_asset_selected
                and self.scrolled_list_actor_joints_empty
                and self.scrolled_list_actor_joints_lbl_desc_empty):
            self.is_joints_list_ui_active = False
            self.scrolled_list_actor_joints_empty.show()
            self.scrolled_list_actor_joints_lbl_desc_empty.show()
            if (self.scrolled_list_actor_joints
                    and self.scrolled_list_actor_joints_lbl_desc):
                self.scrolled_list_actor_joints.remove_node()
                self.scrolled_list_actor_joints_lbl_desc.remove_node()

        self.base.accept("set_joints_list_ui", self.editor_ui.set_joints_list_ui)
        self.update_fields()

        if self.base.game_mode is False and self.base.menu_mode:
            self.frame.destroy()
            return task.done

        return task.cont
