from PyQt6.QtCore import QRectF, QTimer, pyqtSignal, QObject
from PIL import ImageGrab
import numpy as np
import time


class CaptureModule(QObject):
    cap_pic_exit = pyqtSignal()
    close_window = pyqtSignal()
    def __init__(self, monitor_geom, monitor_dpi_scale, ms_to_run=5000, fps=5, filename='capture'):
        super().__init__()

        self.MAX_LAGGED_FRAMES = 2

        self.monitor_geom = monitor_geom
        self.monitor_dpi_scale = monitor_dpi_scale
        self.monitor_scale = (1920/(monitor_geom.width() * monitor_dpi_scale), 1080/(monitor_geom.height() * monitor_dpi_scale))
        self.fps_ms = int(1000/fps)
        self.fps = fps
        self.ms_to_run = ms_to_run
        self.total_frames = int(ms_to_run / 1000 * fps)
        self.filename = filename
        self.capture_rect = QRectF()
        self.snips = []
        self.capture_rect = ()
        self.future_frame_timings = ()
        self.start_ms = 0
        self.frame_counter = 0
        self.lagged_frames = 0
        self.captured_frame_timings = []
        self.last_frame_delay = 0
        self.last_frame_ms = 0

        self.cap_timer = QTimer()
        self.cap_timer.setSingleShot(True)

        self.cap_timer.timeout.connect(self.capture_pictures)
        self.cap_pic_exit.connect(self.save_pictures)


    def start_capture_pictures(self, capture_rect):

        # PIL's ImageGrab doesn't auto-scale to your current monitor's rez and just treat it
        # like 1920x1080, unlike PyQt6, so need to manually scale the selection zone.
        mod_capture_rect = QRectF(capture_rect.x() * self.monitor_dpi_scale
                                  , capture_rect.y() * self.monitor_dpi_scale
                                  , capture_rect.width() * self.monitor_dpi_scale
                                  , capture_rect.height() * self.monitor_dpi_scale)
        
        mod_monitor_geom = QRectF(self.monitor_geom.x() * self.monitor_scale[0]
                                  , self.monitor_geom.y() * self.monitor_scale[1]
                                  , self.monitor_geom.width() * self.monitor_scale[0],
                                  self.monitor_geom.height() * self.monitor_scale[1])
        
        self.capture_rect = (mod_capture_rect.x() + mod_monitor_geom.x()
                    , mod_capture_rect.y() + mod_monitor_geom.y()
                    , mod_capture_rect.x() + mod_capture_rect.width() + mod_monitor_geom.x()
                    , mod_capture_rect.y() + mod_capture_rect.height() + mod_monitor_geom.y())

        self.frame_counter = 0
        self.start_ms = self.last_frame_ms = get_ms()

        # the time each snip should take place so we can adjust the pause between depending on snip speed
        self.future_frame_timings = np.linspace(self.start_ms, self.start_ms + self.ms_to_run, self.total_frames)
        self.future_frame_timings = self.future_frame_timings[1:] # pop first value so we always look at how long until the next frame is
        self.capture_pictures()


    def capture_pictures(self):
        if self.frame_counter > 0:
            self.captured_frame_timings.insert(len(self.captured_frame_timings), get_ms() - self.last_frame_ms)
        self.last_frame_ms = get_ms()

        screenshot = ImageGrab.grab(bbox=self.capture_rect, all_screens=True)
        self.snips.append(screenshot)
        self.frame_counter += 1

        # if there's still time left, take another snip, otherwise break out
        if get_ms() < self.start_ms + self.ms_to_run:
            if self.frame_counter == self.total_frames - 1: # just take a guess that the last one is close to the one before
                time_to_next_snip = self.last_frame_delay

            else: # how much time until the next snip should be taken
                if len(self.future_frame_timings) > 0:
                    time_to_next_snip = max(0, self.future_frame_timings[0] - get_ms())
                    # pop off the first value so we don't have to keep track of a potentially changing index if we change the fps
                    self.future_frame_timings = self.future_frame_timings[1:]
                else:
                    time_to_next_snip = self.fps_ms
            
            # if we're falling behind drop the fps until we catch up
            if time_to_next_snip == 0:
                self.lagged_frames += 1
                if self.lagged_frames >= self.MAX_LAGGED_FRAMES:
                    self.recalc_fps(self.fps - 1)
                    self.lagged_frames = 0
            else:
                self.lagged_frames = 0

            self.last_frame_delay = time_to_next_snip
            print('capturing frame: ' + str(self.frame_counter), 'frame delay: ' + str(time_to_next_snip))
            self.cap_timer.start(int(time_to_next_snip))
        else:
            self.captured_frame_timings.insert(len(self.captured_frame_timings), get_ms() - self.last_frame_ms)
            self.cap_pic_exit.emit()


    def recalc_fps(self, target_fps):
        self.fps = target_fps
        self.fps_ms = int(1000/target_fps)
        ms_already_run = (get_ms() - self.start_ms)
        self.total_frames = int(self.frame_counter + ((self.ms_to_run - ms_already_run) / 1000 * target_fps))
        print(self.total_frames)
        self.future_frame_timings = np.linspace(get_ms(), self.start_ms + self.ms_to_run, self.total_frames - self.frame_counter - 1)
        self.future_frame_timings = self.future_frame_timings[1:] # pop first value so we always look at how long until the next frame is


    def save_pictures(self):
        print('ending fps: ' + str(self.fps))
        print('saving')

        # BUG temp fix for the playback running fast, this seems to almost completely fix it, still need to find the root tho
        adjusted_frame_timings = [(x * 1.05) for x in self.captured_frame_timings] 
        self.snips[0].save(
            self.filename + '.gif',
            save_all=True,
            append_images=self.snips[1:],
            optimize=False,
            duration=adjusted_frame_timings,
            loop=0
        )

        # idx = 0
        # for snip in self.snips:
        #     snip.save('snip_' + str(idx) + '.png')
        #     idx += 1
        print('saved')
        self.close_window.emit()


def get_ms():
    return time.time_ns() / 1000000