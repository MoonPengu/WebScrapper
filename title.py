# Extract the title of Web page
import requests
from bs4 import BeautifulSoup

page = requests.get(
    input("Enter the url : "))
soup = BeautifulSoup(page.content, 'html.parser')

# Extract title of page
page_title = soup.title.text

# print the result
print(page_title)

