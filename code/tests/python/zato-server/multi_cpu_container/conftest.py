# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys

# pytest
import pytest

# ################################################################################################################################
# ################################################################################################################################

_this_directory = os.path.dirname(__file__)
_tests_directory = os.path.abspath(os.path.join(_this_directory, '..', '..'))

# The shared libraries of the live suites and the helpers of this suite
sys.path.insert(0, os.path.join(_tests_directory, 'zato-common', 'lib'))
sys.path.insert(0, _this_directory)

# Zato
from zato_container import build_image

# ################################################################################################################################
# ################################################################################################################################

@pytest.fixture(scope='session', autouse=True)
def runtime_image() -> 'None':
    """ Builds the image that every container of the suite runs, once per session.
    """
    build_image()

# ################################################################################################################################
# ################################################################################################################################
