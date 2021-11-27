from direct.gui.OnscreenImage import OnscreenImage
from panda3d.core import TransparencyAttrib
from direct.gui.DirectGui import DirectWaitBar
from direct.gui.DirectGui import DirectFrame


class HUD:
    def __init__(self):
        self.game_dir = base.game_dir
        self.images = base.textures_collector(path="{0}/Settings/UI".format(self.game_dir))
        self.cursor_ui_pos = (0, 0, 0)
        self.cursor_ui_scale = 0.04
        self.day_hud_ui_pos = (0.0, 0, 0.90)
        self.day_hud_ui_scale = (0.5, 0, 0.1)
        self.weapon_state_ui_pos = (1.8, 0, -0.90)
        self.weapon_state_ui_scale = 0.07
        # Left, right, bottom, top
        self.player_bar_ui_frame_size = [-1.85, -1.55, -0.99, -0.88]
        self.player_bar_ui_scale = (0.14, 0, 0.10)
        # HUD attributes
        self.day_hud_ui = None
        self.weapon_state_ui = None
        self.player_bar_ui_frame = None
        self.player_bar_ui_health = None
        self.player_bar_ui_stamina = None
        self.player_bar_ui_courage = None
        self.cursor_ui = None

    def set_aim_cursor(self):
        base.cursor_ui = OnscreenImage(image=self.images['crosshair'])
        base.cursor_ui.set_pos(self.cursor_ui_pos)
        base.cursor_ui.setTransparency(TransparencyAttrib.MAlpha)
        base.cursor_ui.set_scale(self.cursor_ui_scale)
        base.cursor_ui.hide()

    def clear_aim_cursor(self):
        if base.cursor_ui:
            base.cursor_ui.destroy()
            base.cursor_ui.remove_node()

    def set_day_hud(self):
        base.day_hud_ui = OnscreenImage(image=self.images['day_hud_light_ui'])
        base.day_hud_ui.setTransparency(TransparencyAttrib.MAlpha)
        base.day_hud_ui.set_pos(self.day_hud_ui_pos)
        base.day_hud_ui.set_scale(self.day_hud_ui_scale)
        base.day_hud_ui.hide()

    def clear_day_hud(self):
        if base.day_hud_ui:
            base.day_hud_ui.destroy()
            base.day_hud_ui.remove_node()

    def toggle_day_hud(self, time):
        if (time and isinstance(time, str)
                and hasattr(base, "day_hud_ui")
                and base.day_hud_ui):
            if time == "light":
                base.day_hud_ui.show()
                base.day_hud_ui.setImage(self.images['day_hud_light_ui'])
                base.day_hud_ui.setTransparency(TransparencyAttrib.MAlpha)
            if time == "night":
                base.day_hud_ui.show()
                base.day_hud_ui.setImage(self.images['day_hud_night_ui'])
                base.day_hud_ui.setTransparency(TransparencyAttrib.MAlpha)
            if time == "off":
                base.day_hud_ui.hide()

    def set_player_bar(self):
        self.player_bar_ui_frame = DirectFrame(text="", frameColor=(0.0, 0.0, 0.0, 0.7),
                                               frameSize=self.player_bar_ui_frame_size)
        base.player_bar_ui_health = DirectWaitBar(text="", value=100,
                                                  barTexture=self.images["health_bar"], range=100)
        base.player_bar_ui_health.set_pos(-1.7, 0, -0.91)
        base.player_bar_ui_health.set_scale(self.player_bar_ui_scale)

        base.player_bar_ui_stamina = DirectWaitBar(text="", value=100,
                                                   barTexture=self.images["stamina_bar"], range=100)
        base.player_bar_ui_stamina.set_pos(-1.7, 0, -0.93)
        base.player_bar_ui_stamina.set_scale(self.player_bar_ui_scale)

        base.player_bar_ui_courage = DirectWaitBar(text="", value=100,
                                                   barTexture=self.images["courage_bar"], range=100)
        base.player_bar_ui_courage.set_pos(-1.7, 0, -0.95)
        base.player_bar_ui_courage.set_scale(self.player_bar_ui_scale)

        self.player_bar_ui_frame.set_pos(0, 0, 0)

        base.player_bar_ui_health.reparent_to(self.player_bar_ui_frame)
        base.player_bar_ui_stamina.reparent_to(self.player_bar_ui_frame)
        base.player_bar_ui_courage.reparent_to(self.player_bar_ui_frame)

    def clear_player_bar(self):
        if self.player_bar_ui_frame:
            self.player_bar_ui_frame.destroy()

    def set_weapon_ui(self):
        self.weapon_state_ui = OnscreenImage(image=self.images['hands_ui'])
        self.weapon_state_ui.set_pos(self.weapon_state_ui_pos)
        self.weapon_state_ui.setTransparency(TransparencyAttrib.MAlpha)
        self.weapon_state_ui.set_scale(self.weapon_state_ui_scale)

    def clear_weapon_ui(self):
        if self.weapon_state_ui:
            self.weapon_state_ui.destroy()
            self.weapon_state_ui.remove_node()

    def toggle_weapon_state(self, weapon_name):
        if (weapon_name and isinstance(weapon_name, str)
                and self.weapon_state_ui):
            if weapon_name == "hands":
                self.weapon_state_ui.setImage(self.images['hands_ui'])
                self.weapon_state_ui.setTransparency(TransparencyAttrib.MAlpha)
            if weapon_name == "sword":
                self.weapon_state_ui.setImage(self.images['sword_ui'])
                self.weapon_state_ui.setTransparency(TransparencyAttrib.MAlpha)
            if weapon_name == "bow":
                self.weapon_state_ui.setImage(self.images['bow_ui'])
                self.weapon_state_ui.setTransparency(TransparencyAttrib.MAlpha)

    def toggle_all_hud(self, state):
        print(self.weapon_state_ui)
        print(self.player_bar_ui_frame)

        if state and isinstance(state, str):
            if (base.day_hud_ui
                    and self.weapon_state_ui
                    and self.player_bar_ui_frame):
                if state == "visible":
                    base.day_hud_ui.show()
                    self.weapon_state_ui.show()
                    self.player_bar_ui_frame.show()
                    base.player_bar_ui_health.show()
                    base.player_bar_ui_stamina.show()
                    base.player_bar_ui_courage.show()
                if state == "hidden":
                    base.day_hud_ui.hide()
                    self.weapon_state_ui.hide()
                    self.player_bar_ui_frame.hide()
                    base.player_bar_ui_health.hide()
                    base.player_bar_ui_stamina.hide()
                    base.player_bar_ui_courage.hide()
