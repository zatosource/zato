# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# gevent - the database drivers' sockets must be cooperative,
# so the patching runs before anything else is imported.
from gevent import monkey
_ = monkey.patch_all()

# stdlib
import atexit
import os
import sys

sys.path.insert(0, os.path.dirname(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'lib')))

# Zato
from perf import silence_logging_teardown

# The late log-handler cleanup would otherwise fail under gevent once the hub is gone.
_ = atexit.register(silence_logging_teardown)

# ################################################################################################################################
# ################################################################################################################################
