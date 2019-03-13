"""
Redis type bindings.

So far consists only of RedisList.
"""

import collections
import pickle
from functools import partial

from redis import ResponseError

REDIS_TYPE_LIST = b'list'
REDIS_TYPE_NONE = b'none'


def loads(value):
    """Unpickles value, raises a ValueError in case anything fails."""
    try:
        obj = pickle.loads(value)
    except Exception as e:
        raise ValueError('Cannot unpickle value', e)
    return obj


# Serialize pickle dumps using the highest pickle protocol (binary, by default uses ascii)
dumps = partial(pickle.dumps, protocol=pickle.HIGHEST_PROTOCOL)


class RedisList(object):
    """
    Provides basic list bindings for Redis list type.

    Visit https://redis.io/commands#list to have better understanding.

    WARNING!
    All the manipulations with list values are being done with their copies, therefore look
    at the following code:
    >>> from redis import Redis
    >>> r_list = RedisList(Redis(), 'key_name', [{1: 'old_value'}])
    >>> r_list[0][1]
    'old_value'
    >>> r_list[0][1] = 'new_value'
    >>> r_list[0][1]
    'old_value'
    """

    def __init__(self, redis_connection, key_name, iterable=None, pickling=True):
        """
        Initialize RedisList.

        Bind to value in Redis by the given key name. Validates if the value in Redis
        is a list or None (empty). If iterable is given, replace stored in Redis value
        with the iterable.
        """
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
        """Return whole list from Redis."""
        values = self.redis.lrange(self.key_name, 0, -1)
        if self.pickling:
            values = list(map(loads, values))
        return values

    def append(self, value):
        """Append value to the end of list."""
        if self.pickling:
            value = dumps(value)
        self.redis.rpush(self.key_name, value)

    def extend(self, iterable):
        """Extend list by appending elements from the iterable."""
        if self.pickling:
            iterable = map(dumps, iterable)
        self.redis.rpush(self.key_name, *iterable)

    def remove(self, value):
        """
        Remove first occurrence of value.

        Raises ValueError if the value is not present.
        """
        if self.pickling:
            value = dumps(value)
        if not self.redis.lrem(self.key_name, 1, value):
            raise ValueError('value not in list')

    def pop(self):
        """
        Remove and return last item.

        Raises IndexError if list is empty.
        """
        item = self.redis.rpop(self.key_name)
        if item is None:
            raise IndexError('pop from empty list')
        if self.pickling:
            item = loads(item)
        return item

    def __getitem__(self, index):
        """
        Get item by index, or slice from list.

        x.__getitem__(y) <==> x[y]
        """
        if isinstance(index, int):
            item = self.redis.lindex(self.key_name, index)
            if item is None:
                raise IndexError('list index out of range')
            if self.pickling:
                item = loads(item)
            return item
        elif isinstance(index, slice):
            values = self.values
            start, stop, step = index.indices(len(values))
            return values[start:stop:step]
        else:
            raise TypeError('invalid index type')

    def __setitem__(self, index, value):
        """
        Set item to list by index.

        x.__setitem__(index, value) <==> x[index]=value
        """
        if not isinstance(index, int):
            raise TypeError('invalid index type')
        if self.pickling:
            value = dumps(value)
        try:
            self.redis.lset(self.key_name, index, value)
        except ResponseError as e:
            if str(e) == 'index out of range':
                raise IndexError('list assignment index out of range')
            raise e

    def __len__(self):
        """
        Return length of the list.

        x.__len__() <==> len(x)
        """
        return self.redis.llen(self.key_name)

    def __iter__(self):
        """
        Return an iterator object.

        x.__iter__() <==> iter(x)
        """
        for value in self.values:
            yield value

    def __eq__(self, other):
        """
        Compare self RedisList with other object.

        x.__eq__(y) <==> x==y
        """
        if isinstance(other, self.__class__):
            return self.key_name == other.key_name and self.values == other.values
        return False

    def __repr__(self):
        """
        Return string representation of the RedisList object.

        x.__repr__() <==> repr(x)
        """
        return '{0}: {1}'.format(self.__class__.__name__, self.values)
