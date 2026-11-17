# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys

# The registry of the static checks is imported by the tests of this directory under its own name.
_conftest_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _conftest_dir)
