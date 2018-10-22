def test_package_htop(host):
    assert host.package('htop').is_installed


# def test_single_package(host):
#     assert host.package('single').is_installed

# def test_single_config(host):
#     assert host.file('/etc/single/single.conf').exists

# def test_single_service(host):
#     service = host.service('single')
#     assert service.is_running
#     assert service.is_enabled
