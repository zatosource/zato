# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# gevent - the monkey-patching must run before anything imports threading, otherwise the RLock
# objects the coalescing code creates would block the OS thread and silently invalidate
# every interleaving and stress test in this directory.
#
# The ssl module is left alone on purpose - the tests here never open a TLS connection and,
# by the time pytest imports this file, its own plugins have already imported ssl,
# which is what gevent warns about when it patches it.
from gevent import monkey

_ = monkey.patch_all(ssl=False)

# stdlib - imported only now, after the patching above
import atexit
import logging
import threading

# The coalescing tests are meaningless without a patched threading module - fail loudly here
# rather than let them pass against unpatched locks.
assert monkey.is_module_patched('threading'), 'gevent monkey-patching must be active before threading is imported'

# The import is needed only for the assertion above
threading = threading

# ################################################################################################################################
# ################################################################################################################################

def _release_logging_handlers() -> 'None':
    """ Closes the logging handlers while the gevent hub is still around.

    A handler collected during interpreter finalization would have its weak reference callback
    reach for the logging lock, which is a gevent lock now, and greenlets no longer run at that point.
    Dropping the weak references here means that there is nothing left to collect later on.
    """
    logging.shutdown()
    del logging._handlerList[:]

# The handler cleanup has to run before the interpreter starts tearing modules down
atexit.register(_release_logging_handlers)

# ################################################################################################################################
# ################################################################################################################################
