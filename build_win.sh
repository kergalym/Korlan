#!/bin/bash
export PROJDIR="/home/galym/Korlan"
export BUILDDIR="build"
export DISTDIR=$PROJDIR/$BUILDDIR/"win_amd64"

# Purge wheels cache
rm -rf $PROJDIR/$BUILDDIR/"__whl_cache__/"

# Prepare requirements
cp requirements_win.txt requirements.txt

# Enter to virtualenv
. venv3*/bin/activate

# build the game
python3 setup_win.py build_apps # bdist_apps

cd $DISTDIR

# Pack game files into single multifile
multify -c -f GameData.mf Assets Settings Engine

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
rm -rf $DISTDIR/Settings

# Return to project directory
cd $PROJDIR
