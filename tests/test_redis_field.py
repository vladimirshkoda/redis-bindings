from descriptors import BaseRedisField


class BaseRedisTestField(BaseRedisField):
    def get_key_name(self, instance):
        return 'a'


def test_descriptor(r):
    r_field = BaseRedisTestField(r)
    r_field.__set__(instance=None, value={1: 1})
    assert r_field.__get__(instance=None, owner=None) == {1: 1}
    r_field.__delete__(instance=None)
    assert r_field.__get__(instance=None, owner=None) is None


def test_descriptor_with_existing_value(r):
    r_field = BaseRedisTestField(r)
    r_field2 = BaseRedisTestField(r)
    r_field.__set__(instance=None, value=1)
    assert r_field.__get__(instance=None, owner=None) == r_field2.__get__(instance=None, owner=None)


def test_disable_pickling(r):
    r_field = BaseRedisTestField(r, pickling=False)
    r_field.__set__(instance=None, value=1)
    assert r_field.__get__(instance=None, owner=None) == '1'


def test_object_is_not_changed(r):
    r_field = BaseRedisTestField(r)
    r_field.__set__(instance=None, value={1: 1})
    r_field.__get__(instance=None, owner=None)[1] = 2
    assert r_field.__get__(instance=None, owner=None)[1] == 1
