@echo off

:: Make sure VS C++ 14.0 or higher is installed
call vs_buildtools_installer.bat

:: Make and activate virtual enviornment
py -m venv .venv
call ../.venv/Scripts/activate.bat

py -m pip install --upgrade pip

:: Pip install all the deps in deps.txt
for /F "tokens=*" %%A in (scripts/deps.txt) do call pip install --force-reinstall %%A

call RUN.bat

if defined VIRTUAL_ENV (
    deactivate
)