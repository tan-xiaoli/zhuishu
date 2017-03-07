# -*- coding: utf-8 -*-

import MySQLdb
import MySQLdb.cursors
import traceback
from twisted.enterprise import adbapi
from zhuishu import settings
from scrapy.exceptions import DropItem
from zhuishu.lib.mail import QQ_SMTP
from zhuishu.items import BookInfo, ChapterInfo
from zhuishu.lib.tools import get_md5
from . import check_spider_pipeline


class MySqlPipeLine(object):
    """
    MySQL, 使用twisted.enterprise.adbapi
    """

    def __init__(self, dbpool, book_tb):
        self.dbpool = dbpool
        self.book_tb = book_tb

        self.latest_chapter_info = list()

        self.dbpool.runInteraction(self._init_books_tb)

    @classmethod
    def from_settings(cls, settings):
        dbparams = dict(
            host=settings.get('MYSQL_HOST', 'localhost'),
            port=settings.get('MYSQL_PORT', 3306),
            db=settings.get('MYSQL_DBNAME', 'scrapy_zhuishu'),
            user=settings.get('MYSQL_USER', 'root'),
            passwd=settings.get('MYSQL_PASSWD', '123456'),
            charset='utf8',
            cursorclass=MySQLdb.cursors.DictCursor,
        )
        book_tb = settings.get('MYSQL_BOOK_TABLE', 'books')

        dbpool = adbapi.ConnectionPool('MySQLdb', **dbparams)   # **将词典扩展为关键词参数，相当于host=xx, db=yy...

        return cls(dbpool, book_tb)

    @check_spider_pipeline
    def process_item(self, item, spider):
        if isinstance(item, BookInfo):
            try:
                query = self.dbpool.runInteraction(self._insert_books, item, spider)
                query.addErrback(self._handle_error, item, spider)
            except Exception:
                spider.logger.error(traceback.print_exc())
        elif isinstance(item, ChapterInfo):
            try:
                query = self.dbpool.runInteraction(self._insert_chapters, item, spider)
                query.addErrback(self._handle_error, item, spider)
            except Exception:
                spider.logger.error(traceback.print_exc())
        return item

    def _insert_books(self, tx, item, spider):
        """
        添加books
        """
        # 判断数据库中是否存在数据
        cmd = 'SELECT update_time, latest_chapter, latest_chapter_url FROM %s WHERE source="%s" AND book_name="%s"' % (
            self.book_tb, item['source'], item['book_name'])
        ret = tx.execute(cmd)

        if ret == 0:
            # 原来无数据时，添加新数据
            spider.logger.info('Insert books[%s, %s, %s, %s, %s, %s, %s]' %
                                (item['source'], item['book_name'], item['author'], item['update_time'],
                                    item['latest_chapter'], item['latest_chapter_url'], item['chapter_db_name']))

            cmd = '''INSERT INTO %s (source, book_name, author, update_time, latest_chapter, latest_chapter_url, \
                chapter_db_name) VALUES ("%s", "%s", "%s", "%s", "%s", "%s", "%s")''' % \
                (self.book_tb, item['source'], item['book_name'], item['author'], item['update_time'],
                 item['latest_chapter'], item['latest_chapter_url'], item['chapter_db_name'])
            tx.execute(cmd)
        else:
            # 原来有数据时，更新原来的数据
            result = tx.fetchone()

            if result['update_time'] != item['update_time'] or result['latest_chapter'] != item['latest_chapter'] or \
                    result['latest_chapter_url'] != item['latest_chapter_url']:
                spider.logger.info('Update books[%s, %s, %s, %s, %s, %s, %s]' %
                                    (item['source'], item['book_name'], item['author'], item['update_time'],
                                        item['latest_chapter'], item['latest_chapter_url'], item['chapter_db_name']))

                cmd = '''UPDATE %s SET update_time="%s", latest_chapter="%s", latest_chapter_url="%s", \
                    chapter_db_name="%s" WHERE source="%s" AND book_name="%s"''' % \
                    (self.book_tb, item['update_time'], item['latest_chapter'], item['latest_chapter_url'],
                     item['chapter_db_name'], item['source'], item['book_name'])
                tx.execute(cmd)

                # 将新的章节信息添加到last_chapter_info中
                chapter = dict()
                chapter['source'] = item['source']
                chapter['book_name'] = item['book_name']
                chapter['latest_chapter_url'] = item['latest_chapter_url']
                self.latest_chapter_info.append(chapter)

    def _insert_chapters(self, tx, item, spider):
        """
        添加chapters
        """
        # 获取章节数据库名
        md5_name = get_md5('%s_%s' % (item['source'], item['book_name']))

        cmd = 'SELECT chapter_db_name FROM %s WHERE source="%s" AND book_name="%s"' % \
            (self.book_tb, item['source'], item['book_name'])
        ret = tx.execute(cmd)
        db_name = tx.fetchone()['chapter_db_name'] if ret == 1 else md5_name
        spider.logger.debug('book_name=%s db_name=%s' % (item['book_name'], db_name))
        self._check_chapter_tb(tx, db_name, spider)

        # 判断数据库中是否存在数据
        cmd = 'SELECT * FROM %s WHERE source="%s" AND chapter="%s"' % (db_name, item['source'], item['chapter'])
        ret = tx.execute(cmd)

        if ret == 0:
            # 原来无数据时，添加新数据
            spider.logger.info('Insert chapter[%s, %s, %s, %s, %s, %s]' % (
                item['source'], item['book_name'], item['chapter'], item['title'], item['url'], item['content_path']))

            cmd = '''INSERT INTO %s (source, book_name, chapter, title, url, content_path) VALUES \
                ("%s", "%s", "%s", "%s", "%s", "%s")''' % \
                (db_name, item['source'], item['book_name'], item['chapter'], item['title'], item['url'],
                    item['content_path'])
            tx.execute(cmd)

            # 发送邮件
            for chapter in self.latest_chapter_info:
                spider.logger.info('Send E-Mail chapter=%s item=%s' % (str(chapter), str(
                    {'source': item['source'], 'book_name': item['book_name'], 'latest_chapter_url': item['url']})))
                if chapter['source'] == item['source'] and chapter['book_name'] == item['book_name'] and \
                        chapter['latest_chapter_url'] == item['url']:
                    with open(item['content_path'], 'rb') as _f:
                        body = _f.read()
                    subject = '%s_%s_%s_%s' % (item['source'], item['book_name'], item['chapter'], item['title'])
                    qq_email = QQ_SMTP()
                    qq_email.send(subject=subject, body=body)
                    self.latest_chapter_info.remove(chapter)

    def _handle_error(self, failue, item, spider):
        if isinstance(item, BookInfo):
            spider.logger.error('[MySqlPipeLine] Error while dealing with books[%s, %s, %s, %s, %s, %s, %s].' %
                                (item['source'], item['book_name'], item['author'], item['update_time'],
                                    item['latest_chapter'], item['latest_chapter_url'], item['chapter_db_name']))
        elif isinstance(item, ChapterInfo):
            spider.logger.error('[MySqlPipeLine] Error while dealing with chapter[%s, %s, %s, %s, %s, %s]' %
                                (item['source'], item['book_name'], item['chapter'], item['title'], item['url'],
                                    item['content_path']))
        raise DropItem(failue.printDetailedTraceback())

    def _check_chapter_tb(self, tx, db_name, spider):
        """
        判断数据库中，表是否存在
        """
        cmd = 'SELECT * FROM information_schema.INNODB_SYS_TABLES WHERE name="%s/%s"' % (settings.MYSQL_DBNAME, db_name)
        ret = tx.execute(cmd)
        if ret == 0:
            spider.logger.warning('Don\'t exist table[%s]. Create it!' % db_name)
            cmd = '''CREATE TABLE IF NOT EXISTS %s
                (source VARCHAR(100), \
                book_name VARCHAR(100), \
                chapter VARCHAR(100), \
                title VARCHAR(100), \
                url VARCHAR(100), \
                content_path VARCHAR(500)) CHARSET="utf8"''' % db_name
            tx.execute(cmd)

    def _init_books_tb(self, tx):
        """
        初始化books table
        """
        cmd = 'SELECT * FROM information_schema.INNODB_SYS_TABLES WHERE name="%s/%s"' % \
            (settings.MYSQL_DBNAME, self.book_tb)
        ret = tx.execute(cmd)
        if ret == 0:
            cmd = '''CREATE TABLE IF NOT EXISTS %s \
                (id int(11) NOT NULL AUTO_INCREMENT PRIMARY KEY, \
                source VARCHAR(100) NOT NULL,\
                book_name VARCHAR(100) NOT NULL,\
                author VARCHAR(100) NOT NULL, \
                update_time VARCHAR(100) NOT NULL, \
                latest_chapter VARCHAR(100) NOT NULL, \
                latest_chapter_url VARCHAR(100) NOT NULL, \
                chapter_db_name VARCHAR(100) NOT NULL)\
                ENGINE=InnoDB DEFAULT CHARSET="utf8"'''  % self.book_tb
            tx.execute(cmd)

    def spider_closed(self):
        self.dbpool.close()


