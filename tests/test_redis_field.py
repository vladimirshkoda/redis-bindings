import pytest

from redistypes import IRedisField

from tests.conftest import VAL_1


class RedisTestField(IRedisField):
    """IRedisField implementation."""

    def get_key_name(self, instance):
        """Return Redis key name for the attribute."""
        return self.name


@pytest.fixture
def model_with_redis_field(r):
    """Class with RedisField attribute."""
    class Model(object):
        redis_field = RedisTestField(r)
    return Model


@pytest.fixture
def model_with_redis_field_without_pickling(r):
    """Class with RedisField attribute without pickling."""
    class Model(object):
        redis_field = RedisTestField(r, pickling=False)
    return Model


def test_key_name(r, model_with_redis_field):
    """
    Test ``__set_name__`` and ``get_key_name`` methods.

    Should set the attribute value to Redis on the key returned by ``get_key_name`` method.
    ``get_key_name`` method should return the attribute name.
    """
    test_object = model_with_redis_field()
    test_object.redis_field = VAL_1
    assert r.keys() == [b'redis_field']


def test_descriptor(model_with_redis_field):
    """
    Test ``__get__``, ``__set__``, and ``__delete__`` methods of descriptor.

    Should return Null when the instance is created.

    Should return the same value that was set.

    Should remove the key, and return None.
    """
    test_object = model_with_redis_field()
    assert test_object.redis_field is None

    test_object.redis_field = VAL_1
    assert test_object.redis_field == VAL_1

    del test_object.redis_field
    assert test_object.redis_field is None


def test_descriptor_without_pickling(model_with_redis_field_without_pickling):
    """
    Test ``__get__`` and ``__set__`` methods of descriptor without pickling.

    Should return the same value that was set but in bytes.
    """
    test_object = model_with_redis_field_without_pickling()
    test_object.redis_field = VAL_1
    assert test_object.redis_field == VAL_1.encode()
