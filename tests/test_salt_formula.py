# -*- coding: utf-8 -*-
import os

from textwrap import dedent


def _create_assets(testdir, config):
    if 'ini' in config:
        testdir.makeini(config['ini'])

    if 'pyfile' in config:
        testdir.makepyfile(config['pyfile'])

    if 'states' in config:
        for name, cfg in config['states'].items():
            statedir = testdir.tmpdir.mkdir('../{}'.format(name))
            slsfile = statedir.join('init.sls')
            slsfile.write(dedent(cfg['content']))

            def mkpaths(type):
                _path = statedir.mkdir(type)
                for name, content in cfg[type].items():
                    dirs, name = os.path.split(name)
                    path = _path
                    for d in dirs.split('/'):
                        path = path.ensure_dir(d)
                    path.join(name).write(dedent(content))

            if 'files' in cfg:
                mkpaths('files')

            if 'templates' in cfg:
                mkpaths('templates')


def test_file_roots_ini_setting_is_set(testdir):
    testdir.makeini("""
        [pytest]
        SALT_FILE_ROOTS = .
    """)

    testdir.makepyfile("""
        import pytest

        @pytest.fixture
        def _file_roots(request):
            return request.config.getini('SALT_FILE_ROOTS')

        def test_file_roots(_file_roots):
            assert ['{}']== _file_roots
    """.format(testdir.tmpdir.join('.')))

    result = testdir.runpytest('-v')
    result.assert_outcomes(passed=1)
    result.stdout.fnmatch_lines([
        '*::test_file_roots PASSED*',
    ])
    assert result.ret == 0


def test_file_roots_ini_setting_is_not_set(testdir):
    testdir.makeini("""
        [pytest]
    """)

    testdir.makepyfile("""
        import pytest

        @pytest.fixture
        def _file_roots(request):
            return request.config.getini('SALT_FILE_ROOTS')

        def test_file_roots(_file_roots):
            assert [] == _file_roots
    """.format(str(testdir.tmpdir.join('..'))))

    result = testdir.runpytest('-v')
    result.assert_outcomes(passed=1)
    result.stdout.fnmatch_lines([
        '*::test_file_roots PASSED*',
    ])
    assert result.ret == 0


def test_fixture_file_roots_is_a_valid_list_when_ini_setting_is_set(testdir):
    testdir.makeini("""
        [pytest]
        SALT_FILE_ROOTS = ../../salt
    """)

    testdir.makepyfile("""
        def test_file_roots_fixture(file_roots):
            assert isinstance(file_roots, list)
            assert file_roots[0] == '{}'
    """.format(testdir.tmpdir.join('../../salt')))

    result = testdir.runpytest('-v')
    result.assert_outcomes(passed=1)
    result.stdout.fnmatch_lines([
        '*::test_file_roots_fixture PASSED*',
    ])
    assert result.ret == 0


def test_fixture_file_roots_is_a_valid_list_when_ini_setting_is_not_set(testdir):
    testdir.makeini("""
        [pytest]
    """)

    testdir.makepyfile("""
        def test_file_roots_fixture(file_roots):
            assert isinstance(file_roots, list)
            assert file_roots[0] == '{}'
    """.format(testdir.tmpdir.join('../')))

    result = testdir.runpytest('-v')
    result.assert_outcomes(passed=1)
    result.stdout.fnmatch_lines([
        '*::test_file_roots_fixture PASSED*',
    ])
    assert result.ret == 0


def test_minion_opts_when_module_dirs_is_set(testdir):
    testdir.makeini("""
        [pytest]
        SALT_MODULE_DIRS = /tmp/_modules
    """)

    testdir.makepyfile("""
        def test_minion_config(minion_opts):
            assert minion_opts['root_dir'].startswith('{}')
            assert minion_opts.has_key('module_dirs')
            assert minion_opts['module_dirs'] == ['/tmp/_modules']
    """.format(testdir.tmpdir.join('../')))

    result = testdir.runpytest('-v')
    result.assert_outcomes(passed=1)
    assert result.ret == 0


def test_minion_opts_when_module_dirs_is_unset(testdir):
    testdir.makeini("""
        [pytest]
    """)

    testdir.makepyfile("""
        def test_minion_config(minion_opts):
            assert minion_opts['root_dir'].startswith('{}')
            assert minion_opts['module_dirs'] == []
    """.format(testdir.tmpdir.join('../')))

    result = testdir.runpytest('-v')
    result.assert_outcomes(passed=1)
    assert result.ret == 0


