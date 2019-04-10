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
* IRedisDictField

The classes are abstract because it requires user to override ``get_key_name``
method to define key name for Redis. Here is an example of how it can be
implemented (can be found in `example.py <https://github.com/vladimirshkoda/redis
-bindings/blob/master/example.py>`_).

.. literalinclude:: example.py
    :language: python

The defined above ``Student`` model has the following behaviour:

.. code-block:: pycon

    >>> from example import Student
    >>> student = Student(pk=1, name='John Galt', subjects=['math', 'physics'])
    >>> student.name
    John Galt
    >>> student.subjects
    RedisList: ['math', 'physics']
    >>> student.subjects.append('p.e.')
    >>> student.subjects
    RedisList: ['math', 'physics', 'p.e.']
    >>> student.subjects[-1] = 'art'
    >>> student.subjects
    RedisList: ['math', 'physics', 'art']

Let's check what keys we've got in Redis:

.. code-block:: pycon

    >>> from redis import Redis
    >>> r = Redis()
    >>> r.keys()
    [b'Student:1:name', b'Student:1:subjects']

Warning!
--------

As you saw above, we are able to change items of the RedisList, e.g. replace one subject
with another by index. But what if we set list value to the regular field? Let's replace
name of the student with list consisting of the first name and the last name.

.. code-block:: pycon

    >>> student.name = ['John', 'Galt']
    >>> student.name
    ['John', 'Galt']
    >>> student.name[-1] = 'Smith'
    >>> student.name
    ['John', 'Galt']

In that way, we changed the name value from string to list of two items, but since
``name`` is a simple RedisField keeping all value as string in Redis, we are not
able to modify stored items themselves.
**All values stored inside the Redis data structures are immutable!**
As the example above shows, index lookup from the list stored as string in redis will
return a copy of the item.
