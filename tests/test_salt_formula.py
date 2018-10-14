# -*- coding: utf-8 -*-


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
        def test_test_ping(salt_minion):
            assert salt_minion.cmd('test.ping') == True
    """)

    result = testdir.runpytest('-v')
    result.assert_outcomes(passed=1)


sls0 = """\
test_apply_should_mock_itself:
  cmd.run:
    - name: ls -l
"""


def test_salt_minion_state_apply_is_mocked(testdir):
    testdir.makepyfile("""
        import logging

        def test_state_apply(salt_minion, caplog):
            with caplog.at_level(logging.INFO, logger='salt'):
                assert type(salt_minion.cmd('state.apply', 'teststate0')) == dict
            assert 'Not called, mocked' in caplog.text
    """)

    slsfile = testdir.tmpdir.mkdir('../teststate0/').join('init.sls')
    slsfile.write(sls0)

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


def test_show_sls(testdir):
    testdir.makepyfile("""
        def test_show_sls(show_sls):
            with show_sls('teststate1', {}) as sls:
                print(sls.to_yaml())
                assert len(sls) > 0
    """)

    slsfile = testdir.tmpdir.mkdir('../teststate1/').join('init.sls')
    slsfile.write(sls1)

    result = testdir.runpytest('-v')
    result.assert_outcomes(passed=1)


def test_show_sls_contain_id(testdir):
    testdir.makepyfile("""
        from expects import expect
        from pytest_salt_formula.matchers import contain_id

        def test_show_sls(show_sls):
            with show_sls('teststate1a', {}) as sls:
                expect(sls).to(contain_id('whatever'))
    """)

    slsfile = testdir.tmpdir.mkdir('../teststate1a/').join('init.sls')
    slsfile.write(sls1)

    result = testdir.runpytest('-v')
    result.assert_outcomes(passed=1)


def test_show_sls_contain_id_with_comment(testdir):
    testdir.makepyfile("""
        from expects import expect
        from pytest_salt_formula.matchers import contain_id

        def test_show_sls(show_sls):
            with show_sls('teststate1b', {}) as sls:
                print(sls.to_yaml())
                expect(sls).to(
                    contain_id('whatever')
                    .with_comment('This is a comment again.')
                )
    """)

    slsfile = testdir.tmpdir.mkdir('../teststate1b/').join('init.sls')
    slsfile.write(sls1)

    result = testdir.runpytest('-v')
    result.assert_outcomes(passed=1)


def test_show_sls_contain_id_with_the_incorrect_comment(testdir):
    testdir.makepyfile("""
        from expects import expect
        from pytest_salt_formula.matchers import contain_id

        def test_show_sls(show_sls):
            with show_sls('teststate1c', {}) as sls:
                print(sls.to_yaml())
                expect(sls).to(
                    contain_id('whatever')
                    .with_comment('This is a test.')
                )
    """)

    slsfile = testdir.tmpdir.mkdir('../teststate1c/').join('init.sls')
    slsfile.write(sls1)

    result = testdir.runpytest('-v')
    result.assert_outcomes(failed=1)
    result.stdout.fnmatch_lines([
        "*value 'This is a test.' does not match property*",
    ])


def test_show_sls_contain_id_with_invalid_property(testdir):
    testdir.makepyfile("""
        from expects import expect
        from pytest_salt_formula.matchers import contain_id

        def test_show_sls(show_sls):
            with show_sls('teststate1d', {}) as sls:
                print(sls.to_yaml())
                expect(sls).to(
                    contain_id('whatever')
                    .with_does_not_exist('This does not exist')
                )
    """)

    slsfile = testdir.tmpdir.mkdir('../teststate1d/').join('init.sls')
    slsfile.write(sls1)

    result = testdir.runpytest('-v')
    result.assert_outcomes(failed=1)
    result.stdout.fnmatch_lines([
        "*but: 'does_not_exist' property not found in state with id 'whatever'*",
    ])


def test_show_sls_contain_id_with_comment_and_whatever(testdir):
    testdir.makepyfile("""
        from expects import expect
        from pytest_salt_formula.matchers import contain_id

        def test_show_sls(show_sls):
            with show_sls('teststate1e', {}) as sls:
                print(sls.to_yaml())
                expect(sls).to(
                    contain_id('test_a_test_configurable_test_state')
                    .with_comment('This is a test.')
                    .with_name('foo')
                )
    """)

    slsfile = testdir.tmpdir.mkdir('../teststate1e/').join('init.sls')
    slsfile.write(sls1)

    result = testdir.runpytest('-v')
    result.assert_outcomes(passed=1)


sls2 = """\
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
    - rendered: blah

test_a_managed_service:
  service.running:
    - name: shenanigan
    - enable: true
    - watch:
      - file: test_a_managed_file
"""


m0 = """\
{% if sheanaigans | default(False) %}
shenanigans
{% endif %}
"""


def test_show_sls_with_pkg_service_config(testdir):
    testdir.makepyfile("""
        from expects import expect
        from pytest_salt_formula.matchers import *

        def test_show_sls(show_sls):
            with show_sls('teststate2a', {}) as sls:
                print(sls.to_yaml())
                expect(sls).to(contain_pkg('python'))
                expect(sls).to(contain_file('/tmp/managed0.txt'))
                expect(sls).to(contain_file('/tmp/managed1.txt'))
                expect(sls).to(
                    contain_service('shenanigan')
                        .with_enable(True)
                        .with_watch([{'file': 'test_a_managed_file'}])
                )
    """)

    statedir = testdir.tmpdir.mkdir('../teststate2a/')
    slsfile = statedir.join('init.sls')
    slsfile.write(sls2)

    filesd = statedir.mkdir('files')
    filesd.join('managed.txt').write(m0)
    templatesd = statedir.mkdir('templates')
    templatesd.join('managed.txt.j2').write(m0)

    result = testdir.runpytest('-v')
    result.assert_outcomes(passed=1)


def test_show_sls_with_missing_package(testdir):
    testdir.makepyfile("""
        from expects import expect
        from pytest_salt_formula.matchers import *

        def test_show_sls(show_sls):
            with show_sls('teststate2b', {}) as sls:
                print(sls.to_yaml())
                expect(sls).to(contain_pkg('does-not-exist'))
    """)

    statedir = testdir.tmpdir.mkdir('../teststate2b/')
    slsfile = statedir.join('init.sls')
    slsfile.write(sls2)

    result = testdir.runpytest('-v')
    result.assert_outcomes(failed=1)
    result.stdout.fnmatch_lines([
        "*but: no package state found with name 'does-not-exist'*"
    ])
