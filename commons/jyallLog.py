# -*- coding: utf-8 -*-
# Created by Taylor at 2018/05/07

import logging
import getpass
import sys
import os

import time


class log(object):
    def __init__(self):
        root_directory = '/data/jyall/log/'
        # 文件不存在就创建
        if not os.path.exists(root_directory):
            os.makedirs(root_directory)
        # root_directory = '/Users/taylor/jyall/log/'
        path = root_directory + time.strftime('%Y-%m-%d', time.localtime(time.time()))
        try:
            os.mkdir(path)
        except OSError:
            pass

        user = getpass.getuser()
        self.logger = logging.getLogger(user)
        self.logger.setLevel(logging.DEBUG)
        logFile = os.path.basename(sys.argv[0]) + '.log'
        # print(os.path.basename(sys.argv[0]))

        formatter = logging.Formatter('%(asctime)-12s %(levelname)-8s %(name)-10s %(message)-12s')
        logHand = logging.FileHandler(path + '/' + logFile)
        logHand.setFormatter(formatter)
        logHand.setLevel(logging.INFO)
        logHandSt = logging.StreamHandler()
        logHandSt.setFormatter(formatter)
        self.logger.addHandler(logHand)
        self.logger.addHandler(logHandSt)

    def debug(self, msg):
        self.logger.debug(msg)

    def info(self, msg):
        self.logger.info(msg)

    def error(self, msg):
        self.logger.error(msg)

    def warn(self, msg):
        self.logger.warn(msg)

    def critical(self, msg):
        self.logger.critical(msg)


mylog = log()
if __name__ == '__main__':
    mylog.debug("I'm debug" + "hello world")
    mylog.info("I'm info" + " hello world")
    mylog.warn("I'm warn")
    mylog.error("I'm error")
    mylog.critical("I'm critical")
