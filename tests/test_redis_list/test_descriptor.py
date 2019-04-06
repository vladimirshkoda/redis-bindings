def test_set_empty_list(r, redis_list, model_with_redis_field):
    """Should remove existing key in Redis."""
    test_object = model_with_redis_field()
    assert test_object.redis_field == redis_list

    test_object.redis_field = []
    assert list(test_object.redis_field) == [] == r.keys()


def test_set_new_value(str_list, redis_list, model_with_redis_field, another_str_list):
    """Should override existing value."""
    test_object = model_with_redis_field()
    assert list(test_object.redis_field) == list(redis_list) == str_list

    test_object.redis_field = another_str_list
    assert list(test_object.redis_field) == another_str_list


def test_set_new_value_without_pickling(
    str_list,
    bytes_list,
    model_with_redis_field_without_pickling
):
    """Should set str_list and return bytes_list."""
    test_object = model_with_redis_field_without_pickling()
    test_object.redis_field = str_list
    assert list(test_object.redis_field) == bytes_list
