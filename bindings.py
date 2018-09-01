import cPickle
import collections

from functools import partial


REDIS_TYPE_LIST = 'list'
REDIS_TYPE_NONE = 'none'


def loads(value):
    """
    Unpickles value, raises a ValueError in case anything fails.
    """
    try:
        obj = cPickle.loads(value)
    except Exception as e:
        raise ValueError('Cannot unpickle value', e)
    return obj


# Serialize pickle dumps using the highest pickle protocol (binary, by default uses ascii)
dumps = partial(cPickle.dumps, protocol=cPickle.HIGHEST_PROTOCOL)


class RedisList(object):
    """
    Provides basic list bindings for Redis list type. Visit https://redis.io/commands#list
    to have better understanding.
    """
    def __init__(self, redis_connection, key_name, iterable=None, pickling=True):
        self.redis = redis_connection
        if iterable:
            if not isinstance(iterable, collections.Iterable):
                raise ValueError('values are not iterable')
            self.redis.delete(key_name)
            if pickling:
                iterable = map(dumps, iterable)
            self.redis.rpush(key_name, *iterable)
        else:
            key_type = self.redis.type(key_name)
            if key_type not in (REDIS_TYPE_LIST, REDIS_TYPE_NONE):
                raise TypeError('Cannot bind to "{0}"'.format(key_type))
        self.key_name = key_name
        self.pickling = pickling

    @property
    def values(self):
        """ Return whole list from Redis """
        values = self.redis.lrange(self.key_name, 0, -1)
        if self.pickling:
            values = map(loads, values)
        return values

    def append(self, value):
        """ Append value to the end of list """
        if self.pickling:
            value = dumps(value)
        self.redis.rpush(self.key_name, value)

    def extend(self, iterable):
        """ Extend list by appending elements from the iterable """
        if self.pickling:
            iterable = map(dumps, iterable)
        self.redis.rpush(self.key_name, *iterable)

    def remove(self, value):
        """
        L.remove(value) -- remove first occurrence of value.
        Raises ValueError if the value is not present.
        """
        if self.pickling:
            value = dumps(value)
        if not self.redis.lrem(self.key_name, value, 1):
            raise ValueError('value not in list')

    def __getitem__(self, index):
        """ x.__getitem__(y) <==> x[y] """
        if isinstance(index, int):
            item = self.redis.lindex(self.key_name, index)
            if self.pickling:
                item = loads(item)
            return item
        elif isinstance(index, slice):
            start, stop, step = index.indices(len(self))
            item = self.redis.lrange(self.key_name, start, stop)
            if self.pickling:
                item = map(loads, item)
            return item
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
