from setuptools import setup

setup(
    name="Korlan",
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
                'Settings/UI/ui_tex/**/*.png',
                'Settings/UI/ui_tex/*.png',
                'Settings/UI/**/*.ttf',
                'Settings/UI/**/*.txt',
                'Settings/Sound/*.ogg',
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
                'p3ptloader',
            ],
        }
    }
)
