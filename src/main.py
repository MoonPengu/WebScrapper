from PyQt5 import QtWidgets
import sys
from PyQt5.QtWidgets import QApplication

from ui.mainWindow import Ui_MainWindow

import webbrowser
import csv

from core.Features import getOwnHostIP
from utils.FetchDataUrl import FetchData
from PyQt5.QtCore import QObject, QThread, pyqtSignal

from views.LoadingProgress import LoadingProgress


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    """Wrapper of Main window"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        # Set hostName and IP
        self.__setHostNameIP()

        # Configure Tables
        self.__configureTables()

        # Connecting clicks
        self.importBtn.clicked.connect(self.__chooseDialog)
        self.developedMsgLbl.mousePressEvent = self.__openGitHubRepo

    def __setHostNameIP(self, ):
        hostname, IPAddr = getOwnHostIP()

        self.hostNameLbl.setText(hostname)
        self.IPLbl.setText(IPAddr)

    def __configureTables(self, ):
        # Setting table widths
        topTW = self.TopTW.horizontalHeader()
        topTW.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        topTW.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
        topTW.setSectionResizeMode(2, QtWidgets.QHeaderView.ResizeToContents)

        emailTW = self.EmailTW.horizontalHeader()
        emailTW.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        emailTW.setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)

        numberTW = self.NumberTW.horizontalHeader()
        numberTW.setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
        numberTW.setSectionResizeMode(
            1, QtWidgets.QHeaderView.Stretch)

        # Disable Table Cell Editing
        self.TopTW.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        self.EmailTW.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)
        self.NumberTW.setEditTriggers(QtWidgets.QTableWidget.NoEditTriggers)

        # Clearing all elements
        self.__clearAllTables()

    def __clearAllTables(self, ):
        # Clearing Tables
        self.TopTW.setRowCount(0)
        self.EmailTW.setRowCount(0)
        self.NumberTW.setRowCount(0)

    def __openGitHubRepo(self, event):
        webbrowser.open_new('https://github.com/MoonPengu/WebScrapper')

    def __chooseDialog(self, ):
        path = QtWidgets.QFileDialog.getOpenFileName(self, 'Choose a csv containing list of URLs', '',
                                                     'All Files (*.csv)')
        if path != ('', ''):
            print("File path : " + path[0])
            self.filePath = path[0]
            self.__processItems()
        else:
            print("Please choose a valid folder path!")

    def __processItems(self, ):
        print("Processing Items ...")
        self.data = None

        # initializing the titles and rows list
        # fields = []
        urls = []

        # reading csv file
        with open(self.filePath, 'r') as csvfile:
            # creating a csv reader object
            csvreader = csv.reader(csvfile)

            # extracting field names through first row
            # fields = next(csvreader)

            # extracting each data row one by one
            for row in csvreader:
                for col in row:
                    urls.append(col)

            # get total number of rows
            print("Total no. of base urls: %d" % (csvreader.line_num - 1))

        """
        # Iterating urls one by one and processing it
        self.data = {}
        for url in urls[1:]:
            print("Processing URL : ", url)
            self.data[url] = self.__fetchDataFromUrl(url)
        """

        self.inputItemCount = len(urls[1:])*2 # Multiplied with feature count
        self.worker = FetchData(urls[1:])

        self.thread = QThread()
        self.worker.moveToThread(self.thread)  # move worker to thread

        # end the thread running the worker
        self.worker.finishedSignal.connect(self.thread.quit)
        self.worker.finishedSignal.connect(
            self.__finishFetchData)  # return data to workComplete

        self.worker.finishedSignal.connect(
            self.worker.deleteLater)  # delete the worker
        self.thread.finished.connect(
            self.thread.deleteLater)  # delete the thread
        
        # To register work progress
        self.worker.urlStartSignal.connect(self.__updateCurrentUrl)
        self.worker.reportProgress.connect(self.__updateLoadingProgress)
        # self.worker.updateMaxSize.connect(self.__updateLoadingProgressSize)
        self.__showLoadingProgress()

        # Disable the window
        self.importBtn.setEnabled(False)

        self.thread.finished.connect(
            lambda: self.importBtn.setEnabled(True)
        )

        self.thread.started.connect(self.worker.startFetching)
        self.thread.start()

        """
        self.data = {
            "https://www.hybrique.com": {
                "url": "https://www.hybrique.com",
                "title": "Hybrique | What is Hybrique",
                "ip": "186.85.75.45",
                "emails": [
                    "admin@hybrique.com",
                    "hybrique@gmail.com"
                ],
                "numbers": [
                    "95464212424",
                    "65 2126-1215"
                ]
            },
            "https://www.google.com": {
                "url": "https://www.google.com",
                "title": "Google",
                "ip": "120.53.65.45",
                "emails": [
                    "google@gmail.com",
                ],
                "numbers": [
                    "5246-2642",
                    "+91 9125464342"
                ]
            }
        }
        """

    """
    def __fetchDataFromUrl(self, url):
        # Process for given url
        emails, numbers = getEmailAndNumber(url)
        output = {
            "url": url,
            "title": getPageTitle(url),
            "ip": getIP(url),
            "emails": list(emails),
            "numbers": list(numbers)
        }
        # print(output)
        return output
    """

    def __showLoadingProgress(self):
        """Show Loading Progress UI"""
        self.progressBarWin = LoadingProgress(self, self.inputItemCount)
        self.progressBarWin.show()

    def __closeLoadingProgress(self):
        """Close loading progress UI"""
        self.progressBarWin.close()

    def __updateLoadingProgress(self, progress):
        """Update loading progress UI"""
        if progress <= self.inputItemCount:
            self.progressBarWin.updateProgressBar(progress)

    # def __updateLoadingProgressSize(self, size):
    #     self.progressBarWin.updateProgressBarSize(size)

    def __updateCurrentUrl(self, url):
        """Update Current Url"""
        self.progressBarWin.updateCurrentUrl(url)
        
    def __finishFetchData(self, data):
        self.__closeLoadingProgress()
        self.data = data
        self.__loadTables()


    def __loadTables(self, ):
        print("Loading Table Contents ...")

        self.__clearAllTables()

        if self.data and len(self.data.keys()) > 0:
            for key in self.data.keys():
                item = self.data[key]

                url = item["url"]
                title = item["title"]
                ip = item["ip"]

                # Inserting data to Top Table
                self.__insertRowToTopTable(url, title, ip)

                emails = item["emails"]
                numbers = item["numbers"]

                for email in emails:
                    # Inserting data to Email Table
                    self.__insertRowToEmailsTable(url, email)

                for number in numbers:
                    # Inserting data to Number Table
                    self.__insertRowToNumbersTable(url, number)

    def __insertRowToTopTable(self, url, title, ip):
        rowPosition = self.TopTW.rowCount()
        self.TopTW.insertRow(rowPosition)




        self.TopTW.setItem(
            rowPosition, 0, QtWidgets.QTableWidgetItem(str(url)))
        self.TopTW.setItem(
            rowPosition, 1, QtWidgets.QTableWidgetItem(str(title)))
        self.TopTW.setItem(rowPosition, 2, QtWidgets.QTableWidgetItem(str(ip)))

    def __insertRowToEmailsTable(self, url, email):
        rowPosition = self.EmailTW.rowCount()
        self.EmailTW.insertRow(rowPosition)

        self.EmailTW.setItem(
            rowPosition, 0, QtWidgets.QTableWidgetItem(str(url)))
        self.EmailTW.setItem(
            rowPosition, 1, QtWidgets.QTableWidgetItem(str(email)))

    def __insertRowToNumbersTable(self, url, number):
        rowPosition = self.NumberTW.rowCount()
        self.NumberTW.insertRow(rowPosition)

        self.NumberTW.setItem(
            rowPosition, 0, QtWidgets.QTableWidgetItem(str(url)))
        self.NumberTW.setItem(
            rowPosition, 1, QtWidgets.QTableWidgetItem(str(number)))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
