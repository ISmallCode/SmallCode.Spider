# -*- coding: utf-8 -*-
import json
import random
import sys

import scrapy
from scrapy.crawler import CrawlerRunner
from scrapy.http import FormRequest
from scrapy.http import Request
from scrapy.selector import Selector
from scrapy.utils.log import configure_logging
from twisted.internet import reactor

from tutorial.function import sql_helper
from tutorial.items import UpdateUserInfoItem
from tutorial.items import UserItem
from tutorial.spiders.csdn_word import CsdnWordSpider

reload(sys)
sys.setdefaultencoding('utf8')


class CsdnUserSpider(scrapy.Spider):
    name = "csdn_user"
    allowed_domains = ["blog.csdn.net"]
    start_urls = (
        'http://blog.csdn.net',
    )

    def __init__(self, *args):
        self.args = args
        self.page_info = ""
        self.fout = open('csdn_user.txt', 'w')
        self.fout2 = open('csdn_user_url.txt', 'w')
        self.j = 0
        self.k = 0
        self.i = 0
        self.m = 0
        self.n = 0
        self.o = 0
        self.p = 0
        self.q = 0
        self.page_num = 0
        self.page_num2 = 0
        self.source = "CSDN"

    def parse(self, response):
        self.j = self.j + 1
        try:
            sel = Selector(response)
            alive_links = sel.xpath('//dl[@class="alive_user"]/dt/a/@href').extract()
            for alive_item in alive_links:
                link_url = alive_item
                if (sql_helper.select_user(link_url, self.source) == 0):
                    yield Request(callback=self.parse_user, url=link_url, dont_filter=True)
            experts_links = sel.xpath('//dl[@class="experts"]/dd/ul/li/a/@href').extract()
            for experts_item in experts_links:
                link_url = experts_item
                if (sql_helper.select_user(link_url, self.source) == 0):
                    yield Request(callback=self.parse_user, url=link_url, dont_filter=True)
            yield Request(callback=self.parse_user_list, url="http://blog.csdn.net/honour/experts.html",
                          dont_filter=True)
            yield Request(callback=self.parse_user_expert,
                          url="http://my.csdn.net/my/my/chenge_expert/" + str(random.randint(0, 120)),
                          dont_filter=True)
        except Exception, e:
            string = "Error %s,Url:%s,From=%s \n" % (e, response.url, "csdn_user,parse")
            self.fout.write(string)

    def parse_user_expert(self, response):
        try:
            data = json.loads(response.body)
            for item in data['info']:
                url = "http://my.csdn.net/" + str(item['username'])
                if (sql_helper.select_user(url, self.source) == 0):
                    yield Request(callback=self.parse_user_info, url=url, dont_filter=True,
                                  meta={"refer": response.url})
        except Exception, e:
            string = "Error %s,Url:%s,From=%s \n" % (e, response.url, "csdn_user,parse_user_expert")
            self.fout.write(string)
    def parse_user_list(self, response):
        self.n = self.n + 1
        try:
            sel = Selector(response)
            user_list = sel.xpath('//ul[@class="list_4"]/li/a/@href').extract()
            for user_item in user_list:
                yield Request(callback=self.parse_user, url=user_item, dont_filter=True)
        except Exception, e:
            string = "Error %s,Url:%s,From=%s \n" % (e, response.url, "csdn,parse_user_list")
            self.fout.write(string)

    def parse_user(self, response):
        self.k = self.k + 1
        try:
            url = response.url
            UserName = str(url).split("http://blog.csdn.net/")[1]
            yield Request(callback=self.parse_user_info, url="http://my.csdn.net/" + UserName, dont_filter=True,
                          meta={"refer": response.url})
        except Exception, e:
            string = "Error %s,Url:%s,From:(csdn_user,parse_user), \n" % (e, response.url)
            self.fout.write(string)

    def parse_user_info(self, response):
        self.i = self.i + 1
        print str(self.j) + "_" + str(self.k) + "_" + str(self.m) + "_" + str(self.n) + "_" + str(self.i) + "_" + str(
            self.o) + "_" + str(self.p) + "_" + str(self.q)
        try:
            sel = Selector(response)
            fellow = sel.xpath('//div[@class="person_info_con"]/dl[1]/dd[1]/b/text()').extract()
            if (len(fellow) != 0):
                Info = ""
                detail = sel.xpath("string(//dd[@class='person-detail'])").extract()[0]
                for item in str(detail).split("|"):
                    Info += str(item).strip() + "|"
                UserInfoUrl = response.url
                UserName = str(UserInfoUrl).split("http://my.csdn.net/")[1].encode("utf-8")
                item = UserItem()
                sel = Selector(response)
                item['UserName'] = UserName
                item['NickName'] = sel.xpath('//dt[@class="person-nick-name"]/span/text()').extract()[0]
                item['Info'] = Info
                item['UserWordUrl'] = str("http://blog.csdn.net/") + str(UserName)
                item['UserInfoUrl'] = UserInfoUrl
                item['Fellow'] = int(fellow[0])
                item['Fans'] = int(sel.xpath('//div[@class="person_info_con"]/dl[1]/dd[2]/b/text()').extract()[0])
                item['Source'] = self.source
                item['Score'] = 0
                item['Description'] = sel.xpath('//dd[@class="person-sign"]/text()').extract()[0]
                item['Skill'] = ""
                item['Email'] = ""
                item['Phone'] = ""
                item['QQ'] = ""
                item['WeiXin'] = ""
                item['Field'] = ""
                item['FunctionStyle'] = "InsertUser"
                sql_helper.insert_user(item['UserName'], item['Fellow'], item['Fans'], item['Score'],
                                       item['UserInfoUrl'],
                                       item['Source'], item['UserWordUrl'], item['NickName'], item['Description'],
                                       item['Skill'], item['Email'], item['Phone'], item['QQ'], item['WeiXin'],
                                       item['Field'], item['Info'])
            else:
                self.fout2.write(response.url + "\n")
        except Exception, e:
            string = "Error %s,Url:%s,From=%s \n" % (e, response.url, "csdn_user,parse_user_info")
            self.fout.write(string)
        yield FormRequest(url="http://my.csdn.net/service/main/uc",
                          formdata={'username': UserName, "method": "getSkill"},
                          callback=self.user_skill, method={"username": UserName})
        yield FormRequest(url="http://my.csdn.net/service/main/uc",
                          formdata={'username': UserName, "method": "getContact"},
                          callback=self.user_contact, method={"username": UserName})
        yield Request(url="http://my.csdn.net/service/main/get_knownarea_list?username=" + UserName,
                      dont_filter=True, callback=self.user_field, method={"username": UserName})
        yield Request(url="http://my.csdn.net/service/main/get_knownarea_list?username=" + UserName,
                      callback=self.user_field, dont_filter=True)
        yield Request(url="http://my.csdn.net/service/main/visited?username=" + UserName,
                      callback=self.user_visited, dont_filter=True)
        yield Request(url=response.url + "/follow", callback=self.user_follow, dont_filter=True)
        yield Request(url=response.url + "/follow/fans", callback=self.user_follow, dont_filter=True)

    def user_follow(self, respnse):
        sel = Selector(respnse)
        user_list = sel.xpath("//div[@class='list row']/div[@class='col-sm-6']/dl/dt/a/@href").extract()
        for user_item in user_list:
            user_href = "http://my.csdn.net" + user_item
            if (sql_helper.select_user(user_href, self.source) == 0):
                yield Request(callback=self.parse_user_info, url=user_href, dont_filter=True)
        next_href = sel.xpath('//a[@class="btn btn-xs btn-default btn-next"]/@href').extract()
        if (len(next_href) != 0):
            yield Request(callback=self.user_follow, url="http://my.csdn.net" + next_href[0], dont_filter=True)

    def user_visited(self, response):
        self.m = self.m + 1
        try:
            data = json.loads(response.body)
            if data['err'] != 0:
                print u'接口挫了'
                pass
            else:
                for user_item in data['result']['list']:
                    user_href = "http://my.csdn.net/" + user_item['username']
                    yield Request(callback=self.parse_user_info, url=user_href, dont_filter=True)
        except Exception, e:
            string = "Error %s,Url:%s,From:(csdn_user,user_visited), \n" % (e, response.url)
            self.fout.write(string)

    def user_field(self, response):
        self.o = self.o + 1
        field = ""
        sites = Selector(text=response.body)
        data = json.loads(sites.xpath("string()").extract())
        if (data['err'] != 0):
            print u'接口挫了'
        else:
            if(len(data['result'])!=0):
                try:
                    for item in data['result']:
                        field += str(item['name']).encode("utf-8") + ","
                    item = UpdateUserInfoItem()
                    item['UserName'] = response.method['username']
                    item['Source'] = "CSDN"
                    item['Colunm'] = "Field"
                    item['Data'] = field
                    item['FunctionStyle'] = "UpdateUserInfo"
                    sql_helper.update_user_Info(response.method['username'], "CSDN", "Field", field)

                except Exception, e:
                    string = "Error %s,Url:%s,From:(csdn_user,user_field), \n" % (e, response.url)
                    self.fout.write(string)

    def user_skill(self, response):
        self.p = self.p + 1
        try:
            skill = ""
            sites = Selector(text=response.body)
            data = json.loads(sites.xpath("string()").extract())
            if data['err'] != 0:
                print u'接口挫了'
            else:
                if(len(data['result'])!=0):
                    for item in data['result']:
                        skill += str(item['skillname']).encode("utf-8") + ","
                    item = UpdateUserInfoItem()
                    item['UserName'] = response.method['username']
                    item['Source'] = "CSDN"
                    item['Colunm'] = "Skill"
                    item['Data'] = skill
                    item['FunctionStyle'] = "UpdateUserInfo"
                    sql_helper.update_user_Info(response.method['username'], "CSDN", "Skill", skill)
        except Exception, e:
            string = "Error %s,Url:%s,From:(csdn_user,user_skill), \n" % (e, response.url)
            self.fout.write(string)

    def user_contact(self, response):
        self.q = self.q + 1
        contact = []
        sites = Selector(text=response.body)
        data = json.loads(sites.xpath("string()").extract())
        info = data['result']['contactinfo']
        if data['err'] != 0:
            print u'接口挫了'
        else:
            try:
                contact[0] = hasattr(info, 'pubemail') if str(info['pubemail']).encode("utf-8") else ""
                contact[1] = hasattr(info, 'submobile') if str(info['submobile']).encode("utf-8") else ""
                contact[2] = hasattr(info, '0') if str(info[0]['value']).encode("utf-8") else ""
                contact[3] = hasattr(info, '1') if str(info[1]['value']).encode("utf-8") else ""
                sql_helper.update_user_Info(response.method['username'], "CSDN", "Email", contact[0])
                sql_helper.update_user_Info(response.method['username'], "CSDN", "Phone", contact[1])
                sql_helper.update_user_Info(response.method['username'], "CSDN", "QQ", contact[2])
                sql_helper.update_user_Info(response.method['username'], "CSDN", "WeiXin", contact[3])
            except Exception, e:
                string = "Error %s,Url:%s,From:(csdn_user,user_contact), \n" % (e, response.url)
                self.fout.write(string)
    def __exit__(self, exc_type, exc_val, exc_tb):
        print str(self.i)
        self.fout.close()
        configure_logging()
        runner = CrawlerRunner()
        runner.crawl(CsdnWordSpider)
        reactor.stop()
        reactor.run()
