import pymysql
import datetime


__cnx = None

def connect_sql():
    global __cnx 
    if __cnx == None :
        __cnx = pymysql.connect(user = 'root', password = 'vishruth', database = 'grocery_store')
    print('you got connected')
    return __cnx


