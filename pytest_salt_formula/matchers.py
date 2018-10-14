# -*- coding: utf-8 -*-
from expects.matchers import Matcher

__all__ = ['contain_id', 'contain_pkg', 'contain_service', 'contain_file']


class StatefulMatcher(Matcher):
    def __init__(self, expected, parent=None):
        self._expected = expected
        self._parent = parent
        self._matched = None

    def _match(self, subject):
        raise NotImplementedError(
            'subclasses should implement `_match` method'
        )


class WithMethodsMixin(object):
    def __getattr__(self, attr):
        if attr.startswith('with_'):
            return HasPropertyMatcher(attr[5:], self._parent_reference)
        raise AttributeError(
            "'{}' object has no attribute '{}'".format(self.__class__.__name__, attr)
        )


class PropertyValueMatcher(StatefulMatcher, WithMethodsMixin):
    def __init__(self, expected, parent=None):
        super(PropertyValueMatcher, self).__init__(expected, parent)
        self._parent_reference = self._parent._parent

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


class HasPropertyMatcher(StatefulMatcher):
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
        return PropertyValueMatcher(value, self)


class ConditionalContainsMatcher(StatefulMatcher, WithMethodsMixin):
    _no_match = NotImplemented

    def __init__(self, expected, parent=None):
        super(ConditionalContainsMatcher, self).__init__(expected, parent)
        self._parent_reference = self

    def _is_match(self, state):
        raise NotImplementedError(
            'subclasses should implement an `_is_match` method'
        )

    def _match(self, lowstate):
        for state in lowstate:
            if self._is_match(state):
                self._matched = state
                break

        ok, reasons = self._matched is not None, []
        if not ok:
            reasons.append(self._no_match.format(self._expected))
        return ok, reasons


class contain_id(ConditionalContainsMatcher):
    _no_match = 'state with id {!r} not found'

    def _is_match(self, state):
        return self._expected == state['__id__']


class contain_pkg(ConditionalContainsMatcher):
    _no_match = 'no package state found with name {!r}'

    def _is_match(self, state):
        return state['state'] == 'pkg' and state['name'] == self._expected


class contain_service(ConditionalContainsMatcher):
    _no_match = 'no service state found with name {!r}'

    def _is_match(self, state):
        return state['state'] == 'service' and state['name'] == self._expected


class contain_file(ConditionalContainsMatcher):
    _no_match = 'no file state found with name {!r}'

    def _is_match(self, state):
        return state['state'] == 'file' and state['name'] == self._expected
