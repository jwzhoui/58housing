# -*- coding: utf-8 -*-
ISPROXY = 1  # 如需要使用代理，改为1，并设置代理IP参数 proxy
DATABASES = {
    'host': '192.168.3.207',
    'port': 3306,
    'user': 'root',
    'passwd': 'root',
    'db': 'bbzf',
    'charset': 'utf8'
}

# 58条件查询抓取
CITIES_CONDITIONS = [
    # {'base_url': 'http://sz.58.com/chuzu/1?key=布新统建楼'},
]

# 58城市整体抓取
CITIES_COMPLETE = [
    {'base_url': 'http://sz.58.com/chuzu/1/'},
]
