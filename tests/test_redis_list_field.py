import pytest

from bindings import RedisList
from descriptors import RedisListField


class RedisTestListField(RedisListField):
    def get_key_name(self, instance):
        return 'a'


def test_descriptor(r):
    r_field = RedisTestListField(r)
    r_field.__set__(instance=None, value=[1])
    value = r_field.__get__(instance=None, owner=None)
    assert isinstance(value, RedisList)
    assert value.values == [1]


def test_set_not_iterable(r):
    r_field = RedisTestListField(r)
    with pytest.raises(ValueError):
        r_field.__set__(instance=None, value=1)


def test_set_empty_list(r):
    r_field = RedisTestListField(r)
    r_field.__set__(instance=None, value=[])
    assert r_field.__get__(instance=None, owner=None).values == []
