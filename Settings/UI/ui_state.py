from direct.gui.DirectGui import *
from panda3d.core import FontPool


class UIState:
    def __init__(self):
        self.game_settings = base.game_settings
        self.game_dir = base.game_dir
        # instance of the abstract class
        self.font = FontPool
        self.menu_font = '{0}/Settings/UI/JetBrainsMono-1.0.2/ttf/JetBrainsMono-Regular.ttf'.format(self.game_dir)
        self.text_state = OnscreenText(text="_DEBUG_TEXT_",
                                       pos=(-1.7, 0.9),
                                       scale=0.03,
                                       fg=(255, 255, 255, 0.9),
                                       font=self.font.load_font(self.menu_font),
                                       mayChange=True)

    def set_state_text(self, records):
        if records and isinstance(records, str):
            if (self.game_settings['Debug']['set_debug_mode'] == "YES"
                    and base.game_mode):
                self.text_state.setText(records)
            elif (self.game_settings['Debug']['set_debug_mode'] == "YES"
                  and base.game_mode is False):
                self.text_state.destroy()


class UIMisc:

    def state_text(self, records):
        if records and isinstance(records, dict):
            records_designed = ''
            for state in records:
                text_h = "{0}:\n".format(state)
                text_x = "X: {0}:\n".format(records[state][0])
                text_y = "Y: {0}:\n".format(records[state][1])
                text_z = "Z: {0}:\n".format(records[state][2])
                records_designed = "{0}".format(text_h)
                records_designed += "{0}{1}{2}".format(text_x, text_y, text_z)
            return records_designed
