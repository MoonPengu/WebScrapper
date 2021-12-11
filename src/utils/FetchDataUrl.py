import time

from PyQt5.QtCore import QObject, pyqtSignal
from selenium import webdriver

from core.Features import getIP, getPageTitle, getEmailAndNumber, getAllUrls

CHROME_DRIVER_PATH = "./utils/chromedriver.exe"


class FetchData(QObject):
    """Fetch data from URL"""
    finishedSignal = pyqtSignal(dict)
    urlStartSignal = pyqtSignal(str)
    reportProgress = pyqtSignal(int)
    # updateMaxSize = pyqtSignal(int)
    progress = 0

    def __init__(self, urls):
        super().__init__()
        self.urls = urls

    def __fetchDataFromUrl(self, url):
        # Process for given url

        # Get IP
        ip = getIP(url)
        # self.progress += 1
        # self.reportProgress.emit(self.progress)

        # Get Page Title
        title = getPageTitle(url)
        # self.progress += 1
        # self.reportProgress.emit(self.progress)

        # Get Emails and Numbers
        try:
            emails, numbers = getEmailAndNumber(url)
        except:
            emails = []
            numbers = []

        output = {
            "url": url,
            "title": title,
            "ip": ip,
            "emails": list(emails),
            "numbers": list(numbers)
        }
        # print(output)
        return output

    def startFetching(self, ):
        self.output = {}
        self.reportProgress.emit(self.progress)

        for url in self.urls:
            # Getting all Urls:
            allUrls = getAllUrls(url)

            # print("Maxsize : ", len(allUrls) + 1)
            # self.updateMaxSize.emit(len(allUrls) + 1)

            print("Processing URL : ", url)
            self.urlStartSignal.emit(url)

            self.output[url] = self.__fetchDataFromUrl(url)

            self.progress += 1
            self.reportProgress.emit(self.progress)

            # Later it can be improved by recursively scanning all sub urls
            # Fetching all subUrls
            for u in allUrls:
                if u not in self.output:
                    print("Processing URL : ", u)
                    self.urlStartSignal.emit(u)

                    self.output[u] = self.__fetchDataFromUrl(u)

            self.progress += 1
            self.reportProgress.emit(self.progress)

        self.finishedSignal.emit(self.output)


class NetworkAnalyser(QObject):
    """Network Analyser"""
    updateSignal = pyqtSignal(dict)
    finishedSignal = pyqtSignal(int)

    def __init__(self, startUrl, availableUrls):
        super().__init__()
        self.startUrl = startUrl
        self.availableUrls = availableUrls

    def startWebDriver(self, ):
        print("Starting Network Analyser ---")
        self.driver = webdriver.Chrome(executable_path=CHROME_DRIVER_PATH)
        self.driver.get(self.startUrl)
        self.__observeClicks()

    def __observeClicks(self, ):
        while True:
            time.sleep(0.1)
            try:
                currUrl = self.driver.current_url
                title = ""
                ip = ""
                if currUrl not in self.availableUrls:
                    self.availableUrls.append(currUrl)
                    title = getPageTitle(currUrl)
                    ip = getIP(currUrl)

                data = {
                    "curr-url": currUrl,
                    "title": title,
                    "ip": ip
                }
                self.updateSignal.emit(data)
                self.driver.switch_to.window(self.driver.window_handles[-1])
            except:
                break

        self.finishedSignal.emit(1)
