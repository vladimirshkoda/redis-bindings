# redis-bindings
[![Build Status](https://travis-ci.org/vladimirshkoda/redis-bindings.svg?branch=master)](https://travis-ci.org/vladimirshkoda/redis-bindings)

Provides type bindings to native Redis list and dict for Python.  
Based on [redis-py](https://github.com/andymccurdy/redis-py).

## RedisList
RedisList has the following methods of the usual `list` implemented
* append
* extend
* remove
* pop
* \_\_getitem__
* \_\_setitem__
* \_\_len__
* \_\_iter__
* \_\_eq__
* \_\_ne__
* \_\_repr__
```python
>>> from redis import Redis
>>> from bindings import RedisList
>>> r = RedisList(Redis(), 'a', [1])
>>> r
RedisList: [1]
>>> r.append(2)
>>> r.values == [1, 2]
True
>>> r.extend([2])
>>> r
RedisList: [1, 2, 2]
>>> r.remove(2)
>>> r
RedisList: [1, 2]
>>> r.pop()
2

```
You can use an existing list in Redis, just omitting the init value in constructor.
```python
>>> r2 = RedisList(Redis(), 'a')
>>> r2
RedisList: [1]
```
WARNING! Values in the list are immutable.
```python
>>> r_list = RedisList(Redis(), 'a', [{1: 'old_value'}])
>>> r_list[0][1] = 'new_value'
>>> r_list[0][1]
'old_value'
```
