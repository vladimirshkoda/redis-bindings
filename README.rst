redis-bindings
==============

.. image:: https://travis-ci.org/vladimirshkoda/redis-bindings.svg?branch=master
    :target: https://travis-ci.org/vladimirshkoda/redis-bindings

.. image:: https://badge.fury.io/py/redistypes.svg
    :target: https://pypi.org/project/redistypes

.. image:: https://img.shields.io/badge/style-wemake-000000.svg
    :target: https://github.com/wemake-services/wemake-python-styleguide

Redis bindings is an attempt to bring Redis types into Python as native ones. It
is based on `redis-py <https://github.com/andymccurdy/redis-py>`_ and has the
following types implemented so far:

* `RedisList <https://redis.io/commands#list>`_
* `RedisDict <https://redis.io/commands#hash>`_

Moreover, it provides some abstract classes as Redis descriptors:

* IRedisField
* IRedisListField

The classes are abstract because it requires user to override ``get_key_name``
method to define key name for Redis. Here is an example of how it can be
implemented (can be found in `example.py <https://github.com/vladimirshkoda/redis
-bindings/blob/master/example.py>`_).

.. code-block:: python

    """An example of the Redis descriptors usage."""

    from redis import Redis

    from redistypes.descriptors import IRedisField, IRedisListField

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


    class RedisListField(IRedisListField, RedisField):
        """IRedisListField implementation."""


    class Student(object):
        """Casual model of student."""

        name = RedisField()
        subjects = RedisListField()

        def __init__(self, pk):
            """Student instance has to be initialized with a primary key ``pk``."""
            self.pk = pk

The defined above ``Student`` class have the following behaviour:

.. code-block:: pycon

    >>> from example import Student
    >>> s = Student(pk=1)
    >>> s.name = 'John Galt'
    >>> s.subjects = ['math', 'physics']
    >>> s.name
    John Galt
    >>> s.subjects
    RedisList: ['math', 'physics']
    >>> s.subjects.append('p.e.')
    >>> s.subjects
    RedisList: ['math', 'physics', 'p.e.']
    >>> # Values stored inside the Redis data structures are immutable!
    >>> s.subjects.append({'name': 'art', 'avg_score': 4.5})
    >>> s.subjects[3]
    {'avg_score': 4.5, 'name': 'art'}
    >>> s.subjects[3]['avg_score'] = 3
    >>> s.subjects[3]
    {'avg_score': 4.5, 'name': 'art'}

Warning!
--------

All values stored inside the Redis data structures are immutable! As the example above
shows, an attempt to change the value stored in the dictionary inside the
RedisList leads to nothing.
