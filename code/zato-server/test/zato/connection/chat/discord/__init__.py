# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# gevent
from gevent import monkey

# The client runs its handshake in a greenlet, which must not block the test's own greenlet
# while the websocket waits for data, the same as in a server.
if not monkey.is_module_patched('threading'):
    _ = monkey.patch_all()

# stdlib
import atexit
import os
import sys

# The Discord simulator is in the shared test library, which every module of this package imports from
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', '..',
    'tests', 'python', 'zato-common', 'lib')))

# Test support
from logging_teardown import silence_logging_teardown # noqa: E402

# The log handlers of the run are flushed at exit, before the final garbage collection of the interpreter,
# which would otherwise take the lock of the logging module after gevent can no longer switch greenlets.
_ = atexit.register(silence_logging_teardown)
