# -*- coding: utf-8 -*-
import sys
import time

import MySQLdb
#import pymssql
import scrapy
from scrapy.selector import Selector

from tutorial.items import DmozItem

reload(sys)
sys.setdefaultencoding('utf8')


class CnhubeiSpider(scrapy.Spider):
    name = "cnhubei"
    allowed_domains = ["cnhubei.com"]
    start_urls = [
        "http://news.cnhubei.com"
    ]

    def parse(self, response):
        items = []
        sel = Selector(response)
        sites = sel.xpath("//div[@class='first_box_mid left']/div[@class='news_mid_box']").extract()
        for site in sites:
            body = Selector(text=site)
            desc = body.xpath("//div[@class='news_subnav_2']/h1/text()").extract()
            for list in body.xpath("//ul/li").extract():
                item = DmozItem()
                list_body = Selector(text=list)
                links = list_body.xpath("//a/@href").extract()
                if (links[0][0] == "."):
                    links[0] = "http://news.cnhubei.com" + links[0][1:]
                # print links[0]
                # print type(links[0])
                # print "--------------"
                yield scrapy.Request(url=links[0], meta={'desc': desc[0].encode('utf-8'), 'source': response.url},
                                     callback=self.parse_word)

        sites2 = sel.xpath("//div[@class='first_box_mid left']/div[@class='news_mid_box cBlue']").extract()
        for site in sites2:
            body = Selector(text=site)
            desc = body.xpath("//div[@class='news_subnav_2']/h1/text()").extract()
            for list in body.xpath("//ul/li").extract():
                item = DmozItem()
                list_body = Selector(text=list)
                links = list_body.xpath("//a/@href").extract()
                if (links[0][0] == "."):
                    links[0] = "http://news.cnhubei.com" + links[0][1:]
                yield scrapy.Request(url=links[0], meta={'desc': desc[0].encode('utf-8')}, callback=self.parse_word)

    def parse_word(self, response):
        # print response.meta['desc']
        # item = DmozItem()
        desc = response.meta['desc']
        ISOTIMEFORMAT = '%Y-%m-%d %X'
        conn = MySQLdb.connect(host="118.192.146.104", user="root", passwd="root", db="test", port=3306,
                                charset='utf8')
        cursor = conn.cursor()
        conn2 = MySQLdb.connect(host="121.42.136.4", user='root', passwd='123456', db='spider', port=3306,
                                charset='utf8')
        cursor2 = conn2.cursor()
        word_sel = Selector(response)
        href = response.url
        title = word_sel.xpath("//div[@class='left_content']/div[@class='title']/text()").extract()
        body = word_sel.xpath("//div[@class='left_content']/div[@class='content_box']/p").extract()
        content = ''
        if (len(body) == 0):
            body = word_sel.xpath("//div[@class='left_content']/div[@class='content_box']/div").extract()
        for n in body:
            p_site = Selector(text=n)
            img_src = p_site.xpath("//img/@oldsrc").extract()
            if (len(img_src) != 0):
                url_obj = href.split('/')
                url = ""
                for i in range(0, len(url_obj) - 1):
                    url += url_obj[i] + "/"
                old_str = "./" + str(img_src[0]).encode("utf-8")
                new_str = str(url).encode("utf-8") + str(img_src[0]).encode("utf-8")
                n = n.replace(old_str, new_str)
                content += n
            else:
                content += n
        # item['title']=[n.decode("utf8").encode('gbk') for n in title]
        # item['body']=content.decode("utf8").encode('gbk')
        # item['desc']=desc.decode("utf8").encode('gbk')
        # item['link']=href.decode("utf8").encode('gbk')
        select_sql = "select * from  T_News where Url=%s"
        parm = (href.encode('utf-8'))
        cursor.execute(select_sql, parm)
        select_sql2 = "select * from  news where url='" + href.encode('utf-8') + "'"
        cursor2.execute(select_sql2)
        result = cursor.fetchall()
        result2 = cursor2.fetchall()
        if (len(result) == 0):
            sql = "Insert into T_News(Title,Content,DateTime,Url,Source,Category)values('" + title[0].encode(
                'utf-8') + "','" + content.encode('utf-8') + "','" + time.strftime(ISOTIMEFORMAT,
                                                                                   time.localtime()) + "','" + href.encode(
                'utf-8') + "','荆楚网','" + desc + "')"
            cursor.execute(sql)
            conn.commit()
        else:
            if (len(result2) == 0):
                sql2 = "Insert into news (title,text,datetime,url) VALUES (%s,%s,%s,%s)"
                parm2 = [title[0].encode('utf-8'), content.encode('utf-8'),
                         time.strftime(ISOTIMEFORMAT, time.localtime()), href.encode('utf-8')]
                cursor2.execute(sql2, parm2)
                conn2.commit()
            else:
                print "Is have"
