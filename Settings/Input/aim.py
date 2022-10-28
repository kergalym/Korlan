class Aim:

    def __init__(self):
        self.base = base
        self.base.game_instance["is_arrow_ready"] = False
        self.base.game_instance['is_aiming'] = False

    def on_aim_activate(self):
        if self.base.game_instance['cursor_ui']:
            if self.base.game_instance['cursor_ui'].is_hidden():
                self.base.game_instance['cursor_ui'].show()

        if not self.base.game_instance['is_aiming']:
            self.base.game_instance['is_aiming'] = True

        pos_y = 0
        pos_z = 0
        if (self.base.game_instance['player_ref'].get_python_tag("is_on_horse")
                and self.base.game_instance['is_aiming']
                and not self.base.game_instance['free_camera']):
            pos_y = -3.7
            pos_z = 0.29
        elif (not self.base.game_instance['player_ref'].get_python_tag("is_on_horse")
                and self.base.game_instance['is_aiming']
                and not self.base.game_instance['free_camera']):
            pos_y = self.base.game_instance["mouse_y_cam"]
            pos_z = -0.2
        self.base.camera.set_x(0.5)

        if not self.base.game_instance["is_arrow_ready"]:
            self.base.camera.set_y(pos_y)

        self.base.camera.set_z(pos_z)

    def on_aim_activate_charge(self):
        if self.base.game_instance['cursor_ui']:
            if self.base.game_instance['cursor_ui'].is_hidden():
                self.base.game_instance['cursor_ui'].show()

        if not self.base.game_instance['is_aiming']:
            self.base.game_instance['is_aiming'] = True

        if (self.base.game_instance['player_ref'].get_python_tag("is_on_horse")
                and self.base.game_instance['is_aiming']
                and not self.base.game_instance['free_camera']):
            pos_y = -3.7
            pos_z = 0.29
        else:
            pos_y = -2
            pos_z = -0.2

        self.base.camera.set_x(0.5)

        if not self.base.game_instance["is_arrow_ready"]:
            self.base.camera.set_y(pos_y)

        self.base.camera.set_z(pos_z)

    def on_aim_deactivate(self):
        if self.base.game_instance['cursor_ui']:
            if not self.base.game_instance['cursor_ui'].is_hidden():
                self.base.game_instance['cursor_ui'].hide()

        self.base.camera.set_x(0)

        if self.base.game_instance['player_ref'].get_python_tag("is_on_horse"):
            self.base.camera.set_z(0.5)
        elif not self.base.game_instance['player_ref'].get_python_tag("is_on_horse"):
            self.base.camera.set_y(self.base.game_instance["mouse_y_cam"])
            self.base.camera.set_z(0)
        if self.base.game_instance['is_aiming']:
            self.base.game_instance['is_aiming'] = False
            self.base.game_instance["is_arrow_ready"] = False

    def aim_state_task(self, task):
        if self.base.game_instance['menu_mode']:
            return task.done

        if (self.base.player_states['has_bow']
                and not self.base.game_instance["is_indoor"]
                and not self.base.game_instance['ui_mode']):
            if (self.base.game_instance['kbd_np'].keymap["block"]
                    and self.base.game_instance['kbd_np'].keymap["attack"]):
                # Start aiming and charging arrow
                self.on_aim_activate_charge()

            elif (self.base.game_instance['kbd_np'].keymap["block"]
                  and self.base.game_instance['arrow_count'] > 1
                  and not self.base.game_instance['kbd_np'].keymap["attack"]):
                # Just start aiming
                self.on_aim_activate()

            elif (not self.base.game_instance['kbd_np'].keymap["block"]
                  and not self.base.game_instance['kbd_np'].keymap["attack"]):
                # Stop aiming
                self.on_aim_deactivate()

        return task.cont
