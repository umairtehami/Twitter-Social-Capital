from PyQt5.QtGui import QIcon

from Feedback import Feedback
from New_Credentials import *
from New_Project import *
from PyQt5.QtCore import QThread, QObject, pyqtSignal, QTime
from List import *
from OAuth1 import *
from OAuth2 import *
from Project import *
from Unweighted import *
from Weighted import *
from Tweets import *
import os

# Communicate class allow us to send and receive signals between threads.
class Communicate(QObject):
    sig = pyqtSignal(int)

# Worker class execute the extraction in background.
class Worker(QObject):
    finished = pyqtSignal()
    intCount = pyqtSignal(int)

    def __init__(self, extraction, communicate = Communicate()):
        super(Worker, self).__init__()
        self.extraction = extraction
        self.com = communicate

    # Ran the different extractions.
    def run(self):
        """Long-running task."""
        if(self.extraction.type == "followers"):
            self.extraction.execute_followers(self.com)
        elif (self.extraction.type == "mentions"):
            self.extraction.execute_mentions(self.com)
        elif(self.extraction.type == "followers_weighted"):
            self.extraction.execute_followers_weighted(self.com)
        elif (self.extraction.type == "mentions_weighted"):
            self.extraction.execute_mentions_weighted(self.com)
        elif (self.extraction.type == "Tweets"):
            self.extraction.execute_tweets(self.com)

# OutLog class is used to show the feedback messages in the Log through the visual panel.
class OutLog:
    def __init__(self, edit, out=None, color=None):
        self.edit = edit
        self.out = out
        self.color = color

    def write(self, m):
        if self.color:
            self.tc = self.edit.textColor()
            self.edit.setTextColor(self.color)

        self.edit.moveCursor(QtGui.QTextCursor.End)
        self.edit.insertPlainText(m)

        if self.color:
            self.edit.setTextColor(self.tc)

        if self.out:
            self.out.write(m)

