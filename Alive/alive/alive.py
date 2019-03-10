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
        if response.text == None:
            return None
        else:
            if response.proxy:
                return response.proxy


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
