import pytest
import redis


@pytest.fixture()
def r():
    """Redis client."""
    client = redis.Redis(host='localhost', port=6379, db=9)
    client.flushdb()
    yield client
    client.flushdb()
    client.connection_pool.disconnect()
