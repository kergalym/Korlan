from direct.gui.DirectButton import DirectButton
from direct.gui.DirectLabel import DirectLabel
from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.OnscreenText import OnscreenText
from direct.interval.FunctionInterval import Func
from direct.interval.LerpInterval import LerpPosInterval
from direct.interval.MetaInterval import Sequence
from direct.task.TaskManagerGlobal import taskMgr
from panda3d.core import TransparencyAttrib, TextNode, FontPool, Point3, Vec3
from direct.gui.DirectGui import DirectWaitBar
from direct.gui.DirectGui import DirectFrame
from Engine.Renderer.rpcore import PointLight as RP_PointLight


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

        close_btn_maps = base.loader.load_model(ui_geoms['btn_t_close_icon'])
        close_btn_geoms = (close_btn_maps.find('**/button_close_ready'),
                           close_btn_maps.find('**/button_close_clicked'),
                           close_btn_maps.find('**/button_close_rollover'))

        select_btn_maps = base.loader.load_model(ui_geoms['btn_t_select_icon'])
        select_btn_geoms = (select_btn_maps.find('**/button_select_ready'),
                            select_btn_maps.find('**/button_select_clicked'),
                            select_btn_maps.find('**/button_select_rollover'))

        sounds = self.base.sounds_collector()
        self.sound_gui_click = self.base.loader.load_sfx(sounds.get('zapsplat_button_click'))

        self.btn_close = DirectButton(text="",
                                      text_fg=(255, 255, 255, 0.9),
                                      text_font=self.font.load_font(self.menu_font),
                                      frameColor=(0, 0, 0, 0),
                                      scale=self.btn_scale, borderWidth=(0, 0),
                                      geom=close_btn_geoms, geom_scale=(0.13, 0, 0.16),
                                      clickSound=self.sound_gui_click,
                                      command=self.clear_item_menu,
                                      pos=(-1.8, 0, 0.9),
                                      parent=self.item_menu_ui)

        self.btn_select = DirectButton(text="",
                                       text_fg=(255, 255, 255, 0.9),
                                       text_font=self.font.load_font(self.menu_font),
                                       frameColor=(0, 0, 0, 0),
                                       scale=0.05, borderWidth=(0, 0),
                                       geom=select_btn_geoms, geom_scale=(0.13, 0, 0.16),
                                       clickSound=self.sound_gui_click,
                                       command=self._select_item,
                                       pos=(0, 0, -0.7),
                                       parent=self.item_menu_ui)

        # quest selector geoms
        q_maps_scrolled_dec = base.loader.load_model(ui_geoms['btn_t_icon_dec'])

        q_maps_scrolled_inc = base.loader.load_model(ui_geoms['btn_t_icon_inc'])
        q_maps_scrolled_dec.set_transparency(TransparencyAttrib.MAlpha)
        q_maps_scrolled_inc.set_transparency(TransparencyAttrib.MAlpha)

        # inventory & journal geoms
        iui_maps_scrolled_dec = base.loader.load_model(ui_geoms['btn_inv_icon_dec'])
        iui_geoms_scrolled_dec = (iui_maps_scrolled_dec.find('**/button_any_dec'),
                                  iui_maps_scrolled_dec.find('**/button_pressed_dec'),
                                  iui_maps_scrolled_dec.find('**/button_rollover_dec'),
                                  iui_maps_scrolled_dec.find('**/button_disabled_dec'))

        iui_maps_scrolled_inc = base.loader.load_model(ui_geoms['btn_inv_icon_inc'])
        iui_geoms_scrolled_inc = (iui_maps_scrolled_inc.find('**/button_any_inc'),
                                  iui_maps_scrolled_inc.find('**/button_pressed_inc'),
                                  iui_maps_scrolled_inc.find('**/button_rollover_inc'),
                                  iui_maps_scrolled_inc.find('**/button_disabled_inc'))
        iui_maps_scrolled_inc.set_transparency(TransparencyAttrib.MAlpha)
        iui_maps_scrolled_dec.set_transparency(TransparencyAttrib.MAlpha)

        self.btn_select_dec = DirectButton(text="<|",
                                           text_fg=(0.7, 0.7, 0.7, 1),
                                           text_font=self.font.load_font(self.menu_font),
                                           frameColor=(0, 0, 0, 0),
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
                                           frameColor=(0, 0, 0, 0),
                                           scale=.03, borderWidth=(0, 0),
                                           geom=iui_geoms_scrolled_inc, geom_scale=(15.3, 0, 2),
                                           hpr=(0, 0, -90),
                                           clickSound=self.sound_gui_click,
                                           command=self._increment_carousel_item,
                                           pos=(1.2, 0, -0.5),
                                           parent=self.item_menu_ui)

        self.close_y = -0.0
        self.def_y = self.base.game_instance["mouse_y_cam"]
        self.def_y_indoor = -2.0

        self.active_item_materials = {}
        self.active_item_textures = {}

        self.current_indices_offset = 0
        self.active_item = None
        self.usable_item_list_count = 0
        self.usable_item_list_indices = 0
        self.anims = None
        self.current_action = None
        self.current_light = None
        self.light_energy = 30
        self.light_color = (0.030531512498855596, 0.004492279797792435, 0.000447507366538048)

    def _interpolate_to(self, target, start):
        LerpPosInterval(self.base.camera,
                        duration=1.0,
                        pos=Point3(target[0], target[1], target[2]),
                        startPos=Point3(start[0], start[1], start[2])).start()

    def _camera_zoom_in(self):
        if not self.base.game_instance["item_menu_mode"]:
            if self.base.game_instance["is_indoor"]:
                self._interpolate_to(target=(-0.1, self.close_y, -0.7), start=(0, self.def_y_indoor, 0))
            elif not self.base.game_instance["is_indoor"]:
                self._interpolate_to(target=(-0.1, self.close_y, -0.7), start=(0, self.def_y, 0))

            pivot = render.find("**/pivot")
            if pivot:
                pivot.set_pos(-0.1, 0.3, 1.1)
                pivot.set_hpr(180, -41.4, 0)

    def _camera_zoom_out(self):
        if self.base.game_instance["item_menu_mode"]:
            if self.base.game_instance["is_indoor"]:
                self._interpolate_to(target=(0, self.def_y_indoor, 0), start=(-0.1, self.close_y, -0.7))
            elif not self.base.game_instance["is_indoor"]:
                self._interpolate_to(target=(0, self.def_y, 0), start=(-0.1, self.close_y, -0.7))

            pivot = render.find("**/pivot")
            if pivot:
                pivot.set_pos(0, 0, 0.5)
                pivot.set_hpr(0, 0, 0)

    def _set_item_lighting(self, item_np, pos, player):
        if item_np and pos and player:
            world_pos = render.get_relative_point(item_np.get_parent(), pos)
            self.current_light = RP_PointLight()
            self.current_light.pos = (world_pos[0], world_pos[1], 0.6)
            self.current_light.color = self.light_color
            self.current_light.energy = self.light_energy
            self.current_light.ies_profile = self.base.game_instance["renderpipeline_np"].load_ies_profile("pear.ies")
            self.current_light.casts_shadows = True
            self.current_light.shadow_map_resolution = 512
            self.current_light.near_plane = 0.2
            self.current_light.radius = 0.38
            self.base.game_instance["renderpipeline_np"].add_light(self.current_light)

    def _decrement_carousel_item(self):
        player = self.base.game_instance["player_ref"]

        # Step backward to the next item
        if (self.current_indices_offset > 0
                and not self.current_indices_offset > self.usable_item_list_indices):
            self.current_indices_offset -= 1

            # Enable highlighting for the back next item
            items = player.get_python_tag("usable_item_list")["name"]
            name = items[self.current_indices_offset]

            nodepath = render.find("**/{0}".format(name))
            if nodepath:
                pos = nodepath.get_pos()
                world_pos = render.get_relative_point(nodepath.get_parent(), pos)
                self.current_light.pos = (world_pos[0], world_pos[1], 0.6)
                self.active_item = nodepath

        # self.btn_select_dec["state"] = DGG.DISABLED

    def _increment_carousel_item(self):
        player = self.base.game_instance["player_ref"]

        # Step forward to the next item
        if self.current_indices_offset < self.usable_item_list_indices:
            self.current_indices_offset += 1

            # Enable highlighting for the next item
            items = player.get_python_tag("usable_item_list")["name"]
            name = items[self.current_indices_offset]

            nodepath = render.find("**/{0}".format(name))
            if nodepath:
                pos = nodepath.get_pos()
                world_pos = render.get_relative_point(nodepath.get_parent(), pos)
                self.current_light.pos = (world_pos[0], world_pos[1], 0.6)
                self.active_item = nodepath

        # self.btn_select_inc["state"] = DGG.DISABLED

    def _select_item(self):
        player = self.base.game_instance["player_ref"]
        if not player.get_python_tag("used_item_np"):
            player.set_python_tag("used_item_np", self.active_item)

    def set_item_menu(self, anims, action):
        # Keep anims list and action
        self.anims = anims
        self.current_action = action

        # Zoom in the camera and show item menu
        self._camera_zoom_in()
        self.base.game_instance["item_menu_mode"] = True
        self.base.win_props.set_cursor_hidden(False)
        self.base.win.request_properties(self.base.win_props)

        # Hide player we want to see item which we can choose
        player = self.base.game_instance["player_ref"]
        player.hide()

        # Update usable items current count
        self.usable_item_list_count = len(player.get_python_tag("usable_item_list")["name"])
        self.current_indices_offset = self.usable_item_list_count - 1
        self.usable_item_list_indices = self.usable_item_list_count - 1

        # Highlight the last item
        name = player.get_python_tag("usable_item_list")["name"][self.usable_item_list_indices]
        item_np = render.find("**/{0}".format(name))
        self._set_item_lighting(item_np, item_np.get_pos(), player)

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

        # Turn light off
        if self.current_light:
            self.base.game_instance["renderpipeline_np"].remove_light(self.current_light)

        if player.get_python_tag("used_item_np"):
            player.set_python_tag("is_item_ready", True)
        elif not player.get_python_tag("used_item_np"):
            player.set_python_tag("is_item_ready", False)

        # Pickup or drop the item from this menu
        if player.get_python_tag("is_item_ready"):
            if self.anims and self.current_action:
                player_actions_cls = self.base.game_instance["player_actions_cls"]
                player_state_cls = self.base.game_instance['player_state_cls']

                if (not player.get_python_tag("is_item_using")
                        and player.get_python_tag("is_close_to_use_item")):
                    taskMgr.add(player_actions_cls.seq_pick_item_wrapper_task,
                                "seq_pick_item_wrapper_task",
                                extraArgs=[player, self.anims,
                                           self.current_action,
                                           "Korlan:RightHand"],
                                appendTask=True),
                    any_action_seq = player.actor_interval(self.anims[self.current_action],
                                                           playRate=self.base.actor_play_rate)
                    Sequence(Func(player_state_cls.set_action_state, "is_using", True),
                             any_action_seq,
                             Func(taskMgr.remove, "seq_pick_item_wrapper_task"),
                             Func(player_state_cls.set_action_state, "is_using", False),
                             Func(player_state_cls.set_do_once_key, "use", False),
                             ).start()

                elif (player.get_python_tag("is_item_using")
                      and player.get_python_tag("is_close_to_use_iem")):
                    taskMgr.add(player_actions_cls.seq_drop_item_wrapper_task,
                                "seq_drop_item_wrapper_task",
                                extraArgs=[player, self.anims, self.current_action],
                                appendTask=True),
                    any_action_seq = player.actor_interval(self.anims[self.current_action],
                                                           playRate=self.base.actor_play_rate)
                    Sequence(Func(player_state_cls.set_action_state, "is_using", True),
                             any_action_seq,
                             Func(taskMgr.remove, "seq_drop_item_wrapper"),
                             Func(player_state_cls.set_action_state, "is_using", False),
                             Func(player_state_cls.set_do_once_key, "use", False),
                             ).start()

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
