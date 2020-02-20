from direct.gui.DirectGui import *
from panda3d.core import FontPool, TextNode


class UIState:
    def __init__(self):
        self.game_settings = base.game_settings
        self.game_dir = base.game_dir
        # instance of the abstract class
        self.font = FontPool
        self.menu_font = '{0}/Settings/UI/JetBrainsMono-1.0.2/ttf/JetBrainsMono-Regular.ttf'.format(self.game_dir)
        if self.game_settings['Debug']['set_debug_mode'] == "YES":
            OnscreenText(text="DEBUG MODE: Object Position",
                         pos=(-1.8, 0.9),
                         scale=0.03,
                         fg=(255, 255, 255, 0.9),
                         font=self.font.load_font(self.menu_font),
                         align=TextNode.ALeft,
                         mayChange=False)

            self.text_state_h = OnscreenText(text="_DEBUG_TEXT_",
                                             pos=(-1.8, 0.8),
                                             scale=0.03,
                                             fg=(255, 255, 255, 0.9),
                                             font=self.font.load_font(self.menu_font),
                                             align=TextNode.ALeft,
                                             mayChange=True)

            self.text_state_p = OnscreenText(text="_DEBUG_TEXT_",
                                             pos=(-1.4, 0.8),
                                             scale=0.03,
                                             fg=(255, 255, 255, 0.9),
                                             font=self.font.load_font(self.menu_font),
                                             align=TextNode.ALeft,
                                             mayChange=True)

    def set_state_text(self, records_h, records_p):
        if (records_h and records_p
                and isinstance(records_h, str)
                and isinstance(records_p, str)):
            if self.game_settings['Debug']['set_debug_mode'] == "YES":
                if base.game_mode:
                    self.text_state_h.setText(records_h)
                    self.text_state_p.setText(records_p)
                elif base.game_mode is False:
                    self.text_state_h.destroy()
                    self.text_state_p.destroy()


class UIMisc:

    def state_text_h(self, records):
        if records and isinstance(records, dict):
            records_designed = ''
            for state in records:
                text_h = "{0}: \n".format(state)
                records_designed += text_h
            return records_designed

    def state_text_p(self, records):
        if records and isinstance(records, dict):
            records_designed = ''
            for state in records:
                text_x = "  X: {0} ".format(records[state][0])
                text_y = "  Y: {0} ".format(records[state][1])
                text_z = "  Z: {0} \n".format(records[state][2])
                records_designed += text_x
                records_designed += text_y
                records_designed += text_z
            return records_designed
