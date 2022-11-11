from direct.gui.DirectLabel import DirectLabel
from direct.gui.OnscreenImage import OnscreenImage
from direct.gui.OnscreenText import OnscreenText
from panda3d.core import TransparencyAttrib, TextNode, FontPool
from direct.gui.DirectGui import DirectWaitBar
from direct.gui.DirectGui import DirectFrame


class HUD:
    def __init__(self):
        self.base = base
        self.game_dir = base.game_dir
        self.images = base.textures_collector(path="Settings/UI")
        self.fonts = base.fonts_collector()
        self.crosshair_ui_pos = (0, 0, 0)
        self.crosshair_ui_scale = 0.04
        self.day_hud_ui_pos = (0.0, 0, 0.90)
        self.day_hud_ui_scale = (0.5, 0, 0.1)
        self.weapon_state_ui_pos = (1.7, 0, -0.80)
        self.weapon_state_ui_scale = 0.09
        self.arrow_count_ui_pos = (1.78, 0, -0.87)
        self.arrow_count_ui_scale = 0.6

        # Left, right, bottom, top
        self.player_bar_ui_frame_size = [-1.85, -1.55, -0.99, -0.88]
        self.weapon_ui_frame_size = [1.85, 1.55, -0.90, -0.7]
        self.player_bar_ui_scale = (0.14, 0, 0.10)
        self.weapon_ui_scale = (0.14, 0, 0.14)

        # Left, right, bottom, top
        self.npc_hud_ui_frame_size = [-1.85, -1, 1.99, 0.88]
        self.npc_hud_ui_scale = (1.2, 0, 0.20)

        # HUD attributes
        self.day_hud_ui = None
        self.weapon_ui_frame = None
        self.weapon_state_ui = None
        self.arrow_count_ui = None
        self.player_bar_ui_frame = None
        self.player_bar_ui_health = None
        self.player_bar_ui_stamina = None
        self.player_bar_ui_courage = None
        self.crosshair_ui = None
        self.charge_arrow_bar_ui = None
        self.cooldown_bar_ui = None

        self.day_hud_light_tex = self.images['day_hud_light_ui']
        self.day_hud_night_tex = self.images['day_hud_night_ui']

        self.day_cycle_state = {
            "light": False,
            "night": False
        }
        self.menu_font = self.fonts['OpenSans-Regular']
        # instance of the abstract class
        self.font = FontPool
        self.text = TextNode("TextNode")

    def set_aim_crosshair(self):
        self.crosshair_ui = OnscreenImage(image=self.images['crosshair'])
        self.crosshair_ui.set_pos(self.crosshair_ui_pos)
        self.crosshair_ui.set_transparency(TransparencyAttrib.MAlpha)
        self.crosshair_ui.set_scale(self.crosshair_ui_scale)
        self.crosshair_ui.hide()
        self.base.game_instance['crosshair_ui'] = self.crosshair_ui

    def set_day_hud(self):
        self.day_hud_ui = OnscreenImage(image=self.images['day_hud_light_ui'])
        self.day_hud_ui.set_transparency(TransparencyAttrib.MAlpha)
        self.day_hud_ui.set_pos(self.day_hud_ui_pos)
        self.day_hud_ui.set_scale(self.day_hud_ui_scale)
        self.day_hud_ui.hide()

    def set_player_bar(self):
        self.player_bar_ui_frame = DirectFrame(text="", frameColor=(0.0, 0.0, 0.0, 1),
                                               frameSize=self.player_bar_ui_frame_size)

        health = self.base.game_instance['player_props']['health']
        self.player_bar_ui_health = DirectWaitBar(text="", value=health, range=100,
                                                  frameColor=(0, 0.1, 0.1, 0),
                                                  barTexture=self.images["health_bar"])
        self.player_bar_ui_health.set_pos(-1.7, 0, -0.91)
        self.player_bar_ui_health.set_scale(self.player_bar_ui_scale)

        stamina = self.base.game_instance['player_props']['stamina']

        self.player_bar_ui_stamina = DirectWaitBar(text="", value=stamina, range=100,
                                                   frameColor=(0, 0.1, 0.1, 0),
                                                   barTexture=self.images["stamina_bar"])
        self.player_bar_ui_stamina.set_pos(-1.7, 0, -0.93)
        self.player_bar_ui_stamina.set_scale(self.player_bar_ui_scale)

        courage = self.base.game_instance['player_props']['courage']

        self.player_bar_ui_courage = DirectWaitBar(text="", value=courage, range=100,
                                                   frameColor=(0, 0.1, 0.1, 0),
                                                   barTexture=self.images["courage_bar"])
        self.player_bar_ui_courage.set_pos(-1.7, 0, -0.95)
        self.player_bar_ui_courage.set_scale(self.player_bar_ui_scale)

        self.player_bar_ui_frame.set_pos(0, 0, 0)

        self.player_bar_ui_health.reparent_to(self.player_bar_ui_frame)
        self.player_bar_ui_stamina.reparent_to(self.player_bar_ui_frame)
        self.player_bar_ui_courage.reparent_to(self.player_bar_ui_frame)

    def set_weapon_ui(self):
        # Set weapon frame
        self.weapon_ui_frame = DirectFrame(text="", frameColor=(0.0, 0.0, 0.0, 0.4),
                                           frameSize=self.weapon_ui_frame_size)
        self.weapon_ui_frame.set_pos(0, 0, 0)
        base.weapon_ui_frame = self.weapon_ui_frame

        # Set weapon icon
        self.weapon_state_ui = OnscreenImage(image=self.images['hands_ui'])
        self.weapon_state_ui.set_pos(self.weapon_state_ui_pos)
        self.weapon_state_ui.set_transparency(TransparencyAttrib.MAlpha)
        self.weapon_state_ui.set_scale(self.weapon_state_ui_scale)

        # Set weapon count
        text = str(self.base.game_instance['arrow_count'])
        self.arrow_count_ui = OnscreenText(text=text, fg=(255, 255, 255, 1))
        self.arrow_count_ui.set_pos(self.arrow_count_ui_pos)
        self.arrow_count_ui.set_scale(self.arrow_count_ui_scale)
        self.arrow_count_ui.hide()

    def set_arrow_charge_ui(self):
        self.charge_arrow_bar_ui = DirectWaitBar(text="",
                                                 value=0,
                                                 range=100,
                                                 frameColor=(0, 0.1, 0.1, 0),
                                                 barColor=(0.6, 0, 0, 1),
                                                 pos=(-1.43, 0, -0.93),
                                                 scale=(0.1, 0, 0.69))

    def clear_arrow_charge_ui(self):
        if self.charge_arrow_bar_ui:
            self.charge_arrow_bar_ui.hide()
            self.charge_arrow_bar_ui.destroy()
            self.charge_arrow_bar_ui.remove_node()

    def set_cooldown_bar_ui(self):
        self.cooldown_bar_ui = DirectWaitBar(text="",
                                             value=100,
                                             range=100,
                                             frameColor=(0, 0.1, 0.1, 0),
                                             barColor=(0.6, 0.7, 0.4, 1),
                                             pos=(-1.2, 0, -0.93),
                                             scale=(0.1, 0, 0.69))
        self.cooldown_bar_ui.hide()

    def clear_cooldown_bar_ui(self):
        if self.cooldown_bar_ui:
            self.cooldown_bar_ui.hide()
            self.cooldown_bar_ui.destroy()
            self.cooldown_bar_ui.remove_node()

    def clear_aim_crosshair(self):
        if self.crosshair_ui:
            self.crosshair_ui.destroy()
            self.crosshair_ui.remove_node()

    def clear_player_bar(self):
        if self.player_bar_ui_frame:
            self.player_bar_ui_frame.destroy()
            self.player_bar_ui_frame.remove_node()

    def clear_day_hud(self):
        if self.day_hud_ui:
            self.day_hud_ui.destroy()
            self.day_hud_ui.remove_node()

    def clear_weapon_ui(self):
        if self.weapon_ui_frame:
            self.weapon_ui_frame.destroy()
            self.weapon_ui_frame.remove_node()
        if self.weapon_state_ui:
            self.weapon_state_ui.destroy()
            self.weapon_state_ui.remove_node()
        if self.arrow_count_ui:
            self.arrow_count_ui.destroy()
            self.arrow_count_ui.remove_node()

    def toggle_weapon_state(self, weapon_name):
        if not self.base.game_instance['ui_mode']:
            if (weapon_name and isinstance(weapon_name, str)
                    and self.weapon_state_ui):
                self.weapon_state_ui.setImage(self.images['{0}_ui'.format(weapon_name)])
                self.weapon_state_ui.set_transparency(TransparencyAttrib.MAlpha)

                if "bow" in weapon_name:
                    if self.arrow_count_ui:
                        self.arrow_count_ui.show()
                else:
                    if self.arrow_count_ui:
                        self.arrow_count_ui.hide()

    def toggle_day_hud(self, time):
        if not self.base.game_instance['ui_mode']:
            if (time and isinstance(time, str)
                    and self.day_hud_ui):
                if time == "light" and not self.day_cycle_state["light"]:
                    if self.day_hud_ui.is_hidden():
                        self.day_hud_ui.show()
                    self.day_hud_ui.setImage(self.day_hud_light_tex)
                    self.day_hud_ui.set_transparency(TransparencyAttrib.MAlpha)
                    self.day_cycle_state["light"] = True
                    self.day_cycle_state["night"] = False
                if time == "night" and not self.day_cycle_state["night"]:
                    if self.day_hud_ui.is_hidden():
                        self.day_hud_ui.show()
                    self.day_hud_ui.setImage(self.day_hud_night_tex)
                    self.day_hud_ui.set_transparency(TransparencyAttrib.MAlpha)
                    self.day_cycle_state["night"] = True
                    self.day_cycle_state["light"] = False
                if time == "off":
                    self.day_hud_ui.hide()

    def toggle_all_hud(self, state):
        if state and isinstance(state, str):
            if (self.day_hud_ui
                    and self.weapon_state_ui
                    and self.player_bar_ui_frame):
                if state == "visible":
                    self.day_hud_ui.show()
                    self.weapon_state_ui.show()
                    self.player_bar_ui_frame.show()
                if state == "hidden":
                    self.day_hud_ui.hide()
                    self.weapon_state_ui.hide()
                    self.player_bar_ui_frame.hide()
