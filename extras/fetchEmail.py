from bs4 import BeautifulSoup  # Parses html and xml documents
import requests  # Send requests
import requests.exceptions  # Handle exceptions in case of request timeout
import urllib.parse  # Manages all url stuffs
from collections import deque  # Keeps all url in a list and takes one at a time
import re  # re is regex

# Take urls as str input from the user
user_url = str(input('[+]Enter the target url to scan:'))
# Transferring the user urls to deque
urls = deque([user_url])

# Variable to store the scrapped urls and a variable to store the emails
scrapped_urls = set()
emails = set()

count = 0
try:
    while len(urls):
        # Takes one url at a time
        count += 1
        if count == 100:  # Stop here when the urls reach 100
            break

        # Take urls from the left side of deque
        url = urls.popleft()
        scrapped_urls.add(url)

        parts = urllib.parse.urlsplit(url)
        base_url = '{0.scheme}://{0.netloc}', format(parts)  # fetches the network location (for ex ip address)

        # Take urls one by one and show the user that its processing
        path = url[:url.rfind('/') + 1] if '/' in parts.path else url
        print('[%d] Processing %s' % (count, url))

        try:
            response = requests.get(url)
        except(requests.exceptions.MissingSchema, requests.exceptions.ConnectionError):
            print("There is some issue!")
            continue

        new_emails = set(re.findall(r'[a-z0-9\. \-+_]+@[a-z0-9\. \-+_]+', response.text, re.I))
        emails.update(new_emails)

        soup = BeautifulSoup(response.text, features="lxml")

        for anchor in soup.find_all("a"):
            link = anchor.attrs['href'] if 'href' in anchor.attrs else ''
        if link.startswith('/'):
            link = base_url + link
            if not link in urls and not link in scrapped_urls:
                urls.append(link)

    print("Printing mails")
    for mail in emails:
        print(mail)

except KeyboardInterrupt:
    print('[-] Closing!')

    for mail in emails:
        print(mail)
