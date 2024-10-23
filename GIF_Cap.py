
#✅ Darken the screen
# - Transparent black image?
# - Apply to all screens

#✅ Let user click and drag to select bounding box 
#✅ - Lighten selected area

#✅ Capture picture from bounded area

# Capture a picture (24?) frames a second?  (41.66 ms per frame)
# - Hotkey to stop capturing (Esc?)
# - Save individual images in folder? (Start with lower FPS like 3)

# Stitch saved images together into a GIF
# - Save GIF to folder
# - Save GIF to clipboard

from PyQt6.QtGui import QKeyEvent, QMouseEvent, QRegion
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt6.QtCore import QPointF, QRectF, Qt
from PIL import ImageGrab
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        
        monitor_res = (3840, 2160)
        self.monitor_x_scale = monitor_res[0]/1920
        self.monitor_y_scale = monitor_res[1]/1080

        self.setWindowTitle("GIF_Cap")
        self.setGeometry(0, 0, 500, 500)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, False)

        self.mouse_down_coords = QPointF(0, 0)
        self.mouse_up_coords = QPointF(0, 0)
        self.box_rect = QRectF(0, 0, 0, 0)

        self.resize_box = QWidget()
        self.resize_box.setStyleSheet("background-color:rgba(0, 0, 0, 0)")
        self.setStyleSheet("background-color:rgba(0, 0, 0, 40)")

        container = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self.resize_box)
        container.setLayout(layout)

        self.setCentralWidget(container)


    def keyPressEvent(self, e: QKeyEvent | None) -> None:
        if (e.key() == Qt.Key.Key_Escape):
            self.close()


    def mousePressEvent(self, e):
        self.mouse_down_coords = e.pos()
        mouse_down_point = self.mouse_down_coords.toPointF()

        self.resize_box.setGeometry(int(mouse_down_point.x()), int(mouse_down_point.y()), 0, 0)
        

    def mouseReleaseEvent(self, e):

        self.mouse_up_coords = e.pos()
        screenshot = ImageGrab.grab(bbox=(self.box_rect.x() * self.monitor_x_scale
                                        , self.box_rect.y() * self.monitor_y_scale
                                        , (self.box_rect.x() + self.box_rect.width()) * self.monitor_x_scale
                                        , (self.box_rect.y() + self.box_rect.height()) * self.monitor_y_scale))
        screenshot.save('test.png')
        
    
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

        self.box_rect = QRectF(x, y, w, h)

        self.resize_box.setGeometry(self.box_rect.toRect())

        mask = QRegion(self.box_rect.toRect(), QRegion.RegionType.Rectangle)
        empty_region = QRegion(self.geometry(), QRegion.RegionType.Rectangle)
        self.setMask(empty_region.subtracted(mask))


app = QApplication(sys.argv)

window = MainWindow()
window.showFullScreen()

app.exec()