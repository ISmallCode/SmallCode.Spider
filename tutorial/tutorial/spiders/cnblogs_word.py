# -*- coding: utf-8 -*-
import sys

from scrapy.contrib.spiders import CrawlSpider
from scrapy.http import Request
from scrapy.selector import Selector

from tutorial.function import sql_helper
from tutorial.items import DmozItem

reload(sys)
sys.setdefaultencoding('utf8')


class CnblogsWordSpider(CrawlSpider):
    name = "cnblogs_word"
    allowed_domains = ["cnblogs.com"]
    start_urls = (
        'http://www.cnblogs.com/AllBloggers.aspx/',
    )

    def __init__(self):
        self.page_len = 0
        self.fout = open('cnblogs_word.txt', 'w')
        self.i = 0
        self.j = 0
        self.k = 0
        self.m = 0
        self.n = 0
        self.cookie = {
            ".CNBlogsCookie": "4BC1F02D9A9C4C8DAFB20D13CBCF4E951E02753E9B670B2A850645E4C905423411B2816B9308AC7A33B43DAF52660B23422B971258379EBC03638E3DD58F957CFEE195649446056FDFF34D928397B23EDFF4AC77"}
        self.page_info = ""
    def parse(self, response):
        self.i = self.i + 1
        list = sql_helper.get_user_list("博客园")
        for item in list:
            if (len(item) != 0):
                yield Request(url=str(item[0]), callback=self.parse_blogger_spider, dont_filter=True)

    def parse_item(self, response):
        self.j = self.j + 1
        try:
            if (response.status != 404) and (response.status != 302) and (response.status != 502):
                sel = Selector(response)
                word_links = sel.xpath("//div[@class='post_item']/div[2]/h3/a/@href").extract()
                for word_item in word_links:
                    yield Request(url=str(word_item), callback=self.parse_word)
                pages = sel.xpath('//div[@id="nav_next_page"]/a/@href').extract()
                if (len(pages) == 0):
                    pages_href = sel.xpath('//div[@class="pager"]/a/@href').extract()
                    pages_text = sel.xpath('//div[@class="pager"]/a/text()').extract()
                    if (pages_text[len(pages_text) - 1] == "下一页"):
                        page_url = "http://www.cnblogs.com" + str(pages_href[len(pages_href) - 1])
                        yield Request(url=str(page_url), callback=self.parse_item, cookies=self.cookie)
                else:
                    yield Request(url=str(pages[0]), callback=self.parse_item)
        except Exception, e:
            string = "Error %s,Url:%s,From:%s \n" % (e, response.url, "cnblogs,parse_item")
            self.fout.write(string)
            print string

    def parse_blogger(self, response):
        self.k = self.k + 1
        try:
            if (response.status != 404) and (response.status != 302) and (response.status != 502):
                sel = Selector(response)
                blogger_list = sel.xpath('//div[@id="blogger_list"]/ul/li/a/@href').extract()
                # yield Request(url=blogger_list[0], callback=self.parse_blogger_spider)
                for blogger_item in blogger_list:
                    yield Request(url=blogger_item, callback=self.parse_blogger_spider, cookies=self.cookie)
        except Exception, e:
            string = "Error %s,Url:%s,From:%s \n" % (e, response.url, "cnblogs,parse_blogger")
            self.fout.write(string)
            print string

    def parse_blogger_spider(self, response):
        self.m = self.m + 1
        if (response.status != 404) and (response.status != 302) and (response.status != 502) and (
            "post/readauth?url=" not in str(response.url)) and ("user/signin?ReturnUrl=" not in str(response.url)):
            sel = Selector(response)
            blogger_href = sel.xpath('//div[@class="post post-list-item"]/a/@href').extract()
            if (len(blogger_href) == 0):
                blogger_href = sel.xpath('//div[@class="postTitle"]/a/@href').extract()
            for href_item in blogger_href:
                yield Request(url=href_item, callback=self.parse_word)
            page = sel.xpath('//*[@id="pager"]/a/@href').extract()
            if (len(page) == 0):
                page = sel.xpath('//div[@id="nav_next_page"]/a/@href').extract()
                if (len(page) != 0):
                    yield Request(url=page[0], callback=self.parse_blogger_spider, dont_filter=True)
                else:
                    page = sel.xpath('//div[@class="pager"]/a/@href').extract()
                    page_text = sel.xpath('//div[@class="pager"]/a/text()').extract()
                    j = 0
                    for page_item in page_text:
                        if (page_item == "Next >"):
                            break
                        j += 1
                    if (j != len(page_text)):
                        yield Request(url=page[j], callback=self.parse_blogger_spider, dont_filter=True)
                    else:
                        i = 0
                        for page_item in page_text:
                            if (page_item == "下一页"):
                                break
                            i += 1
                        if (i != len(page_text)):
                            yield Request(url=page[i], callback=self.parse_blogger_spider,
                                          dont_filter=True)
                        else:
                            self.page_len = 0
                            string = "Page,Url:%s,From:%s \n" % (response.url, "cnblogs_word,parse_blogger_spider")
                            self.fout.write(string)
            else:
                if (page[len(page) - 1] == self.page_info):
                    self.page_info = page[len(page) - 1]
                    yield Request(url=page[len(page) - 1], callback=self.parse_blogger_spider, dont_filter=True,
                                  cookies=self.cookie)

    def parse_word(self, response):
        self.n = self.n + 1
        if ("post/readauth?url=" not in str(response.url)) and ("user/signin?ReturnUrl=" not in str(response.url)):
            sel = Selector(response)
            title = sel.xpath('//a[@id="cb_post_title_url"]/text()').extract()
            if (len(title) == 0):
                title = sel.xpath('//a[@class="postTitle2"]/text()').extract()
                if (len(title) == 0):
                    title = sel.xpath('//div[@id="news_title"]/a/text()').extract()
                    if (len(title) == 0):
                        string = "Title,Url:%s,From:%s \n" % (response.url, "cnblogs_word,parse_word")
                        print string
                        self.fout.write(string)
                        pass
            body = sel.xpath('//*[@id="cnblogs_post_body"]/*').extract()
            if (len(body) == 0):
                body = sel.xpath('//div[@class="postBody"]/*').extract()
                if (len(body) == 0):
                    body = sel.xpath('//div[@id="news_body"]/*').extract()
            category = sel.xpath('//div[@id="BlogPostCategory"]/a/text()').extract()
            item = DmozItem()
            item['title'] = str(title[0]).encode('utf-8').strip()
            word = ""
            for n in body:
                word += str(n).encode('utf-8')
            item['body'] = word
            item['url'] = response.url
            item['source'] = "博客园"
            item['table_name'] = 'cnblogs'
            item['browse'] = 0
            item['reply_count'] = 0
            item['category'] = "博客园"
            item['label'] = ""
            item['author'] = str(response.url).split("/")[3]
            sql_helper.insert_item(item)
            url_arr = str(response.url).split("/")
            postid = str(url_arr[len(url_arr) - 1]).strip(".html")
            print str(self.i) + "_" + str(self.j) + "_" + str(self.k) + "_" + str(self.m) + "_" + str(self.n)
            yield Request(url="http://www.cnblogs.com/mvc/blog/ViewCountCommentCout.aspx?postId=" + postid,
                          callback=self.parse_browse, dont_filter=True, meta={'URL': response.url}, cookies=self.cookie)

    def parse_browse(self, response):
        URL = response.meta['URL']
        browse = response.body
        sql_helper.update_word_Info(URL, browse)
