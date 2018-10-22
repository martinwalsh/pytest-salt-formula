def test_{{ cookiecutter.formula_name }}_package(host):
    assert host.package('{{ cookiecutter.formula_name }}').is_installed

def test_{{ cookiecutter.formula_name }}_config(host):
    assert host.file('/etc/{{ cookiecutter.formula_name }}/{{ cookiecutter.formula_name }}.conf').exists

def test_{{ cookiecutter.formula_name }}_service(host):
    service = host.service('{{ cookiecutter.formula_name }}')
    assert service.is_running
    assert service.is_enabled
