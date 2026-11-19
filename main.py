import sys
from PySide6.QtWidgets import QApplication, QMainWindow
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QGraphicsScene
from PySide6.QtCore import Qt
from GUI.py.mainWind import Ui_MainWindow

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        scene = QGraphicsScene()
        pixmap = QPixmap("images/im1.jpg")
        scene.addPixmap(pixmap)
        self.ui.graphicsView.setScene(scene)
        self.ui.graphicsView.fitInView(scene.sceneRect(), Qt.KeepAspectRatio)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())