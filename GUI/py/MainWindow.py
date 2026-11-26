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

        # --- Save buttons ---
        self.ui.saveRefContext_btn.clicked.connect(self._on_save_refcontext)
        self.ui.saveROI_btn.clicked.connect(self._on_save_roi)

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

    # ------------------------------------------------------------------
    # Save handlers
    # ------------------------------------------------------------------
    @Slot()
    def _on_save_refcontext(self):
        """Собирает значения полей RefContext и пишет их в лог-бар."""
        fields = {
            "RefContext/Filename":
                self.ui.RefContext_filename_edit.text(),
            "RefContext/Ref_img_name":
                self.ui.Ref_img_name_edit.text(),
            "RefContext/Ref_bin_img_name":
                self.ui.Ref_bin_img_name_edit.text(),
            "RefContext/bin_thereshold":
                self.ui.Ref_context_bin_thereshold_edit.text(),
            "RefContext/min_contour_length":
                self.ui.RefContext_min_contour_length_edit.text(),
        }
        self._log_section("Save RefContext", fields)

    @Slot()
    def _on_save_roi(self):
        """Собирает значения полей ROIs и пишет их в лог-бар."""
        fields = {
            "ROIs/Filename":
                self.ui.ROIs_filename_edit.text(),
        }
        self._log_section("Save ROIs", fields)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _log_section(self, title: str, fields: dict):
        """Форматирует блок полей и добавляет его в log_bar_panel."""
        lines = [f"=== {title} ==="]
        for key, value in fields.items():
            shown = value if value else "<empty>"
            lines.append(f"  {key}: {shown}")
        lines.append("")  # пустая строка-разделитель
        self.ui.log_bar_panel.appendPlainText("\n".join(lines))