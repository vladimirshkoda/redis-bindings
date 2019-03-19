import pytest

from redistypes.bindings import RedisDict

REDIS_TEST_KEY_NAME = 'redis_key_name'
KEY_1 = 'KEY_1'
KEY_2 = 'KEY_2'
VAL_1 = 'VAL_1'
VAL_2 = 'VAL_2'
TEST_DICT = {KEY_1: VAL_2, KEY_2: VAL_2}
TEST_B_DICT = {k.encode(): v.encode() for k, v in TEST_DICT.items()}


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
        assert not redis_dict

    def test_bind_to_hash(self, r):
        """Should have the same items as TEST_B_DICT."""
        test_dict = TEST_B_DICT.copy()
        r.hmset(REDIS_TEST_KEY_NAME, test_dict)
        redis_dict = RedisDict(r, REDIS_TEST_KEY_NAME, pickling=False)
        assert redis_dict.items() == test_dict.items()

    def test_init_with_mapping(self, r):
        """Should have the same items as TEST_DICT."""
        test_dict = TEST_DICT.copy()
        redis_dict = RedisDict(r, REDIS_TEST_KEY_NAME, test_dict)
        assert test_dict.items() == redis_dict.items()

    def test_init_with_disabled_pickling(self, r):
        """
        Should have the same items as TEST_B_DICT.

        With pickling=False, should have the same items as TEST_B_DICT, despite of
        it was initialized with TEST_DICT.
        """
        test_dict = TEST_DICT.copy()
        redis_dict = RedisDict(r, REDIS_TEST_KEY_NAME, test_dict, pickling=False)
        assert redis_dict.items() == TEST_B_DICT.copy().items()

    def test_override_previous_hash(self, r):
        """Should have new items, despite of it was initialized with TEST_DICT."""
        test_dict = TEST_DICT.copy()
        redis_dict = RedisDict(r, REDIS_TEST_KEY_NAME, test_dict)
        assert redis_dict.items() == test_dict.items()

        new_dict = {'new_key': 'new_value'}
        redis_dict = RedisDict(r, REDIS_TEST_KEY_NAME, new_dict)
        assert redis_dict.items() == new_dict.items() and TEST_DICT != new_dict


class TestContains(object):
    """Test __contains__ method."""

    def test_empty_hash(self, r):
        """
        Should not find any key in the empty hash.

        It is more like to test whether HEXISTS method of Redis works with the none type.
        """
        redis_dict = RedisDict(r, REDIS_TEST_KEY_NAME)
        assert KEY_1 not in redis_dict

    def test_not_empty_hash(self, r):
        """Should find keys that are presented in TEST_DICT."""
        redis_dict = RedisDict(r, REDIS_TEST_KEY_NAME, TEST_DICT.copy())
        assert KEY_1 in TEST_DICT and KEY_1 in redis_dict

        non_existent_key = 'non_existent_key'
        assert non_existent_key not in TEST_DICT and non_existent_key not in redis_dict

    def test_not_empty_hash_without_pickling(self, r):
        """Should find keys that are presented in TEST_B_DICT."""
        redis_dict = RedisDict(r, REDIS_TEST_KEY_NAME, TEST_DICT.copy(), pickling=False)
        encoded_key = KEY_1.encode()
        assert encoded_key in redis_dict and encoded_key in TEST_B_DICT


class TestLen(object):
    """Test __len__ method."""

    def test_empty_hash(self, r):
        """
        Should return 0.

        Casting to bool should be False.
        """
        redis_dict = RedisDict(r, REDIS_TEST_KEY_NAME)
        assert len(redis_dict) == 0
        assert bool(redis_dict) is False

    def test_not_empty_hash(self, r):
        """
        Should return length of TEST_DICT.

        Casting to bool should be True.
        """
        redis_dict = RedisDict(r, REDIS_TEST_KEY_NAME, TEST_DICT.copy())
        assert len(redis_dict) == len(TEST_DICT) == 2
        assert bool(redis_dict) is True
