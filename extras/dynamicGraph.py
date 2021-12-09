from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5 import QtCore, QtWidgets
import sys
from selenium import webdriver

import matplotlib
matplotlib.use('Qt5Agg')


class MplCanvas(FigureCanvas):

    def __init__(self, parent=None, width=5, height=4, dpi=100):
        fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = fig.add_subplot(111)
        super(MplCanvas, self).__init__(fig)


class MainWindow(QtWidgets.QMainWindow):

    def __init__(self, *args, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)

        self.clickCountCanvas = MplCanvas(self, width=5, height=4, dpi=100)

        # layout = QtWidgets.QVBoxLayout()
        # layout.addWidget(self.clickCountCanvas)
        # self.setLayout(layout)

        self.setCentralWidget(self.clickCountCanvas)
        
        self.driver = webdriver.Chrome(executable_path="chromedriver.exe")
        urlA = "https://www.google.com"
        self.driver.get(urlA)
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

        self.xdata = [0]
        self.ydata = [1]

        self.clickCountCanvas.axes.set_xlim([0, 0])
        self.clickCountCanvas.axes.set_ylim([0, 1])

        # We need to store a reference to the plotted line
        # somewhere, so we can apply the new data to it.
        plot_refs = self.clickCountCanvas.axes.plot(self.xdata, self.ydata, 'r')
        self._plot_ref = plot_refs[0]

        # self.update_plot()

        self.show()

        # Setup a timer to trigger the redraw by calling update_plot.
        self.timer = QtCore.QTimer()
        self.timer.setInterval(100)
        self.timer.timeout.connect(self.update_plot)
        self.timer.start()

    def update_plot(self):
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
                self.xdata += [self.lastIndex]
                self.ydata += [1]
            else:
                self.urlLog[self.currUrl]["click"] += 1

                if self.urlLog[self.currUrl]["click"] > self.maxClicks:
                    self.maxClicks = self.urlLog[self.currUrl]["click"]

                    # Increase y-range
                    self.clickCountCanvas.axes.set_ylim([0, self.maxClicks])
                
                # Increase y-value
                self.ydata[self.urlLog[self.currUrl]["index"]] = self.urlLog[self.currUrl]["click"]
                
            self.oldUrl = self.currUrl

            self._plot_ref.set_xdata(self.xdata)
            self._plot_ref.set_ydata(self.ydata)

            # Trigger the canvas to update and redraw.
            self.clickCountCanvas.draw()

        
        # Switch to the active window
        self.driver.switch_to.window(self.driver.window_handles[-1])


app = QtWidgets.QApplication(sys.argv)
w = MainWindow()
app.exec_()
