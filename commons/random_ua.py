# -*- coding:utf-8 -*-  
############################################################################  
''''' 
# 程序：创造爬虫随机头部
# 功能：创造爬虫随机头部
# 创建时间：2018/04/16
# 使用库：requests、BeautifulSoup4、MySQLdb 
# 作者：taylor 
'''
#############################################################################  
import random


def randHeader():
    # 随机生成User-Agent 
    head_connection = ['Keep-Alive', 'close']
    head_accept = ['text/html, application/xhtml+xml, */*']
    head_accept_language = ['zh-CN,fr-FR;q=0.5', 'en-US,en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3']
    # head_user_agent = ['Opera/8.0 (Macintosh; PPC Mac OS X; U; en)',  
    #                    'Opera/9.27 (Windows NT 5.2; U; zh-cn)',  
    #                    'Mozilla/5.0 (Macintosh; PPC Mac OS X; U; en) Opera 8.0',
    #                    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36',
    #                    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:59.0) Gecko/20100101 Firefox/59.0',
    #                    "Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36",  
    #                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.153 Safari/537.36",  
    #                    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:30.0) Gecko/20100101 Firefox/30.0",  
    #                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_2) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/7.0.3 Safari/537.75.14",  
    #                    "Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Win64; x64; Trident/6.0)"
    #                    ] 
    head_user_agent = []
    # with open("/data/jyall/1000-ua.log") as fh:
    with open("1000-ua.log") as fh:
        for line in fh:
            head_user_agent.append(line.strip())

    result = {
        'Connection': head_connection[0],
        'Accept': head_accept[0],
        'Accept-Language': head_accept_language[1],
        'User-Agent': head_user_agent[random.randrange(0, len(head_user_agent))]
    }
    return result


def randHeader_android(authorization):
    # 随机生成User-Agent 
    head_connection = ['Keep-Alive', 'close']
    head_accept = ['text/html, application/xhtml+xml, */*']
    head_accept_language = ['zh-CN,fr-FR;q=0.5', 'en-US,en;q=0.8,zh-Hans-CN;q=0.5,zh-Hans;q=0.3']
    head_user_agent = []
    with open("1000-android.log") as fh:
        for line in fh:
            head_user_agent.append(line.strip())

    result = {
        'Connection': head_connection[0],
        'Accept': head_accept[0],
        'Accept-Language': head_accept_language[1],
        'User-Agent': head_user_agent[random.randrange(0, len(head_user_agent))],
        'Authorization': authorization
    }
    return result
