# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import codecs
import json
import time

from scrapy import signals
from scrapy.xlib.pydispatch import dispatcher

from tutorial.function import common
from tutorial.function import sql_helper


class CsdnblogPipeline(object):
    def __init__(self):
        self.file = codecs.open('CSDNBlog_data.json', mode='wb', encoding='utf-8')
        # signals.dispatcher.connect(self.spider_opened, signals.spider_opened)
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def process_item(self, item, spider):
        if 'title' in item:
            line = json.dumps(dict(item)) + "\n"
        self.file.write(line.decode('unicode_escape'))
        if (item['FunctionStyle'] == "InsertUser"):
            sql_helper.insert_user(item['UserName'], item['Fellow'], item['Fans'], item['Score'], item['UserInfoUrl'],
                                   item['Source'], item['UserWordUrl'], item['NickName'], item['Description'],
                                   item['Skill'], item['Email'], item['Phone'], item['QQ'], item['WeiXin'],
                                   item['Field'], item['Info'])
        elif (item['FuctionStyle'] == "InsertWord"):
            sql_helper.insert_query(item['TableName'], item['Source'], item['Title'], item['Category'],
                                    item['Description'], item['URL'], item['Lable'], item['ReplyCount'],
                                    item['Browses'], item['Author'])
        elif (item['FunctionStyle'] == "UpdateUserInfo"):
            sql_helper.update_user_Info(item['UserName'], item['Source'], item['Colunm'], item['Data'])
        elif (item['FunctionStyle']=="City"):
            sql_helper.insert_city(item['title'])
        return item
    def spider_closed(self, spider, reason):
        ISOTIMEFORMAT = '%Y-%m-%d %X'
        fout = open('pipelines.txt', 'w')
        try:
            self.file.close()
            word = ""
            f = open(spider.name+".txt", "r")
            lines = f.readlines()
            for line in lines:
                word += line + "<br>"
            f.close()
            #f2 = open("except.txt", "r")
            #lines = f2.readlines()
            #for line in lines:
            #    word += line + "<br>"
            #f2.close()
            if(len(word)!=0):
                common.send_mail(spider.name+"_"+reason + ",Error", word)
            else:
                common.send_mail(reason, spider.name + "_" + reason)
        except Exception as e:
            string = "Error: %s,Time:%s\n" % (e, time.strftime(ISOTIMEFORMAT, time.localtime()))
            fout.write(string)
