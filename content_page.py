#tbody
#views-field views-field-title

from bs4 import BeautifulSoup

def ctrl_c(signum, frame):
    global shutdown_event
    shutdown_event.set()
    raise SystemExit("\nCancelling...")

def getKeyword(html):
    fp = open("title&link.csv", "a")
    soup = BeautifulSoup(html)
    items = soup.find_all("td", class_="views-field views-field-title")
    for i in items:
        a = i.select("a")
        title = (a[0].get_text())
        link = (a[0].get('href'))
        fp.write(title + ";" + link + "\n")
        print (title + "," + link)
f = open("Content | myUSF1.html", "r")
html = f.read()
getKeyword(html)
