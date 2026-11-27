from PySide6.QtWidgets import QMainWindow
from PySide6.QtCore import Slot

from ..main_wind import Ui_mainWindow
from backend import img_process as ip
from backend.workers.camera_worker import CameraWorker


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_mainWindow()
        self.ui.setupUi(self)

        self._show_live = True

        self._connect_signals()
        self._setup_initial_state()
        self._cap_setup()

    # ------------------------------------------------------------------
    # Setup
    # ------------------------------------------------------------------
    def _connect_signals(self):
        """Connect all signals to slots """
        # --- Validation / Settings ---
        self.ui.settings_validation_page_btns.setId(self.ui.validation_page_btn, 0)
        self.ui.settings_validation_page_btns.setId(self.ui.settings_page_btn, 1)
        self.ui.settings_validation_page_btns.idClicked.connect(
            self._on_page_btn_clicked
        )

        # --- RefContext / ROIs ---
        self.ui.RefContext_ROIs_page_btns.setId(self.ui.RefContext_page_btn, 0)
        self.ui.RefContext_ROIs_page_btns.setId(self.ui.ROIs_page_btn, 1)
        self.ui.RefContext_ROIs_page_btns.idClicked.connect(
            self._on_refcontext_rois_btn_clicked
        )

        # --- RefContext buttons ---
        self.ui.loadRefContext_btn.clicked.connect(self._on_load_refcontext)
        self.ui.saveRefContext_btn.clicked.connect(self._on_save_refcontext)
        self.ui.select_RefContext_params_btn.clicked.connect(
            self._on_select_refcontext_params
        )

        # --- ROI buttons ---
        self.ui.addROI_btn.clicked.connect(self._on_add_roi)
        self.ui.copyROI_btn.clicked.connect(self._on_copy_roi)
        self.ui.delROI_btn.clicked.connect(self._on_delete_roi)
        self.ui.saveROI_btn.clicked.connect(self._on_save_roi)

    def _setup_initial_state(self):
        """Start pages state setting."""
        self.ui.validation_page_btn.setChecked(True)
        self.ui.validation_settings_stacked.setCurrentIndex(0)

        self.ui.RefContext_page_btn.setChecked(True)
        self.ui.RefContext_ROI_stacked.setCurrentIndex(0)

    def _cap_setup(self):
        """Start cap """
        self.camera = CameraWorker(parent=self)
        self.camera.frame_ready.connect(self._on_frame_ready)
        self.camera.error.connect(self._on_camera_error)
        self.camera.start()

    # ------------------------------------------------------------------
    # Page switching
    # ------------------------------------------------------------------
    @Slot(int)
    def _on_page_btn_clicked(self, page_id: int):
        self.ui.validation_settings_stacked.setCurrentIndex(page_id)

    @Slot(int)
    def _on_refcontext_rois_btn_clicked(self, page_id: int):
        self.ui.RefContext_ROI_stacked.setCurrentIndex(page_id)

    # ------------------------------------------------------------------
    # RefContext handlers
    # ------------------------------------------------------------------
    @Slot()
    def _on_load_refcontext(self):
        """"""
        self.ui.log_bar_panel.appendPlainText("load_refcontext_btn")

    @Slot()
    def _on_save_refcontext(self):
        """"""
        for i in range(1,20):
            self.ui.log_bar_panel.appendPlainText("save_refcontext_btn")

    @Slot()
    def _on_select_refcontext_params(self):
        """"""
        self.ui.log_bar_panel.appendPlainText("select_refcontext_params_btn")

    # ------------------------------------------------------------------
    # ROI handlers
    # ------------------------------------------------------------------
    @Slot()
    def _on_add_roi(self):
        """"""
        self.ui.log_bar_panel.appendPlainText("add_roi_btn")

    @Slot()
    def _on_copy_roi(self):
        """"""
        self.ui.log_bar_panel.appendPlainText("copy_roi_btn")

    @Slot()
    def _on_delete_roi(self):
        """"""
        self.ui.log_bar_panel.appendPlainText("delete_roi_btn")

    @Slot()
    def _on_save_roi(self):
        """"""
        self.ui.log_bar_panel.appendPlainText("save_roi_btn")

    @Slot(object)
    def _on_frame_ready(self, frame):
        if not self._show_live:
            return
        pixmap = ip.cv2qt_img(frame)
        self.ui.main_img.setPixmap(
            ip.scale_pixmap(pixmap, self.ui.main_img.size())
        )

    @Slot(str)
    def _on_camera_error(self, msg: str):
        self.ui.log_bar_panel.appendPlainText(msg)

    def closeEvent(self, event):
        self.camera.stop()
        super().closeEvent(event)