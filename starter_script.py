import subprocess
import os

cwd = os.getcwd()
creationflags=0

if os.path.isfile(cwd + "/GIF_Cap.py"):
    script_file = cwd + "/GIF_Cap.py"
if os.path.isfile(cwd + "/GIF_Cap.pyw"):
    script_file = cwd + "/GIF_Cap.pyw"
    creationflags=subprocess.CREATE_NO_WINDOW

python_bin = cwd + "/.venv/Scripts/python.exe"

subprocess.Popen([python_bin, script_file], creationflags=creationflags)