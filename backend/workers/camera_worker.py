import cv2
import numpy as np
from PySide6.QtCore import QObject, QThread, Signal, Slot

from backend import constants as c


class _CaptureThread(QThread):
    """Reads frames from cv2.VideoCapture in a background thread."""

    frame_ready = Signal(object)   # np.ndarray (BGR)
    error = Signal(str)

    def __init__(self, cam_index: int, width: int, height: int, fps: int, parent=None):
        super().__init__(parent)
        self._cam_index = cam_index
        self._width = width
        self._height = height
        self._fps = fps
        self._running = False
        self._paused = False

    def pause(self):
        self._paused = True

    def resume(self):
        self._paused = False

    def run(self):
        cap = cv2.VideoCapture(self._cam_index)
        if not cap.isOpened():
            self.error.emit("Error: failed to connect to the camera.")
            return

        cap.set(cv2.CAP_PROP_FRAME_WIDTH, self._width)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, self._height)

        self._running = True
        interval_ms = max(1, int(1000 / self._fps))
        try:
            while self._running:
                ok, frame = cap.read()
                if not ok or frame is None:
                    self.error.emit("Error: failed to read a frame from the camera.")
                    self.msleep(50)
                    continue
                if not self._paused:
                    self.frame_ready.emit(frame)
                self.msleep(interval_ms)
        finally:
            cap.release()

    def stop(self):
        self._running = False


class CameraWorker(QObject):
    """Facade over the capture thread.

    Public interface:
      - start() / stop()
      - is_running
      - last_frame : np.ndarray | None  (most recent BGR frame)
      - signals: frame_ready(object), error(str)
    """

    frame_ready = Signal(object)
    error = Signal(str)

    def __init__(self, cam_index: int = c.CAM_INDEX,
                 width: int = c.CAM_WIDTH,
                 height: int = c.CAM_HEIGHT,
                 fps: int = 30,
                 parent=None):
        super().__init__(parent)
        self.last_frame: np.ndarray | None = None

        self._thread = _CaptureThread(cam_index, width, height, fps, parent=self)
        self._thread.frame_ready.connect(self._on_frame)
        self._thread.frame_ready.connect(self.frame_ready)
        self._thread.error.connect(self.error)

    @property
    def is_running(self) -> bool:
        return self._thread.isRunning()

    @Slot(object)
    def _on_frame(self, frame):
        self.last_frame = frame

    @Slot()
    def start(self):
        if not self._thread.isRunning():
            self._thread.start()

    @Slot()
    def stop(self):
        if self._thread.isRunning():
            self._thread.stop()
            self._thread.wait(2000)

    def pause(self):
        self._thread.pause()

    def resume(self):
        self._thread.resume()