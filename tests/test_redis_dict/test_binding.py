import pytest

from redistypes import RedisDict
from tests.conftest import REDIS_TEST_KEY_NAME, VAL_1, VAL_3
from tests.test_redis_dict.conftest import KEY_1, KEY_3


class TestInit(object):
    """
    Test ``__init__`` method.

    Since there is no other way to evaluate the result, this test includes also tests
    for ``copy`` and, as a result, ``items`` methods.
    """

    def test_init_with_not_mapping_data_type(self, r):
        """Should raise ValueError."""
        with pytest.raises(ValueError):
            RedisDict(r, REDIS_TEST_KEY_NAME, 1)

    def test_bind_to_wrong_type(self, r):
        """Should raise TypeError."""
        r.set(REDIS_TEST_KEY_NAME, 1)
        with pytest.raises(TypeError):
            RedisDict(r, REDIS_TEST_KEY_NAME)

    def test_bind_to_none(self, r):
        """Should be equal to empty dictionary."""
        redis_dict = RedisDict(r, REDIS_TEST_KEY_NAME)
        assert redis_dict.copy() == {}

    def test_bind_to_existing_hash(self, r, bytes_dict):
        """Should be equal to bytes_dict."""
        r.hmset(REDIS_TEST_KEY_NAME, bytes_dict)
        redis_dict = RedisDict(r, REDIS_TEST_KEY_NAME, pickling=False)
        assert redis_dict.copy() == bytes_dict

    def test_init_with_mapping(self, redis_dict, str_dict):
        """Should be equal to str_dict."""
        assert redis_dict.copy() == str_dict

    def test_init_without_pickling(self, redis_dict_without_pickling, bytes_dict):
        """
        Should be equal to bytes_dict.

        With pickling=False, should be equal to bytes_dict, despite of
        it was initialized with str_dict.
        """
        assert redis_dict_without_pickling.copy() == bytes_dict

    def test_override_previous_hash(self, r, str_dict, another_str_dict):
        """
        Should be equal to another_str_dict.

        Despite of it was initialized with str_dict.
        """
        redis_dict = RedisDict(r, REDIS_TEST_KEY_NAME, str_dict)
        assert redis_dict.copy() == str_dict

        redis_dict = RedisDict(r, REDIS_TEST_KEY_NAME, another_str_dict)
        assert redis_dict.copy() == another_str_dict != str_dict


class TestClear(object):
    """Test ``clear`` method."""

    def test_hash_exists(self, redis_dict, str_dict):
        """Should remove all items from the hash."""
        assert redis_dict.copy() == str_dict
        redis_dict.clear()
        assert redis_dict.copy() == {}

    def test_hash_does_not_exist(self, redis_empty_dict):
        """Should remove all items despite of the hash is empty."""
        redis_empty_dict.clear()
        assert redis_empty_dict.copy() == {}


class TestGet(object):
    """Test ``get`` method."""

    def test_key_exists(self, redis_dict):
        """Should return VAL1."""
        assert redis_dict.get(KEY_1) == VAL_1

    def test_key_does_not_exist(self, redis_dict):
        """Should return default argument value."""
        assert redis_dict.get(KEY_3) is None
        assert redis_dict.get(KEY_3, VAL_3) == VAL_3


class TestKeys(object):
    """Test ``keys`` method."""

    def test_empty_hash(self, redis_empty_dict):
        """Should return an empty list."""
        assert redis_empty_dict.keys() == []

    def test_not_empty_hash(self, redis_dict, str_dict):
        """Should have the same keys as str_dict."""
        assert redis_dict.keys() == list(str_dict.keys())

    def test_not_empty_hash_without_pickling(self, redis_dict_without_pickling, bytes_dict):
        """Should have the same keys as bytes_dict."""
        assert redis_dict_without_pickling.keys() == list(bytes_dict.keys())


