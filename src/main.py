from PyQt5 import QtWidgets
import sys
from PyQt5.QtWidgets import QApplication

from ui.mainWindow import Ui_MainWindow

import webbrowser
import csv

from core.Features import getOwnHostIP
from utils.FetchDataUrl import FetchData
from PyQt5.QtCore import QObject, QThread, pyqtSignal

import sys
import platform
import os
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtCore import (QCoreApplication, QPropertyAnimation, QDate, QDateTime,
                          QMetaObject, QObject, QPoint, QRect, QSize, QTime, QUrl, Qt, QEvent)
from PyQt5.QtGui import (QBrush, QColor, QConicalGradient, QCursor, QFont, QFontDatabase,
                         QIcon, QKeySequence, QLinearGradient, QPalette, QPainter, QPixmap, QRadialGradient)
from PyQt5.QtWidgets import *
from PyQt5 import uic
import psutil
from pyqtgraph import PlotWidget
import pyqtgraph as pg
from pathlib import Path
import numpy as np
from collections import deque

from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5 import QtCore, QtWidgets
import sys
from selenium import webdriver

import matplotlib
matplotlib.use('Qt5Agg')

from views.LoadingProgress import LoadingProgress

CHROME_DRIVER_PATH = "./utils/chromedriver.exe"
START_URL = "https://www.google.com"

class MplCanvas(FigureCanvas):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi, edgecolor = "black")
        self.axes = fig.add_subplot(111, facecolor="black")
        # self.axes.set_xticklabels(labels = xlabels, rotation=45)
        self.axes.tick_params(axis="x", labelrotation=45)
        super(MplCanvas, self).__init__(fig)