def test_salt_minion_test_ping(testdir):
    testdir.makepyfile("""
        def test_test_ping(minion):
            assert minion.cmd('test.ping') == True
    """)

    result = testdir.runpytest('-v')
    result.assert_outcomes(passed=1)


def test_salt_minion_state_apply_is_mocked(testdir):
    _create_assets(testdir, {
        'pyfile': """
            import logging

            def test_state_apply(minion, caplog):
                with caplog.at_level(logging.INFO, logger='salt'):
                    assert type(minion.cmd('state.apply', 'teststate0')) == dict
                assert 'Not called, mocked' in caplog.text
        """,
        'states': {
            'teststate0': {
                'content': """
                    test_apply_should_mock_itself:
                      cmd.run:
                        - name: ls -l
                """
            }
        }
    })

    result = testdir.runpytest('-vv')
    result.assert_outcomes(passed=1)
    result.stdout.fnmatch_lines([
        '*::test_state_apply PASSED*',
    ])


sls1 = """\
test_a_test_configurable_test_state:
  test.configurable_test_state:
    - name: foo
    - changes: True
    - result: True
    - comment: This is a test.


whatever:
  test.configurable_test_state:
    - changes: False
    - result: False
    - comment: This is a comment again.
"""


def test_show_low_sls(testdir):
    _create_assets(testdir, {
        'pyfile': """
            def test_show_low_sls(show_low_sls):
                with show_low_sls('teststate1a', {}) as sls:
                    assert len(sls) > 0
        """,
        'states': {
            'teststate1a': {
                'content': """
                    at_least_one:
                      test.configurable_test_state:
                        - name: foo
                        - changes: True
                        - result: True
                        - comment: This is a test.
                """
            }
        }
    })

    result = testdir.runpytest('-v')
    result.assert_outcomes(passed=1)


def test_show_low_sls_contain_id(testdir):
    _create_assets(testdir, {
        'pyfile': """
            from expects import expect
            from pytest_salt_formula.matchers import contain_id

            def test_show_low_sls(show_low_sls):
                with show_low_sls('teststate1b', {}) as sls:
                    expect(sls).to(contain_id('whatever'))
        """,
        'states': {
            'teststate1b': {
                'content': """
                    whatever:
                      test.configurable_test_state:
                        - changes: False
                        - result: False
                        - comment: This is a comment again.
                """
            }
        }
    })

    result = testdir.runpytest('-v')
    result.assert_outcomes(passed=1)


def test_show_low_sls_contain_id_with_comment(testdir):
    _create_assets(testdir, {
        'pyfile': """
            from expects import expect
            from pytest_salt_formula.matchers import contain_id

            def test_show_low_sls(show_low_sls):
                with show_low_sls('teststate1c', {}) as sls:
                    expect(sls).to(
                        contain_id('whatever')
                        .with_comment('This is a comment again.')
                    )
        """,
        'states': {
            'teststate1c': {
                'content': """
                    whatever:
                      test.configurable_test_state:
                        - changes: False
                        - result: False
                        - comment: This is a comment again.
                """
            }
        }
    })

    result = testdir.runpytest('-v')
    result.assert_outcomes(passed=1)


def test_show_low_sls_contain_id_with_the_incorrect_comment(testdir):
    _create_assets(testdir, {
        'pyfile': """
            from expects import expect
            from pytest_salt_formula.matchers import contain_id

            def test_show_low_sls(show_low_sls):
                with show_low_sls('teststate1d', {}) as sls:
                    expect(sls).to(
                        contain_id('whatever')
                        .with_comment('This is a test.')
                    )
        """,
        'states': {
            'teststate1d': {
                'content': """
                    whatever:
                      test.configurable_test_state:
                        - changes: False
                        - result: False
                        - comment: This is a comment again.
                """
            }
        }
    })

    result = testdir.runpytest('-v')
    result.assert_outcomes(failed=1)
    result.stdout.fnmatch_lines([
        "*value 'This is a test.' does not match property*",
    ])


def test_show_low_sls_contain_id_with_invalid_property(testdir):
    _create_assets(testdir, {
        'pyfile': """
            from expects import expect
            from pytest_salt_formula.matchers import contain_id

            def test_show_low_sls(show_low_sls):
                with show_low_sls('teststate1e', {}) as sls:
                    expect(sls).to(
                        contain_id('whatever')
                        .with_does_not_exist('This does not exist')
                    )
        """,
        'states': {'teststate1e': {'content': sls1}}
    })

    result = testdir.runpytest('-v')
    result.assert_outcomes(failed=1)
    result.stdout.fnmatch_lines([
        "*but: 'does_not_exist' property not found in state with id 'whatever'*",
    ])


