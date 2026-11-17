# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# gevent - the write APIs run their SQLite calls in the thread pool of the hub, as they do in a server,
# so the patching runs before anything else is imported.
from gevent import monkey
_ = monkey.patch_all()

# stdlib
import os
import sys

_here = os.path.dirname(__file__)

# The write APIs of this directory and the native fault libraries of the fault suite
sys.path.insert(0, _here)
sys.path.insert(0, os.path.abspath(os.path.join(_here, '..', '..', 'pubsub_faults')))

# ################################################################################################################################
# ################################################################################################################################
