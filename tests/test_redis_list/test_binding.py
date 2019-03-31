import pytest

from redistypes import RedisList

from tests.conftest import REDIS_TEST_KEY_NAME, VAL_3


class TestInit(object):
    """Test ``__init__`` method."""

    def test_init_with_not_iterable_data_type(self, r):
        """Should raise ValueError."""
        with pytest.raises(ValueError):
            RedisList(r, REDIS_TEST_KEY_NAME, 1)

    def test_bind_to_wrong_type(self, r):
        """Should raise TypeError."""
        r.set(REDIS_TEST_KEY_NAME, 1)
        with pytest.raises(TypeError):
            RedisList(r, REDIS_TEST_KEY_NAME)

    def test_bind_to_none(self, r):
        """Should be equal to empty string."""
        redis_list = RedisList(r, REDIS_TEST_KEY_NAME)
        assert list(redis_list) == []

    def test_bind_to_existing_list(self, r, bytes_list):
        """
        Should be equal to bytes_list.

        Since the items are stored in the Redis as bytes, pickling is disabled.
        """
        r.rpush(REDIS_TEST_KEY_NAME, *bytes_list)
        redis_list = RedisList(r, REDIS_TEST_KEY_NAME, pickling=False)
        assert list(redis_list) == bytes_list

    def test_init_with_iterable(self, redis_list, str_list):
        """Should be equal to str_list."""
        assert list(redis_list) == str_list

    def test_init_without_pickling(self, redis_list_without_pickling, bytes_list):
        """
        Should be equal to bytes_list.

        With pickling=False, should be equal to bytes_list, despite of it was initialized
        with str_list.
        """
        assert list(redis_list_without_pickling) == bytes_list

    def test_override_previous_list(self, r, str_list, another_str_list):
        """
        Should be equal to another_str_list.

        Despite of it was initialized with str_list.
        """
        redis_list = RedisList(r, REDIS_TEST_KEY_NAME, str_list)
        assert list(redis_list) == str_list

        redis_list = RedisList(r, REDIS_TEST_KEY_NAME, another_str_list)
        assert list(redis_list) == another_str_list != str_list


class TestAppend(object):
    """Test ``append`` method."""

    def test_append(self, redis_list, str_list):
        """Should be equal to updated str_list."""
        redis_list.append(VAL_3)
        str_list.append(VAL_3)
        assert list(redis_list) == list(str_list)

    def test_append_without_pickling(self, redis_list_without_pickling, bytes_list):
        """Should be equal to updated bytes_list."""
        redis_list_without_pickling.append(VAL_3)
        bytes_list.append(VAL_3.encode())
        assert list(redis_list_without_pickling) == bytes_list


def test_extend(r):
    r_list = RedisList(r, 'a')
    r_list.extend([1, 2])
    assert list(r_list) == [1, 2]


def test_remove(r):
    r_list = RedisList(r, 'a', [1, 2, 1])
    r_list.remove(1)
    assert list(r_list) == [2, 1]
    with pytest.raises(ValueError):
        r_list.remove(3)


def test_pop(r):
    r_list = RedisList(r, 'a', [1, 2])
    assert r_list.pop() == 2
    r_list.pop()
    with pytest.raises(IndexError):
        r_list.pop()


def test_get_item(r):
    r_list = RedisList(r, 'a', [1, 2, 3, 4, 5])
    assert r_list[1] == 2
    assert r_list[1:4] == [2, 3, 4]
    assert r_list[::2] == [1, 3, 5]
    with pytest.raises(TypeError):
        r_list['a']
    with pytest.raises(IndexError):
        r_list[5]


def test_set_item(r):
    r_list = RedisList(r, 'a', [1])
    r_list[0] = 2
    assert r_list[0] == 2
    with pytest.raises(IndexError):
        r_list[1] = 1


def test_len(r):
    r_list = RedisList(r, 'a', [1])
    assert len(r_list) == 1


def test_iter(r):
    r_list = RedisList(r, 'a', [1])
    assert list(r_list) == [1]


def test_repr(r):
    r_list = RedisList(r, 'a', [1])
    assert str(r_list) == 'RedisList: [1]'


def test_object_is_not_changed(r):
    r_list = RedisList(r, 'a', [{1: 1}])
    r_list[0][1] = 2
    assert r_list[0][1] == 1
