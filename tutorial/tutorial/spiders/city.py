# -*- coding: utf-8 -*-
import MySQLdb
#import pymssql
import scrapy

from tutorial.items import DmozItem
from tutorial.function import sql_helper

class CitySpider(scrapy.Spider):
    name = "city"
    allowed_domains = ["58.com"]
    start_urls = (
        'http://www.58.com/changecity.aspx',
    )

    def parse(self, response):
        item = DmozItem()
        sel = scrapy.Selector(response)
        sites = sel.xpath("//dl[@id='clist']/dd/a/text()").extract()
        item['title'] = [n.encode('utf-8') for n in sites]
        for name in item['title']:
            print name
            sql_helper.insert_city(name)
