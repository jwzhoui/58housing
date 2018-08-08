# -*- coding: utf-8 -*-
import settings
from commons import random_ua
from house_project.core import SoufangCore
import traceback
from copy import deepcopy
from commons.utility import get_soup_by_url, getURL
from commons.jyallLog import mylog
from bs4 import BeautifulSoup
import sys

reload(sys)


class SoufangSpider():
    global Soufang_core
    Soufang_core = SoufangCore()

    def __init__(self):
        self.totle_item = 1

    def soufang_spider_conditions(self, url):
        soup = get_soup_by_url(url)
        Soufang_core.souFang_core(soup, url)

    def soufang_spider_complete(self, url, ho=0):
        try:
            base_url_split = url.split('//')
            soup = get_soup_by_url(url)
            try:
                areas = soup.select_one('.secitem_fist').select('a')
            except Exception, e:
                traceback.print_exc()
                ho = ho + 1
                mylog.error('第%s次获取根页面失败' % str(ho))
                self.soufang_spider_complete(url, ho=ho)
            for area in areas[1:]:
                # 城市链接
                area_href = base_url_split[0] + '//' + base_url_split[1].split('/')[0] + area.get('href')
                # 商圈链接s
                try:
                    res_area_href = getURL(area_href)
                    area_soup = BeautifulSoup(res_area_href, 'html.parser')
                    circles = area_soup.select_one('.arealist').select('a')
                except Exception, e:
                    try:
                        res_area_href = getURL(area_href)
                        area_soup = BeautifulSoup(res_area_href, 'html.parser')
                        circles = area_soup.select_one('.arealist').select('a')
                    except Exception, e:
                        mylog.warn('商圈链接获取失败，或无商圈')
                        Soufang_core.souFang_core(area_soup, area_href)
                        continue
                for circle in circles:
                    print circle.get('href')
                    res_circle_href = base_url_split[0] + '//' + base_url_split[1].split('/')[0] + circle.get('href')
                    url = res_circle_href
                    Soufang_core.souFang_core(get_soup_by_url(url), url)
        except Exception, e:
            traceback.print_exc()
            mylog.info(traceback.print_exc())
            print e
