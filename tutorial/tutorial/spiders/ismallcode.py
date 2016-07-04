# -*- coding: utf-8 -*-
from scrapy.selector import Selector
from scrapy.spider import Spider


class IsmallcodeSpider(Spider):
    name = "ismallcode"
    allowed_domains = ["ismallcode.com"]
    start_urls = ['http://www.ismallcode.com/']

    def __init__(self):
        self.num=0

    def parse(self, response):
        sel = Selector(response)
        items = sel.xpath('//nav/*').extract()
    def parse_blog(self, response):
        print response.url
    def parse_cursor(self, response):
        print response.url
    def parse_demand(self, response):
        print response.url
    def parse_forum(self, response):
        print response.url