def test_show_low_sls_contain_id_with_comment_and_whatever(testdir):
    _create_assets(testdir, {
        'pyfile': """
            from expects import expect
            from pytest_salt_formula.matchers import contain_id

            def test_show_low_sls(show_low_sls):
                with show_low_sls('teststate1f', {}) as sls:
                    expect(sls).to(
                        contain_id('test_a_test_configurable_test_state')
                        .with_comment('This is a test.')
                        .with_name('foo')
                    )
        """,
        'states': {'teststate1f': {'content': sls1}}
    })

    result = testdir.runpytest('-v')
    result.assert_outcomes(passed=1)


def test_show_low_sls_with_pkg_service_config(testdir):
    _create_assets(testdir, {
        'pyfile': """
            from expects import expect

            def test_show_low_sls(show_low_sls, contain_service, contain_pkg, contain_file):
               with show_low_sls('teststate2', {}) as sls:
                    expect(sls).to(contain_pkg('python'))
                    expect(sls).to(contain_file('/tmp/managed0.txt'))
                    expect(sls).to(contain_file('/tmp/managed1.txt'))
                    expect(sls).to(
                        contain_service('shenanigan')
                            .with_enable(True)
                            .with_watch([{'file': 'test_a_managed_file'}])
                    )
        """,
        'states': {
            'teststate2': {
                'content': """
                    test_a_managed_package:
                      pkg.installed:
                        - name: python
                        - version: latest

                    test_a_managed_file:
                      file.managed:
                        - name: /tmp/managed0.txt
                        - source: salt://{{ slspath }}/files/managed.txt
                        - user: nobody
                        - group: nobody
                        - mode: '0644'

                    test_a_managed_template:
                      file.managed:
                        - name: /tmp/managed1.txt
                        - source: salt://{{ slspath }}/templates/managed.txt.j2
                        - user: nobody
                        - group: nobody
                        - mode: '0644'
                        - template: jinja
                        - context:
                            shenanigans: true

                    test_a_managed_service:
                      service.running:
                        - name: shenanigan
                        - enable: true
                        - watch:
                          - file: test_a_managed_file
                """,
                'files': {
                    'managed.txt': """
                        {% if shenanigans | default(False) %}
                        shenanigans
                        {% endif %}
                    """
                },
                'templates': {
                    'managed.txt.j2': """
                        {% if shenanigans | default(False) %}
                        shenanigans
                        {% endif %}
                    """
                },
            }
        }
    })

    result = testdir.runpytest('-v')
    result.assert_outcomes(passed=1)


def test_show_low_sls_with_missing_package_should_fail(testdir):
    _create_assets(testdir, {
        'pyfile': """
            from expects import expect

            def test_show_low_sls(show_low_sls, contain_pkg):
                with show_low_sls('teststate3a', {}) as sls:
                    expect(sls).to(contain_pkg('does-not-exist'))
        """,
        'states': {
            'teststate3a': {
                'content': """
                    test_a_managed_package:
                      pkg.installed:
                        - name: python
                        - version: latest
                """
            }
        }
    })

    result = testdir.runpytest('-v')
    result.assert_outcomes(failed=1)
    result.stdout.fnmatch_lines([
        "*but: no pkg state found with name 'does-not-exist'*"
    ])


def test_show_low_sls_with_missing_package_when_using_to_not_should_pass(testdir):
    _create_assets(testdir, {
        'pyfile': """
            from expects import expect

            def test_show_low_sls(show_low_sls, contain_pkg):
                with show_low_sls('teststate3b', {}) as sls:
                    expect(sls).to_not(contain_pkg('does-not-exist'))
        """,
        'states': {
            'teststate3b': {
                'content': """
                    test_a_managed_package:
                      pkg.installed:
                        - name: python
                        - version: latest
                """
            }
        }
    })

    result = testdir.runpytest('-v')
    result.assert_outcomes(passed=1)


