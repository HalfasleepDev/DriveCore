# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'MainWindowfkCUmi.ui'
##
## Created by: Qt User Interface Compiler version 6.9.0
##
## WARNING! All changes made in this file will be lost when recompiling UI file!
################################################################################

# TODO: UPDATE THE STYLESHEET AND QT DESIGNER ELEMENTS!

from PySide6.QtCore import (QCoreApplication, QDate, QDateTime, QLocale,
    QMetaObject, QObject, QPoint, QRect,
    QSize, QTime, QUrl, Qt)
from PySide6.QtGui import (QBrush, QColor, QConicalGradient, QCursor,
    QFont, QFontDatabase, QGradient, QIcon,
    QImage, QKeySequence, QLinearGradient, QPainter,
    QPalette, QPixmap, QRadialGradient, QTransform)
from PySide6.QtWidgets import (QApplication, QComboBox, QFrame, QGridLayout,
    QGroupBox, QHBoxLayout, QLabel, QLayout,
    QLineEdit, QMainWindow, QPushButton, QSizePolicy,
    QSlider, QSpacerItem, QStackedWidget, QVBoxLayout,
    QWidget)
import resource

from appFunctions import PageWithKeyEvents

from appUiElements import (GitHubInfoPanel, SystemLogViewer, CalibrationWidget,
    DescriptionWidget, LogConsoleWidget, DriveAssistWidget, PRNDWidget,
    SpeedometerWidget, SteeringPathWidget, CarConnectWidget)

import os

