#!/usr/bin/python
# coding=utf-8

import sys
reload(sys)
sys.setdefaultencoding('UTF-8')

import json
import codecs
from collections import OrderedDict
from . import check_spider_pipeline


class JsonWithEncodingWriterPipeLine(object):
    """
    Json带编码输出到文件
    """

    def __init__(self, json_file):
        self.file = codecs.open(json_file, 'wb', encoding='utf-8')

    def __del__(self):
        self.file.close()

    @classmethod
    def from_settings(cls, settings):
        json_file = settings.get('JSON_FILE', 'info.json')
        return cls(json_file)

    @check_spider_pipeline
    def process_item(self, item, spider):
        line = json.dumps(OrderedDict(item), ensure_ascii=False, sort_keys=False) + '\n'
        self.file.write(line)
        return item

    def spider_closed(self):
        self.file.close()
