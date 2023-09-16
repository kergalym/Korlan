from direct.interval.FunctionInterval import Wait, Func
from direct.interval.MetaInterval import Sequence


class Aim:

    def __init__(self):
        self.base = base
        self.base.game_instance["is_arrow_ready"] = False
        self.base.game_instance['is_aiming'] = False
        self._crosshair_sequence = Sequence()

    def on_aim_activate(self):
        if self.base.game_settings['Main']['crosshair_visibility'] == 'on':
            if self.base.game_instance['crosshair_ui']:
                if self.base.game_instance['crosshair_ui'].is_hidden():
                    self.base.game_instance['crosshair_ui'].show()

        if not self.base.game_instance['is_aiming']:
            self.base.game_instance['is_aiming'] = True

        pos_z = 0
        if (self.base.game_instance['player_ref'].get_python_tag("is_on_horse")
                and self.base.game_instance['is_aiming']
                and not self.base.game_instance['free_camera']):
            pos_z = 1
        elif (not self.base.game_instance['player_ref'].get_python_tag("is_on_horse")
                and self.base.game_instance['is_aiming']
                and not self.base.game_instance['free_camera']):
            pos_z = -0.2

        self.base.camera.set_x(0.5)

        self.base.camera.set_z(pos_z)

    def on_aim_activate_charge(self):
        if self.base.game_settings['Main']['crosshair_visibility'] == 'on':
            if self.base.game_instance['crosshair_ui']:
                if self.base.game_instance['crosshair_ui'].is_hidden():
                    self.base.game_instance['crosshair_ui'].show()

        if not self.base.game_instance['is_aiming']:
            self.base.game_instance['is_aiming'] = True

        if (self.base.game_instance['player_ref'].get_python_tag("is_on_horse")
                and self.base.game_instance['is_aiming']
                and not self.base.game_instance['free_camera']):
            pos_z = 1
        else:
            pos_z = -0.2

        self.base.camera.set_x(0.5)

        self.base.camera.set_z(pos_z)

    def on_aim_deactivate(self):
        if self.base.game_settings['Main']['crosshair_visibility'] == 'on':
            if self.base.game_instance['crosshair_ui']:
                if not self.base.game_instance['crosshair_ui'].is_hidden():
                    self.base.game_instance['crosshair_ui'].hide()

        if self.base.game_instance['is_aiming']:

            self.base.camera.set_x(0)
            if self.base.game_instance['player_ref'].get_python_tag("is_on_horse"):
                self.base.camera.set_z(0.5)
            elif not self.base.game_instance['player_ref'].get_python_tag("is_on_horse"):
                self.base.camera.set_z(0)

            self.base.game_instance['is_aiming'] = False
            self.base.game_instance["is_arrow_ready"] = False

    def downscale_crosshair(self):
        if self._crosshair_sequence is not None and not self.base.game_instance['crosshair_ui'].is_empty():
            if (self.base.game_instance['crosshair_ui'].get_scale().x > 0.01
                    and not self._crosshair_sequence.is_playing()):
                self._crosshair_sequence = Sequence()
                self._crosshair_sequence.append(Wait(0.1))
                self._crosshair_sequence.append(Func(self.base.game_instance['crosshair_ui'].set_scale, 0.03))
                self._crosshair_sequence.append(Wait(0.1))
                self._crosshair_sequence.append(Func(self.base.game_instance['crosshair_ui'].set_scale, 0.02))
                self._crosshair_sequence.append(Wait(0.1))
                self._crosshair_sequence.append(Func(self.base.game_instance['crosshair_ui'].set_scale, 0.01))
                self._crosshair_sequence.append(Wait(0.1))
                self._crosshair_sequence.start()

    def upscale_crosshair(self):
        if self._crosshair_sequence is not None and not self.base.game_instance['crosshair_ui'].is_empty():
            if (self.base.game_instance['crosshair_ui'].get_scale().x < 0.04
                    and not self._crosshair_sequence.is_playing()):
                self._crosshair_sequence = Sequence()
                self._crosshair_sequence.append(Wait(0.1))
                self._crosshair_sequence.append(Func(self.base.game_instance['crosshair_ui'].set_scale, 0.02))
                self._crosshair_sequence.append(Wait(0.1))
                self._crosshair_sequence.append(Func(self.base.game_instance['crosshair_ui'].set_scale, 0.03))
                self._crosshair_sequence.append(Wait(0.1))
                self._crosshair_sequence.append(Func(self.base.game_instance['crosshair_ui'].set_scale, 0.04))
                self._crosshair_sequence.append(Wait(0.1))
                self._crosshair_sequence.start()

    def aim_state_task(self, task):
        if self.base.game_instance['menu_mode']:
            return task.done

        if (self.base.player_states['has_bow']
                and base.player_states["is_alive"]
                and not self.base.game_instance["is_indoor"]
                and not self.base.game_instance['ui_mode']):
            if (self.base.game_instance['kbd_np'].keymap["block"]
                    and self.base.game_instance['kbd_np'].keymap["attack"]):
                # Start aiming and charging arrow
                self.on_aim_activate_charge()
                self.downscale_crosshair()

            elif (self.base.game_instance['kbd_np'].keymap["block"]
                  and self.base.game_instance['arrow_count'] > 1
                  and not self.base.game_instance['kbd_np'].keymap["attack"]):
                # Start aiming
                self.on_aim_activate()

            elif (not self.base.game_instance['kbd_np'].keymap["block"]
                  and not self.base.game_instance['kbd_np'].keymap["attack"]):
                # Stop aiming
                self.on_aim_deactivate()
                self.upscale_crosshair()

        return task.cont

