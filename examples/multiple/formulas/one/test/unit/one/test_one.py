from expects import expect


def test_contains_package_config_and_service(show_low_sls, contain_file, contain_service, contain_pkg):
    with show_low_sls('one', {}) as sls:
        assert isinstance(sls, list)
