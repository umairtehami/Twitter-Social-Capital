import PyQt5.QtWidgets as QtWidgets

from Main_Window import *


#This software is created for users who want to extract data from Twitter to calculate their social capital. It only needs a list of profiles and
#the especification of the extraction properties to generate a .csv file which contains the information about the profiles interaction.


#This software is divided in four main sections.

# -> Section 1 (Project Managment): This sections is used to manage the Project properties, it allow us to create a new one,
#import if we already have one and save the changes in the current Project.

# -> Section 2 (Access Configuration): The Access configuration allow us to manage all things related to the authentication credentials for the API,
#like the type of access, type of authentication, import existing credentials, etc.

# -> Section 3 (Network Configuration): In this section we can define the parameters for our extraction. It allow us to define the type of extraction,
#type of network, if we want a weighted network or not, etc. In this section the user needs to provide Twitter list ID for the extraction.

# -> Section 4 (Execution): Here the user can define the date interval for the extraction.

#Main function
if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    Widget = QtWidgets.QStackedWidget()
    MainWindow = MainWindow()
    MainWindow.show()
    sys.exit(app.exec_())