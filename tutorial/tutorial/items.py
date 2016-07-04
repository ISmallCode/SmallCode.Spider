# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html
import scrapy
from scrapy.contrib.loader import ItemLoader
from scrapy.contrib.loader.processor import MapCompose, TakeFirst, Join

class TutorialItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass

class MyItemLoader(ItemLoader):
    default_input_processor = MapCompose(lambda s: s.strip())
    default_output_processor = TakeFirst()
    description_out = Join()

class DmozItem(scrapy.Item):
    title = scrapy.Field()
    url = scrapy.Field()
    category = scrapy.Field()
    body=scrapy.Field()
    browse = scrapy.Field()
    reply_count = scrapy.Field()
    table_name = scrapy.Field()
    source = scrapy.Field()
    label = scrapy.Field()
    author = scrapy.Field()


class UserItem(scrapy.Item):
    UserName = scrapy.Field()
    NickName = scrapy.Field()
    Fellow = scrapy.Field()
    Fans = scrapy.Field()
    Score = scrapy.Field()
    UserInfoUrl = scrapy.Field()
    UserWordUrl = scrapy.Field()
    Source = scrapy.Field()
    Description = scrapy.Field()
    Skill = scrapy.Field()
    Field = scrapy.Field()
    Email = scrapy.Field()
    Phone = scrapy.Field()
    QQ = scrapy.Field()
    Info = scrapy.Field()
    WeiXin = scrapy.Field()
    FunctionStyle = scrapy.Field()


class WordItem(scrapy.Item):
    Title = scrapy.Field()
    URL = scrapy.Field()
    Category = scrapy.Field()
    Description = scrapy.Field()
    Browses = scrapy.Field()
    ReplyCount = scrapy.Field()
    Source = scrapy.Field()
    Label = scrapy.Field()
    Author = scrapy.Field
    TableName = scrapy.Field()
    FunctionStyle = scrapy.Field()


class UpdateUserInfoItem(scrapy.Item):
    UserName = scrapy.Field()
    Source = scrapy.Field()
    Colunm = scrapy.Field()
    Data = scrapy.Field()
    FunctionStyle = scrapy.Field()
