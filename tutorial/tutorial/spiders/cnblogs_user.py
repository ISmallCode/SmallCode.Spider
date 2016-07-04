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
from tutorial.spiders.cnblogs_word import CnblogsWordSpider

reload(sys)
sys.setdefaultencoding('utf8')


class cnblogs_user(Spider):
    name = "cnblogs_user"
    allowed_domains = ["cnblogs.com"]
    start_urls = (
        'http://www.cnblogs.com/AllBloggers.aspx',
    )

    def __init__(self):
        self.fout = open("cnblogs_user.txt", "w")
        self.source = str(u"博客园").encode("utf-8")
        self.cookie = {
            ".CNBlogsCookie": "4BC1F02D9A9C4C8DAFB20D13CBCF4E951E02753E9B670B2A850645E4C905423411B2816B9308AC7A33B43DAF52660B23422B971258379EBC03638E3DD58F957CFEE195649446056FDFF34D928397B23EDFF4AC77"}
        self.i = 0
        self.j = 0
        self.k = 0
        self.l = 0

    def parse(self, response):
        self.i = self.i + 1
        try:
            sel = Selector(response)
            all_bloggers = sel.xpath('//table/tr/td/a[1]/@href').extract()
            for blogger_item in all_bloggers:
                yield Request(url=blogger_item, cookies=self.cookie, callback=self.parse_item, dont_filter=True)
        except Exception, e:
            string = "Error %s,Url:%s,From=%s \n" % (e, response.url, "csblogs_user,parse")
            self.fout.write(string)

    def parse_item(self, response):
        self.j = self.j + 1
        try:
            url = response.url
            UserName = str(url).split("http://www.cnblogs.com/")[1].strip("/")
            UserInfoUrl = "http://home.cnblogs.com/u/" + UserName
            if (sql_helper.select_user(UserInfoUrl, self.source) == 0):
                yield Request(url=UserInfoUrl, cookies=self.cookie, callback=self.parse_info, dont_filter=True)
        except Exception, e:
            string = "Error %s,Url:%s,From=%s \n" % (e, response.url, "csblogs_user,parse_item")
            self.fout.write(string)

    def parse_info(self, response):
        self.k = self.k + 1
        try:
            item = UserItem()
            sel = Selector(response)
            name = str(response.url).split("http://home.cnblogs.com/u/")
            username = name[1]
            item['UserName'] = username[0:-1]
            nickname = sel.xpath('//h1[@class="display_name"]/text()').extract()
            if (len(nickname) != 0):
                item['NickName'] = str(nickname[0]).strip()
                info_list = sel.xpath('string(//ul[@id="user_profile"]/li)').extract()
                Info = ""
                for i in info_list:
                    Info += str(i).encode("utf-8").strip() + "|"
                item['Info'] = Info
                word_url = sel.xpath('//ul[@id="user_profile"]/li/a/@href').extract()
                if (len(word_url) != 0):
                    item['UserWordUrl'] = word_url[0]
                else:
                    item['UserWordUrl'] = ""
                item['UserInfoUrl'] = response.url
                item['Fellow'] = \
                sel.xpath('//div[@class="data_count_block"]/div[@class="data_left"]/div/a/text()').extract()[0]
                item['Fans'] = \
                sel.xpath('//div[@class="data_count_block"]/div[@class="data_right"]/div/a/text()').extract()[0]
                item['Source'] = self.source
                item['Score'] = 0
                item['Description'] = ""
                item['Skill'] = ""
                item['Email'] = ""
                item['Phone'] = ""
                item['QQ'] = ""
                item['WeiXin'] = ""
                item['Field'] = ""
                item['FunctionStyle'] = "InsertUser"
                # yield item
                print str(self.i) + "_" + str(self.j) + "_" + str(self.k) + "_" + str(self.l)
                sql_helper.insert_user(item['UserName'], item['Fellow'], item['Fans'], item['Score'], item['UserInfoUrl'],
                                       item['Source'], item['UserWordUrl'], item['NickName'], item['Description'],
                                       item['Skill'], item['Email'], item['Phone'], item['QQ'], item['WeiXin'],
                                       item['Field'], item['Info'])
                yield Request(url=response.url + "/followers", cookies=self.cookie, callback=self.parse_user,
                              dont_filter=True)
                yield Request(url=response.url + "/followees", cookies=self.cookie, callback=self.parse_user,
                              dont_filter=True)
                print str(self.i) + "_" + str(self.j) + "_" + str(self.k) + "_" + str(self.l)
        except Exception, e:
            string = "Error %s,Url:%s,From=%s \n" % (e, response.url, "csblogs_user,parse_info")
            self.fout.write(string)

    def parse_user(self, response):
        self.l = self.l + 1
        try:
            sel = Selector(response)
            avtar_list = sel.xpath('//div[@class="avatar_list"]/ul/li/div/a/@href').extract()
            for avtar_item in avtar_list:
                user_url = "http://home.cnblogs.com" + avtar_item
                if (sql_helper.select_user(user_url, self.source) == 0):
                    yield Request(url=user_url, cookies=self.cookie, callback=self.parse_info, dont_filter=True)
            page_text = sel.xpath('//div[@class="pager"]/a/text()').extract()
            page_href = sel.xpath('//div[@class="pager"]/a/@href').extract()
            if (len(page_text) != 0):
                if (page_text[len(page_text) - 1] == "Next >"):
                    page_next = page_href[len(page_href) - 1]
                    page_next_url = "http://home.cnblogs.com" + page_next
                    yield Request(url=page_next_url, cookies=self.cookie, callback=self.parse_user, dont_filter=True)
                else:
                    string = "Page,Url:%s,From=%s \n" % (response.url, "csblogs_user,parse_user")
                    print string
        except Exception, e:
            string = "Error %s,Url:%s,From=%s \n" % (e, response.url, "csblogs_user,parse_user")
            self.fout.write(string)

    def __exit__(self, exc_type, exc_val, exc_tb):
        print str(self.i)
        self.fout.close()
        configure_logging()
        runner = CrawlerRunner()
        runner.crawl(CnblogsWordSpider)
        reactor.run()
