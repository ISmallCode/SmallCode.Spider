# coding=utf-8
import json
import os
import random
import sys
import time
import urllib
import urllib2
from sys import argv

import MySQLdb

from fun import settings

reload(sys)
sys.setdefaultencoding('utf8')

conn = MySQLdb.connect(host="118.192.146.104", user='vister', passwd='sc!@#123', db='nw', port=3388, charset='utf8')
cursor = conn.cursor()
ISOTIMEFORMAT = '%Y-%m-%d %X'

def main(member_id, page=1, index=0):
    try:
        member_url = 'http://worldcosplay.net/en/api/member/photos?member_id=%s&page=%s&limit=100000&rows=16&p3_photo_list=1' % (
        member_id, page)
        r = urllib2.urlopen(member_url)

        if r.code == 200:
            data = json.loads(r.read())
            if data['has_error'] != 0:
                print u'接口挫了'
                pass

            photo_data_list = data['list']
            if not photo_data_list:
                if (index == 0):
                    index = 1
                if (page == 0):
                    page = 1
                print u'没东西了？第 %s 页，共下载了 %s 个图片' % (page - 1, index - 1)
                return 1
            else:
                for photo_data in photo_data_list:
                    url = photo_data['photo']['sq300_url']
                    subject = photo_data['photo']['subject']
                    description = str(photo_data['photo']['subject']).encode('utf-8') + "_" + str(photo_data['photo']['id'])
                    url = url.replace('/sq300', '')
                    subject = subject.replace('/', '_')
                    Path = settings.IMAGES_STORE + "/worldcosplay/" + member_id
                    file_name = member_id + "_" + str(index) + "_" + subject
                    if not os.path.exists(Path):
                        os.makedirs(Path)
                    filename = Path + "/" + file_name + ".jpg"

                    try:
                        if not os.path.isfile(filename):
                            urllib.urlretrieve(url, filename)
                        print u'下完了%s张' % (index + 1)
                        index += 1
                        img_path = '/Spider/worldcosplay/' + member_id + '/' + file_name + ".jpg"
                        insert_imge_info(subject, member_url, img_path, file_name, description)

                    except Exception, e:
                        print(u'这张图片下载出问题了： %s' % url)
                        print e

                page += 1
                main(member_id, page=page, index=index)
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
            insert_parm = [Title, Url, 'worldcosplay', datetime, description,6]
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
            parm = (file_title, Path, datetime, ImageThemeId, description,6)
            cursor.execute(sql, parm)
            conn.commit()
        else:
            sql = "Update image set Path=%s,ModifyDate=%s,ImageThemeId=%s,ModifyBy=$s where Title=%s"
            parm = (Path,datetime, ImageThemeId,6,file_title)
            cursor.execute(sql, parm)
            conn.commit()
    except MySQLdb.Error,e:
        string = "Mysql Error %d: %s" % (e.args[0], e.args[1])
        print string
        fout.write(string)
        conn.rollback()


if __name__ == '__main__':
    if len(argv) < 2:
        for i in range(0, 100):
            num = random.randint(10000, 100000)
            print num
            main(str(num), 1)
    else:
        member_id = argv[1]
        main(member_id, 1)
