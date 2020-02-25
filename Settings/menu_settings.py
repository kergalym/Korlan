import configparser
from configparser import ConfigParser
from pathlib import Path
from os.path import exists
from os.path import isfile
from os import walk
from sys import exit as sys_exit
from Xlib import display
from Xlib.ext import randr
from panda3d.core import WindowProperties
from panda3d.core import LODNode


class MenuSettings:
    def __init__(self):
        self.cfg_path_default = "{}/Korlan/Configs/default_config.ini".format(str(Path.home()))
        self.cfg_path = "{}/Korlan - Daughter of the Steppes/settings.ini".format(str(Path.home()))
        self.node = None
        self.lod = None
        self.game_settings = None
        self.props = WindowProperties()
        self.cfg_parser = ConfigParser()
        self.allowed_keys = ['Q', 'W', 'E', 'R', 'T', 'Y', 'U',
                             'I', 'O', 'P', 'A', 'S', 'D', 'F',
                             'G', 'H', 'J', 'K', 'L', 'Z', 'X',
                             'C', 'V', 'B', 'N', 'M', '1', '2',
                             '3', '4', '5', '6', '7', '8', '9'
                             ]

    def input_validate(self, cfg_path, op_type):
        if cfg_path and isinstance(op_type, str):
            self.cfg_parser.read(cfg_path)
            data = self.cfg_parser

            if op_type is 'lng':
                try:
                    if data['Main']['language'] == 'russian':
                        return data['Main']['language']
                    elif data['Main']['language'] == 'kazakh':
                        return data['Main']['language']
                    elif data['Main']['language'] == 'english':
                        return data['Main']['language']
                except KeyError or ValueError:
                    sys_exit("\nConfiguration file '{}' is damaged. "
                             "Please delete it and re-run the game again.\n".format(self.cfg_path))

            elif op_type is 'gfx':

                gfx_dict = {}
                gfx_dict_keys = {}
                for x in data['Main']:
                    try:
                        gfx_dict_keys[x] = data['Main'][x]
                    except KeyError or ValueError:
                        sys_exit("\nConfiguration file '{}' is damaged. "
                                 "Please delete it and re-run the game again.\n".format(self.cfg_path))
                gfx_dict['Keymap'] = gfx_dict_keys
                return gfx_dict

            elif op_type is 'snd':

                snd_dict = {}
                snd_dict_keys = {}
                for x in data['Main']:
                    try:
                        snd_dict_keys[x] = data['Main'][x]
                    except KeyError or ValueError:
                        sys_exit("\nConfiguration file '{}' is damaged. "
                                 "Please delete it and re-run the game again.\n".format(self.cfg_path))
                snd_dict['Main'] = snd_dict_keys
                return snd_dict

            elif op_type is 'kmp':

                kmp_dict = {}
                kmp_dict_keys = {}
                for x in data['Keymap']:
                    try:
                        kmp_dict_keys[x] = data['Keymap'][x]
                    except KeyError or ValueError:
                        sys_exit("\nConfiguration file '{}' is damaged. "
                                 "Please delete it and re-run the game again.\n".format(self.cfg_path))
                kmp_dict['Keymap'] = kmp_dict_keys
                return kmp_dict

            elif op_type is 'dev':

                dev_dict = {}
                dev_dict_keys = {}
                for x in data['Debug']:
                    try:
                        dev_dict_keys[x] = data['Debug'][x]
                    except KeyError or ValueError:
                        sys_exit("\nConfiguration file '{}' is damaged. "
                                 "Please delete it and re-run the game again.\n".format(self.cfg_path))
                dev_dict['Debug'] = dev_dict_keys
                return dev_dict

    def float_input_validate_dev_mode(self, data, numeric_type=float):
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
        if isinstance(data, str) and len(data) == 1:
            if any(data in x for x in self.allowed_keys):
                return data
            else:
                return None

    def duplicate_key_check(self, data, loaded_settings):
        if isinstance(data, str) and len(data) == 1:
            only_key_values = [v for x, v in loaded_settings['Keymap'].items()]

            n = 1
            for x in only_key_values:
                if x is data:
                    n = n + 1

            if n == 2:
                return None
            elif n == 1:
                return data

    def load_settings(self):

        if exists(self.cfg_path) and isfile(self.cfg_path):

            try:
                self.cfg_parser.read(self.cfg_path)
                return self.cfg_parser
            except configparser.MissingSectionHeaderError:
                sys_exit("\nNo configuration loaded. "
                         "Please delete damaged configuration file and restart the game."
                         "\nFile: {}".format(self.cfg_path))
            except KeyError:
                sys_exit("\nNo configuration loaded. "
                         "Please delete damaged configuration file and restart the game."
                         "\nFile: {}".format(self.cfg_path))

        elif exists(self.cfg_path_default) and isfile(self.cfg_path_default):

            try:
                self.cfg_parser.read(self.cfg_path_default)
                return self.cfg_parser
            except configparser.MissingSectionHeaderError:
                sys_exit("\nNo configuration loaded. "
                         "Please delete damaged configuration file and restart the game."
                         "\nFile: {}".format(self.cfg_path_default))
            except KeyError:
                sys_exit("\nNo configuration loaded. "
                         "Please delete damaged configuration file and restart the game."
                         "\nFile: {}".format(self.cfg_path_default))


