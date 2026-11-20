from PySide6.QtWidgets import QMainWindow, QDialog, QLabel, QVBoxLayout
from PySide6.QtCore import Qt, Slot

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

        self._fail_windows = []
        self._show_live = True

        self.camera = CameraWorker(parent=self)
        self.camera.frame_ready.connect(self._on_frame_ready)
        self.camera.error.connect(self._on_camera_error)
        self.camera.start()

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

    def show_validation_result(self, images, result=None):
        """Shows validation result GUI.

        - images["main"]   -> label_image
        - images["fail:*"] -> in separate windows
        """
        if not images:
            return

        main_img = images.get("main")
        if main_img is not None:
            self.ui.label_image.setPixmap(
                ip.scale_pixmap(
                    ip.cv2qt_img(main_img), self.ui.label_image.size()
                )
            )

        self._close_fail_windows()

        for key, img in images.items():
            if not key.startswith("fail:"):
                continue
            name = key[len("fail:"):]
            stage = visualize._stage_label(result, name) if result is not None else "unknown"
            title = f"Validation fail: {stage}, {name}"
            self._show_fail_window(title, img)

    def _show_fail_window(self, title, bgr_img):
        """Creates a separate window for an NG ROI."""
        label = QLabel()
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        label.setPixmap(ip.cv2qt_img(bgr_img))

        dlg = QDialog(self)
        dlg.setWindowTitle(title)
        dlg.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        layout = QVBoxLayout(dlg)
        layout.addWidget(label)
        dlg.adjustSize()
        dlg.show()

        self._fail_windows.append(dlg)
        dlg.finished.connect(lambda _result, d=dlg: self._forget_fail_window(d))

    def _forget_fail_window(self, dlg):
        if dlg in self._fail_windows:
            self._fail_windows.remove(dlg)

    def _close_fail_windows(self):
        for dlg in list(self._fail_windows):
            try:
                dlg.close()
            except RuntimeError:
                pass
            self._forget_fail_window(dlg)

    def on_btn_clear_clicked(self):
        self.ui.text_log.clear()
        self._close_fail_windows()
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
        except Exception as e:
            self.ui.text_log.appendPlainText(f"Validation error: {e}")
            return

        self._show_live = False         # freeze live feed, keep result on screen
        self.show_validation_result(canvases, result)

    def closeEvent(self, event):
        self.camera.stop()
        self._close_fail_windows()
        super().closeEvent(event)