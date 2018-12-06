# -*, coding: utf-8 -*-

BOT_NAME = 'product_scrapers'

LOG_LEVEL = 'DEBUG'

SPIDER_MODULES = ['scrapers.spiders']
NEWSPIDER_MODULE = 'scrapers.spiders'

USER_AGENT = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'
RETRY_ENABLED= True
RETRY_TIMES = 3
ROBOTSTXT_OBEY = True

# CONCURRENT_REQUESTS = 100
CLOSESPIDER_ITEMCOUNT = 5400

DOWNLOAD_DELAY = 3

CONCURRENT_REQUESTS_PER_DOMAIN = 4
CONCURRENT_REQUESTS = 100
DEPTH_LIMIT = 3

# CONCURRENT_REQUESTS_PER_IP = 100
COOKIES_ENABLED=True

DEFAULT_REQUEST_HEADERS = {
  'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
  'Accept-Language': 'en',
}

# See http://scrapy.readthedocs.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
    # 'scrapers.middlewares.RandomUserAgentMiddleware': 399,
    # 'scrapers.middlewares.IgnoreDuplicates': 543,
    'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
}

ITEM_PIPELINES = {
    # 'scrapers.pipelines.ElasticPipeline': 300
}
