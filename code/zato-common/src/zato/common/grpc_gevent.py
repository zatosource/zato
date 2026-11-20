# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The C-core of gRPC cooperates with gevent only in a process that has run init_gevent before its first channel
# is created. Each gevent-based module that creates channels imports this one first, and the import runs the call
# once per process.

# gRPC
from grpc.experimental.gevent import init_gevent

# ################################################################################################################################
# ################################################################################################################################

init_gevent()

# ################################################################################################################################
# ################################################################################################################################
