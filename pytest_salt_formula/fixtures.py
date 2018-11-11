# -*- coding: utf-8 -*-
import os
import pytest
import salt.utils
import salt.config
import salt.client

from utils import abspath, touch
from contextlib import contextmanager
from salt.exceptions import SaltException


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


def get_file_content(source, state, minion, pillar):
    if state.get('template') is None:
        cached = minion.cmd('cp.get_file_str', path=source)
        if cached is not False:
            return cached
    else:
        cached = minion.cmd(
            'cp.get_template',
            path=source,
            dest='',  # an empty string forces download and cache of the rendered template
            template=state['template'],
            context=state.get('context'),
            pillar=pillar,
        )
        if cached is not False:
            with open(cached) as f:
                return f.read()
    raise SaltException('Unable to locate source for {!r}'.format(source))


def attach_file_content(sls, minion, pillar):
    for state in sls:
        if state['state'] == 'file':
            if state['fun'] == 'rename':  # the `source` of `file.rename` is not a local file
                continue

            if 'source' in state and 'sources' in state:
                raise SaltException(
                    '`source` and `sources` are mutually exclusive in state with id `{}`.'.format(state['__id__'])
                )

            if 'sources' in state:
                content = []
                for source in state['sources']:
                    content.append(get_file_content(source, state, minion, pillar))
                state['__file_content'] = ''.join(content)

            if 'source' in state:
                if state['fun'] == 'recurse':
                    files = {}
                    prefix = state['source'][7:]  # remove the salt:// portion of the source url
                    for path in minion.cmd('cp.list_master', prefix=prefix):
                        destination = os.path.join(state['name'], path[len(prefix)+1:])
                        files[destination] = get_file_content(
                            'salt://{}'.format(path), state, minion, pillar
                        )
                    state['__file_content'] = files
                    print(files)
                else:
                    if not isinstance(state['source'], list):
                        state['source'] = [state['source']]
                    for source in state['source']:
                        try:
                            state['__file_content'] = get_file_content(source, state, minion, pillar)
                            break
                        except SaltException:
                            pass
                    else:
                        raise SaltException('Unable to locate source for {!r}'.format(state['source']))
    return sls


@pytest.fixture(scope='function')
def show_low_sls(request, minion):
    @contextmanager
    def _show_low_sls(name, grains, pillar=None):
        for key, value in grains.items():
            minion.cmd('grains.setval', key, value)

        try:
            sls = LowSLS(minion.cmd('state.show_low_sls', name, pillar=pillar))
            if request.config.getoption('verbose') >= 2:
                print('$ salt-call --local state.show_low_sls {} --out yaml'.format(name))
                print(sls.to_yaml())
            yield attach_file_content(sls, minion, pillar)
        finally:
            for key in grains.keys():
                minion.cmd('grains.delkey', key)
    return _show_low_sls
