from PyQt5 import QtCore, QtGui, QtWidgets
import os

from PyQt5.QtGui import QIcon

from Project import *
import json

class New_Project(QtWidgets.QWidget):

    def __init__(self, communicate):
        super(New_Project, self).__init__()
        self.communicate  = communicate
        self.setupUi(self)
        self.Config()

    # Used to print the UI components
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(955, 221)
        self.project_managment = QtWidgets.QGroupBox(Dialog)
        self.project_managment.setGeometry(QtCore.QRect(20, 10, 921, 191))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.project_managment.setFont(font)
        self.project_managment.setObjectName("project_managment")
        self.next_project = QtWidgets.QPushButton(self.project_managment)
        self.next_project.setGeometry(QtCore.QRect(820, 160, 91, 21))
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setBold(False)
        font.setWeight(50)
        self.next_project.setFont(font)
        self.next_project.setObjectName("next_project")
        self.horizontalLayoutWidget = QtWidgets.QWidget(self.project_managment)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(10, 50, 901, 41))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.lineEdit = QtWidgets.QLineEdit(self.horizontalLayoutWidget)
        self.lineEdit.setObjectName("lineEdit")
        self.horizontalLayout.addWidget(self.lineEdit)
        self.lineEdit_2 = QtWidgets.QLineEdit(self.horizontalLayoutWidget)
        self.lineEdit_2.setObjectName("lineEdit_2")
        self.horizontalLayout.addWidget(self.lineEdit_2)
        self.pushButton = QtWidgets.QPushButton(self.horizontalLayoutWidget)
        font = QtGui.QFont()
        font.setBold(False)
        font.setWeight(50)
        self.pushButton.setFont(font)
        self.pushButton.setObjectName("pushButton")
        self.horizontalLayout.addWidget(self.pushButton)
        self.horizontalLayoutWidget_2 = QtWidgets.QWidget(self.project_managment)
        self.horizontalLayoutWidget_2.setGeometry(QtCore.QRect(9, 30, 821, 21))
        self.horizontalLayoutWidget_2.setObjectName("horizontalLayoutWidget_2")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget_2)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_2 = QtWidgets.QLabel(self.horizontalLayoutWidget_2)
        self.label_2.setObjectName("label_2")
        self.horizontalLayout_2.addWidget(self.label_2)
        self.label = QtWidgets.QLabel(self.horizontalLayoutWidget_2)
        self.label.setObjectName("label")
        self.horizontalLayout_2.addWidget(self.label)
        self.verticalLayoutWidget = QtWidgets.QWidget(self.project_managment)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(10, 90, 901, 46))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label_3 = QtWidgets.QLabel(self.verticalLayoutWidget)
        self.label_3.setObjectName("label_3")
        self.verticalLayout.addWidget(self.label_3)
        self.lineEdit_3 = QtWidgets.QLineEdit(self.verticalLayoutWidget)
        self.lineEdit_3.setObjectName("lineEdit_3")
        self.verticalLayout.addWidget(self.lineEdit_3)
        self.listView = QtWidgets.QListView(Dialog)
        self.listView.setGeometry(QtCore.QRect(-25, -9, 1021, 251))
        self.listView.setObjectName("listView")
        self.listView.raise_()
        self.project_managment.raise_()

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    # Used to print the UI components
    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.project_managment.setTitle(_translate("Dialog", "Project Managment"))
        self.next_project.setText(_translate("Dialog", "Create"))
        self.pushButton.setText(_translate("Dialog", "Select"))
        self.label_2.setText(_translate("Dialog", "Name"))
        self.label.setText(_translate("Dialog", "Path"))
        self.label_3.setText(_translate("Dialog", "Description"))

    # Visual and Logical configurations of the New Project Window.
    def Config(self):
        self.next_project.clicked.connect(lambda: self.Create_new_Configuration())
        self.pushButton.clicked.connect(lambda: self.get_path())
        self.lineEdit_2.setEnabled(False)
        self.next_project.setStyleSheet("background-color : rgb(1, 130, 153); color : white; style : outset; border-radius : 6px")
        self.pushButton.setStyleSheet("background-color : rgb(1, 130, 153); color : white;")
        self.setWindowTitle('Extraction Configuration')
        self.setWindowIcon(QIcon('network.png'))

    # Show a browser window to select the save path for project.
    def get_path(self):
        file = str(QtWidgets.QFileDialog.getExistingDirectory(self, "Select Directory"))
        if(len(file) != 0):
            self.lineEdit_2.setText(file)
            self.lineEdit_2.setStyleSheet("background-color : rgb(144,238,144); color : white; style : outset;")

    # Create a new project folder on user specified path
    def Create_new_Configuration(self):
        if(self.lineEdit.text() and self.lineEdit_2.text() and self.lineEdit_3.text()):
            file = self.lineEdit_2.text() + "/" + self.lineEdit.text()
            try:
                self.project = Project(self.lineEdit.text(), self.lineEdit_3.text(), file)
                os.mkdir(file)
                dictionary = {'name': self.project.name,
                              'description': self.project.description,
                              'path': self.project.path}

                aux = self.project.path + '/' + 'config.json'
                try:
                    with open(aux, 'w') as fp:
                        json.dump(dictionary, fp)

                    # Show message if the project has created successfully
                    self.communicate.sig.emit(100)
                    msg = QtWidgets.QMessageBox()
                    msg.setIcon(QtWidgets.QMessageBox.Information)
                    msg.setText("Save Correct")
                    msg.setInformativeText('Project saved successfully')
                    msg.setWindowTitle("Saved")
                    msg.exec_()
                    self.close()
                except:
                    # Show message if the project creation failed.
                    msg = QtWidgets.QMessageBox()
                    msg.setIcon(QtWidgets.QMessageBox.Warning)
                    msg.setText("Error")
                    msg.setInformativeText('Please try again')
                    msg.setWindowTitle("Error")
                    msg.exec_()
            except OSError:
                # Show message if the project already exists.
                msg = QtWidgets.QMessageBox()
                msg.setIcon(QtWidgets.QMessageBox.Warning)
                msg.setText("Error")
                msg.setInformativeText('Project already exists')
                msg.setWindowTitle("Error")
                msg.exec_()
        else:
            # Show message if any attribute is empty
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Warning)
            msg.setText("Error")
            msg.setInformativeText('Please introduce all the values')
            msg.setWindowTitle("Error")
            msg.exec_()

    # Returns current project entity
    def return_project(self):
        return self.project