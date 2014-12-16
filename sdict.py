# -*- coding: utf-8 -*-

"""
    sdict
    ~~~~~

    dict subclass with slicing and insertion.

"""

__title__ = 'sdict'
__version__ = '0.1.0'
__author__ = 'Jared Suttles'
__license__ = 'Modified BSD'
__copyright__ = 'Copyright 2014 Jared Suttles'

import sys as _sys
try:
    from collections import (MutableMapping as _DictMixin, KeysView as
    _KeysView, ValuesView as _ValuesView, ItemsView as _ItemsView)
except ImportError:
    from UserDict import _DictMixin
try:
    from itertools import imap as _imap
except ImportError:
    _imap = map
try:
    from thread import get_ident as _get_ident
except ImportError:
    from _thread import get_ident as _get_ident
from operator import eq as _eq

_py   = _sys.version_info
_py27 = (2, 7, 0) <= _py < (2, 8, 0)
_py3  = _py >= (3, 0, 0)


class sdict(dict):
    def __init__(self, other=None, **kwds):
        self.__root = root = []
        root[:] = [root, root, None]
        self.__map = {}
        self.__update({} if other is None else other, **kwds)

    __update = update = _DictMixin.update
    __marker = object()

    def __insert(self, link_prev, key_value):
        key, value = key_value
        if link_prev[2] != key:
            if key in self:
                del self[key]
            link_next = link_prev[1]
            link = [link_prev, link_next, key]
            self.__map[key] = link_prev[1] = link_next[0] = link
        super(self.__class__, self).__setitem__(key, value)

    def __iterate(self, start, stop, step):
        # todo implement step
        step = self.__slice_step(step)  # guarentee None or int
        move = 1 if step is None or step > 0 else 0
        root = self.__root
        curr = root[move] if start is None else self.__map[start]
        key = curr[2]
        while (key != stop) or (stop is None and curr is not root):
            yield curr
            curr = curr[move]
            key = curr[2]

    def __slice_step(self, step):
        if not (step is None or isinstance(step, (int, long))):
            if hasattr(step, '__index__'):
                step = step.__index__()
                if not isinstance(step, (int, long)):
                    raise TypeError(
                        '__index__ returned non-(int,long) (type %s)' %
                        type(step).__name__
                    )
            else:
                raise TypeError('slice indices must be integers or None')
        elif step == 0:
            raise ValueError('slice step cannot be zero')
        return step

    def __delete_section(self, start, stop, step):
        # will delete the section spanning start to stop
        # including start; excluding stop
        # closes the gap; start-> stop+1 and start<-stop+1
        # return the left and right link, allowing for slice assignment
        links = self.__iterate(start, stop, step)

        try:
            first = last = next(links)
        except StopIteration:            # meaning start == stop
            link = self.__map[start][0]  # go back one since...
            return link, link[1]         # we possibly want to insert *before*

        for link in links:
            key = link[2]
            super(self.__class__, self).__delitem__(key)
            del self.__map[key]
            last = link
        left = first[0]
        right = last[1]
        left[1] = right
        right[0] = left
        return left, right

    def __getitem__(self, key):
        if isinstance(key, slice):
            return self.slicevalues(key.start, key.stop, key.step)
        return super(self.__class__, self).__getitem__(key)

    def __setitem__(self, key, value):
        if isinstance(key, slice):
            d = self.__class__(value)  # check valid before changing internals
            prev, end = self.__delete_section(key.start, key.stop, key.step)
            for key, value in d.sliceitems():
                curr = [prev, end, key]
                prev[1] = curr
                prev = curr
                super(self.__class__, self).__setitem__(key, value)
            end[0] = prev
        else:
            if key not in self:
                root = self.__root
                last = root[0]
                last[1] = root[0] = self.__map[key] = [last, root, key]
            super(self.__class__, self).__setitem__(key, value)

    def __delitem__(self, key):
        if isinstance(key, slice):
            self.__delete_section(key.start, key.stop, key.step)
        else:
            super(self.__class__, self).__delitem__(key)
            link_prev, link_next, _ = self.__map.pop(key)
            link_prev[1] = link_next
            link_next[0] = link_prev

    def __iter__(self):
        for _, _, key in self.__iterate(None, None, None):
            yield key

    def __reversed__(self):
        for _, _, key in self.__iterate(None, None, -1):
            yield key

    def slicekeys(self, start=None, stop=None, step=None):
        for _, _, key in self.__iterate(start, stop, step):
            yield key

    def slicevalues(self, start=None, stop=None, step=None):
        for key in self.slicekeys(start, stop, step):
            yield self[key]

    def sliceitems(self, start=None, stop=None, step=None):
        for key in self.slicekeys(start, stop, step):
            yield key, self[key]

    def insert(self, key, key_value, before=True):
        link = self.__map[key]
        if before:
            link = link[0]
        self.__insert(link, key_value)

    def clear(self):
        root = self.__root
        root[:] = [root, root, None]
        self.__map.clear()
        dict.clear(self)

    def pop(self, key, default=__marker):
        if key in self:
            result = self[key]
            del self[key]
            return result
        if default is self.__marker:
            raise KeyError(key)
        return default

    def setdefault(self, key, default=None):
        if key in self:
            return self[key]
        self[key] = default
        return default

    def popitem(self, last=True):
        if not self:
            raise KeyError('dictionary is empty')
        key = next(reversed(self) if last else iter(self))
        value = self.pop(key)
        return key, value

    def __repr__(self, _repr_running={}):
        call_key = id(self), _get_ident()
        if call_key in _repr_running:
            return '...'
        _repr_running[call_key] = 1
        try:
            if not self:
                return '%s()' % (self.__class__.__name__,)
            return '%s(%r)' % (self.__class__.__name__, self.items())
        finally:
            del _repr_running[call_key]

    def __reduce__(self):
        items = [[k, self[k]] for k in self]
        inst_dict = vars(self).copy()
        for k in vars(self.__class__()):
            inst_dict.pop(k, None)
        if inst_dict:
            return (self.__class__, (items,), inst_dict)
        return self.__class__, (items,)

    def copy(self):
        return self.__class__(self)

    @classmethod
    def fromkeys(cls, iterable, value=None):
        self = cls()
        for key in iterable:
            self[key] = value
        return self

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return dict.__eq__(self, other) and all(_imap(_eq, self, other))
        return dict.__eq__(self, other)

    def __ne__(self, other):
        return not self.__eq__(other)

    if _py3:
        def keys(self):
            return _KeysView(self)

        def values(self):
            return _ValuesView(self)

        def items(self):
            return _ItemsView(self)

    else:
        def keys(self):
            return list(self)

        def values(self):
            return [self[key] for key in self]

        def items(self):
            return [(key, self[key]) for key in self]

        def iterkeys(self):
            return iter(self)

        def itervalues(self):
            for key in self:
                yield self[key]

        def iteritems(self):
            for key in self:
                yield key, self[key]

        if _py27:
            def viewkeys(self):
                return _KeysView(self)

            def viewvalues(self):
                return _ValuesView(self)

            def viewitems(self):
                return _ItemsView(self)
