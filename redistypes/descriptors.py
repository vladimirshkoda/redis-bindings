import collections

from .bindings import loads, dumps, RedisList


class IRedisField(object):
    """ Basic Redis descriptor interface. """
    def __init__(self, redis_connection, pickling=True):
        self.redis = redis_connection
        self.pickling = pickling
        self.name = None

    def get_key_name(self, instance):
        """
        It's recommended to follow "Redis" convention of key naming using semicolon
        to separate namespaces. E.g., "cls_name:obj_id:field_name".
        """
        raise NotImplementedError

    def __get__(self, instance, owner):
        value = self.redis.get(self.get_key_name(instance))
        if self.pickling and value is not None:
            value = loads(value)
        return value

    def __set__(self, instance, value):
        if self.pickling:
            value = dumps(value)
        self.redis.set(self.get_key_name(instance), value)

    def __delete__(self, instance):
        self.redis.delete(self.get_key_name(instance))

    def __set_name__(self, owner, name):
        self.name = name


class IRedisListField(IRedisField):
    """ Redis list descriptor interface. """
    def __get__(self, instance, owner):
        return RedisList(self.redis, self.get_key_name(instance))

    def __set__(self, instance, value):
        if not isinstance(value, collections.Iterable):
            raise ValueError('value is not iterable')
        key_name = self.get_key_name(instance)
        self.redis.delete(key_name)
        if value:
            if self.pickling:
                value = map(dumps, value)
            self.redis.rpush(key_name, *value)
