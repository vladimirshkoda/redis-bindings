import pytest
import redis

REDIS_TEST_KEY_NAME = 'redis_key_name'
VAL_1 = 'VAL_1'
VAL_2 = 'VAL_2'
VAL_3 = 'VAL_3'


@pytest.fixture()
def r():
    """Redis client."""
    client = redis.Redis(host='localhost', port=6379, db=9)
    client.flushdb()
    yield client
    client.flushdb()
    client.connection_pool.disconnect()
