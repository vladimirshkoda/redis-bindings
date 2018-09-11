from redis import Redis
from descriptors import IRedisField, IRedisListField


r_connection = Redis()


class RedisField(IRedisField):
    def __init__(self, pickling=True):
        super(RedisField, self).__init__(
            redis_connection=r_connection,
            pickling=pickling
        )

    def get_key_name(self, instance):
        return ':'.join([
            instance.__class__.__name__, str(instance.pk), self.name
        ])


class RedisListField(IRedisListField,
                     RedisField):
    pass


class SetNameMeta(type):
    def __new__(mcs, name, bases, attrs):
        cls = super(SetNameMeta, mcs).__new__(mcs, name, bases, attrs)
        for attr, obj in attrs.items():
            if isinstance(obj, IRedisField):
                obj.__set_name__(cls, attr)
        return cls


class Student(object):
    __metaclass__ = SetNameMeta

    name = RedisField()
    avg_score = RedisField()
    subjects = RedisListField()

    def __init__(self, pk):
        self.pk = pk
