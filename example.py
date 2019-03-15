"""An example of the Redis descriptors usage."""

from redis import Redis

from redistypes.descriptors import IRedisField, IRedisListField

r_connection = Redis()


class RedisField(IRedisField):
    """IRedisField implementation."""

    def __init__(self, pickling=True):
        """Set `r_connection` as the Redis connection pool by default."""
        super().__init__(
            redis_connection=r_connection,
            pickling=pickling,
        )

    def get_key_name(self, instance):
        """
        Return Redis key name of the attribute.

        It enforces instance using this descriptor to have the `pk` attribute.
        """
        return ':'.join([
            instance.__class__.__name__, str(instance.pk), self.name,
        ])


class RedisListField(IRedisListField, RedisField):
    """IRedisListField implementation."""


class Student(object):
    """Casual model of student."""

    name = RedisField()
    subjects = RedisListField()

    def __init__(self, pk):
        """Student instance has to be initialized with a primary key `pk`."""
        self.pk = pk
