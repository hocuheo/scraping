import scrapy
import re
import collections

from w3lib.html import remove_tags, remove_tags_with_content
from urllib.parse import quote, unquote, urlparse


def flatten(l):
    for el in l:
        if isinstance(el, collections.Iterable) and not isinstance(el, (str, bytes)):
            yield from flatten(el)
        else:
            yield el


class AIOSpider(scrapy.Spider):
    name = 'aio'
    BLACK_LIST = [
        'google',
        'facebook',
        'twitter',
        'cdn'
    ]
    custom_settings = {
        "DOWNLOADER_MIDDLEWARES": {
            # 'scrapers.middlewares.RandomUserAgentMiddleware': 399,
            'scrapers.middlewares.IgnoreDuplicates': 543,
            'scrapy.downloadermiddlewares.httpproxy.HttpProxyMiddleware': 110,
        },
        "ITEM_PIPELINES": {
            'scrapers.pipelines.ElasticPipeline': 300
        }
    }
    crawled_urls = []
    pattern = re.compile(r"https?://(www\.)?")
    def __init__(self,
                 urls,
                 runner,
                 *args,
                 **kwargs):
        super(AIOSpider, self).__init__(*args, **kwargs)
        self.start_urls = urls
        self.runner = runner

    def start_requests(self):
        self.logger.info("Starting request {}".format(self.start_urls))
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def is_black_list(self, link):
        for l in self.BLACK_LIST:
            if l in link:
                return True
        return False

    def clean_protocol_url(self, url):
        parsed_result = urlparse(url)
        path_only_url =  parsed_result.netloc + parsed_result.path
        return quote(
            self.pattern.sub('', path_only_url).strip().strip('/')
        )

    def is_valid_url(self, url):
        parsed = urlparse(url)
        if parsed.scheme in ['http', 'https'] and parsed.netloc:
            return True
        else:
            return False

    def parse(self, response):
        request_url = response.request.url
        self.crawled_urls.append(request_url)

        links = [
            response.urljoin(unquote(link))
            for link in response.css('a::attr(href)').extract()
            if not self.is_black_list(link) and self.link_is_valid(link)
        ]

        unvisited_links = [
            link
            for link in links
            if link not in self.crawled_urls and self.is_valid_url(link)
        ]
        self.logger.info("Updating links")
        self.logger.info(unvisited_links)

        for l in unvisited_links:
            yield scrapy.Request(url=l, callback=self.parse)
        
        body = response.css('body')
        images = list({
            response.urljoin(img)
            for img in body.css('img::attr(src)').extract()
            if img
        })
        tags = list(self.parse_tags(body))
        header = self.parse_header(body)
        p_extracts = body.css('p').extract()
        if len(p_extracts) > 0 and header:
            body_text = "<p>" + "</p><p>".join([
                remove_tags(remove_tags_with_content(p, ('script', 'style')))
                for p in p_extracts
            ]) + "</p>"

            yield {
                "id": self.clean_protocol_url(request_url),
                "url": request_url,
                "tags": tags,
                "images": images,
                "title": header,
                "body": body_text
            }

    def link_is_valid(self, link):
        keys = ['member', 'upgrade', 'promotion']
        extensions = [
            '.jpg', '.png', '.gif', '.pdf', '.mp4', '.mp3', '.wav',
            '.css', '.js', '.scss', '.doc', '.swf'
        ]
        for key in keys:
            if key in link:
                return False
        for ext in extensions:
            if link.endswith(ext):
                return False
        return True

    def parse_header(self, body):
        for i in range(1, 7):
            header = body.css('h{}::text'.format(i)).extract_first()
            if header:
                return header

    def parse_tags(self, body):
        texts = flatten([d.css("::text").extract() for d in body.css('[class*="tag"]')])
        return {
            text.replace('\n', ' ').replace('\r', '')
            for text in texts
            if text
        }
