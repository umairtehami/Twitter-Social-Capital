from PyQt5 import QtCore, QtGui, QtWidgets
from Main_Window import *
from New_Project import *

class Start_Window(QtWidgets.QWidget):

    def __init__(self):
        super(Start_Window, self).__init__()
        self.setupUi(self)
        self.Config()

    def setupUi(self, Form):
        Form.setObjectName("Form")
        Form.resize(381, 251)
        self.listView = QtWidgets.QListView(Form)
        self.listView.setGeometry(QtCore.QRect(-20, -10, 411, 361))
        self.listView.setObjectName("listView")
        self.pushButton = QtWidgets.QPushButton(Form)
        self.pushButton.setGeometry(QtCore.QRect(10, 149, 359, 41))
        self.pushButton.setIconSize(QtCore.QSize(16, 30))
        self.pushButton.setObjectName("pushButton")
        self.pushButton_2 = QtWidgets.QPushButton(Form)
        self.pushButton_2.setGeometry(QtCore.QRect(10, 196, 359, 41))
        self.pushButton_2.setObjectName("pushButton_2")
        self.label = QtWidgets.QLabel(Form)
        self.label.setEnabled(True)
        self.label.setGeometry(QtCore.QRect(10, 10, 359, 121))
        font = QtGui.QFont()
        font.setFamily("Microsoft YaHei")
        font.setPointSize(16)
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        font.setStrikeOut(False)
        self.label.setFont(font)
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.label.setWordWrap(True)
        self.label.setObjectName("label")

        self.retranslateUi(Form)
        QtCore.QMetaObject.connectSlotsByName(Form)

    def retranslateUi(self, Form):
        _translate = QtCore.QCoreApplication.translate
        Form.setWindowTitle(_translate("Form", "Form"))
        self.pushButton.setText(_translate("Form", "Create new project"))
        self.pushButton_2.setText(_translate("Form", "Open project"))
        self.label.setText(_translate("Form", "MINER DATA"))

    def Config(self):
        self.pushButton.clicked.connect(lambda: self.Create_new_Project())
        self.pushButton_2.clicked.connect(lambda: self.Open_project())
        self.pushButton.setStyleSheet("background-color : rgb(1, 130, 153); color : white; style : outset; border-radius : 6px")
        self.pushButton_2.setStyleSheet("background-color : rgb(1, 130, 153); color : white; style : outset; border-radius : 6px")
        self.label.setStyleSheet("background-color : white; color : rgb(1, 130, 153); style : outset;")


    def Create_new_Project(self):
        self.New_Project = New_Project()
        self.New_Project.show()
        self.close()

    def Open_project(self):
        try:
            fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Single File', QtCore.QDir.rootPath() , '*.json')
            if(fileName != ""):
                self.MainWindow = MainWindow(True,fileName)
                self.MainWindow.show()
                self.close()
        except:
            pass
