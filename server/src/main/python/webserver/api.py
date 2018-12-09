import os
import functools
import json
from datetime import datetime

from klein import Klein
from twisted.web.static import File
from scrapers import crawler
from scrapers.spiders.shop import GiganSpider, VerkkoSpider
from twisted.internet import defer
from twisted.internet import threads
from urllib.parse import quote_plus
from common.redis import redis_store

import json

app = Klein()


def get_spider(shop):
    if shop == 'gigantti':
        return GiganSpider
    else:
        return VerkkoSpider

def get_redis_key(shop, query):
    return "{}_{}".format(shop, query)


def store_results(results, query):
    expiration = int(os.getenv('EXPIRATION', 172800))
    for shop, result in results.items():
        if len(result['items']) > 0 and 'cached' not in result:
            redis_store.set(get_redis_key(shop, query), json.dumps(result), expiration)
    return results

def get_result_from_redis(shop, query, size):
    key = get_redis_key(shop, query)
    raw_data = redis_store.get(key)
    if raw_data:
        data = json.loads(raw_data.decode())
        data['cached'] = True
        return defer.maybeDeferred(lambda: data)

    return crawler.run(spider=get_spider(shop), query=query, size=size)

def group_result(shops, results):
    return {
        shop: results[idx]
        for idx, shop in enumerate(shops)
        if results[idx]
    }

def auth(f):
    @functools.wraps(f)
    def wrapper(request, *args, **kwargs):
        if os.getenv('AUTH_ENABLED', 'false').lower() == 'true':
            stamp = float(request.getHeader(b'Authorization') or 0)
            now = datetime.now().timestamp()
            delta = now - stamp
            if  0 <= delta <= 500:
                return f(request, *args, **kwargs)
            else:
                request.setResponseCode(401)
                return 'May dien ah'
        else:
            return f(request, *args, **kwargs)

    return wrapper


@app.route('/', branch=True)
def index(request):
    print(os.path.dirname(__file__))
    resource_path = os.path.abspath(os.path.dirname(__file__ )+ '../../../resources/public')
    print(resource_path)
    return File(resource_path)


@app.route('/crawl')
@auth
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
@auth
def search(request):
    size = int(request.args.get(b'size')[0].decode().strip())
    shops = request.args.get(b'shops')[0].decode().split(',')
    query = quote_plus(request.args.get(b'query')[0].decode().lower().strip())
    deferred = defer.gatherResults([
        get_result_from_redis(shop, query, size) for shop in shops
    ])
    # deferred = crawler.run(spider=get_spider(shops[0]), query=query, size=size)
    deferred.addCallback(lambda results: group_result(shops, results))
    deferred.addCallback(lambda results: store_results(results, query))
    deferred.addCallback(lambda results: json.dumps(results))
    return deferred
