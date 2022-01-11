from Settings.menu_settings import MenuSettings


class Sound(MenuSettings):
    def __init__(self):
        MenuSettings.__init__(self)

    def set_default_snd(self):
        """ Function    : set_default_snd

            Description : Set default sound settings

            Input       : None

            Output      : None

            Return      : None
        """
        if self.load_settings():
            loaded_settings = self.load_settings()
            loaded_settings['Main']['sound'] = 'on'
            loaded_settings['Main']['music'] = 'on'
            loaded_settings['Main']['sfx'] = 'on'
            with open(self.cfg_path, "w") as cfg_file:
                loaded_settings.write(cfg_file)

    def get_sound_value(self):
        loaded_settings = self.load_settings()
        if loaded_settings['Main']['sound'] == 'on':
            base.enable_all_audio()
            return 1
        elif loaded_settings['Main']['sound'] == 'off':
            base.disable_all_audio()
            return 2

    def load_sound_value(self):
        sound_stat = {1: 'ON', 2: 'OFF'}
        return sound_stat

    def get_music_value(self):
        loaded_settings = self.load_settings()
        if loaded_settings['Main']['music'] == 'on':
            base.enable_music(True)
            return 1
        elif loaded_settings['Main']['music'] == 'off':
            base.enable_music(False)
            return 2

    def load_music_value(self):
        music_stat = {1: 'ON', 2: 'OFF'}
        return music_stat

    def get_sfx_value(self):
        loaded_settings = self.load_settings()
        if loaded_settings['Main']['sfx'] == 'on':
            base.enable_sound_effects(True)
            return 1
        elif loaded_settings['Main']['sfx'] == 'off':
            base.enable_sound_effects(False)
            return 2

    def load_sfx_value(self):
        sfx_stat = {1: 'ON', 2: 'OFF'}
        return sfx_stat

    def save_sound_value(self, data):
        loaded_settings = self.load_settings()
        if isinstance(data, str):
            loaded_settings['Main']['sound'] = data.lower()
            with open(self.cfg_path, "w") as cfg_file:
                loaded_settings.write(cfg_file)

    def save_music_value(self, data):
        loaded_settings = self.load_settings()
        if isinstance(data, str):
            loaded_settings['Main']['music'] = data.lower()
            with open(self.cfg_path, "w") as cfg_file:
                loaded_settings.write(cfg_file)

    def save_sfx_value(self, data):
        loaded_settings = self.load_settings()
        if isinstance(data, str):
            loaded_settings['Main']['sfx'] = data.lower()
            with open(self.cfg_path, "w") as cfg_file:
                loaded_settings.write(cfg_file)
