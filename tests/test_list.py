import pytest

from bindings import RedisList


class TestRedisList(object):

    def test_values(self, r):
        r_list = RedisList(r, 'a', 1)
        assert r_list.values == ['1']

    def test_append(self, r):
        r_list = RedisList(r, 'a')
        r_list.append(1)
        assert r_list.values == ['1']

    def test_extend(self, r):
        r_list = RedisList(r, 'a')
        r_list.extend([1, 2])
        assert r_list.values == ['1', '2']

    def test_remove(self, r):
        r_list = RedisList(r, 'a', 1, 2, 1)
        r_list.remove('1')
        assert r_list.values == ['2', '1']
        with pytest.raises(ValueError):
            r_list.remove('3')

    def test_get_item(self, r):
        r_list = RedisList(r, 'a', 1, 2, 1)
        assert r_list[1] == '2'
        assert r_list[1:2] == ['2', '1']
        with pytest.raises(TypeError):
            r_list['a']

    def test_len(self, r):
        r_list = RedisList(r, 'a', 1)
        assert len(r_list) == 1

    def test_iter(self, r):
        r_list = RedisList(r, 'a', 1)
        assert list(r_list) == ['1']

    def test_repr(self, r):
        r_list = RedisList(r, 'a', 1)
        assert str(r_list) == 'RedisList: [\'1\']'
