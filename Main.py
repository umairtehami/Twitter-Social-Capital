from Start_Window import *

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Widget = QtWidgets.QStackedWidget()
    MainWindow = MainWindow()
    MainWindow.show()
    sys.exit(app.exec_())