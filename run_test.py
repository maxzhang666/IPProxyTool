import logging.config
import os
import re
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# 禁用安全请求警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
logging_path = os.path.split(
    os.path.realpath(__file__))[0] + os.sep + 'logging.conf'
logging.config.fileConfig(logging_path)
logger = logging.getLogger('gogogo')


class TaskThread():

    def __init__(self, num: int = 10):
        # 线程池+线程同步改造添加代码处1/5： 定义锁和线程池
        # 我们第二大节中说的是锁不能在线程类内部实例化，这个是调用类不是线程类，所以可以在这里实例化
        self.threadLock = threading.Lock()
        # 定义2个线程的线程池
        self.thread_pool = ThreadPoolExecutor(num)
        # 定义2个进程的进程池。进程池没用写在这里只想表示进程池的用法和线程池基本一样
        # self.process_pool = ProcessPoolExecutor(2)
        pass

    def main_logic(self, ips, codes):

        for ip in ips:
            for code in codes:
                self.call_do_something({'proxy': {'http': ip}, 'code': code})

    # 线程池+线程同步改造添加代码处2/5： 添加一个通过线程池调用do_something的中间方法。参数与do_something一致
    def call_do_something(self, para):
        self.thread_pool.submit(self.do_request, para)

    def do_request(self, para):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:50.0) Gecko/20100101 Firefox/50.0',
            'origin': 'https://greasyfork.org'
        }

        try:
            start_time = time.perf_counter()
            session = requests.session()
            session.verify = None
            session.headers.update(headers)
            session.proxies = para['proxy']

            response = session.get('https://greasyfork.org/zh-CN/scripts/{}'.format(para['code']))
            # 二次访问 获取authcode
            response = session.get(response.url)

            pattern = re.compile("data-ping-url=\"(.+?)\"", re.S)
            infos = re.findall(pattern, response.text)

            post_url = "https://greasyfork.org{}".format(infos[0])

            post_response = session.post(post_url, {})
            stop_time = time.perf_counter()
            cost = stop_time - start_time
            logger.info('代理{},请求结果:{}({});耗时:{}秒'.format(para, '成功' if post_response.status_code == 204 else '失败', post_response.status_code, cost))
        except Exception as e:
            logger.error(e)


if __name__ == '__main__':
    # sql = SqlManager()

    go_type = sys.argv[1] or 'local'
    code = sys.argv[2] or '384538'

    if go_type == 'local':
        ip_handle = open('./ip.txt')
        ips = ip_handle.readlines()
        task = TaskThread(100)
        task.main_logic(ips, [code])
    logger.info('任务生成完成')
