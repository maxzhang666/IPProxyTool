# http://www.ip3366.net/free/?stype=1
# coding=utf-8

import re

from scrapy import Selector

from proxy import Proxy
from .basespider import BaseSpider


class Ip3366Spider(BaseSpider):
    name = 'ip3366'

    def __init__(self, *a, **kwargs):
        super(Ip3366Spider, self).__init__(*a, **kwargs)

        self.urls = ['http://www.ip3366.net/free/?stype=1&page=%s' % n for n in range(1, 10)]
        self.headers = {
            # 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            # 'Accept-Encoding': 'gzip, deflate',
            # 'Accept-Language': 'en-US,en;q=0.5',
            # 'Cache-Control': 'max-age=0',
            # 'Connection': 'keep-alive',
            # 'Host': 'www.ip3366.net',
            # 'Upgrade-Insecure-Requests': '1',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.11; rv:50.0) Gecko/20100101 Firefox/50.0',
        }

        self.init()

    def parse_page(self, response):
        pattern = re.compile('<tr><td>(.*?)</td><td>(.*?)</td><td>(.*?)</td><td>(.*?)</td><td>(.*?)</td><td>(.*?)</td><td>(.*?)</td></tr>',
                             re.S)
        # items = re.findall(pattern, response.body.decode())
        # items = re.findall(pattern, response.text)
        xel= Selector(response)
        items = xel.xpath('//tbody/tr').extract()
        for i, item in enumerate(items):
            val = Selector(text=item)
            proxy = Proxy()
            proxy.set_value(
                ip=val.xpath('//td[1]/text()').extract_first(),
                port=val.xpath('//td[2]/text()').extract_first(),
                country=val.xpath('//td[5]/text()').extract_first(),
                anonymity=val.xpath('//td[3]/text()').extract_first(),
                source=self.name
            )

            self.add_proxy(proxy=proxy)
