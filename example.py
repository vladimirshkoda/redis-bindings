"""An example of the Redis descriptors usage."""

from redis import Redis
from redistypes import IRedisField, IRedisListField

r_connection = Redis()


class RedisField(IRedisField):
    """IRedisField implementation."""

    def __init__(self, pickling=True):
        """Set ``r_connection`` as the Redis connection pool by default."""
        super().__init__(
            redis_connection=r_connection,
            pickling=pickling,
        )

    def get_key_name(self, instance):
        """
        Return Redis key name of the attribute.

        It enforces instance using this descriptor to have the ``pk`` attribute.
        """
        return ':'.join([
            instance.__class__.__name__, str(instance.pk), self.name,
        ])


class RedisListField(RedisField, IRedisListField):
    """IRedisListField implementation."""


class Student(object):
    """Casual model of student."""

    name = RedisField()
    subjects = RedisListField()

    def __init__(self, pk, name=None, subjects=None):
        """Student instance has to be initialized with a primary key ``pk``."""
        self.pk = pk
        if name:
            self.name = name
        if subjects:
            self.subjects = subjects
