from PySide6.QtWidgets import QMainWindow
from PySide6.QtCore import Slot

from ..main_wind import Ui_mainWindow
from backend import img_process as ip
from backend.workers.camera_worker import CameraWorker
from backend.sessions.ref_context_session import RefContextSession


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_mainWindow()
        self.ui.setupUi(self)

        self._show_live = True
        self._last_frame = None
        self._ref_session: RefContextSession | None = None

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

        # slider: valueChanged(int)
        self.ui.Ref_context_bin_thereshold_slider.valueChanged.connect(
            self._on_Ref_context_bin_thereshold_slider_changed
        )
        # threshold field: returnPressed
        self.ui.Ref_context_bin_thereshold_edit.returnPressed.connect(
            self._on_Ref_context_bin_thereshold_edit
        )
        # min_contour_length field
        self.ui.RefContext_min_contour_length_edit.returnPressed.connect(
            self._on_RefContext_min_contour_length_edit
        )

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
        self._close_ref_session()

    @Slot()
    def _on_select_refcontext_params(self):
        """
        Start interactive RefContext tuning:
        1) freeze live feed
        2) seed params from the form (or defaults)
        3) rebuild + preview
        """
        if self._ref_session is not None:
            self.ui.log_bar_panel.appendPlainText(
                "--MES: RefContext session already active"
            )
            return

        # last frame is what main_img currently shows; store it
        frame = self._last_frame
        if frame is None:
            self.ui.log_bar_panel.appendPlainText(
                "--ERR: no frame to freeze (camera not ready)"
            )
            return

        self._freeze_live()

        try:
            session = RefContextSession(frame)
        except Exception as e:
            self._unfreeze_live()
            self.ui.log_bar_panel.appendPlainText(f"--ERR: {e}")
            return

        # seed from form fields if they have values, else keep defaults
        bt = self._read_int_or(self.ui.Ref_context_bin_thereshold_edit.text().strip(),
                            session.bin_threshold)
        ml = self._read_int_or(self.ui.RefContext_min_contour_length_edit.text().strip(),
                                session.min_contour_len)
        try:
            session.set_params(bt, ml)
        except Exception as e:
            self.ui.log_bar_panel.appendPlainText(f"--ERR: {e}")

        self._ref_session = session
        self._render_ref_preview()
        self.ui.log_bar_panel.appendPlainText(
            f"--MES: RefContext session started "
            f"(bin={session.bin_threshold}, min_len={session.min_contour_len})"
        )

    @Slot(int)
    def _on_Ref_context_bin_thereshold_slider_changed(self, value: int):
        """Slider -> edit field -> reprocess."""
        # 1) sync the text field
        self.ui.Ref_context_bin_thereshold_edit.setText(str(value))
        # 2) reprocess with the new threshold, min_len taken from the form
        ml = self._read_int_or(
            self.ui.RefContext_min_contour_length_edit.text().strip(),
            self._ref_session.min_contour_len if self._ref_session else 0,
        )
        self._on_ref_params_changed(bt=value, ml=ml)

    @Slot()
    def _on_Ref_context_bin_thereshold_edit(self):
        """Threshold edit field -> slider -> reprocess."""
        txt = self.ui.Ref_context_bin_thereshold_edit.text().strip()
        default = self._ref_session.bin_threshold if self._ref_session else 127
        bt = self._read_int_or(txt, default)
        bt = max(0, min(255, bt))  # slider is limited to 0..255

        # 1) sync the slider (guard against the valueChanged feedback loop)
        self.ui.Ref_context_bin_thereshold_slider.blockSignals(True)
        self.ui.Ref_context_bin_thereshold_slider.setValue(bt)
        self.ui.Ref_context_bin_thereshold_slider.blockSignals(False)

        # 2) reprocess
        ml = self._read_int_or(
            self.ui.RefContext_min_contour_length_edit.text().strip(),
            self._ref_session.min_contour_len if self._ref_session else 0,
        )
        self._on_ref_params_changed(bt=bt, ml=ml)

    @Slot()
    def _on_RefContext_min_contour_length_edit(self):
        """min_contour_length edit field -> reprocess."""
        default = self._ref_session.min_contour_len if self._ref_session else 0
        ml = self._read_int_or(
            self.ui.RefContext_min_contour_length_edit.text().strip(), default
        )
        ml = max(0, ml)
        # take the current threshold from the slider (it is always in sync with the field)
        bt = self.ui.Ref_context_bin_thereshold_slider.value()
        self._on_ref_params_changed(bt=bt, ml=ml)
        
    def _on_ref_params_changed(self, bt: int, ml: int):
        """1) reprocess with the new params; render to screen."""
        if self._ref_session is None:
            return

        try:
            changed = self._ref_session.set_params(bt, ml)
        except Exception as e:
            self.ui.log_bar_panel.appendPlainText(f"--ERR: {e}")
            return

        if not changed:
            return
        
        self._render_ref_preview()

    def _render_ref_preview(self):
        if self._ref_session is None:
            return
        canvas = self._ref_session.preview_canvas()   # BGR
        pixmap = ip.cv2qt_img(canvas)
        self.ui.main_img.setPixmap(
            ip.scale_pixmap(pixmap, self.ui.main_img.size())
        )
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
        self._last_frame = frame
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

    def _freeze_live(self):
        self._show_live = False
        self.camera.pause()

    def _unfreeze_live(self):
        self._show_live = True
        self.camera.resume()

    def _close_ref_session(self, resume_live: bool = True):
        self._ref_session = None
        if resume_live:
            self._unfreeze_live()

    def _read_int_or(self, value, default: int) -> int:
        txt = value
        if not txt:
            return default
        try:
            return int(txt)
        except ValueError:
            self.ui.log_bar_panel.appendPlainText(
                f"--WARN: cannot parse int from '{txt}', using {default}"
            )
            return default