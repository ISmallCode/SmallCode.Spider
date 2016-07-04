# coding=utf-8
import sys
import time

import MySQLdb
import pygal
from pygal.style import DefaultStyle

from tutorial.function import common

reload(sys)
sys.setdefaultencoding('utf8')

ISOTIMEFORMAT = '%Y-%m-%d %X'
datetime = time.strftime(ISOTIMEFORMAT, time.localtime())

conn = MySQLdb.connect(host="118.192.146.104", user='vister', passwd='sc!@#123', db='nw', port=3388, charset='utf8')
cursor = conn.cursor()
cursor.execute(
    "select count(*),FROM_UNIXTIME(UNIX_TIMESTAMP(CreateDate),'%Y-%m-%d') from exarticletemp where to_days(CreateDate)=to_days(now())")
insert_exarticletemp_num = cursor.fetchall()
cursor.execute(
    "select count(*),FROM_UNIXTIME(UNIX_TIMESTAMP(ModifyDate),'%Y-%m-%d') from exarticletemp where to_days(ModifyDate)=to_days(now())")
update_exarticletemp_num = cursor.fetchall()
cursor.execute(
    "select count(*),FROM_UNIXTIME(UNIX_TIMESTAMP(CreateDate),'%Y-%m-%d') from image where to_days(CreateDate)=to_days(now())")
insert_img_num = cursor.fetchall()
cursor.execute(
    "select count(*),FROM_UNIXTIME(UNIX_TIMESTAMP(ModifyDate),'%Y-%m-%d') from image where to_days(ModifyDate)=to_days(now())")
update_img_num = cursor.fetchall()
cursor.execute(
    "select count(*),FROM_UNIXTIME(UNIX_TIMESTAMP(CreateDate),'%Y-%m-%d') from exarticle where to_days(CreateDate)=to_days(now())")
insert_exarticle_num = cursor.fetchall()
cursor.execute(
    "select count(*),FROM_UNIXTIME(UNIX_TIMESTAMP(ModifyDate),'%Y-%m-%d') from exarticle where to_days(ModifyDate)=to_days(now())")
update_exarticle_num = cursor.fetchall()
cursor.execute(
    "SELECT count(1) from (SELECT Ip,Count(1) from log where DATE_FORMAT(CreateDate,'%Y-%m-%d') =date(NOW())  GROUP BY Ip ) as A")
ip_num = cursor.fetchall()

Date1 = insert_exarticletemp_num[0][1]
Number1 = insert_exarticletemp_num[0][0]
Date2 = update_exarticletemp_num[0][1]
Number2 = update_exarticletemp_num[0][0]

Date3 = insert_img_num[0][1]
Number3 = insert_img_num[0][0]
Date4 = update_img_num[0][1]
Number4 = update_img_num[0][0]

Date5 = insert_exarticle_num[0][1]
Number5 = insert_exarticle_num[0][0]
Date6 = update_exarticle_num[0][1]
Number6 = update_exarticle_num[0][0]

Ip_Number = ip_num[0][0]

cursor.execute("select * from exarticleamountstat where Day=%s", [Date1])
returnDate1 = cursor.fetchall()
if (len(returnDate1) == 0):
    sql = "Insert into exarticleamountstat(Day,Number,Type,CreateBy,CreateDate) values (%s,%s,%s,%s,%s)"
    parm1 = (Date1, Number1, "exarticletemp_insert", 6, time.strftime(ISOTIMEFORMAT, time.localtime()))
    parm2 = (Date1, Number2, "exarticletemp_update", 6, time.strftime(ISOTIMEFORMAT, time.localtime()))
    parm3 = (Date1, Number3, "image_insert", 6, time.strftime(ISOTIMEFORMAT, time.localtime()))
    parm4 = (Date1, Number4, "image_update", 6, time.strftime(ISOTIMEFORMAT, time.localtime()))
    parm5 = (Date1, Number5, "exarticle_insert", 6, time.strftime(ISOTIMEFORMAT, time.localtime()))
    parm6 = (Date1, Number6, "exarticle_update", 6, time.strftime(ISOTIMEFORMAT, time.localtime()))
    parm7 = (Date1, Ip_Number, "Ip_Number", 6, time.strftime(ISOTIMEFORMAT, time.localtime()))
    args = [parm1, parm2, parm3, parm4, parm5, parm6, parm7]
    cursor.executemany(sql, args)
    conn.commit()
else:
    sql = "Update exarticleamountstat set Number=%s,ModifyBy=%s,ModifyDate=%s where Day=%s and Type=%s"
    parm1 = (Number1, 6, time.strftime(ISOTIMEFORMAT, time.localtime()), Date1, "exarticletemp_insert")
    parm2 = (Number2, 6, time.strftime(ISOTIMEFORMAT, time.localtime()), Date1, "exarticletemp_update")
    parm3 = (Number3, 6, time.strftime(ISOTIMEFORMAT, time.localtime()), Date1, "image_insert")
    parm4 = (Number4, 6, time.strftime(ISOTIMEFORMAT, time.localtime()), Date1, "image_update")
    parm5 = (Number5, 6, time.strftime(ISOTIMEFORMAT, time.localtime()), Date1, "exarticle_insert")
    parm6 = (Number6, 6, time.strftime(ISOTIMEFORMAT, time.localtime()), Date1, "exarticle_update")
    parm7 = (Ip_Number, 6, time.strftime(ISOTIMEFORMAT, time.localtime()), Date6, "Ip_Number")
    args = [parm1, parm2, parm3, parm4, parm5, parm6, parm7]
    cursor.executemany(sql, args)
    conn.commit()


cursor.execute(
    "select Number,FROM_UNIXTIME(UNIX_TIMESTAMP(Day),'%Y-%m-%d') from exarticleamountstat where Type='exarticletemp_update' group by TO_DAYS(Day)")
num1 = cursor.fetchall()
cursor.execute(
    "select Number,FROM_UNIXTIME(UNIX_TIMESTAMP(Day),'%Y-%m-%d') from exarticleamountstat where Type='exarticletemp_insert' group by TO_DAYS(Day)")
num2 = cursor.fetchall()
line_chart = pygal.Line(style=DefaultStyle)
line_chart.title = time.strftime(ISOTIMEFORMAT, time.localtime()) + " " + u'爬虫统计'
x_item = []
y_item1 = []
y_item2 = []
for item in num1:
    x_item.append(item[1])
    y_item1.append(int(item[0]))
for item in num2:
    y_item2.append(int(item[0]))
line_chart.x_labels = x_item
line_chart.add('update', y_item1)
line_chart.add('insert', y_item2)
line_chart.render(is_unicode=True)
print common.send_mail('ismallcode(小码代码)，今日爬虫统计',
                       '今日更新文章数量：' + str(Number2) + "<br/>" + "今日增加文章数量：" + str(Number1) + "<br/>今日增加图片数量：" + str(
                           Number3) + "<br/>今日更新图片数量：" + str(Number4) + "<br/>今日增加正式文章数量：" + str(
                           Number5) + "<br/>今日修改正式文章数量：" + str(Number6) + "<br/>访客数：" + str(
                           Ip_Number) + line_chart.render(),
                       0)
