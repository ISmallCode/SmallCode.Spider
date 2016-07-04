# -*- coding: utf-8 -*-
import sys

import scrapy
from scrapy.http import Request
from scrapy.selector import Selector

from tutorial.function import sql_helper

reload(sys)
sys.setdefaultencoding('utf8')


class OschinaWordSpider(scrapy.Spider):
    name = "oschina_word"
    allowed_domains = ["oschina.net/blog"]
    start_urls = (
        'http://www.oschina.net/blog',
    )

    def __init__(self):
        self.page = 1
        self.tag_tf = True
        self.tag_num = 1
        self.num = 1
        self.fout = open('oschina_word.txt', 'w')

    def parse(self, response):
        try:
            list = sql_helper.get_user_list("开源中国")
            for item in list:
                if (len(item) != 0):
                    yield Request(callback=self.parse_user_blog, url=str(item[0]), dont_filter=True,
                                  meta={"referer": response.url})
        except Exception, e:
            string = "Error %s,Url:%s,From=%s \n" % (e, response.url, "csdn_word,parse")
            print string
            self.fout.write(string)

    def parse_user_blog(self, response):
        try:
            blog_url = response.meta['referer']
            sel = Selector(response)
            blog_lists = sel.xpath('//li[@class="Blog"]/div/div/h2/a/@href').extract()
            for blog_item in blog_lists:
                yield Request(url=blog_item, callback=self.parse_word, meta={"referer": response.url}, dont_filter=True)
            pages = sel.xpath('//div[@class="page next"]/a/@href').extract()
            if (len(pages) != 0):
                yield Request(url=blog_url + pages[0], callback=self.parse_user_blog, dont_filter=True,
                              meta={'referer': blog_url})
        except Exception, e:
            string = "Error %s,Url:%s,From=%s \n" % (e, response.url, "oschina,parse_user_blog")
            self.fout.write(string)
            print string

    def parse_word(self, response):
        if (response.status != 404) and (response.status != 302) and (response.status != 502):
            sel = Selector(response)
            title = sel.xpath('//div[@class="BlogTitle"]/h1/text()').extract()
            browse = sel.xpath('//div[@class="BlogStat"]/span[1]/text()').extract()
            reply = sel.xpath('//div[@class="BlogStat"]/a/span/text()').extract()
            catalogs = sel.xpath('//span[@class="catalogs"]/ul/li[1]/a/text()').extract()
            label = sel.xpath('//div[@class="BlogTags"]/a/text()').extract()
            if (len(label) != 0):
                label_item = ""
                for l in label:
                    label_item += l + ","
                label_item = label_item[0:-1]
            else:
                label_item = ""
            body = sel.xpath('//div[@class="BlogContent"]/*').extract()
            body1 = sel.xpath('//div[@class="BlogAbstracts"]/*').extract()
            body2 = sel.xpath('//div[@class="BlogAnchor"]/*').extract()
            body_item = ""
            for b1 in body1:
                body_item += b1
            for b2 in body2:
                body_item += b2
            for b in body:
                body_item += b
            if (len(body_item) == 0):
                text = sel.xpath('string(//*[@class="noshow_content"])').extract()
                body_item = text[0]

            item_title = str(title[len(title) - 1]).strip("\t")
            if (len(browse) == 0):
                item_browse = 0
            else:
                item_browse = int(str(browse[0]).strip())
            item_reply = int(str(reply[0]).strip())
            item_category = str(catalogs[0]).encode('utf-8').strip()
            item_body = body_item.encode('utf-8')
            item_href = str(response.url).encode('utf-8')
            item_label = label_item
            url_arr = str(response.url).split("/")
            item_author = url_arr[3]
            sql_helper.insert_query("oschina", "开源中国", item_title, item_category, item_body, item_href, item_label,
                                    item_author,
                                    item_reply, item_browse)
