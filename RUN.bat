@echo off

if not defined VIRTUAL_ENV (
    call .venv/Scripts/activate.bat
)

call py scripts/persistent_icon.py

if defined VIRTUAL_ENV (
    deactivate
)