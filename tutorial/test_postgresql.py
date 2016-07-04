import psycopg2
import sys

con = None

try:

    con =psycopg2.connect(database='SmallCode',user="postgres", password="koala19920716", host="51newren.com", port="5432")
    cur = con.cursor()
    sql = "select * from EXArticleAuthor;"
    cur.execute(sql)
    ver = cur.fetchone()
    print ver

except psycopg2.DatabaseError, e:
    print 'Error %s' % e
    sys.exit(1)

finally:

    if con:
        con.close()