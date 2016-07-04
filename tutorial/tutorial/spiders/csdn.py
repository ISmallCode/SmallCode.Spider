# -*- coding: utf-8 -*-
import sys

import scrapy
from scrapy.http import Request
from scrapy.selector import Selector
from scrapy.settings import Settings

from tutorial.function import sql_helper

reload(sys)
sys.setdefaultencoding('utf8')


class CsdnSpider(scrapy.Spider):
    name = "csdn"
    allowed_domains = ["blog.csdn.net"]
    start_urls = (
        'http://blog.csdn.net',
    )

    def __init__(self):
        self.page_info = ""
        self.fout = open('csdn.txt', 'w')
        self.i = 0
        self.j = 0
        self.k = 0
        self.page_num = 0
        self.page_num2 = 0

    def parse(self, response):
        try:
            sel = Selector(response)
            nav_links = sel.xpath('//ul[@class="navbar-nav"]/li/a/@href').extract()
            for i in range(0, len(nav_links) - 2):
                link_url = str("http://blog.csdn.net" + nav_links[i])
                yield Request(callback=self.parse_item, url=link_url, dont_filter=True)
            side_links = sel.xpath('//div[@class="side_nav"]/ul/li/a/@href').extract()
            for link_item in side_links:
                link_url = "http://blog.csdn.net" + link_item
                yield Request(callback=self.parse_item, url=link_url, dont_filter=True)
            alive_links = sel.xpath('//dl[@class="alive_user"]/dt/a/@href').extract()
            for alive_item in alive_links:
                link_url = alive_item
                yield Request(callback=self.parse_user, url=link_url, dont_filter=True)
            experts_links = sel.xpath('//dl[@class="experts"]/dd/ul/li/a/@href').extract()
            for experts_item in experts_links:
                link_url = experts_item
                yield Request(callback=self.parse_user, url=link_url, dont_filter=True)
        except Exception, e:
            string = "Error %s,Url:%s,From=%s \n" % (e, response.url, "csdn,parse")
            self.fout.write(string)

    def parse_item(self, response):
        self.j = self.j + 1
        try:
            sel = Selector(response)
            sites = sel.xpath("//div[@class='blog_list']").extract()
            for site in sites:
                body = Selector(text=site)
                href = body.xpath("//h1/a/@href").extract()
                desc = body.xpath("//h1/a[@class='category']/text()").extract()
                replynum = body.xpath('//div[@class="about_info"]/span[@class="fl"]/a[3]/text()').extract()
                    # print len(desc)
                URL = href[len(href) - 1]
                if (len(desc) == 0):
                    desc_str = 0
                    desc.append(desc_str)
                yield Request(url=URL,
                              meta={'desc': desc[0].encode('utf-8'), 'replynum': replynum, 'referer': response.url},
                              callback=self.parse_word)
            pages = sel.xpath("//div[@class='page_nav']/a/@href").extract()
            pages_text = sel.xpath('//div[@class="page_nav"]/a/text()').extract()
            page_num = 0
            for page_item in pages_text:
                if (page_item == u"下一页"):
                    break
                page_num += 1
            if (page_num != len(pages)):
                yield Request(callback=self.parse_item, url="http://blog.csdn.net" + pages[page_num], dont_filter=True)

        except Exception, e:
            string = "Error %s,Url:%s,From:(csdn,parse_item), \n" % (e, response.url)
            self.fout.write(string)
            print string
            Settings.DOWNLOAD_DELAY = 10

    def parse_user(self, response):
        self.k = self.k + 1
        try:
            sel = Selector(response)
            title_links = sel.xpath('//div[@class="list_item article_item"]').extract()
            for title_item in title_links:
                body = Selector(text=title_item)
                link_url = body.xpath('//div[@class="article_title"]/h1/span/a/@href').extract()
                replynum = body.xpath('div[@class="article_manage"]/span[@class="link_comments"]/text()').extract()
                yield Request(callback=self.parse_word, url="http://blog.csdn.net" + link_url[0], dont_filter=True,
                              meta={'desc': 0, 'replynum': replynum, 'referer': response.url})
            pages = sel.xpath("//div[@id='papelist']/a/@href").extract()
            if (len(pages) >= self.page_num):
                page_link = pages[-2]
                self.page_num = len(pages)
                self.page_info = pages[-1]
                url = "http://blog.csdn.net" + page_link
                print str(self.j) + "_" + str(self.k) + "_" + str(self.i)
                yield Request(callback=self.parse_user, url=url, dont_filter=True)
            else:
                self.page_num = 0
        except Exception, e:
            string = "Error %s,Url:%s,From:(csdn,parse_user), \n" % (e, response.url)
            self.fout.write(string)

    def parse_word(self, response):
        self.i = self.i + 1
        print str(self.j) + "_" + str(self.k) + "_" + str(self.i)
        try:
            if (response.status != 404) and (response.status != 302) and (response.status != 502):
                category = response.meta['desc']
                replynum = self.getReplyCount(response.meta['replynum'])
                word_sel = Selector(response)
                if (category == 0):
                    category_info = word_sel.xpath('//div["category_r"]/label/span/text()').extract()
                    if (len(category_info) != 0):
                        category = category_info[0]
                    else:
                        category = u'其他'
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
                item_author = url_list[4]
                sql_helper.insert_query("csdn", "CSDN", item_title, item_category, item_body, item_href, item_label,
                                        item_author,
                                        item_reply, item_browse)
        except Exception, e:
            string = "Error %s \n" % (e)
            referer = response.meta['referer']
            self.fout.write("<GET:" + response.url + ">(referer:" + referer + "),From:(csdn,parse_word)," + string)

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
