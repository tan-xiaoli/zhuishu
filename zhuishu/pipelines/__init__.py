#!/usr/bin/python
# coding=utf-8

import sys
reload(sys)
sys.setdefaultencoding('UTF-8')

import functools


def check_spider_pipeline(process_item_method):
    """
    当有多个pipeline时，判断spider如何使用指定的管道
    """

    @functools.wraps(process_item_method)
    def wrapper(self, item, spider):
        msg = "%%s %s pipeline step" % (self.__class__.__name__,)
        if self.__class__ in spider.pipeline:
            spider.logger.debug(msg % 'executing...')
            return process_item_method(self, item, spider)
        else:
            spider.logger.debug(msg % 'skipping...')
            return item

    return wrapper
