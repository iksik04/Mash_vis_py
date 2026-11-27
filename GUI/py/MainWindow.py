from PySide6.QtWidgets import QMainWindow
from PySide6.QtCore import Slot

from ..main_wind import Ui_mainWindow


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_mainWindow()
        self.ui.setupUi(self)

        self._connect_signals()
        self._setup_initial_state()

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
        pass

    @Slot()
    def _on_save_refcontext(self):
        """"""
        pass

    @Slot()
    def _on_select_refcontext_params(self):
        """"""
        pass

    # ------------------------------------------------------------------
    # ROI handlers
    # ------------------------------------------------------------------
    @Slot()
    def _on_add_roi(self):
        """"""
        pass

    @Slot()
    def _on_copy_roi(self):
        """"""
        pass

    @Slot()
    def _on_delete_roi(self):
        """"""
        pass

    @Slot()
    def _on_save_roi(self):
        """"""
        pass