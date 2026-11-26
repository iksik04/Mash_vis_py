# settings_widget.py (или отдельный файл wrapper)
from PySide6.QtWidgets import QWidget
from ..ROI_settings_widget import Ui_Form


class SettingsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_Form()
        self.ui.setupUi(self)