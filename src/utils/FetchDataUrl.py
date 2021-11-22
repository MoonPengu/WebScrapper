from PyQt5.QtCore import QObject, QThread, pyqtSignal
from core.Features import getIP, getPageTitle, getEmailAndNumber, getAllUrls

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