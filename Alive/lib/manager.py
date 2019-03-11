#!/usr/bin/python
# coding:utf-8

"""
Author:Lijiacai
Email:1050518702@qq.com
===========================================
CopyRight@Baidu.com.xxxxxx
===========================================
"""
import ConfigParser
import os
import sys
import json
import redis
from elasticsearch import Elasticsearch
from elasticsearch import helpers


def get_conf(conf_file):
    config = ConfigParser.ConfigParser()
    config.read(conf_file)
    return config._sections


class Es():
    def __init__(self, conf, index_type="proxy_index"):
        self.conf = conf
        self.es_servers = self.conf.get("es").get("es_servers")
        self.index_name = self.conf.get(index_type).get("index_name")
        self.read_num = int(self.conf.get(index_type).get("read_num"))
        self.es = Elasticsearch(eval(self.es_servers))
        if not self.index_exist():
            raise ("Current index doesn't exist(index name = %s)" % self.index_name)

    def index_exist(self):
        return self.es.indices.exists(self.index_name)

    def write_more(self, datas):
        helpers.bulk(self.es, actions=datas)

    def read_more(self):
        body = {
            "query": {
                "match":
                    {
                        "status": 0
                    }
            },
            # "from": 1,
            "size": self.read_num
        }

        result = self.es.search(index=self.index_name, doc_type=self.index_name, body=body)
        return result["hits"]["hits"]


class Rs():
    def __init__(self, conf, db="db1", try_time=10):
        """
        :param conf:
        :param db:
        """
        self.conf = conf
        self.db = eval(self.conf.get("redis").get(db))
        self.connection_timeout = self.conf.get("redis").get("connection_timeout", None)
        self.alive_time = int(self.db.get("alive_time", "0"))
        host = self.db.get("host")
        port = int(self.db.get("port"))
        password = self.db.get("password", None)
        database = int(self.db.get("database", "0"))
        pool = redis.ConnectionPool(host=host, port=port, password=password, db=database,
                                    socket_connect_timeout=float(self.connection_timeout),
                                    decode_responses=True)
        self.rs = redis.Redis(connection_pool=pool)
        self.response = None
        for i in range(try_time):
            try:
                self.response = self.rs.ping()
                break
            except:
                continue
        if self.response== None:
            raise (AssertionError,"Connect redis defeat")

    def write_one(self, data):
        """
        :param data:
                {"key":"....","value": "..."}
        :return:
        """
        if not self.alive_time:
            self.alive_time = None
        self.rs.set(data["key"], data["value"], ex=self.alive_time)

    def write_more(self, data):
        pass

    def read_more(self, pattern):
        """
        :param pattern:
        :return:
        """
        return self.rs.keys(pattern=pattern)

    def read_one(self):
        """
        :return:
        """
        return self.rs.randomkey()


def test():
    conf = {
        "es": {
            "__name__": "es",
            "es_servers": "[{\"host\": \"106.12.217.41\",\"port\": \"9200\"}]"
        },
        "proxy_index": {
            "__name__": "proxy_index",
            "index_name": "proxy",
            "read_num": "20"
        },
        "redis": {
            "db1": "{\"host\": \"106.12.217.41\", \"port\": \"6379\",\"database\":\"10\",\"password\":\"123456\",\"alive_time\": \"3\"}",
            "connection_timeout": "1"
        }
    }
    es = Es(conf)
    print len(es.read_more())
    # rs = Rs(conf=conf, db="db1")
    # data = {"key": "hello", "value": "lijiacai"}
    # rs.write_one(data)
    # print rs.read_one()


if __name__ == '__main__':
    test()
