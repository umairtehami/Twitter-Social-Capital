import sys
from PyQt5 import QtCore, QtGui, QtWidgets
import time as t

# OutLog class is used to show the feedback messages in the Log through the visual panel.
class OutLog:
    def __init__(self, edit, out=None, color=None):
        self.edit = edit
        self.out = out
        self.color = color

    def write(self, m):
        t.sleep(0.1)
        if self.color:
            self.tc = self.edit.textColor()
            self.edit.setTextColor(self.color)

        self.edit.moveCursor(QtGui.QTextCursor.End)
        self.edit.insertPlainText(m)

# Feedback class gives extraction evolution information to the user.
class Feedback(QtWidgets.QWidget):

    def __init__(self, communicate):
        super(Feedback, self).__init__()
        self.communicate  = communicate
        self.setupUi(self)
        self.Config()
        sys.stdout = OutLog(self.visual_panel, sys.stdout)

    # Used to print the UI components
    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(805, 394)
        self.buttonBox = QtWidgets.QDialogButtonBox(Dialog)
        self.buttonBox.setGeometry(QtCore.QRect(450, 450, 341, 32))
        self.buttonBox.setOrientation(QtCore.Qt.Horizontal)
        self.buttonBox.setStandardButtons(QtWidgets.QDialogButtonBox.Cancel|QtWidgets.QDialogButtonBox.Ok)
        self.buttonBox.setObjectName("buttonBox")
        self.listWidget = QtWidgets.QListWidget(Dialog)
        self.listWidget.setEnabled(True)
        self.listWidget.setGeometry(QtCore.QRect(-45, -19, 881, 541))
        self.listWidget.setObjectName("listWidget")
        self.groupBox = QtWidgets.QGroupBox(Dialog)
        self.groupBox.setGeometry(QtCore.QRect(20, 20, 771, 251))
        self.groupBox.setObjectName("groupBox")
        self.visual_panel = QtWidgets.QTextBrowser(self.groupBox)
        self.visual_panel.setGeometry(QtCore.QRect(10, 20, 751, 211))
        self.visual_panel.setObjectName("visual_panel")
        self.groupBox_2 = QtWidgets.QGroupBox(Dialog)
        self.groupBox_2.setGeometry(QtCore.QRect(19, 279, 771, 71))
        self.groupBox_2.setObjectName("groupBox_2")
        self.progressBar = QtWidgets.QProgressBar(self.groupBox_2)
        self.progressBar.setGeometry(QtCore.QRect(10, 30, 751, 23))
        self.progressBar.setProperty("value", 0)
        self.progressBar.setObjectName("progressBar")
        self.cerrar = QtWidgets.QPushButton(Dialog)
        self.cerrar.setEnabled(False)
        self.cerrar.setGeometry(QtCore.QRect(710, 360, 75, 23))
        self.cerrar.setObjectName("close")

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    # Used to print the UI components
    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.groupBox.setTitle(_translate("Dialog", "Execution"))
        self.groupBox_2.setTitle(_translate("Dialog", "Progress"))
        self.cerrar.setText(_translate("Dialog", "Close"))

    # Visual and Logical configurations of the Feedback Window.
    def Config(self):
        self.cerrar.clicked.connect(lambda : self.cerrar_ventana())

    # Update the progress bar
    def update_progress(self, pro):
        self.progressBar.setValue(pro)
        if (pro == 100):
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Information)
            msg.setText("Completed")
            msg.setInformativeText('Extraction completed successfully')
            msg.setWindowTitle("Completed")
            msg.exec_()

        if(pro==9999):
            self.cerrar.setEnabled(True)

    # Closes the window when the extraction had finished.
    def cerrar_ventana(self):
        self.close()