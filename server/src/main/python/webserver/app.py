import logging

from elasticsearch_dsl.connections import connections

from datetime import datetime
from webserver.api import app

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(process)d] [%(levelname)s] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
)

if __name__ == '__main__':
    connections.create_connection(hosts=['app-elastic'])
    app.run("0.0.0.0", 9090)