def test_show_low_sls_with_existing_package_when_using_to_not_should_fail(testdir):
    _create_assets(testdir, {
        'pyfile': """
            from expects import expect

            def test_show_low_sls(show_low_sls, contain_pkg):
                with show_low_sls('teststate3c', {}) as sls:
                    expect(sls).to_not(contain_pkg('python'))
        """,
        'states': {
            'teststate3c': {
                'content': """
                    test_a_managed_package:
                      pkg.installed:
                        - name: python
                        - version: latest
                """
            }
        }
    })

    result = testdir.runpytest('-v')
    result.assert_outcomes(failed=1)
    result.stdout.fnmatch_lines([
        "*not to contain pkg 'python'*"
    ])


def test_show_low_sls_with_static_file_that_has_content(testdir):
    _create_assets(testdir, {
        'pyfile': """
            from expects import expect

            def test_show_low_sls(show_low_sls, contain_file):
                with show_low_sls('teststate4a', {}) as sls:
                    expect(sls).to(
                        contain_file('/tmp/managed.txt')
                            .that_has_content('shenanigans')
                    )
        """,
        'states': {
            'teststate4a': {
                'content': """
                    a_test_file_with_content:
                      file.managed:
                        - name: /tmp/managed.txt
                        - source: salt://{{ slspath }}/files/managed.txt
                        - user: nobody
                        - group: nobody
                        - mode: '0644'
                """,
                'files': {
                    'managed.txt': '\nshenanigans\n',
                },
            }
        }
    })

    result = testdir.runpytest('-v')
    result.assert_outcomes(passed=1)


def test_show_low_sls_with_static_file_that_matches_regex(testdir):
    _create_assets(testdir, {
        'pyfile': """
            import re
            from expects import expect

            def test_show_low_sls(show_low_sls, contain_file):
                pattern = re.compile(r'shen[an]{2}igans')
                with show_low_sls('teststate4b', {}) as sls:
                    expect(sls).to(
                        contain_file('/tmp/managed.txt')
                            .that_has_content(pattern)
                    )
        """,
        'states': {
            'teststate4b': {
                'content': """
                    a_test_file_with_content:
                      file.managed:
                        - name: /tmp/managed.txt
                        - source: salt://{{ slspath }}/files/managed.txt
                        - user: nobody
                        - group: nobody
                        - mode: '0644'
                """,
                'files': {
                    'managed.txt': '\nshenanigans\n',
                },
            }
        }
    })

    result = testdir.runpytest('-v')
    result.assert_outcomes(passed=1)


def test_show_low_sls_with_template_that_has_content(testdir):
    _create_assets(testdir, {
        'pyfile': """
            from expects import expect

            def test_show_low_sls(show_low_sls, contain_file):
                with show_low_sls('teststate5', {}) as sls:
                    expect(sls).to(
                        contain_file('/tmp/managed.txt')
                            .that_has_content('\\nshenanigans\\n')
                    )
        """,
        'states': {
            'teststate5': {
                'content': """
                    a_test_file_with_content:
                      file.managed:
                        - name: /tmp/managed.txt
                        - source: salt://{{ slspath }}/templates/managed.txt.j2
                        - user: nobody
                        - group: nobody
                        - mode: '0644'
                        - template: jinja
                        - context:
                            shenanigans: true
                """,
                'templates': {
                    'managed.txt.j2': '{% if shenanigans %}\nshenanigans\n{% endif %}',
                },
            }
        }
    })

    result = testdir.runpytest('-v')
    result.assert_outcomes(passed=1)


def test_show_low_sls_with_append_and_multiple_sources(testdir):
    _create_assets(testdir, {
        'pyfile': """
            from expects import expect

            def test_show_low_sls(show_low_sls, contain_file):
                with show_low_sls('teststate6', {}) as sls:
                    expect(sls).to(
                        contain_file('/tmp/managed.txt')
                            .that_has_content('append1\\nappend2\\n')
                    )
        """,
        'states': {
            'teststate6': {
                'content': """
                    a_test_file_with_content:
                      file.append:
                        - name: /tmp/managed.txt
                        - sources:
                          - salt://{{ slspath }}/files/append1.txt
                          - salt://{{ slspath }}/files/append2.txt
                        - user: nobody
                        - group: nobody
                        - mode: '0644'
                """,
                'files': {
                    'append1.txt': 'append1\n',
                    'append2.txt': 'append2\n',
                },
            }
        }
    })

    result = testdir.runpytest('-v')
    result.assert_outcomes(passed=1)


