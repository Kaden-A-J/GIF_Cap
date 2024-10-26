
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

#✅ Stitch saved images together into a GIF
#✅ - Save GIF to folder
# - Save GIF to clipboard

from PyQt6.QtGui import QKeyEvent, QMouseEvent, QRegion
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QWidget
from PyQt6.QtCore import QPointF, QRectF, Qt, QTimer, pyqtSignal, pyqtSlot, QObject
from PIL import ImageGrab
import numpy as np
import sys, time


MONITOR_RES = (3840, 2160)
MS_TO_RUN = 10000
FPS = 10


class Snipper(QObject):
    cap_pic_exit = pyqtSignal()
    close_window = pyqtSignal()
    def __init__(self, monitor_res, ms_to_run, fps, filename='capture'):
        super().__init__()

        self.MAX_LAGGED_FRAMES = 2

        self.monitor_scale = (monitor_res[0]/1920, monitor_res[1]/1080)
        self.fps_ms = int(1000/fps)
        self.fps = fps
        self.ms_to_run = ms_to_run
        self.total_frames = int(ms_to_run / 1000 * fps)
        self.filename = filename
        self.capture_rect = QRectF()
        self.snips = []
        self.custom_bbox = ()
        self.times_to_snip = ()
        self.start_ms = 0
        self.snip_counter = 0
        self.lagged_frames = 0

        self.cap_timer = QTimer()
        self.cap_timer.setSingleShot(True)

        self.cap_timer.timeout.connect(self.capture_pictures)
        self.cap_pic_exit.connect(self.save_pictures)


    def start_capture_pictures(self, capture_rect):
        # PIL's ImageGrab doesn't auto-scale to your current monitor's rez and just treat it
        # like 1920x1080, unlike PyQt6, so need to manually scale the selection zone.
        self.custom_bbox = (capture_rect.x() * self.monitor_scale[0]
                    , capture_rect.y() * self.monitor_scale[1]
                    , (capture_rect.x() + capture_rect.width()) * self.monitor_scale[0]
                    , (capture_rect.y() + capture_rect.height()) * self.monitor_scale[1])

        self.snip_counter = 0
        self.start_ms = self.get_ms()

        # the time each snip should take place so we can adjust the pause between depending on snip speed
        self.times_to_snip = np.linspace(self.start_ms, self.start_ms + self.ms_to_run, self.total_frames)
        self.times_to_snip = self.times_to_snip[1:] # pop first value so we always look at how long until the next frame is
        self.capture_pictures()


    def capture_pictures(self):
        screenshot = ImageGrab.grab(bbox=self.custom_bbox)
        self.snips.append(screenshot)
        self.snip_counter += 1

        # if there's still time left, take another snip, otherwise break out
        if self.snip_counter < self.total_frames:
            if self.snip_counter == self.total_frames - 1: # just take a guess on the last one
                time_to_next_snip = self.fps_ms

            else: # how much time until the next snip should be taken
                time_to_next_snip = max(0, self.times_to_snip[0] - self.get_ms())
                # pop off the first value so we don't have to keep track of a potentially changing index if we change the fps
                self.times_to_snip = self.times_to_snip[1:]
            
            # if we're falling behind drop the fps until we catch up
            if time_to_next_snip == 0:
                self.lagged_frames += 1
                if self.lagged_frames >= self.MAX_LAGGED_FRAMES:
                    self.recalc_fps(self.fps - 1)
                    self.lagged_frames = 0
            else:
                self.lagged_frames = 0

            print(self.snip_counter, time_to_next_snip)
            self.cap_timer.start(int(time_to_next_snip))
        else:
            self.cap_pic_exit.emit()


    def recalc_fps(self, target_fps):
        self.fps = target_fps
        self.fps_ms = int(1000/target_fps)
        self.total_frames = int(self.ms_to_run / 1000 * target_fps)
        self.times_to_snip = np.linspace(self.get_ms(), self.get_ms() + self.ms_to_run, self.total_frames - self.snip_counter)
        self.times_to_snip = self.times_to_snip[1:] # pop first value so we always look at how long until the next frame is


    def save_pictures(self):
        print('saving')
        print('ending fps: ' + str(self.fps))
        print(len(self.snips))
        self.snips[0].save(
            self.filename + '.gif',
            save_all=True,
            append_images=self.snips[1:],
            optimize=False,
            duration=self.fps_ms,
            loop=0
        )
        # idx = 0
        # for snip in self.snips:
        #     snip.save('snip_' + str(idx) + '.png')
        #     idx += 1
        print('saved')
        self.close_window.emit()


    def get_ms(self):
        return time.time_ns() // 1000000


class MainWindow(QMainWindow):
    def __init__(self, snipper):
        super().__init__()

        self.snipper = snipper
        self.snipper.close_window.connect(self.close_window)

        self.setWindowTitle("GIF_Cap")
        self.setGeometry(0, 0, 500, 500)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents, False)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.WindowStaysOnTopHint)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, False)

        self.mouse_down_coords = QPointF(0, 0)
        self.mouse_up_coords = QPointF(0, 0)
        self.selection_rect = QRectF(0, 0, 0, 0)

        self.setStyleSheet("background-color:rgba(0, 0, 0, 40)")


    def close_window(self):
        self.close()

    def keyPressEvent(self, e: QKeyEvent | None) -> None:
        if (e.key() == Qt.Key.Key_Escape):
            self.close_window()


    def mousePressEvent(self, e):
        self.mouse_down_coords = e.pos()


    def mouseReleaseEvent(self, e):
        self.mouse_up_coords = e.pos()
        snipper.start_capture_pictures(self.selection_rect)


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
        empty_region = QRegion(self.geometry(), QRegion.RegionType.Rectangle)
        self.setMask(empty_region.subtracted(mask))
    

app = QApplication(sys.argv)

snipper = Snipper(monitor_res=MONITOR_RES, ms_to_run=MS_TO_RUN, fps=FPS)

window = MainWindow(snipper)
window.showFullScreen()


app.exec()