from Main_Window import *

class New_Configuration(QtWidgets.QWidget):

    def __init__(self, path, name, description):
        super(New_Configuration, self).__init__()
        self.path = path
        self.name = name
        self.description = description
        self.setupUi(self)
        self.Config()

    def setupUi(self, Dialog):
        Dialog.setObjectName("Dialog")
        Dialog.resize(971, 284)
        self.acces_configuration = QtWidgets.QGroupBox(Dialog)
        self.acces_configuration.setGeometry(QtCore.QRect(20, 20, 931, 251))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.acces_configuration.setFont(font)
        self.acces_configuration.setObjectName("acces_configuration")
        self.groupBox_3 = QtWidgets.QGroupBox(self.acces_configuration)
        self.groupBox_3.setGeometry(QtCore.QRect(311, 101, 601, 101))
        font = QtGui.QFont()
        font.setPointSize(8)
        self.groupBox_3.setFont(font)
        self.groupBox_3.setObjectName("groupBox_3")
        self.formLayoutWidget_2 = QtWidgets.QWidget(self.groupBox_3)
        self.formLayoutWidget_2.setGeometry(QtCore.QRect(10, 20, 581, 80))
        self.formLayoutWidget_2.setObjectName("formLayoutWidget_2")
        self.formLayout_2 = QtWidgets.QFormLayout(self.formLayoutWidget_2)
        self.formLayout_2.setContentsMargins(0, 0, 0, 0)
        self.formLayout_2.setObjectName("formLayout_2")
        self.label_3 = QtWidgets.QLabel(self.formLayoutWidget_2)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setBold(True)
        font.setWeight(75)
        self.label_3.setFont(font)
        self.label_3.setObjectName("label_3")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label_3)
        self.label_5 = QtWidgets.QLabel(self.formLayoutWidget_2)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setBold(True)
        font.setWeight(75)
        self.label_5.setFont(font)
        self.label_5.setObjectName("label_5")
        self.formLayout_2.setWidget(3, QtWidgets.QFormLayout.LabelRole, self.label_5)
        self.label_4 = QtWidgets.QLabel(self.formLayoutWidget_2)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setBold(True)
        font.setWeight(75)
        self.label_4.setFont(font)
        self.label_4.setObjectName("label_4")
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_4)
        self.access_token = QtWidgets.QLineEdit(self.formLayoutWidget_2)
        self.access_token.setObjectName("access_token")
        self.formLayout_2.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.access_token)
        self.aceess_secret_token = QtWidgets.QLineEdit(self.formLayoutWidget_2)
        self.aceess_secret_token.setObjectName("aceess_secret_token")
        self.formLayout_2.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.aceess_secret_token)
        self.bearer_token = QtWidgets.QLineEdit(self.formLayoutWidget_2)
        self.bearer_token.setObjectName("bearer_token")
        self.formLayout_2.setWidget(3, QtWidgets.QFormLayout.FieldRole, self.bearer_token)
        self.formLayoutWidget = QtWidgets.QWidget(self.acces_configuration)
        self.formLayoutWidget.setGeometry(QtCore.QRect(30, 30, 871, 52))
        self.formLayoutWidget.setObjectName("formLayoutWidget")
        self.formLayout = QtWidgets.QFormLayout(self.formLayoutWidget)
        self.formLayout.setContentsMargins(0, 0, 0, 0)
        self.formLayout.setObjectName("formLayout")
        self.label = QtWidgets.QLabel(self.formLayoutWidget)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setBold(True)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName("label")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.LabelRole, self.label)
        self.consumer_key = QtWidgets.QLineEdit(self.formLayoutWidget)
        self.consumer_key.setObjectName("consumer_key")
        self.formLayout.setWidget(0, QtWidgets.QFormLayout.FieldRole, self.consumer_key)
        self.label_2 = QtWidgets.QLabel(self.formLayoutWidget)
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setBold(True)
        font.setWeight(75)
        self.label_2.setFont(font)
        self.label_2.setObjectName("label_2")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.LabelRole, self.label_2)
        self.consumer_secret_key = QtWidgets.QLineEdit(self.formLayoutWidget)
        self.consumer_secret_key.setObjectName("consumer_secret_key")
        self.formLayout.setWidget(1, QtWidgets.QFormLayout.FieldRole, self.consumer_secret_key)
        self.save_credentials = QtWidgets.QPushButton(self.acces_configuration)
        self.save_credentials.setGeometry(QtCore.QRect(820, 220, 91, 21))
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setBold(False)
        font.setWeight(50)
        self.save_credentials.setFont(font)
        self.save_credentials.setObjectName("save_credentials")
        self.type_access = QtWidgets.QGroupBox(self.acces_configuration)
        self.type_access.setGeometry(QtCore.QRect(30, 100, 131, 121))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setBold(True)
        font.setWeight(75)
        self.type_access.setFont(font)
        self.type_access.setObjectName("type_access")
        self.horizontalLayoutWidget = QtWidgets.QWidget(self.type_access)
        self.horizontalLayoutWidget.setGeometry(QtCore.QRect(10, 20, 111, 92))
        self.horizontalLayoutWidget.setObjectName("horizontalLayoutWidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.horizontalLayoutWidget)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setSpacing(15)
        self.verticalLayout.setObjectName("verticalLayout")
        self.standard = QtWidgets.QRadioButton(self.horizontalLayoutWidget)
        self.standard.setChecked(True)
        self.standard.setObjectName("standard")
        self.verticalLayout.addWidget(self.standard)
        self.academic = QtWidgets.QRadioButton(self.horizontalLayoutWidget)
        self.academic.setObjectName("academic")
        self.verticalLayout.addWidget(self.academic)
        self.premium = QtWidgets.QRadioButton(self.horizontalLayoutWidget)
        self.premium.setObjectName("premium")
        self.verticalLayout.addWidget(self.premium)
        self.type_oauth = QtWidgets.QGroupBox(self.acces_configuration)
        self.type_oauth.setGeometry(QtCore.QRect(171, 101, 131, 121))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setBold(True)
        font.setWeight(75)
        self.type_oauth.setFont(font)
        self.type_oauth.setObjectName("type_oauth")
        self.horizontalLayoutWidget_2 = QtWidgets.QWidget(self.type_oauth)
        self.horizontalLayoutWidget_2.setGeometry(QtCore.QRect(10, 20, 111, 91))
        self.horizontalLayoutWidget_2.setObjectName("horizontalLayoutWidget_2")
        self.verticalLayout_2 = QtWidgets.QVBoxLayout(self.horizontalLayoutWidget_2)
        self.verticalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_2.setSpacing(15)
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.oauth1 = QtWidgets.QRadioButton(self.horizontalLayoutWidget_2)
        self.oauth1.setChecked(True)
        self.oauth1.setObjectName("oauth1")
        self.verticalLayout_2.addWidget(self.oauth1)
        self.oauth2 = QtWidgets.QRadioButton(self.horizontalLayoutWidget_2)
        self.oauth2.setObjectName("oauth2")
        self.verticalLayout_2.addWidget(self.oauth2)
        self.listView = QtWidgets.QListView(Dialog)
        self.listView.setGeometry(QtCore.QRect(-100, -40, 1131, 341))
        self.listView.setObjectName("listView")
        self.listView.raise_()
        self.acces_configuration.raise_()

        self.retranslateUi(Dialog)
        QtCore.QMetaObject.connectSlotsByName(Dialog)

    def retranslateUi(self, Dialog):
        _translate = QtCore.QCoreApplication.translate
        Dialog.setWindowTitle(_translate("Dialog", "Dialog"))
        self.acces_configuration.setTitle(_translate("Dialog", "Access configuration"))
        self.groupBox_3.setTitle(_translate("Dialog", "Tokens"))
        self.label_3.setText(_translate("Dialog", "Access Token:"))
        self.label_5.setText(_translate("Dialog", "Bearer Token:"))
        self.label_4.setText(_translate("Dialog", "Access Secret Token:"))
        self.label.setText(_translate("Dialog", "Consumer Key:"))
        self.label_2.setText(_translate("Dialog", "Consumer Secret Key:"))
        self.save_credentials.setText(_translate("Dialog", "Next"))
        self.type_access.setTitle(_translate("Dialog", "Type Access"))
        self.standard.setText(_translate("Dialog", "Standard"))
        self.academic.setText(_translate("Dialog", "Academic"))
        self.premium.setText(_translate("Dialog", "Premium"))
        self.type_oauth.setTitle(_translate("Dialog", "Type OAuth"))
        self.oauth1.setText(_translate("Dialog", "OAuth1"))
        self.oauth2.setText(_translate("Dialog", "OAuth2"))

    def Config(self):
        self.oauth2.setEnabled(False)
        self.oauth1.setEnabled(False)
        self.bearer_token.setEnabled(False)
        self.standard.clicked.connect(lambda: self.change_oauth("standard"))
        self.academic.clicked.connect(lambda: self.change_oauth("academic"))
        self.premium.clicked.connect(lambda: self.change_oauth("premium"))
        self.save_credentials.clicked.connect(lambda: self.save_cred())

    def change_oauth(self,type):

        if(type == "academic" or type == "premium"):
            self.oauth2.setChecked(True)
            self.bearer_token.setEnabled(True)
            self.consumer_key.setEnabled(False)
            self.consumer_secret_key.setEnabled(False)
            self.access_token.setEnabled(False)
            self.aceess_secret_token.setEnabled(False)
        elif(type == "standard"):
            self.oauth1.setChecked(True)
            self.bearer_token.setEnabled(False)
            self.consumer_key.setEnabled(True)
            self.consumer_secret_key.setEnabled(True)
            self.access_token.setEnabled(True)
            self.aceess_secret_token.setEnabled(True)

    def save_cred(self):

        if(self.standard.isChecked()):
            if(self.consumer_key.text() and self.consumer_secret_key.text() and self.access_token.text() and self.aceess_secret_token.text()):
                dictionary = {'Type':'oauth1',
                              'name':self.name,
                              'description':self.description,
                              'path':self.path,
                              'consumer_key':self.consumer_key.text(),
                              'consumer_secret_key':self.consumer_secret_key.text(),
                              'access_token':self.access_token.text(),
                              'aceess_secret_token':self.aceess_secret_token.text()}

                aux = self.path + '/' + 'oauth1'
                try:
                    with open(aux+'.json', 'w') as fp:
                        json.dump(dictionary, fp)

                    self.MainWindow = MainWindow(False,self.path)
                    self.MainWindow.show()
                    self.close()
                except:
                    msg = QtWidgets.QMessageBox()
                    msg.setIcon(QtWidgets.QMessageBox.Warning)
                    msg.setText("Error")
                    msg.setInformativeText('Please try again')
                    msg.setWindowTitle("Error")
                    msg.exec_()
            else:
                msg = QtWidgets.QMessageBox()
                msg.setIcon(QtWidgets.QMessageBox.Warning)
                msg.setText("Error")
                msg.setInformativeText('Please introduce all the values')
                msg.setWindowTitle("Error")
                msg.exec_()
        elif(self.academic.isChecked() or self.premium.isChecked()):
            if(self.bearer_token.text()):
                dictionary = {'Type':'oauth2',
                              'name':self.name,
                              'description':self.description,
                              'path':self.path,
                              'bearer_token': self.bearer_token.text()}

                aux = self.path + '/' + 'oauth2'
                try:
                    with open(aux + '.json', 'w') as fp:
                        json.dump(dictionary, fp)

                    self.MainWindow = MainWindow(False,self.path)
                    self.MainWindow.show()
                    self.close()
                except:
                    msg = QtWidgets.QMessageBox()
                    msg.setIcon(QtWidgets.QMessageBox.Warning)
                    msg.setText("Error")
                    msg.setInformativeText('Please try again')
                    msg.setWindowTitle("Error")
                    msg.exec_()
            else:
                msg = QtWidgets.QMessageBox()
                msg.setIcon(QtWidgets.QMessageBox.Warning)
                msg.setText("Error")
                msg.setInformativeText('Please introduce all the values')
                msg.setWindowTitle("Error")
                msg.exec_()
