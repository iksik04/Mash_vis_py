from PySide6.QtWidgets import QMainWindow
from GUI.Qt.mainWind import Ui_MainWindow
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QImage, QPixmap

import cv2

from backend import constants as c
from backend.operation import validation


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # status variables
        self.is_live = True

        # update frame by timer 
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_frame)
        self.timer.start(30) # 30 FPS

    def cup_setup(self):
        '''Connect to cap and set settings'''
        self.cap = cv2.VideoCapture(c.CAM_INDEX)
        if self.cap.isOpened():
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, c.CAM_WIDTH)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, c.CAM_HEIGHT)
        else:
            self.ui.text_log.appendPlainText("Ошибка: не удалось подключиться к камере.")


    def update_frame(self):
        """Capture frame from cap, shows it if is_live"""
        if not self.is_live or not self.cap.isOpened():
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

    def on_btn_run_clicked(self):
        self.is_live = False

        if not self.cap.isOpened():
            return
        ok, frame = self.cap.read()
        if ok and frame is not None:
            validation.validate(frame)

    def on_btn_clear_clicked(self):
        self.ui.text_log.clear()