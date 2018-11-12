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
