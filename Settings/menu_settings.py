import configparser
from configparser import ConfigParser
from pathlib import Path
from os.path import exists
from os.path import isfile
from sys import exit as sys_exit


class MenuSettings:
    def __init__(self):
        self.cfg_path_default = "{0}/Korlan/Configs/default_config.ini".format(str(Path.home()))
        self.cfg_path = "{0}/Korlan - Daughter of the Steppes/settings.ini".format(str(Path.home()))
        self.node = None
        self.lod = None
        self.game_settings = None
        self.cfg_parser = ConfigParser()
        self.allowed_keys = ['Q', 'W', 'E', 'R', 'T', 'Y', 'U',
                             'I', 'O', 'P', 'A', 'S', 'D', 'F',
                             'G', 'H', 'J', 'K', 'L', 'Z', 'X',
                             'C', 'V', 'B', 'N', 'M', '1', '2',
                             '3', '4', '5', '6', '7', '8', '9'
                             ]

    def input_validate(self, cfg_path, op_type):
        """ Function    : input_validate

            Description : Validate input.

            Input       : String

            Output      : None

            Return      : Dictionary
        """
        if cfg_path and isinstance(op_type, str):
            self.cfg_parser.read(cfg_path)
            data = self.cfg_parser
            if op_type == 'lng':
                try:
                    if data['Main']['language'] == 'russian':
                        return data['Main']['language']
                    elif data['Main']['language'] == 'kazakh':
                        return data['Main']['language']
                    elif data['Main']['language'] == 'english':
                        return data['Main']['language']
                except KeyError or ValueError:
                    sys_exit("\nConfiguration file '{0}' is damaged. "
                             "Please delete it and re-run the game again.\n".format(self.cfg_path))
            elif op_type == 'gfx':
                gfx_dict = {}
                gfx_dict_keys = {}
                for x in data['Main']:
                    try:
                        gfx_dict_keys[x] = data['Main'][x]
                    except KeyError or ValueError:
                        sys_exit("\nConfiguration file '{0}' is damaged. "
                                 "Please delete it and re-run the game again.\n".format(self.cfg_path))
                gfx_dict['Keymap'] = gfx_dict_keys
                return gfx_dict
            elif op_type == 'snd':
                snd_dict = {}
                snd_dict_keys = {}
                for x in data['Main']:
                    try:
                        snd_dict_keys[x] = data['Main'][x]
                    except KeyError or ValueError:
                        sys_exit("\nConfiguration file '{0}' is damaged. "
                                 "Please delete it and re-run the game again.\n".format(self.cfg_path))
                snd_dict['Main'] = snd_dict_keys
                return snd_dict
            elif op_type == 'kmp':
                kmp_dict = {}
                kmp_dict_keys = {}
                for x in data['Keymap']:
                    try:
                        kmp_dict_keys[x] = data['Keymap'][x]
                    except KeyError or ValueError:
                        sys_exit("\nConfiguration file '{0}' is damaged. "
                                 "Please delete it and re-run the game again.\n".format(self.cfg_path))
                kmp_dict['Keymap'] = kmp_dict_keys
                return kmp_dict
            elif op_type == 'dev':
                dev_dict = {}
                dev_dict_keys = {}
                for x in data['Debug']:
                    try:
                        dev_dict_keys[x] = data['Debug'][x]
                    except KeyError or ValueError:
                        sys_exit("\nConfiguration file '{0}' is damaged. "
                                 "Please delete it and re-run the game again.\n".format(self.cfg_path))
                dev_dict['Debug'] = dev_dict_keys
                return dev_dict

    def float_input_validate_dev_mode(self, data, numeric_type=float):
        """ Function    : float_input_validate_dev_mode

            Description : Validate input float.

            Input       : String

            Output      : None

            Return      : None
        """
        if (isinstance(data, str) and len(data) <= 5
                or "-" in data):
            try:
                data = float(data)
                return numeric_type(data)
            except ValueError:
                pass
            except TypeError:
                pass

    def int_input_validate(self, data, numeric_type=int):
        """ Function    : int_input_validate

            Description : Validate input int.

            Input       : String

            Output      : None

            Return      : None
        """
        if (isinstance(data, str) and len(data) <= 5
                or "-" in data):
            try:
                data = int(data)
                return numeric_type(data)
            except ValueError:
                pass
            except TypeError:
                pass

    def str_input_validate_keymap(self, data):
        """ Function    : str_input_validate_keymap

            Description : Validate input string.

            Input       : String

            Output      : None

            Return      : String or None
        """
        if isinstance(data, str) and len(data) == 1:
            if any(data in x for x in self.allowed_keys):
                return data
            else:
                return None

    def duplicate_key_check(self, data, loaded_settings):
        """ Function    : duplicate_key_check

            Description : Check for duplicate key.

            Input       : String, Dict

            Output      : None

            Return      : Boolean
        """
        if isinstance(data, str) and len(data) == 1:
            only_key_values = [v for x, v in loaded_settings['Keymap'].items()]

            for key in only_key_values:
                if data == key:
                    return True

        return False

    def load_settings(self):
        """ Function    : load_settings

            Description : Load settings.

            Input       : None

            Output      : None

            Return      : Object or None
        """
        if exists(self.cfg_path) and isfile(self.cfg_path):
            try:
                self.cfg_parser.read(self.cfg_path)
                return self.cfg_parser
            except configparser.MissingSectionHeaderError:
                sys_exit("\nNo configuration loaded. "
                         "Please delete damaged configuration file and restart the game."
                         "\nFile: {0}".format(self.cfg_path))
            except KeyError:
                sys_exit("\nNo configuration loaded. "
                         "Please delete damaged configuration file and restart the game."
                         "\nFile: {0}".format(self.cfg_path))
        elif exists(self.cfg_path_default) and isfile(self.cfg_path_default):
            try:
                self.cfg_parser.read(self.cfg_path_default)
                return self.cfg_parser
            except configparser.MissingSectionHeaderError:
                sys_exit("\nNo configuration loaded. "
                         "Please delete damaged configuration file and restart the game."
                         "\nFile: {0}".format(self.cfg_path_default))
            except KeyError:
                sys_exit("\nNo configuration loaded. "
                         "Please delete damaged configuration file and restart the game."
                         "\nFile: {0}".format(self.cfg_path_default))

