import sys
import time
import psycopg2
import MySQLdb
import jieba
import pygal

from tutorial.function import common

reload(sys)
sys.setdefaultencoding('utf8')

ISOTIMEFORMAT = '%Y-%m-%d %X'
fout = open('except.txt', 'w')
conn = MySQLdb.connect(host="118.192.146.104", user='vister', passwd='sc!@#123', db='spider', port=3388,
                       charset='utf8')

conn1 = MySQLdb.connect(host="118.192.146.104", user='vister', passwd='sc!@#123', db='nw', port=3388,charset='utf8')
conn1=psycopg2.connect(database='smallcode',user="postgres", password="koala19920716", host="51newren.com", port="5432")
conn_text = MySQLdb.connect(host="118.192.146.104", user='vister', passwd='sc!@#123', db='test', port=3388,
                            charset='utf8')
def insert_city(self,name):
    cursor2 = conn_text.cursor()
    sql2 = "Insert into cities(name) VALUES (%s)"
    cursor2.execute(sql2, [name])
    conn_text.commit()

def insert_query(table_name, source, title, category, body, url, lable, authorname, reply=0, browse=0):
    datetime = time.strftime(ISOTIMEFORMAT, time.localtime())
    fenci_list = jieba.cut(title)
    fenci = "/ ".join(fenci_list)
    #conn.ping()
    cursor = conn.cursor()
    try:
        cursor.execute("select * from " + table_name + " where href =%s", [url])
        returnDate = cursor.fetchall()
        if (len(returnDate) == 0):
            cursor.execute("select * from label where name = %s", [category])
            result = cursor.fetchall()
            if (len(result) == 0):
                insert_sql = "Insert into label(name) VALUE (%s)"
                insert_parm = [category]
                cursor.execute(insert_sql, insert_parm)
                cursor.execute("select * from label where name = %s", [category])
                result = cursor.fetchall()
                label_id = result[0][0]
            else:
                label_id = result[0][0]
            sql = "Insert into " + table_name + " (title,datetime,label_id,text,href,browse) values (%s,%s,%s,%s,%s,%s)"
            parm = (title, datetime, label_id, body, url, browse)
            cursor.execute(sql, parm)
            conn.commit()
            print "Spider Insert"
        else:
            print "Is Have"
    except MySQLdb.Error, e:
        string = "Mysql Error %d: %s,Time:%s\n" % (e.args[0], e.args[1], time.strftime(ISOTIMEFORMAT, time.localtime()))
        fout.write(string)
        conn.rollback()
    #conn1.ping()
    cursor1 = conn1.cursor()
    try:
        cursor1.execute("select * from exarticleuser where UserName=%s and Source=%s",
                        [authorname, source])
        author = cursor1.fetchall()
        if (len(author) != 0):
            author_id = author[0][0]
        else:
            author_id = 0
        cursor1.execute("set global max_allowed_packet=524288000")
        cursor1.execute("select * from exarticletemp where URL = %s and Source=%s", [url,source])
        returnDate1 = cursor1.fetchall()
        if (len(returnDate1) == 0):
            cursor1.execute("set names utf8")
            conn1.commit()
            sql1 = "Insert into exarticletemp(Title,Description,Source,URL,ReplyCount,Category,Label,CreateDate,CreateBy,IsDelete,FenCi,AuthorId) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            parm1 = (title, body, source, url, reply, category, lable, datetime, 6, 0, fenci, author_id)
            cursor1.execute(sql1, parm1)
            conn1.commit()
            print "Nw Insert"
        else:
            print "Nw update"
            sql2 = "Update exarticletemp set ReplyCount=%s,ModifyDate=%s,ModifyBy=%s,Status=%s,FenCi=%s,Label=%s where URL=%s"
            parm2 = [reply, datetime, 6, 0, fenci, lable, url]
            cursor1.execute(sql2, parm2)
            conn1.commit()
       
    except MySQLdb.Error, e:
        string = "Mysql Error %d: %s,Time:%s\n" % (e.args[0], e.args[1], time.strftime(ISOTIMEFORMAT, time.localtime()))
        fout.write(string)
        conn1.rollback()
    cursor1.close()
    cursor.close()

