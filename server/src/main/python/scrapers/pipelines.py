import logging
from datetime import datetime
from common.models import Page

class ElasticPipeline(object):
    def process_item(self, item, spider):
        logging.info('Into the pipeline')
        logging.info('Saving %s', item["url"])

        Page(
            _id=item['id'],
            title=item['title'],
            body=item['body'],
            url=item['url'],
            image=item['images'],
            tags=item['tags'],
            created_at=datetime.now()
        ).save()
