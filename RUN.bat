@echo off

if not exist .venv/ (
    call scripts/install_deps.bat
)

if not defined VIRTUAL_ENV (
    call .venv/Scripts/activate.bat
)

start /B pythonw scripts/persistent_icon.py
echo "GIF_Cap taskbar icon opened"

if defined VIRTUAL_ENV (
    deactivate
)