class DevMode(MenuSettings):
    def __init__(self):

        MenuSettings.__init__(self)

    def check_game_assets_devmode(self, exclude):
        asset_path = "{0}/Assets".format(Path.cwd())

        asset_names = []

        if exists(asset_path):
            for root, dirs, files in walk(asset_path, topdown=True):
                if exclude in dirs:
                    dirs.remove(exclude)
                for file in files:
                    if '.egg' and '.egg.bam' not in file:
                        asset_names.append(file)
                    elif '.egg.bam' in file:
                        asset_names.append(file)

        return asset_names

    def get_active_node(self, node_name):
        if node_name and isinstance(node_name, str):
            self.node = node_name
            t = None
            for x in self.check_game_assets_devmode(exclude='Animations'):
                if x is node_name or 'Korlan':
                    t = render.find('**/{}'.format(node_name))
                elif x is node_name:
                    t = render.find('**/{}*'.format(node_name))
                else:
                    return None
            return t
        else:
            return False

    def set_node_pos_x(self, float_pos_x):
        node = self.get_active_node(self.node)
        if node and self.float_input_validate_dev_mode(float_pos_x):
            float_pos_x = self.float_input_validate_dev_mode(float_pos_x)
            node.setX(float_pos_x)
        else:
            return None

    def set_node_pos_y(self, float_pos_y):
        node = self.get_active_node(self.node)
        if node and self.float_input_validate_dev_mode(float_pos_y):
            float_pos_y = self.float_input_validate_dev_mode(float_pos_y)
            node.setY(float_pos_y)
        else:
            return None

    def set_node_pos_z(self, float_pos_z):
        node = self.get_active_node(self.node)
        if node and self.float_input_validate_dev_mode(float_pos_z):
            float_pos_z = self.float_input_validate_dev_mode(float_pos_z)
            node.setZ(float_pos_z)
        else:
            return None

    def set_node_rot_h(self, float_rot_h):
        node = self.get_active_node(self.node)
        if node and self.float_input_validate_dev_mode(float_rot_h):
            float_rot_h = self.float_input_validate_dev_mode(float_rot_h)
            node.setH(float_rot_h)
        else:
            return None

    def set_node_rot_p(self, float_rot_p):
        node = self.get_active_node(self.node)
        if node and self.float_input_validate_dev_mode(float_rot_p):
            float_rot_p = self.float_input_validate_dev_mode(float_rot_p)
            node.setP(float_rot_p)
        else:
            return None

    def set_node_rot_r(self, float_rot_r):
        node = self.get_active_node(self.node)
        if node and self.float_input_validate_dev_mode(float_rot_r):
            float_rot_r = self.float_input_validate_dev_mode(float_rot_r)
            node.setR(float_rot_r)
        else:
            return None

    def save_node_pos(self):
        x = None
        status = None
        if (exists(self.cfg_path)
                and isfile(self.cfg_path)
                and exists(self.cfg_path_default)
                and isfile(self.cfg_path_default)):

            for x in self.check_game_assets_devmode():
                if x is 'Korlan':
                    status = 'player'
                else:
                    status = 'env'

            if status is 'player':
                self.cfg_parser = ConfigParser()
                self.cfg_parser.read(self.cfg_path)
                self.cfg_parser['Debug']['player_pos_x'] = str(render.find("**/{}".format(x)).getX())
                self.cfg_parser['Debug']['player_pos_y'] = str(render.find("**/{}".format(x)).getY())
                self.cfg_parser['Debug']['player_pos_z'] = str(render.find("**/{}".format(x)).getZ())
                self.cfg_parser['Debug']['player_rot_h'] = str(render.find("**/{}".format(x)).getH())
                self.cfg_parser['Debug']['player_rot_p'] = str(render.find("**/{}".format(x)).getP())
                self.cfg_parser['Debug']['player_rot_r'] = str(render.find("**/{}".format(x)).getR())

                with open(self.cfg_path, 'w') as cfg_file:
                    self.cfg_parser.write(cfg_file)

            if status is 'env':
                self.cfg_parser = ConfigParser()
                self.cfg_parser.read(self.cfg_path_default)
                self.cfg_parser[x] = {'pos_x': str(render.find("**/{}".format(x)).getX()),
                                      'pos_y': str(render.find("**/{}".format(x)).getY()),
                                      'pos_z': str(render.find("**/{}".format(x)).getZ()),
                                      'rot_h': str(render.find("**/{}".format(x)).getH()),
                                      'rot_p': str(render.find("**/{}".format(x)).getP()),
                                      'rot_r': str(render.find("**/{}".format(x)).getR())
                                      }

                with open(self.cfg_path_default, "w") as cfg_file:
                    self.cfg_parser.write(cfg_file)

        else:
            return False

    def read_node_pos(self, node_name):
        if (exists(self.cfg_path)
                and isfile(self.cfg_path)
                and node_name):

            for x in self.check_game_assets_devmode():
                if x is node_name and 'Korlan':
                    self.cfg_parser = ConfigParser()
                    self.cfg_parser.read(self.cfg_path)
                    render.find("**/{}".format(x)).setX(float(self.cfg_parser['Debug']['player_pos_x']))
                    render.find("**/{}".format(x)).setY(float(self.cfg_parser['Debug']['player_pos_y']))
                    render.find("**/{}".format(x)).setZ(float(self.cfg_parser['Debug']['player_pos_z']))
                    render.find("**/{}".format(x)).setH(float(self.cfg_parser['Debug']['player_rot_h']))
                    render.find("**/{}".format(x)).setP(float(self.cfg_parser['Debug']['player_rot_p']))
                    render.find("**/{}".format(x)).setR(float(self.cfg_parser['Debug']['player_rot_r']))
                else:
                    self.cfg_parser = ConfigParser()
                    self.cfg_parser.read(self.cfg_path_default)
                    # import pdb; pdb.set_trace()
                    render.find("**/{}*".format(x)).setX(float(self.cfg_parser[x]['pos_x']))
                    render.find("**/{}*".format(x)).setY(float(self.cfg_parser[x]['pos_y']))
                    render.find("**/{}*".format(x)).setZ(float(self.cfg_parser[x]['pos_z']))
                    render.find("**/{}*".format(x)).setH(float(self.cfg_parser[x]['rot_h']))
                    render.find("**/{}*".format(x)).setP(float(self.cfg_parser[x]['rot_p']))
                    render.find("**/{}*".format(x)).setR(float(self.cfg_parser[x]['rot_r']))

        else:
            return False

    def load_node_exp_value(self):
        node_exp_stat = {1: 'YES', 2: 'NO'}
        return node_exp_stat

    def node_exp_value(self):
        loaded_settings = self.load_settings()
        # import pdb; pdb.set_trace()
        if loaded_settings['Debug']['set_debug_mode'] == 'YES':
            return 1
        elif loaded_settings['Debug']['set_debug_mode'] == 'NO':
            return 2

    def save_node_exp_value(self, data):
        loaded_settings = self.load_settings()
        if isinstance(data, str):
            loaded_settings['Debug']['set_debug_mode'] = data

            with open(self.cfg_path, "w") as cfg_file:
                loaded_settings.write(cfg_file)


