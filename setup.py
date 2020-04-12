from setuptools import setup

setup(
    name="Korlan",
    version='0.0.1',
    include_package_data=True,
    package_dir={'': 'Engine/Render/'},
    packages=['Engine.Render.rpcore.native.GPUCommand',
              'Engine.Render.rpcore.native.GPUCommandList',
              'Engine.Render.rpcore.native.IESDataset',
              'Engine.Render.rpcore.native.InternalLightManager',
              'Engine.Render.rpcore.native.PointLight',
              'Engine.Render.rpcore.native.ShadowManager',
              'Engine.Render.rpcore.native.SpotLight',
              'Engine.Render.rpcore.native.TagStateManager',
              'Engine.Render.rpcore.native.native_',
              'cyaml', 'dumper', 'error', 'events',
              'loader', 'nodes', 'ordereddict',
              'Engine.Render.rpplugins.env_probes.environment_probe',
              'thread', 'tokens', 'yaml_py2.SafeLoader',
              'yaml_py2.YAMLError', 'yaml_py2.load',
              'yaml_py3.SafeLoader', 'yaml_py3.YAMLError', 'yaml_py3.load'],
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
                'Engine/Render/**/*.txo',
                'Engine/Render/**/*.yaml',
                'Engine/Render/**/*.frag.glsl',
                'Engine/Render/**/*.vert.glsl',
                'Engine/Shaders/**/*.frag',
                'Engine/Shaders/**/*.vert',
            ],
            'gui_apps': {
                'Korlan': 'main.py',
            },
            'platforms': [
                'manylinux1_x86_64',
                'win_amd64',
            ],
            'plugins': [
                'pandagl',
                'p3openal_audio',
                'p3ffmpeg',
                'p3ptloader',
            ],
        }
    }
)
