# GIF_Cap needs to be started from this file to use the virtual enviornment populated with the deps.
# If you manually install all the deps to your global Python env you can run it directly.

import subprocess
import os


creationflags=0

# If .py extension: make a console, otherwise don't.
if os.path.isfile("./scripts/GIF_Cap.py"):
    script_file = "./scripts/GIF_Cap.py"
elif os.path.isfile("./scripts/GIF_Cap.pyw"):
    script_file = "./scripts/GIF_Cap.pyw"
    creationflags=subprocess.CREATE_NO_WINDOW

# Check both directories incase user ran scripts directly
elif os.path.isfile("./GIF_Cap.py"):
    script_file = "./GIF_Cap.py"
elif os.path.isfile("./GIF_Cap.pyw"):
    script_file = "./GIF_Cap.pyw"
    creationflags=subprocess.CREATE_NO_WINDOW
else:
    print('starter_script.py not found')
    quit()


python_bin = ""
if os.path.isdir("./.venv"):
    python_bin = "./.venv/Scripts/python.exe"
elif os.path.isdir("./../.venv"):
    python_bin = "./../.venv/Scripts/python.exe"
else:
    print('virtual enviornment not found')
    quit()


subprocess.Popen([python_bin, script_file], creationflags=creationflags)