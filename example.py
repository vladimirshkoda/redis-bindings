from redis import Redis
from redistypes import IRedisField, IRedisListField


r_connection = Redis()


class RedisField(IRedisField):
    def __init__(self, name, pickling=True):
        super(RedisField, self).__init__(
            redis_connection=r_connection,
            pickling=pickling
        )
        self.name = name

    def get_key_name(self, instance):
        return ':'.join([
            instance.__class__.__name__, str(instance.pk), self.name
        ])


class RedisListField(IRedisListField, RedisField):
    pass


class Student(object):
    name = RedisField('name')
    subjects = RedisListField('subjects')

    def __init__(self, pk):
        self.pk = pk
