# -*- coding: utf-8 -*-
import sys

import scrapy
from scrapy.http import Request
from scrapy.selector import Selector

from tutorial.function import sql_helper

reload(sys)
sys.setdefaultencoding('utf8')

class WillSpider(scrapy.Spider):
    name = "will"
    allowed_domains = ["williamlong.info"]
    start_urls = (
        'http://www.williamlong.info/',
    )

    def __init__(self):
        self.i = 1
        self.fout = open('will.txt', 'w')

    def parse(self, response):
        try:
            if (response.status != 404) and (response.status != 302) and (response.status != 502):
                sel = Selector(response)
                sites = sel.xpath("//div[@id='divMain']/div/h2[@class='post-title']").extract()
                for site in sites:
                    body = Selector(text=site)
                    href = body.xpath("//a/@href").extract()
                    yield Request(callback=self.parse_word, url=href[0], meta={'referer': response.url})
                    # if (self.i <= 149):
                    #     self.i = self.i + 1
                    #     url = "http://www.williamlong.info/cat/?page=" + str(self.i)
                    #     yield Request(callback=self.parse, url=url)
        except Exception, e:
            string = "Error %s,Url:%s,From:(will,parse), \n" % (e, response.url)
            self.fout.write(string)

    def parse_word(self, response):
        try:
            if (response.status != 404) and (response.status != 302) and (response.status != 502):
                sel = Selector(response)
                title = sel.xpath("string(//h1[@class='post-title'])").extract()
                body = sel.xpath("//div[@id='artibody']/p").extract()
                label = sel.xpath('//*[@id="divMain"]/div[3]/h6/div[2]/a/span/text()').extract()
                category = sel.xpath('//*[@id="divMain"]/div[3]/h6/div[1]/a/span/text()').extract()
                Id = sel.xpath("//p[@class='cloudreamHelperLink']/@entryid").extract()
                span_id = "spn" + Id[0]
                if (len(label) != 0):
                    label_name = label[0].encode('utf-8').strip()
                else:
                    label_name = ""
                word = ""
                for n in body:
                    p_site = Selector(text=n)
                    img_src = p_site.xpath("//img/@src").extract()
                    if (len(img_src) != 0):
                        url = "http://www.williamlong.info"
                        old_str = str(img_src[0]).encode("utf-8")
                        new_str = url + str(img_src[0]).encode("utf-8")
                        n = n.replace(old_str, new_str)
                        word += n
                    else:
                        word += n
                footer_str = sel.xpath('string(//h6[@class="post-footer"])').extract()
                footer = str(footer_str).strip('[').strip(']').split('|')
                reply = str(footer[3]).decode('unicode-escape').encode('utf-8').strip(" 评论:")

                if (len(reply) != 0):
                    reply_count = int(reply)
                else:
                    reply_count = 0
                item_title = str(title[0]).encode("utf8").strip()
                item_category = str(category[0]).encode("utf-8")
                item_body = word.encode('utf-8')
                item_href = response.url
                item_label = label_name
                item_reply = reply_count
                item_browse = 0

                sql_helper.insert_query("will", "月光博客", item_title, item_category, item_body, item_href, item_label, "",
                                        item_reply, item_browse)
        except Exception, e:
            string = "Error %s \n" % (e)
            referer = response.meta['referer']
            self.fout.write("<GET:" + response.url + ">(referer:" + referer + "),From:(will,parse_word)," + string)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.fout.close()