def insert_item(item):
    datetime = time.strftime(ISOTIMEFORMAT, time.localtime())
    #conn1.ping()
    cursor1 = conn1.cursor()
    try:
        fenci_list = jieba.cut(item['title'])
        fenci = "/ ".join(fenci_list)
        cursor1.execute("select * from exarticleuser where UserName=%s and Source=%s",
                        [item["author"], item["source"]])
        author = cursor1.fetchall()
        if (len(author) != 0):
            author_id = author[0][0]
        else:
            author_id = 0
        cursor1.execute("set global max_allowed_packet=524288000")
        cursor1.execute("select * from exarticletemp where URL = %s and Source=%s", [item['url'],item['source']])
        returnDate1 = cursor1.fetchall()
        if (len(returnDate1) == 0):
            cursor1.execute("set names utf8")
            conn1.commit()
            sql1 = "Insert into exarticletemp(Title,Description,Source,URL,ReplyCount,Category,Label,CreateDate,CreateBy,IsDelete,FenCi,AuthorId) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            parm1 = (item['title'], item['body'], item['source'], item['url'], item['reply_count'], item['category'],
                     item['label'], datetime, 6, 0, fenci, author_id)
            cursor1.execute(sql1, parm1)
            conn1.commit()
            print "Nw Insert"
        else:
            print "Nw update"
            sql2 = "Update exarticletemp set ReplyCount=%s,ModifyDate=%s,ModifyBy=%s,Status=%s,FenCi=%s,Label=%s where URL=%s"
            parm2 = [item['reply_count'], datetime, 6, 0, fenci, item['label'], item['url']]
            cursor1.execute(sql2, parm2)
            conn1.commit()

    except MySQLdb.Error, e:
        string = "Mysql Error %d: %s,Time:%s\n" % (e.args[0], e.args[1], time.strftime(ISOTIMEFORMAT, time.localtime()))
        fout.write(string)
        conn1.rollback()
    cursor1.close()

def show_spider_num(data_name, table_name, column, source, where=''):
    datetime = time.strftime(ISOTIMEFORMAT, time.localtime())
    conn3 = MySQLdb.connect(host="118.192.146.104", user='vister', passwd='sc!@#123', db=data_name, port=3388,
                            charset='utf8')
    #conn3.ping()
    cursor3 = conn3.cursor()
    try:
        cursor3.execute(
            "select count(*) as num,FROM_UNIXTIME(UNIX_TIMESTAMP(" + column + "),'%Y-%m-%d') as time from " + table_name + " " + where + " group by TO_DAYS(" + column + ")")
        num = cursor3.fetchall()

        line_chart = pygal.Line()
        line_chart.title = 'Browser usage evolution (in %)'
        x_item = []
        y_item = []
        for item in num:
            x_item.append(item[1])
            y_item.append(int(item[0]))
        line_chart.x_labels = x_item
        line_chart.add(data_name + "_" + source, y_item)
        line_chart.render()
        common.send_mail(data_name + "_" + table_name, line_chart.render())
    except Exception, e:
        string = "Mysql Error %d: %s,Time:%s" % (e.args[0], e.args[1], time.strftime(ISOTIMEFORMAT, time.localtime()))
        fout.write(string)
        conn3.rollback()
    cursor3.close()
    conn3.close()

