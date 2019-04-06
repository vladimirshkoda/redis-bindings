"""Provides RedisDict class."""

import collections

from redistypes.pickling import dumps, loads

REDIS_TYPE_HASH = b'hash'
REDIS_TYPE_NONE = b'none'

UNDEFINED = object()


class RedisDict(object):
    """
    Python binding to the Redis hash type.

    Visit https://redis.io/commands#hash to have better understanding.

    Unlike the dictionary in Python, the Redis hash does not preserve insertion order.

    WARNING!
    The value returned by the key lookup is a *copy* of what is in Redis. As such,
    mutating a value in place *will not* be saved back to redis.
    """

    def __init__(self, redis_connection, key_name, mapping=None, pickling=True):
        """
        Initialize RedisDict.

        Bind to value in Redis by the given key name. Validates if the value stored in Redis
        is a hash or None (empty). If ``mapping`` is given, replace stored in Redis value with
        the iterable.
        """
        self.redis = redis_connection
        if mapping:
            if not isinstance(mapping, collections.Mapping):
                raise ValueError('values are not mapping')
            pipe = self.redis.pipeline()
            pipe.delete(key_name)
            if pickling:
                mapping = {
                    dumps(k): dumps(v) for k, v in mapping.items()
                }
            pipe.hmset(key_name, mapping)
            pipe.execute()
        else:
            key_type = self.redis.type(key_name)
            if key_type not in (REDIS_TYPE_HASH, REDIS_TYPE_NONE):
                raise TypeError('Cannot bind to "{0}"'.format(key_type))
        self.key_name = key_name
        self.pickling = pickling

    def clear(self):
        """Remove all items from the hash."""
        self.redis.delete(self.key_name)

    def copy(self):
        """Return a copy of the hash."""
        return dict(self.items())

    def get(self, key, default=None):
        """
        Return the value for ``key`` if ``key`` is in the dictionary, else ``default``.

        If default is not given, it defaults to None, so that this method never raises
        a KeyError.
        """
        try:
            return self.__getitem__(key)
        except KeyError:
            return default

    def items(self):
        """Return a copy of the hash’s items as ((key, value) pairs)."""
        r_dict = self.redis.hgetall(self.key_name)
        if self.pickling:
            r_dict = {
                loads(k): loads(v) for k, v in r_dict.items()
            }
        return list(r_dict.items())

    def keys(self):
        """Return a copy of the hash’s keys."""
        keys = self.redis.hkeys(self.key_name)
        if self.pickling:
            keys = list(map(loads, keys))
        return keys

    def pop(self, key, default=UNDEFINED):
        """
        If ``key`` is in the dictionary, remove it and return its value.

        If not, return ``default``.
        """
        original_key = key
        if self.pickling:
            key = dumps(key)
        pipe = self.redis.pipeline()
        pipe.hget(self.key_name, key)
        pipe.hdel(self.key_name, key)
        item, _ = pipe.execute()
        if item is None:
            if default is UNDEFINED:
                raise KeyError(original_key)
            return default
        else:
            if self.pickling:
                item = loads(item)
            return item

    def popitem(self):
        """
        Remove and return a (key, value) pair from the hash.

        Cannot be implemented by Redis means.
        """
        raise NotImplementedError

    def setdefault(self, key, default=None):
        """
        If ``key`` is in the hash, return its value.

        If not, insert key with a value of ``default`` and return ``default``.
        """
        if self.pickling:
            key = dumps(key)
            default = dumps(default)
        pipe = self.redis.pipeline()
        pipe.hsetnx(self.key_name, key, default)
        pipe.hget(self.key_name, key)
        _, item = pipe.execute()
        if self.pickling:
            item = loads(item)
        return item

    def update(self, other):
        """
        Update the dictionary with the key/value pairs from ``other``.

        Overwrites existing keys. Returns None.
        """
        if not isinstance(other, collections.Mapping):
            raise ValueError('values are not mapping')
        if self.pickling:
            other = {
                dumps(k): dumps(v) for k, v in other.items()
            }
        self.redis.hmset(self.key_name, other)

    def values(self):
        """Return a copy of the hash’s values."""
        values = self.redis.hvals(self.key_name)
        if self.pickling:
            values = list(map(loads, values))
        return values

    def __contains__(self, key):
        """Return True if the hash has a key ``key``, else False."""
        if self.pickling:
            key = dumps(key)
        return self.redis.hexists(self.key_name, key)

    def __len__(self):
        """Return the number of items in the hash."""
        return self.redis.hlen(self.key_name)

    def __getitem__(self, key):
        """
        Return the item of the hash with key ``key``.

        Raises a KeyError if key is not in the map.
        """
        original_key = key
        if self.pickling:
            key = dumps(key)
        item = self.redis.hget(self.key_name, key)
        if item is None:
            raise KeyError(original_key)
        if self.pickling:
            item = loads(item)
        return item

    def __setitem__(self, key, value):
        """Set the item of the hash with key ``key`` to ``value``."""
        if self.pickling:
            key = dumps(key)
            value = dumps(value)
        self.redis.hset(self.key_name, key, value)

    def __delitem__(self, key):
        """
        Remove the item by the ``key`` from the hash.

        Raises a KeyError if ``key`` is not in the map.
        """
        original_key = key
        if self.pickling:
            key = dumps(key)
        if not self.redis.hdel(self.key_name, key):
            raise KeyError(original_key)

    def __iter__(self):
        """
        Return an iterator over the keys of the dictionary.

        This is a shortcut for iter(d.keys()).
        """
        return iter(self.keys())

    def __eq__(self, other):
        """
        Compare the hash with ``other``.

        Return True if the hash and the ``other`` have the same hash name, or all items
        of both are equal, else False.
        """
        if isinstance(other, self.__class__):
            return self.key_name == other.key_name or self.items() == other.items()
        return False

    def __repr__(self):
        """Return string representation of RedisDict instance."""
        return '{0}: {1}'.format(self.__class__.__name__, dict(self.items()))
