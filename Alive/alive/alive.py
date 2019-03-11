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
import re
import sys
import json
from lib import manager
from SpiderTool import Request


class Alive():
    def __init__(self, conf, proxies):
        self.conf = conf
        self.request = Request.Request(proxies=proxies, try_time=5, timeout=2)

    def http(self):
        test_url = self.conf.get("http").get("alive_url")
        return self.deal(test_url)

    def https(self):
        test_url = self.conf.get("https").get("alive_url")
        return self.deal(test_url)

    def deal(self, url):
        response = self.request.get(url=url)
        if response.text == None or response.status_code == None:
            return None
        else:
            if response.proxy:
                return response.proxy


def first_alive(data, conf, alive_conf):
    data = json.loads(data)
    proxies = [data.get("_source").get("ip") + ":" + data.get("_source").get("port")]
    ali = Alive(conf=alive_conf, proxies=data)
    proxy = ali.https()
    if proxy:
        out = {"key": "https-" + proxy, "value": ""}
    else:
        proxy = ali.http()
        if proxy:
            out = {"key": "http-" + proxy, "value": ""}
        else:
            return
    rs1 = manager.Rs(conf=conf, db="db1", try_time=1)
    es = manager.Es(conf=conf)
    rs1.write_one(out)
    data["_source"]["status"] = 1
    es.write_more([data])


def second_alive(conf, alive_conf, second_alive_stop):
    rs1 = manager.Rs(conf=conf, db="db1", try_time=1)
    rs2 = manager.Rs(conf=conf, db="db2", try_time=1)
    while not second_alive_stop.value:
        result = rs1.read_one()
        # result = "http-1.2.3.4:9999"
        if re.findall("http", result):
            proxies = [result.split("-")[1]]
            ali = Alive(conf=alive_conf, proxies=proxies)
            proxy = ali.http()
            if proxy:
                rs2.write_one({"key": result, "value": ""})


def test():
    conf = {
        "http": {
            "alive_url": "http://www.baidu.com"
        },
        "https": {
            "alive_utl": "https://www.baidu.com"
        }
    }
    proxies = ["124.93.201.59:42672", "61.164.39.68:53281"]
    alive = Alive(conf=conf, proxies=proxies)
    print alive.http()


if __name__ == '__main__':
    test()
