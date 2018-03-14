#test if the regex is correct

try:
    from urllib3 import urlopen, Request, HTTPError, URLError
except ImportError:
    from urllib.request import urlopen, Request, HTTPError, URLError

import signal
import threading
from bs4 import BeautifulSoup
import sys
import time
import urllib3
import re
import ssl

ssl._create_default_https_context = ssl._create_unverified_context #some computer need this for urllib open

shutdown_event = None
GAME_OVER = "game over"
keyword1 = "<iframe"
keyword2 = "</iframe>"
link = "https://myusf.usfca.edu/hps/tobacco-free"

def build_request(url, data=None, headers={}):
    headers["User-Agent"] = "Dynamsoft"
    return Request(url, data=data, headers=headers)

def ctrl_c(signum, frame):
    global shutdown_event
    shutdown_event.set()
    raise SystemExit("\nCancelling...")

def getKeyword(html, link):
    #r=r'https://www.usfca.edu.*'
    #r = match
    re_element=re.compile(r'' + keyword1 + '.*' + keyword2)
    content = html.decode("utf-8").lower()
    elements = set(re.findall(re_element, content))
    return elements


request = build_request(link)
f = urlopen(request, timeout=3)
xml = f.read()
#print (xml)
result = getKeyword(xml, link)
for i in result:
    print (i)
