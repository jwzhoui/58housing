# -*- coding:utf-8 -*-
import sqlite3
import threading
import traceback
import MySQLdb
from commons.jyallLog import mylog
import settings


class SQLiteWraper(object):
    """
    数据库的一个小封装，更好的处理多线程写入
    """

    def __init__(self, command='', *args, **kwargs):
        self.lock = threading.RLock()  # 锁
        if command != '':
            conn = self.get_conn()
            cu = conn.cursor()
            cu.execute(command)

    def get_conn(self):
        conn = MySQLdb.connect(
            **settings.DATABASES
        )
        return conn

    # def get_conn(self):
    #     conn = MySQLdb.connect(
    #         host='10.10.38.83',
    #         port=3306,
    #         user='bbzf',
    #         passwd='bbzf123qwe',
    #         db='bbzf',
    #         charset='utf8'
    #     )
    #     return conn

    def conn_close(self, conn=None):
        conn.close()

    def conn_trans(func):
        def connection(self, *args, **kwargs):
            self.lock.acquire()
            conn = self.get_conn()
            kwargs['conn'] = conn
            try:
                rs = func(self, *args, **kwargs)
                return rs
            except Exception, me:
                traceback.print_exc()
                mylog.error(me.args)
                # print '执行方法错误：%s' %  func.func_name
            finally:
                conn.rollback()
                self.conn_close(conn)
                self.lock.release()

        return connection

    @conn_trans
    def fetchall(self, command="", conn=None):
        cu = conn.cursor()
        lists = []
        try:
            cu.execute(command)
            lists = cu.fetchall()
        except Exception, e:
            print e
            pass
        return lists

    @conn_trans
    def execute(self, command, method_flag=0, conn=None):
        cu = conn.cursor()
        try:
            if not method_flag:
                cu.execute(command)
            else:
                cu.execute(command[0], command[1])
            conn.commit()
        except sqlite3.IntegrityError, e:
            # print e　'insert into xiaoqu values( 东城逸墅,东城,工体,塔板结合, 2009)'
            return -1
        except Exception, e:
            print e
            return -2
        return 0

    def code(self, list):
        for i, s in enumerate(list):
            s = '' if s == None else s
            list[i] = str(s)
        return list

    # 插入数据
    @conn_trans
    def insertData(self, table, my_dict, conn=None):
        try:
            cu = conn.cursor()
            cols = ', '.join(self.code(my_dict.keys()))
            values = ','.join(['"' + str(i) + '"' for i in self.code(my_dict.values())])
            values = values.replace('"null"', 'null').replace('"None"', 'null').replace('""', 'null')
            sql = 'insert INTO %s (%s) VALUES (%s)' % (table, cols, values)
            cu.execute(sql)
            conn.commit()
        except sqlite3.IntegrityError, e:
            traceback.print_exc()
            mylog.error(e.message + ' 错误sql: %s ' % sql)
