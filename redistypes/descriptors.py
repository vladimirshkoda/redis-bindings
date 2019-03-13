"""
Redis type descriptors.

Includes IRedisField, IRedisListField.
"""

import collections

from redistypes.bindings import RedisList, dumps, loads


class IRedisField(object):
    """Basic Redis descriptor interface."""

    def __init__(self, redis_connection, pickling=True):
        """
        Initialize Redis field descriptor.

        Accepts user data only as bytes, strings or numbers (ints, longs and floats). An attempt
        to specify a key or a value as any other type will raise a DataError exception.
        """
        self.redis = redis_connection
        self.pickling = pickling
        self.name = None

    def get_key_name(self, instance):
        """
        Return Redis key name of the attribute.

        Needs to be defined by user. It's recommended to follow the Redis convention of key
        naming using colon to split namespaces. E.g., 'cls_name:obj_id:field_name'.
        """
        raise NotImplementedError

    def __get__(self, instance, owner):
        """Return the attribute value."""
        value = self.redis.get(self.get_key_name(instance))
        if self.pickling and value is not None:
            value = loads(value)
        return value

    def __set__(self, instance, value):
        """Set the attribute on the instance to the new value."""
        if self.pickling:
            value = dumps(value)
        self.redis.set(self.get_key_name(instance), value)

    def __delete__(self, instance):  # noqa: Z434
        """Delete the attribute on an instance of the owner class."""
        self.redis.delete(self.get_key_name(instance))

    def __set_name__(self, owner, name):
        """
        Set the name the descriptor has been assigned to name.

        Called at the time the owner class is created.
        """
        self.name = name


class IRedisListField(IRedisField):
    """Redis list descriptor interface."""

    def __get__(self, instance, owner):
        """Return the attribute value."""
        return RedisList(self.redis, self.get_key_name(instance))

    def __set__(self, instance, value):
        """Set the attribute on the instance to the new value."""
        if not isinstance(value, collections.Iterable):
            raise ValueError('value is not iterable')
        key_name = self.get_key_name(instance)
        self.redis.delete(key_name)
        if value:
            if self.pickling:
                value = map(dumps, value)
            self.redis.rpush(key_name, *value)
