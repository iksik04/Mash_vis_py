# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ui_main_wind.ui'
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
from PySide6.QtWidgets import (QApplication, QButtonGroup, QHBoxLayout, QLabel,
    QMainWindow, QPlainTextEdit, QPushButton, QSizePolicy,
    QSpacerItem, QStackedWidget, QVBoxLayout, QWidget)

from .py.SettingsWidget import SettingsWidget

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(1920, 1080)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(Form.sizePolicy().hasHeightForWidth())
        Form.setSizePolicy(sizePolicy)
        Form.setStyleSheet(u"QPushButton {padding: 10px 10px;}")
        self.centralwidget = QWidget(Form)
        self.centralwidget.setObjectName(u"centralwidget")
        self.verticalLayout = QVBoxLayout(self.centralwidget)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.widget = QWidget(self.centralwidget)
        self.widget.setObjectName(u"widget")
        self.widget.setMinimumSize(QSize(0, 0))
        self.widget.setMaximumSize(QSize(16777215, 40))
        self.widget.setStyleSheet(u"background-color:  rgb(0, 170, 127);")
        self.horizontalLayout = QHBoxLayout(self.widget)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.validation_page_btn = QPushButton(self.widget)
        self.page_btns = QButtonGroup(Form)
        self.page_btns.setObjectName(u"page_btns")
        self.page_btns.addButton(self.validation_page_btn)
        self.validation_page_btn.setObjectName(u"validation_page_btn")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.validation_page_btn.sizePolicy().hasHeightForWidth())
        self.validation_page_btn.setSizePolicy(sizePolicy1)

        self.horizontalLayout.addWidget(self.validation_page_btn)

        self.settings_page_btn = QPushButton(self.widget)
        self.page_btns.addButton(self.settings_page_btn)
        self.settings_page_btn.setObjectName(u"settings_page_btn")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Ignored)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.settings_page_btn.sizePolicy().hasHeightForWidth())
        self.settings_page_btn.setSizePolicy(sizePolicy2)

        self.horizontalLayout.addWidget(self.settings_page_btn)


        self.verticalLayout.addWidget(self.widget)

        self.stackedWidget = QStackedWidget(self.centralwidget)
        self.stackedWidget.setObjectName(u"stackedWidget")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.stackedWidget.sizePolicy().hasHeightForWidth())
        self.stackedWidget.setSizePolicy(sizePolicy3)
        self.stackedWidget.setStyleSheet(u"")
        self.validation = QWidget()
        self.validation.setObjectName(u"validation")
        self.verticalLayout_3 = QVBoxLayout(self.validation)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.widget_3 = QWidget(self.validation)
        self.widget_3.setObjectName(u"widget_3")

        self.verticalLayout_3.addWidget(self.widget_3)

        self.stackedWidget.addWidget(self.validation)
        self.settings_page = QWidget()
        self.settings_page.setObjectName(u"settings_page")
        self.verticalLayout_2 = QVBoxLayout(self.settings_page)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.settings_bar = QWidget(self.settings_page)
        self.settings_bar.setObjectName(u"settings_bar")
        sizePolicy4 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.settings_bar.sizePolicy().hasHeightForWidth())
        self.settings_bar.setSizePolicy(sizePolicy4)
        self.settings_bar.setMinimumSize(QSize(0, 50))
        self.settings_bar.setMaximumSize(QSize(16777215, 50))
        self.settings_bar.setStyleSheet(u"background-color:  rgb(0, 170, 127);")
        self.horizontalLayout_3 = QHBoxLayout(self.settings_bar)
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_2)

        self.RefContext = QPushButton(self.settings_bar)
        self.RefContext.setObjectName(u"RefContext")
        sizePolicy5 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        sizePolicy5.setHorizontalStretch(0)
        sizePolicy5.setVerticalStretch(0)
        sizePolicy5.setHeightForWidth(self.RefContext.sizePolicy().hasHeightForWidth())
        self.RefContext.setSizePolicy(sizePolicy5)
        self.RefContext.setMinimumSize(QSize(100, 0))

        self.horizontalLayout_3.addWidget(self.RefContext)

        self.ROIs = QPushButton(self.settings_bar)
        self.ROIs.setObjectName(u"ROIs")
        sizePolicy5.setHeightForWidth(self.ROIs.sizePolicy().hasHeightForWidth())
        self.ROIs.setSizePolicy(sizePolicy5)
        self.ROIs.setMinimumSize(QSize(100, 0))

        self.horizontalLayout_3.addWidget(self.ROIs)


        self.verticalLayout_2.addWidget(self.settings_bar)

        self.horizontalLayout_2 = QHBoxLayout()
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.label = QLabel(self.settings_page)
        self.label.setObjectName(u"label")

        self.horizontalLayout_2.addWidget(self.label)

        self.widget_2 = SettingsWidget(self.settings_page)
        self.widget_2.setObjectName(u"widget_2")
        self.widget_2.setMaximumSize(QSize(500, 16777215))

        self.horizontalLayout_2.addWidget(self.widget_2)


        self.verticalLayout_2.addLayout(self.horizontalLayout_2)

        self.log_bar_panel = QPlainTextEdit(self.settings_page)
        self.log_bar_panel.setObjectName(u"log_bar_panel")
        self.log_bar_panel.setMaximumSize(QSize(16777215, 100))

        self.verticalLayout_2.addWidget(self.log_bar_panel)

        self.stackedWidget.addWidget(self.settings_page)

        self.verticalLayout.addWidget(self.stackedWidget)

        Form.setCentralWidget(self.centralwidget)

        self.retranslateUi(Form)

        self.stackedWidget.setCurrentIndex(1)


        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.validation_page_btn.setText(QCoreApplication.translate("Form", u"Validation", None))
        self.settings_page_btn.setText(QCoreApplication.translate("Form", u"Settings", None))
        self.RefContext.setText(QCoreApplication.translate("Form", u"RefContext", None))
        self.ROIs.setText(QCoreApplication.translate("Form", u"ROIs", None))
        self.label.setText(QCoreApplication.translate("Form", u"TextLabel", None))
    # retranslateUi

