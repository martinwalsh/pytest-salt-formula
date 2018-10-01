# -*- coding: utf-8 -*-
import os


def abspath(path, join=''):
    return os.path.realpath(
        os.path.abspath(os.path.join(path, join))
    )


def touch(path, _tmpdir):
    path_elements = path.lstrip('/').split('/')
    while len(path_elements) > 1:
        _tmpdir = _tmpdir.mkdir(path_elements.pop(0))
    last = _tmpdir.join(path_elements.pop(0))
    last.write('')
    return last