# Main Window class
class MainWindow(QtWidgets.QMainWindow):

    def __init__(self):
        super(MainWindow, self).__init__()
        self.project = None
        self.oauth = None
        self.setupUi(self)
        self.Config()

    # Progress bar updating
    def updateProgress(self,pro):
        self.feedback.update_progress(pro)

        #if the progress bar is complete, finish the thread and allow another extraction.
        if(pro == 9999):
            self.thread.exit()
            self.extract.setEnabled(True)

    # Used to print the UI components
    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(949, 897)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.list_id = QtWidgets.QGroupBox(self.centralwidget)
        self.list_id.setGeometry(QtCore.QRect(40, 630, 411, 51))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.list_id.setFont(font)
        self.list_id.setObjectName("list_id")
        self.edit_list_id = QtWidgets.QLineEdit(self.list_id)
        self.edit_list_id.setGeometry(QtCore.QRect(12, 19, 391, 21))
        self.edit_list_id.setObjectName("edit_list_id")
        self.network = QtWidgets.QGroupBox(self.centralwidget)
        self.network.setGeometry(QtCore.QRect(40, 440, 131, 181))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setBold(True)
        font.setWeight(75)
        self.network.setFont(font)
        self.network.setObjectName("network")
        self.verticalLayoutWidget = QtWidgets.QWidget(self.network)
        self.verticalLayoutWidget.setGeometry(QtCore.QRect(10, 29, 111, 141))
        self.verticalLayoutWidget.setObjectName("verticalLayoutWidget")
        self.verticalLayout_3 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget)
        self.verticalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.followers = QtWidgets.QRadioButton(self.verticalLayoutWidget)
        self.followers.setChecked(False)
        self.followers.setAutoExclusive(False)
        self.followers.setObjectName("followers")
        self.verticalLayout_3.addWidget(self.followers)
        self.mentions = QtWidgets.QRadioButton(self.verticalLayoutWidget)
        self.mentions.setObjectName("mentions")
        self.verticalLayout_3.addWidget(self.mentions)
        self.type_relations = QtWidgets.QGroupBox(self.centralwidget)
        self.type_relations.setGeometry(QtCore.QRect(180, 440, 131, 181))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setBold(True)
        font.setWeight(75)
        self.type_relations.setFont(font)
        self.type_relations.setObjectName("type_relations")
        self.verticalLayoutWidget_2 = QtWidgets.QWidget(self.type_relations)
        self.verticalLayoutWidget_2.setGeometry(QtCore.QRect(10, 30, 111, 141))
        self.verticalLayoutWidget_2.setObjectName("verticalLayoutWidget_2")
        self.verticalLayout_4 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_2)
        self.verticalLayout_4.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.simple = QtWidgets.QRadioButton(self.verticalLayoutWidget_2)
        self.simple.setChecked(True)
        self.simple.setObjectName("simple")
        self.verticalLayout_4.addWidget(self.simple)
        self.weigthed = QtWidgets.QRadioButton(self.verticalLayoutWidget_2)
        self.weigthed.setCheckable(True)
        self.weigthed.setChecked(False)
        self.weigthed.setObjectName("weigthed")
        self.verticalLayout_4.addWidget(self.weigthed)
        self.type_weight = QtWidgets.QGroupBox(self.centralwidget)
        self.type_weight.setEnabled(True)
        self.type_weight.setGeometry(QtCore.QRect(320, 440, 131, 181))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setBold(True)
        font.setWeight(75)
        self.type_weight.setFont(font)
        self.type_weight.setObjectName("type_weight")
        self.verticalLayoutWidget_3 = QtWidgets.QWidget(self.type_weight)
        self.verticalLayoutWidget_3.setGeometry(QtCore.QRect(10, 30, 111, 141))
        self.verticalLayoutWidget_3.setObjectName("verticalLayoutWidget_3")
        self.verticalLayout_5 = QtWidgets.QVBoxLayout(self.verticalLayoutWidget_3)
        self.verticalLayout_5.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout_5.setObjectName("verticalLayout_5")
        self.weight_mentions = QtWidgets.QCheckBox(self.verticalLayoutWidget_3)
        self.weight_mentions.setChecked(False)
        self.weight_mentions.setObjectName("weight_mentions")
        self.verticalLayout_5.addWidget(self.weight_mentions)
        self.weight_retweets = QtWidgets.QCheckBox(self.verticalLayoutWidget_3)
        self.weight_retweets.setObjectName("weight_retweets")
        self.verticalLayout_5.addWidget(self.weight_retweets)
        self.weight_replies = QtWidgets.QCheckBox(self.verticalLayoutWidget_3)
        self.weight_replies.setObjectName("weight_replies")
        self.verticalLayout_5.addWidget(self.weight_replies)
        self.acces_configuration = QtWidgets.QGroupBox(self.centralwidget)
        self.acces_configuration.setGeometry(QtCore.QRect(10, 160, 931, 241))
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
        self.new_credentials = QtWidgets.QPushButton(self.acces_configuration)
        self.new_credentials.setGeometry(QtCore.QRect(820, 210, 81, 21))
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setBold(False)
        font.setWeight(50)
        self.new_credentials.setFont(font)
        self.new_credentials.setObjectName("new_credentials")
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
        self.save_credentials = QtWidgets.QPushButton(self.acces_configuration)
        self.save_credentials.setGeometry(QtCore.QRect(730, 210, 81, 21))
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setBold(False)
        font.setWeight(50)
        self.save_credentials.setFont(font)
        self.save_credentials.setObjectName("save_credentials")
        self.import_credentials = QtWidgets.QPushButton(self.acces_configuration)
        self.import_credentials.setGeometry(QtCore.QRect(630, 210, 91, 21))
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setBold(False)
        font.setWeight(50)
        self.import_credentials.setFont(font)
        self.import_credentials.setObjectName("import_credentials")
        self.execution = QtWidgets.QGroupBox(self.centralwidget)
        self.execution.setGeometry(QtCore.QRect(480, 710, 461, 131))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.execution.setFont(font)
        self.execution.setObjectName("execution")
        self.extract = QtWidgets.QPushButton(self.execution)
        self.extract.setGeometry(QtCore.QRect(130, 80, 201, 21))
        self.extract.setObjectName("extract")
        self.network_configuration = QtWidgets.QGroupBox(self.centralwidget)
        self.network_configuration.setGeometry(QtCore.QRect(10, 410, 931, 291))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.network_configuration.setFont(font)
        self.network_configuration.setObjectName("network_configuration")
        self.groupBox = QtWidgets.QGroupBox(self.network_configuration)
        self.groupBox.setGeometry(QtCore.QRect(470, 30, 441, 251))
        self.groupBox.setTitle("")
        self.groupBox.setObjectName("groupBox")
        self.tweet_information = QtWidgets.QGroupBox(self.groupBox)
        self.tweet_information.setEnabled(True)
        self.tweet_information.setGeometry(QtCore.QRect(10, 50, 421, 191))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setBold(True)
        font.setWeight(75)
        self.tweet_information.setFont(font)
        self.tweet_information.setObjectName("tweet_information")
        self.gridLayoutWidget = QtWidgets.QWidget(self.tweet_information)
        self.gridLayoutWidget.setGeometry(QtCore.QRect(10, 20, 401, 161))
        self.gridLayoutWidget.setObjectName("gridLayoutWidget")
        self.gridLayout = QtWidgets.QGridLayout(self.gridLayoutWidget)
        self.gridLayout.setContentsMargins(0, 0, 0, 0)
        self.gridLayout.setObjectName("gridLayout")
        self.checkBox_2 = QtWidgets.QCheckBox(self.gridLayoutWidget)
        self.checkBox_2.setObjectName("checkBox_2")
        self.gridLayout.addWidget(self.checkBox_2, 2, 0, 1, 1)
        self.checkBox = QtWidgets.QCheckBox(self.gridLayoutWidget)
        self.checkBox.setEnabled(True)
        self.checkBox.setCheckable(True)
        self.checkBox.setObjectName("checkBox")
        self.gridLayout.addWidget(self.checkBox, 0, 0, 1, 1)
        self.checkBox_1 = QtWidgets.QCheckBox(self.gridLayoutWidget)
        self.checkBox_1.setEnabled(True)
        self.checkBox_1.setObjectName("checkBox_1")
        self.gridLayout.addWidget(self.checkBox_1, 1, 0, 1, 1)
        self.checkBox_5 = QtWidgets.QCheckBox(self.gridLayoutWidget)
        self.checkBox_5.setObjectName("checkBox_5")
        self.gridLayout.addWidget(self.checkBox_5, 5, 0, 1, 1)
        self.checkBox_4 = QtWidgets.QCheckBox(self.gridLayoutWidget)
        self.checkBox_4.setObjectName("checkBox_4")
        self.gridLayout.addWidget(self.checkBox_4, 4, 0, 1, 1)
        self.checkBox_3 = QtWidgets.QCheckBox(self.gridLayoutWidget)
        self.checkBox_3.setObjectName("checkBox_3")
        self.gridLayout.addWidget(self.checkBox_3, 3, 0, 1, 1)
        self.checkBox_7 = QtWidgets.QCheckBox(self.gridLayoutWidget)
        self.checkBox_7.setObjectName("checkBox_7")
        self.gridLayout.addWidget(self.checkBox_7, 6, 0, 1, 1)
        self.checkBox_12 = QtWidgets.QCheckBox(self.gridLayoutWidget)
        self.checkBox_12.setObjectName("checkBox_12")
        self.gridLayout.addWidget(self.checkBox_12, 4, 1, 1, 1)
        self.checkBox_6 = QtWidgets.QCheckBox(self.gridLayoutWidget)
        self.checkBox_6.setObjectName("checkBox_6")
        self.gridLayout.addWidget(self.checkBox_6, 2, 1, 1, 1)
        self.checkBox_11 = QtWidgets.QCheckBox(self.gridLayoutWidget)
        self.checkBox_11.setObjectName("checkBox_11")
        self.gridLayout.addWidget(self.checkBox_11, 3, 1, 1, 1)
        self.checkBox_9 = QtWidgets.QCheckBox(self.gridLayoutWidget)
        self.checkBox_9.setObjectName("checkBox_9")
        self.gridLayout.addWidget(self.checkBox_9, 1, 1, 1, 1)
        self.checkBox_8 = QtWidgets.QCheckBox(self.gridLayoutWidget)
        self.checkBox_8.setObjectName("checkBox_8")
        self.gridLayout.addWidget(self.checkBox_8, 0, 1, 1, 1)
        self.checkBox_10 = QtWidgets.QCheckBox(self.gridLayoutWidget)
        self.checkBox_10.setObjectName("checkBox_10")
        self.gridLayout.addWidget(self.checkBox_10, 5, 1, 1, 1)
        self.checkBox_13 = QtWidgets.QCheckBox(self.gridLayoutWidget)
        self.checkBox_13.setObjectName("checkBox_13")
        self.gridLayout.addWidget(self.checkBox_13, 6, 1, 1, 1)
        self.groupBox_2 = QtWidgets.QGroupBox(self.groupBox)
        self.groupBox_2.setGeometry(QtCore.QRect(10, 10, 421, 31))
        self.groupBox_2.setTitle("")
        self.groupBox_2.setObjectName("groupBox_2")
        self.tweets = QtWidgets.QRadioButton(self.groupBox_2)
        self.tweets.setGeometry(QtCore.QRect(10, 7, 109, 16))
        self.tweets.setObjectName("tweets")
        self.line = QtWidgets.QFrame(self.network_configuration)
        self.line.setGeometry(QtCore.QRect(450, 20, 20, 261))
        self.line.setFrameShape(QtWidgets.QFrame.VLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.project_managment = QtWidgets.QGroupBox(self.centralwidget)
        self.project_managment.setGeometry(QtCore.QRect(10, 10, 931, 141))
        font = QtGui.QFont()
        font.setFamily("Arial")
        font.setPointSize(10)
        font.setBold(True)
        font.setWeight(75)
        self.project_managment.setFont(font)
        self.project_managment.setObjectName("project_managment")
        self.horizontalLayoutWidget_3 = QtWidgets.QWidget(self.project_managment)
        self.horizontalLayoutWidget_3.setGeometry(QtCore.QRect(30, 30, 871, 31))
        self.horizontalLayoutWidget_3.setObjectName("horizontalLayoutWidget_3")
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget_3)
        self.horizontalLayout.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout.setObjectName("horizontalLayout")
        self.label_7 = QtWidgets.QLabel(self.horizontalLayoutWidget_3)
        self.label_7.setObjectName("label_7")
        self.horizontalLayout.addWidget(self.label_7)
        self.name = QtWidgets.QLineEdit(self.horizontalLayoutWidget_3)
        self.name.setObjectName("name")
        self.horizontalLayout.addWidget(self.name)
        self.label_6 = QtWidgets.QLabel(self.horizontalLayoutWidget_3)
        self.label_6.setObjectName("label_6")
        self.horizontalLayout.addWidget(self.label_6)
        self.path = QtWidgets.QLineEdit(self.horizontalLayoutWidget_3)
        self.path.setObjectName("path")
        self.horizontalLayout.addWidget(self.path)
        self.horizontalLayoutWidget_4 = QtWidgets.QWidget(self.project_managment)
        self.horizontalLayoutWidget_4.setGeometry(QtCore.QRect(30, 70, 871, 31))
        self.horizontalLayoutWidget_4.setObjectName("horizontalLayoutWidget_4")
        self.horizontalLayout_2 = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget_4)
        self.horizontalLayout_2.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_2.setObjectName("horizontalLayout_2")
        self.label_8 = QtWidgets.QLabel(self.horizontalLayoutWidget_4)
        self.label_8.setObjectName("label_8")
        self.horizontalLayout_2.addWidget(self.label_8)
        self.description = QtWidgets.QLineEdit(self.horizontalLayoutWidget_4)
        self.description.setObjectName("description")
        self.horizontalLayout_2.addWidget(self.description)
        self.save_project = QtWidgets.QPushButton(self.project_managment)
        self.save_project.setGeometry(QtCore.QRect(730, 110, 81, 21))
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setBold(False)
        font.setWeight(50)
        self.save_project.setFont(font)
        self.save_project.setObjectName("save_project")
        self.import_project = QtWidgets.QPushButton(self.project_managment)
        self.import_project.setGeometry(QtCore.QRect(630, 110, 91, 21))
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setBold(False)
        font.setWeight(50)
        self.import_project.setFont(font)
        self.import_project.setObjectName("import_project")
        self.new_project = QtWidgets.QPushButton(self.project_managment)
        self.new_project.setGeometry(QtCore.QRect(820, 110, 81, 21))
        font = QtGui.QFont()
        font.setPointSize(8)
        font.setBold(False)
        font.setWeight(50)
        self.new_project.setFont(font)
        self.new_project.setObjectName("new_project")
        self.listView = QtWidgets.QListView(self.centralwidget)
        self.listView.setGeometry(QtCore.QRect(0, -40, 1231, 951))
        self.listView.setObjectName("listView")
        self.groupBox_4 = QtWidgets.QGroupBox(self.centralwidget)
        self.groupBox_4.setGeometry(QtCore.QRect(10, 710, 451, 131))
        self.groupBox_4.setObjectName("groupBox_4")
        self.horizontalLayoutWidget_5 = QtWidgets.QWidget(self.groupBox_4)
        self.horizontalLayoutWidget_5.setGeometry(QtCore.QRect(50, 90, 371, 24))
        self.horizontalLayoutWidget_5.setObjectName("horizontalLayoutWidget_5")
        self.horizontalLayout_3 = QtWidgets.QHBoxLayout(self.horizontalLayoutWidget_5)
        self.horizontalLayout_3.setContentsMargins(0, 0, 0, 0)
        self.horizontalLayout_3.setObjectName("horizontalLayout_3")
        self.startDate_show = QtWidgets.QLineEdit(self.horizontalLayoutWidget_5)
        self.startDate_show.setEnabled(False)
        self.startDate_show.setAlignment(QtCore.Qt.AlignCenter)
        self.startDate_show.setObjectName("startDate_show")
        self.horizontalLayout_3.addWidget(self.startDate_show)
        self.endDate_show = QtWidgets.QLineEdit(self.horizontalLayoutWidget_5)
        self.endDate_show.setEnabled(False)
        self.endDate_show.setAlignment(QtCore.Qt.AlignCenter)
        self.endDate_show.setObjectName("endDate_show")
        self.horizontalLayout_3.addWidget(self.endDate_show)
        self.label_9 = QtWidgets.QLabel(self.groupBox_4)
        self.label_9.setGeometry(QtCore.QRect(110, 20, 61, 16))
        self.label_9.setObjectName("label_9")
        self.label_10 = QtWidgets.QLabel(self.groupBox_4)
        self.label_10.setGeometry(QtCore.QRect(260, 20, 31, 16))
        self.label_10.setObjectName("label_10")
        self.dateEdit_end = QtWidgets.QDateEdit(self.groupBox_4)
        self.dateEdit_end.setGeometry(QtCore.QRect(110, 40, 110, 22))
        self.dateEdit_end.setCalendarPopup(True)
        self.dateEdit_end.setObjectName("dateEdit_end")
        self.label_11 = QtWidgets.QLabel(self.groupBox_4)
        self.label_11.setGeometry(QtCore.QRect(240, 40, 21, 16))
        self.label_11.setObjectName("label_11")
        self.spinBox = QtWidgets.QSpinBox(self.groupBox_4)
        self.spinBox.setGeometry(QtCore.QRect(260, 40, 81, 22))
        self.spinBox.setProperty("showGroupSeparator", False)
        self.spinBox.setObjectName("spinBox")
        self.listView.raise_()
        self.project_managment.raise_()
        self.execution.raise_()
        self.network_configuration.raise_()
        self.acces_configuration.raise_()
        self.list_id.raise_()
        self.network.raise_()
        self.type_relations.raise_()
        self.type_weight.raise_()
        self.groupBox_4.raise_()
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 949, 21))
        self.menubar.setObjectName("menubar")
        self.menuFile = QtWidgets.QMenu(self.menubar)
        self.menuFile.setObjectName("menuFile")
        self.menuEdit = QtWidgets.QMenu(self.menubar)
        self.menuEdit.setObjectName("menuEdit")
        self.menuView = QtWidgets.QMenu(self.menubar)
        self.menuView.setObjectName("menuView")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.actionOpen_credentials = QtWidgets.QAction(MainWindow)
        self.actionOpen_credentials.setObjectName("actionOpen_credentials")
        self.actionSave_credentials = QtWidgets.QAction(MainWindow)
        self.actionSave_credentials.setObjectName("actionSave_credentials")
        self.actionImport_Credentials = QtWidgets.QAction(MainWindow)
        self.actionImport_Credentials.setObjectName("actionImport_Credentials")
        self.actionSave_credentials_2 = QtWidgets.QAction(MainWindow)
        self.actionSave_credentials_2.setObjectName("actionSave_credentials_2")
        self.actionClose_Project = QtWidgets.QAction(MainWindow)
        self.actionClose_Project.setObjectName("actionClose_Project")
        self.menuFile.addAction(self.actionOpen_credentials)
        self.menuFile.addAction(self.actionSave_credentials)
        self.menuFile.addAction(self.actionImport_Credentials)
        self.menuFile.addAction(self.actionSave_credentials_2)
        self.menuFile.addAction(self.actionClose_Project)
        self.menubar.addAction(self.menuFile.menuAction())
        self.menubar.addAction(self.menuEdit.menuAction())
        self.menubar.addAction(self.menuView.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    # Used to print the UI components
    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.list_id.setTitle(_translate("MainWindow", "Twitter List ID"))
        self.network.setTitle(_translate("MainWindow", "Network"))
        self.followers.setText(_translate("MainWindow", "Followers"))
        self.mentions.setText(_translate("MainWindow", "Mentions"))
        self.type_relations.setTitle(_translate("MainWindow", "Type of network"))
        self.simple.setText(_translate("MainWindow", "No Weighted"))
        self.weigthed.setText(_translate("MainWindow", "Weighted"))
        self.type_weight.setTitle(_translate("MainWindow", "Type of weight"))
        self.weight_mentions.setText(_translate("MainWindow", "Mentions"))
        self.weight_retweets.setText(_translate("MainWindow", "Retweets"))
        self.weight_replies.setText(_translate("MainWindow", "Replies"))
        self.acces_configuration.setTitle(_translate("MainWindow", "Access configuration"))
        self.groupBox_3.setTitle(_translate("MainWindow", "Tokens"))
        self.label_3.setText(_translate("MainWindow", "Access Token:"))
        self.label_5.setText(_translate("MainWindow", "Bearer Token:"))
        self.label_4.setText(_translate("MainWindow", "Access Secret Token:"))
        self.label.setText(_translate("MainWindow", "Consumer Key:"))
        self.label_2.setText(_translate("MainWindow", "Consumer Secret Key:"))
        self.new_credentials.setText(_translate("MainWindow", "New"))
        self.type_access.setTitle(_translate("MainWindow", "Type Access"))
        self.standard.setText(_translate("MainWindow", "Standard"))
        self.academic.setText(_translate("MainWindow", "Academic"))
        self.premium.setText(_translate("MainWindow", "Premium"))
        self.type_oauth.setTitle(_translate("MainWindow", "Type OAuth"))
        self.oauth1.setText(_translate("MainWindow", "OAuth1"))
        self.oauth2.setText(_translate("MainWindow", "OAuth2"))
        self.save_credentials.setText(_translate("MainWindow", "Save"))
        self.import_credentials.setText(_translate("MainWindow", "Import"))
        self.execution.setTitle(_translate("MainWindow", "Execution"))
        self.extract.setText(_translate("MainWindow", "Extract"))
        self.network_configuration.setTitle(_translate("MainWindow", "Network configuration"))
        self.tweet_information.setTitle(_translate("MainWindow", "Tweet information"))
        self.checkBox_2.setText(_translate("MainWindow", "Favorites"))
        self.checkBox.setText(_translate("MainWindow", "Author"))
        self.checkBox_1.setText(_translate("MainWindow", "Date"))
        self.checkBox_5.setText(_translate("MainWindow", "Users mentioned"))
        self.checkBox_4.setText(_translate("MainWindow", "Number of mentions"))
        self.checkBox_3.setText(_translate("MainWindow", "Retweets"))
        self.checkBox_7.setText(_translate("MainWindow", "Text"))
        self.checkBox_12.setText(_translate("MainWindow", "Tweet url"))
        self.checkBox_6.setText(_translate("MainWindow", "Location"))
        self.checkBox_11.setText(_translate("MainWindow", "Urls"))
        self.checkBox_9.setText(_translate("MainWindow", "Hashtags"))
        self.checkBox_8.setText(_translate("MainWindow", "Sensitive"))
        self.checkBox_10.setText(_translate("MainWindow", "User description"))
        self.checkBox_13.setText(_translate("MainWindow", "User followers/followees"))
        self.tweets.setText(_translate("MainWindow", "Tweets"))
        self.project_managment.setTitle(_translate("MainWindow", "Project Managment"))
        self.label_7.setText(_translate("MainWindow", "Name:"))
        self.label_6.setText(_translate("MainWindow", "Path:"))
        self.label_8.setText(_translate("MainWindow", "Description:"))
        self.save_project.setText(_translate("MainWindow", "Save"))
        self.import_project.setText(_translate("MainWindow", "Import"))
        self.new_project.setText(_translate("MainWindow", "New"))
        self.groupBox_4.setTitle(_translate("MainWindow", "Date especification"))
        self.label_9.setText(_translate("MainWindow", "End Date"))
        self.label_10.setText(_translate("MainWindow", "Days"))
        self.label_11.setText(_translate("MainWindow", "-"))
        self.menuFile.setTitle(_translate("MainWindow", "File"))
        self.menuEdit.setTitle(_translate("MainWindow", "Edit"))
        self.menuView.setTitle(_translate("MainWindow", "View"))
        self.actionOpen_credentials.setText(_translate("MainWindow", "New Project"))
        self.actionSave_credentials.setText(_translate("MainWindow", "Open Poject"))
        self.actionImport_Credentials.setText(_translate("MainWindow", "Import Credentials"))
        self.actionSave_credentials_2.setText(_translate("MainWindow", "Save credentials"))
        self.actionClose_Project.setText(_translate("MainWindow", "Close Project"))

    # Visual and Logical configurations of the Main Window.
    def Config(self):

        self.path.setEnabled(False)

        self.extract.clicked.connect(lambda: self.extract_data())
        self.dateEdit_end.setDate(datetime.now())
        self.dateEdit_end.dateChanged.connect(lambda: self.dateshow())
        self.spinBox.valueChanged.connect(lambda: self.dateshow())
        self.spinBox.setValue(7)
        self.spinBox.setMaximum(1820)
        self.spinBox.setMinimum(1)

        self.setWindowTitle('Extraction Configuration')
        self.setWindowIcon(QIcon('network.png'))

        self.type_access.setEnabled(False)
        self.type_oauth.setEnabled(False)

        self.new_project.clicked.connect(lambda: self.new_proj())
        self.import_project.clicked.connect(lambda: self.import_created_proj())
        self.save_project.clicked.connect(lambda: self.save_edited_proj())

        self.new_credentials.clicked.connect(lambda: self.new_cred())
        self.import_credentials.clicked.connect(lambda: self.import_cred())
        self.save_credentials.clicked.connect(lambda: self.save_edited_cred())

        self.followers.clicked.connect(lambda: self.enable_followers())
        self.mentions.clicked.connect(lambda: self.enable_mentions())
        self.tweets.clicked.connect(lambda: self.enable_tweets())

        self.followers.setAutoExclusive(False)
        self.followers.setChecked(True)
        self.mentions.setAutoExclusive(False)
        self.type_weight.setEnabled(False)
        self.tweet_information.setEnabled(False)

        self.simple.clicked.connect(lambda: self.type_weight.setEnabled(False))
        self.weigthed.clicked.connect(lambda: self.check_weigth())

        self.extract.setStyleSheet("background-color : rgb(1, 130, 153); color : white; style : outset; border-radius : 6px")
        self.import_project.setStyleSheet("background-color : rgb(1, 130, 153); color : white; style : outset; border-radius : 6px")
        self.save_project.setStyleSheet("background-color : rgb(1, 130, 153); color : white; style : outset; border-radius : 6px")
        self.new_project.setStyleSheet("background-color : rgb(1, 130, 153); color : white; style : outset; border-radius : 6px")
        self.import_credentials.setStyleSheet("background-color : rgb(1, 130, 153); color : white; style : outset; border-radius : 6px")
        self.save_credentials.setStyleSheet("background-color : rgb(1, 130, 153); color : white; style : outset; border-radius : 6px")
        self.new_credentials.setStyleSheet("background-color : rgb(1, 130, 153); color : white; style : outset; border-radius : 6px")

        self.communicate_proj = Communicate()
        self.communicate = Communicate()
        self.communicate_cred = Communicate()

        self.communicate_proj.sig[int].connect(self.import_new_proj)
        self.communicate.sig[int].connect(self.updateProgress)
        self.communicate_cred.sig[int].connect(self.import_new_cred)

    # Allow weighted checkbox if followers network is checked.
    def check_weigth(self):
        if(self.followers.isChecked()):
            self.type_weight.setEnabled(True)

    # Calculate and show the extraction interval date.
    def dateshow(self):
        end_date = self.dateEdit_end.dateTime().toPyDateTime().astimezone().isoformat()
        start_date = (self.dateEdit_end.dateTime().toPyDateTime().astimezone() - timedelta(days=self.spinBox.value())).isoformat()
        self.startDate_show.setText(end_date[:10])
        self.endDate_show.setText(start_date[:10])

    # Configurations if followers network is checked.
    def enable_followers(self):
        self.type_relations.setEnabled(True)
        self.weigthed.setEnabled(True)
        self.type_weight.setEnabled(False)
        self.simple.setChecked(True)
        self.tweets.setChecked(False)
        self.mentions.setChecked(False)
        self.tweet_information.setEnabled(False)

    # Configurations if mentions network is checked.
    def enable_mentions(self):
        self.type_relations.setEnabled(True)
        self.weigthed.setEnabled(True)
        self.type_weight.setEnabled(False)
        self.simple.setChecked(True)
        self.tweets.setChecked(False)
        self.followers.setChecked(False)
        self.tweet_information.setEnabled(False)

    # Configurations if tweets extraction is checked.
    def enable_tweets(self):
        self.type_relations.setEnabled(False)
        self.followers.setChecked(False)
        self.simple.setChecked(True)
        self.type_weight.setEnabled(False)
        self.mentions.setChecked(False)
        self.tweet_information.setEnabled(True)

    # Detect authentication type of a imported project.
    def detect_aouth(self, filename, message = True):
        with open(filename, 'r') as fp:
            data = json.load(fp)
            if (data["Type"] == "oauth1"):
                self.consumer_key.setText(data["consumer_key"])
                self.consumer_secret_key.setText(data["consumer_secret_key"])
                self.access_token.setText(data["access_token"])
                self.aceess_secret_token.setText(data["aceess_secret_token"])
                self.oauth = OAuth1(data["name"], filename, self.consumer_key.text(), self.consumer_secret_key.text(),self.access_token.text(), self.aceess_secret_token.text(), self.communicate)
                self.bearer_token.clear()
                self.disable_oauth2()
            elif (data["Type"] == "oauth2"):
                self.bearer_token.setText(data["bearer_token"])
                self.oauth = OAuth2(data["name"], filename, self.bearer_token.text())
                self.consumer_key.clear()
                self.consumer_secret_key.clear()
                self.access_token.clear()
                self.aceess_secret_token.clear()
                self.disable_oauth1()

        if(message):
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Information)
            msg.setText("Imported")
            msg.setInformativeText('Imported successfully')
            msg.setWindowTitle("successfully")
            msg.exec_()

    # Configurations if authentication type is oauth1.
    def disable_oauth2(self):
        self.standard.setChecked(True)
        self.oauth1.setChecked(True)
        self.spinBox.setEnabled(False)
        self.bearer_token.setEnabled(False)
        self.consumer_key.setEnabled(True)
        self.consumer_secret_key.setEnabled(True)
        self.access_token.setEnabled(True)
        self.aceess_secret_token.setEnabled(True)

    # Configurations if authentication type is oauth2.
    def disable_oauth1(self):
        self.academic.setChecked(True)
        self.oauth2.setChecked(True)
        self.spinBox.setEnabled(True)
        self.consumer_key.setEnabled(False)
        self.consumer_secret_key.setEnabled(False)
        self.access_token.setEnabled(False)
        self.aceess_secret_token.setEnabled(False)
        self.bearer_token.setEnabled(True)

    # Configurations if the network extraction is not checked.
    def disable_network(self):
        self.followers.setChecked(False)
        self.mentions.setChecked(False)
        self.type_weight.setEnabled(False)
        self.type_relations.setEnabled(False)
        self.tweet_information.setEnabled(True)

    # Configurations if the tweets extraction is not checked.
    def disable_tweets(self):
        self.tweets.setChecked(False)
        self.type_relations.setEnabled(True)
        self.tweet_information.setEnabled(False)

    # Take the current Project JSON file information and set the last status of them.
    def set_data(self,data):
        if(("name" in data) and ("description" in data) and ("path" in data)):
            self.name.setText(data["name"])
            self.description.setText(data["description"])
            self.path.setText(data["path"])
        if("bearer_token" in data and not self.consumer_key.text() and not self.bearer_token.text()):
            if(data['bearer_token'] != ""):
                self.bearer_token.setText(data['bearer_token'])
                self.oauth = OAuth2(data["credentials_name"], data["credentials_path"], self.bearer_token.text())
                self.disable_oauth1()
                if(data["type_access"] == "premium"):
                    self.premium.setChecked(True)
                elif(data["type_access"] == "academic"):
                    self.academic.setChecked(True)
            elif(data['consumer_key'] != ""):
                self.consumer_key.setText(data['consumer_key'])
                self.consumer_secret_key.setText(data['consumer_secret_key'])
                self.access_token.setText(data['access_token'])
                self.aceess_secret_token.setText(data['aceess_secret_token'])
                self.oauth = OAuth1(data["credentials_name"], data["credentials_path"], self.consumer_key.text(), self.consumer_secret_key.text(),self.access_token.text(), self.aceess_secret_token.text(), self.communicate)
                self.disable_oauth2()

        if("network" in data):
            if(data['network'] == "followers"):
                self.followers.setChecked(True)

                if (data["type_network"] == "simple"):
                    self.simple.setChecked(True)
                    self.type_weight.setEnabled(False)
                else:
                    self.weigthed.setChecked(True)
                    self.type_weight.setEnabled(True)
                    for atributo in data["attributes"]:
                        if (atributo == "mentions"):
                            self.weight_mentions.setChecked(True)
                        if (atributo == "replies"):
                            self.weight_replies.setChecked(True)
                        if (atributo == "retweets"):
                            self.weight_retweets.setChecked(True)

            elif(data["network"] == "mentions"):
                self.followers.setChecked(False)
                self.mentions.setChecked(True)
                if (data["type_network"] == "simple"):
                    self.simple.setChecked(True)
                    self.type_weight.setEnabled(False)
                else:
                    self.weigthed.setChecked(True)
                    self.type_weight.setEnabled(False)
            elif(data["network"] == "tweets"):
                self.followers.setChecked(False)
                self.mentions.setChecked(False)
                self.type_relations.setEnabled(False)
                self.type_weight.setEnabled(False)
                self.tweets.setChecked(True)
                self.tweet_information.setEnabled(True)
                for information in data["tweets_information"]:
                    if (information == "author"):
                        self.checkBox.setChecked(True)

                    if (information == "date"):
                        self.checkBox_1.setChecked(True)

                    if (information == "favorites"):
                        self.checkBox_2.setChecked(True)

                    if (information == "retweets"):
                        self.checkBox_3.setChecked(True)

                    if (information == "number_mentions"):
                        self.checkBox_4.setChecked(True)

                    if (information == "users_mentioned"):
                        self.checkBox_5.setChecked(True)

                    if (information == "location"):
                        self.checkBox_6.setChecked(True)

                    if (information == "text"):
                        self.checkBox_7.setChecked(True)

                    if (information == "sensitive"):
                        self.checkBox_8.setChecked(True)

                    if (information == "hashtag"):
                        self.checkBox_9.setChecked(True)

                    if (information == "urls"):
                        self.checkBox_11.setChecked(True)

                    if (information == "tweet_url"):
                        self.checkBox_12.setChecked(True)

                    if (information == "user_description"):
                        self.checkBox_10.setChecked(True)

                    if (information == "user_followers"):
                        self.checkBox_13.setChecked(True)


            self.edit_list_id.setText(data["list"])
            self.credentials_path = data["credentials_path"]

    # Save in a list all the attributes that the user wants to retrieve for each tweet.
    def tweet_attributes(self):
        lista = []
        if (self.checkBox.isChecked()):
            lista.append("author")

        if (self.checkBox_1.isChecked()):
            lista.append("date")

        if (self.checkBox_10.isChecked()):
            lista.append("user_description")

        if (self.checkBox_13.isChecked()):
            lista.append("user_followers")
            lista.append("user_followees")

        if (self.checkBox_2.isChecked()):
            lista.append("favorites")

        if (self.checkBox_3.isChecked()):
            lista.append("retweets")

        if (self.checkBox_4.isChecked()):
            lista.append("number_mentions")

        if (self.checkBox_5.isChecked()):
            lista.append("users_mentioned")

        if (self.checkBox_6.isChecked()):
            lista.append("location")

        if (self.checkBox_7.isChecked()):
            lista.append("text")

        if (self.checkBox_8.isChecked()):
            lista.append("sensitive")

        if (self.checkBox_9.isChecked()):
            lista.append("hashtag")

        if (self.checkBox_11.isChecked()):
            lista.append("urls")

        if (self.checkBox_12.isChecked()):
            lista.append("tweet_url")

        return lista

    # Show the new project window.
    def new_proj(self):
        self.New_Proj = New_Project(self.communicate_proj)
        self.New_Proj.show()

    # Used to import a new project.
    def import_new_proj(self):
        self.project = self.New_Proj.return_project()
        if (os.path.isfile(self.project.path + "/config.json")):
            with open(self.project.path + "/config.json", 'r') as fp:
                data = json.load(fp)
                self.set_data(data)

    # Show a browser window and allow the user to select an existing Project.
    def import_created_proj(self, fileName = None):
        if(fileName == None):
            fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Single File', QtCore.QDir.rootPath(), '*.json')
            if(len(fileName) != 0):
                with open(fileName, 'r') as fp:
                    data = json.load(fp)
                    self.project = Project(data["name"], data["description"], data["path"])
                    self.set_data(data)

                msg = QtWidgets.QMessageBox()
                msg.setIcon(QtWidgets.QMessageBox.Information)
                msg.setText("Imported")
                msg.setInformativeText('Imported successfully')
                msg.setWindowTitle("successfully")
                msg.exec_()
        else:
            with open(fileName, 'r') as fp:
                data = json.load(fp)
                self.project = Project(data["name"], data["description"], data["path"])
                self.set_data(data)

    # Save the current Project.
    def save_edited_proj(self, message = True):
        if(self.project != None):
            dictionary = {'name': self.name.text(),
                          'description': self.description.text(),
                          'path': self.path.text(),
                          'consumer_key': self.consumer_key.text(),
                          'consumer_secret_key': self.consumer_secret_key.text(),
                          'access_token': self.access_token.text(),
                          'aceess_secret_token': self.aceess_secret_token.text(),
                          'bearer_token': self.bearer_token.text(),
                          'list': self.edit_list_id.text()}

            if(self.oauth != None):
                dictionary['credentials_name'] = self.oauth.name
                dictionary['credentials_path'] = self.oauth.path

            if(self.standard.isChecked()):
                dictionary['type_access'] = "standard"
            elif(self.academic.isChecked()):
                dictionary['type_access'] = "academic"
            elif(self.premium.isChecked()):
                dictionary['type_access'] = "premium"

            if(self.followers.isChecked()):
                dictionary['network'] = "followers"
            elif(self.mentions.isChecked()):
                dictionary['network'] = "mentions"
            elif (self.tweets.isChecked()):
                dictionary['network'] = "tweets"
                lista = self.tweet_attributes()
                dictionary['tweets_information'] = lista


            if(self.simple.isChecked()):
                dictionary['type_network'] = "simple"
            elif(self.weigthed.isChecked()):
                dictionary['type_network'] = "weighted"
                lista = []
                if(self.weight_mentions.isChecked()):
                    lista.append("mentions")
                if(self.weight_replies.isChecked()):
                    lista.append("replies")
                if(self.weight_retweets.isChecked()):
                    lista.append("retweets")

                dictionary['attributes'] = lista


            aux = self.project.path + '/' + 'config.json'
            try:
                with open(aux, 'w') as fp:
                    json.dump(dictionary, fp)

                if(message):
                    msg = QtWidgets.QMessageBox()
                    msg.setIcon(QtWidgets.QMessageBox.Information)
                    msg.setText("Save Correct")
                    msg.setInformativeText('Saved successfully')
                    msg.setWindowTitle("Saved")
                    msg.exec_()
            except:
                print("failed")

    # Show the new credentials window.
    def new_cred(self):
        self.New_Cred = New_Credentials(self.communicate_cred)
        self.New_Cred.show()

    # Used to import a new credentials.
    def import_new_cred(self):
        filename = self.New_Cred.ret_filename()
        self.detect_aouth(filename, False)

    # Show a browser window and allow the user to select an existing credentials.
    def import_cred(self):
        if(self.project != None):
            try:
                fileName, _ = QtWidgets.QFileDialog.getOpenFileName(self, 'Single File', QtCore.QDir.rootPath() , '*.json')
                if(len(fileName) != 0):
                    self.detect_aouth(fileName)
            except:
                pass

    # Save the current credentials.
    def save_edited_cred(self):
        if (self.oauth != None):
            if(self.oauth.id == 1):
                dictionary = {'Type': 'oauth1',
                              'name': self.oauth.name,
                              'path': self.oauth.path,
                              'consumer_key': self.consumer_key.text(),
                              'consumer_secret_key': self.consumer_secret_key.text(),
                              'access_token': self.access_token.text(),
                              'aceess_secret_token': self.aceess_secret_token.text()}

                aux = OAuth1(self.oauth.name, self.oauth.path, self.consumer_key.text(),self.consumer_secret_key.text(), self.access_token.text(), self.aceess_secret_token.text(), self.communicate)

            else:
                dictionary = {'Type': 'oauth2',
                              'name': self.oauth.name,
                              'path': self.oauth.path,
                              'bearer_token': self.bearer_token.text()}

                aux = OAuth2(self.oauth.name, self.oauth.path, self.bearer_token.text())

            try:
                with open(self.oauth.path, 'w') as fp:
                    json.dump(dictionary, fp)

                self.oauth = aux
                msg = QtWidgets.QMessageBox()
                msg.setIcon(QtWidgets.QMessageBox.Information)
                msg.setText("Save Correct")
                msg.setInformativeText('Credentials saved successfully')
                msg.setWindowTitle("Saved")
                msg.exec_()
            except:
                msg = QtWidgets.QMessageBox()
                msg.setIcon(QtWidgets.QMessageBox.Warning)
                msg.setText("Error")
                msg.setInformativeText('Please try again')
                msg.setWindowTitle("Error")
                msg.exec_()

    # Extraction data main function
    def extract_data(self):

        # Check if all the sections are completed and the credentials are correct, in other case, show an error message.
        if(self.project != None and self.oauth != None and self.edit_list_id.text() and self.oauth.check_credentials()):
            self.feedback = Feedback(self.communicate_proj)
            self.feedback.show() # Show a feedback window.
            list = List(self.edit_list_id.text())
            self.save_edited_proj(False) # Save the las status of the project
            self.extract.clicked.connect(lambda: self.extract.setEnabled(False)) # Disable extract button until the extraction finish.

            if (self.followers.isChecked() and self.simple.isChecked()): # Execute followers no weighted network.
                # Create a new extraction

                if (self.dateEdit_end.date().toPyDate() == date.today()):
                    end_date = (datetime.combine((self.dateEdit_end.date().toPyDate()),
                                                 (time.fromisoformat('23:59:00'))).astimezone() - timedelta(
                        days=1)).isoformat()
                else:
                    end_date = datetime.combine((self.dateEdit_end.date().toPyDate()),
                                                (time.fromisoformat('23:59:00'))).astimezone().isoformat()

                start_date = (datetime.combine((self.dateEdit_end.date().toPyDate()),
                                               (time.fromisoformat('00:00:01'))).astimezone() - timedelta(
                    days=self.spinBox.value())).isoformat()

                extraction = Unweighted("followers",end_date, start_date, list,self.oauth, self.project.path)
                self.project.add_extraction(extraction)

                # Create a new worker thread.
                self.thread = QThread()
                self.worker = Worker(extraction, self.communicate)
                self.worker.moveToThread(self.thread)
                self.thread.started.connect(self.worker.run)
                self.thread.start()
            elif(self.mentions.isChecked() and self.simple.isChecked()): # Execute mentions no weighted network.
                # Create a new extraction

                if (self.dateEdit_end.date().toPyDate() == date.today()):
                    end_date = (datetime.combine((self.dateEdit_end.date().toPyDate()),
                                                 (time.fromisoformat('23:59:00'))).astimezone() - timedelta(
                        days=1)).isoformat()
                else:
                    end_date = datetime.combine((self.dateEdit_end.date().toPyDate()),
                                                (time.fromisoformat('23:59:00'))).astimezone().isoformat()

                start_date = (datetime.combine((self.dateEdit_end.date().toPyDate()),
                                               (time.fromisoformat('00:00:01'))).astimezone() - timedelta(
                    days=self.spinBox.value())).isoformat()

                extraction = Unweighted("mentions",end_date, start_date, list, self.oauth, self.project.path)
                self.project.add_extraction(extraction)

                # Create a new worker thread.
                self.thread = QThread()
                self.worker = Worker(extraction, self.communicate)
                self.worker.moveToThread(self.thread)
                self.thread.started.connect(self.worker.run)
                self.thread.start()
            elif(self.followers.isChecked() and self.weigthed.isChecked()): # Execute followers weighted network.
                # Set type of weight
                type_weight = []
                if(self.weight_mentions.isChecked()):
                    type_weight.append("M")
                if(self.weight_replies.isChecked()):
                    type_weight.append("RP")
                if (self.weight_retweets.isChecked()):
                    type_weight.append("RT")

                # Set the date interval
                if (self.dateEdit_end.date().toPyDate() == date.today()):
                    end_date = (datetime.combine((self.dateEdit_end.date().toPyDate()),
                                                 (time.fromisoformat('23:59:00'))).astimezone() - timedelta(
                        days=1)).isoformat()
                else:
                    end_date = datetime.combine((self.dateEdit_end.date().toPyDate()),
                                                (time.fromisoformat('23:59:00'))).astimezone().isoformat()

                start_date = (datetime.combine((self.dateEdit_end.date().toPyDate()),
                                               (time.fromisoformat('00:00:01'))).astimezone() - timedelta(
                    days=self.spinBox.value())).isoformat()

                # Create a new extraction
                extraction = Weighted("followers_weighted", end_date, start_date, list, self.oauth, self.project.path, type_weight)
                self.project.add_extraction(extraction)

                # Create a new worker thread.
                self.thread = QThread()
                self.worker = Worker(extraction, self.communicate)
                self.worker.moveToThread(self.thread)
                self.thread.started.connect(self.worker.run)
                self.thread.start()
            elif (self.mentions.isChecked() and self.weigthed.isChecked()): # Execute mentions weighted network.
                type_weight = []
                # Set the date interval
                if (self.dateEdit_end.date().toPyDate() == date.today()):
                    end_date = (datetime.combine((self.dateEdit_end.date().toPyDate()),
                                                 (time.fromisoformat('23:59:00'))).astimezone() - timedelta(
                        days=1)).isoformat()
                else:
                    end_date = datetime.combine((self.dateEdit_end.date().toPyDate()),
                                                (time.fromisoformat('23:59:00'))).astimezone().isoformat()

                start_date = (datetime.combine((self.dateEdit_end.date().toPyDate()),
                                               (time.fromisoformat('00:00:01'))).astimezone() - timedelta(
                    days=self.spinBox.value())).isoformat()

                # Create a new extraction
                extraction = Weighted("mentions_weighted", end_date, start_date, list, self.oauth, self.project.path, type_weight)
                self.project.add_extraction(extraction)

                # Create a new worker thread.
                self.thread = QThread()
                self.worker = Worker(extraction, self.communicate)
                self.worker.moveToThread(self.thread)
                self.thread.started.connect(self.worker.run)
                self.thread.start()
            elif (self.tweets.isChecked()): # Execute tweets extraction.
                # Set tweet atributes to retrieve.
                type_attributes = self.tweet_attributes()

                # Set the date interval
                #end_date = self.dateEdit_end.dateTime().toPyDateTime().astimezone().isoformat()
                if(self.dateEdit_end.date().toPyDate() == date.today()):
                    end_date = (datetime.combine((self.dateEdit_end.date().toPyDate()),(time.fromisoformat('23:59:00'))).astimezone() - timedelta(days=1)).isoformat()
                else:
                    end_date = datetime.combine((self.dateEdit_end.date().toPyDate()),(time.fromisoformat('23:59:00'))).astimezone().isoformat()

                start_date = (datetime.combine((self.dateEdit_end.date().toPyDate()),(time.fromisoformat('00:00:01'))).astimezone() - timedelta(days=self.spinBox.value())).isoformat()

                # Create a new extraction
                extraction = Tweets("Tweets", end_date, start_date, list, self.oauth, self.project.path, type_attributes)
                self.project.add_extraction(extraction)

                # Create a new worker thread.
                self.thread = QThread()
                self.worker = Worker(extraction, self.communicate)
                self.worker.moveToThread(self.thread)
                self.thread.started.connect(self.worker.run)
                self.thread.start()
        else:
            # Show an error message
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Warning)
            msg.setText("Error")
            msg.setInformativeText('Please introduce all the values')
            msg.setWindowTitle("Error")
            msg.exec_()