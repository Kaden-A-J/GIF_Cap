import subprocess
import os

cwd = os.getcwd()
script_file = cwd + "/GIF_Cap.py"
python_bin = cwd + "/.venv/Scripts/python.exe"

subprocess.Popen([python_bin, script_file])