@echo off

if not exist .venv (
	py -m venv .venv
	call .venv/Scripts/activate.bat

	py -m pip install --upgrade pip
	pip install Pillow
	pip install PyQt6
	pip install numpy
)
else (
	call .venv/Scripts/activate.bat
)


py starter_script.py
deactivate