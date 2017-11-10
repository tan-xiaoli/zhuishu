#!/bin/bash

# 创建mysql所需要到docker container

BASE_IMAGE=docker.io/mysql

# msyql默认端口是3306
# 将数据保存在data下
docker run -d -e TZ="Asia/Shanghai" \
    -v /etc/localtime:/etc/localtime:ro \
    --name "mysql_scrapy" \
    --privileged \
    -h "root" \
    --restart always \
    -v "$PWD/data:/var/lib/mysql:rw" \
    -p 3305:3306 \
    -e MYSQL_ROOT_PASSWORD="123456" \
    -e MYSQL_DATABASE="scrapy_zhuishu" \
    -e MYSQL_USER="test" \
    -e MYSQL_PASSWORD="123456" \
    $BASE_IMAGE --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci

