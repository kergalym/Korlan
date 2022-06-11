#!/bin/bash
export PROJDIR="/home/galym/Korlan"
export BUILDDIR=$PROJDIR"/build/manylinux1_x86_64"

# export PYTHONPATH=$PROJDIR"/venv3.7/built"
# export LD_LIBRARY_PATH=$PROJDIR"/venv3.7/built/lib"

cp requirements_lin.txt requirements.txt
. venv3*/bin/activate
python3 setup_lin.py build_apps # bdist_apps
cd $BUILDDIR
multify -c -f GameData.mf Assets Settings Engine
deactivate

rm -rf $BUILDDIR/Assets/Actors
rm -rf $BUILDDIR/Assets/Animations
rm -rf $BUILDDIR/Assets/Colliders
rm -rf $BUILDDIR/Assets/Inventory
rm -rf $BUILDDIR/Assets/Items
rm -rf $BUILDDIR/Assets/Levels
rm -rf $BUILDDIR/Assets/Menu
rm -rf $BUILDDIR/Assets/Particles
rm -rf $BUILDDIR/Assets/Sounds
rm -rf $BUILDDIR/Assets/Videos
rm -rf $BUILDDIR/Assets/Weapons
rm -rf $BUILDDIR/Engine/Shaders
rm -rf $BUILDDIR/Settings

cd $PROJDIR