#!/usr/bin/python
# coding:utf-8

"""
Author:Lijiacai
Email:1050518702@qq.com
===========================================
CopyRight@Baidu.com.xxxxxx
===========================================
"""

import os
import sys
import json
import time
import setproctitle
from spider import spider
from lib import manager
from SpiderTool import Request
import hashlib
from loggingtool import loggingtool
logging = loggingtool.init_log("proxy", "filetime", level="DEBUG", when="M", backupCount=5,
                       filename="./log/proxy.log")

class Main():
    def __init__(self):
        self.es_client()
        self.run_spider()

    def es_client(self):
        es_file = "conf/main.conf"
        conf = manager.get_conf(conf_file=es_file)
        es_url = "http://" + conf.get("es").get("master")
        request = Request.Request(try_time=100, frequence=1)
        response = request.get(url=es_url, response_status=201)
        if response.text == None:
            raise ("ES start error")
        self.es = manager.Es(conf=conf)

    def run_spider(self):
        spider_file = "conf/spider.conf"
        conf = manager.get_conf(conf_file=spider_file)
        crawler = spider.Spider(conf)
        for spider_name in conf:
            try:
                result = eval("crawler.%s" % spider_name)()
            except Exception as e:
                logging.exception(str(e))
                continue
            if result:
                try:
                    self.es.write_more(self.deal_data(result))
                except Exception as e:
                    logging.exception(str(e))

    def deal_data(self, data):
        result = []
        for one in data:
            struct = {"_index": "proxy", "_type": "proxy", "_id": "", "_source": {}}
            one["status"] = 0
            one["type"] = ""
            one["createTime"] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(time.time()))
            ip_port = one.get("ip") + ":" + one.get("port")
            md = hashlib.md5()
            md.update(ip_port)
            _id = md.hexdigest()
            struct["_id"] = _id
            struct["_source"] = one
            result.append(struct)
        return result


if __name__ == '__main__':
    setproctitle.setproctitle("lijiacai_spider")
    Main()
