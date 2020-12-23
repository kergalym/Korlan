#!/bin/bash
  cp requirements_lin.txt requirements.txt
. venv3*/bin/activate && python3 setup_lin.py build_apps bdist_apps && deactivate
  cp requirements_win.txt requirements.txt
. venv3*/bin/activate && python3 setup_win.py build_apps bdist_apps && deactivate

