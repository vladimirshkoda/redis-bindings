REDIS_TYPE_LIST = 'list'
REDIS_TYPE_NONE = 'none'


class RedisList(object):
    """
    Provides basic list bindings for Redis list type. Visit https://redis.io/commands#list
    to have better understanding. All values will be casted to STRINGS.
    """
    def __init__(self, redis, key_name, *values):
        self.redis = redis
        if values:
            self.redis.delete(key_name)
            self.redis.rpush(key_name, *values)
        else:
            key_type = self.redis.type(key_name)
            if key_type not in (REDIS_TYPE_LIST, REDIS_TYPE_NONE):
                raise TypeError('Cannot bind to "{0}"'.format(key_type))
        self.key_name = key_name

    @property
    def values(self):
        """ Return whole list from Redis """
        return self.redis.lrange(self.key_name, 0, -1)

    def append(self, value):
        """ Append value to the end of list """
        self.redis.rpush(self.key_name, value)

    def extend(self, iterable):
        """ Extend list by appending elements from the iterable """
        self.redis.rpush(self.key_name, *iterable)

    def remove(self, value):
        """
        L.remove(value) -- remove first occurrence of value.
        Raises ValueError if the value is not present.
        """
        if not self.redis.lrem(self.key_name, value, 1):
            raise ValueError('value not in list')

    def __getitem__(self, index):
        """ x.__getitem__(y) <==> x[y] """
        if isinstance(index, int):
            return self.redis.lindex(self.key_name, index)
        elif isinstance(index, slice):
            start, stop, step = index.indices(len(self))
            return self.redis.lrange(self.key_name, start, stop)
        else:
            raise TypeError('Invalid index type')

    def __len__(self):
        """ x.__len__() <==> len(x) """
        return self.redis.llen(self.key_name)

    def __iter__(self):
        """ x.__iter__() <==> iter(x) """
        for value in self.values:
            yield value

    def __repr__(self):
        """ x.__repr__() <==> repr(x) """
        return '{0}: {1}'.format(self.__class__.__name__, self.values)