class MySqldbPipeLine(object):
    """
    MySQL,使用mysqldb
    """

    def __init__(self, dbparams):
        # MySQLdb默认查询结果都是返回tuple,使用DictCursor返回Dict
        self.conn = MySQLdb.connect(host=dbparams['host'], port=dbparams['port'], db=dbparams['db'],
                                    user=dbparams['user'], passwd=dbparams['passwd'], charset=dbparams['charset'],
                                    cursorclass=MySQLdb.cursors.DictCursor)
        self.book_tb = dbparams['book_tb']
        self.conn.autocommit(True)  # 使用事务引擎，设置自动提交，不用每次conn.commit()
        self.cursor = self.conn.cursor()

        self._init_books_tb()

    @classmethod
    def from_settings(cls, settings):
        dbparams = dict(
            host=settings.get('MYSQL_HOST', 'localhost'),
            port=settings.get('MYSQL_PORT', 3306),
            db=settings.get('MYSQL_DBNAME', 'scrapy_zhuishu'),
            user=settings.get('MYSQL_USER', 'root'),
            passwd=settings.get('MYSQL_PASSWD', '123456'),
            charset='utf8',
            book_tb=settings.get('MYSQL_BOOK_TABLE', 'books')
        )
        return cls(dbparams)

    @check_spider_pipeline
    def process_item(self, item, spider):
        if isinstance(item, BookInfo):
            try:
                self._insert_books(item, spider)
            except:
                self.conn.rollback()
                spider.logger.error('[MySqldbPipeLine] Error while dealing with books[%s, %s, %s, %s, %s, %s, %s].' %
                                    (item['source'], item['book_name'], item['author'], item['update_time'],
                                     item['latest_chapter'], item['latest_chapter_url'], item['chapter_db_name']))
                spider.logger.error(traceback.print_exc())
        elif isinstance(item, ChapterInfo):
            try:
                self._insert_chapter(item, spider)
            except:
                self.conn.rollback()
                spider.logger.error('[MySqldbPipeLine] Error while dealing with chapter[%s, %s, %s, %s, %s, %s]' %
                                    (item['source'], item['book_name'], item['chapter'], item['title'], item['url'],
                                     item['content_path']))
                spider.logger.error(traceback.print_exc())
        return item

    def _insert_books(self, item, spider):
        """
        添加books
        """
        # 判断数据库中是否存在数据
        cmd = 'SELECT update_time, latest_chapter FROM %s WHERE source="%s" AND book_name="%s"' % \
            (self.book_tb, item['source'], item['book_name'])
        ret = self.cursor.execute(cmd)  # cursor.execute() 返回的是受影响的row数

        if ret == 0:
            # 原来无数据时，添加新数据
            cmd = '''INSERT INTO %s (source, book_name, author, update_time, latest_chapter, latest_chapter_url, \
                chapter_db_name) VALUES ("%s", "%s", "%s", "%s", "%s", "%s", "%s")''' % \
                (self.book_tb, item['source'], item['book_name'], item['author'], item['update_time'],
                 item['latest_chapter'], item['latest_chapter_url'], item['chapter_db_name'])
            self.cursor.execute(cmd)
        else:
            # 原来有数据时，检查数据，并更新原来的数据
            result = self.cursor.fetchone()
            # 无更新，返回
            if result['update_time'] == item['update_time'] and result['latest_chapter'] == item['latest_chapter']:
                return

            # 更新
            cmd = '''UPDATE %s SET update_time="%s", latest_chapter="%s", latest_chapter_url="%s", \
                chapter_db_name="%s" WHERE source="%s" AND book_name="%s"''' % \
                (self.book_tb, item['update_time'], item['latest_chapter'], item['latest_chapter_url'],
                    item['chapter_db_name'], item['source'], item['book_name'])
            self.cursor.execute(cmd)

    def _insert_chapter(self, item, spider):
        """
        添加chapter
        """
        # 获取章节数据库名
        md5_name = get_md5('%s_%s' % (item['source'], item['book_name']))
        cmd = 'SELECT chapter_db_name FROM %s WHERE source="%s" AND book_name="%s"' % \
            (self.book_tb, item['source'], item['book_name'])
        ret = self.cursor.execute(cmd)
        db_name = self.cursor.fetchone()['chapter_db_name'] if ret == 1 else md5_name
        self._check_chapter_tb(db_name)

        # 判断数据库中是否存在数据
        cmd = 'SELECT * FROM %s WHERE source="%s" AND book_name="%s" AND chapter="%s"' % \
            (db_name, item['source'], item['book_name'], item['chapter'])
        ret = self.cursor.execute(cmd)

        if ret == 0:
            # 原来无数据时，添加新数据
            cmd = '''INSERT INTO %s (source, book_name, chapter, title, url, content_path) VALUES \
                ("%s", "%s", "%s", "%s", "%s", "%s")''' % \
                (db_name, item['source'], item['book_name'], item['chapter'], item['title'], item['url'],
                    item['content_path'])
            self.cursor.execute(cmd)
        else:
            # 原来有数据时，更新原来的数据
            cmd = '''UPDATE %s SET title="%s", url="%s", content_path="%s" WHERE source="%s" AND book_name="%s" AND \
                chapter="%s"''' % (db_name, item['title'], item['url'], item['content_path'], item['source'],
                                   item['book_name'], item['chapter'])
            self.cursor.execute(cmd)

    def _init_books_tb(self):
        """
        初始化books table
        """
        cmd = 'SELECT * FROM information_schema.INNODB_SYS_TABLES WHERE name="%s/%s"' % \
            (settings.MYSQL_DBNAME, self.book_tb)
        ret = self.cursor.execute(cmd)
        if ret == 0:
            cmd = '''CREATE TABLE IF NOT EXISTS %s \
                (id int(11) NOT NULL AUTO_INCREMENT PRIMARY KEY, \
                source VARCHAR(100) NOT NULL,\
                book_name VARCHAR(100) NOT NULL,\
                author VARCHAR(100) NOT NULL, \
                update_time VARCHAR(100) NOT NULL, \
                latest_chapter VARCHAR(100) NOT NULL, \
                latest_chapter_url VARCHAR(100) NOT NULL, \
                chapter_db_name VARCHAR(100) NOT NULL)\
                ENGINE=InnoDB DEFAULT CHARSET="utf8"'''  % self.book_tb
            self.cursor.execute(cmd)

    def _check_chapter_tb(self, db_name, spider):
        """
        判断数据库中，表是否存在
        """
        cmd = 'SELECT * FROM information_schema.INNODB_SYS_TABLES WHERE name="%s/%s"' % \
            (settings.MYSQL_DBNAME, db_name)
        ret = self.cursor.execute(cmd)
        if ret == 0:
            cmd = '''CREATE TABLE IF NOT EXISTS %s \
                (source VARCHAR(100), \
                book_name VARCHAR(100), \
                chapter VARCHAR(100), \
                title VARCHAR(100), \
                url VARCHAR(100), \
                content_path VARCHAR(500)) \
                CHARSET="utf8"'''  % db_name
            self.cursor.execute(cmd)

    def spider_close(self):
        self.cursor.close()
