from direct.gui.DirectButton import DirectButton
from direct.gui.DirectLabel import DirectLabel
from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.OnscreenText import OnscreenText
from direct.interval.LerpInterval import LerpPosInterval
from panda3d.core import TransparencyAttrib, TextNode, FontPool, Point3, Vec3
from direct.gui.DirectGui import DirectWaitBar
from direct.gui.DirectGui import DirectFrame


class ItemMenu:
    def __init__(self):
        self.base = base
        self.game_dir = base.game_dir
        self.images = base.textures_collector(path="Settings/UI")
        self.fonts = base.fonts_collector()

        """ Frame Sizes """
        # Left, right, bottom, top
        self.item_menu_ui_frame_size = [-1.85, -1.55, -0.99, -0.88]

        """ Frame Colors """
        self.frm_opacity = 1

        """ Buttons, Label Scaling """
        self.lbl_scale = .03
        self.btn_scale = .03

        # Menu attributes
        self.item_menu_ui = DirectFrame(frameColor=(0, 0, 0, 0.0),
                                        frameSize=self.item_menu_ui_frame_size,
                                        pos=(0, 0, 0))
        self.item_menu_ui.hide()

        self.menu_font = self.fonts['OpenSans-Regular']
        # instance of the abstract class
        self.font = FontPool
        self.text = TextNode("TextNode")

        ui_geoms = base.ui_geom_collector()
        maps = base.loader.loadModel(ui_geoms['btn_t_close_icon'])
        geoms = (maps.find('**/button_close_ready'),
                 maps.find('**/button_close_clicked'),
                 maps.find('**/button_close_rollover'))
        sounds = self.base.sounds_collector()
        self.sound_gui_click = self.base.loader.load_sfx(sounds.get('zapsplat_button_click'))

        self.btn_close = DirectButton(text="",
                                      text_fg=(255, 255, 255, 0.9),
                                      text_font=self.font.load_font(self.menu_font),
                                      frameColor=(0, 0, 0, self.frm_opacity),
                                      scale=self.btn_scale, borderWidth=(0, 0),
                                      geom=geoms, geom_scale=(0.13, 0, 0.16),
                                      clickSound=self.sound_gui_click,
                                      command=self.clear_item_menu,
                                      pos=(-1.8, 0, 0.9),
                                      parent=self.item_menu_ui)

        self.btn_select = DirectButton(text="",
                                       text_fg=(255, 255, 255, 0.9),
                                       text_font=self.font.load_font(self.menu_font),
                                       frameColor=(0, 0, 0, self.frm_opacity),
                                       scale=self.btn_scale, borderWidth=(0, 0),
                                       geom=geoms, geom_scale=(0.13, 0, 0.16),
                                       clickSound=self.sound_gui_click,
                                       command=self._select_item,
                                       pos=(0, 0, -0.7),
                                       parent=self.item_menu_ui)

        # quest selector geoms
        q_maps_scrolled_dec = base.loader.loadModel(ui_geoms['btn_t_icon_dec'])

        q_maps_scrolled_inc = base.loader.loadModel(ui_geoms['btn_t_icon_inc'])
        q_maps_scrolled_dec.set_transparency(TransparencyAttrib.MAlpha)
        q_maps_scrolled_inc.set_transparency(TransparencyAttrib.MAlpha)

        # inventory & journal geoms
        iui_maps_scrolled_dec = base.loader.loadModel(ui_geoms['btn_inv_icon_dec'])
        iui_geoms_scrolled_dec = (iui_maps_scrolled_dec.find('**/button_any_dec'),
                                  iui_maps_scrolled_dec.find('**/button_pressed_dec'),
                                  iui_maps_scrolled_dec.find('**/button_rollover_dec'),
                                  iui_maps_scrolled_dec.find('**/button_disabled_dec'))

        iui_maps_scrolled_inc = base.loader.loadModel(ui_geoms['btn_inv_icon_inc'])
        iui_geoms_scrolled_inc = (iui_maps_scrolled_inc.find('**/button_any_inc'),
                                  iui_maps_scrolled_inc.find('**/button_pressed_inc'),
                                  iui_maps_scrolled_inc.find('**/button_rollover_inc'),
                                  iui_maps_scrolled_inc.find('**/button_disabled_inc'))
        iui_maps_scrolled_inc.set_transparency(TransparencyAttrib.MAlpha)
        iui_maps_scrolled_dec.set_transparency(TransparencyAttrib.MAlpha)

        self.btn_select_dec = DirectButton(text="<|",
                                           text_fg=(0.7, 0.7, 0.7, 1),
                                           text_font=self.font.load_font(self.menu_font),
                                           frameColor=(0, 0, 0, 1),
                                           scale=.03, borderWidth=(0, 0),
                                           geom=iui_geoms_scrolled_dec, geom_scale=(15.3, 0, 2),
                                           hpr=(0, 0, -90),
                                           clickSound=self.sound_gui_click,
                                           command=self._decrement_carousel_item,
                                           pos=(-1.2, 0, -0.5),
                                           parent=self.item_menu_ui)
        self.btn_select_inc = DirectButton(text="|>",
                                           text_fg=(0.7, 0.7, 0.7, 1),
                                           text_font=self.font.load_font(self.menu_font),
                                           frameColor=(0, 0, 0, 1),
                                           scale=.03, borderWidth=(0, 0),
                                           geom=iui_geoms_scrolled_inc, geom_scale=(15.3, 0, 2),
                                           hpr=(0, 0, -90),
                                           clickSound=self.sound_gui_click,
                                           command=self._increment_carousel_item,
                                           pos=(1.2, 0, -0.5),
                                           parent=self.item_menu_ui)

        self.btn_select_inc.set_transparency(True)
        self.btn_select_dec.set_transparency(True)

        self.close_y = -0.0
        self.def_y = self.base.game_instance["mouse_y_cam"]
        self.def_y_indoor = self.close_y

        self.active_item_materials = {}
        self.active_item_textures = {}

        self.current_indices_offset = 0
        self.active_item = None
        self.usable_item_list_count = 0

    def _interpolate_to(self, target, start):
        LerpPosInterval(self.base.camera,
                        duration=1.0,
                        pos=Point3(target[0], target[1], target[2]),
                        startPos=Point3(start[0], start[1], start[2])).start()

    def _camera_zoom_in(self):
        if not self.base.game_instance["item_menu_mode"]:
            if self.base.game_instance["is_indoor"]:
                self._interpolate_to(target=(0, self.close_y, 0), start=(0, self.def_y_indoor, 0))

            self._interpolate_to(target=(0, self.close_y, 0), start=(0, self.def_y, 0))

    def _camera_zoom_out(self):
        if self.base.game_instance["item_menu_mode"]:
            if self.base.game_instance["is_indoor"]:
                self._interpolate_to(target=(0, self.def_y_indoor, 0), start=(0, self.close_y, 0))

            self._interpolate_to(target=(0, self.def_y, 0), start=(0, self.close_y, 0))

    def _decrement_carousel_item(self):
        player = self.base.game_instance["player_ref"]
        rp = self.base.game_instance["renderpipeline_np"]

        # Step backward to the next item
        if self.current_indices_offset > 0:
            self.current_indices_offset -= 1

        # Enable highlighting for the back next item
        items = player.get_python_tag("usable_item_list")["name"]
        name = items[self.current_indices_offset]
        nodepath = render.find("**/{0}".format(name))
        if nodepath:
            self._collect_item_materials(nodepath)
            self._collect_item_textures(nodepath)
            rp.set_effect(nodepath,
                          "{0}/Engine/Renderer/effects/enable_item_highlight.yaml".format(
                              self.game_dir),
                          {})
            self.active_item = nodepath

        # Disable highlighting for the previous item
        if (self.current_indices_offset + 1) < self.usable_item_list_count:
            name = items[self.current_indices_offset + 1]
            nodepath = render.find("**/{0}".format(name))
            if nodepath:
                rp.set_effect(nodepath,
                              "{0}/Engine/Renderer/effects/disable_item_highlight.yaml".format(
                                  self.game_dir),
                              {})

                if self.active_item_materials.get(name):
                    for mat in self.active_item_materials[name]:
                        # item_np.set_material(mat)
                        nodepath.set_shader_input('baseColor', Vec3(1, 1, 1))
                        nodepath.set_shader_input('specularIor', 0.5)

                if self.active_item_textures.get(name):
                    for tex in self.active_item_textures[name]:
                        nodepath.set_shader_input('itemTex', tex)
        # self.btn_select_dec["state"] = DGG.DISABLED

    def _increment_carousel_item(self):
        player = self.base.game_instance["player_ref"]
        rp = self.base.game_instance["renderpipeline_np"]

        # Step forward to the next item
        if self.current_indices_offset < self.usable_item_list_count:
            self.current_indices_offset += 1

        # Enable highlighting for the next item
        items = player.get_python_tag("usable_item_list")["name"]
        name = items[self.current_indices_offset]
        nodepath = render.find("**/{0}".format(name))
        if nodepath:
            self._collect_item_materials(nodepath)
            self._collect_item_textures(nodepath)
            rp.set_effect(nodepath,
                          "{0}/Engine/Renderer/effects/enable_item_highlight.yaml".format(
                              self.game_dir),
                          {})
            self.active_item = nodepath

        # Disable highlighting for the previous item
        if (self.current_indices_offset - 1) > 0:
            name = items[self.current_indices_offset - 1]
            nodepath = render.find("**/{0}".format(name))
            if nodepath:
                rp.set_effect(nodepath,
                              "{0}/Engine/Renderer/effects/disable_item_highlight.yaml".format(
                                  self.game_dir),
                              {})

                if self.active_item_materials.get(name):
                    for mat in self.active_item_materials[name]:
                        # item_np.set_material(mat)
                        nodepath.set_shader_input('baseColor', Vec3(1, 1, 1))
                        nodepath.set_shader_input('specularIor', 0.5)

                if self.active_item_textures.get(name):
                    for tex in self.active_item_textures[name]:
                        nodepath.set_shader_input('itemTex', tex)
        # self.btn_select_inc["state"] = DGG.DISABLED

    def _select_item(self):
        player = self.base.game_instance["player_ref"]
        player.set_python_tag("used_item_np", self.active_item)

    def set_item_menu(self):
        # Zoom in the camera and show item menu
        self._camera_zoom_in()
        self.base.game_instance["item_menu_mode"] = True
        self.base.win_props.set_cursor_hidden(False)
        self.base.win.request_properties(self.base.win_props)

        # Hide player we want to see item which we can choose
        player = self.base.game_instance["player_ref"]
        player.hide()

        # Update usable items current count
        self.usable_item_list_count = len(player.get_python_tag("usable_item_list")["name"]) - 1
        self.current_indices_offset = self.usable_item_list_count

    def clear_item_menu(self):
        # Zoom out the camera and hide item menu
        self.item_menu_ui.hide()
        self._camera_zoom_out()
        self.base.game_instance["item_menu_mode"] = False
        self.base.win_props.set_cursor_hidden(True)
        self.base.win.request_properties(self.base.win_props)

        # Show player since we done with choosing item
        player = self.base.game_instance["player_ref"]
        player.show()

        # Restore original material properties of the item. Stop highlighting
        item_np = player.get_python_tag("used_item_np")
        rp = self.base.game_instance["renderpipeline_np"]
        for name in player.get_python_tag("usable_item_list")["name"]:
            nodepath = render.find("**/{0}".format(name))
            if nodepath and item_np:
                if nodepath.get_name() == item_np.get_name():

                    rp.set_effect(nodepath,
                                  "{0}/Engine/Renderer/effects/disable_item_highlight.yaml".format(
                                      self.game_dir),
                                  {})

                    name = item_np.get_name()
                    if self.active_item_materials.get(name):
                        for mat in self.active_item_materials[name]:
                            # item_np.set_material(mat)
                            nodepath.set_shader_input('baseColor', Vec3(1, 1, 1))
                            nodepath.set_shader_input('specularIor', 0.5)

                    if self.active_item_textures.get(name):
                        for tex in self.active_item_textures[name]:
                            nodepath.set_shader_input('itemTex', tex)

        player.set_python_tag("is_item_ready", True)

    def _collect_item_materials(self, item_np):
        if item_np:
            materials = []

            for mat in item_np.find_all_materials():
                materials.append(mat)

            name = item_np.get_name()
            self.active_item_materials[name] = materials

            return self.active_item_materials

    def _collect_item_textures(self, item_np):
        if item_np:
            textures = []

            for tex in item_np.find_all_textures():
                textures.append(tex)

            name = item_np.get_name()
            self.active_item_textures[name] = textures

            return self.active_item_textures
