#!/usr/bin/python
# coding=utf-8

import sys
reload(sys)
sys.setdefaultencoding('UTF-8')
sys.path.append('..')

import logging
import coloredlogs
from logging.handlers import TimedRotatingFileHandler

# log formatter
formatter_pattern = "%(asctime)s [%(levelname)s] [%(filename)s:%(lineno)d] %(message)s"
time_pattern = '%Y-%m-%d %H:%M:%S'
formatter = coloredlogs.ColoredFormatter(formatter_pattern, time_pattern)

# 定义一个流处理器StreamHandler,将INFO及以上的日志打印到标准错误（stream_handler输出）
stream_handler = logging.StreamHandler()
stream_handler.addFilter(coloredlogs.HostNameFilter())
stream_handler.setLevel(logging.DEBUG)
stream_handler.setFormatter(formatter)

# 按时间切分的TimeRotatingFileHandler
rotate_handler = TimedRotatingFileHandler(filename='./log/scrapy.log', when='midnight', interval=1, backupCount=10)
rotate_handler.setLevel(logging.INFO)
rotate_handler.suffix = '%Y%m%d.log'
rotate_handler.setFormatter(formatter)

# logger,全局使用
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(stream_handler)
logger.addHandler(rotate_handler)
