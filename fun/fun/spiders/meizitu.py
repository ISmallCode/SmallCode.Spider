# -*- coding: utf-8 -*-
import scrapy
from scrapy.contrib.loader import ItemLoader, Identity
from scrapy.selector import Selector

from fun.items import MeizituItem


class MeizituSpider(scrapy.Spider):
    name = "meizitu"
    allowed_domains = ["meizitu.com"]
    start_urls = (
        'http://www.meizitu.com/',
    )

    def parse(self, response):
        sel = Selector(response)
        for link in sel.xpath('//h2/a/@href').extract():
            request = scrapy.Request(link, callback=self.parse_item)
            yield request
        request = scrapy.Request('http://www.meizitu.com/a/list_1_1.html', callback=self.parse_link)
        yield request

    def parse_link(self, response):
        sel = Selector(response)
        for link in sel.xpath('//h3[@class="tit"]/a/@href').extract():
            request = scrapy.Request(link, callback=self.parse_item)
            yield request
        page_url = sel.xpath('//div[@id="wp_page_numbers"]/ul/li/a/@href').extract()
        page_text = sel.xpath('//div[@id="wp_page_numbers"]/ul/li/a/text()').extract()
        page_num = 0
        page_next = u"下一页".encode('gbk')
        for item in page_text:
            page_item = unicode(item).encode('gbk')
            if (page_item == page_next):
                break
            page_num += 1

        if (page_num < len(page_url)):
            scrapy.Request("http://www.meizitu.com/a/" + page_url[page_num], callback=self.parse_link)

    def parse_item(self, response):
        l = ItemLoader(item=MeizituItem(), response=response)
        l.add_xpath('name', '//h2/a/text()')
        l.add_xpath('info', "//div[@id='maincontent']/div[@class='postmeta  clearfix']/div[@class='metaRight']/p")
        l.add_xpath('image_urls', "//div[@id='picture']/p/img/@src", Identity())
        l.add_value('url', response.url)
        l.add_value('source', 'meizitu')
        if (len(l.get_output_value('info')) == 0):
            l.replace_value('info', "//div[@class='post__staff post__info-group']/span/text()")
        return l.load_item()