def test_show_low_sls_with_rename(testdir):
    _create_assets(testdir, {
        'pyfile': """
            from expects import expect

            def test_show_low_sls(show_low_sls, contain_file):
                with show_low_sls('teststate7', {}) as sls:
                    expect(sls).to(
                        contain_file('/tmp/renamed_to.txt').with_source('/tmp/renamed_from.txt')
                    )
        """,
        'states': {
            'teststate7': {
                'content': """
                    a_test_file_rename:
                      file.rename:
                        - name: /tmp/renamed_to.txt
                        - source: /tmp/renamed_from.txt
                """,
            }
        }
    })

    result = testdir.runpytest('-v')
    result.assert_outcomes(passed=1)


def test_show_low_sls_file_managed_with_multiple_source_files_first_exists(testdir):
    _create_assets(testdir, {
        'pyfile': """
            from expects import expect

            def test_show_low_sls(show_low_sls, contain_file):
                with show_low_sls('teststate8a', {}) as sls:
                    expect(sls).to(
                        contain_file('/tmp/managed.txt')
                            .that_has_content('managed-exists.txt')
                    )
        """,
        'states': {
            'teststate8a': {
                'content': """
                    a_test_file_with_multiple_sources_first_exists:
                      file.managed:
                        - name: /tmp/managed.txt
                        - source:
                          - salt://{{ slspath }}/files/managed-exists.txt
                          - salt://{{ slspath }}/files/managed-does-not.txt
                """,
                'files': {'managed-exists.txt': 'managed-exists.txt\n'}
            }
        }
    })

    result = testdir.runpytest('-v')
    result.assert_outcomes(passed=1)


def test_show_low_sls_file_managed_with_multiple_source_files_second_exists(testdir):
    _create_assets(testdir, {
        'pyfile': """
            from expects import expect

            def test_show_low_sls(show_low_sls, contain_file):
                with show_low_sls('teststate8b', {}) as sls:
                    expect(sls).to(
                        contain_file('/tmp/managed.txt')
                            .that_has_content('managed-exists.txt')
                    )
        """,
        'states': {
            'teststate8b': {
                'content': """
                    a_test_file_with_multiple_sources_first_exists:
                      file.managed:
                        - name: /tmp/managed.txt
                        - source:
                          - salt://{{ slspath }}/files/managed-does-not.txt
                          - salt://{{ slspath }}/files/managed-exists.txt
                """,
                'files': {'managed-exists.txt': 'managed-exists.txt\n'}
            }
        }
    })

    result = testdir.runpytest('-v')
    result.assert_outcomes(passed=1)


def test_show_low_sls_file_recurse(testdir):
    _create_assets(testdir, {
        'pyfile': """
            from expects import expect

            def test_show_low_sls(show_low_sls, contain_file):
                with show_low_sls('teststate9', {}) as sls:
                    expect(sls).to(
                        contain_file('/tmp/managed_dir/managed1.txt')
                            .that_has_content('managed1.txt')
                    )
        """,
        'states': {
            'teststate9': {
                'content': """
                    a_test_file_recurse:
                      file.recurse:
                        - name: /tmp/managed_dir
                        - source: salt://{{ slspath }}/files/managed_dir
                """,
                'files': {
                    'managed_dir/managed1.txt': 'managed1.txt\n',
                    'managed_dir/managed2.txt': 'manage2.txt\n',
                }
            }
        }
    })

    result = testdir.runpytest('-v')
    result.assert_outcomes(passed=1)


def test_show_low_sls_source_and_sources_raises(testdir):
    _create_assets(testdir, {
        'pyfile': """
            from expects import expect

            def test_show_low_sls(show_low_sls, contain_file):
                with show_low_sls('teststate10', {}) as sls:
                    expect(sls).to(
                        contain_file('/tmp/managed.txt')
                            .that_has_content('managed.txt')
                    )
        """,
        'states': {
            'teststate10': {
                'content': """
                    a_test_file_recurse:
                      file.append:
                        - name: /tmp/managed.txt
                        - source: salt://{{ slspath }}/files/managed.txt
                        - sources:
                            - salt://{{ slspath }}/files/managed1.txt
                            - salt://{{ slspath }}/files/managed2.txt
                """,
                'files': {
                    'managed.txt': 'managed.txt\n',
                    'managed1.txt': 'managed1.txt\n',
                    'managed2.txt': 'manage2.txt\n',
                }
            }
        }
    })

    result = testdir.runpytest('-vv')
    result.assert_outcomes(failed=1, passed=0)
