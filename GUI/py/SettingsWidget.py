# settings_widget.py (или отдельный файл wrapper)
from PySide6.QtWidgets import QWidget
from ..settings_widget import Ui_SettingsWidget


class SettingsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_SettingsWidget()
        self.ui.setupUi(self)