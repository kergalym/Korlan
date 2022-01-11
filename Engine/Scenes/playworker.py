

class PlayWorker:

    def __init__(self):
        self.base = base
        self.game_settings = base.game_settings
        self.game_dir = base.game_dir
        self.game_cfg = base.game_cfg
        self.game_cfg_dir = base.game_cfg_dir
        self.game_settings_filename = base.game_settings_filename
        self.cfg_path = self.game_cfg

    def load_game(self):
        if self.base.game_instance['menu_mode']:
            pass

    def save_game(self):
        if self.base.game_instance['menu_mode']:
            pass

    def delete_game(self):
        if self.base.game_instance['menu_mode']:
            pass
