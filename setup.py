from setuptools import setup

setup(
    name="Korlan",
    include_package_data=True,
    options={
        'build_apps': {
            'include_patterns': [
                'Assets/**/tex/*.png',
                'Assets/**/tex/*.jpg',
                'Assets/**/*.egg',
                'Configs/Language/*.json',
                'Configs/Keyboard/*.json',
                'Configs/Mice/*.json',
                'Settings/UI/*.json',
                'Settings/UI/ui_tex/*.png',
                'Settings/UI/Open_Sans/*.ttf',
                'Settings/UI/Open_Sans/*.txt',
                'Settings/Sound/*.ogg',
                'Engine/Shaders/**/*.frag',
                'Engine/Shaders/**/*.vert',
                'RenderPipeline/**/*',
            ],
            'gui_apps': {
                'Korlan': 'Korlan.py',
            },
            'platforms': [
                'manylinux1_x86_64',
            ],
            'plugins': [
                'pandagl',
                'p3openal_audio',
                'p3ptloader',
            ],
        }
    }
)
