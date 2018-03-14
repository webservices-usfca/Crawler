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
keyword = "www.youtube" #you can change keyword here

def build_request(url, data=None, headers={}):
    headers["User-Agent"] = "Dynamsoft"
    return Request(url, data=data, headers=headers)

def ctrl_c(signum, frame):
    global shutdown_event
    shutdown_event.set()
    raise SystemExit("\nCancelling...")

class Crawler(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)

    def run(self):
        file = None
        try:
            try:
            	# Change the file name below this to change where the links are written to
                file = open("videolinks_v2.csv", "w+")#every time delete the old file and then write
            except:
                print ("Failed to open file.")

            if file != None:
                pages = self.readSiteMap()
                # pages = ["http://192.168.8.233/test.aspx"] # for test
                for page in pages:
                    links = self.readHref(page)
                    if links == GAME_OVER:
                        break;

                    ret = self.crawlLinks(links, pages, file)
                    if ret == GAME_OVER:
                        break;
        except IOError:
            print( "IOError")
        finally:
            if file:
                file.close()

    def queryLinks(self, result):
        links = []
        content = b"".join(result)
        soup = BeautifulSoup(content)
        elements = soup.select("a")

        for element in elements:
            if shutdown_event.isSet():
                return GAME_OVER

            try:
                link = element.get("href")
                if link.startswith("http"):
                    links.append(link)
            except:
                print ("href error!!!")
                continue

        return links

    def readHref(self, url):
        result = []
        try:
            request = build_request(url)
            f = urlopen(request, timeout=3)
            while 1 and not shutdown_event.isSet():
                tmp = f.read(10240)
                if len(tmp) == 0:
                    break
                else:
                    result.append(tmp)

            f.close()
        except (HTTPError, URLError):
            print (URLError.code)

        if shutdown_event.isSet():
            return GAME_OVER

        return self.queryLinks(result)

    def readSiteMap(self):
        pages = []
        try:
            # f = urlopen("http://www.codepool.biz/sitemap.xml")
            # Change the link when you need to crawl a different page
            url = "https://www.usfca.edu/sitemap.xml"
            maps = self.getLinks(self.getHtml(url))
            for map in maps:
                request = build_request(map)
                f = urlopen(request, timeout=3)
                xml = f.read()

                soup = BeautifulSoup(xml)
                urlTags = soup.find_all("url")
                # print(urlTags)

                print ("The number of url tags in sitemap: ", str(len(urlTags)))

                for sitemap in urlTags:
                    link = sitemap.findNext("loc").text
                    pages.append(link)
                f.close()

        except (HTTPError, URLError):
            print (URLError.code)

        return pages

    def getHtml(self, url):
        request = build_request(url)
        f = urlopen(request, timeout=3)
        xml = f.read()
        return xml

    def getYoutube(self, html, link):
        #r=r'https://www.usfca.edu.*'
        #r = match
        re_video=re.compile(r'' + keyword + '.*?"')
        videolinks = set(re.findall(re_video, html.decode("utf-8")))
        return {'youtube' : list(videolinks), 'link': link}

    def getLinks(self, html):
        r=r'<loc>.*</loc>'
        re_maps = re.compile(r)
        temps = set(re.findall(re_maps, html.decode("utf-8")))
        maps = []
        for usfmap in temps:
            maps.append(usfmap[5:-6])
        return maps


    def crawlLinks(self, links, pages, file=None):
        res = []
        for link in pages:
            if shutdown_event.isSet():
                return GAME_OVER
            status_code = 0

            # This is due to an error the program will pick up
            if link != "https://www.linkedin.com/edu/school?id=17968":
                try:
                    request = build_request(link)
                    f = urlopen(request)
                    status_code = f.code
                    f.close()
                except (HTTPError, URLError):
                    status_code = HTTPError

                if status_code == 200:
                    request = build_request(link)
                    f = urlopen(request, timeout=3)
                    xml = f.read()
                    youtubes = self.getYoutube(xml, link)
                    l = len(youtubes['youtube'])
                    for i in range(l):
                        youtubeURL = youtubes['youtube'][i][:-1]
                        if youtubeURL in res: continue
                        res.append(youtubeURL)
                        print (youtubeURL + ", " + youtubes['link'])
                        file.write(youtubeURL + "," + youtubes['link'] + "\n")
                        file.flush()

        return GAME_OVER

def crawlPages():
    global shutdown_event
    shutdown_event = threading.Event()

    signal.signal(signal.SIGINT, ctrl_c)

    crawler = Crawler()
    crawler.start()
    while crawler.isAlive():
        crawler.join(timeout=0.1)

    print (GAME_OVER)

def main():
    try:
        crawlPages()
    except KeyboardInterrupt:
        print_("\nKeyboardInterrupt")

if __name__ == "__main__":
    main()
