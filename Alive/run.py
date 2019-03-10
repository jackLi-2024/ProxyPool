#!/usr/bin/python
# coding:utf-8

"""
Author:Lijiacai
Email:1050518702@qq.com
===========================================
CopyRight@Baidu.com.xxxxxx
===========================================
"""
import multiprocessing
import os
import re
import sys
import json
from lib import manager
from alive import alive
from SpiderTool import Request
from Producer_Consumer.QueueTool import QueueProducer
from Producer_Consumer.QueueTool import QueueConsumer
from Producer_Consumer.QueueTool import QueueConsumerProcess


class Main():
    def __init__(self):
        self.conf = manager.get_conf(conf_file="./conf/main.conf")
        self.alive_conf = manager.get_conf(conf_file="./conf/alive.conf")
        self.es_client()
        self.redis_client()
        self.run_alive()

    def es_client(self):
        es_url = "http://" + self.conf.get("es").get("master")
        request = Request.Request(try_time=1, frequence=1)
        response = request.get(url=es_url, response_status=201)
        if response.text == None:
            raise ("ES start error")
        self.es = manager.Es(conf=self.conf)
        pass

    def redis_client(self):
        self.rs1 = manager.Rs(conf=self.conf, db="db1", try_time=1)
        self.rs2 = manager.Rs(conf=self.conf, db="db2", try_time=1)
        if self.rs1.response == None:
            raise ("Redis start error")
        pass

    def first_alive(self, data):
        print data
        data = json.loads(data)
        type_ = "http"
        proxies = [data.get("_source").get("ip") + ":" + data.get("_source").get("ip")]
        print proxies
        ali = alive.Alive(conf=self.alive_conf, proxies=[data])
        proxy = ali.https()
        if proxy:
            self.rs1.write_one({"key": "https-" + proxy, "value": ""})
            type_ = "https"
        else:
            proxy = ali.http()
            if proxy:
                self.rs1.write_one({"key": "http-" + proxy, "value": ""})
            else:
                return
        data["_source"]["status"] = 1
        self.es.write_more([data])

    def second_alive(self):
        self.second_alive_stop = False
        while self.second_alive_stop:
            result = self.rs1.read_one()
            # result = "http-1.2.3.4:9999"
            if re.findall("http", result):
                proxies = [result.split("-")[1]]
                ali = alive.Alive(conf=self.alive_conf, proxies=proxies)
                proxy = ali.http()
                if proxy:
                    self.rs2.write_one({"key": result, "value": ""})

    def run_alive(self):
        process_list = []
        # second_process = multiprocessing.Process(target=self.second_alive, args=())
        # second_process.start()
        # process_list.append(second_process)

        producer = QueueProducer()
        lock = multiprocessing.Lock()
        for i in range(2):
            p = QueueConsumerProcess(target=test, input_queue=producer.queue,
                                     name="process%d" % i, lock=lock)
            p.start()
            process_list.append(p)
        result = self.es.read_more()
        for i in range(len(result)):
            result[i]["_source"]["status"] = -1
        self.es.write_more(datas=result)
        for i in range(len(result)):
            producer.produce(json.dumps(result[i], ensure_ascii=False))
        for p in process_list:
            p.stop()
            p.join()


def test(data):
    print data


if __name__ == '__main__':
    Main()
