# -*- coding: utf-8 -*-
import pytest
import logging

from matchers import find_matcher


def pytest_addoption(parser):
    parser.addini('SALT_FILE_ROOTS',
                  type='pathlist',
                  default=None,
                  help='where to find salt states relative to the pytest rootdir')
    parser.addini('SALT_MODULE_DIRS',
                  type='pathlist',
                  default=None,
                  help='where to find custom salt modules relative to the pytest rootdir')
    parser.addini('SALT_LOG_LEVEL',
                  default='ERROR',
                  help='the log level for salt logs (default: error)')
    parser.addini('SALT_FUNCTION_WHITELIST',
                  type='linelist',
                  default=['state.show_low_sls',
                           'test.ping',
                           'cp.get_file_str',
                           'cp.list_master'],
                  help='list of salt functions that should not be mocked')


def pytest_configure(config):
    logging.getLogger('salt').setLevel(
        getattr(logging, config.getini('SALT_LOG_LEVEL'))
    )


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_setup(item):
    for name in item.fixturenames:
        if name.startswith('contain_') and name not in item.funcargs:
            item.funcargs[name] = find_matcher(name[8:])
    yield
