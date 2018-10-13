# -*- coding: utf-8 -*-
from expects.matchers import Matcher

__all__ = ['contain_id']


class StatefulMatcher(Matcher):
    def __init__(self, expected, parent=None):
        self._expected = expected
        self._parent = parent
        self._matched = None

    def _match(self, subject):
        raise NotImplementedError(
            'subclasses should implement `_match` method'
        )


class PropertyValue(StatefulMatcher):
    def _match(self, lowstate):
        ok, reasons = self._parent._match(lowstate)

        if not ok:
            return ok, reasons

        ok = self._expected == self._parent._matched
        if not ok:
            reasons.append(
                'value {!r} does not match property {!r} from state with id {!r}'.format(
                    self._expected, self._parent._matched, self._parent._parent._expected
                )
            )
        return ok, reasons

    def __getattr__(self, attr):
        if attr.startswith('with_'):
            return HasProperty(attr[5:], self._parent._parent)
        raise AttributeError(
            "'{}' object has no attribute '{}'".format(self.__class__.__name__, attr)
        )


class HasProperty(StatefulMatcher):
    def _match(self, lowstate):
        ok, reasons = self._parent._match(lowstate)
        try:
            self._matched = self._parent._matched[self._expected]
        except KeyError:
            reasons.append(
                '{!r} property not found in state with id {!r}'.format(
                    self._expected, self._parent._expected
                )
            )
        return self._matched is not None, reasons

    def __call__(self, value):
        return PropertyValue(value, self)


class contain_id(StatefulMatcher):
    def _match(self, lowstate):
        for state in lowstate:
            if self._expected == state['__id__']:
                self._matched = state

        ok, reasons = self._matched is not None, []
        if not ok:
            reasons.append('state with id {!r} not found'.format(self._expected))
        return ok, reasons

    def __getattr__(self, attr):
        if attr.startswith('with_'):
            return HasProperty(attr[5:], self)
        raise AttributeError(
            "'{}' object has no attribute '{}'".format(self.__class__.__name__, attr)
        )
