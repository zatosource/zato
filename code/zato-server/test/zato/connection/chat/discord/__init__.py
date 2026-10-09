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
import os
import sys

# The Discord simulator is in the shared test library, which every module of this package imports from
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..', '..', '..', '..',
    'tests', 'python', 'zato-common', 'lib')))
