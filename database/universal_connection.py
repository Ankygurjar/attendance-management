import pymysql
from pymysql.cursors import DictCursor 

def connect():
        return pymysql.connect(host='localhost',
        user='root',
        password='',
        db='attendance',
        cursorclass=DictCursor
        )