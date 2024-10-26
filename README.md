A small Python script that captures a .gif of a selected area.

Output is saved as capture.gif in the root folder.

# How to run:
Download project as .zip and extract.

Execute RUN.bat

- If dependencies fail the install can be retried by deleting .venv

This opens a taskbar icon. Either click on it or press CRTL+SHIFT+PRINTSCREEN with it running to start capturing a gif.


# Settings are currently found near the top of GIF_Cap.pyw:
- MS_TO_RUN: the milliseconds to capture the gif
- FPS: the initial frames per second

# Dependencies (automatically handled):
- Python
- PyQt6
  - Visual Studio C++ Build Tools (14.0 or greater)
- PIL
- numpy
- setuptools
- pystray
- keyboard
