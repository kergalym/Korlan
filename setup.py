from setuptools import setup

setup(
    name="Korlan",
    options={
        'build_apps': {
            'include_patterns': [
                'Assets/*',
                'Configs/*',
                'Engine/*',
                'RenderPipeline/*',
                'Settings/*',
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
            ],
        }
    }
)
