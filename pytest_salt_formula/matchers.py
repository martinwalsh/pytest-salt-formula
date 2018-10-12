# -*- coding: utf-8 -*-
from expects import have_properties
from expects.matchers import Matcher

__all__ = ['contain_id']


class _LowState(object):
    def __init__(self, states):
        self.states = states

    def __contains__(self, _id):
        return _id in [s['__id__'] for s in self.states]


class _ContainsIdWith(object):
    def __init__(self, _id, _data):
        self._data = _LowState(_data)
        self._id = _id

    def __bool__(self):
        return self._id in self._data

    __nonzero__ = __bool__


class contain_id(Matcher):
    def __init__(self, _id):
        self._expected = _id

    def _match(self, lowstate):
        return _ContainsIdWith(self._expected, lowstate)
