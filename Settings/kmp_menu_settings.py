from Settings.menu_settings import MenuSettings


class Keymap(MenuSettings):
    def __init__(self):
        self.settings = None
        MenuSettings.__init__(self)

    def set_key_forward(self, data):
        if self.load_settings() and self.str_input_validate_keymap(data):
            loaded_settings = self.load_settings()
            if self.duplicate_key_check(data, loaded_settings) is not None:
                data = self.duplicate_key_check(data, loaded_settings)
                loaded_settings['Keymap']['forward'] = self.str_input_validate_keymap(data)
            with open(self.cfg_path, "w") as cfg_file:
                loaded_settings.write(cfg_file)

    def set_key_backward(self, data):
        if self.load_settings() and self.str_input_validate_keymap(data):
            loaded_settings = self.load_settings()
            if self.duplicate_key_check(data, loaded_settings) is not None:
                data = self.duplicate_key_check(data, loaded_settings)
                loaded_settings['Keymap']['backward'] = self.str_input_validate_keymap(data)
            with open(self.cfg_path, "w") as cfg_file:
                loaded_settings.write(cfg_file)

    def set_key_left(self, data):
        if self.load_settings() and self.str_input_validate_keymap(data):
            loaded_settings = self.load_settings()
            if self.duplicate_key_check(data, loaded_settings) is not None:
                data = self.duplicate_key_check(data, loaded_settings)
                loaded_settings['Keymap']['left'] = self.str_input_validate_keymap(data)
            with open(self.cfg_path, "w") as cfg_file:
                loaded_settings.write(cfg_file)

    def set_key_right(self, data):
        if self.load_settings() and self.str_input_validate_keymap(data):
            loaded_settings = self.load_settings()
            if self.duplicate_key_check(data, loaded_settings) is not None:
                data = self.duplicate_key_check(data, loaded_settings)
                loaded_settings['Keymap']['right'] = self.str_input_validate_keymap(data)
            with open(self.cfg_path, "w") as cfg_file:
                loaded_settings.write(cfg_file)

    def set_key_crouch(self, data):
        if self.load_settings() and self.str_input_validate_keymap(data):
            loaded_settings = self.load_settings()
            if self.duplicate_key_check(data, loaded_settings) is not None:
                data = self.duplicate_key_check(data, loaded_settings)
                loaded_settings['Keymap']['crouch'] = self.str_input_validate_keymap(data)
            with open(self.cfg_path, "w") as cfg_file:
                loaded_settings.write(cfg_file)

    def set_key_jump(self, data):
        if self.load_settings() and self.str_input_validate_keymap(data):
            loaded_settings = self.load_settings()
            if self.duplicate_key_check(data, loaded_settings) is not None:
                data = self.duplicate_key_check(data, loaded_settings)
                loaded_settings['Keymap']['jump'] = self.str_input_validate_keymap(data)
            with open(self.cfg_path, "w") as cfg_file:
                loaded_settings.write(cfg_file)

    def set_key_use(self, data):
        if self.load_settings() and self.str_input_validate_keymap(data):
            loaded_settings = self.load_settings()
            if self.duplicate_key_check(data, loaded_settings) is not None:
                data = self.duplicate_key_check(data, loaded_settings)
                loaded_settings['Keymap']['use'] = self.str_input_validate_keymap(data)
            with open(self.cfg_path, "w") as cfg_file:
                loaded_settings.write(cfg_file)

    def set_key_attack(self, data):
        if self.load_settings() and self.str_input_validate_keymap(data):
            loaded_settings = self.load_settings()
            if self.duplicate_key_check(data, loaded_settings) is not None:
                data = self.duplicate_key_check(data, loaded_settings)
                loaded_settings['Keymap']['attack'] = self.str_input_validate_keymap(data)
            with open(self.cfg_path, "w") as cfg_file:
                loaded_settings.write(cfg_file)

    def set_key_h_attack(self, data):
        if self.load_settings() and self.str_input_validate_keymap(data):
            loaded_settings = self.load_settings()
            if self.duplicate_key_check(data, loaded_settings) is not None:
                data = self.duplicate_key_check(data, loaded_settings)
                loaded_settings['Keymap']['h_attack'] = self.str_input_validate_keymap(data)
            with open(self.cfg_path, "w") as cfg_file:
                loaded_settings.write(cfg_file)

    def set_key_f_attack(self, data):
        if self.load_settings() and self.str_input_validate_keymap(data):
            loaded_settings = self.load_settings()
            if self.duplicate_key_check(data, loaded_settings) is not None:
                data = self.duplicate_key_check(data, loaded_settings)
                loaded_settings['Keymap']['f_attack'] = self.str_input_validate_keymap(data)
            with open(self.cfg_path, "w") as cfg_file:
                loaded_settings.write(cfg_file)

    def set_key_block(self, data):
        if self.load_settings() and self.str_input_validate_keymap(data):
            loaded_settings = self.load_settings()
            if self.duplicate_key_check(data, loaded_settings) is not None:
                data = self.duplicate_key_check(data, loaded_settings)
                loaded_settings['Keymap']['block'] = self.str_input_validate_keymap(data)
            with open(self.cfg_path, "w") as cfg_file:
                loaded_settings.write(cfg_file)

    def set_key_sword(self, data):
        if self.load_settings() and self.str_input_validate_keymap(data):
            loaded_settings = self.load_settings()
            if self.duplicate_key_check(data, loaded_settings) is not None:
                data = self.duplicate_key_check(data, loaded_settings)
                loaded_settings['Keymap']['sword'] = self.str_input_validate_keymap(data)
            with open(self.cfg_path, "w") as cfg_file:
                loaded_settings.write(cfg_file)

    def set_key_bow(self, data):
        if self.load_settings() and self.str_input_validate_keymap(data):
            loaded_settings = self.load_settings()
            if self.duplicate_key_check(data, loaded_settings) is not None:
                data = self.duplicate_key_check(data, loaded_settings)
                loaded_settings['Keymap']['bow'] = self.str_input_validate_keymap(data)
            with open(self.cfg_path, "w") as cfg_file:
                loaded_settings.write(cfg_file)

    def set_key_tengri(self, data):
        if self.load_settings() and self.str_input_validate_keymap(data):
            loaded_settings = self.load_settings()
            if self.duplicate_key_check(data, loaded_settings) is not None:
                data = self.duplicate_key_check(data, loaded_settings)
                loaded_settings['Keymap']['tengri'] = self.str_input_validate_keymap(data)
            with open(self.cfg_path, "w") as cfg_file:
                loaded_settings.write(cfg_file)

    def set_key_umay(self, data):
        if self.load_settings() and self.str_input_validate_keymap(data):
            loaded_settings = self.load_settings()
            if self.duplicate_key_check(data, loaded_settings) is not None:
                data = self.duplicate_key_check(data, loaded_settings)
                loaded_settings['Keymap']['umai'] = self.str_input_validate_keymap(data)
            with open(self.cfg_path, "w") as cfg_file:
                loaded_settings.write(cfg_file)

    def set_default_keymap(self):
        if self.load_settings():
            loaded_settings = self.load_settings()
            loaded_settings['Keymap']['forward'] = 'W'
            loaded_settings['Keymap']['backward'] = 'S'
            loaded_settings['Keymap']['left'] = 'A'
            loaded_settings['Keymap']['right'] = 'D'
            loaded_settings['Keymap']['crouch'] = 'C'
            loaded_settings['Keymap']['jump'] = 'spacebar'
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
