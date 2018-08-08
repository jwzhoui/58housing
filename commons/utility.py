# -*- coding:utf-8 -*-  
############################################################################  
''''' 
# 程序：爬虫utility 
# 功能：多维工具集合 
# 创建时间：2018/04/16
# 作者：taylor 
'''
#############################################################################
import os
import time
import datetime
import settings
from commons import random_ua
from copy import deepcopy
from requests.exceptions import SSLError
from commons.jyallLog import mylog
import requests
from bs4 import BeautifulSoup
import time


def getCurrentDate():
    return time.strftime('%Y-%m-%d', time.localtime(time.time()))


def getCurrentTime():
    # 获取当前时间
    return time.strftime('[%Y-%m-%d %H:%M:%S]', time.localtime(time.time()))


def getTimeWithStamp(timeStamp):
    timeArray = time.localtime(timeStamp)
    return time.strftime("%Y-%m-%d %H:%M:%S", timeArray)


def get_day_of_day(n=0):
    if (n < 0):
        n = abs(n)
        return datetime.date.today() - datetime.timedelta(days=n)
    else:
        return datetime.date.today() + datetime.timedelta(days=n)


def getStrToDate(string):
    return datetime.datetime.strptime(string, '%Y-%m-%d %H:%M:%s')


def getstringNoCode(string):
    if string == None:
        return ''
    else:
        return string


def to_int(string):
    try:
        aa = int(string.strip('%'))  # 去掉s 字符串中的 %
        return aa
    except Exception, e:
        return '0'


def getstringNoCodeRe(string):
    if string == None:
        return ''
    else:
        return string.strip().replace('\n', '').replace('\t', '').replace(' ', '').replace('\r', '') if string else ''


def getstring(string):
    if string == None:
        return ''
    else:
        return string.encode('UTF-8').replace('\n', '').replace(' ', '')


def getDBstring(string):
    if string == None:
        return '0'
    elif string == '':
        return '0'
    else:
        return str(string).encode('UTF-8').replace('\n', '').replace(' ', '')


def getDBNoneConvert(string):
    if string == None:
        return 'null'
    elif string == '':
        return 'null'
    else:
        return str(string).encode('UTF-8').replace('\n', '').replace(' ', '')


def getfloat(string):
    if string == None:
        return 0
    elif string == '':
        return 0
    else:
        return float(string)


def getstrip(string):
    return '' if string == None else string.strip()


def getProxy():
    return {"http": "http://16YPROHH:195778@p10.t.16yun.cn:6446", "https": "http://16YPROHH:195778@p10.t.16yun.cn:6446"}



def getProxy1():
    return {"http": "http://16DRCOYA:253467@n10.t.16yun.cn:6442", "https": "http://16DRCOYA:253467@n10.t.16yun.cn:6442"}


def get_int(string):
    try:
        return int(string)
    except Exception, e:
        return 0


class PinYin(object):
    def __init__(self, dict_file='word.data'):
        self.word_dict = {}
        self.dict_file = dict_file
        self.load_word()

    def load_word(self):
        if not os.path.exists(self.dict_file):
            raise IOError("NotFoundFile")

        with file(self.dict_file) as f_obj:
            for f_line in f_obj.readlines():
                try:
                    line = f_line.split('    ')
                    self.word_dict[line[0]] = line[1]
                except:
                    line = f_line.split('   ')
                    self.word_dict[line[0]] = line[1]

    def hanzi2pinyin(self, string=""):
        result = []
        if not isinstance(string, unicode):
            string = string.decode("utf-8")

        for char in string:
            key = '%X' % ord(char)
            result.append(self.word_dict.get(key, char).split()[0][:-1].lower())

        return result

    def hanzi2pinyin_split(self, string="", split=""):
        result = self.hanzi2pinyin(string=string)
        if split == "":
            return result
        else:
            return split.join(result)

    def get_pinyin_fist_b(self, string):
        return '.'.join(self.hanzi2pinyin(string=string)).title().replace('.', '')


def multi_sub(string):
    n = u'南 '
    new = []
    for s in string:
        if s == n[1]:
            s = ' '
        new.append(s)
    return ''.join(new)


def get_soup_by_url(url):
    if url:
        html_text = getURL(url)
        try:
            soup = BeautifulSoup(html_text, 'html.parser')
        except Exception, e:
            print e.args
        return soup


def getURL(url, tries_num=3, sleep_time=0, time_out=5, max_retry=50):
    sleep_time_p = sleep_time
    time_out_p = time_out
    tries_num_p = deepcopy(tries_num)
    try:
        send_headers = random_ua.randHeader()
        if settings.ISPROXY == 1:
            res = requests.get(url, headers=send_headers, timeout=time_out, proxies=getProxy1())
        else:
            res = requests.get(url, headers=random_ua.randHeader_android(''), timeout=time_out, stream=True)
        res.raise_for_status()  # 如果响应状态码不是 200，就主动抛出异常
    except Exception as e:
        if isinstance(e, SSLError):
            mylog.info('%sURL Connection Error: 页面ssl错误 ' % (url))
            return
        sleep_time_p = sleep_time_p + 2
        time_out_p = time_out_p + 2
        tries_num_p = tries_num_p - 1
        # 设置重试次数，最大timeout 时间和 最长休眠时间  地
        if tries_num_p > 0:
            time.sleep(sleep_time_p)
            mylog.info('%sURL Connection Error:  %s  Retry Connection %s' % (
                url, str(max_retry - tries_num_p), str(e.message)))
            return getURL(url, tries_num_p, sleep_time_p, time_out_p, max_retry)
        else:
            mylog.info('重复请求%s次，结束请求，错误url ：%s' % (str(tries_num), url))
            return
    return res.text.encode('utf-8')


if __name__ == '__main__':
    py = PinYin()
    print py.get_pinyin_fist_b("阿达时发生的发送肺")
