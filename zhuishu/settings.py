# -*- coding: utf-8 -*-

# Scrapy settings for zhuishu project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#     http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
#     http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html

import os

PROJECT_DIR = os.path.abspath(os.path.dirname(__file__))  # 项目路径

BOT_NAME = 'zhuishu'

SPIDER_MODULES = ['zhuishu.spiders']
NEWSPIDER_MODULE = 'zhuishu.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
USER_AGENT = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.75 Safari/537.36'

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Configure maximum concurrent requests performed by Scrapy (default: 16)
# CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See http://scrapy.readthedocs.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
# DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
# CONCURRENT_REQUESTS_PER_DOMAIN = 16
# CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
# COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
# TELNETCONSOLE_ENABLED = False

# Override the default request headers:
DEFAULT_REQUEST_HEADERS = {
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
    'Accept-Encoding': 'gzip, deflate, sdch, br',
    'Accept-Language': 'zh-CN,zh;q=0.8',
}

# Enable or disable spider middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/spider-middleware.html
# SPIDER_MIDDLEWARES = {
#    'zhuishu.middlewares.MyCustomSpiderMiddleware': 543,
# }

# Enable or disable downloader middlewares
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
# DOWNLOADER_MIDDLEWARES = {
#    'zhuishu.middlewares.MyCustomDownloaderMiddleware': 543,
# }

# Enable or disable extensions
# See http://scrapy.readthedocs.org/en/latest/topics/extensions.html
# EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
# }

# Configure item pipelines
# See http://scrapy.readthedocs.org/en/latest/topics/item-pipeline.html
# item按照数字从低到高的顺序，通过pipeline,这些数字定义在0-1000范围内
ITEM_PIPELINES = {
    'zhuishu.pipelines.mysql_pipeline.MySqlPipeLine': 300,
}

# Enable and configure the AutoThrottle extension (disabled by default)
# See http://doc.scrapy.org/en/latest/topics/autothrottle.html
# AUTOTHROTTLE_ENABLED = True
# The initial download delay
# AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
# AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
# AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
# AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
# HTTPCACHE_ENABLED = True
# HTTPCACHE_EXPIRATION_SECS = 0
# HTTPCACHE_DIR = 'httpcache'
# HTTPCACHE_IGNORE_HTTP_CODES = []
# HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

# -------------------------------------------------------
# spider all chapter
SPIDER_ALL_CHAPTER = False  # 扫所有章节

# log settings for user
ENABLE_DEBUG = False

LOG_ENABLED = False  # 是否启用logging
LOG_ENCODING = 'utf-8'  # logging使用编码
LOG_FORMAT = '%(levelname)s %(asctime)s [%(filename)s:%(lineno)d] %(message)s'  # log格式
if ENABLE_DEBUG:
    LOG_LEVEL = 'DEBUG'  # log的最低级别，CRITICAL、 ERROR、WARNING、INFO、DEBUG
    LOG_STDOUT = False  # 如果为 True ，进程所有的标准输出(及错误)将会被重定向到log中
else:
    LOG_FILE = os.path.join(PROJECT_DIR, '../log/scrapy.log')  # logging输出文件名,不再STDOUT
    LOG_LEVEL = 'INFO'  # log的最低级别，CRITICAL、 ERROR、WARNING、INFO、DEBUG
    LOG_STDOUT = False  # 如果为 True ，进程所有的标准输出(及错误)将会被重定向到log中

# Mail设置
<<<<<<< Updated upstream
MAIL_HOST = 'smtp.qq.com'    # SMTP主机
MAIL_PORT = '465'    # SMTP端口
MAIL_USER = 'tan-xiaoli@qq.com'    # SMTP用户
MAIL_PASS = 'xxxxxxxxx'    # 用于SMTP认证(输入自己的SMTP密码)
MAIL_SENDER = 'tan-xiaoli@qq.com'   # MAIL发送者，与SMTP用户一直
=======
MAIL_HOST = 'smtp.qq.com'  # SMTP主机
MAIL_PORT = '465'  # SMTP端口
MAIL_USER = 'tan-xiaoli@qq.com'  # SMTP用户
MAIL_PASS = ''  # 用于SMTP认证
MAIL_SENDER = 'tan-xiaoli@qq.com'  # MAIL发送者，与SMTP用户一直
>>>>>>> Stashed changes
MAIL_RECEIVERS = ['tan-xiaoli@qq.com']  # 邮件接收者

# Json settings for user
JSON_FILE = os.path.join(PROJECT_DIR, 'json/info.json')

# Book save path
BOOK_SAVE_PATH = os.path.join(PROJECT_DIR, 'books/')

# MySQL settings for user
MYSQL_HOST = '127.0.0.1'
MYSQL_PORT = 3305
MYSQL_DBNAME = 'scrapy_zhuishu'
MYSQL_USER = 'root'
MYSQL_PASSWD = '123456'
MYSQL_BOOK_TABLE = 'books'

# SQLite3 settings for user
SQLITE3_DB = os.path.join(PROJECT_DIR, 'db/sqlite3.db')
SQLITE3_BOOK_TABLE = 'books'
