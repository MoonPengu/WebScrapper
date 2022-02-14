from bs4 import BeautifulSoup  # Parses html and xml documents
import requests  # Send requests
import requests.exceptions  # Handle exceptions in case of request timeout
import urllib.parse  # Manages all url stuffs
from collections import deque  # Keeps all url in a list and takes one at a time
import re  # re is regex

# Fetch IP of any website
import socket as s


def getEmailNumberCookie(url):
    """ Returns the list of fetched email and number of the given url"""
    # Transferring the user urls to deque
    urls = deque([url])

    # Variable to store the scrapped urls and a variable to store the emails and numbers
    scrapped_urls = set()
    emails = set()
    numbers = set()
    cookies = []

    count = 0
    while len(urls):
        # Takes one url at a time
        count += 1
        if count == 100:  # Stop here when the urls reach 100
            break

        # Take urls from the left side of deque
        url = urls.popleft()
        scrapped_urls.add(url)

        parts = urllib.parse.urlsplit(url)
        # fetches the network location (for ex ip address)
        base_url = '{0.scheme}://{0.netloc}', format(parts)

        # Take urls one by one and show the user that its processing
        path = url[:url.rfind('/') + 1] if '/' in parts.path else url
        # print('[%d] Processing %s' % (count, url))

        try:
            response = requests.get(url, timeout=30)
        except(requests.exceptions.MissingSchema, requests.exceptions.ConnectionError):
            # print("There is some issue!")
            continue

        # Emails
        new_emails = set(re.findall(
            r'[a-z0-9\. \-+_]+@[a-z0-9\. \-+_]+', response.text, re.I))
        emails.update(new_emails)

        # Numbers
        new_numbers = set(re.findall(
            r'(\d{3}[-\.\s]??\d{3}[-\.\s]??\d{4}|\(\d{3}\)\s*\d{3}[-\.\s]??\d{4}|\d{3}[-\.\s]??\d{4})', response.text, re.I))
        numbers.update(new_numbers)

        # Cookies
        cookies.extend(list(response.cookies))
        
        soup = BeautifulSoup(response.text, features="lxml")

        for anchor in soup.find_all("a"):
            link = anchor.attrs['href'] if 'href' in anchor.attrs else ''
        if link.startswith('/'):
            link = base_url + link
            if not link in urls and not link in scrapped_urls:
                urls.append(link)

    # print("Fetching email and numbers done for URL : " + url)

    # print("Printing mails")
    # for mail in emails:
    #     print(mail)

    # print("Printing Numbers")
    # for num in numbers:
    #     print(num)
    print(cookies)
    return emails, numbers, cookies


def getCookies(url):
    cookies = []


def getOwnHostIP():
    """Returns own host name and IP"""
    hostname = s.gethostname()
    IPAddr = s.gethostbyname(hostname)
    # print("My Computer Name is:" + hostname)
    # print("My Computer IP Address is:" + IPAddr)
    return hostname, IPAddr


def getIP(host):
    """ Returns the IP of the given host"""
    starter1 = "https://www."
    starter2 = "https://"

    host = host.replace(starter1, '')
    host = host.replace(starter2, '')

    if host.find('/') != -1:
        host = host[:host.find('/')]

    ip = None
    try:
        # print(f'IP of {host} is {s.gethostbyname(host)}')
        ip = s.gethostbyname(host)
    except Exception as e:
        print('Failed to resolve IP of the given host ( '+host+' ): ', e)
        ip = 'Failed to resolve IP'

    return ip


def getPageTitle(url):
    """ Returns the page title of the given url"""
    pageTitle = ""
    try:
        page = requests.get(url, timeout=30)
        soup = BeautifulSoup(page.content, 'html.parser')

        # Extract title of page
        pageTitle = soup.title.text

        # print the result
        # print(page_title)
    except:
        # print("Some issue in getting the page title")
        pageTitle = "No page title found"

    return pageTitle


def isDomainUrl(src, dest):
    """Checks if src and dest belongs to same parent domain"""
    # Get the domain from src and dest.
    starter1 = "https://www."
    starter2 = "https://"

    # Getting host from src
    src = src.replace(starter1, '')
    src = src.replace(starter2, '')

    if src.find('/') != -1:
        src = src[:src.find('/')]

    # Getting host from dest
    dest = dest.replace(starter1, '')
    dest = dest.replace(starter2, '')

    if dest.find('/') != -1:
        dest = dest[:dest.find('/')]

    if src == dest:
        return True

    return False


def getAllUrls(url):
    """Returns all the suburls"""
    subUrls = []
    grab = requests.get(url, timeout=30)
    soup = BeautifulSoup(grab.text, 'html.parser')
    for link in soup.find_all("a"):
        subUrl = link.get('href')
        if subUrl and isDomainUrl(url, subUrl):
            subUrls.append(subUrl)

    return subUrls


# print(getAllUrls("https://hybrique.com"))
