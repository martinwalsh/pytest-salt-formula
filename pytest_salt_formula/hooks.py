# -*- coding: utf-8 -*-
import logging


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
                  default=['state.show_sls', 'test.ping', 'cp.get_file_str'],
                  help='list of salt functions that should not be mocked')


def pytest_configure(config):
    logging.getLogger('salt').setLevel(
        getattr(logging, config.getini('SALT_LOG_LEVEL'))
    )
