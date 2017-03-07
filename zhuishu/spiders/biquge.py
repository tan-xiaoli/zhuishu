#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
reload(sys)
sys.setdefaultencoding('utf-8')  # python默认环境编码是ascii

import os
import scrapy
import re
from scrapy.spiders import Spider
from scrapy.selector import Selector
from scrapy.http import Request
from zhuishu import settings
from zhuishu.items import BookInfo, ChapterInfo
from zhuishu.pipelines.json_pipeline import JsonWithEncodingWriterPipeLine
from zhuishu.pipelines.mysql_pipeline import MySqlPipeLine, MySqldbPipeLine
from zhuishu.pipelines.sqlite_pipeline import SQLitePipeLine
from zhuishu.lib.tools import get_md5, cn2dig


class BiqugeSpider(Spider):
    """
    笔趣阁http://www.biquge.tw/
    """
    pipeline = set([MySqlPipeLine, ])   # pipeline
    url_set = set()  # 记录url

    name = 'biquge.tw'          # 爬虫名
    allowed_domains = ['biquge.tw']  # 限定域名
    # 起始URL,目录页
    start_urls = [
        'http://biquge.tw/3_3253/',  # 帝霸
        'http://biquge.tw/0_4/',  # 大主宰
        'http://www.biquge.tw/59_59878/',   # 龙王传说
    ]

    spider_all_chapter = settings.SPIDER_ALL_CHAPTER

    # 当运行命令使爬虫运行起来后，会自动运行start_ruls里的url,将url里的内容下载下来，并将下载下来的数据封装给response
    def parse(self, response):
        """
        解析目录页
        """
        hxs = Selector(response)
        book = BookInfo()
        book['source'] = BiqugeSpider.name
        book['book_name'] = hxs.xpath('//meta[@property="og:novel:book_name"]/@content').extract_first()
        book['author'] = hxs.xpath('//meta[@property="og:novel:author"]/@content').extract_first()
        book['update_time'] = hxs.xpath('//meta[@property="og:novel:update_time"]/@content').extract_first()
        book['latest_chapter'] = hxs.xpath('//meta[@property="og:novel:latest_chapter_name"]/@content').extract_first()
        book['latest_chapter_url'] = hxs.xpath(
            '//meta[@property="og:novel:latest_chapter_url"]/@content').extract_first()
        book['chapter_db_name'] = get_md5('%s_%s' % (book['source'], book['book_name']))

        if not BiqugeSpider.spider_all_chapter:
            yield Request(book['latest_chapter_url'], callback=self.parse_content)
        else:
            # 把所有章节扫到数据库中
            for chp in hxs.xpath('//dd'):
                title = chp.xpath('./a/text()').extract_first()
                if re.match(u'第(.+)章', title):
                    url = response.url + chp.xpath('./a/@href').extract_first().split('/')[2]
                    yield Request(url, callback=self.parse_content)
        yield book

    def parse_content(self, response):
        """
        解析章节内容
        """
        md5_url = get_md5(response.url)
        if md5_url in self.url_set:
            pass
        self.url_set.add(md5_url)
        chp = ChapterInfo()
        hxs = Selector(response)
        title = hxs.xpath('//title/text()').extract_first()
        chp['source'] = BiqugeSpider.name
        chp['book_name'] = title.split('_')[1]
        chp['chapter'] = '%04d' % cn2dig(title.split('_')[0].split(u'章')[0].split(u'第')[1].replace(' ', ''))  # 转成4位

        # 过滤异常章节
        if chp['chapter'] == '5061' or chp['chapter'] == '5060':
            return

        chp['title'] = title.split('_')[0].split(u'章')[1].strip()
        chp['url'] = response.url

        content = hxs.xpath('//*[@id="content"]/text()').extract()
        # content处理
        _content = ''
        for line in content:
            line = line.strip()
            _content = _content + '        ' + line + '\n'

        content_path = os.path.join(settings.BOOK_SAVE_PATH, '%s/%s/%s_%s.txt' %
                                    (BiqugeSpider.name, get_md5(chp['book_name']), chp['chapter'],
                                        get_md5(chp['title'])))
        _path = os.path.split(content_path)[0]

        if not os.path.exists(_path):
            os.makedirs(_path)

        if not os.path.isfile(content_path) or os.path.getsize(content_path) == 0:
            with open(content_path, 'w') as f:
                f.write(_content)

        chp['content_path'] = content_path
        yield chp
