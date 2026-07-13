# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# Process handles and directories that the conftest's atexit cleanup will dispose of.
# This lives in its own module so tests that replace processes (e.g. server restarts)
# can update the same dict the conftest reads, without importing the conftest itself.
cleanup_refs = {
    'server_process': None,
    'dashboard_process': None,
    'listener_process': None,
    'queue_bridge_redis_process': None,
    'temporary_dir': None,
}
