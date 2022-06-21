#!/bin/bash
cd $(pwd)
. venv3*/bin/activate && python3.9 main.py && deactivate
