# coding=utf-8
import json
import math
import os
import sys
import time
import urllib
import urllib2
from sys import argv
from pprint import pprint
import MySQLdb

from fun import settings

reload(sys)
sys.setdefaultencoding('utf8')

conn = MySQLdb.connect(host="118.192.146.104", user='vister', passwd='sc!@#123', db='nw', port=3388, charset='utf8')
cursor = conn.cursor()
ISOTIMEFORMAT = '%Y-%m-%d %X'

def dump(obj):
  '''return a printable representation of an object for debugging'''
  newobj=obj
  if '__dict__' in dir(obj):
    newobj=obj.__dict__
    if ' object at ' in str(obj) and not newobj.has_key('__type__'):
      newobj['__type__']=str(obj)
    for attr in newobj:
      newobj[attr]=dump(newobj[attr])
  return newobj

def main(page, index, word):
    try:
        member_url = 'http://image.baidu.com/search/avatarjson?tn=resultjsonavatarnew&ie=utf-8&word=%s&rn=60&itg=0&z=0&fr=&width=&height=&lm=-1&ic=0&s=0&st=-1&pn=%s' % (
        word, page)
        r = urllib2.urlopen(member_url)

        if r.code == 200:
            try:
                data = json.loads(unicode(r.read()).encode('utf-8'))
                photo_data_list = data['imgs']
                if not photo_data_list:
                    print u'抓完了'
                    print u'没东西了？第 %s 页，共下载了 %s 个图片' % (int(math.ceil(page / 60)), index)
                    return 1
                else:
                    for photo_data in photo_data_list:
                        url = photo_data['objURL']
                        url_split=str(url).split(".");
                        subject = str(photo_data['fromURLHost']).split(".")[1]
                        description = unicode(photo_data['fromURLHost']).encode('utf-8') + "(from:" + unicode(
                            photo_data['fromURL']).encode('utf-8') + ")"
                        Path = settings.IMAGES_STORE + "/baidu/" + str(word).decode('utf-8').encode('gbk')
                        if (len(photo_data['fromPageTitle']) == 0):
                            file_name = subject + "_" + str(index)
                        else:
                            file_name = unicode(photo_data['fromPageTitle']).encode('utf-8').replace(" ", ",")
                        if not os.path.exists(Path):
                            os.makedirs(Path)
                        filename = Path + "/" + subject + "_" + str(index) +"."+url_split[len(url_split)-1]

                        try:
                            if not os.path.isfile(filename):
                                urllib.urlretrieve(url, filename)
                            print u'下完了%s张' % (index + 1)
                            index += 1
                            img_path = '/Spider/baidu/' + word + '/' + subject + "_" + str(index) + "."+url_split[len(url_split)-1]
                            insert_imge_info(subject, member_url, img_path, file_name, description)
                        except Exception, e:
                            print(u'这张图片下载出问题了： %s' % url)
                            print e
                    page += 60
                    main(page, index, word)
            except Exception, e:
                print u'挫了'
                print e
                pass
        elif r.code == 404:
            pass
        else:
            print u'挫了'
            pass
    except urllib2.HTTPError, e:
        print e
        pass


def insert_imge_info(Title, Url, Path, file_title, description):
    datetime = time.strftime(ISOTIMEFORMAT, time.localtime())
    fout = open('worldcosplay.txt', 'w')
    try:
        cursor.execute("select * from imagetheme where Title = %s", [Title])
        result = cursor.fetchall()
        if (len(result) == 0):
            insert_sql = "Insert into imagetheme(Title,Url,Source,CreateDate,Description,CreateBy) VALUE (%s,%s,%s,%s,%s,%s)"
            insert_parm = [Title, Url, 'worldcosplay', datetime, description, 6]
            cursor.execute(insert_sql, insert_parm)
            conn.commit()
            cursor.execute("select * from imagetheme where Title = %s", [Title])
            result = cursor.fetchall()
            ImageThemeId = result[0][0]
        else:
            ImageThemeId = result[0][0]
        cursor.execute("select * from image where Title = %s", [file_title])
        result1 = cursor.fetchall()
        if (len(result1) == 0):
            sql = "Insert into image (Title,Path,CreateDate,ImageThemeId,Description,CreateBy) values (%s,%s,%s,%s,%s,%s)"
            parm = (file_title, Path, datetime, ImageThemeId, description, 6)
            cursor.execute(sql, parm)
            conn.commit()
        else:
            sql = "Update image set Path=%s,ModifyDate=%s,ImageThemeId=%s,ModifyBy=%s where Title=%s"
            parm = (Path, datetime, ImageThemeId, 6, file_title)
            cursor.execute(sql, parm)
            conn.commit()
    except MySQLdb.Error, e:
        string = "Mysql Error %d: %s" % (e.args[0], e.args[1])
        print string
        fout.write(string)
        conn.rollback()


if __name__ == '__main__':
    if len(argv) < 2 :
        main(0,0,'美女')
    else:
        print argv[1]
        main(0,0,str(argv[1]).decode('gbk').encode('utf-8'))