class TestPop(object):
    """Test ``pop`` method."""

    def test_key_exists(self, redis_dict):
        """Should return VAL_1 and remove KEY_1 from the hash."""
        assert redis_dict.pop(KEY_1) == VAL_1
        assert KEY_1 not in redis_dict

    def test_key_does_not_exist(self, redis_dict):
        """Should raise KeyError."""
        with pytest.raises(KeyError):
            redis_dict.pop(KEY_3)

    def test_key_exists_with_default(self, redis_dict):
        """Should return VAL_1 and remove KEY_1 from the hash."""
        assert redis_dict.pop(KEY_1, VAL_3) == VAL_1

    def test_key_does_not_exist_with_default(self, redis_dict):
        """Should return VAL_3."""
        assert redis_dict.pop(KEY_3, VAL_3) == VAL_3

    def test_key_exists_without_pickling(self, redis_dict_without_pickling):
        """Should return VAL_1 in bytes."""
        assert redis_dict_without_pickling.pop(KEY_1) == VAL_1.encode()


def test_popitem(redis_dict):
    """
    Test ``popitem`` method.

    Should raise NotImplementedError.
    """
    with pytest.raises(NotImplementedError):
        redis_dict.popitem()


class TestUpdate(object):
    """Test ``update`` method."""

    def test_keys_are_not_overridden(self, redis_dict, str_dict, another_str_dict):
        """Should be equal to the merge of str_dict and another_str_dict."""
        redis_dict.update(another_str_dict)
        assert redis_dict.copy() == {**str_dict, **another_str_dict}

    def test_keys_are_overridden(self, redis_dict, str_dict):
        """Should override KEY_1 value."""
        another_str_dict = {KEY_1: VAL_3}
        redis_dict.update(another_str_dict)
        str_dict.update(another_str_dict)
        assert redis_dict.copy() == str_dict

    def test_update_without_pickling(
        self,
        redis_dict_without_pickling,
        bytes_dict,
        another_str_dict,
    ):
        """Should be equal to the merge of bytes_dict and encoded another_str_dict."""
        redis_dict_without_pickling.update(another_str_dict)
        assert redis_dict_without_pickling.copy() == {
            KEY_3.encode(): VAL_3.encode(), **bytes_dict
        }

    def test_other_is_not_mapping(self, redis_dict):
        """"Should raise ValueError."""
        with pytest.raises(ValueError):
            redis_dict.update(1)


class TestValues(object):
    """Test ``items`` method."""

    def test_empty_hash(self, redis_empty_dict):
        """Should return an empty list."""
        assert redis_empty_dict.values() == []

    def test_not_empty_hash(self, redis_dict, str_dict):
        """Should have the same values as str_dict."""
        assert redis_dict.values() == list(str_dict.values())

    def test_not_empty_hash_without_pickling(self, redis_dict_without_pickling, bytes_dict):
        """Should have the same values as bytes_dict."""
        assert redis_dict_without_pickling.values() == list(bytes_dict.values())


class TestSetDefault(object):
    """Test ``setdefault`` method."""

    def test_key_already_exists(self, redis_dict):
        """Should return VAL1."""
        assert redis_dict.setdefault(KEY_1, VAL_3) == VAL_1

    def test_key_does_not_exist(self, redis_dict):
        """Should return VAL3."""
        assert redis_dict.setdefault(KEY_3, VAL_3) == VAL_3

    def test_key_already_exists_without_pickling(self, redis_dict_without_pickling):
        """Should return VAL1 in bytes."""
        assert redis_dict_without_pickling.setdefault(KEY_1, VAL_3) == VAL_1.encode()

    def test_key_does_not_exist_without_pickling(self, redis_dict_without_pickling):
        """Should return VAL3 in bytes."""
        assert redis_dict_without_pickling.setdefault(KEY_3, VAL_3) == VAL_3.encode()


class TestContains(object):
    """Test ``__contains__`` method."""

    def test_empty_hash(self, redis_empty_dict):
        """
        Should not find any key in the empty hash.

        It is more like to test whether HEXISTS method of Redis works with the none type.
        """
        assert KEY_1 not in redis_empty_dict

    def test_not_empty_hash(self, redis_dict, str_dict):
        """Should find keys that are presented in str_dict."""
        assert KEY_1 in str_dict and KEY_1 in redis_dict
        assert KEY_3 not in str_dict and KEY_3 not in redis_dict

    def test_not_empty_hash_without_pickling(self, redis_dict_without_pickling, bytes_dict):
        """Should find keys that are presented in bytes_dict."""
        encoded_key = KEY_1.encode()
        assert encoded_key in redis_dict_without_pickling and encoded_key in bytes_dict


