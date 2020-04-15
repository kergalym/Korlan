from Xlib import display
from Xlib.ext import randr
from panda3d.core import LODNode

from Settings.menu_settings import MenuSettings


class Graphics(MenuSettings):
    def __init__(self):
        self.lod = LODNode('LOD')
        self.state_renderpipeline = 'OFF'
        MenuSettings.__init__(self)

    def set_default_gfx(self):
        """ Function    : set_default_gfx

            Description : Set default graphics settings

            Input       : None

            Output      : None

            Return      : None
        """
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

    def get_disp_res_value(self):
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

    def get_shadows_value(self):
        loaded_settings = self.load_settings()
        if loaded_settings['Main']['shadows'] == 'on':
            return 1
        elif loaded_settings['Main']['shadows'] == 'off':
            return 2

    def load_postpro_value(self):
        postpro_stat = {1: 'ON', 2: 'OFF'}
        return postpro_stat

    def get_postpro_value(self):
        loaded_settings = self.load_settings()
        if loaded_settings['Main']['postprocessing'] == 'on':
            return 1
        elif loaded_settings['Main']['postprocessing'] == 'off':
            return 2

    def load_antial_value(self):
        antial_stat = {1: 'ON', 2: 'OFF', 3: 'AUTO', 4: 'multisample'}
        return antial_stat

    def get_antial_value(self):
        loaded_settings = self.load_settings()
        if loaded_settings['Main']['antialiasing'] == 'on':
            return 1
        elif loaded_settings['Main']['antialiasing'] == 'on':
            return 2

    def get_ao_value(self):
        pass
        return 1

    def get_bloom_value(self):
        pass
        return 1

    def get_clouds_value(self):
        pass
        return 1

    def get_cc_value(self):
        pass
        return 1

    def get_scattering_value(self):
        pass
        return 1

    def get_sky_ao_value(self):
        pass
        return 1

    def get_ssr_value(self):
        pass
        return 1

    def get_forward_shading_value(self):
        pass
        return 1

    def get_skin_shading_value(self):
        pass
        return 1

    def get_pssm_value(self):
        pass
        return 1

    def get_dof_value(self):
        pass
        return 1

    def get_env_probes_value(self):
        pass
        return 1

    def get_motion_blur_value(self):
        pass
        return 1

    def get_volumetrics_value(self):
        pass
        return 1

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
