from bs4 import BeautifulSoup as bs
import pandas as pd
import time
import requests
import random

pd.set_option('display.max_colwidth', 800)

# Fetch response from any website
#https://website.com
page = requests.get(input("Enter the url : "))
print("The response of the web-page is : ", page)

# Parsing the webpage
soup = bs(page.content)
print(soup)

