import os
import pymongo
import logging
from scrapy import signals
from scrapy.crawler import Crawler
from scrapy.utils.project import get_project_settings

from scrapers.spiders.general import GeneralSpider
from scrapers.spiders.aio import AIOSpider


os.environ['SCRAPY_SETTINGS_MODULE'] = 'scrapers.settings'

def run(spider=AIOSpider, *args, **kwargs):
    settings = get_project_settings()

    runner = GeneralCrawler(spider, settings=settings)
    return runner.crawl(
        *args,
        **kwargs
    )


def print_err(e):
    logging.exception(e)

class GeneralCrawler(Crawler):
    count = 0
    items = []
    def crawl(self, *args, **kwargs):
        logging.info(self.settings)
        # mongo_host = self.settings.get('MONGODB_HOST')
        # mongo_port = self.settings.get('MONGODB_PORT')
        # mongo_db = self.settings.get('MONGODB_DB')
        # mongo_user=self.settings.get('MONGODB_USER')
        # mongo_pass = self.settings.get('MONGODB_PASS')
        # self.connection = pymongo.MongoClient(
        #     host=mongo_host,
        #     port=mongo_port,
        #     username=mongo_user,
        #     password=mongo_pass,
        #     maxPoolSize = 200
        # )
        # self.db = self.connection
        # logging.info(self.connection.server_info())
        logging.info("Success connection")

        self.signals.connect(self.item_scraped, signals.item_scraped)
        d = super(GeneralCrawler, self).crawl(runner=self, *args, **kwargs)
        d.addCallback(self.results)
        d.addErrback(print_err)
        return d

    def item_scraped(self, item, response, spider):
        if item:
            self.items.append(dict(item))

    def results(self, _):
        return {
            "shop": self.spidercls.name,
            "count": self.count,
            "items": self.items
        }
