# -*- coding: utf-8 -*-
from hooks import pytest_addoption, pytest_configure
from fixtures import show_sls, salt_minion, minion_opts, file_roots
from matchers import *
