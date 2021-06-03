from crawler.spiders.proxy.sixsixip import SixSixIpSpider

if __name__ == '__main__':
    spider = SixSixIpSpider()
    spider.start_requests()