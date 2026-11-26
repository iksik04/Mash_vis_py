# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'ui_main_Wind.ui'
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
    QSpacerItem, QSplitter, QStackedWidget, QVBoxLayout,
    QWidget)

class Ui_Form(object):
    def setupUi(self, Form):
        if not Form.objectName():
            Form.setObjectName(u"Form")
        Form.resize(1920, 1080)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
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
        self.main_bar = QWidget(self.centralwidget)
        self.main_bar.setObjectName(u"main_bar")
        self.main_bar.setMinimumSize(QSize(0, 0))
        self.main_bar.setMaximumSize(QSize(16777215, 40))
        self.main_bar.setStyleSheet(u"background-color:  rgb(189, 189, 189);")
        self.horizontalLayout = QHBoxLayout(self.main_bar)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalSpacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout.addItem(self.horizontalSpacer)

        self.validation_page_btn = QPushButton(self.main_bar)
        self.settings_validation_page_btns = QButtonGroup(Form)
        self.settings_validation_page_btns.setObjectName(u"settings_validation_page_btns")
        self.settings_validation_page_btns.addButton(self.validation_page_btn)
        self.validation_page_btn.setObjectName(u"validation_page_btn")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.validation_page_btn.sizePolicy().hasHeightForWidth())
        self.validation_page_btn.setSizePolicy(sizePolicy1)

        self.horizontalLayout.addWidget(self.validation_page_btn)

        self.settings_page_btn = QPushButton(self.main_bar)
        self.settings_validation_page_btns.addButton(self.settings_page_btn)
        self.settings_page_btn.setObjectName(u"settings_page_btn")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Ignored)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.settings_page_btn.sizePolicy().hasHeightForWidth())
        self.settings_page_btn.setSizePolicy(sizePolicy2)

        self.horizontalLayout.addWidget(self.settings_page_btn)


        self.verticalLayout.addWidget(self.main_bar)

        self.validation_settings_stacked = QStackedWidget(self.centralwidget)
        self.validation_settings_stacked.setObjectName(u"validation_settings_stacked")
        sizePolicy3 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy3.setHorizontalStretch(0)
        sizePolicy3.setVerticalStretch(0)
        sizePolicy3.setHeightForWidth(self.validation_settings_stacked.sizePolicy().hasHeightForWidth())
        self.validation_settings_stacked.setSizePolicy(sizePolicy3)
        self.validation_settings_stacked.setStyleSheet(u"")
        self.validation_page = QWidget()
        self.validation_page.setObjectName(u"validation_page")
        self.verticalLayout_3 = QVBoxLayout(self.validation_page)
        self.verticalLayout_3.setSpacing(0)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.widget_3 = QWidget(self.validation_page)
        self.widget_3.setObjectName(u"widget_3")

        self.verticalLayout_3.addWidget(self.widget_3)

        self.validation_settings_stacked.addWidget(self.validation_page)
        self.settings_page = QWidget()
        self.settings_page.setObjectName(u"settings_page")
        self.verticalLayout_2 = QVBoxLayout(self.settings_page)
        self.verticalLayout_2.setSpacing(0)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.splitter = QSplitter(self.settings_page)
        self.splitter.setObjectName(u"splitter")
        sizePolicy.setHeightForWidth(self.splitter.sizePolicy().hasHeightForWidth())
        self.splitter.setSizePolicy(sizePolicy)
        self.splitter.setOrientation(Qt.Orientation.Horizontal)
        self.label = QLabel(self.splitter)
        self.label.setObjectName(u"label")
        sizePolicy.setHeightForWidth(self.label.sizePolicy().hasHeightForWidth())
        self.label.setSizePolicy(sizePolicy)
        self.label.setMinimumSize(QSize(1000, 0))
        self.splitter.addWidget(self.label)
        self.layoutWidget = QWidget(self.splitter)
        self.layoutWidget.setObjectName(u"layoutWidget")
        self.verticalLayout_4 = QVBoxLayout(self.layoutWidget)
        self.verticalLayout_4.setSpacing(0)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.settings_bar = QWidget(self.layoutWidget)
        self.settings_bar.setObjectName(u"settings_bar")
        sizePolicy4 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        sizePolicy4.setHorizontalStretch(0)
        sizePolicy4.setVerticalStretch(0)
        sizePolicy4.setHeightForWidth(self.settings_bar.sizePolicy().hasHeightForWidth())
        self.settings_bar.setSizePolicy(sizePolicy4)
        self.settings_bar.setMinimumSize(QSize(250, 50))
        self.settings_bar.setMaximumSize(QSize(920, 50))
        self.settings_bar.setStyleSheet(u"background-color:  rgb(189, 189, 189);")
        self.horizontalLayout_3 = QHBoxLayout(self.settings_bar)
        self.horizontalLayout_3.setSpacing(0)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_3.addItem(self.horizontalSpacer_2)

        self.RefContext_btn = QPushButton(self.settings_bar)
        self.RefContext_ROIs_page_btns = QButtonGroup(Form)
        self.RefContext_ROIs_page_btns.setObjectName(u"RefContext_ROIs_page_btns")
        self.RefContext_ROIs_page_btns.addButton(self.RefContext_btn)
        self.RefContext_btn.setObjectName(u"RefContext_btn")
        sizePolicy5 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        sizePolicy5.setHorizontalStretch(0)
        sizePolicy5.setVerticalStretch(0)
        sizePolicy5.setHeightForWidth(self.RefContext_btn.sizePolicy().hasHeightForWidth())
        self.RefContext_btn.setSizePolicy(sizePolicy5)
        self.RefContext_btn.setMinimumSize(QSize(100, 0))

        self.horizontalLayout_3.addWidget(self.RefContext_btn)

        self.ROIs_btn = QPushButton(self.settings_bar)
        self.RefContext_ROIs_page_btns.addButton(self.ROIs_btn)
        self.ROIs_btn.setObjectName(u"ROIs_btn")
        sizePolicy5.setHeightForWidth(self.ROIs_btn.sizePolicy().hasHeightForWidth())
        self.ROIs_btn.setSizePolicy(sizePolicy5)
        self.ROIs_btn.setMinimumSize(QSize(100, 0))

        self.horizontalLayout_3.addWidget(self.ROIs_btn)


        self.verticalLayout_4.addWidget(self.settings_bar)

        self.RefContext_ROI_stacked = QStackedWidget(self.layoutWidget)
        self.RefContext_ROI_stacked.setObjectName(u"RefContext_ROI_stacked")
        sizePolicy6 = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        sizePolicy6.setHorizontalStretch(0)
        sizePolicy6.setVerticalStretch(0)
        sizePolicy6.setHeightForWidth(self.RefContext_ROI_stacked.sizePolicy().hasHeightForWidth())
        self.RefContext_ROI_stacked.setSizePolicy(sizePolicy6)
        self.RefContext_ROI_stacked.setMaximumSize(QSize(1000, 16777215))
        self.RefContext_page = QWidget()
        self.RefContext_page.setObjectName(u"RefContext_page")
        self.RefContext_ROI_stacked.addWidget(self.RefContext_page)
        self.ROI_page = QWidget()
        self.ROI_page.setObjectName(u"ROI_page")
        sizePolicy6.setHeightForWidth(self.ROI_page.sizePolicy().hasHeightForWidth())
        self.ROI_page.setSizePolicy(sizePolicy6)
        self.verticalLayout_5 = QVBoxLayout(self.ROI_page)
        self.verticalLayout_5.setSpacing(0)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.ROI_settings_bar = QWidget(self.ROI_page)
        self.ROI_settings_bar.setObjectName(u"ROI_settings_bar")
        sizePolicy.setHeightForWidth(self.ROI_settings_bar.sizePolicy().hasHeightForWidth())
        self.ROI_settings_bar.setSizePolicy(sizePolicy)
        self.ROI_settings_bar.setMinimumSize(QSize(250, 50))
        self.ROI_settings_bar.setMaximumSize(QSize(920, 50))
        self.ROI_settings_bar.setStyleSheet(u"background-color:  rgb(189, 189, 189);")
        self.horizontalLayout_4 = QHBoxLayout(self.ROI_settings_bar)
        self.horizontalLayout_4.setSpacing(0)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.addROI_btn = QPushButton(self.ROI_settings_bar)
        self.addROI_btn.setObjectName(u"addROI_btn")
        sizePolicy5.setHeightForWidth(self.addROI_btn.sizePolicy().hasHeightForWidth())
        self.addROI_btn.setSizePolicy(sizePolicy5)
        self.addROI_btn.setMinimumSize(QSize(50, 0))
        self.addROI_btn.setMaximumSize(QSize(50, 16777215))
        icon = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.ListAdd))
        self.addROI_btn.setIcon(icon)
        self.addROI_btn.setIconSize(QSize(30, 30))

        self.horizontalLayout_4.addWidget(self.addROI_btn)

        self.copyROI_btn = QPushButton(self.ROI_settings_bar)
        self.copyROI_btn.setObjectName(u"copyROI_btn")
        sizePolicy5.setHeightForWidth(self.copyROI_btn.sizePolicy().hasHeightForWidth())
        self.copyROI_btn.setSizePolicy(sizePolicy5)
        self.copyROI_btn.setMinimumSize(QSize(50, 0))
        self.copyROI_btn.setMaximumSize(QSize(50, 16777215))
        icon1 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.EditCopy))
        self.copyROI_btn.setIcon(icon1)
        self.copyROI_btn.setIconSize(QSize(30, 30))

        self.horizontalLayout_4.addWidget(self.copyROI_btn)

        self.delROI_btn = QPushButton(self.ROI_settings_bar)
        self.delROI_btn.setObjectName(u"delROI_btn")
        sizePolicy5.setHeightForWidth(self.delROI_btn.sizePolicy().hasHeightForWidth())
        self.delROI_btn.setSizePolicy(sizePolicy5)
        self.delROI_btn.setMinimumSize(QSize(48, 0))
        self.delROI_btn.setMaximumSize(QSize(50, 16777215))
        icon2 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.EditDelete))
        self.delROI_btn.setIcon(icon2)
        self.delROI_btn.setIconSize(QSize(30, 30))

        self.horizontalLayout_4.addWidget(self.delROI_btn)

        self.Save_btn = QPushButton(self.ROI_settings_bar)
        self.Save_btn.setObjectName(u"Save_btn")
        sizePolicy5.setHeightForWidth(self.Save_btn.sizePolicy().hasHeightForWidth())
        self.Save_btn.setSizePolicy(sizePolicy5)
        icon3 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.DocumentSave))
        self.Save_btn.setIcon(icon3)
        self.Save_btn.setIconSize(QSize(30, 30))

        self.horizontalLayout_4.addWidget(self.Save_btn)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_3)


        self.verticalLayout_5.addWidget(self.ROI_settings_bar)

        self.ROI_settings_widgets = QWidget(self.ROI_page)
        self.ROI_settings_widgets.setObjectName(u"ROI_settings_widgets")

        self.verticalLayout_5.addWidget(self.ROI_settings_widgets)

        self.RefContext_ROI_stacked.addWidget(self.ROI_page)

        self.verticalLayout_4.addWidget(self.RefContext_ROI_stacked)

        self.splitter.addWidget(self.layoutWidget)

        self.verticalLayout_2.addWidget(self.splitter)

        self.validation_settings_stacked.addWidget(self.settings_page)

        self.verticalLayout.addWidget(self.validation_settings_stacked)

        self.log_bar_panel = QPlainTextEdit(self.centralwidget)
        self.log_bar_panel.setObjectName(u"log_bar_panel")
        self.log_bar_panel.setMaximumSize(QSize(16777215, 100))

        self.verticalLayout.addWidget(self.log_bar_panel)

        Form.setCentralWidget(self.centralwidget)

        self.retranslateUi(Form)

        self.validation_settings_stacked.setCurrentIndex(1)


        QMetaObject.connectSlotsByName(Form)
    # setupUi

    def retranslateUi(self, Form):
        Form.setWindowTitle(QCoreApplication.translate("Form", u"Form", None))
        self.validation_page_btn.setText(QCoreApplication.translate("Form", u"Validation", None))
        self.settings_page_btn.setText(QCoreApplication.translate("Form", u"Settings", None))
        self.label.setText(QCoreApplication.translate("Form", u"TextLabel", None))
        self.RefContext_btn.setText(QCoreApplication.translate("Form", u"RefContext", None))
        self.ROIs_btn.setText(QCoreApplication.translate("Form", u"ROIs", None))
        self.addROI_btn.setText("")
        self.copyROI_btn.setText("")
        self.delROI_btn.setText("")
        self.Save_btn.setText("")
    # retranslateUi