class Graphics(MenuSettings):
    def __init__(self):
        self.lod = LODNode('LOD')
        self.state_renderpipeline = 'OFF'

        MenuSettings.__init__(self)

    """ @var data is the nested list containing the game settings """

    def set_default_gfx(self):
        if self.load_settings():
            loaded_settings = self.load_settings()
            loaded_settings['Main']['dis_res'] = '1920x1080'
            loaded_settings['Main']['fullscreen'] = 'off'
            loaded_settings['Main']['antialiasing'] = 'off'
            loaded_settings['Main']['postprocessing'] = 'off'
            loaded_settings['Main']['shadows'] = 'off'

            with open(self.cfg_path, "w") as cfg_file:
                loaded_settings.write(cfg_file)

    def load_disp_res(self):
        disp = display.Display()
        scrn = disp.screen()
        window = scrn.root.create_window(0, 0, 1, 1, 1, scrn.root_depth)

        res = randr.get_screen_resources(window)
        res_dict = {}
        res.modes.reverse()

        for index, mode in enumerate(res.modes, 1):
            res_dict[index] = "{}x{}".format(mode.width, mode.height)
        return res_dict

    def load_disp_res_value(self):
        disp_res_count = self.load_disp_res()
        if isinstance(disp_res_count, dict):
            return len(disp_res_count)

    def disp_res_value(self):
        loaded_settings = self.load_settings()
        disp_res_dict = self.load_disp_res()
        num = 0
        for index in disp_res_dict:
            if loaded_settings['Main']['disp_res'] == disp_res_dict[index]:
                num = index
        return num

    def load_shadows_value(self):
        shadows_stat = {1: 'ON', 2: 'OFF'}
        return shadows_stat

    def shadows_value(self):
        loaded_settings = self.load_settings()
        if loaded_settings['Main']['shadows'] == 'on':
            return 1
        elif loaded_settings['Main']['shadows'] == 'off':
            return 2

    def load_postpro_value(self):
        postpro_stat = {1: 'ON', 2: 'OFF'}
        return postpro_stat

    def postpro_value(self):
        loaded_settings = self.load_settings()
        if loaded_settings['Main']['postprocessing'] == 'on':
            return 1
        elif loaded_settings['Main']['postprocessing'] == 'off':
            return 2

    def load_antial_value(self):
        antial_stat = {1: 'ON', 2: 'OFF', 3: 'AUTO', 4: 'multisample'}
        return antial_stat

    def antial_value(self):
        loaded_settings = self.load_settings()
        if loaded_settings['Main']['antialiasing'] == 'on':
            return 1
        elif loaded_settings['Main']['antialiasing'] == 'on':
            return 2

    def save_disp_res_value(self, data):
        loaded_settings = self.load_settings()
        if isinstance(data, str):
            loaded_settings['Main']['disp_res'] = data.lower()

            with open(self.cfg_path, "w") as cfg_file:
                loaded_settings.write(cfg_file)

    def save_shadows_value(self, data):
        loaded_settings = self.load_settings()
        if isinstance(data, str):
            loaded_settings['Main']['shadows'] = data.lower()

            with open(self.cfg_path, "w") as cfg_file:
                loaded_settings.write(cfg_file)

    def save_postpro_value(self, data):
        loaded_settings = self.load_settings()
        if isinstance(data, str):
            loaded_settings['Main']['postprocessing'] = data.lower()

            with open(self.cfg_path, "w") as cfg_file:
                loaded_settings.write(cfg_file)

    def save_antial_value(self, data):
        loaded_settings = self.load_settings()
        if isinstance(data, str):
            loaded_settings['Main']['antialiasing'] = data.lower()

            with open(self.cfg_path, "w") as cfg_file:
                loaded_settings.write(cfg_file)


class Sound(MenuSettings):
    def __init__(self):

        MenuSettings.__init__(self)

    def set_default_snd(self):
        if self.load_settings():
            loaded_settings = self.load_settings()
            loaded_settings['Main']['sound'] = 'on'
            loaded_settings['Main']['music'] = 'on'
            loaded_settings['Main']['sfx'] = 'on'

            with open(self.cfg_path, "w") as cfg_file:
                loaded_settings.write(cfg_file)

    def sound_value(self):
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

    def music_value(self):
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

    def sfx_value(self):
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
