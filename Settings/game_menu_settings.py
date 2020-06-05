from Settings.menu_settings import MenuSettings


class Game(MenuSettings):
    def __init__(self):
        MenuSettings.__init__(self)

    def set_default_game(self):
        """ Function    : set_default_game

            Description : Set default game settings

            Input       : None

            Output      : None

            Return      : None
        """
        if self.load_settings():
            loaded_settings = self.load_settings()
            loaded_settings['Main']['person_look_mode'] = 'third'
            loaded_settings['Main']['gameplay_mode'] = 'simple'
            loaded_settings['Main']['show_blood'] = 'on'
            with open(self.cfg_path, "w") as cfg_file:
                loaded_settings.write(cfg_file)

    def get_person_look_mode_value(self):
        loaded_settings = self.load_settings()
        if loaded_settings['Main']['person_look_mode'] == 'third':
            return 1
        elif loaded_settings['Main']['person_look_mode'] == 'first':
            return 2

    def load_person_look_mode_value(self):
        person_look_mode = {1: 'third', 2: 'first'}
        return person_look_mode

    def get_gameplay_mode_value(self):
        loaded_settings = self.load_settings()
        if loaded_settings['Main']['gameplay_mode'] == 'simple':
            return 1
        elif loaded_settings['Main']['gameplay_mode'] == 'enhanced':
            return 2

    def load_gameplay_mode_value(self):
        gameplay_mode = {1: 'simple', 2: 'enhanced'}
        return gameplay_mode

    def get_show_blood_value(self):
        loaded_settings = self.load_settings()
        if loaded_settings['Main']['show_blood'] == 'on':
            return 1
        elif loaded_settings['Main']['show_blood'] == 'off':
            return 2

    def load_show_blood_value(self):
        show_blood = {1: 'ON', 2: 'OFF'}
        return show_blood

    def save_person_look_mode_value(self, data):
        loaded_settings = self.load_settings()
        if isinstance(data, str):
            loaded_settings['Main']['person_look_mode'] = data.lower()
            with open(self.cfg_path, "w") as cfg_file:
                loaded_settings.write(cfg_file)

    def save_gameplay_mode_value(self, data):
        loaded_settings = self.load_settings()
        if isinstance(data, str):
            loaded_settings['Main']['gameplay_mode'] = data.lower()
            with open(self.cfg_path, "w") as cfg_file:
                loaded_settings.write(cfg_file)

    def save_show_blood_value(self, data):
        loaded_settings = self.load_settings()
        if isinstance(data, str):
            loaded_settings['Main']['show_blood'] = data.lower()
            with open(self.cfg_path, "w") as cfg_file:
                loaded_settings.write(cfg_file)