def insert_user(UserName, Fellow, Fans, Score, UserInfoUrl, Source, UserWordUrl, NickName, Description, Skill, Email,
                Phone, QQ, WeiXin, Field, Info):
    datetime = time.strftime(ISOTIMEFORMAT, time.localtime())
    try:
       # conn1.ping()
        cursor1 = conn1.cursor()
        print "Nw"
        count = select_user(UserInfoUrl, Source)
        if (count == 0):
            print "Insert"
            sql = "insert into EXArticleAuthor(UserName,Fellow,Fans,Score,UserInfoUrl,Source,UserWordUrl,NickName,Description,Skill,Email,Phone,QQ,WeiXin,Field,Info,CreateDate,CreateBy) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            #sql = "insert into EXArticleAuthor(CreateBy,CreateDate,Dscription,Email,Fans,Fellow,Field,Info,IsDelete) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)"
            parm = ['6b8c4186-c6c4-44b1-a1ff-3a47a53a5607',datetime,UserInfoUrl,Email,int(Fans),int(Fellow),Field,Info,0]
            cursor1.execute(sql, parm)
            conn1.commit()
        else:
            print "Update"
            cursor1.execute(
                    "Update EXArticleAuthor set Email=%s,Info=%s,Fellow=%s,Fans=%s,Field=%s,ModifyDate=%s,ModifyBy=%s where UserInfoUrl=%s",
                    [Email,Info,int(Fellow),int(Fans),Field,datetime,'6b8c4186-c6c4-44b1-a1ff-3a47a53a5607',UserInfoUrl])
            conn1.commit()
        cursor1.close()
    except MySQLdb.Error, e:
        string = "Error %s,Time:%s,Function:%s \n" % (
        "Mysql Error %d: %s" % (e.args[0], e.args[1]), datetime, "insert_user")
        fout.write(string)
        conn1.rollback()

def update_user_Info(UserName, Source, Colunm, Data):
    datetime = time.strftime(ISOTIMEFORMAT, time.localtime())
    try:
       #conn1.ping()
        cursor1 = conn1.cursor()
        cursor1.execute(
            "Update EXArticleAuthor set " + Colunm + "=%s,ModifyDate=%s,ModifyBy=%s where Source=%s and UserName=%s",
            [Data, datetime, 6, Source, UserName])
        conn1.commit()
        cursor1.close()
    except MySQLdb.Error, e:
        string = "Error %s,Time:%s,Function:%s \n" % (
        "Mysql Error %d: %s" % (e.args[0], e.args[1]), datetime, "update_user_info")
        fout.write(string)
        conn1.rollback()

def select_user(UserUrl, Source):
    datetime = time.strftime(ISOTIMEFORMAT, time.localtime())
    try:
        print 'yes'
        #conn1.ping()
        cursor1 = conn1.cursor()
        sql = "select Id from EXArticleAuthor where Dscription=%s"
        parm = [UserUrl]
        cursor1.execute(sql, parm)
        count = cursor1.fetchall()
        if (len(count) == 0):
            return 0
        else:
            return 1
        cursor1.close()
    except MySQLdb.Error, e:
        string = "Error %s,Time:%s,Function:%s \n" % (
        "Mysql Error %d: %s" % (e.args[0], e.args[1]), datetime, "select_user")
        fout.write(string)

def get_user_list(Style):
    datetime = time.strftime(ISOTIMEFORMAT, time.localtime())
    try:
        #conn1.ping()
        cursor1 = conn1.cursor()
        cursor1.execute("select Dscription from EXArticleAuthor")
        user_word_list = cursor1.fetchall()
        list = []
        for item in user_word_list:
            list.append(item)
        return list
        cursor1.close()
    except MySQLdb.Error, e:
        string = "Mysql Error %d: %s,Time:%s\n" % (e.args[0], e.args[1], time.strftime(ISOTIMEFORMAT, time.localtime()))
        fout.write(string)

def update_word_Info(URL, Browse):
    datetime = time.strftime(ISOTIMEFORMAT, time.localtime())
    try:
        #conn1.ping()
        cursor1 = conn1.cursor()
        cursor1.execute("Update exarticletemp set OldBrowses=%s,ModifyDate=%s,ModifyBy=%s where URL=%s",
                        [Browse, datetime, 6, URL])
        conn1.commit()
        cursor1.close()
    except MySQLdb.Error, e:
        string = "Mysql Error %d: %s,Time:%s\n" % (e.args[0], e.args[1], time.strftime(ISOTIMEFORMAT, time.localtime()))
        fout.write(string)
        conn1.rollback()
