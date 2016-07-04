# -*- coding: utf-8 -*-
from tutorial.function import sql_helper

sql_helper.show_spider_num("spider", "oschina", "datetime", '开源中国')
sql_helper.show_spider_num("nw", "exarticletemp", "CreateDate", '开源中国', "where Source='开源中国'")

sql_helper.show_spider_num("spider", "csdn", "datetime", 'CSDN')
sql_helper.show_spider_num("nw", "exarticletemp", "CreateDate", 'CSDN', "where Source='CSDN'")

sql_helper.show_spider_num("spider", "will", "datetime", "月光博客")
sql_helper.show_spider_num("nw", "exarticletemp", "CreateDate", "月光博客", "where Source='月光博客'")

sql_helper.show_spider_num("spider", "jobbole", "datetime", "伯乐在线")
sql_helper.show_spider_num("nw", "exarticletemp", "CreateDate", "伯乐在线", "where Source='伯乐在线'")
