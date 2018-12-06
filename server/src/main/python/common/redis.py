import redis
import logging
import os

LOGGER = logging.getLogger('scrapers.redis')

class RedisStore:
    def __init__(self):
        self.__connection = redis.Redis(
            host=os.getenv('REDIS_HOST', 'app-redis'),
            port=int(os.getenv('REDIS_PORT', 6379))
        )

    def set(self, key, value, expire=None):
        LOGGER.info('Adding (key, value) (%s, %s)', key, value)
        if expire:
            return self.__connection.set(key, value, ex=expire)
        return self.__connection.set(key, value)

    def get(self, key):
        LOGGER.info('Fetching value from %s', key)
        return self.__connection.get(key)

    def delete(self, *keys):
        LOGGER.info('Removing keys %s', ",".join(keys))
        return self.__connection.delete(*keys)

    def connection(self):
        return self.__connection

redis_store = RedisStore()
