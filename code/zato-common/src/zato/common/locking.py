# -*- coding: utf-8 -*-

"""
Copyright (C) 2016 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging

# retools
from retools.lock import Lock

# ################################################################################################################################

def get_lock(prefix, name, expires, timeout, backend):
    """ Returns a new distributed lock - right now it's only a thin wrapper around retools.lock
    but with time will grow to include SQL-based locks.
    """
    return Lock('{}{}'.format(prefix, name), expires, timeout, backend)