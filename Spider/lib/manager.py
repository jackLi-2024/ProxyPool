#!/usr/bin/python
# coding:utf-8

"""
Author:Lijiacai
Email:1050518702@qq.com
===========================================
CopyRight@Baidu.com.xxxxxx
===========================================
"""
# 从配置文件获取代理的url---爬虫---从配置文件获取es配置---写入es
# 从配置文件获取redis---将探活代理写入es
# 主要实现相关接口封装爬虫接口，实现自动写入es，加入探活队列

import os
import sys
import json
import ConfigParser
from elasticsearch import Elasticsearch
from elasticsearch import helpers


def get_conf(conf_file):
    config = ConfigParser.ConfigParser()
    config.read(conf_file)
    return config._sections


class Es():
    def __init__(self, conf, index_type="proxy_index"):
        """
        init
        :param conf:  dict type
            {
                "es": {
                    "__name__": "es",
                    "es_servers": "[{\"host\": \"106.12.217.41\",\"port\": \"9200\"}]"
                },
                "proxy_index": {
                    "__name__": "proxy_index",
                    "index_name": "proxy",
                    "schema_path": "./schema/proxy.json"
                }
            }
        """
        self.conf = conf
        self.index_name = self.conf.get(index_type).get("index_name")
        self.es_servers = self.conf.get("es").get("es_servers")
        self.schema_path = self.conf.get(index_type).get("schema_path")
        self.es = Elasticsearch(eval(self.es_servers))
        if not self.index_exist():
            proxy_dict = self.read_setting(self.schema_path)
            self.create_index(body=eval(proxy_dict))
        else:
            print("Current index already exists(index name = %s)" % self.index_name)

    def index_exist(self):
        return self.es.indices.exists(self.index_name)

    def create_index(self, body):
        self.es.indices.create(index=self.index_name, body=body)

    def delete_index(self):
        self.es.indices.delete(index=self.index_name)
        return True

    def write_one(self):
        pass

    def write_more(self, datas):
        helpers.bulk(self.es, actions=datas)

    def read_setting(self, filename):
        with open(filename, "r") as f:
            content = f.read()
        return content


def test():
    print get_conf("../conf/spider.conf")


def test1():
    conf = {
        "es": {
            "__name__": "es",
            "es_servers": "[{\"host\": \"106.12.217.41\",\"port\": \"9200\"}]"
        },
        "proxy_index": {
            "__name__": "proxy_index",
            "index_name": "proxy",
            "schema_path": "./schema/proxy.json"
        }
    }
    es = Es(conf)


if __name__ == '__main__':
    test1()
