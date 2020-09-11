from configparser import ConfigParser
from os import walk
from os.path import exists, isfile
from pathlib import Path

from Settings.menu_settings import MenuSettings


class DevMode(MenuSettings):
    def __init__(self):
        MenuSettings.__init__(self)

    def check_game_assets_devmode(self, exclude):
        """ Function    : check_game_assets_devmode

            Description : Check game assets in Developer Mode

            Input       : String

            Output      : None

            Return      : List
        """
        asset_path = "{0}/Assets".format(Path.cwd())
        asset_names = []
        if (exclude and isinstance(exclude, str)
                and exists(asset_path)):
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
        """ Function    : get_active_node

            Description : Get active node

            Input       : String

            Output      : None

            Return      : Nodepath or None
        """
        if node_name and isinstance(node_name, str):
            self.node = node_name
            nodepath = None
            for x in self.check_game_assets_devmode(exclude='Animations'):
                if x is node_name or 'Korlan':
                    nodepath = render.find('**/{}'.format(node_name))
                elif x is node_name:
                    nodepath = render.find('**/{}*'.format(node_name))
                else:
                    return None
            return nodepath
        else:
            return False

    def set_node_pos_x(self, float_pos_x):
        """ Function    : set_node_pos_x

            Description : Set node pos by X coordinate

            Input       : Float

            Output      : None

            Return      : None
        """
        node = self.get_active_node(self.node)
        if node and self.float_input_validate_dev_mode(float_pos_x):
            float_pos_x = self.float_input_validate_dev_mode(float_pos_x)
            node.setX(float_pos_x)
        else:
            return None

    def set_node_pos_y(self, float_pos_y):
        """ Function    : set_node_pos_y

            Description : Set node pos by Y coordinate

            Input       : Float

            Output      : None

            Return      : None
        """
        node = self.get_active_node(self.node)
        if node and self.float_input_validate_dev_mode(float_pos_y):
            float_pos_y = self.float_input_validate_dev_mode(float_pos_y)
            node.setY(float_pos_y)
        else:
            return None

    def set_node_pos_z(self, float_pos_z):
        """ Function    : set_node_pos_z

            Description : Set node pos by Z coordinate

            Input       : Float

            Output      : None

            Return      : None
        """
        node = self.get_active_node(self.node)
        if node and self.float_input_validate_dev_mode(float_pos_z):
            float_pos_z = self.float_input_validate_dev_mode(float_pos_z)
            node.setZ(float_pos_z)
        else:
            return None

    def set_node_rot_h(self, float_rot_h):
        """ Function    : set_node_rot_h

            Description : Set node pos by heading

            Input       : Float

            Output      : None

            Return      : None
        """
        node = self.get_active_node(self.node)
        if node and self.float_input_validate_dev_mode(float_rot_h):
            float_rot_h = self.float_input_validate_dev_mode(float_rot_h)
            node.setH(float_rot_h)
        else:
            return None

    def set_node_rot_p(self, float_rot_p):
        """ Function    : set_node_rot_p

            Description : Set node pos by pitch

            Input       : Float

            Output      : None

            Return      : None
        """
        node = self.get_active_node(self.node)
        if node and self.float_input_validate_dev_mode(float_rot_p):
            float_rot_p = self.float_input_validate_dev_mode(float_rot_p)
            node.setP(float_rot_p)
        else:
            return None

    def set_node_rot_r(self, float_rot_r):
        """ Function    : set_node_rot_r

            Description : Set node pos by roll

            Input       : Float

            Output      : None

            Return      : None
        """
        node = self.get_active_node(self.node)
        if node and self.float_input_validate_dev_mode(float_rot_r):
            float_rot_r = self.float_input_validate_dev_mode(float_rot_r)
            node.setR(float_rot_r)
        else:
            return None

    def save_node_pos(self):
        """ Function    : save_node_pos

            Description : Save node position

            Input       : None

            Output      : None

            Return      : None or False
        """
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
        """ Function    : read_node_pos

            Description : Read node position

            Input       : String

            Output      : None

            Return      : None or False
        """
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

    def load_cc_value(self):
        cc_stat = {1: 'YES', 2: 'NO'}
        return cc_stat

    def cc_value(self):
        loaded_settings = self.load_settings()
        if loaded_settings['Debug']['cache_autoclean'] == 'YES':
            return 1
        elif loaded_settings['Debug']['cache_autoclean'] == 'NO':
            return 2

    def save_cc_value(self, data):
        loaded_settings = self.load_settings()
        if isinstance(data, str):
            loaded_settings['Debug']['cache_autoclean'] = data
            with open(self.cfg_path, "w") as cfg_file:
                loaded_settings.write(cfg_file)
