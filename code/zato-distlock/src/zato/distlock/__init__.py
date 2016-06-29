# -*- coding: utf-8 -*-

"""
Copyright (C) 2016 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing
from ctypes import c_size_t
from datetime import datetime, timedelta
from hashlib import sha256
import logging

# gevent
from gevent import sleep, spawn

# SQLAlchemy
from sqlalchemy import func

# Zato
from zato.common.util import make_repr

# ################################################################################################################################

logger = logging.getLogger(__name__)
has_debug = logger.isEnabledFor(logging.DEBUG)

# ################################################################################################################################

MAX_LEN_NS = 8
MAX_LEN_NAME = 48

class LOCK_TYPE:
    permanent = 'permanent'
    transient = 'transient'

# ################################################################################################################################

class LockInfo(object):
    __slots__ = ('namespace', 'name', 'priv_id', 'pub_id', 'ttl', 'acquired', 'lock_type', 'block', 'block_interval')

    def __init__(self, namespace, name, priv_id, pub_id, ttl, acquired, lock_type, block, block_interval):
        self.namespace = namespace
        self.name = name
        self.priv_id = priv_id
        self.pub_id = pub_id
        self.ttl = ttl
        self.acquired = acquired
        self.lock_type = lock_type
        self.block = block
        self.block_interval = block_interval

    def __repr__(self):
        return make_repr(self)

# ################################################################################################################################

class Lock(object):
    """ Base class for all backend-specific locks.
    """
    def __init__(self, session, namespace, name, ttl, block, block_interval, _permanent=LOCK_TYPE.permanent,
            _transient=LOCK_TYPE.transient):
        self.session = session()
        self.namespace = namespace
        self.name = name
        self.ttl = ttl
        self.priv_id = ''
        self.lock_type = _permanent if ttl else _transient
        self.acquired = False
        self.released = False
        self.block = block
        self.block_interval = block_interval

# ################################################################################################################################

    def __enter__(self, pub_hash_func=sha256, _permanent=LOCK_TYPE.permanent):

        # Compute lock_id in PostgreSQL's internal format which is a 64-bit integer (bigint)
        self.priv_id = str(hash('{}{}'.format(self.namespace, self.name)))

        # Try to acquire the lock
        self.acquired = self._acquire()

        # If it was acquired and we are a permanent lock we need to start a background task
        # to keep the lock around for as long as ttl or (if we are called through `with`)
        # until __exit__ is called, whichever comes first.
        if self.acquired and self.lock_type == _permanent:
            self._sustain()

        return LockInfo(
            self.namespace, self.name, self.priv_id, pub_hash_func(self.priv_id).hexdigest(), self.ttl,
            self.acquired, self.lock_type, self.block, self.block_interval)

# ################################################################################################################################

    def _acquire(self, _utcnow=datetime.utcnow, _has_debug=has_debug):
        """ Try to acquire a lock by its ID. If not possible and block is not False
        sleep for that many seconds as block points to.
        """
        acquired = self._acquire_impl(self.priv_id)

        # Ok, we do not have the lock. If configured to, let's wait until we can obtain one or we time out.

        _block = self.block
        _block_interval = self.block_interval

        if _block and not acquired:

            now = _utcnow()
            until = now + timedelta(seconds=_block)

            while now < until:
                sleep(_block_interval)
                if self._acquire_impl(self.priv_id):
                    break
                now = _utcnow()

        if _has_debug:
            logger.debug('Acquired status for %s is %s', self.priv_id, self.acquired)

        return acquired

# ################################################################################################################################

    def _wait_in_greenlet(self, until, _utcnow=datetime.utcnow):
        """ Sleeps until `until` or until the lock is released and then releases the lock if it is still held.
        """
        now = _utcnow()

        while now < until:
            if self.released:
                break
            now = _utcnow()

        if not self.released:
            self._release()

# ################################################################################################################################

    def _sustain(self, _utcnow=datetime.utcnow, _timedelta=timedelta):
        """ Spawns a greenlet that will sustain the lock for at least self.ttl,
        possibly less if self.__exit__ is called earlier.
        """
        result = spawn(self._wait_in_greenlet, _utcnow() + _timedelta(seconds=self.ttl))

# ################################################################################################################################

    def _release(self, _has_debug=has_debug):
        """ Releases the lock if it has not been released already assuming we managed to acquire the lock at all.
        """
        if self.acquired and self.released:

            self.session.execute(func.pg_advisory_unlock(self.priv_id))
            self.released = True

            if _has_debug:
                logger.info('Released %s', self.priv_id)

        self.session.close()

# ################################################################################################################################

    def __exit__(self, type, value, traceback):
        self._release()

# ################################################################################################################################

class MySQLLock(Lock):
    pass

# ################################################################################################################################

class OracleLock(Lock):
    pass

# ################################################################################################################################

class FCNTLLock(Lock):
    pass

# ################################################################################################################################

class PostgresSQLLock(Lock):
    """ Distributed locks based on PostgreSQL.
    """
    def _acquire_impl(self, lock_id):
        return self.session.execute(func.pg_try_advisory_lock(lock_id)).scalar()

# ################################################################################################################################

class LockManager(object):
    """ A distributed lock manager based on SQL or, if only IPC is needed, on fcntl.
    """
    _lock_impl = {
        'postgresql+pg8000': PostgresSQLLock,
        'oracle': OracleLock,
        'mysql': MySQLLock,
        'fcntl': FCNTLLock,
        }

    def __init__(self, backend_type, session):
        self.backend_type = backend_type
        self.session = session
        self._lock_class = self._lock_impl[backend_type]

    def __call__(self, namespace, name, ttl=None, block=None, block_interval=1, max_len_ns=MAX_LEN_NS, max_len_name=MAX_LEN_NAME):

        if len(namespace) > max_len_ns:
            msg = 'Namespace `{}` exceeds the limit of {} characters'.format(namespace, max_len_ns)
            logger.warn(msg)
            raise ValueError(msg)

        if len(name) > max_len_name:
            msg = 'Name `{}` exceeds the limit of {} characters'.format(namespace, max_len_name)
            logger.warn(msg)
            raise ValueError(msg)

        return self._lock_class(self.session, namespace, name, ttl, block, block_interval)

# ################################################################################################################################
