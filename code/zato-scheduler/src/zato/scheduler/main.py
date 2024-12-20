# -*- coding: utf-8 -*-

"""
Copyright (C) 2024, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# ConcurrentLogHandler - updates stlidb's logging config on import so this needs to stay
try:
    import cloghandler # type: ignore
except ImportError:
    pass
else:
    cloghandler = cloghandler # For pyflakes

# First thing in the process
from gevent import monkey
_ = monkey.patch_all()

# Zato
from zato.scheduler.server import SchedulerServer

# ################################################################################################################################
# ################################################################################################################################

def main():
    SchedulerServer.start_from_repo_location()

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
