# -*- coding: utf-8 -*-
import sys
import time

import scrapy
from scrapy.http import Request
from scrapy.selector import Selector

from tutorial.function import sql_helper

reload(sys)
sys.setdefaultencoding('utf8')


class JobboleSpider(scrapy.Spider):
    name = "jobbole"
    allowed_domains = ["jobbole.com"]
    start_urls = [
        "http://blog.jobbole.com"
    ]
    def __init__(self):
        self.i = 1
        self.fout = open('jobbole.txt', 'w')
        self.ISOTIMEFORMAT = '%Y-%m-%d %X'

    def parse(self, response):
        try:
            if (response.status != 404) and (response.status != 302) and (response.status != 502):
                sel = Selector(response)
                sites = sel.xpath(
                        "//*[@id='widgets-homepage-fullwidth']/div[@class='container']/div[@class='grid-4 floated-thumb']").extract()
                for site in sites:
                    body = Selector(text=site)
                    href = body.xpath("//div[@class='post-meta']/p/a[1]/@href").extract()
                    for url in href:
                        yield Request(callback=self.parse_word, meta={'referer': response.url}, url=url)
                sites_two = sel.xpath(
                        "//*[@id='widgets-homepage-fullwidth']/div[@class='container']/div[@class='grid-4 the-latest']").extract()
                for site in sites_two:
                    body = Selector(text=site)
                    href = body.xpath("//div[@class='post-title']/a/@href").extract()
                    for url in href:
                        yield Request(callback=self.parse_word, meta={'referer': response.url}, url=url)
                yield Request(callback=self.parse_all_posts, url='http://blog.jobbole.com/all-posts')
        except Exception, e:
            string = "Error %s,Url:%s,From:(jobbole,parse),Time=%s \n" % (
            e, response.url, time.strftime(self.ISOTIMEFORMAT, time.localtime()))
            self.fout.write(string)

    def parse_all_posts(self, response):
        try:
            if (response.status != 404) and (response.status != 302) and (response.status != 502):
                all_posts = Selector(response)
                posts = all_posts.xpath(
                    '//*[@id="archive"]/div[@class="post floated-thumb"]/div[@class="post-meta"]/p/a[1]/@href').extract()
                for post in posts:
                    yield Request(callback=self.parse_word, meta={'referer': response.url}, url=post)
                next_url = all_posts.xpath('//div[@class="next page-numbers"]/@href').extract()
                yield Request(callback=self.parse_all_posts, url=next_url[0])
        except Exception, e:
            string = "Error %s,Url:%s,From:(jobbole,parse_all_posts),Time:%s \n" % (
            e, response.url, time.strftime(self.ISOTIMEFORMAT, time.localtime()))
            self.fout.write(string)

    def parse_word(self, response):
        try:
            if (response.status != 404) and (response.status != 302) and (response.status != 502):
                sel = Selector(response)
                title = sel.xpath('//h1[@class="rpost-title"]/text()').extract()
                if (len(title) == 0):
                    title = sel.xpath('//h1[@class="p-tit-single"]/a/text()').extract()
                    if (len(title) == 0):
                        title = sel.xpath('//h1[@class="p-tit-single"]/text()').extract()
                        if (len(title) == 0):
                            title = sel.xpath('//div[@class="entry-header"]/h1/text()').extract()
                            if (len(title) == 0):
                                title = sel.xpath('//div[@class="entry-header"]/h1/span/text()').extract()
                                if (len(title) == 0):
                                    print response.url
                                    print "title"
                                else:
                                    body_list = sel.xpath('//div[@class="entry"]/p').extract()
                                    if (len(body_list) != 0):
                                        category = sel.xpath("//div[@class='p-nav']/span[2]/a/text()").extract()
                                        if (len(category) != 0):
                                            label = sel.xpath('//div[@class="p-meta"]/span[2]/a/text()').extract()
                                            reply_count = sel.xpath('//div[@class="post-adds"]/a/span/text()').extract()
                                            if (len(label) != 0):
                                                jobbole_lable = ""
                                                for n in label:
                                                    jobbole_lable += n + ","
                                                print "5"
                                            else:
                                                print "5"
                                                print response.url
                                                print "label"
                                                self.fout.write("<GET:" + response.url + ">(referer:" + response.meta[
                                                    'referer'] + "),Error:label_5 \n")
                                                jobbole_lable = ""

                                        else:
                                            print "5"
                                            print response.url
                                            print "category"
                                            self.fout.write("<GET:" + response.url + ">(referer:" + response.meta[
                                                'referer'] + "),Error:category_5 \n")
                                    else:
                                        print "5"
                                        print response.url
                                        print "body"
                                        self.fout.write("<GET:" + response.url + ">(referer:" + response.meta[
                                            'referer'] + "),Error:body_5 \n")
                            else:
                                body_list = sel.xpath('//div[@class="entry"]/*').extract()
                                if (len(body_list) != 0):
                                    category = sel.xpath("//div[@class='breadcrumb-wrapper']/a[4]/text()").extract()
                                    if (len(category) != 0):
                                        label = sel.xpath(
                                                '//div[@class="entry-meta"]/p/a[contains(@href,"tag")]/text()').extract()
                                        reply_count = 0
                                        if (len(label) != 0):
                                            jobbole_lable = ""
                                            for n in label:
                                                jobbole_lable += n + ","
                                            print "4"
                                        else:
                                            jobbole_lable = ""
                                            print "4"
                                            print response.url
                                            print "label"
                                            self.fout.write("<GET:" + response.url + ">(referer:" + response.meta[
                                                'referer'] + "),Error:label_4 \n")
                                    else:
                                        print "4"
                                        print response.url
                                        print "category"
                                        self.fout.write("<GET:" + response.url + ">(referer:" + response.meta[
                                            'referer'] + "),Error:category_4 \n")
                                else:
                                    print "4"
                                    print response.url
                                    print "body"
                                    self.fout.write("<GET:" + response.url + ">(referer:" + response.meta[
                                        'referer'] + "),Error:body_4 \n")
                        else:
                            body_list = sel.xpath('//div[@class="p-entry"]/*').extract()
                            if (len(body_list) != 0):
                                category = sel.xpath("//div[@class='p-nav']/span[2]/a/text()").extract()
                                if (len(category) != 0):
                                    label = sel.xpath(
                                            '//p[@class="p-meta"]/span[@class="hide-on-480"]/a/text()').extract()
                                    reply_count = 0
                                    if (len(label) != 0):
                                        jobbole_lable = ""
                                        for n in label:
                                            jobbole_lable += n + ","
                                        print "3"

                                    else:
                                        print "3"
                                        print response.url
                                        print "label"
                                        jobbole_lable = ""
                                        self.fout.write("<GET:" + response.url + ">(referer:" + response.meta[
                                            'referer'] + "),Error:label_3 \n")
                                else:
                                    print "3"
                                    print response.url
                                    print "category"
                                    self.fout.write("<GET:" + response.url + ">(referer:" + response.meta[
                                        'referer'] + "),Error:category_3 \n")
                            else:
                                print "3"
                                print response.url
                                print "body"
                                self.fout.write(
                                        "<GET:" + response.url + ">(referer:" + response.meta[
                                            'referer'] + "),Error:body_3 \n")
                    else:
                        body_list = sel.xpath('//div[@class="p-entry"]/*').extract()
                        if (len(body_list) != 0):
                            category = sel.xpath("//p[@class='p-meta']/span[2]/a/text()").extract()
                            if (len(category) != 0):
                                label = sel.xpath('//span[@class="hide-on-480"]/a/text()').extract()
                                reply_count = sel.xpath(
                                        "//p[@class='p-meta']/span/a[contains(@href,'#comments')]/text()").extract()
                                if (len(label) != 0):
                                    jobbole_lable = ""
                                    for n in label:
                                        jobbole_lable += n + ","
                                    print "2"
                                else:
                                    print "2"
                                    print response.url
                                    print "label"
                                    jobbole_lable = ""
                                    self.fout.write("<GET:" + response.url + ">(referer:" + response.meta[
                                        'referer'] + "),Error:label_2 \n")
                            else:
                                print "2"
                                print response.url
                                print "category"
                                self.fout.write("<GET:" + response.url + ">(referer:" + response.meta[
                                    'referer'] + "),Error:category_2 \n")
                        else:
                            print "2"
                            print response.url
                            print "body"
                            self.fout.write(
                                    "<GET:" + response.url + ">(referer:" + response.meta[
                                        'referer'] + "),Error:body_2 \n")
                else:
                    body_list = sel.xpath('//div[@class="rpost-body"]/p').extract()
                    if (len(body_list) != 0):
                        category = sel.xpath("//ol[@class='breadcrumb']/li[3]/a/text()").extract()
                        if (len(category) != 0):
                            label = sel.xpath('//div[@class="p-meta"]/span/a/text()').extract()
                            reply_count = 0
                            if (len(label) != 0):
                                jobbole_lable = ""
                                for n in label:
                                    jobbole_lable += n + ","
                                print "1"
                            else:
                                print "1"
                                print response.url
                                print "label"
                                jobbole_lable = ""
                                self.fout.write("<GET:" + response.url + ">(referer:" + response.meta[
                                    'referer'] + "),Error:label_1_1 \n")
                        else:
                            category = sel.xpath("//ol[@class='breadcrumb']/li[2]/a/text()").extract()
                            if (len(category) != 0):
                                label = sel.xpath('//div[@class="p-meta"]/span/a/text()').extract()
                                reply_count = 0
                                if (len(label) != 0):
                                    jobbole_lable = ""
                                    for n in label:
                                        jobbole_lable += n + ","
                                    print "1"
                                else:
                                    print "1"
                                    print response.url
                                    print "label"
                                    self.fout.write("<GET:" + response.url + ">(referer:" + response.meta[
                                        'referer'] + "),Error:label_1_2 \n")
                                    jobbole_lable = ""
                            else:
                                print "1"
                                print response.url
                                print "category"
                                self.fout.write("<GET:" + response.url + ">(referer:" + response.meta[
                                    'referer'] + "),Error:category_1 \n")
                    else:
                        print "1"
                        print response.url
                        print "body"
                        self.fout.write(
                                "<GET:" + response.url + ">(referer:" + response.meta['referer'] + "),Error:body_1 \n")

                jobbole_reply = self.getReplyCount(reply_count)
                jobbole_title = str(title[0]).encode('utf-8').strip()
                jobbole_category = str(category[0]).encode('utf-8').strip()

                jobbole_body = ""
                for word in body_list:
                    jobbole_body = jobbole_body + str(word).encode('utf-8')
                sql_helper.insert_query("jobbole", "伯乐在线", jobbole_title, jobbole_category, jobbole_body, response.url,
                                        jobbole_lable, "", jobbole_reply, 0)
        except Exception, e:
            string = "Error %s \n" % (e)
            print string
            referer = response.meta['referer']
            self.fout.write(
                "<GET:" + response.url + ">(referer:" + referer + "),From:(jobbole,parse_all_posts)," + string + "Time:" + time.strftime(
                    self.ISOTIMEFORMAT, time.localtime()))
            # if (response.status != 404) and (response.status != 302) and (response.status != 502):
            #     sel = Selector(response)
            #     title = sel.xpath('//h1[@class="rpost-title"]/text()').extract()
            #     if (len(title) == 0):
            #         title = sel.xpath('//h1[@class="p-tit-single"]/a/text()').extract()
            #         if (len(title) == 0):
            #             title = sel.xpath('//h1[@class="p-tit-single"]/text()').extract()
            #             if (len(title) == 0):
            #                 title = sel.xpath('//div[@class="entry-header"]/h1/text()').extract()
            #                 if (len(title) == 0):
            #                     title = sel.xpath('//div[@class="entry-header"]/h1/span/text()').extract()
            #                     if (len(title) == 0):
            #                         print response.url
            #                         print "title"
            #                     else:
            #                         body_list = sel.xpath('//div[@class="entry"]/p').extract()
            #                         if (len(body_list) != 0):
            #                             category = sel.xpath("//div[@class='p-nav']/span[2]/a/text()").extract()
            #                             if (len(category) != 0):
            #                                 label = sel.xpath('//div[@class="p-meta"]/span[2]/a/text()').extract()
            #                                 reply_count = sel.xpath('//div[@class="post-adds"]/a/span/text()').extract()
            #                                 if (len(label) != 0):
            #                                     jobbole_lable = ""
            #                                     for n in label:
            #                                         jobbole_lable += n + ","
            #                                     print "5"
            #                                 else:
            #                                     print "5"
            #                                     print response.url
            #                                     print "label"
            #                                     self.fout.write("<GET:" + response.url + ">(referer:" + response.meta[
            #                                         'referer'] + "),Error:label_5 \n")
            #                                     jobbole_lable = ""
            #
            #                             else:
            #                                 print "5"
            #                                 print response.url
            #                                 print "category"
            #                                 self.fout.write("<GET:" + response.url + ">(referer:" + response.meta[
            #                                         'referer'] + "),Error:category_5 \n")
            #                         else:
            #                             print "5"
            #                             print response.url
            #                             print "body"
            #                             self.fout.write("<GET:" + response.url + ">(referer:" + response.meta[
            #                                     'referer'] + "),Error:body_5 \n")
            #                 else:
            #                     body_list = sel.xpath('//div[@class="entry"]/*').extract()
            #                     if (len(body_list) != 0):
            #                         category = sel.xpath("//div[@class='breadcrumb-wrapper']/a[4]/text()").extract()
            #                         if (len(category) != 0):
            #                             label = sel.xpath(
            #                                         '//div[@class="entry-meta"]/p/a[contains(@href,"tag")]/text()').extract()
            #                             reply_count = 0
            #                             if (len(label) != 0):
            #                                 jobbole_lable = ""
            #                                 for n in label:
            #                                     jobbole_lable += n + ","
            #                                 print "4"
            #                             else:
            #                                 jobbole_lable = ""
            #                                 print "4"
            #                                 print response.url
            #                                 print "label"
            #                                 self.fout.write("<GET:" + response.url + ">(referer:" + response.meta[
            #                                         'referer'] + "),Error:label_4 \n")
            #                         else:
            #                             print "4"
            #                             print response.url
            #                             print "category"
            #                             self.fout.write("<GET:" + response.url + ">(referer:" + response.meta[
            #                                     'referer'] + "),Error:category_4 \n")
            #                     else:
            #                         print "4"
            #                         print response.url
            #                         print "body"
            #                         self.fout.write("<GET:" + response.url + ">(referer:" + response.meta[
            #                                 'referer'] + "),Error:body_4 \n")
            #             else:
            #                 body_list = sel.xpath('//div[@class="p-entry"]/*').extract()
            #                 if (len(body_list) != 0):
            #                     category = sel.xpath("//div[@class='p-nav']/span[2]/a/text()").extract()
            #                     if (len(category) != 0):
            #                         label = sel.xpath(
            #                                     '//p[@class="p-meta"]/span[@class="hide-on-480"]/a/text()').extract()
            #                         reply_count = 0
            #                         if (len(label) != 0):
            #                             jobbole_lable = ""
            #                             for n in label:
            #                                 jobbole_lable += n + ","
            #                             print "3"
            #
            #                         else:
            #                             print "3"
            #                             print response.url
            #                             print "label"
            #                             jobbole_lable = ""
            #                             self.fout.write("<GET:" + response.url + ">(referer:" + response.meta[
            #                                     'referer'] + "),Error:label_3 \n")
            #                     else:
            #                         print "3"
            #                         print response.url
            #                         print "category"
            #                         self.fout.write("<GET:" + response.url + ">(referer:" + response.meta[
            #                                 'referer'] + "),Error:category_3 \n")
            #                 else:
            #                     print "3"
            #                     print response.url
            #                     print "body"
            #                     self.fout.write(
            #                                 "<GET:" + response.url + ">(referer:" + response.meta[
            #                                     'referer'] + "),Error:body_3 \n")
            #         else:
            #             body_list = sel.xpath('//div[@class="p-entry"]/*').extract()
            #             if (len(body_list) != 0):
            #                 category = sel.xpath("//p[@class='p-meta']/span[2]/a/text()").extract()
            #                 if (len(category) != 0):
            #                     label = sel.xpath('//span[@class="hide-on-480"]/a/text()').extract()
            #                     reply_count = sel.xpath(
            #                                 "//p[@class='p-meta']/span/a[contains(@href,'#comments')]/text()").extract()
            #                     if (len(label) != 0):
            #                         jobbole_lable = ""
            #                         for n in label:
            #                             jobbole_lable += n + ","
            #                         print "2"
            #                     else:
            #                         print "2"
            #                         print response.url
            #                         print "label"
            #                         jobbole_lable = ""
            #                         self.fout.write("<GET:" + response.url + ">(referer:" + response.meta[
            #                                 'referer'] + "),Error:label_2 \n")
            #                 else:
            #                     print "2"
            #                     print response.url
            #                     print "category"
            #                     self.fout.write("<GET:" + response.url + ">(referer:" + response.meta[
            #                             'referer'] + "),Error:category_2 \n")
            #             else:
            #                 print "2"
            #                 print response.url
            #                 print "body"
            #                 self.fout.write(
            #                             "<GET:" + response.url + ">(referer:" + response.meta[
            #                                 'referer'] + "),Error:body_2 \n")
            #     else:
            #         body_list = sel.xpath('//div[@class="rpost-body"]/p').extract()
            #         if (len(body_list) != 0):
            #             category = sel.xpath("//ol[@class='breadcrumb']/li[3]/a/text()").extract()
            #             if (len(category) != 0):
            #                 label = sel.xpath('//div[@class="p-meta"]/span/a/text()').extract()
            #                 reply_count = 0
            #                 if (len(label) != 0):
            #                     jobbole_lable = ""
            #                     for n in label:
            #                         jobbole_lable += n + ","
            #                     print "1"
            #                 else:
            #                     print "1"
            #                     print response.url
            #                     print "label"
            #                     jobbole_lable = ""
            #                     self.fout.write("<GET:" + response.url + ">(referer:" + response.meta[
            #                             'referer'] + "),Error:label_1_1 \n")
            #             else:
            #                 category = sel.xpath("//ol[@class='breadcrumb']/li[2]/a/text()").extract()
            #                 if (len(category) != 0):
            #                     label = sel.xpath('//div[@class="p-meta"]/span/a/text()').extract()
            #                     reply_count = 0
            #                     if (len(label) != 0):
            #                         jobbole_lable = ""
            #                         for n in label:
            #                             jobbole_lable += n + ","
            #                         print "1"
            #                     else:
            #                         print "1"
            #                         print response.url
            #                         print "label"
            #                         self.fout.write("<GET:" + response.url + ">(referer:" + response.meta[
            #                                 'referer'] + "),Error:label_1_2 \n")
            #                         jobbole_lable = ""
            #                 else:
            #                     print "1"
            #                     print response.url
            #                     print "category"
            #                     self.fout.write("<GET:" + response.url + ">(referer:" + response.meta[
            #                             'referer'] + "),Error:category_1 \n")
            #         else:
            #             print "1"
            #             print response.url
            #             print "body"
            #             self.fout.write(
            #                         "<GET:" + response.url + ">(referer:" + response.meta['referer'] + "),Error:body_1 \n")
            #
            #     jobbole_reply = self.getReplyCount(reply_count)
            #     jobbole_title = str(title[0]).encode('utf-8').strip()
            #     jobbole_category = str(category[0]).encode('utf-8').strip()
            #
            #     jobbole_body = ""
            #     for word in body_list:
            #         jobbole_body = jobbole_body + str(word).encode('utf-8')
            #     sql_helper.insert_query("jobbole", "伯乐在线", jobbole_title, jobbole_category, jobbole_body, response.url,
            #                                 jobbole_lable, jobbole_reply, 0)

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.fout.close()

    def getReplyCount(self, replynum):
        if (replynum == 0):
            return 0
        else:
            return str(replynum[0]).strip(' 评论')