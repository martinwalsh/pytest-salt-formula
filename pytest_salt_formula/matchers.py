# -*- coding: utf-8 -*-
import re

from expects import have_properties
from expects.matchers import Matcher

__all__ = ['contain_id']


class _Attrs(object):
    """
    Wraps a dictionary for attribute access by name.
    """
    pattern = re.compile(r'_(_\w+)__')

    def __init__(self, attrs):
        self.__attrs = attrs
        # replace dunder attributes with a single leading underscore
        for k, v in attrs.items():
            setattr(self, self.pattern.sub(r'\1', k), v)


class _With(object):
    def __init__(self, item, reasons):
        self.item = item
        self.reasons = reasons

    def __getattr__(self, attr):
        if attr.startswith('with_'):
            return self.with_(self.item[attr[5:]])
        raise AttributeError(
            "'{}' object has no attribute '{}'".format(self.__class__.__name__, attr)
        )

    def with_(self, attr):
        pass

    def __iter__(self):
        return iter((self.item is not False, self.reasons))


class value_(Matcher):
    def __init__(self, value, parent):
        self._expected = value
        self._parent = parent

    def _match(self, lowstate):
        ok, reasons = self._parent._match(lowstate)
        if self._expected != self._parent._matched:
            reasons.append('value {!r} does not match parent: {!r}'.format(self._expected, self._parent._matched))
            return False, reasons
        else:
            return True, reasons


class with_(Matcher):
    def __init__(self, attr, parent):
        self._expected = attr
        self._parent = parent
        self._matched = None

    def _match(self, lowstate):
        ok, reasons = self._parent._match(lowstate)

        if ok:
            try:
                self._matched = self._parent._matched[self._expected]
            except KeyError:
                reasons.append(
                    '`{}` not found in state with id `{}`'.format(
                        self._expected, self._parent._expected
                    )
                )
            else:
                reasons.append(
                    '`{}` found in state with id `{}`'.format(
                        self._expected, self._parent._expected
                    )
                )
                return True, reasons
        return False, reasons

    def __call__(self, value):
        return value_(value, self)


class contain_id(Matcher):
    def __init__(self, _id):
        self._expected = _id
        self._matched = None

    def _find_id(self, lowstate):
        for state in lowstate:
            if self._expected == state['__id__']:
                return state

    def _match(self, lowstate):
        self._matched = self._find_id(lowstate)
        if self._matched is not None:
            return True, ['id `{}` found'.format(self._expected)]
        return False, ['id `{}` not found'.format(self._expected)]

    def __getattr__(self, attr):
        if attr.startswith('with_'):
            return with_(attr[5:], self)
        raise AttributeError(
            "'{}' object has no attribute '{}'".format(self.__class__.__name__, attr)
        )

# class contain_id(Matcher):
#     def __init__(self, _id):
#         self._expected = _id
#
#     def _match(self, lowstate):
#         for state in lowstate:
#             if state['__id__'] == self._expected:
#                 return _With(state, ['id `{}` found'.format(self._expected)])
#         return _With(False, ['id `{}` not found'.format(self._expected)])



class _LowSLS(object):
    def __init__(self, states):
        self.states = [_State(state) for state in states]

    def __contains__(self, _id):
        return _id in [state._id for state in self.states]


class _ContainsIdWith(object):
    def __init__(self, _id, _data):
        self._data = _LowState(_data)
        self._id = _id

    def __bool__(self):
        return self._id in self._data

    __nonzero__ = __bool__
