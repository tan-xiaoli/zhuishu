# -*- coding: utf-8 -*-

import subprocess
import time

SLEEP_TIME = 5 * 60    # 每5分钟check一次


def start_spider():
    p = subprocess.Popen('scrapy crawl biquge.tw &', shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    p.wait()    # 等待子进程结束


if __name__ == '__main__':
    while 1:
        start_spider()
        time.sleep(SLEEP_TIME)
