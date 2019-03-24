import pytest

from redistypes.bindings import RedisDict


REDIS_TEST_KEY_NAME = 'redis_key_name'
KEY_1, VAL_1 = 'KEY_1', 'VAL_1'
KEY_2, VAL_2 = 'KEY_2', 'VAL_2'
KEY_3, VAL_3 = 'KEY_3', 'VAL_3'
STR_DICT = {KEY_1: VAL_1, KEY_2: VAL_2}
ANOTHER_STR_DICT = {KEY_3: VAL_3}
BYTES_DICT = {k.encode(): v.encode() for k, v in STR_DICT.items()}


@pytest.fixture
def str_dict():
    """Copy of STR_DICT."""
    return STR_DICT.copy()


@pytest.fixture
def bytes_dict():
    """Copy of BYTES_DICT."""
    return BYTES_DICT.copy()


@pytest.fixture
def another_str_dict():
    """Copy of ANOTHER_STR_DICT."""
    return ANOTHER_STR_DICT.copy()


@pytest.fixture
def redis_empty_dict(r):
    """
    RedisDict bonded to empty hash in Redis.

    RedisDict: {}
    """
    return RedisDict(r, REDIS_TEST_KEY_NAME)


@pytest.fixture
def redis_dict(r, str_dict):
    """
    RedisDict bonded to STR_DICT hash in Redis.

    RedisDict: {'KEY_1': 'VAL_1', 'KEY_2': 'VAL_2'}
    """
    return RedisDict(r, REDIS_TEST_KEY_NAME, str_dict)


@pytest.fixture
def redis_dict_without_pickling(r, str_dict):
    """
    RedisDict bonded to BYTES_DICT hash in Redis.

    RedisDict: {b'KEY_1': b'VAL_1', b'KEY_2': b'VAL_2'}
    """
    return RedisDict(r, REDIS_TEST_KEY_NAME, str_dict, pickling=False)
