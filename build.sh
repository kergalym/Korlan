#!/bin/bash
cp requirements_lin.txt requirements.txt
. venv3*/bin/activate
python3 setup_lin.py build_apps bdist_apps
cd build/manylinux1_x86_64/
multify -cv -f GameData.mf Assets Settings Engine
deactivate

# cp requirements_win.txt requirements.txt
# . venv3*/bin/activate
# python3 setup_win.py build_apps bdist_apps
# cd build/win_amd64/
# multify -cv -f GameData.mf Assets Settings Engine
# deactivate

rm -rf Assets/Actors
rm -rf Assets/Animations
rm -rf Assets/Colliders
rm -rf Assets/Inventory
rm -rf Assets/Items
rm -rf Assets/Levels
rm -rf Assets/Menu
rm -rf Assets/Particles
rm -rf Assets/Sounds
rm -rf Assets/Videos
rm -rf Assets/Weapons
rm -rf Engine/Shaders
rm -rf Settings


cd ../../

