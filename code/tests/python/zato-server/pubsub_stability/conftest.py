# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# gevent - the API clients, the partners and the push receiver of the traffic share one process as greenlets,
# so the patching runs before the conftest of any suite imports its modules.
from gevent import monkey
_ = monkey.patch_all()
