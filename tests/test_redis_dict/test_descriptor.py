def test_set_empty_dict(r, redis_dict, model_with_redis_dict_field):
    """Should remove existing key in Redis."""
    test_object = model_with_redis_dict_field()
    assert test_object.redis_field == redis_dict

    test_object.redis_field = {}
    assert test_object.redis_field.copy() == {}
    assert r.keys() == []


def test_set_new_value(str_dict, redis_dict, model_with_redis_dict_field, another_str_dict):
    """Should override existing value."""
    test_object = model_with_redis_dict_field()
    assert test_object.redis_field.copy() == redis_dict.copy() == str_dict

    test_object.redis_field = another_str_dict
    assert test_object.redis_field.copy() == another_str_dict


def test_set_new_value_without_pickling(
    str_dict,
    bytes_dict,
    model_with_redis_dict_field_without_pickling
):
    """Should set str_dict and return bytes_dict."""
    test_object = model_with_redis_dict_field_without_pickling()
    test_object.redis_field = str_dict
    assert test_object.redis_field.copy() == bytes_dict
