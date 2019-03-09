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
from SpiderTool.Request import Request
from lxml import etree
import logging

cur_dir = os.path.split(os.path.realpath(__file__))[0]
sys.path.append("%s/" % cur_dir)


class Spider(object):
    """
        return {"ip": ip, "port": port, "location": location}
    """

    def __init__(self, conf):
        """
        init
        :param conf:
            {"kuaidaili":
                {"url":"https://www.kuaidaili.com/free/inha/","data":"2"},
             "ip89":
                {"url":"http://www.89ip.cn/","data":"1"},
            ....
            }
        """

        self.conf = conf

    def kuaidaili(self):
        conf = self.conf.get("kuaidaili")
        pages = conf.get("data")
        request = Request()
        result = []
        for p in range(1, int(pages) + 1):
            url = conf.get("url") + str(p)
            response = request.get(url=url)
            time.sleep(1)
            if response.text == None:
                raise ("request error!")
            html = response.text
            page = etree.HTML(html)
            tds = page.xpath("//td[@data-title]")
            for i in range(0, len(tds), 7):
                ip = tds[i].text
                port = tds[i + 1].text
                location = tds[i + 4].text
                result.append({"ip": ip, "port": port, "location": location})
        return result

    def ip89(self):
        conf = self.conf.get("ip89")
        return conf


def test():
    conf = {"kuaidaili": {"url": "https://www.kuaidaili.com/free/inha/", "data": "1"},
            "ip89": {"url": "http://www.89ip.cn/", "data": "1"}
            }
    spider = Spider(conf=conf)
    print json.dumps(spider.kuaidaili(), ensure_ascii=False)


if __name__ == '__main__':
    test()
