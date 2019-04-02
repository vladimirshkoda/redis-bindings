import pytest
import random

from redistypes import RedisList

from tests.conftest import (
    REDIS_TEST_KEY_NAME,
    VAL_1,
    VAL_2,
    VAL_3,
)


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


class TestExtend(object):
    """Test ``extend`` method."""

    def test_extend(self, redis_list, str_list, another_str_list):
        """Should be equal to str_list extended by another_str_list."""
        redis_list.extend(another_str_list)
        str_list.extend(another_str_list)
        assert list(redis_list) == str_list

    def test_extend_without_pickling(
        self,
        redis_list_without_pickling,
        bytes_list,
        another_str_list,
    ):
        """Should be equal to bytes_dict extended by encoded another_str_list."""
        redis_list_without_pickling.extend(another_str_list)
        bytes_list.extend([item.encode() for item in another_str_list])
        assert list(redis_list_without_pickling) == bytes_list


class TestRemove(object):
    """Test ``remove`` method."""

    def test_single_item(self, redis_list, str_list):
        """Should remove a single item."""
        redis_list.remove(VAL_1)
        str_list.remove(VAL_1)
        assert list(redis_list) == str_list

    def test_duplicated_item(self, redis_list, str_list):
        """Should remove one of two equal items."""
        redis_list.remove(VAL_2)
        str_list.remove(VAL_2)
        assert list(redis_list) == str_list

    def test_nonexistent_item(self, redis_list):
        """Should raise ValueError."""
        with pytest.raises(ValueError):
            redis_list.remove(VAL_3)

    def test_single_item_without_pickling(self, redis_list_without_pickling, bytes_list):
        """Should remove a single encoded item."""
        redis_list_without_pickling.remove(VAL_1)
        bytes_list.remove(VAL_1.encode())
        assert list(redis_list_without_pickling) == bytes_list


class TestPop(object):
    """Test ``pop`` method."""

    def test_pop_from_empty_list(self, redis_empty_list):
        """Should raise IndexError."""
        with pytest.raises(IndexError):
            redis_empty_list.pop()

    def test_pop(self, redis_list, str_list):
        """Should remove and return the same item as str_list does."""
        assert redis_list.pop() == str_list.pop()
        assert list(redis_list) == str_list

    def test_pop_without_pickling(self, redis_list_without_pickling, bytes_list):
        """Should remove and return the same item as bytes_list does."""
        assert redis_list_without_pickling.pop() == bytes_list.pop()
        assert list(redis_list_without_pickling) == bytes_list


class TestGetItem(object):
    """Test ``__getitem__`` method."""

    def test_invalid_index_type(self, redis_list):
        """Should raise TypeError."""
        with pytest.raises(TypeError):
            redis_list['random_string']

    def test_int_index(self, redis_list, str_list):
        """Should return the same item as str_list does."""
        index = random.randint(0, len(str_list) - 1)
        assert redis_list[index] == str_list[index]

    def test_int_index_without_pickling(self, redis_list_without_pickling, bytes_list):
        """Should return the same item as bytes_list does."""
        index = random.randint(0, len(bytes_list) - 1)
        assert redis_list_without_pickling[index] == bytes_list[index]

    def test_index_out_of_range(self, redis_list):
        """Should raise IndexError."""
        with pytest.raises(IndexError):
            assert redis_list[len(redis_list)]

    def test_slice_index(self, redis_list, str_list):
        """Should return the same items as str_list returns."""
        assert redis_list[0:len(redis_list) - 1:1] == redis_list[0:len(str_list) - 1:1]


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
