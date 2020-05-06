from setuptools import setup, find_packages

setup(
    name="Korlan",
    version='0.0.1',
    include_package_data=True,
    options={
        'build_apps': {
            'include_patterns': [
                # 'Assets/**/*',
                'Assets/**/tex/*',
                'Configs/Language/*.json',
                'Configs/Keyboard/*.json',
                'Configs/Mice/*.json',
                'Settings/UI/*.json',
                'Settings/UI/ui_tex/**/*.png',
                'Settings/UI/ui_tex/*.png',
                'Settings/UI/**/*.ttf',
                'Settings/UI/**/*.txt',
                'Settings/Sound/*.ogg',
                'Engine/Render/**/*.png',
                'Engine/Render/**/*.jpg',
                'Engine/Render/data/**/**/**/*',
                'Engine/Render/**/*.yaml',
                'Engine/Render/**/*.flag',
                'Engine/Render/**/**/**/**/*.prc',
                'Engine/Render/**/**/**/**/*.txt',
                'Engine/Render/**/**/**/**/*.yaml',
                'Engine/Render/**/**/**/**/*.bam',
                'Engine/Render/**/**/**/**/*.ttf',
                'Engine/Render/**/**/**/**/*.ies',
                'Engine/Render/**/**/**/**/*.txo',
                'Engine/Render/**/**/**/**/*.txo.*',
                'Engine/Render/**/**/**/**/*.glsl',
                'Engine/Shaders/**/*.frag',
                'Engine/Shaders/**/*.vert',
            ],
            # Workaround for
            # AssertionError: macos_main_app must be defined if more than one gui_app is defined
            # since we don't have support for macos
            'macos_main_app': 'Korlan',
            'gui_apps': {
                'Korlan': 'main.py',
            },
            'platforms': [
                'manylinux1_x86_64',
                'win_amd64',
            ],
            'include_modules': {'*': ['Engine.Render.rpcore.native.GPUCommand',
                                      'Engine.Render.rpcore.native.GPUCommandList',
                                      'Engine.Render.rpcore.native.IESDataset',
                                      'Engine.Render.rpcore.native.InternalLightManager',
                                      'Engine.Render.rpcore.native.PointLight',
                                      'Engine.Render.rpcore.native.ShadowManager',
                                      'Engine.Render.rpcore.native.SpotLight',
                                      'Engine.Render.rpcore.native.TagStateManager',
                                      'Engine.Render.rpcore.native.native_',
                                      'Engine.Render.rplibs.yaml.yaml_py3.error',
                                      'cyaml',
                                      'Engine.Render.rplibs.yaml.yaml_py3.dumper',
                                      'Engine.Render.rplibs.yaml.error',
                                      'Engine.Render.rplibs.yaml.yaml_py3.events',
                                      'Engine.Render.rplibs.yaml.yaml_py3.loader',
                                      'Engine.Render.rplibs.yaml.yaml_py3.nodes',
                                      'ordereddict',
                                      'Engine.Render.rpplugins.ao',
                                      'Engine.Render.rpplugins.ao.plugin',
                                      'Engine.Render.rpplugins.bloom',
                                      'Engine.Render.rpplugins.bloom.plugin',
                                      'Engine.Render.rpplugins.clouds',
                                      'Engine.Render.rpplugins.clouds.plugin',
                                      'Engine.Render.rpplugins.color_correction',
                                      'Engine.Render.rpplugins.color_correction.plugin',
                                      'Engine.Render.rpplugins.dof',
                                      'Engine.Render.rpplugins.dof.plugin',
                                      'Engine.Render.rpplugins.env_probes',
                                      'Engine.Render.rpplugins.env_probes.environment_probe',
                                      'Engine.Render.rpplugins.env_probes.plugin',
                                      'Engine.Render.rpplugins.forward_shading',
                                      'Engine.Render.rpplugins.forward_shading.plugin',
                                      'Engine.Render.rpplugins.fxaa',
                                      'Engine.Render.rpplugins.fxaa.plugin',
                                      'Engine.Render.rpplugins.motion_blur',
                                      'Engine.Render.rpplugins.motion_blur.plugin',
                                      'Engine.Render.rpplugins.pssm',
                                      'Engine.Render.rpplugins.pssm.plugin',
                                      'Engine.Render.rpplugins.scattering',
                                      'Engine.Render.rpplugins.scattering.plugin',
                                      'Engine.Render.rpplugins.skin_shading',
                                      'Engine.Render.rpplugins.skin_shading.plugin',
                                      'Engine.Render.rpplugins.sky_ao',
                                      'Engine.Render.rpplugins.sky_ao.plugin',
                                      'Engine.Render.rpplugins.smaa',
                                      'Engine.Render.rpplugins.smaa.plugin',
                                      'Engine.Render.rpplugins.ssr',
                                      'Engine.Render.rpplugins.ssr.plugin',
                                      'Engine.Render.rpplugins.volumetrics',
                                      'Engine.Render.rpplugins.volumetrics.plugin',
                                      'Engine.Render.rpplugins.vxgi',
                                      'Engine.Render.rpplugins.vxgi.plugin',
                                      'thread',
                                      'Engine.Render.rplibs.yaml.yaml_py3.tokens',
                                      'Engine.Render.rplibs.yaml.yaml_py3.load']},
            'plugins': [
                'pandagl',
                'p3openal_audio',
                'p3ffmpeg',
                'p3ptloader',
            ],
        }
    }
)
