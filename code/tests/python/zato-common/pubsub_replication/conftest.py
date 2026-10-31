# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# gevent
from gevent import monkey
_ = monkey.patch_all()

# stdlib
import os
import sys

_here = os.path.dirname(__file__)
sys.path.insert(0, _here)

# ################################################################################################################################
# ################################################################################################################################
