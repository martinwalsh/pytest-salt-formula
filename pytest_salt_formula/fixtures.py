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
    cachedir.join('.touch').write('')
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
def minion(request, minion_opts):
    caller = salt.client.Caller(mopts=minion_opts)
    _cmd = caller.cmd

    def cmd(function, *args, **kwds):
        if function not in request.config.getini('SALT_FUNCTION_WHITELIST'):
            kwds['test'] = True
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


def attach_file_content(sls, pillar, minion):
    for state in sls:
        if state['state'] == 'file':
            template = state.get('template', None)
            source = state.get('source', None)
            if source is not None:
                if template is None:
                    state['__file_content'] = minion.cmd('cp.get_file_str', path=source)
                else:
                    cached = minion.cmd(
                        'cp.get_template',
                        path=source,
                        dest='',  # this will cause the rendered file to be downloaded to the cache
                        template=template,
                        context=state.get('context', None),
                        pillar=pillar,
                    )
                    with open(cached) as f:
                        state['__file_content'] = f.read()
    return sls


@pytest.fixture(scope='function')
def show_low_sls(minion):
    @contextmanager
    def _show_low_sls(name, grains, pillar=None):
        for key, value in grains.items():
            minion.cmd('grains.setval', key, value)

        try:
            yield attach_file_content(
                LowSLS(minion.cmd('state.show_low_sls', name, pillar=pillar)),
                pillar, minion
            )
        finally:
            for key in grains.keys():
                minion.cmd('grains.delkey', key)
    return _show_low_sls
