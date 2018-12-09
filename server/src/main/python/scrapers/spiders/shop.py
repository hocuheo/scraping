import scrapy
import math


# https://www.gigantti.fi/search?SearchTerm=ssd&ContentElementCount=300
# .result-sidebar .count
# .mini-product
# .product-name ::href
# .product-name ::title
# .product-price font
# .product-number::text (sku)
class GiganSpider(scrapy.Spider):
    name = 'gigantti'
    info_selectors = {
        "count": ".result-sidebar .count::text",
        "item": ".mini-product"
    }
    item_selectors = {
        "image": ".product-image-link img::attr(data-src)",
        "link": ".product-name::attr(href)",
        "name": ".product-name::attr(title)",
        "price": ".product-price *::text",
        "sku": ".product-number::text"
    }
    def __init__(self,
                 runner,
                 query,
                 size,
                 *args,
                 **kwargs):
        super(GiganSpider, self).__init__(*args, **kwargs)
        self.page = 1
        self.total_pages = math.ceil(size / 12)
        self.url = "https://www.gigantti.fi/search?SearchTerm={query}".format(
            query=query
        )
        #&PageNumber=1
        self.url_next = "https://www.gigantti.fi/INTERSHOP/web/WFS/store-gigantti-Site/fi_FI/-/EUR/ViewParametricSearchBySearchIndex-OfferPaging?SearchTerm={query}&SearchParameter=%26%40QueryTerm%3D{query}%26online%3D1&SortingAttribute=&ContentElementCount=13&StoreElementCount=0&searchResultTab=Products".format(
            query=query
        )
        self.logger.info(self.url)
        self.runner = runner

    def start_requests(self):
        self.logger.info("Starting request {}".format(self.url))
        yield scrapy.Request(url=self.url, callback=self.parse)

    def parse(self, response):
        items = response.css(self.info_selectors['item'])
        if self.page == 1:

            count = response.css(self.info_selectors['count']).extract_first()
            self.runner._count = count
        for item in items:
            item = {
                key: item.css(selector).extract_first()
                for key, selector in self.item_selectors.items()
            }
            item['image'] = response.urljoin(item['image'])
            yield item

        if self.page < self.total_pages:
            self.page += 1
            yield scrapy.Request(
                url=self.url + "&PageNumber={}".format(self.page - 1),
                callback=self.parse
            )

# https://www.verkkokauppa.com/fi/search?query=ssd&page=2 #max 60
# .search-result-count
# .list-product each product
# .list-product .thumbnail-link thumbnail-link--no-hover-border href
# .list-product-info__link href font::text (title)
# .list-product .product-price__price
# .list-product__product-id
#.ribbon-container sold out
# .list-product-info__description

class VerkkoSpider(scrapy.Spider):
    name = 'verkkokauppa'
    info_selectors = {
        "count": ".search-result-count::text",
        "item": ".list-product"
    }
    item_selectors = {
        "image": ".thumbnail__image::attr(src)",
        "link": ".list-product-info__link::attr(href)",
        "name": ".list-product-info__link *::text",
        "price": ".product-price__price *::text",
        "sku": ".list-product__product-id *::text",
        "description": ".list-product-info__description *::text"
    }
    def __init__(self,
                 runner,
                 query,
                 size,
                 *args,
                 **kwargs):
        super(VerkkoSpider, self).__init__(*args, **kwargs)
        self.page = 1
        self.total_pages = math.ceil(size / 60)
        self.url = "https://www.verkkokauppa.com/fi/search?query={query}".format(
            query=query,
            size=size
        )
        self.logger.info(self.url)
        self.runner = runner

    def start_requests(self):
        self.logger.info("Starting request {}".format(self.url))
        yield scrapy.Request(url=self.url, callback=self.parse)

    def parse(self, response):
        items = response.css(self.info_selectors['item'])
        if self.page == 1:
            count = response.css(self.info_selectors['count']).extract_first()
            if count:
                self.runner._count = count.replace('tuotetta', '')
        for item in items:
            item = {
                key: item.css(selector).extract_first()
                for key, selector in self.item_selectors.items()
            }
            item['image'] = response.urljoin(item['image'])
            item['link'] = response.urljoin(item['link'])
            yield item
        if self.page < self.total_pages:
            self.page += 1
            yield scrapy.Request(
                url=self.url_next + "&page={}".format(self.page),
                callback=self.parse
            )
