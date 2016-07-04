# -*- coding: utf-8 -*-
import scrapy
from scrapy.contrib.loader import ItemLoader
from scrapy.selector import Selector

from fun.items import CoserItem


class CoserSpider(scrapy.Spider):
    name = "coser"
    allowed_domains = ["bcy.net"]
    start_urls = (
        'http://www.bcy.net/coser/',
    )

    def parse(self, response):
        sel = Selector(response)
        for link in sel.xpath(
                "//div[@class='l-grid l-grid--10 mb10']/div/div[@class='l-grid__item newThumbnail newThumbnail--118x220 js-img-error']/a/@href").extract():
            link = 'http://bcy.net%s' % link
            request = scrapy.Request(link, callback=self.parse_item)
            yield request

    def parse_item(self, response):
        l = ItemLoader(item=CoserItem(), response=response)
        l.add_xpath('name', "//h1[@class='js-post-title']/text()")
        l.add_xpath('info', "//div[@class='post__info']/div[@class='post__type post__info-group']/span/text()")
        urls = l.get_xpath('//img[@class="detail_std detail_clickable"]/@src')
        urls = [url.replace('/w650', '') for url in urls]
        l.add_value('image_urls', urls)
        l.add_value('url', response.url)
        l.add_value('source', 'coser')
        if (len(l.get_output_value('info')) == 0):
            l.add_xpath('info',
                        "string(//div[@class='post__content js-content-img-wrap js-fullimg js-maincontent mb20'])")
        return l.load_item()