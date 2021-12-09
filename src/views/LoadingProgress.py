from PyQt5 import QtCore, QtWidgets
from ui.loadingProgress import Ui_DisplayLoadingProgress


class LoadingProgress(QtWidgets.QDialog, Ui_DisplayLoadingProgress):
    def __init__(self, parent, maxLimit):
        super().__init__(parent)
        self.setupUi(self)

        self.maxLimit = maxLimit
        self.oneThird = (self.maxLimit * 1) // 3
        self.twoThird = (self.maxLimit * 2) // 3
        self.initUI()


    def initUI(self):
        self.setWindowTitle("Loading")
        self.setWindowFlags(self.windowFlags() | QtCore.Qt.Dialog |
                            QtCore.Qt.SplashScreen | QtCore.Qt.WindowStaysOnTopHint)

        self.loadingProgressBar.setMaximum(self.maxLimit)


    def updateProgressBar(self, value):
        currProgress = (value*100)//self.maxLimit
        self.loadingProgressText.setText(str(currProgress) + "%")
        self.loadingProgressBar.setValue(value)
        
        if value >= self.twoThird:
            self.changeColor('green')
        elif value >= self.oneThird:
            self.changeColor('blue')


    def changeColor(self, color):
        css = """
            ::chunk {{
                background: {0};
            }}
        """.format(color)
        self.loadingProgressBar.setStyleSheet(css)


    def updateCurrentUrl(self, url):
        self.loadingText.setText("Scanning "+ url)


    # def updateProgressBarSize(self, size):
    #     self.maxLimit = size
    #     self.oneThird = (self.maxLimit * 1) // 3
    #     self.twoThird = (self.maxLimit * 2) // 3

    #     self.loadingProgressBar.setMaximum(self.maxLimit)