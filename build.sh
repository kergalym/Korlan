#!/bin/bash
export PROJDIR="/home/galym/Korlan"
export BUILDDIR="build"
export DISTDIR=$PROJDIR/$BUILDDIR/"manylinux1_x86_64"

# export PYTHONPATH=$PROJDIR"/venv3.7/built"
# export LD_LIBRARY_PATH=$PROJDIR"/venv3.7/built/lib"
# export PATH=$PROJDIR"/venv3.7/built"/bin:$PATH

# Purge wheels cache
rm -rf $PROJDIR/$BUILDDIR/"__whl_cache__/"

# Prepare requirements
cp requirements_lin.txt requirements.txt

# Enter to virtualenv
. venv3*/bin/activate

# build the game
venv3.7/bin/python3 setup_lin.py build_apps # bdist_apps

cd $DISTDIR

# Pack game files into single multifile
multify -c -f GameData.mf Assets Engine

# Exit from virtualenv
deactivate

# Purge unused asset files, we packed them already
rm -rf $DISTDIR/Assets/Actors
rm -rf $DISTDIR/Assets/Animations
rm -rf $DISTDIR/Assets/Colliders
rm -rf $DISTDIR/Assets/Inventory
rm -rf $DISTDIR/Assets/ChestInventory
rm -rf $DISTDIR/Assets/Items
rm -rf $DISTDIR/Assets/Levels
rm -rf $DISTDIR/Assets/Menu
rm -rf $DISTDIR/Assets/Particles
rm -rf $DISTDIR/Assets/Sounds
rm -rf $DISTDIR/Assets/Videos
rm -rf $DISTDIR/Assets/Weapons
rm -rf $DISTDIR/Engine/Shaders
# rm -rf $DISTDIR/Settings

# Return to project directory
cd $PROJDIR

