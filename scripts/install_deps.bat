@echo off
echo "Populating virtual enviornment with deps"

:: Make sure VS C++ 14.0 or higher is installed
call scripts/vs_buildtools_installer.bat

:: Make and activate virtual enviornment
py -m venv .venv

if not defined VIRTUAL_ENV (
call .venv/Scripts/activate.bat
)

if not defined VIRTUAL_ENV (
    echo failed to activate venv
    exit
)

py -m pip install --upgrade pip

:: Pip install all the deps in deps.txt
for /F "tokens=*" %%A in (scripts/deps.txt) do call pip install --force-reinstall %%A

if defined VIRTUAL_ENV (
    deactivate
)

echo "Deps finished installing"