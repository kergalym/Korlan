

class PlayWorker:

    def __init__(self):
        self.game_mode = base.game_mode
        self.menu_mode = base.menu_mode
        self.game_settings = base.game_settings
        self.game_dir = base.game_dir
        self.game_cfg = base.game_cfg
        self.game_cfg_dir = base.game_cfg_dir
        self.game_settings_filename = base.game_settings_filename
        self.cfg_path = self.game_cfg

    def load_game(self):
        if (self.game_mode is False
                and self.menu_mode is True):
            pass

    def save_game(self):
        if (self.game_mode is False
                and self.menu_mode is True):
            pass

    def delete_game(self):
        if (self.game_mode is False
                and self.menu_mode is True):
            pass
