# -*- coding: utf-8 -*-
from expects.matchers import Matcher

__all__ = []  # disable * imports


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
            return WithPropertyMatcher(attr[5:], self._parent_reference)
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


class FileContentMatcher(StatefulMatcher):
    def _match(self, lowstate):
        ok, reasons = self._parent._match(lowstate)

        if not ok:
            return ok, reasons

        if hasattr(self._expected, 'pattern'):  # regex match attempt
            ok = self._expected.search(self._parent._matched['__file_content']) is not None
            if not ok:
                reasons.append(
                    'pattern {!r} not found in file content'.format(self._expected.pattern)
                )
        else:
            ok = self._expected in self._parent._matched['__file_content']
            if not ok:
                reasons.append(
                    'text {!r} not found in file content'.format(self._expected)
                )

        return ok, reasons


class WithPropertyMatcher(StatefulMatcher):
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

    def _match(self, lowstate):
        for state in lowstate:
            if self._is_match(state):
                self._matched = state
                break

        ok, reasons = self._matched is not None, []
        if not ok:
            reasons.append(self._no_match.format(self._expected))
        return ok, reasons

    def _is_match(self, state):
        return state['state'] == self.__class__.__name__[8:] and state['name'] == self._expected

    @property
    def _no_match(self):
        return 'no {} state found with name {{!r}}'.format(self.__class__.__name__[8:])


class contain_id(ConditionalContainsMatcher):
    def _is_match(self, state):
        return self._expected == state['__id__']

    @property
    def _no_match(self):
        return 'state with id {{!r}} not found'


class contain_file(ConditionalContainsMatcher):
    def that_has_content(self, pattern_or_string):
        return FileContentMatcher(pattern_or_string, self)


def find_matcher(mod):
    subclasses = {c.__name__: c for c in ConditionalContainsMatcher.__subclasses__()}
    matcher_name = 'contain_{}'.format(mod)
    if matcher_name in subclasses:
        return subclasses[matcher_name]

    return type(matcher_name, (ConditionalContainsMatcher,), {})
