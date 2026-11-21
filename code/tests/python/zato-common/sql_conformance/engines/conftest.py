# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys

# The container of Toxiproxy of the fault suite, which the tests of this directory put in front of PostgreSQL
_conftest_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(_conftest_dir, '..', '..', 'pubsub_faults')))
