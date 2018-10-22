from expects import expect


def test_contains_single_config(show_low_sls, contain_file, contain_service, contain_pkg):
    with show_low_sls('single', {}) as sls:
        expect(sls).to(
            contain_file('/etc/single/single.conf')
            .that_has_content('/etc/single/single.conf')
        )
