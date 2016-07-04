# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import os
import time

import MySQLdb
import requests

from fun import settings


class ImageDownloadPipeline(object):
    def process_item(self, item, spider):
        if 'image_urls' in item:
            images = []
            dir_path = '%s/%s' % (settings.IMAGES_STORE, spider.name)

            if not os.path.exists(dir_path):
                os.makedirs(dir_path)
            for image_item in item['image_urls']:
                us = image_item.split('/')[3:]
                image_file_name = '_'.join(us)
                file_path = '%s/%s' % (dir_path, image_file_name)

                images.append(file_path)
                subject = item['name']
                img_path = '%s/%s' % ('/Spider/' + spider.name, image_file_name)
                description = item['info']
                insert_imge_info(subject, description, item['url'], img_path, item['source'], spider.name)
                if not os.path.isfile(file_path):
                    with open(file_path, 'wb') as handle:
                        response = requests.get(image_item, stream=True)
                        for block in response.iter_content(1024):
                            if not block:
                                break
                            handle.write(block)
            item['images'] = images
        return item


def insert_imge_info(Title, Description, Url, Path, Source, SpiderName):
    fout = open(SpiderName + '.txt', 'w')
    conn = MySQLdb.connect(host="118.192.146.104", user='vister', passwd='sc!@#123', db='nw', port=3388, charset='utf8')
    cursor = conn.cursor()
    ISOTIMEFORMAT = '%Y-%m-%d %X'
    datetime = time.strftime(ISOTIMEFORMAT, time.localtime())
    try:
        cursor.execute("select * from imagetheme where Title = %s", [Title])
        result = cursor.fetchall()
        if (len(result) == 0):
            insert_sql = "Insert into imagetheme(Title,Description,Url,Source,CreateDate,CreateBy) VALUE (%s,%s,%s,%s,%s,%s)"
            insert_parm = [Title, Description, Url, Source, datetime,6]
            cursor.execute(insert_sql, insert_parm)
            conn.commit()
            cursor.execute("select * from imagetheme where Title = %s", [Title])
            result = cursor.fetchall()
            ImageThemeId = result[0][0]
            print ImageThemeId
        else:
            update_sql = "Update imagetheme set Title=%s,Description=%s,Source=%s,ModifyDate=%s,ModifyBy=%s where Url=%s"
            update_parm = [Title, Description, Source, datetime,6,Url]
            cursor.execute(update_sql, update_parm)
            conn.commit()
            ImageThemeId = result[0][0]
        cursor.execute("select * from image where Title = %s", [Title])
        result1 = cursor.fetchall()
        if (len(result1) == 0):
            sql = "Insert into image (Title,Description,Path,ImageThemeId,CreateDate,CreateBy) values (%s,%s,%s,%s,%s,%s)"
            parm = (Title, Description, Path, ImageThemeId,datetime,6)
            cursor.execute(sql, parm)
            conn.commit()
        else:
            sql = "Update image set Path=%s,ImageThemeId=%s,ModifyBy=%s,ModifyDate=%s where Title=%s"
            parm = (Path,  ImageThemeId,datetime,6, Title)
            cursor.execute(sql, parm)
            conn.commit()
    except MySQLdb.Error, e:
        string = "Mysql Error %d: %s" % (e.args[0], e.args[1])
        print string
        fout.write(string)
        conn.rollback()
