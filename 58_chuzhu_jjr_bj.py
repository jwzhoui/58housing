# -*- coding: utf-8 -*-

############################################################################
'''''
# 程序：搜房网爬虫
# 功能：抓取搜房网二手房在售、成交数据
# 创建时间：2018/03/26
# 使用库：requests、BeautifulSoup4、MySQLdb,MySQL-python == 1.2.5
# 作者：taylor
'''
#############################################################################
import multiprocessing
import traceback
import urlparse
import requests
from bs4 import BeautifulSoup
import time
import jyallLog
import utility
import random_ua
import re
import json
import threading
import sqlite3
import MySQLdb
import sys
reload(sys)
sys.setdefaultencoding('utf8')
hds = [{'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'}, \
       {
           'User-Agent': 'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.12 Safari/535.11'}, \
       {'User-Agent': 'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0)'}, \
       {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:34.0) Gecko/20100101 Firefox/34.0'}, \
       {
           'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Ubuntu Chromium/44.0.2403.89 Chrome/44.0.2403.89 Safari/537.36'}, \
       {
           'User-Agent': 'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50'}, \
       {
           'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50'}, \
       {'User-Agent': 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0'}, \
       {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1'}, \
       {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1'}, \
       {
           'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11'}, \
       {'User-Agent': 'Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11'}, \
       {'User-Agent': 'Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11'}]

class SQLiteWraper(object):
    """
    数据库的一个小封装，更好的处理多线程写入
    """
    def __init__(self, path, command='', *args, **kwargs):
        self.lock = threading.RLock()  # 锁
        self.path = path  # 数据库连接参数
        if command != '':
            conn = self.get_conn()
            cu = conn.cursor()
            cu.execute(command)

    def get_conn(self):
        conn = MySQLdb.connect(
            host='192.168.3.207',
            port=3306,
            user='root',
            passwd='root',
            db='bbzf',
            charset='utf8'
        )
        return conn

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
            except Exception ,me:
                print me.message
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
    def code(self,list):
        for i,s in enumerate(list):
            s = '' if s==None else s
            list[i] = str(s)
        return list
    # 插入数据
    @conn_trans
    def insertData(self, table, my_dict,conn=None):
        try:
            cu = conn.cursor()
            cols = ', '.join(self.code(my_dict.keys()))
            values = ','.join(['"'+str(i)+'"' for i in self.code(my_dict.values())])
            values = values.replace('"null"', 'null').replace('"None"','null').replace('""','null')
            sql = 'insert INTO %s (%s) VALUES (%s)' % (table, cols,  values )
            cu.execute(sql)
            conn.commit()
        except sqlite3.IntegrityError, e:
            traceback.print_exc()
            print e

# 修改页面空格 编码
def multi_sub(string ):
    n = u'南 '
    new = []
    for s in string:
        if s==n[1]:
            s = ' '
        new.append(s)
    return ''.join(new)

def getURL(url, tries_num=50, sleep_time=0, time_out=5,max_retry = 50):
        sleep_time_p = sleep_time
        time_out_p = time_out
        tries_num_p = tries_num
        try:
            # proxy_handler=urllib2.ProxyHandler(utility.getProxy())
            # opener=urllib2.build_opener(proxy_handler)
            # urllib2.install_opener(opener)
            send_headers = random_ua.randHeader()
            # res = urllib2.urlopen(url).read()#2018.04.11用request方式获取不到页面信息
            res = requests.Session()
            if isproxy == 1:
                res = requests.get(url, headers=send_headers, timeout=time_out, proxies=proxy)
            else:
                res = requests.get(url, headers=header, timeout=time_out)
            res.raise_for_status()  # 如果响应状态码不是 200，就主动抛出异常
        except requests.RequestException as e:
            sleep_time_p = sleep_time_p + 10
            time_out_p = time_out_p + 10
            tries_num_p = tries_num_p - 1
            # 设置重试次数，最大timeout 时间和 最长休眠时间  地
            if tries_num_p > 0:
                time.sleep(sleep_time_p)
                print url, 'URL Connection Error: 第', max_retry - tries_num_p, u'次 Retry Connection', e
                mylog.info('%sURL Connection Error:  %s  Retry Connection %s' % (url,str(max_retry - tries_num_p),str(e.message)))
                return getURL(url, tries_num_p, sleep_time_p, time_out_p,max_retry)
        return res.text.encode('utf-8')

