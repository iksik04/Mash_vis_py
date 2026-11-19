# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'mainWind.ui'
##
## Created by: Qt User Interface Compiler version 6.12.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QGridLayout, QHBoxLayout, QLabel,
    QMainWindow, QMenuBar, QPlainTextEdit, QPushButton,
    QSizePolicy, QSpacerItem, QStatusBar, QVBoxLayout,
    QWidget)

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(881, 729)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.gridLayout = QGridLayout(self.centralwidget)
        self.gridLayout.setObjectName(u"gridLayout")
        self.main_layout = QVBoxLayout()
        self.main_layout.setObjectName(u"main_layout")
        self.top_layout = QHBoxLayout()
        self.top_layout.setObjectName(u"top_layout")
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.top_layout.addItem(self.horizontalSpacer)

        self.btn_clear = QPushButton(self.centralwidget)
        self.btn_clear.setObjectName(u"btn_clear")

        self.top_layout.addWidget(self.btn_clear)

        self.btn_run = QPushButton(self.centralwidget)
        self.btn_run.setObjectName(u"btn_run")

        self.top_layout.addWidget(self.btn_run)


        self.main_layout.addLayout(self.top_layout)

        self.label_image = QLabel(self.centralwidget)
        self.label_image.setObjectName(u"label_image")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.label_image.sizePolicy().hasHeightForWidth())
        self.label_image.setSizePolicy(sizePolicy)
        self.label_image.setMinimumSize(QSize(320, 240))
        self.label_image.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.main_layout.addWidget(self.label_image)

        self.text_log = QPlainTextEdit(self.centralwidget)
        self.text_log.setObjectName(u"text_log")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.text_log.sizePolicy().hasHeightForWidth())
        self.text_log.setSizePolicy(sizePolicy1)
        self.text_log.setReadOnly(True)

        self.main_layout.addWidget(self.text_log)

        self.main_layout.setStretch(1, 1)

        self.gridLayout.addLayout(self.main_layout, 0, 0, 1, 1)

        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QMenuBar(MainWindow)
        self.menubar.setObjectName(u"menubar")
        self.menubar.setGeometry(QRect(0, 0, 881, 22))
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QStatusBar(MainWindow)
        self.statusbar.setObjectName(u"statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        self.btn_run.clicked.connect(MainWindow.on_btn_run_clicked)
        self.btn_clear.clicked.connect(MainWindow.on_btn_clear_clicked)

        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
        self.btn_clear.setText(QCoreApplication.translate("MainWindow", u"\u041e\u0447\u0438\u0441\u0442\u0438\u0442\u044c", None))
        self.btn_run.setText(QCoreApplication.translate("MainWindow", u"\u041f\u0443\u0441\u043a", None))
        self.label_image.setText(QCoreApplication.translate("MainWindow", u"TextLabel", None))
    # retranslateUi

