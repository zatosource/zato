# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# gevent - the write APIs run under gevent, as they do in a server, so the patching runs before anything else is imported.
from gevent import monkey
_ = monkey.patch_all()

# stdlib
import os
import sys

_here = os.path.dirname(__file__)

# The write APIs of this directory
sys.path.insert(0, _here)

# ################################################################################################################################
# ################################################################################################################################
