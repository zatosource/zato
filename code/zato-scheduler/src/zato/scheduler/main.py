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

# stdlib
import os

# Zato
from zato.scheduler.server import SchedulerServer

# ################################################################################################################################
# ################################################################################################################################

def main():
    base_dir = os.environ['Zato_Component_Dir']
    SchedulerServer.start_from_repo_location(base_dir=base_dir)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
