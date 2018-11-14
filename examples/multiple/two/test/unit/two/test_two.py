from expects import expect


def test_contains_package(show_low_sls, contain_pkg):
    with show_low_sls('two', {}) as sls:
        expect(sls).to(
            contain_pkg('htop')
        )
        expect(sls).to(
            contain_pkg('vim-minimal')
            .with_require([{'sls': 'one'}])
        )
