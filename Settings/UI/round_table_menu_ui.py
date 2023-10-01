from direct.gui.DirectButton import DirectButton
from direct.gui.OnscreenText import OnscreenText
from direct.interval.FunctionInterval import Func
from direct.interval.LerpInterval import LerpPosInterval
from direct.interval.MetaInterval import Sequence
from direct.task.TaskManagerGlobal import taskMgr
from panda3d.core import TransparencyAttrib, TextNode, FontPool, Point3, Vec3
from direct.gui.DirectGui import DirectFrame
from Engine.Renderer.rpcore import PointLight as RP_PointLight
from direct.gui.DirectGui import DGG


class RoundTableMenu:
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
        self.item_menu_ui = None
        self.btn_select_item = None
        self.btn_return_item = None
        self.btn_deselect_item = None
        self.btn_close = None
        self.btn_select_inc = None
        self.btn_select_dec = None

        self.menu_font = self.fonts['OpenSans-Regular']
        self.menu_font_color = (0.8, 0.4, 0, 1)

        # instance of the abstract class
        self.font = FontPool
        self.text = TextNode("TextNode")

        sounds = self.base.sounds_collector()
        self.sound_gui_click = self.base.loader.load_sfx(sounds.get('zapsplat_button_click'))

        self.close_y = -0.0
        self.def_y = self.base.game_instance["mouse_y_cam"]
        self.def_y_indoor = -2.0

        self.active_item_materials = {}
        self.active_item_textures = {}

        self.current_indices_offset = 0
        self.active_item = None
        self.active_item_text = None
        self.active_item_text_scale = 0.08
        self.active_item_text_pos = (0, -0.55)
        self.active_item_text_color = (255, 255, 255, 0.9)
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
            self.current_light.radius = 0.41
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

                # Change item name
                if self.active_item_text:
                    self.active_item_text.setText("")
                    name = self._construct_item_name(name)
                    self.active_item_text.setText(name)

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

                # Change item name
                if self.active_item_text:
                    self.active_item_text.setText("")
                    name = self._construct_item_name(name)
                    self.active_item_text.setText(name)

    def _select_item(self):
        if self.active_item:
            player = self.base.game_instance["player_ref"]

            # Discard the item which is not a part of round table (player was close to item outdoor)
            item_np = player.get_python_tag("used_item_np")
            if item_np:
                if item_np.get_name() != self.active_item.get_name():
                    player.set_python_tag("used_item_np", None)

            # Construct item properties and make item ready to pickup if it not was taken yet
            if not player.get_python_tag("used_item_np"):
                player.set_python_tag("used_item_np", self.active_item)

                self.base.game_instance['item_state'] = {
                    'type': 'item',
                    'name': '{0}'.format(self.active_item.get_name()),
                    'weight': '{0}'.format(1),
                    'in-use': False,
                }
                player.set_python_tag("is_item_ready", True)
                item_prop = self.base.game_instance['item_state']
                player.set_python_tag("current_item_prop", item_prop)

                if self.base.game_instance['hud_np']:
                    self.base.game_instance['hud_np'].toggle_weapon_state(weapon_name="busy_hands")

    def _deselect_item(self):
        if self.active_item:
            player = self.base.game_instance["player_ref"]
            player.set_python_tag("is_item_using", False)
            player.set_python_tag("used_item_np", None)
            player.set_python_tag("is_item_ready", False)
            self.base.game_instance['item_state'].clear()

            # Set hands icon to free back
            if self.base.game_instance['hud_np']:
                self.base.game_instance['hud_np'].toggle_weapon_state(weapon_name="hands")

    def _return_item(self):
        player = self.base.game_instance["player_ref"]

        # Discard the item which is not a part of round table (player was close to item outdoor)
        item_np = player.get_python_tag("used_item_np")
        if item_np:
            name = item_np.get_name()

            player.get_python_tag("usable_item_list")["name"].append(name)
            # Update usable items current count
            self.usable_item_list_count = len(player.get_python_tag("usable_item_list")["name"])
            self.current_indices_offset = self.usable_item_list_count - 1
            self.usable_item_list_indices = self.usable_item_list_count - 1

            self.btn_return_item.destroy()

            # Return item back to round table
            if self.base.game_instance["round_table_np"]:

                if hasattr(item_np.node(), "set_kinematic"):
                    item_np.node().set_kinematic(False)

                player.set_python_tag("is_item_using", False)
                player.set_python_tag("used_item_np", None)
                player.set_python_tag("is_item_ready", False)
                self.base.game_instance['item_state'].clear()

                round_table = self.base.game_instance["round_table_np"]
                item_np.reparent_to(round_table)

                # Set item position and rotation
                for name, pos, hpr in zip(player.get_python_tag("usable_item_list")["name"],
                                          player.get_python_tag("usable_item_list")["pos"],
                                          player.get_python_tag("usable_item_list")["hpr"]):
                    if name in item_np.get_name():
                        item_np.set_hpr(hpr)
                        item_np.set_pos(pos)
                        item_np.set_scale(1)

                # Set hands icon to free back
                if self.base.game_instance['hud_np']:
                    self.base.game_instance['hud_np'].toggle_weapon_state(weapon_name="hands")

                # Show select item button instead of return item button
                ui_geoms = base.ui_geom_collector()

                select_btn_maps = base.loader.load_model(ui_geoms['btn_t_select_icon'])
                select_btn_geoms = (select_btn_maps.find('**/button_select_ready'),
                                    select_btn_maps.find('**/button_select_clicked'),
                                    select_btn_maps.find('**/button_select_rollover'))

                deselect_btn_maps = base.loader.load_model(ui_geoms['btn_t_deselect_icon'])
                deselect_btn_geoms = (deselect_btn_maps.find('**/button_deselect_ready'),
                                      deselect_btn_maps.find('**/button_deselect_clicked'),
                                      deselect_btn_maps.find('**/button_deselect_rollover'))

                self.btn_select_item = DirectButton(text="",
                                                    text_fg=self.menu_font_color,
                                                    text_font=self.font.load_font(self.menu_font),
                                                    frameColor=(0, 0, 0, 0),
                                                    scale=0.05, borderWidth=(0, 0),
                                                    geom=select_btn_geoms, geom_scale=(0.13, 0, 0.16),
                                                    clickSound=self.sound_gui_click,
                                                    command=self._select_item,
                                                    pos=(-0.3, 0, -0.7),
                                                    parent=self.item_menu_ui)
                self.btn_deselect_item = DirectButton(text="",
                                                      text_fg=self.menu_font_color,
                                                      text_font=self.font.load_font(self.menu_font),
                                                      frameColor=(0, 0, 0, 0),
                                                      scale=0.05, borderWidth=(0, 0),
                                                      geom=deselect_btn_geoms, geom_scale=(0.13, 0, 0.16),
                                                      clickSound=self.sound_gui_click,
                                                      command=self._deselect_item,
                                                      pos=(0.3, 0, -0.7),
                                                      parent=self.item_menu_ui)
                self.btn_select_dec["state"] = DGG.NORMAL
                self.btn_select_inc["state"] = DGG.NORMAL

    def _construct_item_name(self, name):
        if name:
            name = name.capitalize()
            if "." in name:
                name = name.replace(".", " ")
            if "000" in name:
                name = name.replace(" 000", "")
            if "00" in name:
                name = name.replace(" 00", " ")
            if "0" in name:
                name = name.replace(" 0", " ")

            return name

    def set_item_menu(self, anims, action):
        # Menu attributes
        self.item_menu_ui = DirectFrame(frameColor=(0, 0, 0, 0.0),
                                        frameSize=self.item_menu_ui_frame_size,
                                        pos=(0, 0, 0))

        ui_geoms = base.ui_geom_collector()

        close_btn_maps = base.loader.load_model(ui_geoms['btn_t_close_icon'])
        close_btn_geoms = (close_btn_maps.find('**/button_close_ready'),
                           close_btn_maps.find('**/button_close_clicked'),
                           close_btn_maps.find('**/button_close_rollover'))

        select_btn_maps = base.loader.load_model(ui_geoms['btn_t_select_icon'])
        select_btn_geoms = (select_btn_maps.find('**/button_select_ready'),
                            select_btn_maps.find('**/button_select_clicked'),
                            select_btn_maps.find('**/button_select_rollover'))

        deselect_btn_maps = base.loader.load_model(ui_geoms['btn_t_deselect_icon'])
        deselect_btn_geoms = (deselect_btn_maps.find('**/button_deselect_ready'),
                              deselect_btn_maps.find('**/button_deselect_clicked'),
                              deselect_btn_maps.find('**/button_deselect_rollover'))

        return_btn_maps = base.loader.load_model(ui_geoms['btn_t_return_icon'])
        return_btn_geoms = (return_btn_maps.find('**/button_return_ready'),
                            return_btn_maps.find('**/button_return_clicked'),
                            return_btn_maps.find('**/button_return_rollover'))

        self.btn_close = DirectButton(text="",
                                      text_fg=self.menu_font_color,
                                      text_font=self.font.load_font(self.menu_font),
                                      frameColor=(0, 0, 0, 0),
                                      scale=self.btn_scale, borderWidth=(0, 0),
                                      geom=close_btn_geoms, geom_scale=(0.13, 0, 0.16),
                                      clickSound=self.sound_gui_click,
                                      command=self.clear_item_menu,
                                      pos=(-1.8, 0, 0.9),
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

        player = self.base.game_instance["player_ref"]
        if not player.get_python_tag("used_item_np"):
            self.btn_select_item = DirectButton(text="",
                                                text_fg=self.menu_font_color,
                                                text_font=self.font.load_font(self.menu_font),
                                                frameColor=(0, 0, 0, 0),
                                                scale=0.05, borderWidth=(0, 0),
                                                geom=select_btn_geoms, geom_scale=(0.13, 0, 0.16),
                                                clickSound=self.sound_gui_click,
                                                command=self._select_item,
                                                pos=(-0.3, 0, -0.7),
                                                parent=self.item_menu_ui)
            self.btn_deselect_item = DirectButton(text="",
                                                  text_fg=self.menu_font_color,
                                                  text_font=self.font.load_font(self.menu_font),
                                                  frameColor=(0, 0, 0, 0),
                                                  scale=0.05, borderWidth=(0, 0),
                                                  geom=deselect_btn_geoms, geom_scale=(0.13, 0, 0.16),
                                                  clickSound=self.sound_gui_click,
                                                  command=self._deselect_item,
                                                  pos=(0.3, 0, -0.7),
                                                  parent=self.item_menu_ui)
            self.btn_select_dec["state"] = DGG.NORMAL
            self.btn_select_inc["state"] = DGG.NORMAL
        else:
            self.btn_return_item = DirectButton(text="",
                                                text_fg=self.menu_font_color,
                                                text_font=self.font.load_font(self.menu_font),
                                                frameColor=(0, 0, 0, 0),
                                                scale=0.05, borderWidth=(0, 0),
                                                geom=return_btn_geoms, geom_scale=(0.13, 0, 0.16),
                                                clickSound=self.sound_gui_click,
                                                command=self._return_item,
                                                pos=(0, 0, -0.7),
                                                parent=self.item_menu_ui)
            self.btn_select_dec["state"] = DGG.DISABLED
            self.btn_select_inc["state"] = DGG.DISABLED

        # Keep anims list and action
        self.anims = anims
        self.current_action = action

        # Zoom in the camera and show item menu
        self._camera_zoom_in()
        self.base.game_instance["item_menu_mode"] = True
        # self.base.win_props.set_cursor_hidden(False)
        # self.base.win.request_properties(self.base.win_props)
        base.cursor.show()

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
        self.active_item = item_np
        self._set_item_lighting(item_np, item_np.get_pos(), player)

        # Set text
        if not self.active_item_text:
            name = self._construct_item_name(name)
            self.active_item_text = OnscreenText(text="{0}".format(name),
                                                 pos=self.active_item_text_pos,
                                                 scale=self.active_item_text_scale,
                                                 fg=self.menu_font_color,
                                                 font=self.font.load_font(self.menu_font),
                                                 align=TextNode.A_center,
                                                 mayChange=True)

        # Set player close to round table with predefined position
        if self.base.game_instance["round_table_np"]:
            round_table = self.base.game_instance["round_table_np"]
            world_pos = render.get_relative_point(round_table.get_parent(), round_table.get_pos())
            margin_x = world_pos[0] - 0.6
            margin_y = world_pos[1] - 0.6
            self.base.game_instance["player_np"].set_x(margin_x)
            self.base.game_instance["player_np"].set_y(margin_y)
            self.base.game_instance["player_np"].look_at(round_table.get_pos())
            self.base.game_instance["player_np"].set_h(138)

    def clear_item_menu(self):
        # Zoom out the camera and hide item menu
        if self.item_menu_ui:
            self.item_menu_ui.hide()
            self.item_menu_ui.destroy()

            self.item_menu_ui = None
            self.btn_select_item = None
            self.btn_deselect_item = None
            self.btn_return_item = None
            self.btn_close = None
            self.btn_select_inc = None
            self.btn_select_dec = None

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

        # Remove text
        if self.active_item_text:
            self.active_item_text.setText("")
            self.active_item_text.destroy()

        if not player.get_python_tag("is_item_ready"):
            player_state_cls = self.base.game_instance['player_state_cls']
            player_state_cls.set_do_once_key("use", False)

        # Pickup or drop the item from this menu
        if player.get_python_tag("is_item_ready"):
            if self.anims and self.current_action:
                player_actions_cls = self.base.game_instance["player_actions_cls"]
                player_state_cls = self.base.game_instance['player_state_cls']

                if (not player.get_python_tag("is_item_using")
                        and player.get_python_tag("used_item_np")
                        and player.get_python_tag("is_close_to_use_item")):
                    base.player_states['is_idle'] = False

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
                             Func(player_actions_cls.remove_seq_pick_item_wrapper_task),
                             Func(player_state_cls.set_action_state, "is_using", False),
                             Func(player_state_cls.set_do_once_key, "use", False),
                             ).start()

