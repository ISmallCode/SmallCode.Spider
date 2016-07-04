#encoding=utf8

import urllib2
import cookielib
import lxml.html
from __builtin__ import False
import threading
import time

ip_list = []#最后的可用列表

def prepare():
    cj = cookielib.MozillaCookieJar()
    cookie_support = urllib2.HTTPCookieProcessor(cj)
    opener = urllib2.build_opener(cookie_support)
    opener.addheaders = [('User-agent','Mozilla/5.0 (X11; Linux x86_64; rv:38.0) Gecko/20100101 Firefox/38.0 Iceweasel/38.3.0')]
    urllib2.install_opener(opener)

def page(j):
    prepare()
    try:
        url = 'http://www.xicidaili.com/wn/'+str(j)
        response = urllib2.urlopen(url)
        http = response.read().decode('utf-8')
        doc = lxml.html.fromstring(http)
        results = doc.xpath('//div/table[@id="ip_list"]/tr/td/text()')
        return results
    except:
        pass

def page_content(j):
    url = 'http://www.xicidaili.com/wn/'+str(j)
    results = page(j)
    for i in range(1,100):
        try:
            proxy = results[i*10]+":"+results[i*10+1]
            sContent = urllib2.urlopen(url,timeout=3).getcode()
            if(sContent == 200):
                print(proxy)
                ip_list.append(proxy)
            else:
                print("***")
        except:
            pass



class everpage(threading.Thread):
    def __init__(self,page):
        threading.Thread.__init__(self)
        self.page = page
        self.thread_stop = False

    def run(self):
        while not self.thread_stop:
            page_content(self.page)

            self.stop()

    def stop(self):
        self.thread_stop = True


if __name__=='__main__':
    for i in range(1,100):
        try:
            everpage(i).start()
            time.sleep(5)
        except:
            pass
