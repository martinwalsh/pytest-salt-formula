from expects import expect

from collections import OrderedDict


def test_contains_package_config_and_service(show_sls, contain_file, contain_service, contain_pkg):
    with show_sls('{{ cookiecutter.formula_name }}', {}) as sls:
        print(sls.to_yaml())
        assert isinstance(sls, (dict, OrderedDict))

