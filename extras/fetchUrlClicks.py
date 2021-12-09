from selenium import webdriver
import selenium
import time
driver = webdriver.Chrome(executable_path="chromedriver.exe")
urlA = "https://www.hybrique.com"
driver.get(urlA)
# time.sleep(10)
# print("Page Title of urlA : " + driver.title)
print("Start URL : ")
print(driver.current_url)
print()
oldUrl = driver.current_url

urlLog = {
    oldUrl: {
        "click":1
    }
}

print('[+] Starting Log Analyser!')
print()

def printLogs():
    print('[-] Closing Log Analyser!')
    print('Printing Results ---')
    print()

    for url, value in urlLog.items():
        print()
        print("URL : " + url)
        clickCount = value["click"]
        print("Click : " + str(clickCount))
        print()

try:
    while(True):
        try:
            time.sleep(0.2)

            currUrl = driver.current_url
            if currUrl and currUrl != oldUrl:
                print("Change detected : ")
                print(oldUrl + " ----> " + currUrl)
                print()
                if currUrl not in urlLog:
                    urlLog[currUrl] = {
                        "click":1
                    }
                else:
                    urlLog[currUrl]["click"] = urlLog[currUrl]["click"] + 1

                oldUrl = currUrl
            
            # Switch to the active window
            driver.switch_to.window(driver.window_handles[-1])
            
            # get current window handle
            # p = driver.current_window_handle
            # print(p)

            # # get first child window
            # chwd = driver.window_handles

            # for w in chwd:
            #     # switch focus to child window
            #     if w != p:
            #         driver.switch_to.window(w)
        except:
            break
    printLogs()

except KeyboardInterrupt:
    printLogs()