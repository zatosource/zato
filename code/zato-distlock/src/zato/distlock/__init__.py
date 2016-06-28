# -*- coding: utf-8 -*-

"""
Copyright (C) 2016 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing
from ctypes import c_size_t

# SQLAlchemy
from sqlalchemy import func

# ################################################################################################################################

class LockManager(object):
    """ A distributed lock manager based on SQL or, if only IPC is needed, on fcntl.
    """
    def __init__(self, session):
        self.session = session

    def obtain(self, name):
        with closing(self.session()) as session:

            lock_id = hash(name)
            is_locked = session.execute(func.pg_try_advisory_lock(lock_id)).scalar()

            return lock_id, is_locked

# ################################################################################################################################

class PostgresSQLLock(object):
    pass

# ################################################################################################################################

class MySQLLock(object):
    pass

# ################################################################################################################################

class OracleLock(object):
    pass

# ################################################################################################################################

class SQLiteLock(object):
    pass

# ################################################################################################################################
