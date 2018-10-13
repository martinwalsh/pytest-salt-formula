# -*- coding: utf-8 -*-
import pytest
import salt.utils
import salt.config
import salt.client

from utils import abspath, touch
from contextlib import contextmanager


@pytest.fixture(scope='session')
def file_roots(request):
    file_roots = request.config.getini('SALT_FILE_ROOTS')
    if not file_roots:
        file_roots = [abspath(str(request.config.rootdir), '../')]
    return [str(p) for p in file_roots]


@pytest.fixture(scope='session')
def minion_opts(request, tmpdir_factory, file_roots):
    tmpdir = tmpdir_factory.mktemp('root')
    cachedir = tmpdir.mkdir('var').mkdir('cache')
    config = touch('/etc/salt/minion', tmpdir)
    __opts__ = salt.config.minion_config(str(config))
    __opts__.update({
        'root_dir': str(tmpdir),
        'file_client': 'local',
        'file_roots': {'base': file_roots},
        'cachedir':  str(cachedir),
        'id': 'test-minion',
    })
    if request.config.getini('SALT_MODULE_DIRS'):
        __opts__['module_dirs'] = request.config.getini('SALT_MODULE_DIRS')
    return __opts__


@pytest.fixture(scope='session')
def salt_minion(request, minion_opts):
    caller = salt.client.Caller(mopts=minion_opts)
    _cmd = caller.cmd

    def cmd(function, *args, **kwds):
        if function not in request.config.getini('SALT_FUNCTION_WHITELIST'):
            if 'test' in kwds:
                kwds['test'] = True
            else:
                kwds['mock'] = True
        return _cmd(function, *args, **kwds)

    caller.cmd = cmd
    return caller


class LowSLS(list):
    def __init__(self, sls):
        self._sls = sls
        list.__init__(self, sls)

    def to_yaml(self):
        return salt.utils.yaml.safe_dump(self._sls, default_flow_style=False)


@pytest.fixture(scope='function')
def show_sls(salt_minion):
    @contextmanager
    def _show_sls(name, grains, pillar=None):
        # if pillar is None:
        #     pillar = {}

        for key, value in grains.items():
            salt_minion.cmd('grains.setval', key, value)

        try:
            yield LowSLS(salt_minion.cmd('state.show_low_sls', name, pillar=pillar))
        finally:
            for key in grains.keys():
                salt_minion.cmd('grains.delkey', key)
    return _show_sls
