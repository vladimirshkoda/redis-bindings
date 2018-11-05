# redis-bindings
[![Build Status](https://travis-ci.org/vladimirshkoda/redis-bindings.svg?branch=master)](
https://travis-ci.org/vladimirshkoda/redis-bindings)

Redis bindings is an attempt to bring Redis types into Python as native ones. It is based on
[redis-py](https://github.com/andymccurdy/redis-py) and has the following types implemented so far:

* [RedisList](https://redis.io/commands#list)

Moreover, it provides some Redis descriptor interfaces:

* IRedisField
* IRedisListField

It is exactly interfaces, because it requires user to override `get_key_name` method to define key name
for Redis. Here is an example of how it can be implemented (can be found in [example.py](example.py)).
```python
from redis import Redis
from redistypes import IRedisField, IRedisListField


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


class RedisListField(IRedisListField, Re/disField):
    pass


class Student:
    name = RedisField()
    subjects = RedisListField()

    def __init__(self, pk):
        self.pk = pk

```

The `Student` class defined above can do the following things:

```python
from example import Student


s = Student(pk=1)
s.name = 'John Galt'
s.subjects = ['math', 'physics']

print(s.name)  # John Galt
print(s.subjects)  # RedisList: ['math', 'physics']

s.subjects.append('p.e.')
print(s.subjects)  # RedisList: ['math', 'physics', 'p.e.']

# Values stored inside the Redis types are immutable!
s.subjects.append({'name': 'art', 'avg_score': 4.5})
print(s.subjects[3])  # {'avg_score': 4.5, 'name': 'art'}
s.subjects[3]['avg_score'] = 3
print(s.subjects[3])  # {'avg_score': 4.5, 'name': 'art'}
```

### Warning!
All values stored inside the Redis types are immutable! As the example above shows, an attempt to change the value stored
in the dictionary inside the RedisList leads to nothing.

### Roadmap

* ~~Python3 support~~
* Querying over the pipe
* RedisDict
