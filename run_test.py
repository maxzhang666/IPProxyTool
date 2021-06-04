import logging.config
import os
import re
import sys
import threading
import time
import urllib.parse
from concurrent.futures import ThreadPoolExecutor
from hashlib import sha1

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# 禁用安全请求警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
logging_path = os.path.split(
    os.path.realpath(__file__))[0] + os.sep + 'logging.conf'
logging.config.fileConfig(logging_path)
logger = logging.getLogger('gogogo')


def get_sha1(str):
    s1 = sha1()
    s1.update(str.encode())
    return s1.hexdigest()


class TaskExecuter():
    def ExecuteTask(self, para: dict):
        ip = str(re.findall(r'(?<!\d)\d{1,3}\.\d{1,3}.\d{1,3}.\d{1,3}(?=\:)', para['proxy']['http'])[0])
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.212 Safari/537.36',
            'origin': 'https://greasyfork.org',
            'REMOTE_ADDR': ip,
            'X-Forwarded-For': ip,
            'HTTP_CLIENT_IP': ip,
            'HTTP_X_FORWARDED_FOR': ip
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

            session.headers['referer'] = response.url

            ping_url_pattern = re.compile("data-ping-url=\"(.+?)\"", re.S)
            script_id_pattern = re.compile("data-script-id=\"(.+?)\"", re.S)
            ping_key_pattern = re.compile("data-ping-key=\"(.+?)\"", re.S)
            ip_address_pattern = re.compile("data-ip-address=\"(.+?)\"", re.S)

            ping_url_source = re.findall(ping_url_pattern, response.text)
            script_id_source = re.findall(script_id_pattern, response.text)
            ping_key_source = re.findall(ping_key_pattern, response.text)
            ip_address_source = re.findall(ip_address_pattern, response.text)

            ping_key = get_sha1('{}{}{}'.format(ip_address_source[0], script_id_source[0], ping_key_source[0]))

            post_url = "https://greasyfork.org{}&mo=1&locale=1&ping_key={}".format(ping_url_source[0], urllib.parse.quote(ping_key))

            post_response = session.post(post_url, {})
            stop_time = time.perf_counter()
            cost = stop_time - start_time
            logger.info('代理{},请求结果:{}({});耗时:{}秒;[{}][{}][{}]'.format(para, '成功' if post_response.status_code == 204 else '失败', post_response.status_code, cost, ip_address_source[0], script_id_source[0], ping_key_source[0]))
        except Exception as e:
            logger.error(e)


class IpTask(TaskExecuter):
    def ExecuteTask(self, para: dict):
        s = requests.session()
        # s.proxies = {'http': 'http://{}'.format(para['proxy']['http'].replace('\n', ''))}
        s.proxies = {'http': 'http://{}'.format(para['proxy']['http'].replace('\n', ''))}
        response = s.get('http://icanhazip.com')
        logger.info('ip:{}'.format(response.text))


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

    def init_task(self, ips, codes, executer: TaskExecuter):
        for ip in ips:
            for code in codes:
                # self.call_custom_func(executer, {'proxy': {'http': 'http://{}'.format(ip.replace('\n', ''))}, 'code': code})
                self.call_custom_func(executer, {'proxy': {'http': '{}'.format(ip.replace('\n', ''))}, 'code': code})

    def call_custom_func(self, func: TaskExecuter, para):
        self.thread_pool.submit(func.ExecuteTask, para)


if __name__ == '__main__':
    # sql = SqlManager()

    # logger.info(get_sha1("{}{}{}".format('118.143.39.133', '426806', 'fde195a51b08a754d6ff')))

    go_type = sys.argv[1] or 'local'
    code = sys.argv[2] or '384538'

    if go_type == 'local':
        ip_handle = open('./ip.txt')
        ips = ip_handle.readlines()

        executer = TaskExecuter()

        task = TaskThread(1)
        task.init_task(ips, [code], executer)
    logger.info('任务生成完成')
