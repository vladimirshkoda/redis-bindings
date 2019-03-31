import pytest

from redistypes import RedisList

from tests.conftest import REDIS_TEST_KEY_NAME, VAL_1, VAL_2, VAL_3

STR_LIST = [VAL_1, VAL_2, VAL_2]
ANOTHER_STR_LIST = [VAL_3]
BYTES_LIST = [item.encode() for item in STR_LIST]


@pytest.fixture
def str_list():
    """Copy of STR_LIST."""
    return STR_LIST.copy()


@pytest.fixture
def another_str_list():
    """Copy of ANOTHER_STR_LIST."""
    return ANOTHER_STR_LIST.copy()


@pytest.fixture
def bytes_list():
    """Copy of BYTES_DICT."""
    return BYTES_LIST.copy()


@pytest.fixture
def redis_empty_list(r):
    """
    RedisList bonded to empty list in Redis.

    RedisList: []
    """
    return RedisList(r, REDIS_TEST_KEY_NAME)


@pytest.fixture
def redis_list(r, str_list):
    """
    RedisList bonded to STR_LIST list in Redis.

    RedisList: ['VAL_1', 'VAL_2', 'VAL_2']
    """
    return RedisList(r, REDIS_TEST_KEY_NAME, str_list)


@pytest.fixture
def redis_list_without_pickling(r, str_list):
    """
    RedisList bonded to BYTES_LIST list in Redis.

    RedisList: [b'VAL_1', b'VAL_2', b'VAL_2']
    """
    return RedisList(r, REDIS_TEST_KEY_NAME, str_list, pickling=False)
