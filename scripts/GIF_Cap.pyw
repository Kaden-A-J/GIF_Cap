
#✅ Darken the screen
# - Apply to all screens

#✅ Let user click and drag to select bounding box 
#✅ - Lighten selected area

#✅ Capture picture from bounded area

#✅ Capture a picture (24?) frames a second?  (41.66 ms per frame)
# - Left click selecting makes you click (or shortcut key) a button before capturing starts
# - Right click selecting automatically starts the capture on the selected area
# - Hotkey to stop capturing (Esc?)
#✅ - Save individual images in folder? (Start with lower FPS like 3)
#✅ - Automatically adjust FPS to the maximum someones comp can keep up with based on frame timing

#✅ Stitch saved images together into a GIF
#✅ - Save GIF to folder
# - Save GIF to clipboard

# BUG
# - High framerate playback is a little fast


MS_TO_RUN = 5000
FPS = 10


from PyQt6.QtGui import QKeyEvent, QMouseEvent, QRegion
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtCore import QPointF, QRectF, Qt, QRect
import sys

from CaptureModule import CaptureModule


class MainWindow(QMainWindow):
    def __init__(self, capture_module):
        super().__init__()

        self.capture_module = capture_module
        self.capture_module.close_window.connect(self.close_window)

        self.mouse_down_coords = QPointF(0, 0)
        self.mouse_up_coords = QPointF(0, 0)
        self.selection_rect = QRectF(0, 0, 0, 0)
        self.relative_geom = QRect()

        self.setWindowTitle("GIF_Cap")
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, False)
        self.setStyleSheet("background-color:rgba(0, 0, 0, 40)")


    def close_window(self):
        # Close all the windows on each screen when one is done.
        quit()
        # self.close()


    def keyPressEvent(self, e: QKeyEvent | None) -> None:
        if (e.key() == Qt.Key.Key_Escape):
            self.close_window()


    def mousePressEvent(self, e):
        # can't set this in __init__ for some reason so just set it here
        self.relative_geom = QRect(0, 0, self.geometry().width(), self.geometry().height())

        self.mouse_down_coords = e.pos()


    def mouseReleaseEvent(self, e):
        self.mouse_up_coords = e.pos()
        self.capture_module.start_capture_pictures(self.selection_rect)


    def mouseMoveEvent(self, e: QMouseEvent | None) -> None:
        mouse_move_point = e.pos().toPointF()
        mouse_down_point = self.mouse_down_coords.toPointF()

        # if mouse is right of where initial click is
        if (mouse_move_point.x() - mouse_down_point.x() > 0):
            x = self.mouse_down_coords.x()
            w = mouse_move_point.x() - mouse_down_point.x()
        else: # otherwise change 'initial position' and modify width to be where it originally was
            x = mouse_move_point.x()
            w = mouse_down_point.x() - mouse_move_point.x()

        # if mouse is below of where initial click it
        if (mouse_move_point.y() - mouse_down_point.y() > 0):
            y = self.mouse_down_coords.y()
            h = mouse_move_point.y() - mouse_down_point.y()
        else: # otherwise change 'initial position' and modify height to be where it originally was
            y = mouse_move_point.y()
            h = mouse_down_point.y() - mouse_move_point.y()

        self.selection_rect = QRectF(x, y, w, h)

        mask = QRegion(self.selection_rect.toRect(), QRegion.RegionType.Rectangle)
        empty_region = QRegion(self.relative_geom, QRegion.RegionType.Rectangle)
        self.setMask(empty_region.subtracted(mask))
    

app = QApplication(sys.argv)

windows = []
capture_modules = []
for screen in app.screens():
    monitor_geom = screen.geometry()
    monitor_dpi_scale = screen.devicePixelRatio()
    capture_module = CaptureModule(monitor_geom=monitor_geom, monitor_dpi_scale=monitor_dpi_scale, ms_to_run=MS_TO_RUN, fps=FPS)
    window = MainWindow(capture_module)

    print(screen.size(), screen.devicePixelRatio())

    window.setScreen(screen)
    window.setGeometry(screen.geometry())
    window.showFullScreen()

    windows.insert(-1, window)
    capture_modules.insert(-1, capture_modules)


app.exec()