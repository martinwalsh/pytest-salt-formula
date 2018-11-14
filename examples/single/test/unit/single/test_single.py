import re
from expects import expect


def test_contains_install_dependencies(show_low_sls, contain_pkg):
    with show_low_sls('single', {}) as sls:
        expect(sls).to(contain_pkg('unzip'))
        expect(sls).to(contain_pkg('curl'))


def test_contains_single_install_package(show_low_sls, contain_pkg):
    with show_low_sls('single', {}) as sls:
        expect(sls).to(contain_pkg('htop').with_version('latest'))


def test_contains_main_config(show_low_sls, contain_file):
    with show_low_sls('single', {}) as sls:
        expect(sls).to(
            contain_file('/etc/single/single.conf')
            .that_has_content('/etc/single/single.conf')
        )


def test_contains_config_d(show_low_sls, contain_file):
    with show_low_sls('single', {}) as sls:
        expect(sls).to(
            contain_file('/etc/single/conf.d').with_clean(True)
        )


def test_contains_confd_entry(show_low_sls, contain_file):
    with show_low_sls('single', {}) as sls:
        expect(sls).to(
            contain_file('/etc/single/conf.d/entry.conf')
            .that_has_content('somevalue')
        )


def test_contains_renamed_file(show_low_sls, contain_file):
    with show_low_sls('single', {}) as sls:
        expect(sls).to(
            contain_file('/etc/single/renamed.txt')
            .with_source('/etc/single/rename-me.txt')
        )


def test_contains_appended_file(show_low_sls, contain_file):
    with show_low_sls('single', {}) as sls:
        expect(sls).to(
            contain_file('/etc/single/single.conf')
            .with_text('Text to append\n')
        )


def test_contains_appended_file_with_source(show_low_sls, contain_file):
    with show_low_sls('single', {}) as sls:
        expect(sls).to(
            contain_file('/etc/single/single.conf')
            .that_has_content('append-single.txt')
        )


def test_contains_appended_file_with_multiple_sources(show_low_sls, contain_file):
    with show_low_sls('single', {}) as sls:
        expect(sls).to(
            contain_file('/etc/single/single.conf')
            .that_has_content('append-one.txt\nappend-two.txt\n')
        )


def test_contains_recurse_dir(show_low_sls, contain_file):
    with show_low_sls('single', {}) as sls:
        expect(sls).to(
            contain_file('/etc/single-recurse')
            .with_source('salt://single/files/single-recurse')
        )


def test_contains_file_from_multiple_sources_first_exists(show_low_sls, contain_id, contain_file):
    with show_low_sls('single', {}) as sls:
        expect(sls).to(
            contain_id('single_file_managed_with_multiple_sources_first')
            .with_source([
                'salt://single/files/this-one-exists.txt',
                'salt://single/files/this-one-does-not-exist.txt',
            ])
        )
        expect(sls).to(
            contain_file('/etc/single/multisource-pickone.txt')
            .that_has_content('this-one-exists.txt')
        )


def test_contains_file_from_multiple_sources_second_exists(show_low_sls, contain_file):
    with show_low_sls('single', {}) as sls:
        pattern = re.compile(r'^# files\/this-one-exists\.txt$')
        expect(sls).to(
            contain_file('/etc/single/multisource-picktwo.txt')
            .that_has_content(pattern)
        )
