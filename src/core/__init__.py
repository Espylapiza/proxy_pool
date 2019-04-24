from .spider import ProxySpider
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings


def run():
    settings = Settings()
    process = CrawlerProcess(settings)
    process.crawl(ProxySpider())
    process.start()
