from direct.gui.DirectEntry import DirectEntry
from panda3d.core import TextNode

from direct.gui.DirectFrame import DirectFrame
from direct.gui.DirectButton import DirectButton
from direct.gui.DirectLabel import DirectLabel
from direct.gui.DirectRadioButton import DirectRadioButton
from direct.gui.DirectScrolledList import DirectScrolledList
from direct.gui.OnscreenText import OnscreenText


class EditorUI:
    def __init__(self, editor):
        self.editor = editor

    def set_ui(self):
        if not self.editor.frame:
            self.editor.frame = DirectFrame(frameColor=(0, 0, 0, 0.6), pos=(0, 0, 0),
                                            frameSize=self.editor.frame_size, geom=self.editor.menu_geom)
            self.editor.active_asset_text = OnscreenText(text="",
                                                         scale=0.04,
                                                         fg=(255, 255, 255, 0.9),
                                                         font=self.editor.font.load_font(self.editor.menu_font),
                                                         align=TextNode.ALeft,
                                                         parent=self.editor.frame,
                                                         mayChange=True)

            self.editor.mouse_in_asset_text = OnscreenText(text="",
                                                           scale=0.03,
                                                           fg=(255, 255, 255, 0.9),
                                                           font=self.editor.font.load_font(self.editor.menu_font),
                                                           align=TextNode.ALeft,
                                                           parent=self.editor.frame,
                                                           mayChange=True)

            self.editor.scrolled_list_lbl = DirectLabel(text="Assets Overview",
                                                        text_fg=(255, 255, 255, 0.9),
                                                        text_font=self.editor.font.load_font(self.editor.menu_font),
                                                        frameColor=(255, 255, 255, 0),
                                                        scale=.05, borderWidth=(self.editor.w, self.editor.h),
                                                        parent=self.editor.frame)

            ui_geoms = self.editor.ui_geom_collector()
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
                if not self.editor.assets_bs:
                    self.editor.scrolled_list_lbl_na = DirectLabel(text="N/A",
                                                                   text_fg=(255, 255, 255, 0.9),
                                                                   text_font=self.editor.font.load_font(
                                                                       self.editor.menu_font),
                                                                   frameColor=(255, 255, 255, 0),
                                                                   scale=.04,
                                                                   borderWidth=(self.editor.w, self.editor.h),
                                                                   parent=self.editor.frame)
                if self.editor.assets_bs:
                    btn_inc_pos = 0.46
                    for index, asset in enumerate(self.editor.assets_bs, 1):
                        btn = DirectButton(text="{0}".format(asset),
                                           text_fg=(255, 255, 255, 1), relief=2,
                                           text_font=self.editor.font.load_font(self.editor.menu_font),
                                           frameColor=(0, 0, 0, 1),
                                           scale=.03, borderWidth=(self.editor.w, self.editor.h),
                                           geom=geoms_scrolled_dbtn, geom_scale=(15.3, 0, 2),
                                           clickSound="",
                                           command=self.editor.select_asset_from_list,
                                           extraArgs=[asset],
                                           parent=self.editor.frame)
                        btn_inc_pos += -0.08
                        btn_list.append(btn)

                    self.editor.scrolled_list = DirectScrolledList(
                        decButton_pos=(0.35, 0, 0.46),
                        decButton_scale=(5, 1, 0.5),
                        decButton_text="",
                        decButton_text_scale=0.04,
                        decButton_borderWidth=(0, 0),
                        decButton_geom=geoms_scrolled_dec,
                        decButton_geom_scale=0.08,

                        incButton_pos=(0.35, 0, btn_inc_pos),
                        incButton_scale=(5, 1, 0.5),
                        incButton_text="",
                        incButton_text_scale=0.04,
                        incButton_borderWidth=(0, 0),
                        incButton_geom=geoms_scrolled_inc,
                        incButton_geom_scale=0.08,

                        frameSize=self.editor.frame_scrolled_size,
                        frameColor=(0, 0, 0, 0),
                        numItemsVisible=15,
                        forceHeight=0.07,
                        items=btn_list,
                        itemFrame_frameSize=self.editor.frame_scrolled_inner_size,
                        itemFrame_pos=(0.35, 0, 0.4),
                        parent=self.editor.frame
                    )

                self.editor.scrolled_list_lbl_desc = DirectLabel(text="Select asset \nfor manipulations on the scene",
                                                                 text_fg=(255, 255, 255, 0.9),
                                                                 text_font=self.editor.font.load_font(
                                                                     self.editor.menu_font),
                                                                 frameColor=(255, 255, 255, 0),
                                                                 scale=.025, borderWidth=(self.editor.w, self.editor.h),
                                                                 parent=self.editor.frame)

                self.editor.asset_management_title = DirectLabel(text="Assets Management",
                                                                 text_fg=(255, 255, 255, 0.9),
                                                                 text_font=self.editor.font.load_font(
                                                                     self.editor.menu_font),
                                                                 frameColor=(255, 255, 255, 0),
                                                                 scale=.05, borderWidth=(self.editor.w, self.editor.h),
                                                                 parent=self.editor.frame)

                self.editor.asset_management_desc = DirectLabel(text="Use these fields to move or rotate geometry",
                                                                text_fg=(255, 255, 255, 0.9),
                                                                text_font=self.editor.font.load_font(
                                                                    self.editor.menu_font),
                                                                frameColor=(255, 255, 255, 0),
                                                                scale=.025, borderWidth=(self.editor.w, self.editor.h),
                                                                parent=self.editor.frame)

                self.editor.lbl_pos_x = DirectLabel(text="X Axis",
                                                    text_fg=(255, 255, 255, 0.9),
                                                    text_font=self.editor.font.load_font(self.editor.menu_font),
                                                    frameColor=(255, 255, 255, 0),
                                                    scale=.03, borderWidth=(self.editor.w, self.editor.h),
                                                    parent=self.editor.frame)

                self.editor.lbl_pos_y = DirectLabel(text="Y Axis",
                                                    text_fg=(255, 255, 255, 0.9),
                                                    text_font=self.editor.font.load_font(self.editor.menu_font),
                                                    frameColor=(255, 255, 255, 0),
                                                    scale=.03, borderWidth=(self.editor.w, self.editor.h),
                                                    parent=self.editor.frame)

                self.editor.lbl_pos_z = DirectLabel(text="Z Axis",
                                                    text_fg=(255, 255, 255, 0.9),
                                                    text_font=self.editor.font.load_font(self.editor.menu_font),
                                                    frameColor=(255, 255, 255, 0),
                                                    scale=.03, borderWidth=(self.editor.w, self.editor.h),
                                                    parent=self.editor.frame)

                self.editor.lbl_rot_h = DirectLabel(text="Heading",
                                                    text_fg=(255, 255, 255, 0.9),
                                                    text_font=self.editor.font.load_font(self.editor.menu_font),
                                                    frameColor=(255, 255, 255, 0),
                                                    scale=.03, borderWidth=(self.editor.w, self.editor.h),
                                                    parent=self.editor.frame)

                self.editor.lbl_rot_p = DirectLabel(text="Pitch",
                                                    text_fg=(255, 255, 255, 0.9),
                                                    text_font=self.editor.font.load_font(self.editor.menu_font),
                                                    frameColor=(255, 255, 255, 0),
                                                    scale=.03, borderWidth=(self.editor.w, self.editor.h),
                                                    parent=self.editor.frame)

                self.editor.lbl_rot_r = DirectLabel(text="Rotation",
                                                    text_fg=(255, 255, 255, 0.9),
                                                    text_font=self.editor.font.load_font(self.editor.menu_font),
                                                    frameColor=(255, 255, 255, 0),
                                                    scale=.03, borderWidth=(self.editor.w, self.editor.h),
                                                    parent=self.editor.frame)

                self.editor.lbl_scale_x = DirectLabel(text="X Scale",
                                                      text_fg=(255, 255, 255, 0.9),
                                                      text_font=self.editor.font.load_font(self.editor.menu_font),
                                                      frameColor=(255, 255, 255, 0),
                                                      scale=.03, borderWidth=(self.editor.w, self.editor.h),
                                                      parent=self.editor.frame)

                self.editor.lbl_scale_y = DirectLabel(text="Y Scale",
                                                      text_fg=(255, 255, 255, 0.9),
                                                      text_font=self.editor.font.load_font(self.editor.menu_font),
                                                      frameColor=(255, 255, 255, 0),
                                                      scale=.03, borderWidth=(self.editor.w, self.editor.h),
                                                      parent=self.editor.frame)

                self.editor.lbl_scale_z = DirectLabel(text="Z Scale",
                                                      text_fg=(255, 255, 255, 0.9),
                                                      text_font=self.editor.font.load_font(self.editor.menu_font),
                                                      frameColor=(255, 255, 255, 0),
                                                      scale=.03, borderWidth=(self.editor.w, self.editor.h),
                                                      parent=self.editor.frame)

                self.editor.inp_pos_x = DirectEntry(initialText="",
                                                    text_bg=(0, 0, 0, 1),
                                                    entryFont=self.editor.font.load_font(self.editor.menu_font),
                                                    text_align=TextNode.A_center,
                                                    scale=.03, width=7, borderWidth=(self.editor.w, self.editor.h),
                                                    parent=self.editor.frame, cursorKeys=1,
                                                    command=self.editor.set_node_pos_x,
                                                    focusInCommand=self.editor.input_clear_pos_x)

                self.editor.inp_pos_y = DirectEntry(initialText="",
                                                    text_bg=(0, 0, 0, 1),
                                                    entryFont=self.editor.font.load_font(self.editor.menu_font),
                                                    text_align=TextNode.A_center,
                                                    scale=.03, width=7, borderWidth=(self.editor.w, self.editor.h),
                                                    parent=self.editor.frame, cursorKeys=1,
                                                    command=self.editor.set_node_pos_y,
                                                    focusInCommand=self.editor.input_clear_pos_y)

                self.editor.inp_pos_z = DirectEntry(initialText="",
                                                    text_bg=(0, 0, 0, 1),
                                                    entryFont=self.editor.font.load_font(self.editor.menu_font),
                                                    text_align=TextNode.A_center,
                                                    scale=.03, width=7, borderWidth=(self.editor.w, self.editor.h),
                                                    parent=self.editor.frame, cursorKeys=1,
                                                    command=self.editor.set_node_pos_z,
                                                    focusInCommand=self.editor.input_clear_pos_z)

                self.editor.inp_rot_h = DirectEntry(initialText="",
                                                    text_bg=(0, 0, 0, 1),
                                                    entryFont=self.editor.font.load_font(self.editor.menu_font),
                                                    text_align=TextNode.A_center,
                                                    scale=.03, width=7, borderWidth=(self.editor.w, self.editor.h),
                                                    parent=self.editor.frame, cursorKeys=1,
                                                    command=self.editor.set_node_h,
                                                    focusInCommand=self.editor.input_clear_rot_h)

                self.editor.inp_rot_p = DirectEntry(initialText="",
                                                    text_bg=(0, 0, 0, 1),
                                                    entryFont=self.editor.font.load_font(self.editor.menu_font),
                                                    text_align=TextNode.A_center,
                                                    scale=.03, width=7, borderWidth=(self.editor.w, self.editor.h),
                                                    parent=self.editor.frame, cursorKeys=1,
                                                    command=self.editor.set_node_p,
                                                    focusInCommand=self.editor.input_clear_rot_p)

                self.editor.inp_rot_r = DirectEntry(initialText="",
                                                    text_bg=(0, 0, 0, 1),
                                                    entryFont=self.editor.font.load_font(self.editor.menu_font),
                                                    text_align=TextNode.A_center,
                                                    scale=.03, width=7, borderWidth=(self.editor.w, self.editor.h),
                                                    parent=self.editor.frame, cursorKeys=1,
                                                    command=self.editor.set_node_r,
                                                    focusInCommand=self.editor.input_clear_rot_r)

                self.editor.inp_scale_x = DirectEntry(initialText="",
                                                      text_bg=(0, 0, 0, 1),
                                                      entryFont=self.editor.font.load_font(self.editor.menu_font),
                                                      text_align=TextNode.A_center,
                                                      scale=.03, width=7, borderWidth=(self.editor.w, self.editor.h),
                                                      parent=self.editor.frame, cursorKeys=1,
                                                      command=self.editor.set_node_scale_x,
                                                      focusInCommand=self.editor.input_clear_scale_x)

                self.editor.inp_scale_y = DirectEntry(initialText="",
                                                      text_bg=(0, 0, 0, 1),
                                                      entryFont=self.editor.font.load_font(self.editor.menu_font),
                                                      text_align=TextNode.A_center,
                                                      scale=.03, width=7, borderWidth=(self.editor.w, self.editor.h),
                                                      parent=self.editor.frame, cursorKeys=1,
                                                      command=self.editor.set_node_scale_y,
                                                      focusInCommand=self.editor.input_clear_scale_y)

                self.editor.inp_scale_z = DirectEntry(initialText="",
                                                      text_bg=(0, 0, 0, 1),
                                                      entryFont=self.editor.font.load_font(self.editor.menu_font),
                                                      text_align=TextNode.A_center,
                                                      scale=.03, width=7, borderWidth=(self.editor.w, self.editor.h),
                                                      parent=self.editor.frame, cursorKeys=1,
                                                      command=self.editor.set_node_scale_z,
                                                      focusInCommand=self.editor.input_clear_scale_z)

                self.editor.save_asset_pos = DirectButton(text="Save Asset Pos",
                                                          text_fg=(255, 255, 255, 1), relief=2,
                                                          text_font=self.editor.font.load_font(self.editor.menu_font),
                                                          frameColor=(0, 0, 0, 1),
                                                          scale=.03, borderWidth=(self.editor.w, self.editor.h),
                                                          geom=geoms_scrolled_dbtn, geom_scale=(11.3, 0, 2),
                                                          clickSound="",
                                                          parent=self.editor.frame,
                                                          command=self.editor.save_asset_orientation)

                self.editor.joint_item_management_title = DirectLabel(text="Joint Child Management",
                                                                      text_fg=(255, 255, 255, 0.9),
                                                                      text_font=self.editor.font.load_font(
                                                                          self.editor.menu_font),
                                                                      frameColor=(255, 255, 255, 0),
                                                                      scale=.05,
                                                                      borderWidth=(self.editor.w, self.editor.h),
                                                                      parent=self.editor.frame)

                self.editor.joint_item_management_desc = DirectLabel(
                    text="Use these fields to move or rotate child geometry",
                    text_fg=(255, 255, 255, 0.9),
                    text_font=self.editor.font.load_font(self.editor.menu_font),
                    frameColor=(255, 255, 255, 0),
                    scale=.025, borderWidth=(self.editor.w, self.editor.h),
                    parent=self.editor.frame)

                self.editor.lbl_joint_item_pos_x = DirectLabel(text="X Axis",
                                                               text_fg=(255, 255, 255, 0.9),
                                                               text_font=self.editor.font.load_font(
                                                                   self.editor.menu_font),
                                                               frameColor=(255, 255, 255, 0),
                                                               scale=.03, borderWidth=(self.editor.w, self.editor.h),
                                                               parent=self.editor.frame)

                self.editor.lbl_joint_item_pos_y = DirectLabel(text="Y Axis",
                                                               text_fg=(255, 255, 255, 0.9),
                                                               text_font=self.editor.font.load_font(
                                                                   self.editor.menu_font),
                                                               frameColor=(255, 255, 255, 0),
                                                               scale=.03, borderWidth=(self.editor.w, self.editor.h),
                                                               parent=self.editor.frame)

                self.editor.lbl_joint_item_pos_z = DirectLabel(text="Z Axis",
                                                               text_fg=(255, 255, 255, 0.9),
                                                               text_font=self.editor.font.load_font(
                                                                   self.editor.menu_font),
                                                               frameColor=(255, 255, 255, 0),
                                                               scale=.03, borderWidth=(self.editor.w, self.editor.h),
                                                               parent=self.editor.frame)

                self.editor.lbl_joint_item_rot_h = DirectLabel(text="Heading",
                                                               text_fg=(255, 255, 255, 0.9),
                                                               text_font=self.editor.font.load_font(
                                                                   self.editor.menu_font),
                                                               frameColor=(255, 255, 255, 0),
                                                               scale=.03, borderWidth=(self.editor.w, self.editor.h),
                                                               parent=self.editor.frame)

                self.editor.lbl_joint_item_rot_p = DirectLabel(text="Pitch",
                                                               text_fg=(255, 255, 255, 0.9),
                                                               text_font=self.editor.font.load_font(
                                                                   self.editor.menu_font),
                                                               frameColor=(255, 255, 255, 0),
                                                               scale=.03, borderWidth=(self.editor.w, self.editor.h),
                                                               parent=self.editor.frame)

                self.editor.lbl_joint_item_rot_r = DirectLabel(text="Rotation",
                                                               text_fg=(255, 255, 255, 0.9),
                                                               text_font=self.editor.font.load_font(
                                                                   self.editor.menu_font),
                                                               frameColor=(255, 255, 255, 0),
                                                               scale=.03, borderWidth=(self.editor.w, self.editor.h),
                                                               parent=self.editor.frame)

                self.editor.lbl_joint_item_scale_x = DirectLabel(text="X Scale",
                                                                 text_fg=(255, 255, 255, 0.9),
                                                                 text_font=self.editor.font.load_font(
                                                                     self.editor.menu_font),
                                                                 frameColor=(255, 255, 255, 0),
                                                                 scale=.03, borderWidth=(self.editor.w, self.editor.h),
                                                                 parent=self.editor.frame)

                self.editor.lbl_joint_item_scale_y = DirectLabel(text="Y Scale",
                                                                 text_fg=(255, 255, 255, 0.9),
                                                                 text_font=self.editor.font.load_font(
                                                                     self.editor.menu_font),
                                                                 frameColor=(255, 255, 255, 0),
                                                                 scale=.03, borderWidth=(self.editor.w, self.editor.h),
                                                                 parent=self.editor.frame)

                self.editor.lbl_joint_item_scale_z = DirectLabel(text="Z Scale",
                                                                 text_fg=(255, 255, 255, 0.9),
                                                                 text_font=self.editor.font.load_font(
                                                                     self.editor.menu_font),
                                                                 frameColor=(255, 255, 255, 0),
                                                                 scale=.03, borderWidth=(self.editor.w, self.editor.h),
                                                                 parent=self.editor.frame)

                self.editor.inp_joint_item_pos_x = DirectEntry(initialText="",
                                                               text_bg=(0, 0, 0, 1),
                                                               entryFont=self.editor.font.load_font(
                                                                   self.editor.menu_font),
                                                               text_align=TextNode.A_center,
                                                               scale=.03, width=7,
                                                               borderWidth=(self.editor.w, self.editor.h),
                                                               parent=self.editor.frame, cursorKeys=1,
                                                               command=self.editor.set_joint_pos_x,
                                                               focusInCommand=self.editor.input_joint_item_clear_pos_x)

                self.editor.inp_joint_item_pos_y = DirectEntry(initialText="",
                                                               text_bg=(0, 0, 0, 1),
                                                               entryFont=self.editor.font.load_font(
                                                                   self.editor.menu_font),
                                                               text_align=TextNode.A_center,
                                                               scale=.03, width=7,
                                                               borderWidth=(self.editor.w, self.editor.h),
                                                               parent=self.editor.frame, cursorKeys=1,
                                                               command=self.editor.set_joint_pos_y,
                                                               focusInCommand=self.editor.input_joint_item_clear_pos_y)

                self.editor.inp_joint_item_pos_z = DirectEntry(initialText="",
                                                               text_bg=(0, 0, 0, 1),
                                                               entryFont=self.editor.font.load_font(
                                                                   self.editor.menu_font),
                                                               text_align=TextNode.A_center,
                                                               scale=.03, width=7,
                                                               borderWidth=(self.editor.w, self.editor.h),
                                                               parent=self.editor.frame, cursorKeys=1,
                                                               command=self.editor.set_joint_pos_z,
                                                               focusInCommand=self.editor.input_joint_item_clear_pos_z)

                self.editor.inp_joint_item_rot_h = DirectEntry(initialText="",
                                                               text_bg=(0, 0, 0, 1),
                                                               entryFont=self.editor.font.load_font(
                                                                   self.editor.menu_font),
                                                               text_align=TextNode.A_center,
                                                               scale=.03, width=7,
                                                               borderWidth=(self.editor.w, self.editor.h),
                                                               parent=self.editor.frame, cursorKeys=1,
                                                               command=self.editor.set_joint_h,
                                                               focusInCommand=self.editor.input_joint_item_clear_rot_h)

                self.editor.inp_joint_item_rot_p = DirectEntry(initialText="",
                                                               text_bg=(0, 0, 0, 1),
                                                               entryFont=self.editor.font.load_font(
                                                                   self.editor.menu_font),
                                                               text_align=TextNode.A_center,
                                                               scale=.03, width=7,
                                                               borderWidth=(self.editor.w, self.editor.h),
                                                               parent=self.editor.frame, cursorKeys=1,
                                                               command=self.editor.set_joint_p,
                                                               focusInCommand=self.editor.input_joint_item_clear_rot_p)

                self.editor.inp_joint_item_rot_r = DirectEntry(initialText="",
                                                               text_bg=(0, 0, 0, 1),
                                                               entryFont=self.editor.font.load_font(
                                                                   self.editor.menu_font),
                                                               text_align=TextNode.A_center,
                                                               scale=.03, width=7,
                                                               borderWidth=(self.editor.w, self.editor.h),
                                                               parent=self.editor.frame, cursorKeys=1,
                                                               command=self.editor.set_joint_r,
                                                               focusInCommand=self.editor.input_joint_item_clear_rot_r)

                self.editor.inp_joint_item_scale_x = DirectEntry(initialText="",
                                                                 text_bg=(0, 0, 0, 1),
                                                                 entryFont=self.editor.font.load_font(
                                                                     self.editor.menu_font),
                                                                 text_align=TextNode.A_center,
                                                                 scale=.03, width=7,
                                                                 borderWidth=(self.editor.w, self.editor.h),
                                                                 parent=self.editor.frame, cursorKeys=1,
                                                                 command=self.editor.set_joint_scale_x,
                                                                 focusInCommand=self.editor.input_joint_item_clear_scale_x)

                self.editor.inp_joint_item_scale_y = DirectEntry(initialText="",
                                                                 text_bg=(0, 0, 0, 1),
                                                                 entryFont=self.editor.font.load_font(
                                                                     self.editor.menu_font),
                                                                 text_align=TextNode.A_center,
                                                                 scale=.03, width=7,
                                                                 borderWidth=(self.editor.w, self.editor.h),
                                                                 parent=self.editor.frame, cursorKeys=1,
                                                                 command=self.editor.set_joint_scale_y,
                                                                 focusInCommand=self.editor.input_joint_item_clear_scale_y)

                self.editor.inp_joint_item_scale_z = DirectEntry(initialText="",
                                                                 text_bg=(0, 0, 0, 1),
                                                                 entryFont=self.editor.font.load_font(
                                                                     self.editor.menu_font),
                                                                 text_align=TextNode.A_center,
                                                                 scale=.03, width=7,
                                                                 borderWidth=(self.editor.w, self.editor.h),
                                                                 parent=self.editor.frame, cursorKeys=1,
                                                                 command=self.editor.set_joint_scale_z,
                                                                 focusInCommand=self.editor.input_joint_item_clear_scale_z)

                self.editor.save_joint_item_pos = DirectButton(text="Save Item Pos",
                                                               text_fg=(255, 255, 255, 1), relief=2,
                                                               text_font=self.editor.font.load_font(
                                                                   self.editor.menu_font),
                                                               frameColor=(0, 0, 0, 1),
                                                               scale=.03, borderWidth=(self.editor.w, self.editor.h),
                                                               geom=geoms_scrolled_dbtn, geom_scale=(11.3, 0, 2),
                                                               clickSound="",
                                                               parent=self.editor.frame,
                                                               command=self.editor.save_joint_item_orientation)

                self.editor.scrolled_list_actor_joints_lbl = DirectLabel(text="Actor Joints",
                                                                         text_fg=(255, 255, 255, 0.9),
                                                                         text_font=self.editor.font.load_font(
                                                                             self.editor.menu_font),
                                                                         frameColor=(255, 255, 255, 0),
                                                                         scale=.05,
                                                                         borderWidth=(self.editor.w, self.editor.h),
                                                                         parent=self.editor.frame)

                btn2_list = []
                joints = self.editor.get_actor_joints()
                if not joints:
                    btn = DirectButton(text="Where joints, Johnny?",
                                       text_fg=(255, 255, 255, 1), relief=2,
                                       text_font=self.editor.font.load_font(self.editor.menu_font),
                                       frameColor=(0, 0, 0, 1),
                                       scale=.03, borderWidth=(self.editor.w, self.editor.h),
                                       geom=geoms_scrolled_dbtn, geom_scale=(15.3, 0, 2),
                                       clickSound="",
                                       command="",
                                       parent=self.editor.frame)

                    btn2_list.append(btn)
                    self.editor.scrolled_list_actor_joints_empty = DirectScrolledList(
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

                        frameSize=self.editor.frame_scrolled_size,
                        frameColor=(0, 0, 0, 0),
                        numItemsVisible=1,
                        forceHeight=0.11,
                        items=btn2_list,
                        itemFrame_frameSize=self.editor.frame_scrolled_inner_size,
                        itemFrame_pos=(0.35, 0, 0.4),
                        parent=self.editor.frame,
                    )

                    self.editor.scrolled_list_actor_joints_lbl_desc_empty = DirectLabel(
                        text="No actor is selected",
                        text_fg=(255, 255, 255, 0.9),
                        text_font=self.editor.font.load_font(self.editor.menu_font),
                        frameColor=(255, 255, 255, 0),
                        scale=.025, borderWidth=(self.editor.w, self.editor.h),
                        parent=self.editor.frame)

        if self.editor.scrolled_list_lbl:
            self.editor.scrolled_list_lbl.set_pos(-1.65, 0, 0.85)
        if self.editor.scrolled_list_lbl_na:
            self.editor.scrolled_list_lbl_na.set_pos(-1.65, 0, 0.32)
        if self.editor.scrolled_list:
            self.editor.scrolled_list.set_pos(-2.0, 0, 0.32)
        if self.editor.scrolled_list_lbl_desc:
            self.editor.scrolled_list_lbl_desc.set_pos(-1.65, 0, -0.40)

        self.editor.active_asset_text.set_pos(1.3, 0, 0.85)
        self.editor.mouse_in_asset_text.set_pos(-1.2, 0, -0.3)

        self.editor.asset_management_title.set_pos(-1.0, 0, -0.59)
        self.editor.asset_management_desc.set_pos(-0.92, 0, -0.63)

        self.editor.lbl_pos_x.set_pos(-1.2, 0, -0.7)
        self.editor.lbl_pos_y.set_pos(-1.2, 0, -0.8)
        self.editor.lbl_pos_z.set_pos(-1.2, 0, -0.9)

        self.editor.inp_pos_x.set_pos(-1.0, 0, -0.7)
        self.editor.inp_pos_y.set_pos(-1.0, 0, -0.8)
        self.editor.inp_pos_z.set_pos(-1.0, 0, -0.9)

        self.editor.lbl_rot_h.set_pos(-0.75, 0, -0.7)
        self.editor.lbl_rot_p.set_pos(-0.75, 0, -0.8)
        self.editor.lbl_rot_r.set_pos(-0.75, 0, -0.9)

        self.editor.inp_rot_h.set_pos(-0.51, 0, -0.7)
        self.editor.inp_rot_p.set_pos(-0.51, 0, -0.8)
        self.editor.inp_rot_r.set_pos(-0.51, 0, -0.9)

        self.editor.lbl_scale_x.set_pos(-0.25, 0, -0.7)
        self.editor.lbl_scale_y.set_pos(-0.25, 0, -0.8)
        self.editor.lbl_scale_z.set_pos(-0.25, 0, -0.9)

        self.editor.inp_scale_x.set_pos(-0.01, 0, -0.7)
        self.editor.inp_scale_y.set_pos(-0.01, 0, -0.8)
        self.editor.inp_scale_z.set_pos(-0.01, 0, -0.9)

        if self.editor.scrolled_list_actor_joints_lbl:
            self.editor.scrolled_list_actor_joints_lbl.set_pos(-1.65, 0, -0.60)
        if self.editor.scrolled_list_actor_joints_empty:
            self.editor.scrolled_list_actor_joints_empty.set_pos(-2.0, 0, -1.12)
        if self.editor.scrolled_list_actor_joints_lbl_desc_empty:
            self.editor.scrolled_list_actor_joints_lbl_desc_empty.set_pos(-1.65, 0, -0.87)

        self.editor.joint_item_management_title.set_pos(0.6, 0, -0.59)
        self.editor.joint_item_management_desc.set_pos(0.65, 0, -0.63)

        self.editor.lbl_joint_item_pos_x.set_pos(0.35, 0, -0.7)
        self.editor.lbl_joint_item_pos_y.set_pos(0.35, 0, -0.8)
        self.editor.lbl_joint_item_pos_z.set_pos(0.35, 0, -0.9)

        self.editor.inp_joint_item_pos_x.set_pos(0.55, 0, -0.7)
        self.editor.inp_joint_item_pos_y.set_pos(0.55, 0, -0.8)
        self.editor.inp_joint_item_pos_z.set_pos(0.55, 0, -0.9)

        self.editor.lbl_joint_item_rot_h.set_pos(0.75, 0, -0.7)
        self.editor.lbl_joint_item_rot_p.set_pos(0.75, 0, -0.8)
        self.editor.lbl_joint_item_rot_r.set_pos(0.75, 0, -0.9)

        self.editor.inp_joint_item_rot_h.set_pos(0.95, 0, -0.7)
        self.editor.inp_joint_item_rot_p.set_pos(0.95, 0, -0.8)
        self.editor.inp_joint_item_rot_r.set_pos(0.95, 0, -0.9)

        self.editor.lbl_joint_item_scale_x.set_pos(1.15, 0, -0.7)
        self.editor.lbl_joint_item_scale_y.set_pos(1.15, 0, -0.8)
        self.editor.lbl_joint_item_scale_z.set_pos(1.15, 0, -0.9)

        self.editor.inp_joint_item_scale_x.set_pos(1.35, 0, -0.7)
        self.editor.inp_joint_item_scale_y.set_pos(1.35, 0, -0.8)
        self.editor.inp_joint_item_scale_z.set_pos(1.35, 0, -0.9)

        self.editor.save_asset_pos.set_pos(1.7, 0, -0.8)
        self.editor.save_joint_item_pos.set_pos(1.7, 0, -0.9)

        self.editor.inp_pos_x.setText("Axis X")
        self.editor.inp_pos_y.setText("Axis Y")
        self.editor.inp_pos_z.setText("Axis Z")

        self.editor.inp_rot_h.setText("Heading")
        self.editor.inp_rot_p.setText("Pitch")
        self.editor.inp_rot_r.setText("Rotation")

        self.editor.inp_scale_x.setText("Scale X")
        self.editor.inp_scale_y.setText("Scale Y")
        self.editor.inp_scale_z.setText("Scale Z")

        self.editor.inp_joint_item_pos_x.setText("Axis X")
        self.editor.inp_joint_item_pos_y.setText("Axis Y")
        self.editor.inp_joint_item_pos_z.setText("Axis Z")

        self.editor.inp_joint_item_rot_h.setText("Heading")
        self.editor.inp_joint_item_rot_p.setText("Pitch")
        self.editor.inp_joint_item_rot_r.setText("Rotation")

        self.editor.inp_joint_item_scale_x.setText("Scale X")
        self.editor.inp_joint_item_scale_y.setText("Scale Y")
        self.editor.inp_joint_item_scale_z.setText("Scale Z")

    def set_ui_rotation(self):
        ui_geoms = self.editor.ui_geom_collector()
        axis_h_maps = self.editor.base.loader.loadModel(ui_geoms['axis_h_icon'])
        axis_h_geoms = (axis_h_maps.find('**/axis_h_any'), axis_h_maps.find('**/axis_h_pressed'))

        axis_p_maps = self.editor.base.loader.loadModel(ui_geoms['axis_p_icon'])
        axis_p_geoms = (axis_p_maps.find('**/axis_p_any'), axis_p_maps.find('**/axis_p_pressed'))

        axis_r_maps = self.editor.base.loader.loadModel(ui_geoms['axis_r_icon'])
        axis_r_geoms = (axis_r_maps.find('**/axis_r_any'), axis_r_maps.find('**/axis_r_pressed'))

        radbuttons = [

            DirectRadioButton(text='', variable=[0], value=[1], pos=(-1.2, 0, 0.85),
                              parent=self.editor.frame, scale=self.editor.rad_scale,
                              clickSound='',
                              command=self.editor.set_rotation_mode, extraArgs=[1],
                              boxGeom=axis_h_geoms, boxPlacement='Center', frameColor=(255, 255, 255, 0)),

            DirectRadioButton(text='', variable=[0], value=[2], pos=(-1.1, 0, 0.85),
                              parent=self.editor.frame, scale=self.editor.rad_scale,
                              clickSound='',
                              command=self.editor.set_rotation_mode, extraArgs=[2],
                              boxGeom=axis_p_geoms, boxPlacement='Center', frameColor=(255, 255, 255, 0)),

            DirectRadioButton(text='', variable=[0], value=[3], pos=(-1.0, 0, 0.85),
                              parent=self.editor.frame, scale=self.editor.rad_scale,
                              clickSound='',
                              command=self.editor.set_rotation_mode, extraArgs=[3],
                              boxGeom=axis_r_geoms, boxPlacement='Center', frameColor=(255, 255, 255, 0))

        ]

        for radbutton in radbuttons:
            radbutton.setOthers(radbuttons)

    def set_ui_manipulation_modes(self):
        ui_geoms = self.editor.ui_geom_collector()
        pos_mode_maps = self.editor.base.loader.loadModel(ui_geoms['pos_mode_icon'])
        pos_mode_geoms = (pos_mode_maps.find('**/pos_mode_any'), pos_mode_maps.find('**/pos_mode_pressed'))

        rot_mode_maps = self.editor.base.loader.loadModel(ui_geoms['rot_mode_icon'])
        rot_mode_geoms = (rot_mode_maps.find('**/rot_mode_any'), rot_mode_maps.find('**/rot_mode_pressed'))

        radbuttons = [

            DirectRadioButton(text='', variable=[0], value=[1], pos=(-0.8, 0, 0.85),
                              parent=self.editor.frame, scale=self.editor.rad_scale,
                              clickSound='',
                              command=self.editor.set_manipulation_mode, extraArgs=[1],
                              boxGeom=pos_mode_geoms, boxPlacement='Center', frameColor=(255, 255, 255, 0)),

            DirectRadioButton(text='', variable=[0], value=[2], pos=(-0.7, 0, 0.85),
                              parent=self.editor.frame, scale=self.editor.rad_scale,
                              clickSound='',
                              command=self.editor.set_manipulation_mode, extraArgs=[2],
                              boxGeom=rot_mode_geoms, boxPlacement='Center', frameColor=(255, 255, 255, 0)),

        ]

        for radbutton in radbuttons:
            radbutton.setOthers(radbuttons)

    def set_joints_list_ui(self):
        if not self.editor.scrolled_list_actor_joints_lbl_desc:
            ui_geoms = self.editor.ui_geom_collector()
            if ui_geoms:
                maps_scrolled_dbtn = self.editor.base.loader.loadModel(ui_geoms['btn_t_icon'])
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
                for index, joint in enumerate(self.editor.get_actor_joints(), 1):
                    btn = DirectButton(text="{0}".format(joint.get_name()),
                                       text_fg=(255, 255, 255, 1), relief=2,
                                       text_font=self.editor.font.load_font(self.editor.menu_font),
                                       frameColor=(0, 0, 0, 1),
                                       parent=self.editor.frame,
                                       scale=.03, borderWidth=(self.editor.w, self.editor.h),
                                       geom=geoms_scrolled_dbtn, geom_scale=(15.3, 0, 2),
                                       clickSound="",
                                       command=self.editor.select_joint_from_list,
                                       extraArgs=[joint.get_name()])
                    btn2_list.append(btn)

                if not self.editor.scrolled_list_actor_joints_lbl_desc:
                    self.editor.scrolled_list_actor_joints = DirectScrolledList(
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

                        frameSize=self.editor.frame_scrolled_size,
                        frameColor=(0, 0, 0, 0),
                        numItemsVisible=1,
                        forceHeight=0.11,
                        items=btn2_list,
                        itemFrame_frameSize=self.editor.frame_scrolled_inner_size,
                        itemFrame_pos=(0.35, 0, 0.4),
                        parent=self.editor.frame,
                    )

                if not self.editor.scrolled_list_actor_joints_lbl_desc:
                    self.editor.scrolled_list_actor_joints_lbl_desc = DirectLabel(
                        text="Select joint \nfor manipulations on the scene",
                        text_fg=(255, 255, 255, 0.9),
                        text_font=self.editor.font.load_font(self.editor.menu_font),
                        frameColor=(255, 255, 255, 0),
                        scale=.025, borderWidth=(self.editor.w, self.editor.h),
                        parent=self.editor.frame)

                if self.editor.scrolled_list_actor_joints_lbl:
                    self.editor.scrolled_list_actor_joints_lbl.set_pos(-1.65, 0, -0.60)
                if self.editor.scrolled_list_actor_joints:
                    self.editor.scrolled_list_actor_joints.set_pos(-2.0, 0, -1.12)
                if self.editor.scrolled_list_actor_joints_lbl_desc:
                    self.editor.scrolled_list_actor_joints_lbl_desc.set_pos(-1.65, 0, -0.87)
