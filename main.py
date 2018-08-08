# -*- coding: utf-8 -*-
from commons.jyallLog import mylog
import settings
from house_project.spider import SoufangSpider


def main():
    #################58条件页面爬取begin#################
    ## 与整体爬取分开使用
    #
    if len(settings.CITIES_CONDITIONS):
        cities = settings.CITIES_CONDITIONS
        try:
            for city in cities:
                mylog.info('58同城经纪人房源爬取地址===>%s' % (city['base_url']))
                SoufangSpider().soufang_spider_conditions(city)
        except Exception, e:
            print e

    #################58条件页面爬取end#################

    #################58单条详情--未完善--begin#################
    ##
    # cities = [
    #     {'base_url': 'http://bj.58.com/zufang/34877405506250x.shtml', 'city': '北京', 'nb': 'bj'},
    #           ]
    # try:
    #     for city in cities:
    #         mylog.info('58同城经纪人房源爬取地址===>%s   城市===>%s' % (city['base_url'],city['city']))
    #         SoufangSpider().item_info_do(city, db_xq)
    # except Exception, e:
    #     print e

    #################58单条详情end#################

    #################58城市整体爬取begin#################
    ##
    if len(settings.CITIES_COMPLETE):
        cities = settings.CITIES_COMPLETE
        try:
            for city in cities:
                mylog.info('58城市整体爬取  58同城经纪人房源爬取地址===>%s' % (city['base_url']))
                ss = SoufangSpider()
                ss.soufang_spider_complete(city['base_url'])
        except Exception, e:
            print e
    #################58城市整体爬取end#################


try:
    if __name__ == "__main__":
        main()

except Exception, e:
    print e
