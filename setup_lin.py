from setuptools import setup

setup(
    name="Korlan",
    version='0.1.1',
    include_package_data=True,
    options={
        'build_apps': {
            'include_patterns': [
                'Assets/**/*',
                'Assets/**/tex/*',
                'Configs/Language/*.json',
                'Configs/Keyboard/*.json',
                'Configs/Mice/*.json',
                'Settings/UI/*.json',
                'Settings/UI/ui_tex/**/*',
                'Settings/UI/**/*.ttf',
                'Settings/UI/**/*.txt',
                'Settings/UI/**/*.egg*',
                'Settings/Sound/*.ogg',
                'Engine/Renderer/**/*.png',
                'Engine/Renderer/**/*.jpg',
                'Engine/Renderer/data/**/**/**/*',
                'Engine/Renderer/**/*.yaml',
                'Engine/Renderer/**/*.flag',
                'Engine/Renderer/**/*.prc',
                'Engine/Renderer/**/*.txt',
                'Engine/Renderer/**/*.yaml',
                'Engine/Renderer/**/*.bam',
                'Engine/Renderer/**/*.ttf',
                'Engine/Renderer/**/*.ies',
                'Engine/Renderer/**/*.txo',
                'Engine/Renderer/**/*.txo.*',
                'Engine/Renderer/**/*.glsl',
                'Engine/Renderer/**/*.compute',
                'Engine/Shaders/**/*.*',
                'tex/*.*',
            ],
            # Workaround for
            # AssertionError: macos_main_app must be defined if more than one gui_app is defined
            # since we don't have support for macos
            'macos_main_app': 'Korlan',
            'gui_apps': {
                'Korlan': 'main.py',
            },
            "icons": {
                "Korlan": ["icon-256.png", "icon-128.png", "icon-48.png", "icon-32.png", "icon-16.png"],
            },
            'platforms': [
                'manylinux1_x86_64',
            ],
            'include_modules': {'*': ['Engine.Renderer.rpcore.native.GPUCommand',
                                      'Engine.Renderer.rpcore.native.GPUCommandList',
                                      'Engine.Renderer.rpcore.native.IESDataset',
                                      'Engine.Renderer.rpcore.native.InternalLightManager',
                                      'Engine.Renderer.rpcore.native.PointLight',
                                      'Engine.Renderer.rpcore.native.ShadowManager',
                                      'Engine.Renderer.rpcore.native.SpotLight',
                                      'Engine.Renderer.rpcore.native.TagStateManager',
                                      'Engine.Renderer.rpcore.native.native_',
                                      'Engine.Renderer.rpcore.native.PSSMCameraRig',
                                      'Engine.Renderer.rplibs.yaml_py2.SafeLoader',
                                      'Engine.Renderer.rplibs.yaml_py2.YAMLError',
                                      'Engine.Renderer.rplibs.yaml_py2.load',
                                      'Engine.Renderer.rplibs.yaml_py3.SafeLoader',
                                      'Engine.Renderer.rplibs.yaml_py3.YAMLError',
                                      'Engine.Renderer.rplibs.yaml_py3.load',
                                      'cyaml',
                                      'Engine.Renderer.rplibs.yaml.yaml_py3.error',
                                      'Engine.Renderer.rplibs.yaml.yaml_py3.dumper',
                                      'Engine.Renderer.rplibs.yaml.error',
                                      'Engine.Renderer.rplibs.yaml.yaml_py3.events',
                                      'Engine.Renderer.rplibs.yaml.yaml_py3.loader',
                                      'Engine.Renderer.rplibs.yaml.yaml_py3.nodes',
                                      'ordereddict',
                                      'Engine.Renderer.rpplugins.ao',
                                      'Engine.Renderer.rpplugins.ao.plugin',
                                      'Engine.Renderer.rpplugins.bloom',
                                      'Engine.Renderer.rpplugins.bloom.plugin',
                                      'Engine.Renderer.rpplugins.clouds',
                                      'Engine.Renderer.rpplugins.clouds.plugin',
                                      'Engine.Renderer.rpplugins.color_correction',
                                      'Engine.Renderer.rpplugins.color_correction.plugin',
                                      'Engine.Renderer.rpplugins.dof',
                                      'Engine.Renderer.rpplugins.dof.plugin',
                                      'Engine.Renderer.rpplugins.env_probes',
                                      'Engine.Renderer.rpplugins.env_probes.environment_probe',
                                      'Engine.Renderer.rpplugins.env_probes.plugin',
                                      'Engine.Renderer.rpplugins.forward_shading',
                                      'Engine.Renderer.rpplugins.forward_shading.plugin',
                                      'Engine.Renderer.rpplugins.fxaa',
                                      'Engine.Renderer.rpplugins.fxaa.plugin',
                                      'Engine.Renderer.rpplugins.motion_blur',
                                      'Engine.Renderer.rpplugins.motion_blur.plugin',
                                      'Engine.Renderer.rpplugins.pssm',
                                      'Engine.Renderer.rpplugins.pssm.plugin',
                                      'Engine.Renderer.rpplugins.scattering',
                                      'Engine.Renderer.rpplugins.scattering.plugin',
                                      'Engine.Renderer.rpplugins.skin_shading',
                                      'Engine.Renderer.rpplugins.skin_shading.plugin',
                                      'Engine.Renderer.rpplugins.sky_ao',
                                      'Engine.Renderer.rpplugins.sky_ao.plugin',
                                      'Engine.Renderer.rpplugins.smaa',
                                      'Engine.Renderer.rpplugins.smaa.plugin',
                                      'Engine.Renderer.rpplugins.ssr',
                                      'Engine.Renderer.rpplugins.ssr.plugin',
                                      'Engine.Renderer.rpplugins.volumetrics',
                                      'Engine.Renderer.rpplugins.volumetrics.plugin',
                                      'Engine.Renderer.rpplugins.vxgi',
                                      'Engine.Renderer.rpplugins.vxgi.plugin',
                                      'thread',
                                      'Engine.Renderer.rplibs.yaml.yaml_py3.tokens',
                                      'Engine.Renderer.rplibs.yaml.yaml_py3.load'
                                      ]},
            'plugins': [
                'pandagl',
                'p3openal_audio',
                'p3ffmpeg',
                'p3ptloader',
            ],
        }
    }
)
