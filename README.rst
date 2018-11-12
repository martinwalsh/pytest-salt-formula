===================
pytest-salt-formula
===================

.. image:: https://img.shields.io/pypi/v/pytest-salt-formula.svg
    :target: https://pypi.org/project/pytest-salt-formula
    :alt: PyPI version

.. image:: https://img.shields.io/pypi/pyversions/pytest-salt-formula.svg
    :target: https://pypi.org/project/pytest-salt-formula
    :alt: Python versions

.. image:: https://travis-ci.org/martinwalsh/pytest-salt-formula.svg?branch=master
    :target: https://travis-ci.org/martinwalsh/pytest-salt-formula
    :alt: See Build Status on Travis CI

A pytest plugin for testing salt formulae.

----

This `pytest`_ plugin was generated with `Cookiecutter`_ along with `@hackebrot`_'s `cookiecutter-pytest-plugin`_ template.


Features
--------

* TODO


Requirements
------------

* TODO


Installation
------------

You can install "pytest-salt-formula" via `pip`_ from `PyPI`_::

    $ pip install pytest-salt-formula


Usage
-----

* TODO

Contributing
------------
Contributions are very welcome. Tests can be run with `tox`_, please ensure
the coverage at least stays the same before you submit a pull request.

Todo
----

Implement order checking, something like the following:

```
def test_install_package(show_low_sls, contain_pkg, contain_file):
    with show_low_sls('statename', {}) as sls:
       expect(sls).to(
           contain_pkg('package-name').before(
               contain_file('/etc/service-name/service-name.conf')
           )
       )
```

License
-------

Distributed under the terms of the `MIT`_ license, "pytest-salt-formula" is free and open source software


Issues
------

If you encounter any problems, please `file an issue`_ along with a detailed description.

.. _`Cookiecutter`: https://github.com/audreyr/cookiecutter
.. _`@hackebrot`: https://github.com/hackebrot
.. _`MIT`: http://opensource.org/licenses/MIT
.. _`BSD-3`: http://opensource.org/licenses/BSD-3-Clause
.. _`GNU GPL v3.0`: http://www.gnu.org/licenses/gpl-3.0.txt
.. _`Apache Software License 2.0`: http://www.apache.org/licenses/LICENSE-2.0
.. _`cookiecutter-pytest-plugin`: https://github.com/pytest-dev/cookiecutter-pytest-plugin
.. _`file an issue`: https://github.com/martinwalsh/pytest-salt-formula/issues
.. _`pytest`: https://github.com/pytest-dev/pytest
.. _`tox`: https://tox.readthedocs.io/en/latest/
.. _`pip`: https://pypi.org/project/pip/
.. _`PyPI`: https://pypi.org/project
