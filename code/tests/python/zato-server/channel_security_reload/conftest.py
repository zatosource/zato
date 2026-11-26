# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# gevent
from gevent import monkey

# The modules of this suite import the server's configuration manager, and with it every library a server uses,
# so the process is patched before any of them binds a lock or a socket of its own.
if not monkey.is_module_patched('threading'):
    _ = monkey.patch_all()

# ################################################################################################################################
# ################################################################################################################################