class SoufangSpider():
    def __init__(self):
        self.totle_item = 1

    def getCityURL(self,fang_url):
        '''''
           从给定的主页登录，获取一级城市URL链接信息；剔除香港和更多城市链接
           :param fang_url:给定的主页登录，也可以从任一城市或者区域入口进入
           :return:返回城市名称及URL信息
        '''
        res = getURL(fang_url)
        soup = BeautifulSoup(res)
        result = []
        gio_district = soup.find('div', class_="city20141104nr")
        try:
            for link in gio_district.find_all('a'):
                district = {}
                district['base_url'] = link.get('href')
                district['city'] = link.get_text()
                #print  district['code'],district['name']
                #剔除香港和更多城市链接
                if district['base_url'] not in [u'http://www.hkproperty.com/',u'/newsecond/esfcities.aspx']:
                    result.append(district)
        except  Exception, e:
            print  'getRegions', fang_url, u"Exception:%s" % (e.message)

            return result
        #print result
        return result

    def getRegions(self,fang_url):
        '''''
          根据城市链接入口，获取每个城市的一级行政区域，因网站默认只显示100页，
          在数量量大的情况下，可以细化条件以扩大爬取数据量；
          搜房网字符集编码为GBK，否则中文乱码
        :param fang_url:城市链接入口
        :return:返回一级区域名称及URL信息
        '''
        res = getURL(fang_url)
        # res.encoding = 'gbk'
        # print 'res',res
        soup = BeautifulSoup(res,'html.parser')
        result = []
        # gio_district = soup.find('div', class_="qxName")
        # print 'soup',soup.find_all('dl',class_='secitem_fist')
        district = soup.find_all('dl', class_='secitem-fist')[0]
        # print '----->',district
        gio_district = district.find('dd')
        # print '----->',gio_district
        # return ''
        try:
            for link in gio_district.find_all('a'):
                district = {}
                district['code'] = link.get('href')
                district['name'] = link.get_text()
                # print  district['code'],district['name']
                #剔除不限，减少重复数据爬取，因中文乱码，这里用unicode代替
                if district['name'] <> u'\u4e0d\u9650':
                    result.append(district)
        except  Exception, e:
            print  'getRegions', fang_url, u"Exception:%s" % (e.message)
            return result
        return result

    def getSubRegions(self,fang_url):
        '''''
         从一级行政区域出发，获取二级区域链接，处理方式同一级行政区域
        :param fang_url:二级行政区域URL（全拼，需加上城市URL前缀，二级URL已包含一级URL，这个与链家不同）
        :return:返回二级区域的名称及URL信息
        '''
        res = getURL(fang_url)
        # res.encoding = 'gbk'
        soup = BeautifulSoup(res, 'html.parser')
        result = []
        print 'soup',fang_url
        # gio_plate = soup.find('p', id="shangQuancontain")
        gio_plate = soup.find_all('div', id='qySelectSecond')[0]
        # print 'gio_plate',gio_plate
        try:
            for link in gio_plate.find_all('a'):
                district = {}
                district['code'] = link.get('href')
                district['name'] = link.get_text()
                # print  district['code'],district['name']
                if district['name'] <> u'\u4e0d\u9650':
                    result.append(district)
        except Exception, e:
            print  'getSubRegions', fang_url, u"Exception:%s" % (e.message)
            mylog.error('getSubRegions==>%s   Exception==>%s' %(fang_url,e.message))
            return result
        return result

    def getSoufangList(self,fang_url, args):
        base_url = args['base_url']
        result = {}
        print '58房源地址：',fang_url
        res = getURL(fang_url)
        # res.encoding = 'gbk'
        soup = BeautifulSoup(res, 'html.parser')
        fanglist = soup.find_all("ul", class_="house-list-wrap")
        print '每页房源总数量：', len(fanglist[0].find_all("li"))
        for fang in fanglist[0].find_all("li"):
            # time.sleep(sleep_time)
            try:
                if not fang.has_attr('id'):
                    fang_url = fang.find_all('div',class_='pic')[0].find_all('a')[0]['href'].strip().encode('UTF-8')
                    print 'fang的信息: ',fang_url
                    res = getURL(fang_url)
                    soupfang = BeautifulSoup(res, 'html.parser')
                    # div = soupfang.find_all("div", id="bigCustomer")[0]
                    brokertel = soupfang.find_all("p",class_="phone-num")[0].getText().replace(' ','').replace('\n','')
                    brokername = '经纪人'
                    brokergroup = '公司'
                    # print 'soupfang',soupfang
                    sript = soupfang.find_all("script")[0].getText()
                    # print 'sript',sript
                    sriptArray = sript.split(';\n')
                    # print 'sriptArray',sriptArray
                    for sriptstr in sriptArray:
                        sriptstr = sriptstr.replace(' ','').replace('\n','')
                        # print 'sriptstr',sriptstr
                        if sriptstr.find('____json4fe=') == 0:
                            # print 'sriptstr',sriptstr
                            jsonArray = sriptstr.split('json4fe=')
                            if len(jsonArray)==2:
                                # print 'jsonArray[1]',jsonArray[1]
                                jsonDic = json.loads(jsonArray[1])
                                # print "json: ", jsonDic
                                brokername = jsonDic['userName']
                                brokergroup = jsonDic['entName']
                    # return ''
                    # script = soup.find("script", text=pattern)
                    # brokername = soupfang.find_all('div',class_="agent-name")[0].find_all('a')[0].getText().replace(' ','').replace('\n','')
                    # brokergroup = soupfang.find_all('p',class_="agent-belong")[0].find_all('span')[1].getText().replace(' ','').replace('\n','')
                    result['fang_url'] = fang_url
                    result['name'] = utility.getstring(brokername)
                    result['phone'] = utility.getDBstring(brokertel)
                    result['company_name'] = utility.getstring(brokergroup)
                    result['city_name'] = '北京'
                    result['area_name'] = args['region']
                    result['trade_name'] = args['subRegion']
                    result['type'] = '二手房'
                    result['createtime'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    result['updatetime'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                    clo = {}#判断条件
                    clo['phone'] = brokertel
                    clo['trade_name'] = result['trade_name']
                    clo['type'] = result['type']
                    if mySQL.selectCountDataNew('broker_58',clo) == 0:
                         mylog.info('-->'+brokergroup+'-'+brokername+'-'+brokertel)
                         print '-->经纪人公司：',brokergroup+'-'+brokername
                         print '-->经纪人电话：',brokertel
                         mySQL.insertData('broker_58',result)
                    else:
                         print '-->重复经纪人'
                         mylog.info('-->重复经纪人')
            except Exception, e:
                print  'error：',e.message
                mylog.error(e.message)

    def get_village_info_by_name(self,name,db_xq):
        if name is None or name == '':
            return []
        sql = 'select bvi.id,bvi.name,bvi.city_id,bvi.city_name,bvi.city_pinyin,bvi.area_id,bvi.area_name,bvi.area_pinyin,bvi.trade_area_id,bvi.trade_area_name' \
              ',bvi.metro_id,bvi.metro_name,bvi.station_id,bvi.station_name,bvi.address,bvi.province_id,bvi.province_name,bvi.province_pinyin from basic_village_info bvi where bvi.name = "%s"' % (name)
        list = db_xq.fetchall(sql)
        return list

    def get_rental_mode(self,rental_mode_name,db_xq):
        if rental_mode_name is None or rental_mode_name == '':
            return []
        sql = 'select sci.id from sys_code_info sci where sci.name = "%s"' % (rental_mode_name)
        list = db_xq.fetchall(sql)
        return list

    # 插入经纪人
    def inster_hous_broker(self,house_url, soup,db_xq):
        try:
            broker_info = soup.find('div', attrs={'class': 'house-agent-info'})
            broker = {}
            broker_name_ = broker_info.select_one('.c_000').get_text().split('(')
            if len(broker_name_)<2:
                print broker_name_
            broker['broker_name'] = broker_name_[0] if len(broker_name_)>1 else broker_name_
            broker['broker_mobile'] = soup.select_one('.house-chat-txt').get_text()
            broker['broker_company_name'] = soup.select_one('.agent-subgroup').get_text().split(' ')[0]
            broker['house_source_url'] = 'http:'+house_url
            # 房源描述
            house_desc_ = soup.find_all('span',attrs={'class':'a2'})
            broker['house_desc'] = house_desc_[1].get_text() if len(house_desc_)>2 else ''
            price_ = soup.find('b', attrs={'class': 'f36'})
            price = price_.get_text() if price_ else ''
            broker['price'] = price
            broker['source_type'] = 1
            broker['create_date'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            broker['last_update_date'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            db_xq.insertData('broker_house_info', broker)
        except Exception, e:
            traceback.print_exc()
            mylog.error('房源经纪人异常url==%s' % (str(house_url)))
            mylog.error('房源经纪人异常err==%s' % (e.message))
            print e
            return
        # 插入图片列表
    def inster_hous_images(self,house_url, soup,db_xq):
        try:
            images = soup.find_all('li', attrs={'id': re.compile('xtu_')})
            for image_ in images:
                image_url = 'http:'+image_.find('img').get('src')
                reshouse_image_info = {}
                reshouse_image_info['source_url'] = image_url
                reshouse_image_info['house_url'] = 'http:'+house_url
                reshouse_image_info['create_date'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                db_xq.insertData('basic_house_image_info',reshouse_image_info)
        except Exception, e:
            traceback.print_exc()
            print e

    def souFang_core(self,city,db_xq):
        soup = BeautifulSoup(getURL(city['base_url']), 'html.parser')
        # 页里面项数
        item_num = 0
        # 本页数据
        items = soup.find_all('div', attrs={'class': 'img_list'})
        for item in items:
            try:
                reshouse = {}
                item_num += 1
                href = item.find('a').get('href')
                reshouse['source_url'] = 'http:'+href
                item_info = BeautifulSoup(getURL('http:'+href), 'html.parser')
                if item_info:
                    # 标题
                    title = item_info.find('h1',attrs={'class':'c_333 f20'})
                    reshouse['title'] = title.get_text() if title else ''
                    # 封面
                    image_ = item_info.select_one('#smainPic')
                    reshouse['image'] = 'http:'+image_.get('src') if image_ else ''
                    # 房屋类型
                    try:
                        list = item_info.find('div', attrs={'class': 'house-desc-item fl c_333'}).find_all('li')
                        house_type_ = list[1].find_all('span')[1]
                    except Exception, e:
                        mylog.error('err_url  href:%s' % (href))

                    house_type = multi_sub(house_type_.get_text() if house_type_ else '')
                    house_type_s = [i for i in house_type.split(' ') if i != '']
                    # 户型名称
                    house_type_name = house_type_s[0]
                    # 厅数
                    liveroom_count = house_type_name.encode('utf-8').split('厅')[0][-1]
                    reshouse['liveroom_count'] = liveroom_count
                    # 室数
                    bedroom_count = house_type_name.encode('utf-8').split('室')[0][-1]
                    reshouse['bedroom_count'] = bedroom_count
                    # 装修名称
                    len_house_type_s = len(house_type_s)
                    if len_house_type_s > 3:
                        renovation_name = house_type_s[3]
                    else:
                        renovation_name = ''
                    reshouse['renovation_name'] = renovation_name
                    reshouse['house_type_name'] = house_type_name
                    acreage = house_type_s[1]  # 大小  如 110-120平
                    # 面积
                    reshouse['acreage'] = acreage.strip()
                    # TODO house_type_id   户型id 外键未关联
                    # 小区名称
                    if list[3].find('a'):
                        name = list[3].find('a').get_text()
                    else:
                        name = ''

                    reshouse['village_name'] = name
                    # 来源  爬取
                    reshouse['source_type'] = '1'
                    # 价格
                    price_ = item_info.find('b', attrs={'class': 'f36'})
                    price = price_.get_text() if price_ else ''
                    reshouse['price'] = price
                    # 详细地址
                    if len(list)>5 and len(list[5].find_all('span'))>1:
                        address = list[5].find_all('span')[1].get_text()
                    else:
                        address = ''
                    reshouse['address'] = address.replace('\n', '').replace(' ', '')
                    # 租赁 方式
                    lease_ = list[0].find_all('span')[1]
                    lease = lease_.get_text() if lease_ else ''
                    reshouse['rental_mode_name'] = lease.split('-')[0].replace(' ','')
                    rental_mode_ids = self.get_rental_mode(reshouse['rental_mode_name'],db_xq)
                    if len(rental_mode_ids)>0:
                        rental_mode_id = rental_mode_ids[0][0]
                    else:
                        rental_mode_id = None
                    reshouse['rental_mode_id'] = rental_mode_id
                    # 房屋朝向 u'东南  中层/共32层'
                    orientation_ = list[2].find_all('span')[1]
                    if orientation_:
                        orientation = orientation_.get_text()
                    else:
                        orientation = ''
                    orientation = multi_sub(orientation)
                    orientation_s = orientation.split('  ')
                    if len(orientation_s) > 1:
                        reshouse['orientation_name'] = orientation_s[0]
                        # 楼层名称（高中低等）
                        reshouse['floor_name'] = orientation_s[1].split('/')[0]
                    else:
                        reshouse['orientation_name'] = ''
                        # 楼层名称（高中低等）
                        reshouse['floor_name'] = ''
                    # 房屋描述
                    house_info_ = item_info.find_all('span',attrs={'class':'a2'})
                    reshouse['house_info'] = house_info_[1].get_text() if len(house_info_) > 1 else ''
                    # 位置 坐标
                    coordinates_ = item_info.find('a', attrs={
                        'onclick': 'clickLog(\'from=fcpc_detail_%s_xiaoquxq_ditu_xiangxi\')' % (city['nb'])})
                    if coordinates_:
                        query = urlparse.urlparse(coordinates_.get('href')).query
                        parses_coordinates = dict([(k, v[0]) for k, v in urlparse.parse_qs(query).items()])[
                            'location'].split(',')
                        coordinates_lat = parses_coordinates[0]  # 坐标经度
                        reshouse['lat'] = coordinates_lat
                        coordinates_lng = parses_coordinates[1]  # 坐标纬度
                        reshouse['lng'] = coordinates_lng
                    else:
                        reshouse['lat'] = ''
                        reshouse['lng'] = ''
                    # 浏览量
                    see_count = item_info.select_one('#totalcount')
                    reshouse['see_count'] = see_count.get_text() if see_count else ''
                    # 房源类型 出租房
                    reshouse['house_source_type'] = '1'
                    # 出租房
                    reshouse['second_hand_house'] = '1'
                    reshouse['update_date'] = unicode(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
                    reshouse['create_date'] = unicode(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
                    # 小区关联信息
                    village_infos = self.get_village_info_by_name(name, db_xq)
                    if len(village_infos) > 0:
                        village_info = village_infos[0]
                        reshouse['village_id'] = village_info[0]
                        reshouse['village_name'] = village_info[1]
                        reshouse['city_id'] = village_info[2]
                        reshouse['city_name'] = village_info[3]
                        reshouse['city_pinyin'] = village_info[4]
                        reshouse['area_id'] = village_info[5]
                        reshouse['area_name'] = village_info[6]
                        reshouse['area_pinyin'] = village_info[7]
                        reshouse['trade_area_id'] = village_info[8]
                        reshouse['trade_area_name'] = village_info[9]
                        reshouse['metro_id'] = village_info[10]
                        reshouse['metro_name'] = village_info[11]
                        reshouse['metro_station_id'] = village_info[12]
                        reshouse['metro_station_name'] = village_info[13]
                        reshouse['address'] = village_info[14]
                        reshouse['province_id'] = village_info[15]
                        reshouse['province_name'] = village_info[16]
                        reshouse['province_pinyin'] = village_info[17]
                    # 插入图片列表
                    self.inster_hous_images(href,item_info,db_xq)
                    # 插入经纪人信息
                    self.inster_hous_broker(href,item_info,db_xq)
                    # 插入房源数据
                    db_xq.insertData('basic_house_info', reshouse)
                    mylog.info('当前页: url: %s----当前项数%s---------总项数 %s' % ('http:'+str(href), item_num, self.totle_item))
                    self.totle_item = self.totle_item + 1
                else:
                    print 'None'
            except Exception, e:
                print traceback.print_exc()
                print e
        # 每页详情

        # 抓取数据
        # 找出 总页数  每50页启一个线程  最多 100个线程

        # 下页链接 抓取
        next_pg_tag = soup.find('a', attrs={'class': 'next'})
        if next_pg_tag:
            next_pg_href = next_pg_tag.attrs['href']
            city['base_url'] = next_pg_href
            self.souFang_core(city, db_xq)


    def getSoufangMutiCityMain(self,city,db_xq,page_nb=1,page_item=1):
        try:
            base_url_split = city['base_url'].split('//')
            res = getURL(city['base_url'])
            soup = BeautifulSoup(res, 'html.parser')
            try:
                areas = soup.select_one('.secitem_fist').select('a')
            except Exception,e:
                mylog.error('第一次获取根页面失败')
                self.getSoufangMutiCityMain(city,db_xq)
            for area in areas[1:]:
                # 城市链接
                area_href = base_url_split[0]+'//'+base_url_split[1].split('/')[0]+area.get('href')
                # 商圈链接
                res_area_href = getURL(area_href)
                area_soup = BeautifulSoup(res_area_href, 'html.parser')
                circles = area_soup.select_one('.arealist').select('a')
                for circle in circles:
                    res_circle_href = base_url_split[0] + '//' + base_url_split[1].split('/')[0] + circle.get('href')
                    city['base_url'] = res_circle_href
                    self.souFang_core(city,db_xq)

        except Exception, e:
            print traceback.print_exc()
            mylog.info(traceback.print_exc())
            print e


def main():
    global mySQL, start_page, end_page, sleep_time, isproxy, proxy, header ,mylog
    soufang=SoufangSpider()
    isproxy = 1  # 如需要使用代理，改为1，并设置代理IP参数 proxy
    proxy = utility.getProxy()#这里需要替换成可用的代理IP
    header = random_ua.randHeader_android('')
    mylog = jyallLog.log()
    start_page = 1
    sleep_time = 0.5
    db_xq=SQLiteWraper('basic_house_info')
    cities = [
        {'base_url': 'http://bj.58.com/chuzu/1', 'city': '北京', 'nb': 'bj'},
        # {'base_url': 'http://sh.58.com/chuzu/1', 'city': '上海', 'nb': 'sh'},
        # {'base_url': 'http://gz.58.com/chuzu/1', 'city': '广州', 'nb': 'gz'},
        # {'base_url': 'http://sz.58.com/chuzu/1', 'city': '深圳','nb':'sz'},
              ]
    def func(city,db_xq):
        soufang.getSoufangMutiCityMain(city, db_xq)
    try:
        for city in cities:
            mylog.info('58同城经纪人房源爬取地址===>%s   城市===>%s' % (city['base_url'],city['city']))
            soufang.getSoufangMutiCityMain(city,db_xq)

    except Exception, e:
        print e
try:
    if __name__ == "__main__":
        main()

except Exception, e:
    print e


