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

    def append(self, value):
        """ Append value to the end of list """
        with self.redis() as redis:
            redis.rpush(self.key_name, value)

    def extend(self, iterable):
        """ Extend list by appending elements from the iterable """
        with self.redis() as redis:
            redis.rpush(self.key_name, *iterable)

    def remove(self, value):
        """
        L.remove(value) -- remove first occurrence of value.
        Raises ValueError if the value is not present.
        """
        with self.redis() as redis:
            if not redis.lrem(self.key_name, value, 1):
                raise ValueError('value not in list')

    @property
    def values(self):
        """ Return whole list from Redis """
        with self.redis() as redis:
            return redis.lrange(self.key_name, 0, -1)

    def __getitem__(self, index):
        """ x.__getitem__(y) <==> x[y] """
        if isinstance(index, int):
            with self.redis() as redis:
                return redis.lindex(self.key_name, index)
        elif isinstance(index, slice):
            start, stop, step = index.indices(len(self))
            with self.redis() as redis:
                return redis.lrange(self.key_name, start, stop)
        else:
            raise TypeError('Invalid index type')

    def __len__(self):
        """ x.__len__() <==> len(x) """
        with self.redis() as redis:
            return redis.llen(self.key_name)

    def __iter__(self):
        """ x.__iter__() <==> iter(x) """
        for value in self.values:
            yield value

    def __repr__(self):
        """ x.__repr__() <==> repr(x) """
        return "{0}: {1}".format(self.__class__.__name__, self.values)
