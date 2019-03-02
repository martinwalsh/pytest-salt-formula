def test_nothing(host):
    assert True

# def test_one_package(host):
#     assert host.package('one').is_installed
#
# def test_one_config(host):
#     assert host.file('/etc/one/one.conf').exists
#
# def test_one_service(host):
#     service = host.service('one')
#     assert service.is_running
#     assert service.is_enabled
