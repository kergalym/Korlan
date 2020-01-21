from direct.gui.DirectGui import *


class HUD:
    def __init__(self):
        self.image = 'ui_tex/hud_image.jpg'
        self.text = 'ui_tex/hud_text.jpg'
        self.text_fg = 'rgba_code'

        self.hud = DirectEntry()

    def hud(self):
        if self.text and isinstance(self.text, str):
            return self.hud

    def set_hud(self):
        pass

    def get_hud(self):
        pass
