@echo off
echo "Checking VS C++ Build Tools"
setlocal enabledelayedexpansion

set found_one=0

:: Query the registry and store the output in a temporary file
reg query "HKLM\SOFTWARE\Microsoft\VisualStudio" > temp.txt

:: Read the temporary file line by line
for /f "tokens=*" %%A in (temp.txt) do (
    set "line=%%A"
    :: Isolate the last four characters
    set "lastFour=!line:~-4!"
    :: Remove the last two characters
    set "trimmed=!lastFour:~0,-2!"

    echo !trimmed! | findstr /r "^[A-Za-z][A-Za-z]" >nul
    if !errorlevel! equ 1 (
        if !trimmed! geq 14 (
            set found_one=1
        )
    )
)

:: If VS C++ 14 or higher not found, download it
if !found_one! neq 1 (
    echo "VS C++ Build Tools (14.0 or greater) not found."
    powershell -Command "Invoke-WebRequest https://aka.ms/vs/17/release/vs_BuildTools.exe -OutFile vs_BuildTools.exe"
    start "" /w vs_BuildTools.exe --norestart --passive --downloadThenInstall --includeRecommended --add Microsoft.VisualStudio.Workload.NativeDesktop --add Microsoft.VisualStudio.Workload.VCTools --add Microsoft.VisualStudio.Workload.MSBuildTools
    del "vs_BuildTools.exe"
    echo WAIT until the installer is finished then press ENTER to continue.
    pause
) else (
    echo "Sufficient VS C++ Build Tools found"
)


:: Clean up
del temp.txt
endlocal
