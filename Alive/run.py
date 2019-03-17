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
import setproctitle
from lib import manager
from alive import alive
from alive.alive import first_alive
from alive.alive import second_alive
from SpiderTool import Request
from Producer_Consumer.QueueTool import QueueProducer
from Producer_Consumer.QueueTool import QueueConsumer
from Producer_Consumer.QueueTool import QueueConsumerProcess
from loggingtool import loggingtool

logging = loggingtool.init_log("alive", "filetime", level="DEBUG", when="M", backupCount=5,
                               filename="./log/alive.log")


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
        response = request.get(url=es_url, response_status="201")
        if response.status_code == None:
            raise ("ES start error")
        self.es = manager.Es(conf=self.conf)
        pass

    def redis_client(self):
        self.rs1 = manager.Rs(conf=self.conf, db="db1", try_time=1)
        if self.rs1.response == None:
            raise ("Redis start error")
        pass

    def run_alive(self):
        process_list = []
        stop_value = multiprocessing.Manager().Value("b", False)
        second_process = multiprocessing.Process(target=second_alive,
                                                 args=(self.conf, self.alive_conf, stop_value))
        second_process.start()
        process_list.append(second_process)

        producer = QueueProducer()
        lock = multiprocessing.Lock()
        for i in range(2):
            p = QueueConsumerProcess(target=first_alive, input_queue=producer.queue,
                                     name="process%d" % i, lock=lock,
                                     args=(self.conf, self.alive_conf))
            p.start()
            process_list.append(p)

        while not stop_value.value:
            result = self.es.read_more()  
            for i in range(len(result)):
                result[i]["_source"]["status"] = -1
            if result:
                self.es.write_more(datas=result)
            for i in range(len(result)):
                producer.produce(json.dumps(result[i], ensure_ascii=False))
        # for p in process_list:
        #     try:
        #         p.stop()
        #     except:
        #         pass
        #         stop_value.value = True
        #     p.join()


if __name__ == '__main__':
    setproctitle.setproctitle("lijiacai_alive")
    Main()
