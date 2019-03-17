#!/usr/bin/python
# coding:utf-8

"""
Author:Lijiacai
Email:1050518702@qq.com
===========================================
CopyRight@Baidu.com.xxxxxx
===========================================
"""
# 这里是一个任务定时的任务调度

import os
import sys
import json
import schedule
import setproctitle
from lib import manager


def task():
    os.system("python run.py >> ./log/proxy.log")


def run():
    conf = manager.get_conf(conf_file="./conf/main.conf")
    runtime = int(conf.get("other").get("cycletime"))
    schedule.every(runtime).minutes.do(task)
    while True:
        schedule.run_pending()

if __name__ == '__main__':
    setproctitle.setproctitle("lijiacai_spider_task")
    run()


