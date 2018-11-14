def test_nothing(host):
    assert True

# def test_two_package(host):
#     assert host.package('two').is_installed
#
# def test_two_config(host):
#     assert host.file('/etc/two/two.conf').exists
#
# def test_two_service(host):
#     service = host.service('two')
#     assert service.is_running
#     assert service.is_enabled
