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
    QLineEdit, QMainWindow, QPlainTextEdit, QPushButton,
    QSizePolicy, QSpacerItem, QSplitter, QStackedWidget,
    QVBoxLayout, QWidget)

class Ui_mainWindow(object):
    def setupUi(self, mainWindow):
        if not mainWindow.objectName():
            mainWindow.setObjectName(u"mainWindow")
        mainWindow.resize(1740, 841)
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(mainWindow.sizePolicy().hasHeightForWidth())
        mainWindow.setSizePolicy(sizePolicy)
        mainWindow.setStyleSheet(u"QPushButton {padding: 10px 10px;}")
        self.centralwidget = QWidget(mainWindow)
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
        self.settings_validation_page_btns = QButtonGroup(mainWindow)
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

        self.splitter_2 = QSplitter(self.centralwidget)
        self.splitter_2.setObjectName(u"splitter_2")
        self.splitter_2.setOrientation(Qt.Orientation.Vertical)
        self.splitter_2.setChildrenCollapsible(False)
        self.validation_settings_stacked = QStackedWidget(self.splitter_2)
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
        self.splitter.setChildrenCollapsible(False)
        self.main_img = QLabel(self.splitter)
        self.main_img.setObjectName(u"main_img")
        sizePolicy.setHeightForWidth(self.main_img.sizePolicy().hasHeightForWidth())
        self.main_img.setSizePolicy(sizePolicy)
        self.main_img.setMinimumSize(QSize(1000, 0))
        self.splitter.addWidget(self.main_img)
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

        self.RefContext_page_btn = QPushButton(self.settings_bar)
        self.RefContext_ROIs_page_btns = QButtonGroup(mainWindow)
        self.RefContext_ROIs_page_btns.setObjectName(u"RefContext_ROIs_page_btns")
        self.RefContext_ROIs_page_btns.addButton(self.RefContext_page_btn)
        self.RefContext_page_btn.setObjectName(u"RefContext_page_btn")
        sizePolicy5 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Expanding)
        sizePolicy5.setHorizontalStretch(0)
        sizePolicy5.setVerticalStretch(0)
        sizePolicy5.setHeightForWidth(self.RefContext_page_btn.sizePolicy().hasHeightForWidth())
        self.RefContext_page_btn.setSizePolicy(sizePolicy5)
        self.RefContext_page_btn.setMinimumSize(QSize(100, 0))

        self.horizontalLayout_3.addWidget(self.RefContext_page_btn)

        self.ROIs_page_btn = QPushButton(self.settings_bar)
        self.RefContext_ROIs_page_btns.addButton(self.ROIs_page_btn)
        self.ROIs_page_btn.setObjectName(u"ROIs_page_btn")
        sizePolicy5.setHeightForWidth(self.ROIs_page_btn.sizePolicy().hasHeightForWidth())
        self.ROIs_page_btn.setSizePolicy(sizePolicy5)
        self.ROIs_page_btn.setMinimumSize(QSize(100, 0))

        self.horizontalLayout_3.addWidget(self.ROIs_page_btn)


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
        self.verticalLayout_6 = QVBoxLayout(self.RefContext_page)
        self.verticalLayout_6.setSpacing(0)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.verticalLayout_6.setContentsMargins(0, 0, 0, 0)
        self.RefContext_settings_bar = QWidget(self.RefContext_page)
        self.RefContext_settings_bar.setObjectName(u"RefContext_settings_bar")
        sizePolicy6.setHeightForWidth(self.RefContext_settings_bar.sizePolicy().hasHeightForWidth())
        self.RefContext_settings_bar.setSizePolicy(sizePolicy6)
        self.RefContext_settings_bar.setMaximumSize(QSize(16777215, 50))
        self.RefContext_settings_bar.setStyleSheet(u"background-color:  rgb(189, 189, 189);")
        self.horizontalLayout_2 = QHBoxLayout(self.RefContext_settings_bar)
        self.horizontalLayout_2.setSpacing(0)
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.loadRefContext_btn = QPushButton(self.RefContext_settings_bar)
        self.loadRefContext_btn.setObjectName(u"loadRefContext_btn")
        sizePolicy5.setHeightForWidth(self.loadRefContext_btn.sizePolicy().hasHeightForWidth())
        self.loadRefContext_btn.setSizePolicy(sizePolicy5)
        self.loadRefContext_btn.setMinimumSize(QSize(50, 0))
        self.loadRefContext_btn.setMaximumSize(QSize(50, 16777215))
        icon = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.EditFind))
        self.loadRefContext_btn.setIcon(icon)
        self.loadRefContext_btn.setIconSize(QSize(30, 30))

        self.horizontalLayout_2.addWidget(self.loadRefContext_btn)

        self.saveRefContext_btn = QPushButton(self.RefContext_settings_bar)
        self.saveRefContext_btn.setObjectName(u"saveRefContext_btn")
        sizePolicy5.setHeightForWidth(self.saveRefContext_btn.sizePolicy().hasHeightForWidth())
        self.saveRefContext_btn.setSizePolicy(sizePolicy5)
        self.saveRefContext_btn.setMinimumSize(QSize(50, 0))
        self.saveRefContext_btn.setMaximumSize(QSize(50, 16777215))
        icon1 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.DocumentSave))
        self.saveRefContext_btn.setIcon(icon1)
        self.saveRefContext_btn.setIconSize(QSize(30, 30))

        self.horizontalLayout_2.addWidget(self.saveRefContext_btn)

        self.horizontalSpacer_4 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_4)


        self.verticalLayout_6.addWidget(self.RefContext_settings_bar)

        self.widget_2 = QWidget(self.RefContext_page)
        self.widget_2.setObjectName(u"widget_2")
        sizePolicy4.setHeightForWidth(self.widget_2.sizePolicy().hasHeightForWidth())
        self.widget_2.setSizePolicy(sizePolicy4)
        self.widget_2.setMinimumSize(QSize(0, 50))
        self.widget_2.setMaximumSize(QSize(16777215, 50))
        self.horizontalLayout_6 = QHBoxLayout(self.widget_2)
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.label_3 = QLabel(self.widget_2)
        self.label_3.setObjectName(u"label_3")

        self.horizontalLayout_6.addWidget(self.label_3)

        self.RefContext_filename_edit = QLineEdit(self.widget_2)
        self.RefContext_filename_edit.setObjectName(u"RefContext_filename_edit")

        self.horizontalLayout_6.addWidget(self.RefContext_filename_edit)


        self.verticalLayout_6.addWidget(self.widget_2)

        self.widget_4 = QWidget(self.RefContext_page)
        self.widget_4.setObjectName(u"widget_4")
        sizePolicy4.setHeightForWidth(self.widget_4.sizePolicy().hasHeightForWidth())
        self.widget_4.setSizePolicy(sizePolicy4)
        self.widget_4.setMinimumSize(QSize(0, 50))
        self.widget_4.setMaximumSize(QSize(16777215, 50))
        self.horizontalLayout_7 = QHBoxLayout(self.widget_4)
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.label_4 = QLabel(self.widget_4)
        self.label_4.setObjectName(u"label_4")

        self.horizontalLayout_7.addWidget(self.label_4)

        self.ref_img_name_edit = QLineEdit(self.widget_4)
        self.ref_img_name_edit.setObjectName(u"ref_img_name_edit")

        self.horizontalLayout_7.addWidget(self.ref_img_name_edit)


        self.verticalLayout_6.addWidget(self.widget_4)

        self.widget_5 = QWidget(self.RefContext_page)
        self.widget_5.setObjectName(u"widget_5")
        sizePolicy4.setHeightForWidth(self.widget_5.sizePolicy().hasHeightForWidth())
        self.widget_5.setSizePolicy(sizePolicy4)
        self.widget_5.setMinimumSize(QSize(0, 50))
        self.widget_5.setMaximumSize(QSize(16777215, 50))
        self.horizontalLayout_8 = QHBoxLayout(self.widget_5)
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.label_5 = QLabel(self.widget_5)
        self.label_5.setObjectName(u"label_5")

        self.horizontalLayout_8.addWidget(self.label_5)

        self.ref_bin_img_name_edit = QLineEdit(self.widget_5)
        self.ref_bin_img_name_edit.setObjectName(u"ref_bin_img_name_edit")

        self.horizontalLayout_8.addWidget(self.ref_bin_img_name_edit)


        self.verticalLayout_6.addWidget(self.widget_5)

        self.widget_6 = QWidget(self.RefContext_page)
        self.widget_6.setObjectName(u"widget_6")
        sizePolicy4.setHeightForWidth(self.widget_6.sizePolicy().hasHeightForWidth())
        self.widget_6.setSizePolicy(sizePolicy4)
        self.widget_6.setMinimumSize(QSize(0, 50))
        self.widget_6.setMaximumSize(QSize(16777215, 50))
        self.horizontalLayout_9 = QHBoxLayout(self.widget_6)
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.select_RefContext_params_btn = QPushButton(self.widget_6)
        self.select_RefContext_params_btn.setObjectName(u"select_RefContext_params_btn")
        sizePolicy7 = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy7.setHorizontalStretch(0)
        sizePolicy7.setVerticalStretch(0)
        sizePolicy7.setHeightForWidth(self.select_RefContext_params_btn.sizePolicy().hasHeightForWidth())
        self.select_RefContext_params_btn.setSizePolicy(sizePolicy7)
        self.select_RefContext_params_btn.setMinimumSize(QSize(20, 20))
        self.select_RefContext_params_btn.setMaximumSize(QSize(20, 20))
        icon2 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.DocumentProperties))
        self.select_RefContext_params_btn.setIcon(icon2)
        self.select_RefContext_params_btn.setIconSize(QSize(10, 10))

        self.horizontalLayout_9.addWidget(self.select_RefContext_params_btn)

        self.label_6 = QLabel(self.widget_6)
        self.label_6.setObjectName(u"label_6")

        self.horizontalLayout_9.addWidget(self.label_6)


        self.verticalLayout_6.addWidget(self.widget_6)

        self.widget_7 = QWidget(self.RefContext_page)
        self.widget_7.setObjectName(u"widget_7")
        sizePolicy4.setHeightForWidth(self.widget_7.sizePolicy().hasHeightForWidth())
        self.widget_7.setSizePolicy(sizePolicy4)
        self.widget_7.setMinimumSize(QSize(0, 50))
        self.widget_7.setMaximumSize(QSize(16777215, 50))
        self.horizontalLayout_10 = QHBoxLayout(self.widget_7)
        self.horizontalLayout_10.setObjectName(u"horizontalLayout_10")
        self.label_7 = QLabel(self.widget_7)
        self.label_7.setObjectName(u"label_7")

        self.horizontalLayout_10.addWidget(self.label_7)

        self.Ref_context_bin_thereshold_edit = QLineEdit(self.widget_7)
        self.Ref_context_bin_thereshold_edit.setObjectName(u"Ref_context_bin_thereshold_edit")

        self.horizontalLayout_10.addWidget(self.Ref_context_bin_thereshold_edit)


        self.verticalLayout_6.addWidget(self.widget_7)

        self.widget_8 = QWidget(self.RefContext_page)
        self.widget_8.setObjectName(u"widget_8")
        sizePolicy4.setHeightForWidth(self.widget_8.sizePolicy().hasHeightForWidth())
        self.widget_8.setSizePolicy(sizePolicy4)
        self.widget_8.setMinimumSize(QSize(0, 50))
        self.widget_8.setMaximumSize(QSize(16777215, 50))
        self.horizontalLayout_11 = QHBoxLayout(self.widget_8)
        self.horizontalLayout_11.setObjectName(u"horizontalLayout_11")
        self.label_8 = QLabel(self.widget_8)
        self.label_8.setObjectName(u"label_8")

        self.horizontalLayout_11.addWidget(self.label_8)

        self.RefContext_min_contour_length_edit = QLineEdit(self.widget_8)
        self.RefContext_min_contour_length_edit.setObjectName(u"RefContext_min_contour_length_edit")

        self.horizontalLayout_11.addWidget(self.RefContext_min_contour_length_edit)


        self.verticalLayout_6.addWidget(self.widget_8)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_6.addItem(self.verticalSpacer_2)

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
        icon3 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.ListAdd))
        self.addROI_btn.setIcon(icon3)
        self.addROI_btn.setIconSize(QSize(30, 30))

        self.horizontalLayout_4.addWidget(self.addROI_btn)

        self.copyROI_btn = QPushButton(self.ROI_settings_bar)
        self.copyROI_btn.setObjectName(u"copyROI_btn")
        sizePolicy5.setHeightForWidth(self.copyROI_btn.sizePolicy().hasHeightForWidth())
        self.copyROI_btn.setSizePolicy(sizePolicy5)
        self.copyROI_btn.setMinimumSize(QSize(50, 0))
        self.copyROI_btn.setMaximumSize(QSize(50, 16777215))
        icon4 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.EditCopy))
        self.copyROI_btn.setIcon(icon4)
        self.copyROI_btn.setIconSize(QSize(30, 30))

        self.horizontalLayout_4.addWidget(self.copyROI_btn)

        self.delROI_btn = QPushButton(self.ROI_settings_bar)
        self.delROI_btn.setObjectName(u"delROI_btn")
        sizePolicy5.setHeightForWidth(self.delROI_btn.sizePolicy().hasHeightForWidth())
        self.delROI_btn.setSizePolicy(sizePolicy5)
        self.delROI_btn.setMinimumSize(QSize(48, 0))
        self.delROI_btn.setMaximumSize(QSize(50, 16777215))
        icon5 = QIcon(QIcon.fromTheme(QIcon.ThemeIcon.EditDelete))
        self.delROI_btn.setIcon(icon5)
        self.delROI_btn.setIconSize(QSize(30, 30))

        self.horizontalLayout_4.addWidget(self.delROI_btn)

        self.saveROI_btn = QPushButton(self.ROI_settings_bar)
        self.saveROI_btn.setObjectName(u"saveROI_btn")
        sizePolicy5.setHeightForWidth(self.saveROI_btn.sizePolicy().hasHeightForWidth())
        self.saveROI_btn.setSizePolicy(sizePolicy5)
        self.saveROI_btn.setIcon(icon1)
        self.saveROI_btn.setIconSize(QSize(30, 30))

        self.horizontalLayout_4.addWidget(self.saveROI_btn)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_4.addItem(self.horizontalSpacer_3)


        self.verticalLayout_5.addWidget(self.ROI_settings_bar)

        self.widget = QWidget(self.ROI_page)
        self.widget.setObjectName(u"widget")
        sizePolicy4.setHeightForWidth(self.widget.sizePolicy().hasHeightForWidth())
        self.widget.setSizePolicy(sizePolicy4)
        self.widget.setMinimumSize(QSize(0, 50))
        self.widget.setMaximumSize(QSize(16777215, 50))
        self.horizontalLayout_5 = QHBoxLayout(self.widget)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.label_2 = QLabel(self.widget)
        self.label_2.setObjectName(u"label_2")

        self.horizontalLayout_5.addWidget(self.label_2)

        self.ROIs_filename_edit = QLineEdit(self.widget)
        self.ROIs_filename_edit.setObjectName(u"ROIs_filename_edit")

        self.horizontalLayout_5.addWidget(self.ROIs_filename_edit)


        self.verticalLayout_5.addWidget(self.widget)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_5.addItem(self.verticalSpacer)

        self.RefContext_ROI_stacked.addWidget(self.ROI_page)

        self.verticalLayout_4.addWidget(self.RefContext_ROI_stacked)

        self.splitter.addWidget(self.layoutWidget)

        self.verticalLayout_2.addWidget(self.splitter)

        self.validation_settings_stacked.addWidget(self.settings_page)
        self.splitter_2.addWidget(self.validation_settings_stacked)
        self.log_bar_panel = QPlainTextEdit(self.splitter_2)
        self.log_bar_panel.setObjectName(u"log_bar_panel")
        self.log_bar_panel.setMaximumSize(QSize(16777215, 500))
        self.splitter_2.addWidget(self.log_bar_panel)

        self.verticalLayout.addWidget(self.splitter_2)

        mainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(mainWindow)

        self.validation_settings_stacked.setCurrentIndex(1)
        self.RefContext_ROI_stacked.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(mainWindow)
    # setupUi

    def retranslateUi(self, mainWindow):
        mainWindow.setWindowTitle(QCoreApplication.translate("mainWindow", u"Form", None))
        self.validation_page_btn.setText(QCoreApplication.translate("mainWindow", u"Validation", None))
        self.settings_page_btn.setText(QCoreApplication.translate("mainWindow", u"Settings", None))
        self.main_img.setText(QCoreApplication.translate("mainWindow", u"TextLabel", None))
        self.RefContext_page_btn.setText(QCoreApplication.translate("mainWindow", u"RefContext", None))
        self.ROIs_page_btn.setText(QCoreApplication.translate("mainWindow", u"ROIs", None))
        self.loadRefContext_btn.setText("")
        self.saveRefContext_btn.setText("")
        self.label_3.setText(QCoreApplication.translate("mainWindow", u"Filename:", None))
        self.label_4.setText(QCoreApplication.translate("mainWindow", u"Ref_img_name:", None))
        self.label_5.setText(QCoreApplication.translate("mainWindow", u"Ref_bin_img_name:", None))
        self.select_RefContext_params_btn.setText("")
        self.label_6.setText(QCoreApplication.translate("mainWindow", u"Params:", None))
        self.label_7.setText(QCoreApplication.translate("mainWindow", u"bin_thereshold:", None))
        self.label_8.setText(QCoreApplication.translate("mainWindow", u"min_contour_length:", None))
        self.addROI_btn.setText("")
        self.copyROI_btn.setText("")
        self.delROI_btn.setText("")
        self.saveROI_btn.setText("")
        self.label_2.setText(QCoreApplication.translate("mainWindow", u"Filename:", None))
    # retranslateUi

