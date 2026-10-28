# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# gevent - the writer runs under gevent as in the server, so the patching runs before anything else is imported.
from gevent import monkey
_ = monkey.patch_all()

# stdlib
import atexit
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'lib')))

# Zato
from gevent_monitor import pytest_pyfunc_call as pytest_pyfunc_call
from perf import silence_logging_teardown

_ = atexit.register(silence_logging_teardown)

# ################################################################################################################################
# ################################################################################################################################
