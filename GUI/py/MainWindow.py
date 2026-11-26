from PySide6.QtWidgets import QMainWindow
from PySide6.QtCore import Slot

from ..main_wind import Ui_Form


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        # --- Validation / Settings ---
        self.ui.settings_validation_page_btns.setId(self.ui.validation_page_btn, 0)
        self.ui.settings_validation_page_btns.setId(self.ui.settings_page_btn, 1)
        self.ui.settings_validation_page_btns.idClicked.connect(
            self._on_page_btn_clicked
        )

        # --- RefContext / ROIs ---
        self.ui.RefContext_ROIs_page_btns.setId(self.ui.RefContext_btn, 0)
        self.ui.RefContext_ROIs_page_btns.setId(self.ui.ROIs_btn, 1)
        self.ui.RefContext_ROIs_page_btns.idClicked.connect(
            self._on_refcontext_rois_btn_clicked
        )

        self.ui.validation_page_btn.setChecked(True)
        self.ui.validation_settings_stacked.setCurrentIndex(0)

        self.ui.RefContext_btn.setChecked(True)
        self.ui.RefContext_ROI_stacked.setCurrentIndex(1)

    @Slot(int)
    def _on_page_btn_clicked(self, page_id: int):
        self.ui.validation_settings_stacked.setCurrentIndex(page_id)

    @Slot(int)
    def _on_refcontext_rois_btn_clicked(self, page_id: int):
        self.ui.RefContext_ROI_stacked.setCurrentIndex(page_id)