class MainWindow(QtWidgets.QMainWindow, Ui_MainWindow):
    """Wrapper of Main window"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setupUi(self)

        # Set hostName and IP
        self.__setHostNameIP()

        # Configure Tables
        self.__configureTables()

        # Set current widget
        self.__openHomePage()

        # Connecting signal slots
        self.__connectSignalSlots()

        # Setup Network Analyser
        self.__setupNetworkAnalyser()

        # Setup System Monitoring
        self.__setupSystemMonitoring()

    def __connectSignalSlots(self, ):
        # Connecting clicks
        self.importBtn.clicked.connect(self.__chooseDialog)
        self.developedMsgLbl.mousePressEvent = self.__openGitHubRepo
        self.openLiveNetworkAnalyser.clicked.connect(
            self.__openNetworkAnalyserPage)
        self.openWebScrapper.clicked.connect(self.__openWebScrapperPage)
        self.openLiveSystemMonitoring.clicked.connect(
            self.__openSystemMonitoringPage)
        
        self.homeBtn.clicked.connect(
            self.__openHomePage)

        self.liveNAtn.clicked.connect(
            self.__openNetworkAnalyserPage)

        self.webScrapperBtn.clicked.connect(
            self.__openWebScrapperPage)

        self.liveSMBtn.clicked.connect(
            self.__openSystemMonitoringPage)

    def __enableAll(self,):
        self.homeBtn.setEnabled(True)
        self.liveNAtn.setEnabled(True)
        self.webScrapperBtn.setEnabled(True)
        self.liveSMBtn.setEnabled(True)

    def __openNetworkAnalyserPage(self, ): 
        self.stackedWidget.setCurrentWidget(self.NetworkAnalyserPage)
        self.__enableAll()
        self.liveNAtn.setEnabled(False)
        self.__configureNetworkAnalyser()

    def __openWebScrapperPage(self, ):
        self.stackedWidget.setCurrentWidget(self.WebScrapperPage)
        self.__enableAll()
        self.webScrapperBtn.setEnabled(False)

    def __openSystemMonitoringPage(self, ):
        self.stackedWidget.setCurrentWidget(self.SystemMonitorPage)
        self.__enableAll()
        self.liveSMBtn.setEnabled(False)

    def __openHomePage(self, ):
        self.stackedWidget.setCurrentWidget(self.HomePage)
        self.__enableAll()
        self.homeBtn.setEnabled(False)

    def __setHostNameIP(self, ):
        hostname, IPAddr = getOwnHostIP()

        self.hostNameLbl.setText(hostname)
        self.IPLbl.setText(IPAddr)

    def __openGitHubRepo(self, event):
        webbrowser.open_new('https://github.com/MoonPengu/WebScrapper')


    """
    ### Network Analyser -------- (Start)
    """

    def __setupNetworkAnalyser(self, ):
        self.clickCountCanvas = MplCanvas(self, width=10, height=6, dpi=100)
        self.clickCountGridLayout.addWidget(self.clickCountCanvas, 0, 0, 1, 3)
        # self.clickCountCanvas.setStyleSheet("background-color:black;")

        self.clickRateCanvas = MplCanvas(self, width=10, height=6, dpi=100)
        # self.clickRateCanvas.setStyleSheet("background-color:transparent;")
        self.clickRateGridLayout.addWidget(self.clickRateCanvas, 0, 0, 1, 3)

    def __configureNetworkAnalyser(self, ):
        # naw = NetworkAnalyserWindow(self)
        # naw.show()

        # self.clickCountCanvas = MplCanvas(self, width=5, height=4, dpi=100)
        # # self.gridLayout = QGridLayout()

        # self.clickCountGridLayout.addWidget(self.clickCountCanvas, 0, 0, 1, 3)

        # layout = QtWidgets.QVBoxLayout()
        # layout.addWidget(self.gridLayout)
        # self.setLayout(c)

        # self.setCentralWidget(self.gridLayout)
        
        self.driver = webdriver.Chrome(executable_path=CHROME_DRIVER_PATH)
        self.driver.get(START_URL)

        print("Start URL : ")
        print(self.driver.current_url)
        print()

        self.oldUrl = self.driver.current_url
        
        self.urlLog = {
            self.oldUrl: {
                "index": 0,
                "click": 1
            }
        }

        self.lastIndex = 0
        self.maxClicks = 1

        print('[+] Starting Log Analyser!')
        print()

        self.xdata = [self.oldUrl]
        self.ydata = [1]

        self.clickCountCanvas.axes.set_xlim([0, 0])
        self.clickCountCanvas.axes.set_ylim([0, 2])

        # We need to store a reference to the plotted line
        # somewhere, so we can apply the new data to it.
        plot_refs = self.clickCountCanvas.axes.plot(self.xdata, self.ydata, 'r')
        self._plot_ref = plot_refs[0]

        # self.update_plot()

        self.show()

        # Setup a timer to trigger the redraw by calling update_plot.
        self.timer = QtCore.QTimer()
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.updateClickCountPlot)
        self.timer.start()

    def updateClickCountPlot(self):
        self.currUrl = self.driver.current_url

        if self.currUrl and self.currUrl != self.oldUrl:
            print("Change detected : ")
            print(self.oldUrl + " ----> " + self.currUrl)
            print()

            if self.currUrl not in self.urlLog:
                self.urlLog[self.currUrl] = {
                    "index": self.lastIndex,
                    "click":1
                }

                # Increase x-range
                self.lastIndex += 1
                self.clickCountCanvas.axes.set_xlim([0, self.lastIndex])

                # Add new x-value and y-value
                self.xdata += [self.currUrl]
                self.ydata += [1]
            else:
                self.urlLog[self.currUrl]["click"] += 1

                if self.urlLog[self.currUrl]["click"] > self.maxClicks:
                    self.maxClicks = self.urlLog[self.currUrl]["click"]

                    # Increase y-range
                    self.clickCountCanvas.axes.set_ylim([0, self.maxClicks + 1])
                
                # Increase y-value
                self.ydata[self.urlLog[self.currUrl]["index"]] = self.urlLog[self.currUrl]["click"]
                
            self.oldUrl = self.currUrl

            self._plot_ref.set_xdata(self.xdata)
            self._plot_ref.set_ydata(self.ydata)

            # Trigger the canvas to update and redraw.
            self.clickCountCanvas.draw()

        
        # Switch to the active window
        self.driver.switch_to.window(self.driver.window_handles[-1])
    """
    ### Network Analyser -------- (End)
    """

    """
    ### System Monitoring -------- (Start)
    """

    def __setupSystemMonitoring(self, ):
        """Seting up system monitoring"""
        # self.ui = uic.loadUi("main.ui", self)
        self.cpu_percent = 0
        self.ram_percent = 0
        self.traces = dict()
        self.timestamp = 0
        self.timeaxis = []
        self.cpuaxis = []
        self.ramaxis = []
        # self.csv_file = open(datafile, 'w')
        # self.csv_writer = csv.writer(self.csv_file, delimiter=',')
        self.current_timer_graph = None
        self.graph_lim = 15
        self.deque_timestamp = deque([], maxlen=self.graph_lim+20)
        self.deque_cpu = deque([], maxlen=self.graph_lim+20)
        self.deque_ram = deque([], maxlen=self.graph_lim+20)
        self.label.setText(
            f"{platform.system()} {platform.machine()}")
        self.label_8.setText(
            f"Processor: {platform.processor()}")

        self.graphwidget1 = PlotWidget(title="CPU percent")
        x1_axis = self.graphwidget1.getAxis('bottom')
        x1_axis.setLabel(text='Time since start (s)')
        y1_axis = self.graphwidget1.getAxis('left')
        y1_axis.setLabel(text='Percent')

        self.graphwidget2 = PlotWidget(title="RAM percent")
        x2_axis = self.graphwidget2.getAxis('bottom')
        x2_axis.setLabel(text='Time since start (s)')
        y2_axis = self.graphwidget2.getAxis('left')
        y2_axis.setLabel(text='Percent')

        self.pushButton.clicked.connect(self.show_cpu_graph)
        self.pushButton_2.clicked.connect(self.show_ram_graph)
        self.gridLayout.addWidget(self.graphwidget1, 0, 0, 1, 3)
        self.gridLayout.addWidget(self.graphwidget2, 0, 0, 1, 3)

        self.current_timer_systemStat = QtCore.QTimer()
        self.current_timer_systemStat.timeout.connect(
            self.getsystemStatpercent)
        self.current_timer_systemStat.start(1000)
        self.show_cpu_graph()

    def getsystemStatpercent(self):
        # gives a single float value
        self.cpu_percent = psutil.cpu_percent()
        self.ram_percent = psutil.virtual_memory().percent
        self.setValue(self.cpu_percent, self.labelPercentageCPU,
                      self.circularProgressCPU, "rgba(85, 170, 255, 255)")
        self.setValue(self.ram_percent, self.labelPercentageRAM,
                      self.circularProgressRAM, "rgba(255, 0, 127, 255)")

    def start_cpu_graph(self):
        # self.timeaxis = []
        # self.cpuaxis = []
        if self.current_timer_graph:
            self.current_timer_graph.stop()
            self.current_timer_graph.deleteLater()
            self.current_timer_graph = None
        self.current_timer_graph = QtCore.QTimer()
        self.current_timer_graph.timeout.connect(self.update_cpu)
        self.current_timer_graph.start(1000)

    def update_cpu(self):
        self.timestamp += 1

        self.deque_timestamp.append(self.timestamp)
        self.deque_cpu.append(self.cpu_percent)
        self.deque_ram.append(self.ram_percent)
        timeaxis_list = list(self.deque_timestamp)
        cpu_list = list(self.deque_cpu)

        if self.timestamp > self.graph_lim:
            self.graphwidget1.setRange(xRange=[self.timestamp-self.graph_lim+1, self.timestamp], yRange=[
                                       min(cpu_list[-self.graph_lim:]), max(cpu_list[-self.graph_lim:])])
        self.set_plotdata(name="cpu", data_x=timeaxis_list,
                          data_y=cpu_list)

    def start_ram_graph(self):

        if self.current_timer_graph:
            self.current_timer_graph.stop()
            self.current_timer_graph.deleteLater()
            self.current_timer_graph = None
        self.current_timer_graph = QtCore.QTimer()
        self.current_timer_graph.timeout.connect(self.update_ram)
        self.current_timer_graph.start(1000)

    def update_ram(self):
        self.timestamp += 1

        self.deque_timestamp.append(self.timestamp)
        self.deque_cpu.append(self.cpu_percent)
        self.deque_ram.append(self.ram_percent)
        timeaxis_list = list(self.deque_timestamp)
        ram_list = list(self.deque_ram)

        if self.timestamp > self.graph_lim:
            self.graphwidget2.setRange(xRange=[self.timestamp-self.graph_lim+1, self.timestamp], yRange=[
                                       min(ram_list[-self.graph_lim:]), max(ram_list[-self.graph_lim:])])
        self.set_plotdata(name="ram", data_x=timeaxis_list,
                          data_y=ram_list)

    def show_cpu_graph(self):
        self.graphwidget2.hide()
        self.graphwidget1.show()
        self.start_cpu_graph()
        self.pushButton.setEnabled(False)
        self.pushButton_2.setEnabled(True)
        self.pushButton.setStyleSheet(
            """
            font: 75 10pt "MS Shell Dlg 2";
            color: black;
            background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 rgba(103, 212, 236, 255), stop:1 rgba(255, 255, 255, 255))
            """
        )
        self.pushButton_2.setStyleSheet(
            "QPushButton"
            "{"
            "background-color : rgb(255, 44, 174);"
            "}"
            "QPushButton"
            "{"
            "color : white;"
            "}"
        )

    def show_ram_graph(self):
        self.graphwidget1.hide()
        self.graphwidget2.show()
        # self.graphwidget2.autoRange()
        self.start_ram_graph()
        self.pushButton_2.setEnabled(False)
        self.pushButton.setEnabled(True)
        self.pushButton_2.setStyleSheet(
            """
            font: 75 10pt "MS Shell Dlg 2";
            background-color:qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 rgba(195, 146, 255, 255), stop:1 rgba(255, 255, 255, 255));
            color:black;
            """
        )
        self.pushButton.setStyleSheet(
            "QPushButton" "{" "background-color : lightblue;" "}"
        )

    def set_plotdata(self, name, data_x, data_y):
        # print('set_data')
        if name in self.traces:
            self.traces[name].setData(data_x, data_y)
        else:
            if name == "cpu":
                self.traces[name] = self.graphwidget1.getPlotItem().plot(
                    pen=pg.mkPen((85, 170, 255), width=3))

            elif name == "ram":
                self.traces[name] = self.graphwidget2.getPlotItem().plot(
                    pen=pg.mkPen((255, 0, 127), width=3))

    # ==> SET VALUES TO DEF progressBarValue

    def setValue(self, value, labelPercentage, progressBarName, color):

        sliderValue = value

        # HTML TEXT PERCENTAGE
        htmlText = """<p align="center"><span style=" font-size:50pt;">{VALUE}</span><span style=" font-size:40pt; vertical-align:super;">%</span></p>"""
        labelPercentage.setText(htmlText.replace(
            "{VALUE}", f"{sliderValue:.1f}"))

        # CALL DEF progressBarValue
        self.progressBarValue(sliderValue, progressBarName, color)

    # DEF PROGRESS BAR VALUE
    ########################################################################

    def progressBarValue(self, value, widget, color):

        # PROGRESSBAR STYLESHEET BASE
        styleSheet = """
        QFrame{
        	border-radius: 110px;
        	background-color: qconicalgradient(cx:0.5, cy:0.5, angle:90, stop:{STOP_1} rgba(255, 0, 127, 0), stop:{STOP_2} {COLOR});
        }
        """

        # GET PROGRESS BAR VALUE, CONVERT TO FLOAT AND INVERT VALUES
        # stop works of 1.000 to 0.000
        progress = (100 - value) / 100.0

        # GET NEW VALUES
        stop_1 = str(progress - 0.001)
        stop_2 = str(progress)

        # FIX MAX VALUE
        if value == 100:
            stop_1 = "1.000"
            stop_2 = "1.000"

        # SET VALUES TO NEW STYLESHEET
        newStylesheet = styleSheet.replace("{STOP_1}", stop_1).replace(
            "{STOP_2}", stop_2).replace("{COLOR}", color)

        # APPLY STYLESHEET WITH NEW VALUES
        widget.setStyleSheet(newStylesheet)
    
    """
    ### System Monitoring -------- (End)
    """

    """
    ### Web Scrapper -------- (Start)
    """

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
        numberTW.setSectionResizeMode(
            0, QtWidgets.QHeaderView.ResizeToContents)
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

        self.inputItemCount = len(urls[1:])*2  # Multiplied with feature count
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
    
    """
    ### Web Scrapper -------- (End)
    """

if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = MainWindow()
    win.show()
    sys.exit(app.exec_())
