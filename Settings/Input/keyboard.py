from direct.showbase.InputStateGlobal import inputState


class Keyboard:
    def __init__(self):
        self.base = base
        self.game_settings = base.game_settings
        self.game_dir = base.game_dir
        self.game_cfg = base.game_cfg
        self.game_cfg_dir = base.game_cfg_dir
        self.game_settings_filename = base.game_settings_filename
        self.cfg_path = self.game_cfg

        self.k_forward_lo = self.game_settings['Keymap']['forward'].lower()
        self.k_backward_lo = self.game_settings['Keymap']['backward'].lower()
        self.k_left_lo = self.game_settings['Keymap']['left'].lower()
        self.k_right_lo = self.game_settings['Keymap']['right'].lower()
        self.k_run_lo = self.game_settings['Keymap']['run'].lower()
        self.k_crouch_lo = self.game_settings['Keymap']['crouch'].lower()
        self.k_jump_lo = self.game_settings['Keymap']['jump'].lower()
        self.k_use_lo = self.game_settings['Keymap']['use'].lower()
        self.k_attack_lo = self.game_settings['Keymap']['attack'].lower()
        self.k_h_attack_lo = self.game_settings['Keymap']['h_attack'].lower()
        self.k_f_attack_lo = self.game_settings['Keymap']['f_attack'].lower()
        self.k_block_lo = self.game_settings['Keymap']['block'].lower()
        self.k_sword_lo = self.game_settings['Keymap']['sword'].lower()
        self.k_bow_lo = self.game_settings['Keymap']['bow'].lower()
        self.k_tengri_lo = self.game_settings['Keymap']['tengri'].lower()
        self.k_umai_lo = self.game_settings['Keymap']['umai'].lower()

        self.keymap = {
            'forward': False,
            'backward': False,
            'left': False,
            'right': False,
            'run': False,
            'crouch': False,
            'jump': False,
            'use': False,
            'attack': False,
            'h_attack': False,
            'f_attack': False,
            'block': False,
            'sword': False,
            'bow': False,
            'tengri': False,
            'umai': False
        }
        self.base.game_instance['keymap'] = self.keymap

    def set_key(self, key, value):
        """ Function    : set_key

            Description : Set the state of the actions keys

            Input       : String, Boolean

            Output      : None

            Return      : None
        """
        if (key and isinstance(key, str)
                and isinstance(value, bool)):
            self.keymap[key] = value

    def keymap_init(self):
        """ Function    : keymap_init

            Description : Define the keymap for the actions keys

            Input       : None

            Output      : None

            Return      : None
        """
        # Accept the control keys for movement and rotation
        self.base.accept(self.k_forward_lo, self.set_key, ['forward', True])
        self.base.accept(self.k_backward_lo, self.set_key, ['backward', True])
        self.base.accept(self.k_left_lo, self.set_key, ['left', True])
        self.base.accept(self.k_right_lo, self.set_key, ['right', True])
        self.base.accept(self.k_run_lo, self.set_key, ['run', True])
        self.base.accept(self.k_crouch_lo, self.set_key, ['crouch', True])
        self.base.accept(self.k_jump_lo, self.set_key, ['jump', True])
        self.base.accept(self.k_use_lo, self.set_key, ['use', True])
        self.base.accept(self.k_attack_lo, self.set_key, ['attack', True])
        self.base.accept(self.k_h_attack_lo, self.set_key, ['h_attack', True])
        self.base.accept(self.k_f_attack_lo, self.set_key, ['f_attack', True])
        self.base.accept(self.k_block_lo, self.set_key, ['block', True])
        self.base.accept(self.k_sword_lo, self.set_key, ['sword', True])
        self.base.accept(self.k_bow_lo, self.set_key, ['bow', True])
        self.base.accept(self.k_tengri_lo, self.set_key, ['tengri', True])
        self.base.accept(self.k_umai_lo, self.set_key, ['umai', True])

    def keymap_init_released(self):
        """ Function    : keymap_init_released

            Description : Define the keymap for released actions keys

            Input       : None

            Output      : None

            Return      : None
        """
        self.base.accept("{0}-up".format(self.k_forward_lo), self.set_key, ['forward', False])
        self.base.accept("{0}-up".format(self.k_backward_lo), self.set_key, ['backward', False])
        self.base.accept("{0}-up".format(self.k_left_lo), self.set_key, ['left', False])
        self.base.accept("{0}-up".format(self.k_right_lo), self.set_key, ['right', False])
        self.base.accept("{0}-up".format(self.k_run_lo), self.set_key, ['run', False])
        self.base.accept("{0}-up".format(self.k_crouch_lo), self.set_key, ['crouch', False])
        self.base.accept("{0}-up".format(self.k_jump_lo), self.set_key, ['jump', False])
        self.base.accept("{0}-up".format(self.k_use_lo), self.set_key, ['use', False])
        self.base.accept("{0}-up".format(self.k_attack_lo), self.set_key, ['attack', False])
        self.base.accept("{0}-up".format(self.k_h_attack_lo), self.set_key, ['h_attack', False])
        self.base.accept("{0}-up".format(self.k_f_attack_lo), self.set_key, ['f_attack', False])
        self.base.accept("{0}-up".format(self.k_block_lo), self.set_key, ['block', False])
        self.base.accept("{0}-up".format(self.k_sword_lo), self.set_key, ['sword', False])
        self.base.accept("{0}-up".format(self.k_bow_lo), self.set_key, ['bow', False])
        self.base.accept("{0}-up".format(self.k_tengri_lo), self.set_key, ['tengri', False])
        self.base.accept("{0}-up".format(self.k_umai_lo), self.set_key, ['umai', False])

    def bullet_keymap_init(self):
        """ Function    : bullet_keymap_init

            Description : Define the keymap for Bullet actions keys

            Input       : None

            Output      : None

            Return      : None
        """
        inputState.watchWithModifiers('forward', self.k_forward_lo)
        inputState.watchWithModifiers('reverse', self.k_backward_lo)
        inputState.watchWithModifiers('left', self.k_left_lo)
        inputState.watchWithModifiers('right',  self.k_right_lo)

        # inputState.watchWithModifiers('turnLeft', self.k_left_lo)
        # inputState.watchWithModifiers('turnRight', self.k_right_lo)

        return inputState
