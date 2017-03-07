# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class BookInfo(Item):
    """
    书的信息
    """
    source = Field()    # 来源
    book_name = Field()  # 书名
    author = Field()    # 作者
    update_time = Field()   # 最后更新时间
    latest_chapter = Field()    # 最新更新章节
    latest_chapter_url = Field()    # 最新更新章节的URL
    chapter_db_name = Field()   # 章节的数据库名


class ChapterInfo(Item):
    """
    章节信息
    """
    source = Field()    # 来源
    book_name = Field()  # 书名
    chapter = Field()   # 章节
    title = Field()  # 章名
    url = Field()   # url
    content_path = Field()   # 内容保存到文件的路径
