from PySide6.QtWidgets import QMainWindow
from PySide6.QtCore import Slot

from ..main_wind import Ui_Form


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_Form()
        self.ui.setupUi(self)

        self.ui.page_btns.setId(self.ui.validation_page_btn, 0)
        self.ui.page_btns.setId(self.ui.settings_page_btn, 1)

        self.ui.page_btns.idClicked.connect(self._on_page_btn_clicked)

        self.ui.validation_page_btn.setChecked(True)
        self.ui.stackedWidget.setCurrentIndex(0)

    @Slot(int)
    def _on_page_btn_clicked(self, page_id: int):
        self.ui.stackedWidget.setCurrentIndex(page_id)