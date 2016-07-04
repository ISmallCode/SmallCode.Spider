# -*- coding: utf-8 -*-
import sys

from scrapy.crawler import CrawlerRunner
from scrapy.http import Request
from scrapy.selector import Selector
from scrapy.spider import Spider
from scrapy.utils.log import configure_logging
from twisted.internet import reactor

from tutorial.function import sql_helper
from tutorial.items import UserItem
from tutorial.spiders.oschina_word import OschinaWordSpider


reload(sys)
sys.setdefaultencoding('utf8')


class OschinaUserSpider(Spider):
    name = "oschina_user"
    allowed_domains = ["oschina.net/blog"]
    start_urls = (
        'http://www.oschina.net/blog',
    )

    def __init__(self):
        self.i = 0
        self.j = 0
        self.k = 0
        self.fout = open('oschina_user.txt', 'w')
        self.source = "开源中国"

    def parse(self, response):
        self.i = self.i + 1
        try:
            if (response.status != 404) and (response.status != 302) and (response.status != 502):
                sel = Selector(response)
                user_list = sel.xpath('//ul[@class="TOP_OSCER"]/li/a/@href').extract()
                for user_item in user_list:
                    yield Request(url=user_item, callback=self.parse_user, dont_filter=True)

        except Exception, e:
            string = "Error %s,Url:%s,From=%s \n" % (e, response.url, "oschina,parse")
            self.fout.write(string)

    def parse_user(self, response):
        self.j = self.j + 1
        url = response.url
        try:
            if ((unicode(response.body).encode('gbk')) != (u"该用户空间暂时不允许访问".encode('gbk'))):
                sel = Selector(response)
                NickName = sel.xpath('//div[@id="SpaceLeft"]/div/span[@class="U"]/a/text()').extract()
                url_arr = str(url).split("/")
                UserName = url_arr[len(url_arr) - 1]
                Info = ""
                medals_list = sel.xpath('//ul[@id="Medals"]/li/a/@title').extract()
                for item in medals_list:
                    Info += item
                fellow = sel.xpath('//div[@id="SpaceLeft"]/div/div[@class="stat"]/a[1]/span/text()').extract()
                fans = sel.xpath('//div[@id="SpaceLeft"]/div/div[@class="stat"]/a[2]/span/text()').extract()
                score = sel.xpath('//div[@id="SpaceLeft"]/div/div[@class="stat"]/a[3]/span/text()').extract()
                description = sel.xpath('//div[@id="MyResume"]/text()').extract()
                item = UserItem()
                item['UserName'] = UserName
                item['NickName'] = NickName[0]
                item['Info'] = Info
                item['UserWordUrl'] = url + "/blog"
                item['UserInfoUrl'] = url
                item['Fellow'] = int(str(fellow[0]).strip("(").strip(")"))
                item['Fans'] = int(str(fans[0]).strip("(").strip(")"))
                item['Source'] = self.source
                item['Score'] = int(str(score[0]).strip("(").strip(")"))
                item['Description'] = description[0]
                item['Skill'] = ""
                item['Email'] = ""
                item['Phone'] = ""
                item['QQ'] = ""
                item['WeiXin'] = ""
                item['Field'] = ""
                item['FunctionStyle'] = "InsertUser"
                sql_helper.insert_user(item['UserName'], item['Fellow'], item['Fans'], item['Score'],
                                       item['UserInfoUrl'],
                                       item['Source'], item['UserWordUrl'], item['NickName'], item['Description'],
                                       item['Skill'], item['Email'], item['Phone'], item['QQ'], item['WeiXin'],
                                       item['Field'], item['Info'])
                yield Request(url=url + "/fellow", callback=self.parse_user_fellow, dont_filter=True,
                              meta={'referer': url + "/fellow"})
                yield Request(url=url + "/fans", callback=self.parse_user_fellow, dont_filter=True,
                              meta={'referer': url + "/fans"})
                print str(self.i) + "_" + str(self.j) + "_" + str(self.k)
        except Exception, e:
            string = "Error %s,Url:%s,From=%s \n" % (e, url, "oschina,parse_user")
            self.fout.write(string)

    def parse_user_fellow(self, response):
        self.k = self.k + 1
        try:
            referer = response.meta['referer']
            sel = Selector(response)
            user_list = sel.xpath('//td[@class="avatar"]/a/@href').extract()
            for user_item in user_list:
                if (sql_helper.select_user(user_item, self.source) == 0):
                    yield Request(url=user_item, callback=self.parse_user, dont_filter=True)
            pages = sel.xpath('//div[@class="page next"]/a/@href').extract()
            if (len(pages) != 0):
                yield Request(url=referer + pages[0], callback=self.parse_user_fellow, dont_filter=True,
                              meta={'referer': referer})
        except Exception, e:
            string = "Error %s,Url:%s,From=%s \n" % (e, response.url, "oschina,parse_user_fellow")
            print string
            self.fout.write(string)

    def __exit__(self, exc_type, exc_val, exc_tb):
        print str(self.i)
        self.fout.close()
        configure_logging()
        runner = CrawlerRunner()
        runner.crawl(OschinaWordSpider)
        reactor.stop()
        reactor.run()
