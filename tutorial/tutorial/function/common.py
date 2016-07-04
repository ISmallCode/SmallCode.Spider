# -*- coding: UTF-8 -*-
import smtplib
import sys
from email.mime.text import MIMEText

# import csv
# import xlrd
# import os
# import xlwt
# from xlutils.copy import copy
# import datetime
# import time

reload(sys)
sys.setdefaultencoding("utf-8")

mailto_list1 = ["fanfzj@163.com"]
mailto_list2 = ["fanfzj@163.com", "nele@ljyx.biz"]
mail_host = "smtp.qq.com"
mail_user = "1009137312@qq.com"
mail_pass = "2925184fanzhijun"


def send_mail(sub, content, type=0):
    me = "me" + "<" + mail_user + ">"
    msg = MIMEText(content, _subtype='html', _charset='utf-8')
    msg['Subject'] = sub
    msg['From'] = me
    if (type == 0):
        msg['To'] = ";".join(mailto_list1)
    else:
        msg['To'] = ";".join(mailto_list2)
    try:
        server = smtplib.SMTP()
        server.connect(mail_host)
        server.login(mail_user, mail_pass)
        if (type == 0):
            mail_list = mailto_list1
        else:
            mail_list = mailto_list2
        server.sendmail(me, mail_list, msg.as_string())
        server.close()
        return True
    except Exception, e:
        print e
        return False
