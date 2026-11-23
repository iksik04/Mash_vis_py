from PySide6.QtWidgets import QMainWindow
from PySide6.QtCore import Slot

from GUI.Qt.mainWind import Ui_MainWindow

from backend import constants as c
from backend import json_process as js
from backend import img_process as ip
from backend.workers.camera_worker import CameraWorker
from backend.operation import validation, visualize


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self._show_live = True

        self.camera = CameraWorker(parent=self)
        self.camera.frame_ready.connect(self._on_frame_ready)
        self.camera.error.connect(self._on_camera_error)
        self.camera.start()

        self.ui.btn_run.clicked.connect(self.on_btn_run_clicked)
        self.ui.btn_clear.clicked.connect(self.on_btn_clear_clicked)

    @Slot(object)
    def _on_frame_ready(self, frame):
        if not self._show_live:
            return
        pixmap = ip.cv2qt_img(frame)
        self.ui.label_image.setPixmap(
            ip.scale_pixmap(pixmap, self.ui.label_image.size())
        )

    @Slot(str)
    def _on_camera_error(self, msg: str):
        self.ui.text_log.appendPlainText(msg)

    def show_validation_result(self, images):
        """Shows validation result GUI.        """
        if not images:
            return

        main_img = images.get("main")
        if main_img is not None:
            self.ui.label_image.setPixmap(
                ip.scale_pixmap(
                    ip.cv2qt_img(main_img), self.ui.label_image.size()
                )
            )

    def on_btn_clear_clicked(self):
        self.ui.text_log.clear()
        self._show_live = True 

    def on_btn_run_clicked(self):
        frame = self.camera.last_frame
        if frame is None:
            self.ui.text_log.appendPlainText("Error: no frame available from the camera.")
            return

        try:
            multi_roi = js.read_MultiROI(c.MULTIROI_JSON_PATH)
            result = validation.validate(frame, multi_roi)
            canvases = visualize.render_validation_result(frame, result, multi_roi)
            self._show_live = False         # freeze live feed, keep result on screen
            self.show_validation_result(canvases)
            validation_text = validation.format_result(result)
            self.ui.text_log.appendPlainText(validation_text)

        except Exception as e:
            self.ui.text_log.appendPlainText(f"Validation error: {e}")
            return

    def closeEvent(self, event):
        self.camera.stop()
        super().closeEvent(event)