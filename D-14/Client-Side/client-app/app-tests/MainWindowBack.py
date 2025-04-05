# -*- coding: utf-8 -*-

################################################################################
## Form generated from reading UI file 'MainWindowpfEaFq.ui'
##
## Created by: Qt User Interface Compiler version 6.8.2
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
from PySide6.QtWidgets import (QApplication, QComboBox, QFrame, QGridLayout,
    QGroupBox, QHBoxLayout, QLabel, QLayout,
    QLineEdit, QMainWindow, QPushButton, QSizePolicy,
    QSpacerItem, QStackedWidget, QVBoxLayout, QWidget)
import resource
from appFunctions import PageWithKeyEvents

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        if not MainWindow.objectName():
            MainWindow.setObjectName(u"MainWindow")
        MainWindow.resize(1425, 1115)
        self.centralwidget = QWidget(MainWindow)
        self.centralwidget.setObjectName(u"centralwidget")
        self.centralwidget.setStyleSheet(u"/*Settings page*/\n"
"QLabel#settingsHeaderLabel{\n"
"	color: #f1f3f3;\n"
"}\n"
"Line#keysettingsHeaderLine{\n"
"	color: #1e1e21;\n"
"}\n"
"QPushButton#emergencyDisconnectBtn{\n"
"	background-color: #f1f3f3;\n"
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
"/*Drive page*/\n"
"QWidget#videoStreamWidget{\n"
"	background-color: #f1f3f3;\n"
"}\n"
"QLabel#keyBindingsLabel{\n"
"	color: #f1f3f3;\n"
"}\n"
"Line#keyBindingsLine{\n"
"	col"
                        "or: #1e1e21;\n"
"}\n"
"QLabel#wKeyLabel{\n"
"	color: #f1f3f3;\n"
"}\n"
"QLabel#aKeyLabel{\n"
"	color: #f1f3f3;\n"
"}\n"
"QLabel#sKeyLabel{\n"
"	color: #f1f3f3;\n"
"}\n"
"QLabel#dKeyLabel{\n"
"	color: #f1f3f3;\n"
"}\n"
"QLabel#accelerateLabel{\n"
"	color: #f1f3f3;\n"
"}\n"
"QLabel#turnLeftLabel{\n"
"	color: #f1f3f3;\n"
"}\n"
"QLabel#reverseBreakLabel{\n"
"	color: #f1f3f3;\n"
"}\n"
"QLabel#turnRightLabel{\n"
"	color: #f1f3f3;\n"
"}\n"
"QWidget#connectionVehicleTypeWidget{\n"
"	background-color: #1e1e21;\n"
"	border: 1px #1e1e21;\n"
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
"\n"
"\n"
"\n"
"/*Left home widget*/\n"
"QGroupBox#ipInputBox{\n"
"	border: 1px #f1f3f3;\n"
"	border-radius: 15px;\n"
"	background-color: #7a63ff;\n"
"	margin-top: 6px;\n"
"}\n"
"QGroupBox::title#ipInputBox{\n"
"	su"
                        "bcontrol-origin: margin;\n"
"	left: 10px;\n"
"	bottom: -10px;\n"
"	padding: 0 5px;\n"
"	color: #f1f3f3;\n"
"}\n"
"QLineEdit#inputIp{\n"
"	background: #f1f3f3;\n"
"	color: #1e1e21;\n"
"	border: none;\n"
"	border-radius: 5px;\n"
"}\n"
"QGroupBox#recentIpBox{\n"
"	border: 1px #f1f3f3;\n"
"	border-radius: 15px;\n"
"	background-color: #7a63ff;\n"
"	margin-top: 6px;\n"
"}\n"
"QGroupBox::title#recentIpBox{\n"
"	subcontrol-origin: margin;\n"
"	left: 10px;\n"
"	bottom: -10px;\n"
"	padding: 0 5px;\n"
"	color: #f1f3f3;\n"
"}\n"
"QComboBox#recentIpCombo{\n"
"	background: #f1f3f3;\n"
"	color: #1e1e21;\n"
"	border: none;\n"
"	border-radius: 5px;\n"
"}\n"
"QComboBox::drop-down#recentIpCombo{\n"
"	border: none;\n"
"}\n"
"QComboBox::down-arrow#recentIpCombo{\n"
"	border: 1px #7a63ff;\n"
"	border-style: dotted;\n"
"}\n"
"QPushButton#ipComboBtn{\n"
"	background-color: #f1f3f3;\n"
"	border-radius: 5px;\n"
"}\n"
"QPushButton#ipComboBtn:pressed{\n"
"	background-color: #74e1ef;\n"
"}\n"
"\n"
"\n"
"\n"
"/*Right home widget*/\n"
"QWidget#projectInfoWidget {\n"
"	background-color: #74e1ef;\n"
"	border: 1px #74e1ef;\n"
"	border-radius: 15px;\n"
"}\n"
"QLabel#aboutTitle {\n"
"	color: #1e1e21;\n"
"}\n"
""
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
"/*Left menu*/\n"
"QWidget#leftMenu {\n"
"	background-color: #1e1e21;\n"
"}\n"
"\n"
"\n"
"\n"
"/*Left menu buttons*/\n"
"QPushButton#homeBtn {\n"
"	background-color: #f1f3f3;\n"
"    border-style: outset;\n"
"    border-width: 2px;\n"
"    border-radius: 30px;\n"
"    border-color: #f1f3f3;\n"
"    padding: 6px;\n"
"}\n"
"QPushButton#driveBtn {\n"
"	background-color: #f1f3f3;\n"
"    border-style: outset;\n"
"    border-width: 2px;\n"
"    border-radius: 30px;\n"
"    border-color: #f1f3f3;\n"
"    padding: 6px;\n"
"}\n"
"QPushButton#settingsBtn {\n"
"	background-color: #f1f3f3;\n"
"    border-style: outset;\n"
"    border-width: 2px;\n"
"    border-radius: 30px;\n"
"    border-color: #f1f3f3;\n"
"    padding: 6px;\n"
"}\n"
"\n"
"/*Main background*/\n"
"\n"
"QWidget#centralWidget{\n"
"	background-color: #0c0c0d;\n"
"}\n"
"QWidget#mainPage{\n"
""
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
        self.horizontalLayout_2.setSpacing(0)
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

        self.ipInputBox = QGroupBox(self.leftHomeWidget)
        self.ipInputBox.setObjectName(u"ipInputBox")
        self.ipInputBox.setMinimumSize(QSize(0, 90))
        self.ipInputBox.setMaximumSize(QSize(350, 16777215))
        font = QFont()
        font.setPointSize(15)
        font.setBold(False)
        self.ipInputBox.setFont(font)
        self.horizontalLayout_3 = QHBoxLayout(self.ipInputBox)
        self.horizontalLayout_3.setSpacing(15)
        self.horizontalLayout_3.setObjectName(u"horizontalLayout_3")
        self.horizontalLayout_3.setContentsMargins(15, 15, 15, 15)
        self.inputIp = QLineEdit(self.ipInputBox)
        self.inputIp.setObjectName(u"inputIp")
        self.inputIp.setMinimumSize(QSize(0, 35))

        self.horizontalLayout_3.addWidget(self.inputIp, 0, Qt.AlignmentFlag.AlignBottom)


        self.verticalLayout_8.addWidget(self.ipInputBox)

        self.verticalSpacer_4 = QSpacerItem(20, 158, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_8.addItem(self.verticalSpacer_4)

        self.recentIpBox = QGroupBox(self.leftHomeWidget)
        self.recentIpBox.setObjectName(u"recentIpBox")
        self.recentIpBox.setMinimumSize(QSize(0, 90))
        self.recentIpBox.setMaximumSize(QSize(350, 16777215))
        self.recentIpBox.setFont(font)
        self.horizontalLayout_4 = QHBoxLayout(self.recentIpBox)
        self.horizontalLayout_4.setSpacing(15)
        self.horizontalLayout_4.setObjectName(u"horizontalLayout_4")
        self.horizontalLayout_4.setContentsMargins(15, 15, 15, 15)
        self.recentIpCombo = QComboBox(self.recentIpBox)
        '''self.recentIpCombo.addItem("")
        self.recentIpCombo.addItem("")
        self.recentIpCombo.addItem("")
        self.recentIpCombo.addItem("")
        self.recentIpCombo.addItem("")
        self.recentIpCombo.addItem("")'''
        self.recentIpCombo.setObjectName(u"recentIpCombo")
        self.recentIpCombo.setMinimumSize(QSize(0, 35))

        self.horizontalLayout_4.addWidget(self.recentIpCombo, 0, Qt.AlignmentFlag.AlignBottom)

        self.ipComboBtn = QPushButton(self.recentIpBox)
        self.ipComboBtn.setObjectName(u"ipComboBtn")
        self.ipComboBtn.setMinimumSize(QSize(35, 35))
        self.ipComboBtn.setMaximumSize(QSize(35, 35))
        icon4 = QIcon()
        icon4.addFile(u"D-14/Client-Side/client-app/icons/solar--link-bold-duotone.svg", QSize(), QIcon.Mode.Normal, QIcon.State.Off)
        self.ipComboBtn.setIcon(icon4)
        self.ipComboBtn.setIconSize(QSize(30, 30))

        self.horizontalLayout_4.addWidget(self.ipComboBtn, 0, Qt.AlignmentFlag.AlignBottom)

        self.verticalLayout_8.addWidget(self.recentIpBox)

        self.verticalSpacer_3 = QSpacerItem(20, 155, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_8.addItem(self.verticalSpacer_3)


        self.horizontalLayout_2.addWidget(self.leftHomeWidget)

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
        self.label_2.setPixmap(QPixmap(u"D-14/Client-Side/client-app/icons/DriveCore-Logo-V1.png"))
        self.label_2.setScaledContents(True)

        self.verticalLayout_9.addWidget(self.label_2, 0, Qt.AlignmentFlag.AlignHCenter)

        self.projectInfoWidget = QWidget(self.widget_6)
        self.projectInfoWidget.setObjectName(u"projectInfoWidget")
        self.projectInfoWidget.setMinimumSize(QSize(350, 400))
        self.verticalLayout_10 = QVBoxLayout(self.projectInfoWidget)
        self.verticalLayout_10.setObjectName(u"verticalLayout_10")
        self.verticalLayout_10.setContentsMargins(-1, 20, -1, 30)
        self.projectTitle = QLabel(self.projectInfoWidget)
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
        self.githubLink.setMinimumSize(QSize(0, 0))
        self.githubLink.setMaximumSize(QSize(16777215, 40))
        self.githubLink.setWordWrap(True)
        self.githubLink.setMargin(10)
        self.githubLink.setOpenExternalLinks(True)
        self.githubLink.setTextInteractionFlags(Qt.TextInteractionFlag.LinksAccessibleByMouse|Qt.TextInteractionFlag.TextSelectableByMouse)

        self.verticalLayout_10.addWidget(self.githubLink)

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

        self.verticalLayout_10.addWidget(self.description)


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
        self.verticalLayout_15 = QVBoxLayout(self.settingsLeftWidget)
        self.verticalLayout_15.setSpacing(10)
        self.verticalLayout_15.setObjectName(u"verticalLayout_15")
        self.settingsHeaderLabel = QLabel(self.settingsLeftWidget)
        self.settingsHeaderLabel.setObjectName(u"settingsHeaderLabel")
        font3 = QFont()
        font3.setPointSize(24)
        self.settingsHeaderLabel.setFont(font3)

        self.verticalLayout_15.addWidget(self.settingsHeaderLabel)

        self.settingsHeaderLine = QFrame(self.settingsLeftWidget)
        self.settingsHeaderLine.setObjectName(u"settingsHeaderLine")
        self.settingsHeaderLine.setFrameShape(QFrame.Shape.HLine)
        self.settingsHeaderLine.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_15.addWidget(self.settingsHeaderLine)

        self.verticalSpacer_9 = QSpacerItem(20, 432, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_15.addItem(self.verticalSpacer_9)

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

        self.verticalSpacer_8 = QSpacerItem(20, 431, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.verticalLayout_15.addItem(self.verticalSpacer_8)


        self.horizontalLayout_5.addWidget(self.settingsLeftWidget)

        self.settingsRightWidget = QWidget(self.settingsPage)
        self.settingsRightWidget.setObjectName(u"settingsRightWidget")
        self.verticalLayout_16 = QVBoxLayout(self.settingsRightWidget)
        self.verticalLayout_16.setObjectName(u"verticalLayout_16")
        self.verticalSpacer_10 = QSpacerItem(20, 1010, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

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
        sizePolicy1 = QSizePolicy(QSizePolicy.Policy.Ignored, QSizePolicy.Policy.Ignored)
        sizePolicy1.setHorizontalStretch(0)
        sizePolicy1.setVerticalStretch(0)
        sizePolicy1.setHeightForWidth(self.videoStreamWidget.sizePolicy().hasHeightForWidth())
        self.videoStreamWidget.setSizePolicy(sizePolicy1)
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
        sizePolicy1.setHeightForWidth(self.videoStreamLabel.sizePolicy().hasHeightForWidth())
        self.videoStreamLabel.setSizePolicy(sizePolicy1)
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
        self.activeKeyBindingsWidget = QWidget(self.vehicleControlPanelWidget)
        self.activeKeyBindingsWidget.setObjectName(u"activeKeyBindingsWidget")
        self.verticalLayout_6 = QVBoxLayout(self.activeKeyBindingsWidget)
        self.verticalLayout_6.setObjectName(u"verticalLayout_6")
        self.keyBindingsLabel = QLabel(self.activeKeyBindingsWidget)
        self.keyBindingsLabel.setObjectName(u"keyBindingsLabel")
        self.keyBindingsLabel.setMinimumSize(QSize(0, 40))
        self.keyBindingsLabel.setMaximumSize(QSize(16777215, 40))
        self.keyBindingsLabel.setFont(font3)

        self.verticalLayout_6.addWidget(self.keyBindingsLabel)

        self.keyBindingsLine = QFrame(self.activeKeyBindingsWidget)
        self.keyBindingsLine.setObjectName(u"keyBindingsLine")
        self.keyBindingsLine.setFrameShape(QFrame.Shape.HLine)
        self.keyBindingsLine.setFrameShadow(QFrame.Shadow.Sunken)

        self.verticalLayout_6.addWidget(self.keyBindingsLine)

        self.keyBindListWidget = QWidget(self.activeKeyBindingsWidget)
        self.keyBindListWidget.setObjectName(u"keyBindListWidget")
        self.horizontalLayout_7 = QHBoxLayout(self.keyBindListWidget)
        self.horizontalLayout_7.setObjectName(u"horizontalLayout_7")
        self.horizontalLayout_7.setContentsMargins(-1, -1, -1, 0)
        self.keyActiveWidget = QWidget(self.keyBindListWidget)
        self.keyActiveWidget.setObjectName(u"keyActiveWidget")
        self.keyActiveWidget.setMinimumSize(QSize(60, 0))
        self.keyActiveWidget.setMaximumSize(QSize(60, 16777215))
        self.verticalLayout_11 = QVBoxLayout(self.keyActiveWidget)
        self.verticalLayout_11.setSpacing(0)
        self.verticalLayout_11.setObjectName(u"verticalLayout_11")
        self.verticalLayout_11.setContentsMargins(0, 0, 0, 0)
        self.wKeyLabel = QLabel(self.keyActiveWidget)
        self.wKeyLabel.setObjectName(u"wKeyLabel")
        self.wKeyLabel.setFont(font1)
        self.wKeyLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_11.addWidget(self.wKeyLabel)

        self.aKeyLabel = QLabel(self.keyActiveWidget)
        self.aKeyLabel.setObjectName(u"aKeyLabel")
        self.aKeyLabel.setFont(font1)
        self.aKeyLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_11.addWidget(self.aKeyLabel)

        self.sKeyLabel = QLabel(self.keyActiveWidget)
        self.sKeyLabel.setObjectName(u"sKeyLabel")
        self.sKeyLabel.setFont(font1)
        self.sKeyLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_11.addWidget(self.sKeyLabel)

        self.dKeyLabel = QLabel(self.keyActiveWidget)
        self.dKeyLabel.setObjectName(u"dKeyLabel")
        self.dKeyLabel.setFont(font1)
        self.dKeyLabel.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.verticalLayout_11.addWidget(self.dKeyLabel)


        self.horizontalLayout_7.addWidget(self.keyActiveWidget)

        self.keyInfoWitget = QWidget(self.keyBindListWidget)
        self.keyInfoWitget.setObjectName(u"keyInfoWitget")
        self.verticalLayout_12 = QVBoxLayout(self.keyInfoWitget)
        self.verticalLayout_12.setSpacing(0)
        self.verticalLayout_12.setObjectName(u"verticalLayout_12")
        self.verticalLayout_12.setContentsMargins(0, 0, 0, 0)
        self.accelerateLabel = QLabel(self.keyInfoWitget)
        self.accelerateLabel.setObjectName(u"accelerateLabel")
        self.accelerateLabel.setFont(font1)

        self.verticalLayout_12.addWidget(self.accelerateLabel)

        self.turnLeftLabel = QLabel(self.keyInfoWitget)
        self.turnLeftLabel.setObjectName(u"turnLeftLabel")
        self.turnLeftLabel.setFont(font1)

        self.verticalLayout_12.addWidget(self.turnLeftLabel)

        self.reverseBreakLabel = QLabel(self.keyInfoWitget)
        self.reverseBreakLabel.setObjectName(u"reverseBreakLabel")
        self.reverseBreakLabel.setFont(font1)

        self.verticalLayout_12.addWidget(self.reverseBreakLabel)

        self.turnRightLabel = QLabel(self.keyInfoWitget)
        self.turnRightLabel.setObjectName(u"turnRightLabel")
        self.turnRightLabel.setFont(font1)

        self.verticalLayout_12.addWidget(self.turnRightLabel)


        self.horizontalLayout_7.addWidget(self.keyInfoWitget)


        self.verticalLayout_6.addWidget(self.keyBindListWidget)


        self.horizontalLayout_6.addWidget(self.activeKeyBindingsWidget, 0, Qt.AlignmentFlag.AlignLeft)

        self.vehicleStatusWidget = QWidget(self.vehicleControlPanelWidget)
        self.vehicleStatusWidget.setObjectName(u"vehicleStatusWidget")
        self.vehicleStatusWidget.setMinimumSize(QSize(450, 0))
        self.vehicleStatusWidget.setMaximumSize(QSize(450, 16777215))
        self.verticalLayout_14 = QVBoxLayout(self.vehicleStatusWidget)
        self.verticalLayout_14.setObjectName(u"verticalLayout_14")
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


        self.horizontalLayout_6.addWidget(self.vehicleStatusWidget, 0, Qt.AlignmentFlag.AlignRight)


        self.verticalLayout_5.addWidget(self.vehicleControlPanelWidget)

        self.stackedWidget.addWidget(self.drivePage)

        self.verticalLayout_4.addWidget(self.stackedWidget)


        self.horizontalLayout.addWidget(self.mainPage)

        MainWindow.setCentralWidget(self.centralwidget)

        self.retranslateUi(MainWindow)

        self.stackedWidget.setCurrentIndex(0)


        QMetaObject.connectSlotsByName(MainWindow)
    # setupUi

    def retranslateUi(self, MainWindow):
        MainWindow.setWindowTitle(QCoreApplication.translate("MainWindow", u"MainWindow", None))
#if QT_CONFIG(tooltip)
        self.homeBtn.setToolTip(QCoreApplication.translate("MainWindow", u"Home", None))
#endif // QT_CONFIG(tooltip)
        self.homeBtn.setText("")
        self.driveBtn.setText("")
        self.settingsBtn.setText("")
#if QT_CONFIG(tooltip)
        self.mainPage.setToolTip("")
#endif // QT_CONFIG(tooltip)
        self.ipInputBox.setTitle(QCoreApplication.translate("MainWindow", u"Enter an ip address to connect", None))
        self.inputIp.setPlaceholderText(QCoreApplication.translate("MainWindow", u"Enter an ip address...", None))
        self.recentIpBox.setTitle(QCoreApplication.translate("MainWindow", u"Connect to a recent ip address", None))
        self.recentIpCombo.setItemText(0, "")
        '''
        self.recentIpCombo.setItemText(1, QCoreApplication.translate("MainWindow", u"ip-addr test-1", None))
        self.recentIpCombo.setItemText(2, QCoreApplication.translate("MainWindow", u"ip-addr test-2", None))
        self.recentIpCombo.setItemText(3, QCoreApplication.translate("MainWindow", u"ip-addr test-3", None))
        self.recentIpCombo.setItemText(4, QCoreApplication.translate("MainWindow", u"ip-addr test-4", None))
        self.recentIpCombo.setItemText(5, QCoreApplication.translate("MainWindow", u"ip-addr test-5", None))
        '''
        self.ipComboBtn.setText("")
        self.label_2.setText("")
        self.projectTitle.setText(QCoreApplication.translate("MainWindow", u"Follow the project on GitHub", None))
        self.githubLink.setText(QCoreApplication.translate("MainWindow", u"https://github.com/HalfasleepDev/DriveCore", None))
        self.aboutTitle.setText(QCoreApplication.translate("MainWindow", u"About", None))
        self.description.setText(QCoreApplication.translate("MainWindow", u"DriveCore is a modular and scalable platform designed for controlling RC vehicles with the potential for AI-powered autonomy. Built using Python, OpenCV, and a Raspberry Pi, DriveCore serves as the foundation for both manual and automated vehicle operation, integrating computer vision, sensor fusion, and remote control capabilities.", None))
        self.settingsHeaderLabel.setText(QCoreApplication.translate("MainWindow", u"Settings", None))
        self.emergencyDisconnectBtn.setText(QCoreApplication.translate("MainWindow", u"EMERGENCY DISCONNECT", None))
        self.emergencyDisconnectLabel.setText(QCoreApplication.translate("MainWindow", u"WARNING: WILL STOP PROGRAM ON HOST", None))
        self.currentPgrmVersionHeaderLabel.setText(QCoreApplication.translate("MainWindow", u"Current Program Version: ", None))
        self.currentPgrmVersionLabel.setText(QCoreApplication.translate("MainWindow", u"Ver 1.0 (21-02-2025)", None))
        self.videoStreamLabel.setText(QCoreApplication.translate("MainWindow", u"No Conncection", None))
        self.keyBindingsLabel.setText(QCoreApplication.translate("MainWindow", u"Key Bindings", None))
        self.wKeyLabel.setText(QCoreApplication.translate("MainWindow", u"[W]", None))
        self.aKeyLabel.setText(QCoreApplication.translate("MainWindow", u"[A]", None))
        self.sKeyLabel.setText(QCoreApplication.translate("MainWindow", u"[S]", None))
        self.dKeyLabel.setText(QCoreApplication.translate("MainWindow", u"[D]", None))
        self.accelerateLabel.setText(QCoreApplication.translate("MainWindow", u":     Accelerate", None))
        self.turnLeftLabel.setText(QCoreApplication.translate("MainWindow", u":     Turn Left", None))
        self.reverseBreakLabel.setText(QCoreApplication.translate("MainWindow", u":    Reverse/Break", None))
        self.turnRightLabel.setText(QCoreApplication.translate("MainWindow", u":    Turn Right", None))
        self.currentVehicleLabel.setText(QCoreApplication.translate("MainWindow", u"Current vehicle connected to:", None))
        self.vehicleTypeLabel.setText(QCoreApplication.translate("MainWindow", u"Unknown", None))
    # retranslateUi

