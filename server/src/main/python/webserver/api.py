import os

from klein import Klein
from twisted.web.static import File
from scrapers import crawler
from scrapers.spiders.shop import GiganSpider, VerkkoSpider
from twisted.internet import defer
from urllib.parse import quote_plus
# from common.redis import redis_store

import json

app = Klein()


def get_spider(shop):
    if shop == 'gigantti':
        return GiganSpider
    else:
        return VerkkoSpider


# def store_results(results, query):
#     for shop, result in results.items():

#     return results

def group_result(shops, results):
    return {
        shop: results[idx]
        for idx, shop in enumerate(shops)
        if results[idx]
    }

@app.route('/', branch=True)
def index(request):
    print(os.path.dirname(__file__))
    resource_path = os.path.abspath(os.path.dirname(__file__ )+ '../../../resources/public')
    print(resource_path)
    return File(resource_path)


@app.route('/crawl')
def crawl(request):
    d = crawler.run([
        'http://kenh14.vn/',
        'http://www.4chan.org',
        'https://twitter.com/Twitter',
        'https://www.reddit.com/r/doge',
        'https://www.reddit.com/r/news',
        'https://medium.com/',
        'https://www.quora.com/What-is-a-software-developer-What-do-they-do'
        'https://academia.stackexchange.com/'
    ])
    d.addCallback(lambda output: json.dumps(output))
    return "test"


@app.route('/search')
def search(request):
    size = int(request.args.get(b'size')[0].decode().strip())
    shops = request.args.get(b'shops')[0].decode().split(',')
    query = quote_plus(request.args.get(b'query')[0].decode().lower().strip())
    deferred = defer.gatherResults([
        crawler.run(spider=get_spider(shop), query=query, size=size) for shop in shops
    ])
    # deferred = crawler.run(spider=get_spider(shops[0]), query=query, size=size)
    deferred.addCallback(lambda results: group_result(shops, results))
    # deferred.addCallback(lambda results: store_results(results, query))
    deferred.addCallback(lambda results: json.dumps(results))
    return deferred
