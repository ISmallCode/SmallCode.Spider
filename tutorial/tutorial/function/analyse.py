import jieba
import MySQLdb
import sys
import time

reload(sys)
sys.setdefaultencoding('utf8')

ISOTIMEFORMAT = '%Y-%m-%d %X'
fout = open('except.txt', 'w')