os.environ["QT_QPA_PLATFORM"] = "xcb"

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1425, 1115)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        # TODO: UPDATE STYLESHEET
        self.centralwidget.setStyleSheet(u"/*========Settings page=======*/\n"
"QLabel#settingsHeaderLabel{\n"
"	color: #f1f3f3;\n"
"}\n"
"Line#keysettingsHeaderLine{\n"
"	color: #1e1e21;\n"
"}\n"
"QPushButton#openCVSettingsBtn{\n"
"	background-color: #1e1e21;\n"
"	border: 1px #1e1e21;\n"
"	border-radius: 5px;\n"
"	color: #f1f3f3;\n"
"}\n"
"QPushButton#vehicleTuningBtn{\n"
"	background-color: #1e1e21;\n"
"	border: 1px #1e1e21;\n"
"	border-radius: 5px;\n"
"	color: #f1f3f3;\n"
"}\n"
"\n"
"/*OpenCV Settings*/\n"
"QLabel#OpenCVHeaderLabel{\n"
"	color: #f1f3f3;\n"
"}\n"
"Line#OpenCVHeaderLine{\n"
"	color: #1e1e21;\n"
"}\n"
"\n"
"QLabel#DebugCVHeaderLabel{\n"
"	color: #f1f3f3;\n"
"}\n"
"\n"
"/*ObjectVisBtn*/\n"
"QPushButton#ObjectVisBtn{\n"
"	background-color: #1e1e21;\n"
"	border: 1px #1e1e21;\n"
"	border-radius: 5px;\n"
"	color: #f1f3f3;\n"
"}\n"
"QPushButton#ObjectVisBtn:pressed{\n"
"	background-color: #7a63ff;\n"
"	border: 1px #7a63ff;\n"
"	border-radius: 5px;\n"
"	color: #f1f3f3;\n"
"}\n"
"/*FloorVisBtn*/\n"
"QPushButton#FloorVisBtn{\n"
"	background-col"
                        "or: #1e1e21;\n"
"	border: 1px #1e1e21;\n"
"	border-radius: 5px;\n"
"	color: #f1f3f3;\n"
"}\n"
"QPushButton#FloorVisBtn:pressed{\n"
"	background-color: #7a63ff;\n"
"	border: 1px #7a63ff;\n"
"	border-radius: 5px;\n"
"	color: #f1f3f3;\n"
"}\n"
"/*KalmanCenterVisBtn*/\n"
"QPushButton#KalmanCenterVisBtn{\n"
"	background-color: #1e1e21;\n"
"	border: 1px #1e1e21;\n"
"	border-radius: 5px;\n"
"	color: #f1f3f3;\n"
"}\n"
"QPushButton#KalmanCenterVisBtn:pressed{\n"
"	background-color: #7a63ff;\n"
"	border: 1px #7a63ff;\n"
"	border-radius: 5px;\n"
"	color: #f1f3f3;\n"
"}\n"
"/*AmbientVisBtn*/\n"
"QPushButton#AmbientVisBtn{\n"
"	background-color: #1e1e21;\n"
"	border: 1px #1e1e21;\n"
"	border-radius: 5px;\n"
"	color: #f1f3f3;\n"
"}\n"
"QPushButton#AmbientVisBtn:pressed{\n"
"	background-color: #7a63ff;\n"
"	border: 1px #7a63ff;\n"
"	border-radius: 5px;\n"
"	color: #f1f3f3;\n"
"}\n"
"/*FloorSampleVisBtn*/\n"
"QPushButton#FloorSampleVisBtn{\n"
"	background-color: #1e1e21;\n"
"	border: 1px #1e1e21;\n"
"	border-radius: 5px;\n"
""
                        "	color: #f1f3f3;\n"
"}\n"
"QPushButton#FloorSampleVisBtn:pressed{\n"
"	background-color: #7a63ff;\n"
"	border: 1px #7a63ff;\n"
"	border-radius: 5px;\n"
"	color: #f1f3f3;\n"
"}\n"
"/*PathVisBtn*/\n"
"QPushButton#PathVisBtn{\n"
"	background-color: #1e1e21;\n"
"	border: 1px #1e1e21;\n"
"	border-radius: 5px;\n"
"	color: #f1f3f3;\n"
"}\n"
"QPushButton#PathVisBtn:pressed{\n"
"	background-color: #7a63ff;\n"
"	border: 1px #7a63ff;\n"
"	border-radius: 5px;\n"
"	color: #f1f3f3;\n"
"}\n"
"/*CollisionAssistBtn*/\n"
"QPushButton#CollisionAssistBtn{\n"
"	background-color: #1e1e21;\n"
"	border: 1px #1e1e21;\n"
"	border-radius: 5px;\n"
"	color: #f1f3f3;\n"
"}\n"
"QPushButton#CollisionAssistBtn:pressed{\n"
"	background-color: #7a63ff;\n"
"	border: 1px #7a63ff;\n"
"	border-radius: 5px;\n"
"	color: #f1f3f3;\n"
"}\n"
"\n"
"/*HSV Sliders*/\n"
"QSlider::handle:horizontal{\n"
"	background: #7a63ff;\n"
"	width: 10px;\n"
"	margin: -5px -1px;\n"
"	border-radius: 5px;\n"
"}\n"
"QSlider::add-page:horizontal{\n"
"	background: #f1f3f3;\n"
""
                        "	border-radius: 2px;\n"
"}\n"
"QSlider::sub-page:horizontal{\n"
"	background: #7a63ff;\n"
"	border-radius: 2px;\n"
"}\n"
"\n"
"QWidget#HSVSliderWidget{\n"
"	background-color: #1e1e21;\n"
"	border: 1px #1e1e21;\n"
"	border-radius: 5px;\n"
"	color: #f1f3f3;\n"
"}\n"
"QLabel#HRowLabel{\n"
"	color: #f1f3f3;\n"
"}\n"
"QLabel#HRowValueLabel{\n"
"	color: #f1f3f3;\n"
"}\n"
"QLabel#SRowLabel{\n"
"	color: #f1f3f3;\n"
"}\n"
"QLabel#SRowValueLabel{\n"
"	color: #f1f3f3;\n"
"}\n"
"QLabel#VRowLabel{\n"
"	color: #f1f3f3;\n"
"}\n"
"QLabel#VRowValueLabel{\n"
"	color: #f1f3f3;\n"
"}\n"
"QLabel#HSVSettingsHeaderLabel{\n"
"	color: #f1f3f3;\n"
"}\n"
"\n"
"QLabel#CollisionAssistHeaderLabel{\n"
"	color: #f1f3f3;\n"
"}\n"
"\n"
"/*Emergency Disconnect*/\n"
"QPushButton#emergencyDisconnectBtn{\n"
"	background-color: #f1f3f3;\n"
"	color: #1e1e21;\n"
"    border-style: outset;\n"
"    border-width: 2px;\n"
"    border-radius: 30px;\n"
"    border-color: #f1f3f3;\n"
"    padding: 6px;\n"
"}\n"
"QPushButton#emergencyDisconnectBtn:pressed{\n"
""
                        "	background-color: #7a63ff;\n"
"	color: #1e1e21;\n"
"    border-style: outset;\n"
"    border-width: 2px;\n"
"    border-radius: 30px;\n"
"    border-color: #f1f3f3;\n"
"    padding: 6px;\n"
"}\n"
"QLabel#emergencyDisconnectLabel{\n"
"	color: #FF0000;\n"
"}\n"
"QWidget#currentPgrmVersionWidget{\n"
"	background-color: #1e1e21;\n"
"	border: 1px #1e1e21;\n"
"	border-radius: 15px;\n"
"}\n"
"QLabel#currentPgrmVersionLabel{\n"
"	color: #f1f3f3;\n"
"}\n"
"QWidget#currentPgrmVersionHeaderWidget{\n"
"	background-color: #7a63ff;\n"
"	border: 1px #7a63ff;\n"
"	border-radius: 15px;\n"
"}\n"
"QLabel#currentPgrmVersionHeaderLabel{\n"
"	color: #f1f3f3;\n"
"}\n"
"\n"
"\n"
"\n"
"/*=======Drive page=======*/\n"
"QWidget#videoStreamWidget{\n"
"	background-color: #f1f3f3;\n"
"}\n"
"QWidget#prndWidget{\n"
"	background-color: #1e1e21;\n"
"	border: 1px #1e1e21;\n"
"	border-radius: 15px;\n"
"}\n"
"QWidget#speedometerWidget{\n"
"	background-color: #0c0c0d;\n"
"	border: 1px #1e1e21;\n"
"	border-radius: 150px;\n"
"}\n"
"QWidget#steerAng"
                        "leWidget{\n"
"	background-color: #1e1e21;\n"
"	border: 1px #1e1e21;\n"
"	border-radius: 15px;\n"
"}\n"
"QWidget#alertAssistWidget{\n"
"	background-color: #1e1e21;\n"
"	border: 1px #1e1e21;\n"
"	border-radius: 15px;\n"
"}\n"
"\n"
"QPushButton#accelerateBtn{\n"
"	background-color: #1e1e21;\n"
"	border: 1px #1e1e21;\n"
"	border-radius: 5px;\n"
"	color: #f1f3f3;\n"
"}\n"
"QPushButton#turnLeftBtn{\n"
"	background-color: #1e1e21;\n"
"	border: 1px #1e1e21;\n"
"	border-radius: 5px;\n"
"	color: #f1f3f3;\n"
"}\n"
"QPushButton#reverseBtn{\n"
"	background-color: #1e1e21;\n"
"	border: 1px #1e1e21;\n"
"	border-radius: 5px;\n"
"	color: #f1f3f3;\n"
"}\n"
"QPushButton#turnRightBtn{\n"
"	background-color: #1e1e21;\n"
"	border: 1px #1e1e21;\n"
"	border-radius: 5px;\n"
"	color: #f1f3f3;\n"
"}\n"
"QPushButton#brakeBtn{\n"
"	background-color: #1e1e21;\n"
"	border: 1px #1e1e21;\n"
"	border-radius: 5px;\n"
"	color: #f1f3f3;\n"
"}\n"
"\n"
"QWidget#connectionVehicleTypeWidget{\n"
"	background-color: #1e1e21;\n"
"	border: 1px #1e1e21;\n"
""
                        "	border-radius: 15px;\n"
"}\n"
"QLabel#vehicleTypeLabel{\n"
"	color: #f1f3f3;\n"
"}\n"
"QWidget#currentVehicleLblWidget{\n"
"	background-color: #7a63ff;\n"
"	border: 1px #7a63ff;\n"
"	border-radius: 15px;\n"
"}\n"
"QLabel#currentVehicleLabel{\n"
"	color: #f1f3f3;\n"
"}\n"
"QWidget#vehicleAlertLogWidget{\n"
"	background-color: #1e1e21;\n"
"	border: 1px #1e1e21;\n"
"	border-radius: 15px;\n"
"}\n"
"\n"
"/*=======Center home widget=======*/\n"
"QWidget#connectionLogWidget{\n"
"	background-color: #1e1e21;\n"
"	border: 1px #1e1e21;\n"
"	border-radius: 15px;\n"
"}\n"
"\n"
"/*=======Left home widget=======*/\n"
"QWidget#loginWidget{\n"
"	background-color: #7a63ff;\n"
"	border-radius: 15px;\n"
"}\n"
"\n"
"/*=======Right home widget=======*/\n"
"QWidget#projectInfoWidget {\n"
"	background-color: #74e1ef;\n"
"	border: 1px #74e1ef;\n"
"	border-radius: 15px;"
                        "\n"
"}\n"
"QLabel#aboutTitle {\n"
"	color: #1e1e21;\n"
"}\n"
"QLabel#projectTitle {\n"
"	color: #1e1e21;\n"
"}\n"
"QLabel#githubLink {\n"
"	color: #1e1e21;\n"
"}\n"
"QLabel#description {\n"
"	color: #1e1e21;\n"
"}\n"
"\n"
"\n"
"\n"
"/*=======Left menu=======*/\n"
"QWidget#leftMenu {\n"
"	background-color: #1e1e21;\n"
"}\n"
"\n"
"/*=======Left menu buttons=======*/\n"
"QPushButton#homeBtn {\n"
"	background-color: #f1f3f3;\n"
#"    border-style: outset;\n"
#"    border-width: 2px;\n"
"    border-radius: 30px;\n"
#"    border-color: #f1f3f3;\n"
"    padding: 6px;\n"
"}\n"
"QPushButton#driveBtn {\n"
"	background-color: #f1f3f3;\n"
#"    border-style: outset;\n"
#"    border-width: 2px;\n"
"    border-radius: 30px;\n"
#"    border-color: #f1f3f3;\n"
"    padding: 6px;\n"
"}\n"
"QPushButton#settingsBtn {\n"
"	background-color: #f1f3f3;\n"
#"    border-style: outset;\n"
#"    border-width: 2px;\n"
"    border-radius: 30px;\n"
#"    border-color: #f1f3f3;\n"
#"    padding: 6px;\n"
"}\n"
"QPushButton#logBtn {\n"
"	background-col"
                        "or: #f1f3f3;\n"
#"    border-style: outset;\n"
#"    border-width: 2px;\n"
"    border-radius: 30px;\n"
#"    border-color: #f1f3f3;\n"
"    padding: 6px;\n"
"}\n"
"\n"
"/*=======Main background=======*/\n"
"\n"
"QWidget#centralWidget{\n"
"	background-color: #0c0c0d;\n"
"}\n"
"QWidget#mainPage{\n"
"	background-color: #0c0c0d;\n"
"}\n"
"QWidget#homePage{\n"
"	background-color: #0c0c0d;\n"
"}\n"
"QWidget#drivePage{\n"
"	background-color: #0c0c0d;\n"
"}")
        self.horizontalLayout = QHBoxLayout(self.centralwidget)
        self.horizontalLayout.setSpacing(0)
        self.horizontalLayout.setObjectName(u"horizontalLayout")
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.leftMenu = QWidget(self.centralwidget)
        self.leftMenu.setObjectName(u"leftMenu")
        self.leftMenu.setMinimumSize(QSize(100, 0))
        self.verticalLayout = QVBoxLayout(self.leftMenu)
        self.verticalLayout.setSpacing(0)
        self.verticalLayout.setObjectName(u"verticalLayout")
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.widget_2 = QWidget(self.leftMenu)
        self.widget_2.setObjectName(u"widget_2")
        self.verticalLayout_2 = QVBoxLayout(self.widget_2)
        self.verticalLayout_2.setObjectName(u"verticalLayout_2")
        self.homeBtn = QPushButton(self.widget_2)
        self.homeBtn.setObjectName(u"homeBtn")
        sizePolicy = QSizePolicy(QSizePolicy.Policy.Fixed, QSizePolicy.Policy.Fixed)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.homeBtn.sizePolicy().hasHeightForWidth())
        self.homeBtn.setSizePolicy(sizePolicy)
        self.homeBtn.setMinimumSize(QSize(80, 80))
        self.homeBtn.setToolTipDuration(1)
        self.homeBtn.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        icon = QIcon()
        icon.addFile(u"D-14/Client-Side/client-app/icons/solar--home-2-bold.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.homeBtn.setIcon(icon)
        self.homeBtn.setIconSize(QSize(60, 60))
        self.homeBtn.setCheckable(True)
        self.homeBtn.setChecked(False)

        self.verticalLayout_2.addWidget(self.homeBtn)

        self.verticalSpacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer)

        self.driveBtn = QPushButton(self.widget_2)
        self.driveBtn.setObjectName(u"driveBtn")
        sizePolicy.setHeightForWidth(self.driveBtn.sizePolicy().hasHeightForWidth())
        self.driveBtn.setSizePolicy(sizePolicy)
        self.driveBtn.setMinimumSize(QSize(80, 80))
        icon1 = QIcon()
        icon1.addFile(u"D-14/Client-Side/client-app/icons/solar--wheel-angle-bold-duotone.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.driveBtn.setIcon(icon1)
        self.driveBtn.setIconSize(QSize(60, 60))
        self.driveBtn.setCheckable(True)

        self.verticalLayout_2.addWidget(self.driveBtn)

        self.verticalSpacer_9 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_2.addItem(self.verticalSpacer_9)

        self.logBtn = QPushButton(self.widget_2)
        self.logBtn.setObjectName(u"logBtn")
        sizePolicy.setHeightForWidth(self.logBtn.sizePolicy().hasHeightForWidth())
        self.logBtn.setSizePolicy(sizePolicy)
        self.logBtn.setMinimumSize(QSize(80, 80))
        icon5 = QIcon()
        icon5.addFile(u"D-14/Client-Side/client-app/icons/solar--documents-minimalistic-bold-duotone.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.logBtn.setIcon(icon5)
        self.logBtn.setIconSize(QSize(60, 60))
        self.logBtn.setCheckable(True)
        self.logBtn.setChecked(False)

        self.verticalLayout_2.addWidget(self.logBtn)


        self.verticalLayout.addWidget(self.widget_2, 0, Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignTop)

        self.verticalSpacer_2 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout.addItem(self.verticalSpacer_2)

        self.widget_3 = QWidget(self.leftMenu)
        self.widget_3.setObjectName(u"widget_3")
        self.verticalLayout_3 = QVBoxLayout(self.widget_3)
        self.verticalLayout_3.setObjectName(u"verticalLayout_3")
        self.settingsBtn = QPushButton(self.widget_3)
        self.settingsBtn.setObjectName(u"settingsBtn")
        sizePolicy.setHeightForWidth(self.settingsBtn.sizePolicy().hasHeightForWidth())
        self.settingsBtn.setSizePolicy(sizePolicy)
        self.settingsBtn.setMinimumSize(QSize(80, 80))
        icon2 = QIcon()
        icon2.addFile(u"D-14/Client-Side/client-app/icons/solar--settings-bold.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.settingsBtn.setIcon(icon2)
        self.settingsBtn.setIconSize(QSize(60, 60))
        self.settingsBtn.setCheckable(True)

        self.verticalLayout_3.addWidget(self.settingsBtn)


        self.verticalLayout.addWidget(self.widget_3, 0, Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignBottom)


        self.horizontalLayout.addWidget(self.leftMenu, 0, Qt.AlignmentFlag.AlignLeft)

        self.mainPage = QWidget(self.centralwidget)
        self.mainPage.setObjectName(u"mainPage")
        self.verticalLayout_4 = QVBoxLayout(self.mainPage)
        self.verticalLayout_4.setObjectName(u"verticalLayout_4")
        self.stackedWidget = QStackedWidget(self.mainPage)
        self.stackedWidget.setObjectName(u"stackedWidget")
        self.homePage = QWidget()
        self.homePage.setObjectName(u"homePage")
        self.horizontalLayout_2 = QHBoxLayout(self.homePage)
        self.horizontalLayout_2.setSpacing(3) # 0
        self.horizontalLayout_2.setObjectName(u"horizontalLayout_2")
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.leftHomeWidget = QWidget(self.homePage)
        self.leftHomeWidget.setObjectName(u"leftHomeWidget")
        self.verticalLayout_8 = QVBoxLayout(self.leftHomeWidget)
        self.verticalLayout_8.setSpacing(20)
        self.verticalLayout_8.setObjectName(u"verticalLayout_8")
        self.verticalLayout_8.setContentsMargins(50, -1, 50, -1)
        self.verticalSpacer_5 = QSpacerItem(20, 155, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_8.addItem(self.verticalSpacer_5)

        self.loginWidget = QWidget(self.leftHomeWidget)
        self.loginWidget.setObjectName(u"loginWidget")
        self.loginWidget.setMinimumSize(QSize(400, 400))
        self.loginWidget.setMaximumSize(QSize(400, 400))

        self.verticalLayout_8.addWidget(self.loginWidget)

        self.verticalSpacer_3 = QSpacerItem(20, 155, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_8.addItem(self.verticalSpacer_3)


        self.horizontalLayout_2.addWidget(self.leftHomeWidget)

        self.centerHomeWidget = QWidget(self.homePage)
        self.centerHomeWidget.setObjectName(u"centerHomeWidget")
        self.centerHomeWidget.setMinimumSize(QSize(0, 0))
        self.centerHomeWidget.setMaximumSize(QSize(16777215, 16777215))
        self.verticalLayout_20 = QVBoxLayout(self.centerHomeWidget)
        self.verticalLayout_20.setSpacing(20)
        self.verticalLayout_20.setObjectName(u"verticalLayout_20")
        self.verticalLayout_20.setContentsMargins(0, 0, 20, 0)
        self.verticalSpacer_12 = QSpacerItem(20, 301, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

        self.verticalLayout_20.addItem(self.verticalSpacer_12)

        self.connectionLogWidget = QWidget(self.centerHomeWidget)
        self.connectionLogWidget.setObjectName(u"connectionLogWidget")
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.connectionLogWidget.sizePolicy().hasHeightForWidth())
        self.connectionLogWidget.setSizePolicy(sizePolicy1)
        self.connectionLogWidget.setMinimumSize(QSize(400, 450))
        self.connectionLogWidget.setMaximumSize(QSize(400, 620))

        self.verticalLayout_20.addWidget(self.connectionLogWidget)

        self.verticalSpacer_11 = QSpacerItem(20, 300, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

        self.verticalLayout_20.addItem(self.verticalSpacer_11)


        self.horizontalLayout_2.addWidget(self.centerHomeWidget, 0, Qt.AlignmentFlag.AlignLeft)

        self.horizontalSpacer_4 = QSpacerItem(10000, 20, QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_2.addItem(self.horizontalSpacer_4)

        self.rightHomeWidget = QWidget(self.homePage)
        self.rightHomeWidget.setObjectName(u"rightHomeWidget")
        self.rightHomeWidget.setMinimumSize(QSize(400, 0))
        self.rightHomeWidget.setMaximumSize(QSize(500, 16777215))
        self.verticalLayout_7 = QVBoxLayout(self.rightHomeWidget)
        self.verticalLayout_7.setSpacing(0)
        self.verticalLayout_7.setObjectName(u"verticalLayout_7")
        self.verticalLayout_7.setContentsMargins(0, 0, 0, 0)
        self.widget_6 = QWidget(self.rightHomeWidget)
        self.widget_6.setObjectName(u"widget_6")
        self.widget_6.setMinimumSize(QSize(350, 0))
        self.verticalLayout_9 = QVBoxLayout(self.widget_6)
        self.verticalLayout_9.setObjectName(u"verticalLayout_9")
        self.verticalLayout_9.setContentsMargins(0, -1, 0, -1)
        self.label_2 = QLabel(self.widget_6)
        self.label_2.setObjectName(u"label_2")
        self.label_2.setMinimumSize(QSize(320, 240))
        self.label_2.setMaximumSize(QSize(320, 240))
        self.label_2.setPixmap(QPixmap(u"D-14/Client-Side/client-app/icons/DriveCore-Logo-V1-2.png"))
        self.label_2.setScaledContents(True)

        self.verticalLayout_9.addWidget(self.label_2, 0, Qt.AlignmentFlag.AlignHCenter)

        self.projectInfoWidget = QWidget(self.widget_6)

        self.projectInfoWidget.setObjectName(u"projectInfoWidget")
        self.projectInfoWidget.setMinimumSize(QSize(350, 400))
        self.verticalLayout_10 = QVBoxLayout(self.projectInfoWidget)
        self.verticalLayout_10.setObjectName(u"verticalLayout_10")
        self.verticalLayout_10.setContentsMargins(0, 0, 0, 0)

        # * IMPORTANT: GitHubInfoPanel new widget
        self.projectInfoWidgetCustom = GitHubInfoPanel("https://github.com/HalfasleepDev/DriveCore")
        self.verticalLayout_10.addWidget(self.projectInfoWidgetCustom)

        # !REMOVE IN QT DESIGNER
        '''self.projectTitle = QLabel(self.projectInfoWidget)
        self.projectTitle.setObjectName(u"projectTitle")
        self.projectTitle.setMaximumSize(QSize(300, 30))
        font1 = QFont()
        font1.setPointSize(15)
        self.projectTitle.setFont(font1)

        self.verticalLayout_10.addWidget(self.projectTitle)

        self.line_2 = QFrame(self.projectInfoWidget)
        self.line_2.setObjectName(u"line_2")
        self.line_2.setFrameShape(QFrame.Shape.HLine)
        self.line_2.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_10.addWidget(self.line_2)

        self.githubLink = QLabel(self.projectInfoWidget)
        self.githubLink.setObjectName(u"githubLink")
        self.githubLink.setMinimumSize(QSize(0, 200))
        self.githubLink.setMaximumSize(QSize(16777215, 40))
        self.githubLink.setTextFormat(Qt.TextFormat.MarkdownText)
        self.githubLink.setAlignment(Qt.AlignmentFlag.AlignLeading|Qt.AlignmentFlag.AlignLeft|Qt.AlignmentFlag.AlignTop)
        self.githubLink.setWordWrap(True)
        self.githubLink.setMargin(10)
        self.githubLink.setOpenExternalLinks(True)
        self.githubLink.setTextInteractionFlags(Qt.TextInteractionFlag.LinksAccessibleByMouse|Qt.TextInteractionFlag.TextSelectableByMouse)

        self.verticalLayout_10.addWidget(self.githubLink, 0, Qt.AlignmentFlag.AlignTop)

        self.verticalSpacer_6 = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_10.addItem(self.verticalSpacer_6)

        self.aboutTitle = QLabel(self.projectInfoWidget)
        self.aboutTitle.setObjectName(u"aboutTitle")
        self.aboutTitle.setMaximumSize(QSize(300, 30))
        self.aboutTitle.setFont(font1)

        self.verticalLayout_10.addWidget(self.aboutTitle)

        self.line = QFrame(self.projectInfoWidget)
        self.line.setObjectName(u"line")
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_10.addWidget(self.line)

        self.description = QLabel(self.projectInfoWidget)
        self.description.setObjectName(u"description")
        self.description.setMinimumSize(QSize(0, 0))
        font2 = QFont()
        font2.setPointSize(11)
        self.description.setFont(font2)
        self.description.setTextFormat(Qt.TextFormat.MarkdownText)
        self.description.setWordWrap(True)
        self.description.setMargin(10)

        self.verticalLayout_10.addWidget(self.description)'''
        font1 = QFont()
        font1.setPointSize(15)
        font2 = QFont()
        font2.setPointSize(11)


        self.verticalLayout_9.addWidget(self.projectInfoWidget, 0, Qt.AlignmentFlag.AlignHCenter)


        self.verticalLayout_7.addWidget(self.widget_6, 0, Qt.AlignmentFlag.AlignHCenter)


        self.horizontalLayout_2.addWidget(self.rightHomeWidget)

        self.stackedWidget.addWidget(self.homePage)
        self.settingsPage = QWidget()
        self.settingsPage.setObjectName(u"settingsPage")
        self.horizontalLayout_5 = QHBoxLayout(self.settingsPage)
        self.horizontalLayout_5.setObjectName(u"horizontalLayout_5")
        self.settingsLeftWidget = QWidget(self.settingsPage)
        self.settingsLeftWidget.setObjectName(u"settingsLeftWidget")
        self.settingsLeftWidget.setMaximumSize(QSize(825, 16777215))
        self.verticalLayout_15 = QVBoxLayout(self.settingsLeftWidget)
        self.verticalLayout_15.setSpacing(10)
        self.verticalLayout_15.setObjectName(u"verticalLayout_15")
        self.widget = QWidget(self.settingsLeftWidget)
        self.widget.setObjectName(u"widget")
        self.horizontalLayout_17 = QHBoxLayout(self.widget)
        self.horizontalLayout_17.setObjectName(u"horizontalLayout_17")
        self.horizontalLayout_17.setContentsMargins(0, 0, 0, 0)
        self.settingsHeaderLabel = QLabel(self.widget)
        self.settingsHeaderLabel.setObjectName(u"settingsHeaderLabel")
        font3 = QFont()
        font3.setPointSize(24)
        self.settingsHeaderLabel.setFont(font3)

        self.horizontalLayout_17.addWidget(self.settingsHeaderLabel)

        self.openCVSettingsBtn = QPushButton(self.widget)
        self.openCVSettingsBtn.setObjectName(u"openCVSettingsBtn")
        self.openCVSettingsBtn.setMinimumSize(QSize(25, 0))
        self.openCVSettingsBtn.setMaximumSize(QSize(16777215, 25))

        self.horizontalLayout_17.addWidget(self.openCVSettingsBtn)

        self.vehicleTuningBtn = QPushButton(self.widget)
        self.vehicleTuningBtn.setObjectName(u"vehicleTuningBtn")
        self.vehicleTuningBtn.setMinimumSize(QSize(0, 25))
        self.vehicleTuningBtn.setMaximumSize(QSize(16777215, 25))

        self.horizontalLayout_17.addWidget(self.vehicleTuningBtn)


        self.verticalLayout_15.addWidget(self.widget)

        self.settingsHeaderLine = QFrame(self.settingsLeftWidget)
        self.settingsHeaderLine.setObjectName(u"settingsHeaderLine")
        self.settingsHeaderLine.setFrameShape(QFrame.Shape.HLine)
        self.settingsHeaderLine.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_15.addWidget(self.settingsHeaderLine)

        self.settingsStackedWidget = QStackedWidget(self.settingsLeftWidget)
        self.settingsStackedWidget.setObjectName(u"settingsStackedWidget")
        self.settingsStackedWidget.setMinimumSize(QSize(0, 500))
        self.OpenCVSettingsPage = QWidget()
        self.OpenCVSettingsPage.setObjectName(u"OpenCVSettingsPage")
        self.verticalLayout_18 = QVBoxLayout(self.OpenCVSettingsPage)
        self.verticalLayout_18.setSpacing(6)
        self.verticalLayout_18.setObjectName(u"verticalLayout_18")
        self.verticalLayout_18.setContentsMargins(9, 0, 9, 0)
        self.OpenCVHeaderLabel = QLabel(self.OpenCVSettingsPage)
        self.OpenCVHeaderLabel.setObjectName(u"OpenCVHeaderLabel")
        self.OpenCVHeaderLabel.setMinimumSize(QSize(0, 30))
        self.OpenCVHeaderLabel.setMaximumSize(QSize(16777215, 35))
        self.OpenCVHeaderLabel.setFont(font1)

        self.verticalLayout_18.addWidget(self.OpenCVHeaderLabel)

        self.OpenCVHeaderLine = QFrame(self.OpenCVSettingsPage)
        self.OpenCVHeaderLine.setObjectName(u"OpenCVHeaderLine")
        self.OpenCVHeaderLine.setFrameShape(QFrame.Shape.HLine)
        self.OpenCVHeaderLine.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_18.addWidget(self.OpenCVHeaderLine)

        self.DebugCVHeaderLabel = QLabel(self.OpenCVSettingsPage)
        self.DebugCVHeaderLabel.setObjectName(u"DebugCVHeaderLabel")
        self.DebugCVHeaderLabel.setMaximumSize(QSize(16777215, 22))

        self.verticalLayout_18.addWidget(self.DebugCVHeaderLabel)

        self.DebugCVWidget_1 = QWidget(self.OpenCVSettingsPage)
        self.DebugCVWidget_1.setObjectName(u"DebugCVWidget_1")
        self.DebugCVWidget_1.setMaximumSize(QSize(16777215, 50))
        self.horizontalLayout_10 = QHBoxLayout(self.DebugCVWidget_1)
        self.horizontalLayout_10.setObjectName(u"horizontalLayout_10")
        self.horizontalLayout_10.setContentsMargins(0, -1, 0, -1)
        self.ObjectVisBtn = QPushButton(self.DebugCVWidget_1)
        self.ObjectVisBtn.setObjectName(u"ObjectVisBtn")
        self.ObjectVisBtn.setMinimumSize(QSize(0, 25))

        self.horizontalLayout_10.addWidget(self.ObjectVisBtn)

        self.FloorVisBtn = QPushButton(self.DebugCVWidget_1)
        self.FloorVisBtn.setObjectName(u"FloorVisBtn")
        self.FloorVisBtn.setMinimumSize(QSize(0, 25))

        self.horizontalLayout_10.addWidget(self.FloorVisBtn)

        self.KalmanCenterVisBtn = QPushButton(self.DebugCVWidget_1)
        self.KalmanCenterVisBtn.setObjectName(u"KalmanCenterVisBtn")
        self.KalmanCenterVisBtn.setMinimumSize(QSize(0, 25))

        self.horizontalLayout_10.addWidget(self.KalmanCenterVisBtn)


        self.verticalLayout_18.addWidget(self.DebugCVWidget_1)

        self.DebugCVWidget_2 = QWidget(self.OpenCVSettingsPage)
        self.DebugCVWidget_2.setObjectName(u"DebugCVWidget_2")
        self.DebugCVWidget_2.setMaximumSize(QSize(16777215, 50))
        self.horizontalLayout_11 = QHBoxLayout(self.DebugCVWidget_2)
        self.horizontalLayout_11.setObjectName(u"horizontalLayout_11")
        self.horizontalLayout_11.setContentsMargins(0, -1, 0, -1)
        self.AmbientVisBtn = QPushButton(self.DebugCVWidget_2)
        self.AmbientVisBtn.setObjectName(u"AmbientVisBtn")
        self.AmbientVisBtn.setMinimumSize(QSize(0, 25))

        self.horizontalLayout_11.addWidget(self.AmbientVisBtn)

        self.FloorSampleVisBtn = QPushButton(self.DebugCVWidget_2)
        self.FloorSampleVisBtn.setObjectName(u"FloorSampleVisBtn")
        self.FloorSampleVisBtn.setMinimumSize(QSize(0, 25))

        self.horizontalLayout_11.addWidget(self.FloorSampleVisBtn)

        self.PathVisBtn = QPushButton(self.DebugCVWidget_2)
        self.PathVisBtn.setObjectName(u"PathVisBtn")
        self.PathVisBtn.setMinimumSize(QSize(0, 25))

        self.horizontalLayout_11.addWidget(self.PathVisBtn)


        self.verticalLayout_18.addWidget(self.DebugCVWidget_2)

        self.HSVSettingsHeaderLabel = QLabel(self.OpenCVSettingsPage)
        self.HSVSettingsHeaderLabel.setObjectName(u"HSVSettingsHeaderLabel")
        self.HSVSettingsHeaderLabel.setMaximumSize(QSize(16777215, 22))

        self.verticalLayout_18.addWidget(self.HSVSettingsHeaderLabel)

        self.HSVSliderWidget = QWidget(self.OpenCVSettingsPage)
        self.HSVSliderWidget.setObjectName(u"HSVSliderWidget")
        self.HSVSliderWidget.setMaximumSize(QSize(16777215, 130))
        self.verticalLayout_19 = QVBoxLayout(self.HSVSliderWidget)
        self.verticalLayout_19.setSpacing(0)
        self.verticalLayout_19.setObjectName(u"verticalLayout_19")
        self.verticalLayout_19.setContentsMargins(0, 0, 0, 0)
        self.HRowWidget = QWidget(self.HSVSliderWidget)
        self.HRowWidget.setObjectName(u"HRowWidget")
        self.horizontalLayout_12 = QHBoxLayout(self.HRowWidget)
        self.horizontalLayout_12.setObjectName(u"horizontalLayout_12")
        self.horizontalLayout_12.setContentsMargins(9, -1, 0, -1)
        self.HRowLabel = QLabel(self.HRowWidget)
        self.HRowLabel.setObjectName(u"HRowLabel")
        self.HRowLabel.setMinimumSize(QSize(65, 0))
        self.HRowLabel.setMaximumSize(QSize(65, 16777215))

        self.horizontalLayout_12.addWidget(self.HRowLabel)

        self.horizontalSpacer = QSpacerItem(2, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_12.addItem(self.horizontalSpacer)

        self.HRowSlider = QSlider(self.HRowWidget)
        self.HRowSlider.setObjectName(u"HRowSlider")
        self.HRowSlider.setMinimumSize(QSize(675, 0))
        self.HRowSlider.setMaximumSize(QSize(675, 16777215))
        self.HRowSlider.setOrientation(Qt.Orientation.Horizontal)

        self.horizontalLayout_12.addWidget(self.HRowSlider, 0, Qt.AlignmentFlag.AlignVCenter)

        self.HRowValueLabel = QLabel(self.HRowWidget)
        self.HRowValueLabel.setObjectName(u"HRowValueLabel")
        self.HRowValueLabel.setMinimumSize(QSize(25, 0))
        self.HRowValueLabel.setMaximumSize(QSize(25, 16777215))
        self.HRowValueLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_12.addWidget(self.HRowValueLabel, 0, Qt.AlignmentFlag.AlignRight)


        self.verticalLayout_19.addWidget(self.HRowWidget)

        self.SRowWidget = QWidget(self.HSVSliderWidget)
        self.SRowWidget.setObjectName(u"SRowWidget")
        self.horizontalLayout_13 = QHBoxLayout(self.SRowWidget)
        self.horizontalLayout_13.setObjectName(u"horizontalLayout_13")
        self.horizontalLayout_13.setContentsMargins(-1, -1, 0, -1)
        self.SRowLabel = QLabel(self.SRowWidget)
        self.SRowLabel.setObjectName(u"SRowLabel")
        self.SRowLabel.setMinimumSize(QSize(65, 0))
        self.SRowLabel.setMaximumSize(QSize(65, 16777215))

        self.horizontalLayout_13.addWidget(self.SRowLabel, 0, Qt.AlignmentFlag.AlignLeft)

        self.horizontalSpacer_2 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_13.addItem(self.horizontalSpacer_2)

        self.SRowSlider = QSlider(self.SRowWidget)
        self.SRowSlider.setObjectName(u"SRowSlider")
        self.SRowSlider.setMinimumSize(QSize(675, 0))
        self.SRowSlider.setMaximumSize(QSize(675, 16777215))
        self.SRowSlider.setOrientation(Qt.Orientation.Horizontal)

        self.horizontalLayout_13.addWidget(self.SRowSlider, 0, Qt.AlignmentFlag.AlignVCenter)

        self.SRowValueLabel = QLabel(self.SRowWidget)
        self.SRowValueLabel.setObjectName(u"SRowValueLabel")
        self.SRowValueLabel.setMinimumSize(QSize(25, 0))
        self.SRowValueLabel.setMaximumSize(QSize(20, 16777215))
        self.SRowValueLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_13.addWidget(self.SRowValueLabel)


        self.verticalLayout_19.addWidget(self.SRowWidget)

        self.VRowWidget = QWidget(self.HSVSliderWidget)
        self.VRowWidget.setObjectName(u"VRowWidget")
        self.horizontalLayout_14 = QHBoxLayout(self.VRowWidget)
        self.horizontalLayout_14.setObjectName(u"horizontalLayout_14")
        self.horizontalLayout_14.setContentsMargins(-1, -1, 0, -1)
        self.VRowLabel = QLabel(self.VRowWidget)
        self.VRowLabel.setObjectName(u"VRowLabel")
        self.VRowLabel.setMinimumSize(QSize(65, 0))
        self.VRowLabel.setMaximumSize(QSize(65, 16777215))

        self.horizontalLayout_14.addWidget(self.VRowLabel, 0, Qt.AlignmentFlag.AlignLeft)

        self.horizontalSpacer_3 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_14.addItem(self.horizontalSpacer_3)

        self.VRowSlider = QSlider(self.VRowWidget)
        self.VRowSlider.setObjectName(u"VRowSlider")
        self.VRowSlider.setMinimumSize(QSize(675, 0))
        self.VRowSlider.setMaximumSize(QSize(675, 16777215))
        self.VRowSlider.setOrientation(Qt.Orientation.Horizontal)

        self.horizontalLayout_14.addWidget(self.VRowSlider)

        self.VRowValueLabel = QLabel(self.VRowWidget)
        self.VRowValueLabel.setObjectName(u"VRowValueLabel")
        self.VRowValueLabel.setMinimumSize(QSize(25, 0))
        self.VRowValueLabel.setMaximumSize(QSize(20, 16777215))
        self.VRowValueLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_14.addWidget(self.VRowValueLabel)


        self.verticalLayout_19.addWidget(self.VRowWidget)


        self.verticalLayout_18.addWidget(self.HSVSliderWidget)

        self.CollisionAssistHeaderLabel = QLabel(self.OpenCVSettingsPage)
        self.CollisionAssistHeaderLabel.setObjectName(u"CollisionAssistHeaderLabel")
        self.CollisionAssistHeaderLabel.setMaximumSize(QSize(16777215, 22))

        self.verticalLayout_18.addWidget(self.CollisionAssistHeaderLabel)

        self.CollisionAssistWidget = QWidget(self.OpenCVSettingsPage)
        self.CollisionAssistWidget.setObjectName(u"CollisionAssistWidget")
        self.CollisionAssistWidget.setMaximumSize(QSize(16777215, 50))
        self.horizontalLayout_15 = QHBoxLayout(self.CollisionAssistWidget)
        self.horizontalLayout_15.setObjectName(u"horizontalLayout_15")
        self.horizontalLayout_15.setContentsMargins(0, -1, 0, -1)
        self.CollisionAssistBtn = QPushButton(self.CollisionAssistWidget)
        self.CollisionAssistBtn.setObjectName(u"CollisionAssistBtn")
        self.CollisionAssistBtn.setMinimumSize(QSize(0, 25))

        self.horizontalLayout_15.addWidget(self.CollisionAssistBtn)


        self.verticalLayout_18.addWidget(self.CollisionAssistWidget)

        self.settingsStackedWidget.addWidget(self.OpenCVSettingsPage)

        self.verticalLayout_15.addWidget(self.settingsStackedWidget)

        self.verticalSpacer_8 = QSpacerItem(20, 431, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_15.addItem(self.verticalSpacer_8)

        self.emergencyDisconnectBtn = QPushButton(self.settingsLeftWidget)
        self.emergencyDisconnectBtn.setObjectName(u"emergencyDisconnectBtn")
        self.emergencyDisconnectBtn.setFont(font3)
        icon3 = QIcon()
        icon3.addFile(u"D-14/Client-Side/client-app/icons/solar--black-hole-line-duotone.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.emergencyDisconnectBtn.setIcon(icon3)
        self.emergencyDisconnectBtn.setIconSize(QSize(60, 60))

        self.verticalLayout_15.addWidget(self.emergencyDisconnectBtn, 0, Qt.AlignmentFlag.AlignHCenter)

        self.emergencyDisconnectLabel = QLabel(self.settingsLeftWidget)
        self.emergencyDisconnectLabel.setObjectName(u"emergencyDisconnectLabel")
        self.emergencyDisconnectLabel.setFont(font1)

        self.verticalLayout_15.addWidget(self.emergencyDisconnectLabel, 0, Qt.AlignmentFlag.AlignHCenter)


        self.horizontalLayout_5.addWidget(self.settingsLeftWidget)

        self.settingsRightWidget = QWidget(self.settingsPage)
        self.settingsRightWidget.setObjectName(u"settingsRightWidget")
        self.verticalLayout_16 = QVBoxLayout(self.settingsRightWidget)
        self.verticalLayout_16.setObjectName(u"verticalLayout_16")
        self.settingsInfoStackedWidget = QStackedWidget(self.settingsRightWidget)
        self.settingsInfoStackedWidget.setObjectName(u"settingsInfoStackedWidget")
        self.settingsInfoStackedWidget.setMinimumSize(QSize(0, 800))
        self.openCVSettingsInfoPage = QWidget()
        self.openCVSettingsInfoPage.setObjectName(u"openCVSettingsInfoPage")
        self.settingsInfoStackedWidget.addWidget(self.openCVSettingsInfoPage)
        self.vehicleTuningInfoPage = QWidget()
        self.vehicleTuningInfoPage.setObjectName(u"vehicleTuningInfoPage")
        self.settingsInfoStackedWidget.addWidget(self.vehicleTuningInfoPage)

        self.verticalLayout_16.addWidget(self.settingsInfoStackedWidget)

        self.verticalSpacer_10 = QSpacerItem(20, 100, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed)

        self.verticalLayout_16.addItem(self.verticalSpacer_10)

        self.currentPgrmVersionWidget = QWidget(self.settingsRightWidget)
        self.currentPgrmVersionWidget.setObjectName(u"currentPgrmVersionWidget")
        self.horizontalLayout_9 = QHBoxLayout(self.currentPgrmVersionWidget)
        self.horizontalLayout_9.setSpacing(15)
        self.horizontalLayout_9.setObjectName(u"horizontalLayout_9")
        self.horizontalLayout_9.setContentsMargins(0, 0, 15, 0)
        self.currentPgrmVersionHeaderWidget = QWidget(self.currentPgrmVersionWidget)
        self.currentPgrmVersionHeaderWidget.setObjectName(u"currentPgrmVersionHeaderWidget")
        self.verticalLayout_17 = QVBoxLayout(self.currentPgrmVersionHeaderWidget)
        self.verticalLayout_17.setObjectName(u"verticalLayout_17")
        self.currentPgrmVersionHeaderLabel = QLabel(self.currentPgrmVersionHeaderWidget)
        self.currentPgrmVersionHeaderLabel.setObjectName(u"currentPgrmVersionHeaderLabel")
        self.currentPgrmVersionHeaderLabel.setFont(font1)

        self.verticalLayout_17.addWidget(self.currentPgrmVersionHeaderLabel, 0, Qt.AlignmentFlag.AlignRight)


        self.horizontalLayout_9.addWidget(self.currentPgrmVersionHeaderWidget)

        self.currentPgrmVersionLabel = QLabel(self.currentPgrmVersionWidget)
        self.currentPgrmVersionLabel.setObjectName(u"currentPgrmVersionLabel")
        self.currentPgrmVersionLabel.setLayoutDirection(Qt.LayoutDirection.LeftToRight)

        self.horizontalLayout_9.addWidget(self.currentPgrmVersionLabel, 0, Qt.AlignmentFlag.AlignLeft)


        self.verticalLayout_16.addWidget(self.currentPgrmVersionWidget, 0, Qt.AlignmentFlag.AlignRight)


        self.horizontalLayout_5.addWidget(self.settingsRightWidget)

        self.stackedWidget.addWidget(self.settingsPage)
        self.drivePage = PageWithKeyEvents()
        self.drivePage.setObjectName(u"drivePage")
        self.verticalLayout_5 = QVBoxLayout(self.drivePage)
        self.verticalLayout_5.setSpacing(9)
        self.verticalLayout_5.setObjectName(u"verticalLayout_5")
        self.videoStreamWidget = QWidget(self.drivePage)
        self.videoStreamWidget.setObjectName(u"videoStreamWidget")
        sizePolicy2 = QSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        sizePolicy2.setHorizontalStretch(0)
        sizePolicy2.setVerticalStretch(0)
        sizePolicy2.setHeightForWidth(self.videoStreamWidget.sizePolicy().hasHeightForWidth())
        self.videoStreamWidget.setSizePolicy(sizePolicy2)
        self.videoStreamWidget.setMinimumSize(QSize(1280, 720))
        self.videoStreamWidget.setMaximumSize(QSize(1920, 1080))
        self.videoStreamWidget.setSizeIncrement(QSize(0, 0))
        self.videoStreamWidget.setBaseSize(QSize(1280, 720))
        self.videoStreamWidget.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.gridLayout = QGridLayout(self.videoStreamWidget)
        self.gridLayout.setSpacing(0)
        self.gridLayout.setObjectName(u"gridLayout")
        self.gridLayout.setSizeConstraint(QLayout.SizeConstraint.SetMinAndMaxSize)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.videoStreamLabel = QLabel(self.videoStreamWidget)
        self.videoStreamLabel.setObjectName(u"videoStreamLabel")
        sizePolicy2.setHeightForWidth(self.videoStreamLabel.sizePolicy().hasHeightForWidth())
        self.videoStreamLabel.setSizePolicy(sizePolicy2)
        self.videoStreamLabel.setMinimumSize(QSize(1280, 720))
        self.videoStreamLabel.setMaximumSize(QSize(1920, 1080))
        self.videoStreamLabel.setSizeIncrement(QSize(0, 0))
        self.videoStreamLabel.setBaseSize(QSize(1280, 720))
        self.videoStreamLabel.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.videoStreamLabel.setScaledContents(True)
        self.videoStreamLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.videoStreamLabel.setWordWrap(True)

        self.gridLayout.addWidget(self.videoStreamLabel, 0, 0, 1, 1, Qt.AlignmentFlag.AlignHCenter|Qt.AlignmentFlag.AlignVCenter)


        self.verticalLayout_5.addWidget(self.videoStreamWidget)

        self.vehicleControlPanelWidget = QWidget(self.drivePage)
        self.vehicleControlPanelWidget.setObjectName(u"vehicleControlPanelWidget")
        self.vehicleControlPanelWidget.setMinimumSize(QSize(0, 350))
        self.vehicleControlPanelWidget.setMaximumSize(QSize(16777215, 350))
        self.horizontalLayout_6 = QHBoxLayout(self.vehicleControlPanelWidget)
        self.horizontalLayout_6.setObjectName(u"horizontalLayout_6")
        self.horizontalLayout_6.setContentsMargins(0, -1, -1, 0)
        self.vehicleGaugeClusterWidget = QWidget(self.vehicleControlPanelWidget)
        self.vehicleGaugeClusterWidget.setObjectName(u"vehicleGaugeClusterWidget")
        self.vehicleGaugeClusterWidget.setMinimumSize(QSize(800, 0))
        self.vehicleGaugeClusterWidget.setMaximumSize(QSize(1000, 16777215))
        self.verticalLayout_6 = QVBoxLayout(self.vehicleGaugeClusterWidget)
        self.verticalLayout_6.setSpacing(0)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.verticalLayout_6.setContentsMargins(0, 0, -1, 0)
        self.clusterWidget = QWidget(self.vehicleGaugeClusterWidget)
        self.clusterWidget.setObjectName(u"clusterWidget")
        self.clusterWidget.setMinimumSize(QSize(0, 300))
        self.clusterWidget.setMaximumSize(QSize(16777215, 300))
        self.horizontalLayout_16 = QHBoxLayout(self.clusterWidget)
        self.horizontalLayout_16.setObjectName(u"horizontalLayout_16")
        self.horizontalLayout_16.setContentsMargins(0, 0, 0, 0)
        self.prndWidget = QWidget(self.clusterWidget)
        self.prndWidget.setObjectName(u"prndWidget")
        self.prndWidget.setMinimumSize(QSize(75, 300))
        self.prndWidget.setMaximumSize(QSize(75, 300))

        self.horizontalLayout_16.addWidget(self.prndWidget)

        self.horizontalSpacer_6 = QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_16.addItem(self.horizontalSpacer_6)

        self.speedometerWidget = QWidget(self.clusterWidget)
        self.speedometerWidget.setObjectName(u"speedometerWidget")
        self.speedometerWidget.setMinimumSize(QSize(300, 300))
        self.speedometerWidget.setMaximumSize(QSize(300, 300))

        self.horizontalLayout_16.addWidget(self.speedometerWidget)

        self.horizontalSpacer_7 = QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_16.addItem(self.horizontalSpacer_7)

        self.steerAngleWidget = QWidget(self.clusterWidget)
        self.steerAngleWidget.setObjectName(u"steerAngleWidget")
        self.steerAngleWidget.setMinimumSize(QSize(300, 300))
        self.steerAngleWidget.setMaximumSize(QSize(300, 300))

        self.horizontalLayout_16.addWidget(self.steerAngleWidget)


        self.verticalLayout_6.addWidget(self.clusterWidget)

        self.vehicleKeyInfoWidget = QWidget(self.vehicleGaugeClusterWidget)
        self.vehicleKeyInfoWidget.setObjectName(u"vehicleKeyInfoWidget")
        self.vehicleKeyInfoWidget.setMinimumSize(QSize(0, 30))
        self.vehicleKeyInfoWidget.setMaximumSize(QSize(800, 40))
        self.horizontalLayout_7 = QHBoxLayout(self.vehicleKeyInfoWidget)
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.horizontalLayout_7.setContentsMargins(-1, 0, -1, 0)
        self.accelerateBtn = QPushButton(self.vehicleKeyInfoWidget)
        self.accelerateBtn.setObjectName(u"accelerateBtn")
        self.accelerateBtn.setMinimumSize(QSize(0, 25))
        self.accelerateBtn.setMaximumSize(QSize(16777215, 25))

        self.horizontalLayout_7.addWidget(self.accelerateBtn)

        self.turnLeftBtn = QPushButton(self.vehicleKeyInfoWidget)
        self.turnLeftBtn.setObjectName(u"turnLeftBtn")
        self.turnLeftBtn.setMinimumSize(QSize(0, 25))
        self.turnLeftBtn.setMaximumSize(QSize(16777215, 25))

        self.horizontalLayout_7.addWidget(self.turnLeftBtn)

        self.reverseBtn = QPushButton(self.vehicleKeyInfoWidget)
        self.reverseBtn.setObjectName(u"reverseBtn")
        self.reverseBtn.setMinimumSize(QSize(0, 25))
        self.reverseBtn.setMaximumSize(QSize(16777215, 25))

        self.horizontalLayout_7.addWidget(self.reverseBtn)

        self.turnRightBtn = QPushButton(self.vehicleKeyInfoWidget)
        self.turnRightBtn.setObjectName(u"turnRightBtn")
        self.turnRightBtn.setMinimumSize(QSize(0, 25))
        self.turnRightBtn.setMaximumSize(QSize(16777215, 25))

        self.horizontalLayout_7.addWidget(self.turnRightBtn)

        self.brakeBtn = QPushButton(self.vehicleKeyInfoWidget)
        self.brakeBtn.setObjectName(u"brakeBtn")
        self.brakeBtn.setMinimumSize(QSize(0, 25))
        self.brakeBtn.setMaximumSize(QSize(16777215, 25))

        self.horizontalLayout_7.addWidget(self.brakeBtn)


        self.verticalLayout_6.addWidget(self.vehicleKeyInfoWidget, 0, Qt.AlignmentFlag.AlignBottom)


        self.horizontalLayout_6.addWidget(self.vehicleGaugeClusterWidget)

        self.horizontalSpacer_8 = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_6.addItem(self.horizontalSpacer_8)

        self.alertAssistWidget = QWidget(self.vehicleControlPanelWidget)
        self.alertAssistWidget.setObjectName(u"alertAssistWidget")
        self.alertAssistWidget.setMinimumSize(QSize(180, 300))

        self.horizontalLayout_6.addWidget(self.alertAssistWidget)

        self.horizontalSpacer_5 = QSpacerItem(180, 20, QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Minimum)

        self.horizontalLayout_6.addItem(self.horizontalSpacer_5)

        self.vehicleStatusWidget = QWidget(self.vehicleControlPanelWidget)
        self.vehicleStatusWidget.setObjectName(u"vehicleStatusWidget")
        self.vehicleStatusWidget.setMinimumSize(QSize(450, 0))
        self.vehicleStatusWidget.setMaximumSize(QSize(450, 16777215))
        self.verticalLayout_14 = QVBoxLayout(self.vehicleStatusWidget)
        self.verticalLayout_14.setObjectName(u"verticalLayout_14")
        self.verticalLayout_14.setContentsMargins(-1, -1, -1, 0)
        self.connectionVehicleTypeWidget = QWidget(self.vehicleStatusWidget)
        self.connectionVehicleTypeWidget.setObjectName(u"connectionVehicleTypeWidget")
        self.connectionVehicleTypeWidget.setMinimumSize(QSize(0, 50))
        self.connectionVehicleTypeWidget.setMaximumSize(QSize(16777215, 50))
        self.horizontalLayout_8 = QHBoxLayout(self.connectionVehicleTypeWidget)
        self.horizontalLayout_8.setSpacing(10)
        self.horizontalLayout_8.setObjectName(u"horizontalLayout_8")
        self.horizontalLayout_8.setContentsMargins(0, 0, 0, 0)
        self.currentVehicleLblWidget = QWidget(self.connectionVehicleTypeWidget)
        self.currentVehicleLblWidget.setObjectName(u"currentVehicleLblWidget")
        self.currentVehicleLblWidget.setMinimumSize(QSize(0, 50))
        self.currentVehicleLblWidget.setMaximumSize(QSize(16777215, 50))
        self.verticalLayout_13 = QVBoxLayout(self.currentVehicleLblWidget)
        self.verticalLayout_13.setSpacing(10)
        self.verticalLayout_13.setObjectName(u"verticalLayout_13")
        self.verticalLayout_13.setContentsMargins(0, 0, 0, 0)
        self.currentVehicleLabel = QLabel(self.currentVehicleLblWidget)
        self.currentVehicleLabel.setObjectName(u"currentVehicleLabel")
        self.currentVehicleLabel.setFont(font1)
        self.currentVehicleLabel.setLayoutDirection(Qt.LayoutDirection.LeftToRight)
        self.currentVehicleLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_13.addWidget(self.currentVehicleLabel)


        self.horizontalLayout_8.addWidget(self.currentVehicleLblWidget)

        self.vehicleTypeLabel = QLabel(self.connectionVehicleTypeWidget)
        self.vehicleTypeLabel.setObjectName(u"vehicleTypeLabel")
        self.vehicleTypeLabel.setMinimumSize(QSize(100, 0))
        self.vehicleTypeLabel.setMaximumSize(QSize(120, 16777215))
        self.vehicleTypeLabel.setFont(font1)
        self.vehicleTypeLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.horizontalLayout_8.addWidget(self.vehicleTypeLabel)


        self.verticalLayout_14.addWidget(self.connectionVehicleTypeWidget)

        self.verticalSpacer_7 = QSpacerItem(20, 255, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_14.addItem(self.verticalSpacer_7)

        self.vehicleAlertLogWidget = QWidget(self.vehicleStatusWidget)
        self.vehicleAlertLogWidget.setObjectName(u"vehicleAlertLogWidget")
        self.vehicleAlertLogWidget.setMinimumSize(QSize(0, 250))

        self.verticalLayout_14.addWidget(self.vehicleAlertLogWidget)


        self.horizontalLayout_6.addWidget(self.vehicleStatusWidget, 0, Qt.AlignmentFlag.AlignRight)


        self.verticalLayout_5.addWidget(self.vehicleControlPanelWidget)

        self.stackedWidget.addWidget(self.drivePage)

        self.verticalLayout_4.addWidget(self.stackedWidget)


        self.horizontalLayout.addWidget(self.mainPage)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        self.stackedWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)

        #* IMPORTANT: add SystemLogViewer widget to a new page
        self.systemLogPage = SystemLogViewer()
        self.stackedWidget.addWidget(self.systemLogPage)

        #* IMPORTANT: add CalibrationWidget widget to a new settingsStackedWidget page
        self.VehicleTuningSettingsPage = CalibrationWidget()
        self.settingsStackedWidget.addWidget(self.VehicleTuningSettingsPage)

        #* IMPORTANT: add pages for settingsInfoStackedWidget
        # ------ OpenCV ------
        self.settingsInfoOpenCvWidget = DescriptionWidget("D-14/Client-Side/client-app/markdown-descriptions/openCvSettingsTab.md")
        self.settingsInfoStackedWidget.addWidget(self.settingsInfoOpenCvWidget)
        self.settingsInfoStackedWidget.setCurrentWidget(self.settingsInfoOpenCvWidget)
        
        self.settingsInfoStackedWidget.setStyleSheet("""
            QWidget{
                background-color: #74e1ef;
                border-radius: 15px;
            }
        """)

        # ------ Vehicle Calibration ------
        self.settingsInfoVehicleCalibrationWidget = DescriptionWidget("D-14/Client-Side/client-app/markdown-descriptions/vehicleTuningSettingsTab.md")
        self.settingsInfoStackedWidget.addWidget(self.settingsInfoVehicleCalibrationWidget)
        
        #* IMPORTANT: add home page LogConsoleWidget widget to connectionLogWidget
        self.networkConnectionLogWidget = LogConsoleWidget()
        self.horizontalLayout_CLW = QHBoxLayout(self.connectionLogWidget)
        self.horizontalLayout_CLW .addWidget(self.networkConnectionLogWidget)

        #* IMPORTANT: add drive page LogConsoleWidget widget to vehicleAlertLogWidget
        self.vehicleSystemAlertLogWidget = LogConsoleWidget()
        self.horizontalLayout_VALW = QHBoxLayout(self.vehicleAlertLogWidget)
        self.horizontalLayout_VALW.addWidget(self.vehicleSystemAlertLogWidget)

        #* IMPORTANT: add DriveAssistWidget to alertAssistWidget
        self.driveAssistWidget = DriveAssistWidget()
        self.horizontalLayout_AAW = QHBoxLayout(self.alertAssistWidget)
        self.horizontalLayout_AAW.addWidget(self.driveAssistWidget)

        #* IMPORTANT: add PRNDWidget to prndWidget
        self.PRNDWidget = PRNDWidget()
        self.horizontalLayout_PRNDW = QHBoxLayout(self.prndWidget)
        self.horizontalLayout_PRNDW.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_PRNDW.addWidget(self.PRNDWidget)

        #* IMPORTANT: add SpeedometerWidget to speedometerWidget
        self.vehicleSpeedometerWidget = SpeedometerWidget()
        self.horizontalLayout_SW = QHBoxLayout(self.speedometerWidget)
        self.horizontalLayout_SW.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_SW.addWidget(self.vehicleSpeedometerWidget, 0, Qt.AlignmentFlag.AlignCenter)

        #* IMPORTANT: add SteeringPathWidget to steerAngleWidget
        self.steerPathWidget = SteeringPathWidget()
        self.horizontalLayout_SAW = QHBoxLayout(self.steerAngleWidget)
        self.horizontalLayout_SAW.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_SAW.addWidget(self.steerPathWidget, 0, Qt.AlignmentFlag.AlignCenter)

        #* IMPORTANT: add CarConnectWidget to loginWidget
        self.carConnectLoginWidget = CarConnectWidget()
        self.horizontalLayout_LW = QHBoxLayout(self.loginWidget)
        self.horizontalLayout_LW.setContentsMargins(5, 0, 5, 0)
        self.horizontalLayout_LW.addWidget(self.carConnectLoginWidget, 0, Qt.AlignmentFlag.AlignCenter)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
#if QT_CONFIG(tooltip)
        self.homeBtn.setToolTip(QCoreApplication.translate("MainWindow", u"Home", None))
#endif // QT_CONFIG(tooltip)
        self.homeBtn.setText("")
        self.driveBtn.setText("")
        self.logBtn.setText("")
        self.settingsBtn.setText("")
#if QT_CONFIG(tooltip)
        self.mainPage.setToolTip("")
#endif // QT_CONFIG(tooltip)
        #self.ipInputBox.setTitle(QCoreApplication.translate("MainWindow", u"Enter an ip address to connect", None))
        #self.inputIp.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Enter an ip address...", None))
        #self.recentIpBox.setTitle(QCoreApplication.translate("MainWindow", u"Connect to a recent ip address", None))
        #self.recentIpCombo.setItemText(0, "")
        '''
        self.recentIpCombo.setItemText(1, QCoreApplication.translate("MainWindow", u"ip-addr test-1", None))
        self.recentIpCombo.setItemText(2, QCoreApplication.translate("MainWindow", u"ip-addr test-2", None))
        self.recentIpCombo.setItemText(3, QCoreApplication.translate("MainWindow", u"ip-addr test-3", None))
        self.recentIpCombo.setItemText(4, QCoreApplication.translate("MainWindow", u"ip-addr test-4", None))
        self.recentIpCombo.setItemText(5, QCoreApplication.translate("MainWindow", u"ip-addr test-5", None))
        '''
        #self.ipComboBtn.setText("")
        self.label_2.setText("")
        #self.projectTitle.setText(QCoreApplication.translate("MainWindow", u"About", None))
        #self.githubLink.setText(QCoreApplication.translate("MainWindow", u"DriveCore is a modular and scalable platform designed for controlling RC vehicles with the potential for AI-powered autonomy. Built using Python, OpenCV, and a Raspberry Pi, DriveCore serves as the foundation for both manual and automated vehicle operation, integrating computer vision, sensor fusion, and remote control capabilities.", None))
        #self.aboutTitle.setText(QCoreApplication.translate("MainWindow", u"Releases", None))
        #self.description.setText(QCoreApplication.translate("MainWindow", u"Release here:", None))
        self.settingsHeaderLabel.setText(QCoreApplication.translate("MainWindow", u"Settings", None))
        self.openCVSettingsBtn.setText(QCoreApplication.translate("MainWindow", u"Open CV", None))
        self.vehicleTuningBtn.setText(QCoreApplication.translate("MainWindow", u"Vehicle Tuning", None))
        self.OpenCVHeaderLabel.setText(QCoreApplication.translate("MainWindow", u"OpenCV", None))
        self.DebugCVHeaderLabel.setText(QCoreApplication.translate("MainWindow", u"Debug Options:", None))
        self.ObjectVisBtn.setText(QCoreApplication.translate("MainWindow", u"Object Vis: OFF", None))
        self.FloorVisBtn.setText(QCoreApplication.translate("MainWindow", u"Floor Vis: OFF", None))
        self.KalmanCenterVisBtn.setText(QCoreApplication.translate("MainWindow", u"Kalman Center Vis: OFF", None))
        self.AmbientVisBtn.setText(QCoreApplication.translate("MainWindow", u"Ambient Vis: OFF", None))
        self.FloorSampleVisBtn.setText(QCoreApplication.translate("MainWindow", u"FloorSample Vis: OFF", None))
        self.PathVisBtn.setText(QCoreApplication.translate("MainWindow", u"Path Vis: OFF", None))
        self.HSVSettingsHeaderLabel.setText(QCoreApplication.translate("MainWindow", u"Min HSV Sensitivity Margins:", None))
        self.HRowLabel.setText(QCoreApplication.translate("MainWindow", u"H Margin", None))
        self.HRowValueLabel.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.SRowLabel.setText(QCoreApplication.translate("MainWindow", u"S Margin", None))
        self.SRowValueLabel.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.VRowLabel.setText(QCoreApplication.translate("MainWindow", u"V Margin", None))
        self.VRowValueLabel.setText(QCoreApplication.translate("MainWindow", u"0", None))
        self.CollisionAssistHeaderLabel.setText(QCoreApplication.translate("MainWindow", u"Collision Assist:", None))
        self.CollisionAssistBtn.setText(QCoreApplication.translate("MainWindow", u"OFF", None))
        self.emergencyDisconnectBtn.setText(QCoreApplication.translate("MainWindow", u"EMERGENCY DISCONNECT", None))
        self.emergencyDisconnectLabel.setText(QCoreApplication.translate("MainWindow", u"WARNING: WILL STOP PROGRAM ON HOST", None))
        self.currentPgrmVersionHeaderLabel.setText(QCoreApplication.translate("MainWindow", u"Current Program Version: ", None))
        self.currentPgrmVersionLabel.setText(QCoreApplication.translate("MainWindow", u"Ver 1.3 (01-05-2025)", None))
        self.videoStreamLabel.setText(QCoreApplication.translate("MainWindow", u"No Conncection", None))
        self.accelerateBtn.setText(QCoreApplication.translate("MainWindow", u"Accelerate : [W]", None))
        self.turnLeftBtn.setText(QCoreApplication.translate("MainWindow", u"Turn Left : [A]", None))
        self.reverseBtn.setText(QCoreApplication.translate("MainWindow", u"Reverse : [S]", None))
        self.turnRightBtn.setText(QCoreApplication.translate("MainWindow", u"Turn Right : [D]", None))
        self.brakeBtn.setText(QCoreApplication.translate("MainWindow", u"Brake : [SPACE]", None))
        self.currentVehicleLabel.setText(QCoreApplication.translate("MainWindow", u"Current vehicle connected to:", None))
        self.vehicleTypeLabel.setText(QCoreApplication.translate("MainWindow", u"Unknown", None))
    # retranslateUi

