# -*- coding: utf-8 -*-
import sys

import scrapy
from scrapy.http import Request
from scrapy.selector import Selector

from tutorial.function import sql_helper

reload(sys)
sys.setdefaultencoding('utf8')


class CsdnWordSpider(scrapy.Spider):
    name = "csdn_word"
    allowed_domains = ["blog.csdn.net"]
    start_urls = (
        'http://blog.csdn.net',
    )

    def __init__(self):
        self.page_info = ""
        self.fout = open('csdn.txt', 'w')
        self.i = 0
        self.j = 0
        self.page_num = 0
        self.page_num2 = 0

    def parse(self, response):
        try:
            list = sql_helper.get_user_list("csdn")
            for item in list:
                if (len(item) != 0):
                    yield Request(callback=self.parse_item, url=str(item[0]), dont_filter=True)
        except Exception, e:
            string = "Error %s,Url:%s,From=%s \n" % (e, response.url, "csdn_word,parse")
            print string
            self.fout.write(string)

    def parse_item(self, response):
        self.j = self.j + 1
        sel = Selector(response)
        sites = sel.xpath("//div[@class='list_item article_item']").extract()
        for site in sites:
            body = Selector(text=site)
            href = body.xpath("//div[@class='article_title']/h1/span/a/@href").extract()
            replynum = body.xpath('//div[@class="article_manage"]/span[@class="link_comments"]/text()').extract()
            URL = "http://blog.csdn.net" + href[0]
            yield Request(url=URL, meta={'replynum': replynum, 'referer': response.url}, callback=self.parse_word)
        pages_url = sel.xpath("//div[@class='page_nav']/a/@href").extract()
        pages_text = sel.xpath("//div[@class='page_nav']/a/text()").extract()
        num = 0
        for page_item in pages_text:
            if (page_item == "下一页"):
                break
            num += 1
        if (num != len(pages_url)):
            page_link = pages_url[num]
            yield Request(callback=self.parse_item, url=page_link, dont_filter=True)

    def parse_word(self, response):
        self.i = self.i + 1
        try:
            if (response.status != 404) and (response.status != 302) and (response.status != 502):
                replynum = self.getReplyCount(response.meta['replynum'])
                word_sel = Selector(response)
                category_info = word_sel.xpath('//div["category_r"]/label/span/text()').extract()
                if (len(category_info) != 0):
                    category = category_info[0]
                else:
                    category = u'CSDN'
                title = word_sel.xpath(
                    "string(//div[@id='article_details']/div[@class='article_title']/h1/span[@class='link_title']/a)").extract()
                body = word_sel.xpath("//div[@class='details']/div[@class='article_content']").extract()
                browse = word_sel.xpath('//span[@class="link_view"]/text()').extract()
                get_browse = self.getBrowse(browse)
                label = word_sel.xpath('//span[@class="link_categories"]/a/text()').extract()
                label_list = ""
                url_list = str(response.url).split('/')
                if (len(label) != 0):
                    for n in label:
                        label_list += n + ","
                    label_list = label_list[0:-1]

                item_title = str(title[0].encode('utf-8')).replace(' ', '').strip()
                item_category = category
                item_body = [n.encode('utf-8') for n in body]
                item_href = response.url
                item_label = label_list
                item_reply = replynum
                item_browse = int(get_browse)
                item_author = url_list[3]
                sql_helper.insert_query("csdn", "CSDN", item_title, item_category, item_body, item_href, item_label,
                                        item_author,
                                        item_reply, item_browse)
                print str(self.j) + "_" + "_" + str(self.i)
        except Exception, e:
            referer = response.meta['referer']
            string = "<GET:" + response.url + ">(referer:" + referer + "),From:(csdn_word,parse_word)," + "Error %s \n" % (
                e)
            self.fout.write(string)
            print string

    def getBrowse(self, browse):
        if (len(browse) == 0):
            return 0
        else:
            get_browse = browse[0]
            return str(get_browse).strip('人阅读')

    def getReplyCount(self, replynum):
        if (len(replynum) == 0):
            return 0
        else:
            return str(replynum[0]).strip('评论(').strip(')')

    def __exit__(self, exc_type, exc_val, exc_tb):
        print str(self.i)
        self.fout.close()
