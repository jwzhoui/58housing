# -*- coding: utf-8 -*-

############################################################################
'''''
# 程序：搜房网爬虫
# 功能：抓取搜房网二手房在售、成交数据
# 创建时间：2018/03/26
# 使用库：requests、BeautifulSoup4、MySQLdb,MySQL-python == 1.2.5,pinyin==0.4.0
# 作者：taylor
'''
#############################################################################
import sys
import time
import traceback
import urlparse
from commons.jyallLog import mylog
from bs4 import BeautifulSoup
from commons.utility import getstringNoCodeRe, PinYin, to_int, get_int
import re
from commons.utility import getURL, multi_sub, get_soup_by_url
from house_project.sql import SoufangSQL

reload(sys)
sys.setdefaultencoding('utf-8')


def get_nb(url):
    my = url.split('.')[0]
    if my.__contains__('//'):
        my = my.split('//')[1]
    return my


# 修改页面空格 编码
class SoufangCore():
    global db_xq
    db_xq = SoufangSQL()

    def __init__(self):
        self.totle_item = 1

    # 保存小区信息并返回 小区信息详情
    def save_village_info_return_info_core(self, village_info_soup, village_info_url, reshouse, basic_village_info={}):
        try:
            if village_info_soup and village_info_url:

                city_name = \
                    village_info_soup.find('div', attrs={'class': 'breadcrumb-nav'}).find_all('a')[
                        0].get_text().strip().split(
                        '58')[0]
                name = village_info_soup.find('div', attrs={'class': 'title-bar'}).find('span',
                                                                                        attrs={
                                                                                            'class': 'title'}).get_text()
                ###################房源详情  中的小区名称可能与小区详情名称中的   名称不一致 导致小区名称 重复插入
                list = db_xq.find_village_by_name_city(name, city_name)
                if len(list) > 0:
                    return list
                ###################
                info_tb_soup_list = village_info_soup.find('table', attrs={'class': 'info-tb'}).find_all('tr')

                basic_village_info['name'] = name
                # 小区拼音
                village_pinyin = PinYin().get_pinyin_fist_b(name)
                basic_village_info['village_pinyin'] = village_pinyin
                try:
                    village_info = village_info_soup.find('div', attrs={'class': 'detail-mod desc-mod'}).find('p',
                                                                                                              attrs={
                                                                                                                  'class': 'desc'}).get_text()
                    basic_village_info['village_info'] = getstringNoCodeRe(village_info).replace('"',
                                                                                                 ' ') if village_info else ''
                except Exception, e:
                    mylog.warn('小区详情获取错误==> %s' % village_info_url)

                trade_area_name = None
                if len(info_tb_soup_list[0].find_all('td')) > 0:
                    # 商圈名称
                    trade_area_name = info_tb_soup_list[0].find_all('td')[1].get_text().strip().split('\n')[-1]

                    # 地址
                    address = info_tb_soup_list[0].find_all('td')[3].get_text().strip()
                    basic_village_info['address'] = address
                if trade_area_name:
                    # 获取数据库商圈信息
                    basic_trade_area_infos = db_xq.get_basic_trade_area_info_by_name(city_name, trade_area_name)
                    if len(basic_trade_area_infos) > 0:
                        basic_trade_area_info = basic_trade_area_infos[0]
                        basic_village_info['province_id'] = basic_trade_area_info[2]
                        basic_village_info['province_name'] = basic_trade_area_info[3]
                        basic_village_info['province_pinyin'] = basic_trade_area_info[4]
                        basic_village_info['city_id'] = basic_trade_area_info[5]
                        basic_village_info['city_name'] = basic_trade_area_info[6]
                        basic_village_info['city_pinyin'] = basic_trade_area_info[7]
                        basic_village_info['area_id'] = basic_trade_area_info[8]
                        basic_village_info['area_name'] = basic_trade_area_info[9]
                        basic_village_info['area_pinyin'] = basic_trade_area_info[10]
                        basic_village_info['trade_area_id'] = basic_trade_area_info[0]
                        basic_village_info['trade_area_name'] = basic_trade_area_info[1]
                    else:
                        titles = village_info_soup.find('div', attrs={'class': 'breadcrumb-nav'}).find_all('a')
                        if len(titles) > 4:
                            area_name = titles[3].get_text().strip().split('小区')[0]
                            basic_trade_area_infos = db_xq.get_basic_trade_area_by_ca_name(city_name, area_name)
                            if len(basic_trade_area_infos) > 0:
                                mylog.warn('商圈表中缺省商圈：城市=%s,商圈=%s' % (city_name, trade_area_name))
                                basic_trade_area_info = basic_trade_area_infos[0]
                                basic_village_info['province_id'] = basic_trade_area_info[2]
                                basic_village_info['province_name'] = basic_trade_area_info[3]
                                basic_village_info['province_pinyin'] = basic_trade_area_info[4]
                                basic_village_info['city_id'] = basic_trade_area_info[5]
                                basic_village_info['city_name'] = basic_trade_area_info[6]
                                basic_village_info['city_pinyin'] = basic_trade_area_info[7]
                                basic_village_info['area_id'] = basic_trade_area_info[8]
                                basic_village_info['area_name'] = basic_trade_area_info[9]
                                basic_village_info['area_pinyin'] = basic_trade_area_info[10]
                if len(info_tb_soup_list) > 1 and len(info_tb_soup_list[1].find_all('td')) > 3:
                    # 总户数
                    house_num_s = info_tb_soup_list[1].find_all('td')[3].get_text().strip()[0:-1]
                    basic_village_info['house_num'] = house_num_s if not house_num_s.__contains__('无') else '0'
                if len(info_tb_soup_list) > 2 and len(info_tb_soup_list[2].find_all('td')) > 3:
                    # 小区类型名称
                    village_type_name = info_tb_soup_list[2].find_all('td')[1].get_text().strip()
                    basic_village_info['village_type_name'] = village_type_name
                    # 物业费用
                    property_fee_s = info_tb_soup_list[2].find_all('td')[3].get_text().strip().split('元')[0]
                    basic_village_info['property_fee'] = property_fee_s

                if len(info_tb_soup_list) > 3 and len(info_tb_soup_list[3].find_all('td')) > 3:
                    # 产权
                    property_right = info_tb_soup_list[3].find_all('td')[1].get_text().strip()
                    basic_village_info['property_right'] = property_right
                    # 容积率
                    plot_ratio = info_tb_soup_list[3].find_all('td')[3].get_text().strip()
                    basic_village_info['plot_ratio'] = plot_ratio

                if len(info_tb_soup_list) > 4 and len(info_tb_soup_list[4].find_all('td')) > 3:
                    # 建筑年代
                    year_built = info_tb_soup_list[4].find_all('td')[1].get_text().strip()
                    basic_village_info['year_built'] = year_built[:-1]
                    # 绿化率
                    greening_rate = info_tb_soup_list[4].find_all('td')[3].get_text().strip()
                    basic_village_info['greening_rate'] = to_int(greening_rate)

                if len(info_tb_soup_list) > 5 and len(info_tb_soup_list[5].find_all('td')) > 3:
                    # 占地面积
                    occupation_land = info_tb_soup_list[5].find_all('td')[1].get_text().strip()
                    basic_village_info['occupation_land'] = occupation_land
                    # 建筑面积
                    ''
                    built_area = info_tb_soup_list[5].find_all('td')[3].get_text().strip().split('平')[0]
                    basic_village_info['built_area'] = built_area if not built_area.__contains__('暂') else '0'
                if len(info_tb_soup_list) > 7 and len(info_tb_soup_list[7].find_all('td')) > 1:
                    # 物业公司名称
                    property_name = info_tb_soup_list[7].find_all('td')[1].get_text().strip()
                    basic_village_info['property_name'] = property_name

                if len(info_tb_soup_list) > 8 and len(info_tb_soup_list[8].find_all('td')) > 1:
                    # 开发商
                    developers = info_tb_soup_list[8].find_all('td')[1].get_text().strip()
                    basic_village_info['developers'] = developers

                # 均价
                average_price = village_info_soup.find('div', attrs={'class': 'price-container'}).find('span', attrs={
                    'class': 'price'}).get_text()
                basic_village_info['average_price'] = average_price
                # 出租中房屋数量
                try:
                    lease_house_num = \
                        village_info_soup.find('tr', attrs={'class': 'tb-btm'}).find_all('td', attrs={'class': 'desc'})[
                            1].get_text()
                except Exception, e:
                    lease_house_num = '0'
                try:
                    basic_village_info['lease_house_num'] = getstringNoCodeRe(lease_house_num)[:-1]
                except Exception, e:
                    basic_village_info['lease_house_num'] = '0'
                if reshouse:
                    # 经纬度
                    lat = reshouse.get('lat', '')
                    lng = reshouse.get('lng', '')
                    basic_village_info['lat'] = lat
                    basic_village_info['lng'] = lng
                create_date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                last_update_date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                basic_village_info['create_date'] = create_date
                basic_village_info['last_update_date'] = last_update_date
                source_url = village_info_url
                basic_village_info['source_url'] = source_url

                db_xq.insertData('basic_village_info', basic_village_info)
                list = db_xq.find_village_by_name_city(name, city_name)
                return list
        except Exception, e:
            traceback.print_exc()
            mylog.error('小区信息插入错误==> %s,message==> %s' % (village_info_url, e.args))
            return []

    # 插入经纪人
    def inster_hous_broker(self, house_url, soup):
        try:
            broker_info = soup.find('div', attrs={'class': 'house-agent-info'})
            broker = {}
            broker_name_ = broker_info.select_one('.c_000').get_text().split('(')
            if len(broker_name_) < 2:
                print broker_name_
            broker['broker_name'] = broker_name_[0] if len(broker_name_) > 1 else broker_name_
            if soup.select_one('.house-chat-txt'):
                broker['broker_mobile'] = soup.select_one('.house-chat-txt').get_text()
            if soup.select_one('.agent-subgroup'):
                broker['broker_company_name'] = soup.select_one('.agent-subgroup').get_text().split(' ')[0]
            broker['house_source_url'] = 'http:' + house_url
            # 房源描述
            house_desc_ = soup.find_all('span', attrs={'class': 'a2'})
            broker['house_desc'] = house_desc_[1].get_text() if len(house_desc_) > 2 else ''
            price_ = soup.find('b', attrs={'class': 'f36'})
            if price_:
                price = price_.get_text() if price_ else ''
            broker['price'] = price
            broker['source_type'] = 1
            broker['create_date'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            broker['last_update_date'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            broker_count = db_xq.get_broker_house_coune_by_source_url(broker['house_source_url'])
            if broker_count > 0:
                pass
            if not broker_count:
                db_xq.insertData('broker_house_info', broker)
        except Exception, e:
            traceback.print_exc()
            mylog.error('房源经纪人异常url==%s' % (str(house_url)))
            mylog.error('房源经纪人异常err==%s' % (e.message))
            print e
            return

        # 插入图片列表

    def inster_hous_images(self, house_url, soup):
        try:
            images = soup.find_all('li', attrs={'id': re.compile('xtu_')})
            for image_ in images:
                image_url = 'http:' + image_.find('img').get('src')
                reshouse_image_info = {}
                reshouse_image_info['source_url'] = image_url
                reshouse_image_info['house_url'] = 'http:' + house_url
                reshouse_image_info['create_date'] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
                count = db_xq.get_img_count_by_source_url(image_url)
                if not count:
                    db_xq.insertData('basic_house_image_info', reshouse_image_info)
        except Exception, e:
            traceback.print_exc()
            print e

    def valid(self, city_name, price):
        r = False
        try:
            if city_name and price:
                if city_name.__contains__('北京') and float(price) < 1500:
                    r = False
                elif city_name.__contains__('上海') and float(price) < 1500:
                    r = False
                elif city_name.__contains__('广州') and float(price) < 1000:
                    r = False
                elif city_name.__contains__('深圳') and float(price) < 800:
                    r = False
                else:
                    r = True
            return r
        except Exception, e:
            print e.message
            return r

    # 条件查询结果 逐页抓取
    def souFang_core(self, soup, url):
        try:
            sql_db = SoufangSQL()
            # 页里面项数
            item_num = 0
            # 最大页数
            items = soup.find_all('div', attrs={'class': 'img_list'})
            if len(items) == 0:
                # 重复请求 一次防止代理出错
                soup = get_soup_by_url(url)
                items = soup.find_all('div', attrs={'class': 'img_list'})
                if len(items) == 0:
                    return
            for item in items:
                try:
                    now_time = unicode(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
                    reshouse = {}
                    item_num += 1
                    href = item.find('a').get('href')
                    if href and not href.__contains__('souFang_core'):
                        reshouse['source_url'] = 'http:' + href
                        # 房源信息根据 source_url 去重 ，重复更新 update time
                        hous_broker_village_infos = db_xq.get_hous_broker_info_source_url(reshouse['source_url'])
                        if len(hous_broker_village_infos) > 0:
                            db_xq.update_hous_broker_update_time(reshouse['source_url'], now_time)
                            mylog.info('update_source_url  ' + reshouse['source_url'] + str(item_num))
                            continue
                    else:
                        continue
                    item_info = BeautifulSoup(getURL('http:' + href), 'html.parser')
                    if item_info:
                        # 标题
                        title = item_info.find('h1', attrs={'class': 'c_333 f20'})
                        reshouse['title'] = title.get_text() if title else ''
                        # 封面
                        image_ = item_info.select_one('#smainPic')
                        reshouse['image'] = 'http:' + image_.get('src') if image_ else ''
                        reshouse['source_image'] = 'http:' + image_.get('src') if image_ else ''
                        # 房屋类型
                        try:
                            list = item_info.find('div', attrs={'class': 'house-desc-item fl c_333'}).find_all('li')
                            house_type_ = list[1].find_all('span')[1]
                        except Exception, e:
                            try:
                                list = item_info.find('div', attrs={'class': 'house-desc-item fl c_333'}).find('ul',
                                                                                                               attrs={
                                                                                                                   'class': 'f14'}).find_all(
                                    'li')
                                house_type_ = list[1].find_all('span')[1]
                            except Exception, e:
                                mylog.error('err_url 房屋类型模块切割失败  href: http:%s' % (href))
                                continue
                        house_type = multi_sub(house_type_.get_text() if house_type_ else '')
                        house_type_s = [i for i in house_type.split(' ') if i != '']
                        # 户型名称
                        house_type_name = house_type_s[0]
                        # 厅数
                        liveroom_count = house_type_name.encode('utf-8').split('厅')[0][-1]
                        reshouse['liveroom_count'] = get_int(liveroom_count)
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
                        # 小区详情url 以及小区名称
                        village_info_url = None
                        if list[3].find('a'):
                            name = list[3].find('a').get_text()
                            if list[3].find('a').get('href'):
                                village_info_url = 'http:' + list[3].find('a').get('href')
                        else:
                            name = ''
                        reshouse['village_name'] = name
                        # 城市
                        city_name = \
                            item_info.find('div', attrs={'nav-top-bar fl c_888 f12'}).find_all('a')[0].get_text().split(
                                '58')[0]
                        reshouse['city_name'] = city_name
                        # 来源  爬取
                        reshouse['source_type'] = '1'
                        # 价格
                        price_ = item_info.find('b', attrs={'class': 'f36'})
                        price = price_.get_text() if price_ else ''
                        reshouse['price'] = price
                        # 详细地址
                        if len(list) > 5 and len(list[5].find_all('span')) > 1:
                            address = list[5].find_all('span')[1].get_text()
                        else:
                            address = ''
                        reshouse['address'] = address.replace('\n', '').replace(' ', '')
                        # 租赁 方式
                        if len(list[0].find_all('span')) > 0:
                            lease_ = list[0].find_all('span')[1]
                            lease = lease_.get_text() if lease_ else ''
                            reshouse['rental_mode_name'] = lease.split('-')[0].replace(' ', '')
                        try:
                            rental_mode_ids = sql_db.get_rental_mode(reshouse['rental_mode_name'])
                        except Exception as e:
                            rental_mode_ids = []
                        if len(rental_mode_ids) > 0:
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
                            # 楼层名称(高中低等)
                            reshouse['floor_name'] = ''
                        # 房屋描述
                        house_info_ = item_info.find_all('span', attrs={'class': 'a2'})
                        house_info_s = house_info_[1].get_text().replace('\n', '').replace('\t', '') if len(
                            house_info_) > 1 else ''
                        if house_info_s.__contains__('>//'):
                            house_info_sp = house_info_s.split('>//')
                            if len(house_info_sp) > 0:
                                reshouse['house_info'] = house_info_sp[0]
                        # 位置 坐标
                        coordinates_ = item_info.find('a', attrs={
                            'onclick': 'clickLog(\'from=fcpc_detail_%s_xiaoquxq_ditu_xiangxi\')' % (get_nb(url))})
                        if coordinates_:
                            query = urlparse.urlparse(coordinates_.get('href')).query
                            parses_coordinates = dict([(k, v[0]) for k, v in urlparse.parse_qs(query).items()])[
                                'location'].split(',')
                            coordinates_lat = parses_coordinates[0]  # 坐标经度
                            reshouse['lat'] = coordinates_lat
                            coordinates_lng = parses_coordinates[1]  # 坐标纬度
                            reshouse['lng'] = coordinates_lng
                        else:
                            reshouse['lat'] = '0'
                            reshouse['lng'] = '0'
                        # 浏览量
                        see_count = item_info.select_one('#totalcount')
                        reshouse['see_count'] = see_count.get_text() if see_count else ''
                        # 房源类型 出租房
                        reshouse['house_source_type'] = '1'
                        # 出租房
                        reshouse['second_hand_house'] = '1'
                        reshouse['update_date'] = now_time
                        reshouse['create_date'] = now_time
                        reshouse['platform'] = '58'
                        # 小区关联信息 ,village_info_url
                        village_infos = sql_db.get_village_info_by_name(name, village_info_url=village_info_url,
                                                                        reshouse=reshouse, city_name=city_name)
                        if len(village_infos) < 1:
                            village_infos = self.save_village_info_return_info_core(get_soup_by_url(village_info_url),
                                                                                    village_info_url, reshouse)
                        if village_infos and len(village_infos) > 0:
                            village_info = village_infos[0]
                            reshouse['village_id'] = village_info[0]
                            reshouse['village_name'] = village_info[1]
                            reshouse['city_id'] = village_info[2]
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
                        else:  # 小区没有超链接
                            # 房源所在区
                            if len(list) > 4:
                                ''.strip()
                                areas = list[4].get_text().strip().split('\n')
                                basic_trade_areas = []
                                if len(areas) > 2:
                                    # 区名称
                                    area_name = getstringNoCodeRe(areas[1])
                                    # 商圈名称
                                    trade_area = getstringNoCodeRe(areas[2])
                                    basic_trade_areas = sql_db.get_basic_trade_area_info_by_name(city_name, trade_area)
                                    if len(basic_trade_areas) == 0:
                                        basic_trade_areas = sql_db.get_basic_trade_area_by_ca_name(city_name, area_name)
                                    else:
                                        basic_trade_area = basic_trade_areas[0]
                                        reshouse['trade_area_id'] = basic_trade_area[0]
                                        reshouse['trade_area_name'] = basic_trade_area[1]
                                if len(basic_trade_areas) < 1 and len(areas) > 1:
                                    # 城市  及区 查询商圈信息
                                    area_name = getstringNoCodeRe(areas[1])
                                    basic_trade_areas = sql_db.get_basic_trade_area_by_ca_name(city_name, area_name)
                                if len(basic_trade_areas) > 0:
                                    basic_trade_area = basic_trade_areas[0]
                                    reshouse['city_id'] = basic_trade_area[5]
                                    reshouse['city_pinyin'] = basic_trade_area[7]
                                    reshouse['area_id'] = basic_trade_area[8]
                                    reshouse['area_name'] = basic_trade_area[9]
                                    reshouse['area_pinyin'] = basic_trade_area[10]

                                    reshouse['address'] = address
                                    reshouse['province_id'] = basic_trade_area[2]
                                    reshouse['province_name'] = basic_trade_area[3]
                                    reshouse['province_pinyin'] = basic_trade_area[4]
                                else:  # 要是区也查询不到
                                    basic_trade_areas = sql_db.get_basic_trade_area_by_c_name(city_name)
                                    basic_trade_area = basic_trade_areas[0]
                                    reshouse['city_id'] = basic_trade_area[5]
                                    reshouse['city_pinyin'] = basic_trade_area[7]

                                    reshouse['address'] = address
                                    reshouse['province_id'] = basic_trade_area[2]
                                    reshouse['province_name'] = basic_trade_area[3]
                                    reshouse['province_pinyin'] = basic_trade_area[4]
                                    mylog.warn('58页面里 城市的区或镇缺失 或需要调整区或商圈==城市:%s,区:%s' % (city_name, area_name))

                        ## 城市房源价格判断
                        valid = self.valid(reshouse['city_name'], reshouse['price'])
                        if not valid:
                            reshouse['status'] = '2'
                            reshouse['is_delete'] = '2'
                        # 插入图片列表
                        self.inster_hous_images(href, item_info)
                        # 插入经纪人信息
                        self.inster_hous_broker(href, item_info)
                        # 插入房源数据
                        db_xq.insertData('basic_house_info', reshouse)
                        mylog.info(
                            '当前页: url: %s----当前项数%s---------总项数 %s' % ('http:' + str(href), item_num, self.totle_item))
                        self.totle_item = self.totle_item + 1
                    else:
                        print 'None'
                except Exception, e:
                    print traceback.print_exc()
                    print e
                #### 下一页
                url_split = url.split('?')[0].split('/')
                if url_split[-1].__contains__('pn'):
                    next_pg_tag = 'pn' + str(int(url_split[-1][2:]) + 1)
                    ll = url.split('?')[0].split('/')
                    ll.pop()
                    ll.append(next_pg_tag)
                    if len(url.split('?')) > 1:
                        re_url = '/'.join(ll) + '?' + url.split('?')[1]
                    else:
                        re_url = '/'.join(ll)
                elif url_split[-2].__contains__('pn'):
                    next_pg_tag = 'pn' + str(int(url_split[-2][2:]) + 1)
                    ll = url.split('?')[0].split('/')
                    ll.pop(-2)
                    ll.insert(-1, next_pg_tag)
                    uri = '/'.join(ll)
                    if len(url.split('?')) > 1:
                        re_url = uri + '?' + url.split('?')[1]
                    else:
                        re_url = uri
                else:
                    next_pg_tag = 'pn' + '2'
                    ll = url.split('?')[0].split('/')
                    ll.append(next_pg_tag)
                    uri = '/'.join(ll)
                    if len(url.split('?')) > 1:
                        re_url = uri + '?' + url.split('?')[1]
                    else:
                        re_url = uri
                assert re_url
                if re_url:
                    self.souFang_core(get_soup_by_url(re_url), re_url)
        except Exception, e:
            print traceback.print_exc()
            mylog.error(e.message)
            mylog.error('房源下一页切割错误或列表页获取错误：url==%s   获取下一商圈或停止抓取' % url)
