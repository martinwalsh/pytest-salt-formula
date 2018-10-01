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


def test_salt_minion_state_apply_is_disabled(testdir):
    testdir.makepyfile("""
        def test_show_sls(salt_minion):
            assert type(salt_minion.cmd('state.apply', 'teststate0')) == dict
    """)

    slsfile = testdir.tmpdir.mkdir('../teststate0/').join('init.sls')
    slsfile.write(sls0)

    result = testdir.runpytest('-v')
    result.assert_outcomes(passed=1)


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


# def test_show_sls(testdir):
#     testdir.makepyfile("""
#         def test_show_sls(show_sls):
#             with show_sls('teststate1', {}) as sls:
#                 from salt.utils.yaml import safe_dump
#                 print(safe_dump(sls, default_flow_style=False))
#                 assert sls == ''
#     """)
#
#     slsfile = testdir.tmpdir.mkdir('../teststate1/').join('init.sls')
#     slsfile.write(sls1)
#
#     result = testdir.runpytest('-v')
#     result.assert_outcomes(passed=1)
