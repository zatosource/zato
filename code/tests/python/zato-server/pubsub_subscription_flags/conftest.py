# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The live flags suite reuses the fixtures of the governed subscription live suite.

# stdlib
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'ha_pubsub_subscription'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'zato-common', 'lib'))

# pytest
pytest_plugins = ['conftest']

# ################################################################################################################################
# ################################################################################################################################