class TestLen(object):
    """Test ``__len__`` method."""

    def test_empty_hash(self, redis_empty_dict):
        """
        Should return 0.

        Casting to bool should return False.
        """
        assert len(redis_empty_dict) == 0
        assert bool(redis_empty_dict) is False

    def test_not_empty_hash(self, redis_dict, str_dict):
        """
        Should return length of str_dict.

        Casting to bool should return True.
        """
        assert len(redis_dict) == len(str_dict) == 2
        assert bool(redis_dict) is True


class TestGetItem(object):
    """Test ``__getitem__`` method."""

    def test_key_exists(self, redis_dict):
        """Should return VAL1."""
        assert redis_dict[KEY_1] == VAL_1

    def test_key_does_not_exist(self, redis_dict):
        """Should raise KeyError."""
        with pytest.raises(KeyError):
            redis_dict[KEY_3]

    def test_key_exists_without_pickling(self, redis_dict_without_pickling):
        """Should return VAL1 in bytes."""
        assert redis_dict_without_pickling[KEY_1] == VAL_1.encode()

    def test_value_is_none(self, r):
        """Should return None."""
        redis_dict = RedisDict(r, REDIS_TEST_KEY_NAME, {KEY_1: None})
        assert redis_dict[KEY_1] is None


class TestSetItem(object):
    """Test ``__setitem__`` method."""

    def test_key_already_exists(self, redis_dict):
        """Should set VAL3."""
        redis_dict[KEY_1] = VAL_3
        assert redis_dict[KEY_1] == VAL_3

    def test_key_does_not_exist(self, redis_dict):
        """Should set VAL3."""
        redis_dict[KEY_3] = VAL_3
        assert redis_dict[KEY_3] == VAL_3

    def test_key_already_exists_without_pickling(self, redis_dict_without_pickling):
        """Should set VAL3 in bytes."""
        redis_dict_without_pickling[KEY_1] = VAL_3
        assert redis_dict_without_pickling[KEY_1] == VAL_3.encode()

    def test_key_does_not_exist_without_pickling(self, redis_dict_without_pickling):
        """Should set VAL3 in bytes."""
        redis_dict_without_pickling[KEY_3] = VAL_3
        assert redis_dict_without_pickling[KEY_3] == VAL_3.encode()


class TestDelItem(object):
    """Test ``__delitem__`` method."""

    def test_key_exists(self, redis_dict):
        """Should remove KEY1."""
        del redis_dict[KEY_1]
        with pytest.raises(KeyError):
            redis_dict[KEY_1]

    def test_key_does_not_exist(self, redis_dict):
        """Should raise KeyError."""
        with pytest.raises(KeyError):
            del redis_dict[KEY_3]

    def test_key_exist_without_pickling(self, redis_dict_without_pickling):
        """Should remove KEY1."""
        del redis_dict_without_pickling[KEY_1]
        with pytest.raises(KeyError):
            redis_dict_without_pickling[KEY_1]


def test_iter(redis_dict):
    """
    Test ``__iter__`` method.

    Should return keys of redis_dict.
    """
    assert list(redis_dict) == redis_dict.keys()


class TestEq(object):
    """Test ``__eq__`` method."""

    OTHER_HASH_NAME = 'other_hash_name'

    def test_instance_of_another_class(self, redis_dict, str_dict):
        """Should return False."""
        assert redis_dict != str_dict and not isinstance(str_dict, type(redis_dict))

    def test_two_different_redis_dicts(self, r, redis_dict, another_str_dict):
        """Should return False."""
        other_redis_dict = RedisDict(r, self.OTHER_HASH_NAME, another_str_dict)
        assert redis_dict != other_redis_dict and isinstance(other_redis_dict, type(redis_dict))

    def test_equal_key_names(self, r, redis_dict):
        """Should return True."""
        other_redis_dict = RedisDict(r, REDIS_TEST_KEY_NAME)
        assert redis_dict == other_redis_dict and redis_dict.key_name == other_redis_dict.key_name

    def test_equal_items(self, r, redis_dict, str_dict):
        """Should return True."""
        other_redis_dict = RedisDict(r, self.OTHER_HASH_NAME, str_dict)
        assert redis_dict == other_redis_dict and redis_dict.items() == other_redis_dict.items() \
            and redis_dict.key_name != other_redis_dict.key_name


def test_repr(redis_dict, str_dict):
    """Test ``__repr__`` method."""
    assert str(redis_dict) == '{0}: {1}'.format(type(redis_dict).__name__, str_dict)
