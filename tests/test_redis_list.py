import pytest

from bindings import RedisList


def test_init_with_not_iterable(r):
    with pytest.raises(ValueError):
        RedisList(r, 'a', 1)


def test_init_to_wrong_type(r):
    r.hset('a', 1, 1)
    with pytest.raises(TypeError):
        RedisList(r, 'a')


def test_init_with_new_values(r):
    r_list = RedisList(r, 'a', [1])
    assert r_list.values == [1]


def test_init_with_old_values(r):
    r_list = RedisList(r, 'a', [1])
    r_list_2 = RedisList(r, 'a')
    assert r_list.values == r_list_2.values
    assert r_list == r_list_2
    assert r_list is not r_list_2
    assert r_list != RedisList(r, 'b')


def test_disable_pickling(r):
    r_list = RedisList(r, 'a', [1], pickling=False)
    assert r_list.values == ['1']


def test_append(r):
    r_list = RedisList(r, 'a')
    r_list.append(1)
    assert r_list.values == [1]


def test_extend(r):
    r_list = RedisList(r, 'a')
    r_list.extend([1, 2])
    assert r_list.values == [1, 2]


def test_remove(r):
    r_list = RedisList(r, 'a', [1, 2, 1])
    r_list.remove(1)
    assert r_list.values == [2, 1]
    with pytest.raises(ValueError):
        r_list.remove(3)


def test_pop(r):
    r_list = RedisList(r, 'a', [1, 2])
    assert r_list.pop() == 2
    r_list.pop()
    with pytest.raises(IndexError):
        r_list.pop()


def test_pop_without_pickling(r):
    r_list = RedisList(r, 'a', ['', None], pickling=False)
    assert r_list.pop() == 'None'
    assert r_list.pop() == ''


def test_get_item(r):
    r_list = RedisList(r, 'a', [1, 2, 3, 4, 5])
    assert r_list[1] == 2
    assert r_list[1:4] == [2, 3, 4]
    assert r_list[::2] == [1, 3, 5]
    with pytest.raises(TypeError):
        r_list['a']
    with pytest.raises(IndexError):
        r_list[5]


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


def test_changing_object(r):
    r_list = RedisList(r, 'a', [{1: 1}])
    r_list[0][1] = 2
    assert r_list[0][1] == 1
