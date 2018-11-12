# -*- coding: utf-8 -*-
from expects.matchers import Matcher

__all__ = []  # disable * imports


class StatefulMatcher(Matcher):
    def __init__(self, expected, parent=None):
        self._expected = expected
        self._parent = parent
        self._matched = []
        self._matcher_name = self.__class__.__name__[8:]
        self._matcher_attr = 'name'

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

    def _match(self, lowsls):
        ok, reasons = self._parent._match(lowsls)

        if not ok:
            return ok, reasons

        ok = any(m[self._parent._expected] == self._expected for m in self._parent._matched)
        if not ok:
            reasons.append(
                'value {!r} does not match property {!r} from {} with {} {!r}'.format(
                    self._expected,
                    self._parent._expected,
                    self._parent._parent._matcher_name,
                    self._parent._parent._matcher_attr,
                    self._parent._parent._expected
                )
            )
        return ok, reasons


class FileContentMatcher(StatefulMatcher):
    def _match(self, lowsls):
        ok, reasons = self._parent._match(lowsls)

        if not ok:
            return ok, reasons

        def get_content(match):
            content = match.get('__file_content')
            if content is not None and isinstance(content, dict):  # we matched a file.recurse state
                content = match['__file_content'][self._parent._expected]
            # FIXME: fall back to empty string to avoid NoneType comparisons (does this work in all circumstances?)
            return content or ''

        if hasattr(self._expected, 'pattern'):  # regex match attempt
            ok = any(self._expected.search(get_content(m)) for m in self._parent._matched)
            if not ok:
                reasons.append(
                    'pattern {!r} not found in file content'.format(self._expected.pattern)
                )
        else:
            ok = any(self._expected in get_content(m) for m in self._parent._matched)
            if not ok:
                reasons.append(
                    'text {!r} not found in file content'.format(self._expected)
                )

        return ok, reasons


class WithPropertyMatcher(StatefulMatcher):
    def _match(self, lowsls):
        ok, reasons = self._parent._match(lowsls)
        self._matched = [match for match in self._parent._matched if self._expected in match]

        if self._matched == []:
            reasons.append(
                '{!r} property not found in {} with {} {!r}'.format(
                    self._expected,
                    self._parent._matcher_name,
                    self._parent._matcher_attr,
                    self._parent._expected
                )
            )

        return self._matched != [], reasons

    def __call__(self, value):
        return PropertyValueMatcher(value, self)


class ConditionalContainsMatcher(StatefulMatcher, WithMethodsMixin):
    _no_match = NotImplemented

    def __init__(self, expected, parent=None):
        super(ConditionalContainsMatcher, self).__init__(expected, parent)
        self._parent_reference = self

    def _match(self, lowsls):
        for state in lowsls:
            if self._is_match(state):
                self._matched.append(state)

        ok, reasons = self._matched != [], []
        if not ok:
            reasons.append(self._no_match.format(self._expected))
        return ok, reasons

    def _is_match(self, state):
        return state['state'] == self._matcher_name and state['name'] == self._expected

    @property
    def _no_match(self):
        return 'no {} state found with name {{!r}}'.format(self._matcher_name)


class contain_id(ConditionalContainsMatcher):
    def __init__(self, expected, parent=None):
        super(contain_id, self).__init__(expected, parent)
        self._matcher_name = 'state'
        self._matcher_attr = 'id'

    def _is_match(self, state):
        return self._expected == state['__id__']

    @property
    def _no_match(self):
        return 'state with id {!r} not found'


class contain_file(ConditionalContainsMatcher):
    def _is_match(self, state):
        return super(contain_file, self)._is_match(state) or (
            '__file_content' in state and
            isinstance(state['__file_content'], dict) and
            self._expected in state['__file_content']
        )

    def that_has_content(self, pattern_or_string):
        return FileContentMatcher(pattern_or_string, self)


def find_matcher(mod):
    subclasses = {c.__name__: c for c in ConditionalContainsMatcher.__subclasses__()}
    matcher_name = 'contain_{}'.format(mod)
    if matcher_name in subclasses:
        return subclasses[matcher_name]

    return type(matcher_name, (ConditionalContainsMatcher,), {})
