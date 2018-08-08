# -*- coding: utf-8 -*-
from commons.sql_wraper import SQLiteWraper


class SoufangSQL():
    global SQLite_wraper
    SQLite_wraper = SQLiteWraper()

    def get_village_info_by_name(self, name, village_info_url=None, reshouse=None, city_name=None):
        if name is None or name == '' and city_name is None or city_name == '':
            return []
        sql = 'select bvi.id,bvi.name,bvi.city_id,bvi.city_name,bvi.city_pinyin,bvi.area_id,bvi.area_name,bvi.area_pinyin,bvi.trade_area_id,bvi.trade_area_name' \
              ',bvi.metro_id,bvi.metro_name,bvi.station_id,bvi.station_name,bvi.address,bvi.province_id,bvi.province_name,bvi.province_pinyin from basic_village_info bvi ' \
              'where bvi.name = "%s" and bvi.city_name = "%s"' % (name, city_name)
        list = SQLite_wraper.fetchall(sql)
        if len(list) == 0 and village_info_url:
            list = []
            # list = save_village_info_return_info(village_info_url,reshouse)
        if len(list) > 1:
            print name, city_name
        return list

    def get_hous_broker_info_source_url(self, source_url):
        if source_url is None or source_url == '':
            return []
        sql = 'select source_url from basic_house_info bhi where bhi.source_url = "%s"' % (source_url)
        list = SQLite_wraper.fetchall(sql)
        return list

    def get_basic_trade_area_info_by_name(self, city_name, name):
        if name is None or name == '' or city_name is None or city_name == '':
            return []
        sql = 'select * from basic_trade_area bta where bta.name  = "%s" and bta.city_name="%s"' % (name, city_name)
        list = SQLite_wraper.fetchall(sql)
        return list

    def find_village_by_name_city(self, name, city_name):
        if name is None or name == '' or city_name is None or city_name == '':
            return []
        sql = 'select bvi.id,bvi.name,bvi.city_id,bvi.city_name,bvi.city_pinyin,bvi.area_id,bvi.area_name,bvi.area_pinyin,bvi.trade_area_id,bvi.trade_area_name' \
              ',bvi.metro_id,bvi.metro_name,bvi.station_id,bvi.station_name,bvi.address,bvi.province_id,bvi.province_name,bvi.province_pinyin from basic_village_info bvi ' \
              'where bvi.name = "%s" and bvi.city_name = "%s"' % (name, city_name)
        list = SQLite_wraper.fetchall(sql)
        return list

    def get_basic_trade_area_by_ca_name(self, city_name, area_name):
        if city_name is None or city_name == '' or area_name is None or area_name == '':
            return []
        sql = 'select * from basic_trade_area bta where bta.city_name  = "%s" and area_name="%s" ' % (
        city_name, area_name)
        list = SQLite_wraper.fetchall(sql)
        return list

    def get_basic_trade_area_by_c_name(self, city_name):
        if city_name is None or city_name == '':
            return []
        sql = 'select * from basic_trade_area bta where bta.city_name  = "%s" ' % (city_name)
        list = SQLite_wraper.fetchall(sql)
        return list

    def get_rental_mode(self, rental_mode_name):
        if rental_mode_name is None or rental_mode_name == '':
            return []
        sql = 'select sci.id from sys_code_info sci where sci.name = "%s"' % (rental_mode_name)
        list = SQLite_wraper.fetchall(sql)
        return list

    def update_hous_broker_update_time(self, source_url, now_time):
        sql = 'UPDATE `basic_house_info` bhi SET bhi.update_date= "%s" where bhi.source_url= "%s" ' % (
        now_time, source_url)
        SQLite_wraper.execute(sql)

    def get_img_count_by_source_url(self, source_url):
        if source_url is None or source_url == '':
            return 0
        sql = 'SELECT count(id) FROM `basic_house_image_info` where source_url ="%s" ' % (source_url)
        list = SQLite_wraper.fetchall(sql)
        return list[0][0]

    def get_broker_house_coune_by_source_url(self, house_source_url):
        if house_source_url is None or house_source_url == '':
            return 0
        sql = 'SELECT count(id) FROM `broker_house_info` where house_source_url ="%s" ' % (house_source_url)
        list = SQLite_wraper.fetchall(sql)
        return list[0][0]

    def insertData(self, table, parameter, conn=None):
        return SQLite_wraper.insertData(table, parameter, conn=conn)
