# -*- coding: utf-8 -*-

import os
import traceback
import sqlite3
from zhuishu import settings
from scrapy.exceptions import DropItem
from zhuishu.items import BookInfo, ChapterInfo
from zhuishu.lib.tools import get_md5
from . import check_spider_pipeline


class SQLitePipeLine(object):
    """
    SQLite3
    """

    def __init__(self, dbparams):
        is_new = False
        if not os.path.exists(dbparams['db']) or not os.path.isfile(dbparams['db']):
            os.mknod(dbparams['db'])
        self.conn = sqlite3.connect(dbparams['db'])
        self.cursor = self.conn.cursor()
        self.book_tb = dbparams['book_tb']

        self._init_books_tb()

    @classmethod
    def from_settings(cls, settings):
        dbparams = dict(
            db=settings.get('SQLITE3_DB', 'sqlite3.db'),
            book_tb=settings.get('SQLITE3_BOOK_TABLE', 'books'),
        )
        return cls(dbparams)

    @check_spider_pipeline
    def process_item(self, item, spider):
        if isinstance(item, BookInfo):
            try:
                self._insert_books(item)
            except:
                self.conn.rollback()
                traceback.print_exc()
                spider.logger.error('[SQLite] Error while dealing with books[%s, %s, %s, %s, %s, %s, %s].' %
                                    (item['source'], item['book_name'], item['author'], item['update_time'],
                                     item['latest_chapter'], item['latest_chapter_url'], item['chapter_db_name']))
                spider.logger.error(traceback.print_exc())
        elif isinstance(item, ChapterInfo):
            try:
                self._insert_chapter(item)
            except:
                self.conn.rollback()
                traceback.print_exc()
                spider.logger.error('[SQLite] Error while dealing with chapter[%s, %s, %s, %s, %s, %s]' %
                                    (item['source'], item['book_name'], item['chapter'], item['title'], item['url'],
                                     item['content_path']))
        return item

    def _insert_books(self, item):
        """
        添加books
        """
        # 获取章节数据库名
        cmd = 'SELECT update_time, latest_chapter FROM "%s" WHERE source="%s" AND book_name="%s"' % \
            (self.book_tb, item['source'], item['book_name'])
        self.cursor.execute(cmd)

        result = self.cursor.fetchone()

        if result is None:
            # 原来无数据时，添加新数据
            cmd = '''INSERT INTO "%s" (source, book_name, author, update_time, latest_chapter, latest_chapter_url, \
                chapter_db_name) VALUES ("%s", "%s", "%s", "%s", "%s", "%s", "%s")''' % \
                (self.book_tb, item['source'], item['book_name'], item['author'], item['update_time'],
                 item['latest_chapter'], item['latest_chapter_url'], item['chapter_db_name'])
            self.cursor.execute(cmd)
        else:
            # 原来有数据时，检查数据，并更新原来的数据
            if result[0] == item['update_time'] and result[1] == item['latest_chapter']:
                return

            # 更新
            cmd = '''UPDATE "%s" SET update_time="%s", latest_chapter="%s", latest_chapter_url="%s", \
                chapter_db_name="%s" WHERE source="%s" AND book_name="%s"''' % \
                (self.book_tb, item['update_time'], item['latest_chapter'], item['latest_chapter_url'],
                    item['chapter_db_name'], item['source'], item['book_name'])
            self.cursor.execute(cmd)
        self.conn.commit()

    def _insert_chapter(self, item):
        """
        添加chapters
        """
        # 获取章节数据库名
        md5_name = get_md5('%s_%s' % (item['source'], item['book_name']))
        cmd = 'SELECT chapter_db_name FROM "%s" WHERE source="%s" AND book_name="%s"' % \
            (self.book_tb, item['source'], item['book_name'])
        self.cursor.execute(cmd)
        result = self.cursor.fetchone()
        db_name = result[0] if result is not None else md5_name
        self._check_chapter_tb(db_name)

        # 判断数据库中是否存在数据
        cmd = 'SELECT * FROM "%s" WHERE source="%s" AND book_name="%s" AND chapter="%s"' % \
            (db_name, item['source'], item['book_name'], item['chapter'])
        self.cursor.execute(cmd)

        result = self.cursor.fetchone()

        if result is None:
            # 原来无数据时，添加新数据
            cmd = '''INSERT INTO "%s" (source, book_name, chapter, title, url, content_path) VALUES \
                ("%s", "%s", "%s", "%s", "%s", "%s")''' % \
                (db_name, item['source'], item['book_name'], item['chapter'], item['title'], item['url'],
                    item['content_path'])
            self.cursor.execute(cmd)
        else:
            # 原来有数据时，更新原来的数据
            cmd = '''UPDATE "%s" SET title="%s", url="%s", content_path="%s" WHERE source="%s" AND book_name="%s" AND \
                chapter="%s"''' % (db_name, item['title'], item['url'], item['content_path'], item['source'],
                                   item['book_name'], item['chapter'])
            self.cursor.execute(cmd)
        self.conn.commit()

    def _init_books_tb(self):
        """
        初始化sqlite3
        """
        cmd = 'SELECT * FROM "%s"' % self.book_tb
        try:
            self.cursor.execute(cmd)    # 无books table，返回：Error: no such table: books
        except:
            cmd = '''CREATE TABLE IF NOT EXISTS "%s" \
                (id int(11) PRIMARY KEY, \
                source VARCHAR(100) NOT NULL, \
                book_name VARCHAR(100) NOT NULL, \
                author VARCHAR(100) NOT NULL, \
                update_time VARCHAR(100) NOT NULL, \
                latest_chapter VARCHAR(100) NOT NULL, \
                latest_chapter_url VARCHAR(100) NOT NULL, \
                chapter_db_name VARCHAR(100) NOT NULL)''' % self.book_tb
            self.cursor.execute(cmd)
            self.conn.commit()

    def _check_chapter_tb(self, db_name):
        """
        判断数据库中，表是否存在
        """
        cmd = 'SELECT * FROM %s' % db_name
        try:
            self.cursor.execute(cmd)
        except:
            cmd = '''CREATE TABLE IF NOT EXISTS "%s" \
                (source VARCHAR(100) NOT NULL, \
                book_name VARCHAR(100) NOT NULL, \
                chapter VARCHAR(100) NOT NULL, \
                title VARCHAR(100), \
                url VARCHAR(100), \
                content_path VARCHAR(500))''' % db_name
            self.cursor.execute(cmd)
            self.conn.commit()

    def spider_closed(self):
        self.cursor.close()
        self.conn.close()
