"""
Redis type descriptors.

Includes IRedisField, IRedisListField.
"""

from weakref import WeakKeyDictionary

from .bindings import RedisDict, RedisList
from .pickling import dumps, loads


class IRedisField(object):
    """Abstract class for Basic Redis descriptor."""

    def __init__(self, redis_connection, pickling=True):
        """
        Initialize Redis field descriptor.

        Accepts user data only as bytes, strings or numbers (ints, longs and floats). An attempt
        to set value as any other type will raise a DataError exception.
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

    def __delete__(self, instance):
        """Delete the attribute on an instance of the owner class."""
        self.redis.delete(self.get_key_name(instance))

    def __set_name__(self, owner, name):
        """
        Set the name the descriptor has been assigned to name.

        Called at the time the owner class is created.
        """
        self.name = name


class IRedisDataStructureField(IRedisField):
    """Generic abstract class for Redis data structure descriptor."""

    data_structure = None

    def __init__(self, redis_connection, pickling=True):
        """
        Initialize data structure descriptor.

        Creates a dictionary for cache: reference to data structures lives until the reference
        to the instance is not the only one left.
        """
        super().__init__(redis_connection, pickling)
        self.ds_references = WeakKeyDictionary()

    def __get__(self, instance, owner):
        """Return the attribute value."""
        if instance not in self.ds_references:
            self.ds_references[instance] = self.data_structure(
                self.redis,
                self.get_key_name(instance),
                pickling=self.pickling,
            )
        return self.ds_references[instance]

    def __set__(self, instance, value):
        """Set the attribute on the instance to the new value."""
        self.ds_references[instance] = self.data_structure(
            self.redis,
            self.get_key_name(instance),
            value,
            self.pickling,
        )


class IRedisListField(IRedisDataStructureField):
    """Abstract class for Redis list descriptor."""

    data_structure = RedisList


class IRedisDictField(IRedisDataStructureField):
    """Abstract class for Redis hash descriptor."""

    data_structure = RedisDict
