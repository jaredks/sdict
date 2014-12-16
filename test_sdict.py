import sys
import pytest
from sdict import sdict

py3 = sys.version_info >= (3, 0, 0)


@pytest.fixture
def structures():
    return {
        'a': sdict([(1, 10), (2, 20), (3, 30)]),
        'b': sdict([('foo', 'foobar'), ('swag', 'swagger'), ('yolo', '420'), ('blaze', 'it')])
    }


def test_dict_functionality(structures):
    d = structures['a']

    d[2] = 22
    del d[3]
    d.update([('swag', 9000)])

    assert set(d.items()) == set([(1, 10), (2, 22), ('swag', 9000)])

    with pytest.raises(KeyError):
        d['yolo']

    d.update({9: 9999})
    d.update([(10, 101010), (1, 111)])

    assert set(d.items()) == set([(1, 111), (2, 22), ('swag', 9000), (9, 9999), (10, 101010)])


def test_insertion(structures):
    a = structures['a']

    a.insert(2, (2.5, 25), before=False)
    assert list(a.sliceitems()) == [(1, 10), (2, 20), (2.5, 25), (3, 30)]

    a.insert(2, (1.5, 15))
    assert list(a.sliceitems()) == [(1, 10), (1.5, 15), (2, 20), (2.5, 25), (3, 30)]

    a.insert(1, (0, 0))
    assert list(a.sliceitems()) == [(0, 0), (1, 10), (1.5, 15), (2, 20), (2.5, 25), (3, 30)]

    a.insert(3, (4, 40), before=False)
    assert list(a.sliceitems()) == [(0, 0), (1, 10), (1.5, 15), (2, 20), (2.5, 25), (3, 30), (4, 40)]


def test_insertion_exceptions(structures):
    a = structures['a']

    with pytest.raises(KeyError):
        a.insert(5, (6, 60), before=False)
    with pytest.raises(TypeError):
        a.insert({}, (6, 60), before=False)
    with pytest.raises(ValueError):
        a.insert(3, 'yolo', before=False)


def test_slice(structures):
    a = structures['a']
    b = structures['b']

    assert list(a[1:3]) == [10, 20]
    assert list(a[1:]) == [10, 20, 30]

    assert list(b['swag':'blaze']) == ['swagger', '420']


def test_slice_exceptions(structures):
    b = structures['b']

    with pytest.raises(KeyError):
        list(b[0:3])


def test_keys(structures):
    b = structures['b']

    assert list(b.slicekeys())                == ['foo', 'swag', 'yolo', 'blaze']
    assert list(b.slicekeys(start='swag'))    == ['swag', 'yolo', 'blaze']
    assert list(b.slicekeys('yolo'))          == ['yolo', 'blaze']
    assert list(b.slicekeys('swag', 'blaze')) == ['swag', 'yolo']
    assert list(b.slicekeys(stop='blaze'))    == ['foo', 'swag', 'yolo']


def test_values(structures):
    b = structures['b']
    assert list(b.slicevalues()) == ['foobar', 'swagger', '420', 'it'] == list(b[:])


def test_items(structures):
    b = structures['b']
    assert list(b.sliceitems()) == [('foo', 'foobar'), ('swag', 'swagger'), ('yolo', '420'), ('blaze', 'it')]


def test_slice_deletion(structures):
    b = structures['b']
    del b['swag':'blaze']
    assert list(b.slicekeys()) == ['foo', 'blaze']


def test_slice_assignment_1(structures):
    b = structures['b']
    b['swag':'blaze'] = structures['a']
    assert list(b.slicekeys()) == ['foo',    1,  2,  3,  'blaze']
    assert list(b.slicevalues()) == ['foobar', 10, 20, 30, 'it']


def test_slice_assignment_2(structures):
    b = structures['b']
    b['swag':'swag'] = structures['a']

    assert list(b.slicekeys())   == ['foo',    1,  2,  3,  'swag',    'yolo', 'blaze']
    assert list(b.slicevalues()) == ['foobar', 10, 20, 30, 'swagger', '420',  'it']
    assert list(b.sliceitems()) == [
        ('foo', 'foobar'), (1, 10), (2, 20), (3, 30), ('swag', 'swagger'), ('yolo', '420'), ('blaze', 'it')
    ]


def test_slice_assignment_3(structures):
    b = structures['b']
    b['swag':'yolo'] = structures['a']

    assert list(b.slicekeys())   == ['foo',    1,  2,  3,  'yolo', 'blaze']
    assert list(b.slicevalues()) == ['foobar', 10, 20, 30, '420',  'it']
    assert list(b.sliceitems())  == [('foo', 'foobar'), (1, 10), (2, 20), (3, 30), ('yolo', '420'), ('blaze', 'it')]
