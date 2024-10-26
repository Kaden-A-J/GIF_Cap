from PIL import Image, ImageDraw
import pystray, keyboard, subprocess, threading
import os.path


SHORTCUT = 'ctrl+shift+print screen'


starter_path = ''
if os.path.isfile('./scripts/starter_script.py'):
    starter_path = './scripts/starter_script.py'
elif os.path.isfile('./starter_script.py'):
    starter_path = './starter_script.py'
else:
    print('starter_script.py not found')
    quit()

# Create placeholder image with a white background and a black square
def create_image():
    width = 64
    height = 64
    image = Image.new('RGB', (width, height), 'white')
    dc = ImageDraw.Draw(image)
    dc.rectangle(
        (width // 2 - 10, height // 2 - 10, width // 2 + 10, height // 2 + 10),
        fill='black')
    return image


def on_activate():
    subprocess.Popen(['python', starter_path])


def setup(icon):
    icon.visible = True
    threading.Thread(target=keyboard.add_hotkey, args=(SHORTCUT, on_activate)).start()


# Create the system tray icon
icon = pystray.Icon('test', create_image(), 'GIF_Cap', menu=pystray.Menu(
    pystray.MenuItem(text="Open", action=on_activate, default=True),
    pystray.MenuItem(text='Quit', action=lambda icon: icon.stop())
))


icon.run(setup)
