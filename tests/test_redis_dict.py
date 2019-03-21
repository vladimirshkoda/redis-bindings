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

    RedisDict: {'KEY_1': 'VAL_2', 'KEY_2': 'VAL_2'}
    """
    return RedisDict(r, REDIS_TEST_KEY_NAME, str_dict)


@pytest.fixture
def redis_dict_without_pickling(r, str_dict):
    """
    RedisDict bonded to BYTES_DICT hash in Redis.

    RedisDict: {b'KEY_1': b'VAL_2', b'KEY_2': b'VAL_2'}
    """
    return RedisDict(r, REDIS_TEST_KEY_NAME, str_dict, pickling=False)


class TestInit(object):
    """Test __init__ method."""

    def test_init_with_not_mapping_data_type(self, r):
        """Should raise ValueError."""
        # Test int
        with pytest.raises(ValueError):
            RedisDict(r, REDIS_TEST_KEY_NAME, 1)

        # Test list
        with pytest.raises(ValueError):
            RedisDict(r, REDIS_TEST_KEY_NAME, [1, 2])

    def test_bind_to_string(self, r):
        """Should raise TypeError."""
        r.set(REDIS_TEST_KEY_NAME, 1)
        with pytest.raises(TypeError):
            RedisDict(r, REDIS_TEST_KEY_NAME)

    def test_bind_to_list(self, r):
        """Should raise TypeError."""
        r.rpush(REDIS_TEST_KEY_NAME, 1)
        with pytest.raises(TypeError):
            RedisDict(r, REDIS_TEST_KEY_NAME)

    def test_bind_to_none(self, r):
        """Should be initialized as an empty hash."""
        redis_dict = RedisDict(r, REDIS_TEST_KEY_NAME)
        assert redis_dict.items() == []

    def test_bind_to_hash(self, r, bytes_dict):
        """Should have the same items as BYTES_DICT."""
        r.hmset(REDIS_TEST_KEY_NAME, bytes_dict)
        redis_dict = RedisDict(r, REDIS_TEST_KEY_NAME, pickling=False)
        assert redis_dict.items() == list(BYTES_DICT.items())

    def test_init_with_mapping(self, redis_dict):
        """Should have the same items as STR_DICT."""
        assert redis_dict.items() == list(STR_DICT.items())

    def test_init_with_disabled_pickling(self, redis_dict_without_pickling):
        """
        Should have the same items as BYTES_DICT.

        With pickling=False, should have the same items as BYTES_DICT, despite of
        it was initialized with STR_DICT.
        """
        assert redis_dict_without_pickling.items() == list(BYTES_DICT.items())

    def test_override_previous_hash(self, r, str_dict, another_str_dict):
        """
        Should have the same items as ANOTHER_STR_DICT.

        Despite of it was initialized with STR_DICT.
        """
        redis_dict = RedisDict(r, REDIS_TEST_KEY_NAME, str_dict)
        assert redis_dict.items() == list(str_dict.items())

        redis_dict = RedisDict(r, REDIS_TEST_KEY_NAME, another_str_dict)
        assert redis_dict.items() == list(another_str_dict.items()) != list(str_dict.items())


class TestContains(object):
    """Test __contains__ method."""

    def test_empty_hash(self, redis_empty_dict):
        """
        Should not find any key in the empty hash.

        It is more like to test whether HEXISTS method of Redis works with the none type.
        """
        assert KEY_1 not in redis_empty_dict

    def test_not_empty_hash(self, redis_dict):
        """Should find keys that are presented in STR_DICT."""
        assert KEY_1 in STR_DICT and KEY_1 in redis_dict
        assert KEY_3 not in STR_DICT and KEY_3 not in redis_dict

    def test_not_empty_hash_without_pickling(self, redis_dict_without_pickling):
        """Should find keys that are presented in BYTES_DICT."""
        encoded_key = KEY_1.encode()
        assert encoded_key in redis_dict_without_pickling and encoded_key in BYTES_DICT


class TestLen(object):
    """Test __len__ method."""

    def test_empty_hash(self, redis_empty_dict):
        """
        Should return 0.

        Casting to bool should be False.
        """
        assert len(redis_empty_dict) == 0
        assert bool(redis_empty_dict) is False

    def test_not_empty_hash(self, redis_dict):
        """
        Should return length of STR_DICT.

        Casting to bool should be True.
        """
        assert len(redis_dict) == len(STR_DICT) == 2
        assert bool(redis_dict) is True


class TestKeys(object):
    """Test keys method."""

    def test_empty_hash(self, redis_empty_dict):
        """Should return an empty list."""
        assert redis_empty_dict.keys() == []

    def test_not_empty_hash(self, redis_dict):
        """Should have the same keys as STR_DICT."""
        assert redis_dict.keys() == list(STR_DICT.keys())

    def test_not_empty_hash_without_pickling(self, redis_dict_without_pickling):
        """Should have the same keys as BYTES_DICT."""
        assert redis_dict_without_pickling.keys() == list(BYTES_DICT.keys())


class TestValues(object):
    """Test items method."""

    def test_empty_hash(self, redis_empty_dict):
        """Should return an empty list."""
        assert redis_empty_dict.values() == []

    def test_not_empty_hash(self, redis_dict):
        """Should have the same values as STR_DICT."""
        assert redis_dict.values() == list(STR_DICT.values())

    def test_not_empty_hash_without_pickling(self, redis_dict_without_pickling):
        """Should have the same values as BYTES_DICT."""
        assert redis_dict_without_pickling.values() == list(BYTES_DICT.values())


class TestSetDefault(object):
    """Test setdefault method."""

    def test_key_already_exists(self, redis_dict):
        """Should return already existing value."""
        assert redis_dict.setdefault(KEY_1, VAL_3) == VAL_1

    def test_key_does_not_exist(self, redis_dict):
        """Should return new value."""
        assert redis_dict.setdefault(KEY_3, VAL_3) == VAL_3

    def test_key_already_exists_without_pickling(self, redis_dict_without_pickling):
        """Should return already existing value in bytes."""
        assert redis_dict_without_pickling.setdefault(KEY_1, VAL_3) == VAL_1.encode()

    def test_key_does_not_exist_without_pickling(self, redis_dict_without_pickling):
        """Should return new value in bytes."""
        assert redis_dict_without_pickling.setdefault(KEY_3, VAL_3) == VAL_3.encode()
