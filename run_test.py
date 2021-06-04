import logging
import os
import re
import sys

import requests
import logging.config

from crawler.spiders.proxy.sixsixip import SixSixIpSpider
from sql import SqlManager

from requests.packages.urllib3.exceptions import InsecureRequestWarning

# 禁用安全请求警告
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def local_go(code):
    ip_handle = open('./ip.txt')

    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:50.0) Gecko/20100101 Firefox/50.0',
        'origin': 'https://greasyfork.org'
    }

    lines = ip_handle.readlines()
    for item in lines:
        try:
            session = requests.session()
            session.verify = None
            session.headers.update(headers)
            session.proxies = {'http': item}

            response = session.get('https://greasyfork.org/zh-CN/scripts/{}'.format(code))
            # 二次访问 获取authcode
            response = session.get(response.url)

            pattern = re.compile("data-ping-url=\"(.+?)\"", re.S)
            infos = re.findall(pattern, response.text)

            post_url = "https://greasyfork.org{}".format(infos[0])

            post_response = session.post(post_url, {})
            logger.info('代理{},请求结果:{}({})'.format(item, '成功' if post_response.status_code == 204 else '失败', post_response.status_code))
        except Exception as e:
            logger.error(e)


logging_path = os.path.split(
    os.path.realpath(__file__))[0] + os.sep + 'logging.conf'
logging.config.fileConfig(logging_path)
logger = logging.getLogger('gogogo')
if __name__ == '__main__':
    # sql = SqlManager()

    go_type = sys.argv[1] or 'local'
    code = sys.argv[2] or '384538'

    if go_type == 'local':
        local_go(code)
