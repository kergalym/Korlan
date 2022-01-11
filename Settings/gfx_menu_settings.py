from pathlib import Path

from Engine.Render.rplibs.yaml import yaml_py3 as rp_yaml
from Settings.menu_settings import MenuSettings


class Graphics(MenuSettings):
    def __init__(self):
        self.state_renderpipeline = 'OFF'
        self.game_dir = str(Path.cwd())
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
            loaded_settings['Main']['antialiasing'] = 'on'
            loaded_settings['Main']['postprocessing'] = 'on'
            loaded_settings['Main']['details'] = 'high'
            loaded_settings['Main']['texture_compression'] = 'active'
            loaded_settings['Main']['shadows'] = 'on'
            with open(self.cfg_path, "w") as cfg_file:
                loaded_settings.write(cfg_file)

    def load_disp_res(self):
        di = base.pipe.getDisplayInformation()
        res_dict = {}
        for index in range(di.getTotalDisplayModes()):
            res_dict[index] = "{}x{}".format(di.getDisplayModeWidth(index),
                                             di.getDisplayModeHeight(index))
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

    def load_details_value(self):
        details_stat = {1: 'LOW', 2: 'MEDIUM', 3: 'HIGH'}
        return details_stat

    def get_details_value(self):
        loaded_settings = self.load_settings()
        if loaded_settings['Main']['details'] == 'low':
            return 1
        elif loaded_settings['Main']['details'] == 'medium':
            return 2
        elif loaded_settings['Main']['details'] == 'high':
            return 3

    def load_texcomp_value(self):
        textures_stat = {1: 'DEFAULT', 2: 'INACTIVE', 3: 'ACTIVE'}
        return textures_stat

    def get_texcomp_value(self):
        loaded_settings = self.load_settings()
        if loaded_settings['Main']['texture_compression'] == 'default':
            return 1
        elif loaded_settings['Main']['texture_compression'] == 'inactive':
            return 2
        elif loaded_settings['Main']['texture_compression'] == 'active':
            return 3

    def load_shadows_value(self):
        shadows_stat = {1: 'OFF', 2: 'ON'}
        return shadows_stat

    def get_shadows_value(self):
        loaded_settings = self.load_settings()
        if loaded_settings['Main']['shadows'] == 'off':
            return 1
        elif loaded_settings['Main']['shadows'] == 'on':
            return 2

    def load_postpro_value(self):
        postpro_stat = {1: 'OFF', 2: 'ON'}
        return postpro_stat

    def get_postpro_value(self):
        loaded_settings = self.load_settings()
        if loaded_settings['Main']['postprocessing'] == 'off':
            return 1
        elif loaded_settings['Main']['postprocessing'] == 'on':
            return 2

    def load_antial_value(self):
        antial_stat = {1: 'OFF', 2: 'ON', 3: 'AUTO', 4: 'multisample'}
        return antial_stat

    def get_antial_value(self):
        loaded_settings = self.load_settings()
        if loaded_settings['Main']['antialiasing'] == 'off':
            return 1
        elif loaded_settings['Main']['antialiasing'] == 'on':
            return 2

    def load_ao_value(self):
        return {1: 'OFF', 2: 'SSAO', 3: 'HBAO', 4: 'SSVO', 5: 'ALCHEMY', 6: 'UE4AO', 7: 'ON'}

    def load_bloom_value(self):
        return {1: 'OFF', 2: 'ON'}

    def load_clouds_value(self):
        return {1: 'OFF', 2: 'ON'}

    def load_cc_value(self):
        return {1: 'OFF', 2: 'ON'}

    def load_dof_value(self):
        return {1: 'OFF', 2: 'ON'}

    def load_env_probes_value(self):
        return {1: 'OFF', 2: 'ON'}

    def load_forward_shading_value(self):
        return {1: 'OFF', 2: 'ON'}

    def load_motion_blur_value(self):
        return {1: 'OFF', 2: 'ON'}

    def load_pssm_value(self):
        return {1: 'OFF', 2: 'ON'}

    def load_scattering_value(self):
        return {1: 'OFF', 2: 'ON'}

    def load_skin_shading_value(self):
        return {1: 'OFF', 2: 'ON'}

    def load_sky_ao_value(self):
        return {1: 'OFF', 2: 'ON'}

    def load_smaa_value(self):
        return {1: 'OFF', 2: 'ON'}

    def load_ssr_value(self):
        return {1: 'OFF', 2: 'ON'}

    def load_volumetrics_value(self):
        return {1: 'OFF', 2: 'ON'}

    def get_ao_value(self):
        with open("{0}/Engine/Render/config/plugins.yaml".format(self.game_dir), 'r') as f:
            config = rp_yaml.safe_load(f)
            if 'ao' in config['enabled'] and config['overrides']['ao']['technique'] == 'SSAO':
                return 2
            elif 'ao' in config['enabled'] and config['overrides']['ao']['technique'] == 'HBAO':
                return 3
            elif 'ao' in config['enabled'] and config['overrides']['ao']['technique'] == 'SSVO':
                return 4
            elif 'ao' in config['enabled'] and config['overrides']['ao']['technique'] == 'ALCHEMY':
                return 5
            elif 'ao' in config['enabled'] and config['overrides']['ao']['technique'] == 'UE4AO':
                return 6
            else:
                return 7

    def get_bloom_value(self):
        with open("{0}/Engine/Render/config/plugins.yaml".format(self.game_dir), 'r') as f:
            config = rp_yaml.safe_load(f)
            if 'bloom' in config['enabled']:
                return 2
            else:
                return 1

    def get_clouds_value(self):
        with open("{0}/Engine/Render/config/plugins.yaml".format(self.game_dir), 'r') as f:
            config = rp_yaml.safe_load(f)
            if 'clouds' in config['enabled']:
                return 2
            else:
                return 1

    def get_cc_value(self):
        with open("{0}/Engine/Render/config/plugins.yaml".format(self.game_dir), 'r') as f:
            config = rp_yaml.safe_load(f)
            if 'color_correction' in config['enabled']:
                return 2
            else:
                return 1

    def get_scattering_value(self):
        with open("{0}/Engine/Render/config/plugins.yaml".format(self.game_dir), 'r') as f:
            config = rp_yaml.safe_load(f)
            if 'scattering' in config['enabled']:
                return 2
            else:
                return 1

    def get_sky_ao_value(self):
        with open("{0}/Engine/Render/config/plugins.yaml".format(self.game_dir), 'r') as f:
            config = rp_yaml.safe_load(f)
            if 'sky_ao' in config['enabled']:
                return 2
            else:
                return 1

    def get_ssr_value(self):
        with open("{0}/Engine/Render/config/plugins.yaml".format(self.game_dir), 'r') as f:
            config = rp_yaml.safe_load(f)
            if 'ssr' in config['enabled']:
                return 2
            else:
                return 1

    def get_forward_shading_value(self):
        with open("{0}/Engine/Render/config/plugins.yaml".format(self.game_dir), 'r') as f:
            config = rp_yaml.safe_load(f)
            if 'forward_shading' in config['enabled']:
                return 2
            else:
                return 1

    def get_skin_shading_value(self):
        with open("{0}/Engine/Render/config/plugins.yaml".format(self.game_dir), 'r') as f:
            config = rp_yaml.safe_load(f)
            if 'skin_shading' in config['enabled']:
                return 2
            else:
                return 1

    def get_pssm_value(self):
        with open("{0}/Engine/Render/config/plugins.yaml".format(self.game_dir), 'r') as f:
            config = rp_yaml.safe_load(f)
            if 'pssm' in config['enabled']:
                return 2
            else:
                return 1

    def get_dof_value(self):
        with open("{0}/Engine/Render/config/plugins.yaml".format(self.game_dir), 'r') as f:
            config = rp_yaml.safe_load(f)
            if 'dof' in config['enabled']:
                return 2
            else:
                return 1

    def get_env_probes_value(self):
        with open("{0}/Engine/Render/config/plugins.yaml".format(self.game_dir), 'r') as f:
            config = rp_yaml.safe_load(f)
            if 'env_probes' in config['enabled']:
                return 2
            else:
                return 1

    def get_motion_blur_value(self):
        with open("{0}/Engine/Render/config/plugins.yaml".format(self.game_dir), 'r') as f:
            config = rp_yaml.safe_load(f)
            if 'motion_blur' in config['enabled']:
                return 2
            else:
                return 1

    def get_volumetrics_value(self):
        with open("{0}/Engine/Render/config/plugins.yaml".format(self.game_dir), 'r') as f:
            config = rp_yaml.safe_load(f)
            if 'volumetrics' in config['enabled']:
                return 2
            else:
                return 1

    def save_disp_res_value(self, data):
        loaded_settings = self.load_settings()
        if isinstance(data, str):
            loaded_settings['Main']['disp_res'] = data.lower()
            with open(self.cfg_path, "w") as cfg_file:
                loaded_settings.write(cfg_file)

    def save_details_value(self, data):
        loaded_settings = self.load_settings()
        if isinstance(data, str):
            loaded_settings['Main']['details'] = data.lower()
            with open(self.cfg_path, "w") as cfg_file:
                loaded_settings.write(cfg_file)

    def save_texcomp_value(self, data):
        loaded_settings = self.load_settings()
        if isinstance(data, str):
            loaded_settings['Main']['texture_compression'] = data.lower()
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

    def save_ao_value(self, data):
        if data and isinstance(data, str):
            with open("{0}/Engine/Render/config/plugins.yaml".format(self.game_dir), 'r') as f:
                config = rp_yaml.safe_load(f)

                if config.get('disabled') and config.get('enabled'):
                    if data != 'ON' and data != 'OFF':
                        config['overrides']['ao']['technique'] = data
                    with open("{0}/Engine/Render/config/plugins.yaml".format(self.game_dir), 'w') as f:
                        f.write(rp_yaml.safe_dump(config, default_flow_style=False))
                    with open("{0}/Engine/Render/config/plugins.yaml".format(self.game_dir), 'r') as f:
                        config = rp_yaml.safe_load(f)
                        if data == 'ON':
                            if 'ao' in config['disabled']:
                                config['disabled'].remove('ao')
                            if 'ao' not in config['enabled']:
                                config['enabled'].append('ao')
                        if data == 'OFF':
                            if 'ao' not in config['disabled']:
                                config['disabled'].append('ao')
                            if 'ao' in config['enabled']:
                                config['enabled'].remove('ao')

            with open("{0}/Engine/Render/config/plugins.yaml".format(self.game_dir), 'w') as f:
                f.write(rp_yaml.safe_dump(config, default_flow_style=False))

    def save_bloom_value(self, data):
        if data and isinstance(data, str):
            with open("{0}/Engine/Render/config/plugins.yaml".format(self.game_dir), 'r') as f:
                config = rp_yaml.safe_load(f)

                if config.get('disabled') and config.get('enabled'):
                    if data == 'ON':
                        if 'bloom' in config.get('disabled'):
                            config['disabled'].remove('bloom')
                        if 'bloom' not in config.get('enabled'):
                            config['enabled'].append('bloom')
                    if data == 'OFF':
                        if 'bloom' not in config.get('disabled'):
                            config['disabled'].append('bloom')
                        if 'bloom' in config.get('enabled'):
                            config['enabled'].remove('bloom')

            with open("{0}/Engine/Render/config/plugins.yaml".format(self.game_dir), 'w') as f:
                f.write(rp_yaml.safe_dump(config, default_flow_style=False))

    def save_clouds_value(self, data):
        if data and isinstance(data, str):
            with open("{0}/Engine/Render/config/plugins.yaml".format(self.game_dir), 'r') as f:
                config = rp_yaml.safe_load(f)

                if config.get('disabled') and config.get('enabled'):
                    if data == 'ON':
                        if 'clouds' in config['disabled']:
                            config['disabled'].remove('clouds')
                        if 'clouds' not in config['enabled']:
                            config['enabled'].append('clouds')
                    if data == 'OFF':
                        if 'clouds' not in config['disabled']:
                            config['disabled'].append('clouds')
                        if 'clouds' in config['enabled']:
                            config['enabled'].remove('clouds')

            with open("{0}/Engine/Render/config/plugins.yaml".format(self.game_dir), 'w') as f:
                f.write(rp_yaml.safe_dump(config, default_flow_style=False))

    def save_color_correction_value(self, data):
        if data and isinstance(data, str):
            with open("{0}/Engine/Render/config/plugins.yaml".format(self.game_dir), 'r') as f:
                config = rp_yaml.safe_load(f)

                if config.get('disabled') and config.get('enabled'):
                    if data == 'ON':
                        if 'color_correction' in config['disabled']:
                            config['disabled'].remove('color_correction')
                        if 'color_correction' not in config['enabled']:
                            config['enabled'].append('color_correction')
                    if data == 'OFF':
                        if 'color_correction' not in config['disabled']:
                            config['disabled'].append('color_correction')
                        if 'color_correction' in config['enabled']:
                            config['enabled'].remove('color_correction')

            with open("{0}/Engine/Render/config/plugins.yaml".format(self.game_dir), 'w') as f:
                f.write(rp_yaml.safe_dump(config, default_flow_style=False))

    def save_dof_value(self, data):
        if data and isinstance(data, str):
            with open("{0}/Engine/Render/config/plugins.yaml".format(self.game_dir), 'r') as f:
                config = rp_yaml.safe_load(f)

                if config.get('disabled') and config.get('enabled'):
                    if data == 'ON':
                        if 'dof' in config['disabled']:
                            config['disabled'].remove('dof')
                        if 'dof' not in config['enabled']:
                            config['enabled'].append('dof')
                    if data == 'OFF':
                        if 'dof' not in config['disabled']:
                            config['disabled'].append('dof')
                        if 'dof' in config['enabled']:
                            config['enabled'].remove('dof')

            with open("{0}/Engine/Render/config/plugins.yaml".format(self.game_dir), 'w') as f:
                f.write(rp_yaml.safe_dump(config, default_flow_style=False))

    def save_env_probes_value(self, data):
        if data and isinstance(data, str):
            with open("{0}/Engine/Render/config/plugins.yaml".format(self.game_dir), 'r') as f:
                config = rp_yaml.safe_load(f)

                if config.get('disabled') and config.get('enabled'):
                    if data == 'ON':
                        if 'env_probes' in config['disabled']:
                            config['disabled'].remove('env_probes')
                        if 'env_probes' not in config['enabled']:
                            config['enabled'].append('env_probes')
                    if data == 'OFF':
                        if 'env_probes' not in config['disabled']:
                            config['disabled'].append('env_probes')
                        if 'env_probes' in config['enabled']:
                            config['enabled'].remove('env_probes')

            with open("{0}/Engine/Render/config/plugins.yaml".format(self.game_dir), 'w') as f:
                f.write(rp_yaml.safe_dump(config, default_flow_style=False))

    def save_forward_shading_value(self, data):
        if data and isinstance(data, str):
            with open("{0}/Engine/Render/config/plugins.yaml".format(self.game_dir), 'r') as f:
                config = rp_yaml.safe_load(f)

                if config.get('disabled') and config.get('enabled'):
                    if data == 'ON':
                        if 'forward_shading' in config['disabled']:
                            config['disabled'].remove('forward_shading')
                        if 'forward_shading' not in config['enabled']:
                            config['enabled'].append('forward_shading')
                    if data == 'OFF':
                        if 'forward_shading' not in config['disabled']:
                            config['disabled'].append('forward_shading')
                        if 'forward_shading' in config['enabled']:
                            config['enabled'].remove('forward_shading')

            with open("{0}/Engine/Render/config/plugins.yaml".format(self.game_dir), 'w') as f:
                f.write(rp_yaml.safe_dump(config, default_flow_style=False))

    def save_motion_blur_value(self, data):
        if data and isinstance(data, str):
            with open("{0}/Engine/Render/config/plugins.yaml".format(self.game_dir), 'r') as f:
                config = rp_yaml.safe_load(f)

                if config.get('disabled') and config.get('enabled'):
                    if data == 'ON':
                        if 'motion_blur' in config['disabled']:
                            config['disabled'].remove('motion_blur')
                        if 'motion_blur' not in config['enabled']:
                            config['enabled'].append('motion_blur')
                    if data == 'OFF':
                        if 'motion_blur' not in config['disabled']:
                            config['disabled'].append('motion_blur')
                        if 'motion_blur' in config['enabled']:
                            config['enabled'].remove('motion_blur')

            with open("{0}/Engine/Render/config/plugins.yaml".format(self.game_dir), 'w') as f:
                f.write(rp_yaml.safe_dump(config, default_flow_style=False))

    def save_pssm_value(self, data):
        if data and isinstance(data, str):
            with open("{0}/Engine/Render/config/plugins.yaml".format(self.game_dir), 'r') as f:
                config = rp_yaml.safe_load(f)

                if config.get('disabled') and config.get('enabled'):
                    if data == 'ON':
                        if 'pssm' in config['disabled']:
                            config['disabled'].remove('pssm')
                        if 'pssm' not in config['enabled']:
                            config['enabled'].append('pssm')
                    if data == 'OFF':
                        if 'pssm' not in config['disabled']:
                            config['disabled'].append('pssm')
                        if 'pssm' in config['enabled']:
                            config['enabled'].remove('pssm')

            with open("{0}/Engine/Render/config/plugins.yaml".format(self.game_dir), 'w') as f:
                f.write(rp_yaml.safe_dump(config, default_flow_style=False))

    def save_scattering_value(self, data):
        if data and isinstance(data, str):
            with open("{0}/Engine/Render/config/plugins.yaml".format(self.game_dir), 'r') as f:
                config = rp_yaml.safe_load(f)

                if config.get('disabled') and config.get('enabled'):
                    if data == 'ON':
                        if 'scattering' in config['disabled']:
                            config['disabled'].remove('scattering')
                        if 'scattering' not in config['enabled']:
                            config['enabled'].append('scattering')
                    if data == 'OFF':
                        if 'scattering' not in config['disabled']:
                            config['disabled'].append('scattering')
                        if 'scattering' in config['enabled']:
                            config['enabled'].remove('scattering')

            with open("{0}/Engine/Render/config/plugins.yaml".format(self.game_dir), 'w') as f:
                f.write(rp_yaml.safe_dump(config, default_flow_style=False))

    def save_skin_shading_value(self, data):
        if data and isinstance(data, str):
            with open("{0}/Engine/Render/config/plugins.yaml".format(self.game_dir), 'r') as f:
                config = rp_yaml.safe_load(f)

                if config.get('disabled') and config.get('enabled'):
                    if data == 'ON':
                        if 'skin_shading' in config['disabled']:
                            config['disabled'].remove('skin_shading')
                        if 'skin_shading' not in config['enabled']:
                            config['enabled'].append('skin_shading')
                    if data == 'OFF':
                        if 'skin_shading' not in config['disabled']:
                            config['disabled'].append('skin_shading')
                        if 'skin_shading' in config['enabled']:
                            config['enabled'].remove('skin_shading')

            with open("{0}/Engine/Render/config/plugins.yaml".format(self.game_dir), 'w') as f:
                f.write(rp_yaml.safe_dump(config, default_flow_style=False))

    def save_sky_ao_value(self, data):
        if data and isinstance(data, str):
            with open("{0}/Engine/Render/config/plugins.yaml".format(self.game_dir), 'r') as f:
                config = rp_yaml.safe_load(f)

                if config.get('disabled') and config.get('enabled'):
                    if data == 'ON':
                        if 'sky_ao' in config['disabled']:
                            config['disabled'].remove('sky_ao')
                        if 'sky_ao' not in config['enabled']:
                            config['enabled'].append('sky_ao')
                    if data == 'OFF':
                        if 'sky_ao' not in config['disabled']:
                            config['disabled'].append('sky_ao')
                        if 'sky_ao' in config['enabled']:
                            config['enabled'].remove('sky_ao')

            with open("{0}/Engine/Render/config/plugins.yaml".format(self.game_dir), 'w') as f:
                f.write(rp_yaml.safe_dump(config, default_flow_style=False))

    def save_smaa_value(self, data):
        if data and isinstance(data, str):
            with open("{0}/Engine/Render/config/plugins.yaml".format(self.game_dir), 'r') as f:
                config = rp_yaml.safe_load(f)

                if config.get('disabled') and config.get('enabled'):
                    if data == 'ON':
                        if 'smaa' in config['disabled']:
                            config['disabled'].remove('smaa')
                        if 'smaa' not in config['enabled']:
                            config['enabled'].append('smaa')
                    if data == 'OFF':
                        if 'smaa' not in config['disabled']:
                            config['disabled'].append('smaa')
                        if 'smaa' in config['enabled']:
                            config['enabled'].remove('smaa')

            with open("{0}/Engine/Render/config/plugins.yaml".format(self.game_dir), 'w') as f:
                f.write(rp_yaml.safe_dump(config, default_flow_style=False))

    def save_ssr_value(self, data):
        if data and isinstance(data, str):
            with open("{0}/Engine/Render/config/plugins.yaml".format(self.game_dir), 'r') as f:
                config = rp_yaml.safe_load(f)

                if config.get('disabled') and config.get('enabled'):
                    if data == 'ON':
                        if 'ssr' in config['disabled']:
                            config['disabled'].remove('ssr')
                        if 'ssr' not in config['enabled']:
                            config['enabled'].append('ssr')
                    if data == 'OFF':
                        if 'ssr' not in config['disabled']:
                            config['disabled'].append('ssr')
                        if 'ssr' in config['enabled']:
                            config['enabled'].remove('ssr')

            with open("{0}/Engine/Render/config/plugins.yaml".format(self.game_dir), 'w') as f:
                f.write(rp_yaml.safe_dump(config, default_flow_style=False))

    def save_volumetrics_value(self, data):
        if data and isinstance(data, str):
            with open("{0}/Engine/Render/config/plugins.yaml".format(self.game_dir), 'r') as f:
                config = rp_yaml.safe_load(f)

                if config.get('disabled') and config.get('enabled'):
                    if data == 'ON':
                        if 'volumetrics' in config['disabled']:
                            config['disabled'].remove('volumetrics')
                        if 'volumetrics' not in config['enabled']:
                            config['enabled'].append('volumetrics')
                    if data == 'OFF':
                        if 'volumetrics' not in config['disabled']:
                            config['disabled'].append('volumetrics')
                        if 'volumetrics' in config['enabled']:
                            config['enabled'].remove('volumetrics')

            with open("{0}/Engine/Render/config/plugins.yaml".format(self.game_dir), 'w') as f:
                f.write(rp_yaml.safe_dump(config, default_flow_style=False))
