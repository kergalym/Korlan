#!/usr/bin/env bash

echo '######################################################'
echo '#                                                    #'
echo "#   Configuring existing virtualenv for PyCharm...   #"
echo '#                                                    #'
echo '######################################################'

echo ""

rm -f $(pwd)/venv3.7/lib/python3.7/site-packages

echo '#######################################################################'
echo '#                                                                     #'
echo "#   Deleted old symlink Korlan//venv3.7/lib/python3.7/site-packages   #"
echo '#                                                                     #'
echo '#######################################################################'

echo ""

ln -s $(pwd)/venv3.7/opt/python-3.7.5/lib/python3.7/site-packages $(pwd)/venv3.7/lib/python3.7/site-packages

echo '######################################################################'
echo '#                                                                    #'
echo "#   Created old symlink Korlan/venv3.7/lib/python3.7/site-packages   #"
echo '#                                                                    #'
echo '######################################################################'

echo ""

echo '############################################################'
echo '#                                                          #'
echo "#   Configuring existing virtualenv for PyCharm is done!   #"
echo '#                                                          #'
echo '############################################################'
