REDIS_TYPE_LIST = 'list'
REDIS_TYPE_NONE = 'none'


class RedisList(object):
    """
    Provides basic list bindings for Redis list type. Visit https://redis.io/commands#list
    to have better understanding. All values will be casted to STRINGS.
    """
    def __init__(self, redis, key_name, *values):
        self.redis = redis
        with self.redis() as redis:
            if values:
                redis.delete(key_name)
                redis.rpush(key_name, *values)
            else:
                key_type = redis.type(key_name)
                if key_type not in (REDIS_TYPE_LIST, REDIS_TYPE_NONE):
                    raise TypeError('Cannot bind to "{0}"'.format(key_type))
        self.key_name = key_name
