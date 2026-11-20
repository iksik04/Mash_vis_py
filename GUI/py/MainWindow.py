from PySide6.QtWidgets import QMainWindow, QDialog, QLabel, QVBoxLayout, QScrollArea, QWidget
from GUI.Qt.mainWind import Ui_MainWindow
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QImage, QPixmap

import cv2

from backend import constants as c
from backend import json_process as js
from backend.operation import validation, visualize


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # status variables
        self.is_live = True

        self.cap = cv2.VideoCapture(c.CAM_INDEX)

        self.cap_setup

        if self.is_live:
            # update frame by timer 
            self.timer = QTimer(self)
            self.timer.timeout.connect(self.update_frame)
            self.timer.start(30) # 30 FPS

    def cap_setup(self):
        '''Connect to cap and set settings'''
        if self.cap.isOpened():
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, c.CAM_WIDTH)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, c.CAM_HEIGHT)
        else:
            self.ui.text_log.appendPlainText("Ошибка: не удалось подключиться к камере.")


    def update_frame(self):
        """Capture frame from cap, shows it if is_live"""
        if not self.cap.isOpened():
            return

        ok, frame = self.cap.read()
        if ok and frame is not None:
            self.display_image(frame)

    def display_image(self, bgr_img):
        """Convert BGR OpenCV to QPixmap and rescale for QLabel."""
        rgb_img = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_img.shape
        bytes_per_line = ch * w
        qt_img = QImage(rgb_img.data, w, h, bytes_per_line, QImage.Format.Format_RGB888)
        
        pixmap = QPixmap.fromImage(qt_img)
        scaled_pixmap = pixmap.scaled(
            self.ui.label_image.size(),
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation
        )
        self.ui.label_image.setPixmap(scaled_pixmap)

    def show_validation_result(self, images, result=None):
        """Shows validation result GUI.

        - images["main"]  ->  label_image (display_image)
        - images["fail:*"] -> in separate windows
        """
        if not images:
            return

        main_img = images.get("main")
        if main_img is not None:
            self.display_image(main_img)

        self._close_fail_windows()

        for key, img in images.items():
            if not key.startswith("fail:"):
                continue
            name = key[len("fail:"):]
            stage = visualize._stage_label(result, name) if result is not None else "unknown"
            title = f"Validation fail: {stage}, {name}"
            self._show_fail_window(title, img)

    def _show_fail_window(self, title, bgr_img):
        """Creates separate window for NG ROI."""
        rgb_img = cv2.cvtColor(bgr_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_img.shape
        bytes_per_line = ch * w
        qt_img = QImage(rgb_img.data, w, h, bytes_per_line,
                        QImage.Format.Format_RGB888).copy()

        label = QLabel()
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setPixmap(QPixmap.fromImage(qt_img))

        dlg = QDialog(self)
        dlg.setWindowTitle(title)
        dlg.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        layout = QVBoxLayout(dlg)
        layout.addWidget(label)
        dlg.adjustSize()
        dlg.show()

        self._fail_windows.append(dlg)
        dlg.finished.connect(lambda _=0, d=dlg: self._forget_fail_window(d))

    def _forget_fail_window(self, dlg):
        if dlg in self._fail_windows:
            self._fail_windows.remove(dlg)

    def _close_fail_windows(self):
        for dlg in list(self._fail_windows):
            try:
                dlg.close()
            except RuntimeError:
                pass
        self._fail_windows.clear()

    def on_btn_clear_clicked(self):
        self.ui.text_log.clear()
        self._close_fail_windows()

    def on_btn_run_clicked(self):
        self.is_live = False

        if not self.cap.isOpened():
            return
        ok, frame = self.cap.read()
        if ok and frame is not None:
            multi_roi = js.read_MultiROI(c.MULTIROI_JSON_PATH)
            result = validation.validate(frame, multi_roi)
            canvases = visualize.render_validation_result(frame, result, multi_roi)
            self.show_validation_result(canvases, result)

    def on_btn_clear_clicked(self):
        self.ui.text_log.clear()