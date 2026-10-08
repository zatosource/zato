# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sys

# The suite's own helpers, e.g. amqp_stub, must be importable no matter where pytest runs from.
suite_dir = os.path.dirname(__file__)
sys.path.insert(0, suite_dir)

# ################################################################################################################################
# ################################################################################################################################
