# -*- coding: utf-8 -*-
from expects import have_properties
from expects.matchers import Matcher

__all__ = ['contain_state']


class _SaltState(object):
    def __init__(self, name, definition):
        self.name = name
        self.definition = definition


class contain_state(Matcher):
    def __init__(self, slsdata):
        self._expected = [_SaltState(name, _def) for name, _def in slsdata.items()]

    def __getattr__(self, attr):
        if attr.startswith('with_'):
            pass

    def _with(self, *args, **kwds):
        return have_properties(*args, **kwds)
