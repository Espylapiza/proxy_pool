from itertools import cycle
import scrapy
from scrapy.http import Request
from scrapy.utils.misc import load_object
from settings import PROXY_SOURCES, CHECKERS, BASE_CHECKER
import database as db


class ProxyItem(scrapy.Item):
    def __init__(self, proxy, proxy_type):
        scrapy.Item.__init__(self)
        self["proxy"] = proxy
        self["proxy_type"] = proxy_type

    proxy = scrapy.Field()
    proxy_type = scrapy.Field()


def check_format(proxy):
    import re

    proxy_pattern = r"\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}"
    return re.match(proxy_pattern, proxy)


"""
Default:
{
    'scrapy.downloadermiddlewares.robotstxt.RobotsTxtMiddleware': 100,
    'scrapy.downloadermiddlewares.httpauth.HttpAuthMiddleware': 300,
    'scrapy.downloadermiddlewares.downloadtimeout.DownloadTimeoutMiddleware': 350,
    'scrapy.downloadermiddlewares.defaultheaders.DefaultHeadersMiddleware': 400,
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': 500,
    'scrapy.downloadermiddlewares.retry.RetryMiddleware': 550,
    'scrapy.downloadermiddlewares.ajaxcrawl.AjaxCrawlMiddleware': 560,
    'scrapy.downloadermiddlewares.redirect.MetaRefreshMiddleware': 580,
    'scrapy.downloadermiddlewares.httpcompression.HttpCompressionMiddleware': 590,
    'scrapy.downloadermiddlewares.redirect.RedirectMiddleware': 600,
    'scrapy.downloadermiddlewares.cookies.CookiesMiddleware': 700,
    'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 750,
    'scrapy.downloadermiddlewares.stats.DownloaderStats': 850,
    'scrapy.downloadermiddlewares.httpcache.HttpCacheMiddleware': 900,
}
"""


class ProxySpider(scrapy.Spider):
    name = "proxies_pool"
    custom_settings = {
        "DUPEFILTER_CLASS": "scrapy.dupefilters.BaseDupeFilter",
        "REFERRER_POLICY": "scrapy.spidermiddlewares.referer.NoReferrerPolicy",
        "COOKIES_ENABLED": "False",
        "DOWNLOAD_TIMEOUT": 30,
        "DOWNLOADER_MIDDLEWARES": {
            "core.middlewares.HeadersMiddleware": 210,
            "core.middlewares.RandomUserAgentMiddleware": 220,
            "core.middlewares.ProxyMiddleware": 230,
            "core.middlewares.MyRetryMiddleware": 240,
            "scrapy.downloadermiddlewares.retry.RetryMiddleware": None,
        },
        "ITEM_PIPELINES": {"core.spider.ProxyPipeline": 0},
        "RETRY_HTTP_CODES": [500, 502, 503, 504, 408],
    }
    checking = set()

    def __init__(self):
        self.proxy_sources = [load_object(source)() for source in PROXY_SOURCES]
        self.base_checker = load_object(BASE_CHECKER)()
        self.checkers = [load_object(checker)() for checker in CHECKERS]

    def start_requests(self):
        for source in cycle(self.proxy_sources):
            proxy = db.base_proxy_rand()
            url = source.next_url()
            if proxy:
                proxy = str(proxy, "utf-8")
                yield Request(
                    url,
                    callback=self.parse,
                    meta={"parser": source.parse, "proxy": proxy, "request": True},
                    priority=-5,
                )
            else:
                yield Request(
                    url,
                    callback=self.parse,
                    meta={"parser": source.parse, "request": True},
                    priority=-5,
                )

    def parse(self, response):
        for proxy in response.meta["parser"](response.text):
            if check_format(proxy):
                yield self.check(proxy)

    def check(self, proxy):
        if proxy not in self.checking:
            self.checking.add(proxy)
            if not db.base_proxy_exists(proxy):
                (url, meta) = self.base_checker.request(proxy)
                meta["proxy"] = proxy
                return Request(url, callback=self.check_base, meta=meta)
            else:
                return self.check_addition(proxy)

    def check_base(self, response):
        proxy = response.meta["proxy"]
        proxy = proxy[proxy.rindex("/") + 1 :]
        if self.base_checker.check(proxy, response):
            yield ProxyItem(proxy, "base_proxy")
            yield self.check_addition(proxy)
        else:
            self.checking.remove(proxy)

    def check_addition(self, proxy):
        if not db.exists(proxy):
            return self.check_next(proxy, 0)
        else:
            self.checking.remove(proxy)

    def check_next(self, proxy, checker_index):
        if checker_index == len(self.checkers):
            self.checking.remove(proxy)
            return ProxyItem(proxy, "proxy")
        else:
            checker = self.checkers[checker_index]
            (url, meta) = checker.request(proxy)
            meta["checker_index"] = checker_index
            return Request(url, callback=self.check_response, meta=meta)

    def check_response(self, response):
        checker_index = response.meta["checker_index"]
        checker = self.checkers[checker_index]
        proxy = response.meta["proxy"]
        proxy = proxy[proxy.rindex("/") + 1 :]
        if checker.check(proxy, response):
            return self.check_next(proxy, checker_index + 1)
        else:
            self.checking.remove(proxy)


class ProxyPipeline(object):
    def process_item(self, item, spider):
        proxy = item["proxy"]
        proxy_type = item["proxy_type"]
        if proxy_type == "base_proxy":
            db.base_proxy_add(proxy)
        else:
            db.add(proxy)
        return item
