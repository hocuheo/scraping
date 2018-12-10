import random
import logging
import requests

from scrapy.exceptions import IgnoreRequest
from urllib.parse import quote, unquote
from elasticsearch_dsl import Index

from common.models import Page


class RandomUserAgentMiddleware(object):
    def __init__(self, settings):
        self.settings = settings
        self.user_agents = settings.get('USER_AGENTS')

    @classmethod
    def from_crawler(cls, crawler):
        settings = crawler.settings
        return cls(settings)

    def process_request(self, request, spider):
        user_agent = random.choice(self.user_agents)
        if request.headers.get('User-Agent') is None and not request.meta.get('selenium'):
            request.headers.setdefault('User-Agent', user_agent)
            logging.info("Random User-Agent: %s", request.headers.get('User-Agent'))


class IgnoreDuplicates():
    def process_request(self, request, spider):
        if not Index('test').exists():
            return None
        page = Page.get(id=quote(request.url),  ignore=404)
        if page:
            raise IgnoreRequest()
        else:
            return None