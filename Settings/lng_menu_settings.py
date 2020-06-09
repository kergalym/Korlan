from Settings.menu_settings import MenuSettings


class Language(MenuSettings):
    def __init__(self):
        self.lng_en = 0
        self.lng_kz = 1
        self.lng_ru = 2
        MenuSettings.__init__(self)

    def get_selected_language(self):
        loaded_settings = self.load_settings()
        lng_dict = {'english': self.lng_en,
                    'kazakh': self.lng_kz,
                    'russian': self.lng_ru}
        if loaded_settings['Main']['language'] == 'english':
            lng_dict['english'] = 0
            lng_dict['kazakh'] = 1
            lng_dict['russian'] = 2
            return lng_dict
        elif loaded_settings['Main']['language'] == 'kazakh':
            lng_dict['kazakh'] = 0
            lng_dict['english'] = 1
            lng_dict['russian'] = 2
            return lng_dict
        elif loaded_settings['Main']['language'] == 'russian':
            lng_dict['russian'] = 0
            lng_dict['kazakh'] = 1
            lng_dict['english'] = 2
            return lng_dict

    def set_language_english(self):
        loaded_settings = self.load_settings()
        loaded_settings['Main']['language'] = 'english'
        with open(self.cfg_path, "w") as cfg_file:
            loaded_settings.write(cfg_file)

    def set_language_kazakh(self):
        loaded_settings = self.load_settings()
        loaded_settings['Main']['language'] = 'kazakh'
        with open(self.cfg_path, "w") as cfg_file:
            loaded_settings.write(cfg_file)

    def set_language_russian(self):
        loaded_settings = self.load_settings()
        loaded_settings['Main']['language'] = 'russian'
        with open(self.cfg_path, "w") as cfg_file:
            loaded_settings.write(cfg_file)

    def set_default_language(self):
        loaded_settings = self.load_settings()
        loaded_settings['Main']['language'] = 'english'
        with open(self.cfg_path, "w") as cfg_file:
            loaded_settings.write(cfg_file)
