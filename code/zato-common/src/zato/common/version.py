# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import os
from sys import version_info as py_version_info

# Python 2/3 compatibility
from past.builtins import execfile

# ################################################################################################################################
# ################################################################################################################################

def get_version():
    try:
        curdir = os.path.dirname(os.path.abspath(__file__))
        _version_py = os.path.normpath(os.path.join(curdir, '..', '..', '..', '..', '.version.py'))
        _locals = {}
        execfile(_version_py, _locals)
        version = 'Zato {}'.format(_locals['version'])
    except IOError:
        version = '3.1'
    finally:
        version = '{}-py{}.{}.{}'.format(version, py_version_info.major, py_version_info.minor, py_version_info.micro)

    return version

# ################################################################################################################################
# ################################################################################################################################
