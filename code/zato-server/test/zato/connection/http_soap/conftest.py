# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# gevent - the monkey-patching must run before anything imports threading, otherwise the RLock
# objects the coalescing code creates would block the OS thread and silently invalidate
# every interleaving and stress test in this directory.
from gevent import monkey

_ = monkey.patch_all()

# stdlib - imported only now, after the patching above
import threading

# The coalescing tests are meaningless without a patched threading module - fail loudly here
# rather than let them pass against unpatched locks.
assert monkey.is_module_patched('threading'), 'gevent monkey-patching must be active before threading is imported'

# The import is needed only for the assertion above
threading = threading
