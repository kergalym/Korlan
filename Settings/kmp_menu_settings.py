from Settings.menu_settings import MenuSettings


class Keymap(MenuSettings):
    def __init__(self):
        self.settings = None
        MenuSettings.__init__(self)
        self.loaded_settings = self.load_settings()

    def set_key_forward(self, data):
        if self.load_settings() and self.str_input_validate_keymap(data):
            loaded_settings = self.loaded_settings
            if not self.duplicate_key_check(data, loaded_settings):
                loaded_settings['Keymap']['forward'] = data

    def set_key_backward(self, data):
        if self.load_settings() and self.str_input_validate_keymap(data):
            loaded_settings = self.loaded_settings
            if not self.duplicate_key_check(data, loaded_settings):
                loaded_settings['Keymap']['backward'] = data

    def set_key_left(self, data):
        if self.load_settings() and self.str_input_validate_keymap(data):
            loaded_settings = self.loaded_settings
            if not self.duplicate_key_check(data, loaded_settings):
                loaded_settings['Keymap']['left'] = data

    def set_key_right(self, data):
        if self.load_settings() and self.str_input_validate_keymap(data):
            loaded_settings = self.loaded_settings
            if not self.duplicate_key_check(data, loaded_settings):
                loaded_settings['Keymap']['right'] = data

    def set_key_crouch(self, data):
        if self.load_settings() and self.str_input_validate_keymap(data):
            loaded_settings = self.loaded_settings
            if not self.duplicate_key_check(data, loaded_settings):
                loaded_settings['Keymap']['crouch'] = data

    def set_key_jump(self, data):
        if self.load_settings() and self.str_input_validate_keymap(data):
            loaded_settings = self.loaded_settings
            if not self.duplicate_key_check(data, loaded_settings):
                loaded_settings['Keymap']['jump'] = data

    def set_key_use(self, data):
        if self.load_settings() and self.str_input_validate_keymap(data):
            loaded_settings = self.loaded_settings
            if not self.duplicate_key_check(data, loaded_settings):
                loaded_settings['Keymap']['use'] = data

    def set_key_attack(self, data):
        if self.load_settings() and self.str_input_validate_keymap(data):
            loaded_settings = self.loaded_settings
            if not self.duplicate_key_check(data, loaded_settings):
                loaded_settings['Keymap']['attack'] = data

    def set_key_h_attack(self, data):
        if self.load_settings() and self.str_input_validate_keymap(data):
            loaded_settings = self.loaded_settings
            if not self.duplicate_key_check(data, loaded_settings):
                loaded_settings['Keymap']['h_attack'] = data

    def set_key_f_attack(self, data):
        if self.load_settings() and self.str_input_validate_keymap(data):
            loaded_settings = self.loaded_settings
            if not self.duplicate_key_check(data, loaded_settings):
                loaded_settings['Keymap']['f_attack'] = data

    def set_key_block(self, data):
        if self.load_settings() and self.str_input_validate_keymap(data):
            loaded_settings = self.loaded_settings
            if not self.duplicate_key_check(data, loaded_settings):
                loaded_settings['Keymap']['block'] = data

    def set_key_sword(self, data):
        if self.load_settings() and self.str_input_validate_keymap(data):
            loaded_settings = self.loaded_settings
            if not self.duplicate_key_check(data, loaded_settings):
                loaded_settings['Keymap']['sword'] = data

    def set_key_bow(self, data):
        if self.load_settings() and self.str_input_validate_keymap(data):
            loaded_settings = self.loaded_settings
            if not self.duplicate_key_check(data, loaded_settings):
                loaded_settings['Keymap']['bow'] = data

    def set_key_tengri(self, data):
        if self.load_settings() and self.str_input_validate_keymap(data):
            loaded_settings = self.loaded_settings
            if not self.duplicate_key_check(data, loaded_settings):
                loaded_settings['Keymap']['tengri'] = data

    def set_key_umay(self, data):
        if self.load_settings() and self.str_input_validate_keymap(data):
            loaded_settings = self.loaded_settings
            if not self.duplicate_key_check(data, loaded_settings):
                loaded_settings['Keymap']['umai'] = data

    def set_default_keymap(self):
        if self.load_settings():
            loaded_settings = self.loaded_settings
            loaded_settings['Keymap']['forward'] = 'W'
            loaded_settings['Keymap']['backward'] = 'S'
            loaded_settings['Keymap']['left'] = 'A'
            loaded_settings['Keymap']['right'] = 'D'
            loaded_settings['Keymap']['t_up'] = 'ARROW_UP'
            loaded_settings['Keymap']['t_down'] = 'ARROW_DOWN'
            loaded_settings['Keymap']['t_left'] = 'ARROW_LEFT'
            loaded_settings['Keymap']['t_right'] = 'ARROW_RIGHT'
            loaded_settings['Keymap']['crouch'] = 'C'
            loaded_settings['Keymap']['jump'] = 'SPACE'
            loaded_settings['Keymap']['use'] = 'E'
            loaded_settings['Keymap']['attack'] = 'MOUSE1'
            loaded_settings['Keymap']['h_attack'] = 'H'
            loaded_settings['Keymap']['f_attack'] = 'F'
            loaded_settings['Keymap']['block'] = 'MOUSE2'
            loaded_settings['Keymap']['sword'] = '1'
            loaded_settings['Keymap']['bow'] = '2'
            loaded_settings['Keymap']['tengri'] = '3'
            loaded_settings['Keymap']['umai'] = '4'
            with open(self.cfg_path, "w") as cfg_file:
                loaded_settings.write(cfg_file)
