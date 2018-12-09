from elasticsearch_dsl import Document, Date, Integer, Keyword, Text, MetaField, Mapping

from elasticsearch_dsl.connections import connections


class Page(Document):
    title = Text(analyzer='snowball', fields={'raw': Keyword()})
    url = Text(analyzer='snowball')
    body = Text(analyzer='snowball')
    images = Text(multi=True)
    tags = Keyword(multi=True)
    created_at = Date()

    class Meta:
        mapping = Mapping('doc')
        mapping.meta('_all', enabled=True)

    class Index:
        name = 'test'
