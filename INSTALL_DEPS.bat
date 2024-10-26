@echo off

call vs_buildtools_installer.bat

py -m venv .venv
call .venv/Scripts/activate.bat

py -m pip install --upgrade pip
pip install --upgrade setuptools

pip install Pillow
pip install PyQt6
pip install numpy

call RUN.bat

deactivate