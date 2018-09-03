import pytest

from bindings import RedisList


class TestRedisList(object):

    def test_init_with_not_iterable(self, r):
        with pytest.raises(ValueError):
            RedisList(r, 'a', 1)

    def test_init_to_wrong_type(self, r):
        r.hset('a', 1, 1)
        with pytest.raises(TypeError):
            RedisList(r, 'a')

    def test_init_with_new_values(self, r):
        r_list = RedisList(r, 'a', [1])
        assert r_list.values == [1]

    def test_init_with_old_values(self, r):
        r_list = RedisList(r, 'a', [1])
        r_list_2 = RedisList(r, 'a')
        assert r_list.values == r_list_2.values
        assert r_list == r_list_2
        assert r_list is not r_list_2
        assert r_list != RedisList(r, 'b')

    def test_disable_pickling(self, r):
        r_list = RedisList(r, 'a', [1], pickling=False)
        assert r_list.values == ['1']

    def test_append(self, r):
        r_list = RedisList(r, 'a')
        r_list.append(1)
        assert r_list.values == [1]

    def test_extend(self, r):
        r_list = RedisList(r, 'a')
        r_list.extend([1, 2])
        assert r_list.values == [1, 2]

    def test_remove(self, r):
        r_list = RedisList(r, 'a', [1, 2, 1])
        r_list.remove(1)
        assert r_list.values == [2, 1]
        with pytest.raises(ValueError):
            r_list.remove(3)

    def test_pop(self, r):
        r_list = RedisList(r, 'a', [1, 2])
        assert r_list.pop() == 2
        r_list.pop()
        with pytest.raises(IndexError):
            r_list.pop()

    def test_get_item(self, r):
        r_list = RedisList(r, 'a', [1, 2, 3, 4, 5])
        assert r_list[1] == 2
        assert r_list[1:4] == [2, 3, 4]
        assert r_list[::2] == [1, 3, 5]
        with pytest.raises(TypeError):
            r_list['a']

    def test_len(self, r):
        r_list = RedisList(r, 'a', [1])
        assert len(r_list) == 1

    def test_iter(self, r):
        r_list = RedisList(r, 'a', [1])
        assert list(r_list) == [1]

    def test_repr(self, r):
        r_list = RedisList(r, 'a', [1])
        assert str(r_list) == 'RedisList: [1]'
