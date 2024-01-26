# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# pylint: disable=abstract-method, arguments-differ

# stdlib
import logging
import os
from datetime import datetime, timedelta
from errno import ENOENT
from hashlib import sha256
from tempfile import gettempdir
from threading import current_thread
from traceback import format_exc

# gevent
from gevent import sleep, spawn

# portalocker
try:
    from portalocker import lock as portalocker_lock, LockException, LOCK_NB, LOCK_EX, unlock
except ImportError:
    pass

# SQLAlchemy
from sqlalchemy import func

# Zato
from zato.common.util.api import get_current_user, make_repr # pylint: disable=no-name-in-module

# ################################################################################################################################

if 0:
    from typing import BinaryIO
    BinaryIO = BinaryIO

# ################################################################################################################################

logger = logging.getLogger(__name__)
has_debug = logger.isEnabledFor(logging.DEBUG)

# ################################################################################################################################

class MAX:
    LEN_NS = 8
    LEN_NAME = 128

class DEFAULT:
    TTL = 60
    BLOCK = 10
    BLOCK_INTERVAL = 1

class LOCK_TYPE:
    PERMANENT = 'permanent'
    TRANSIENT = 'transient'

# ################################################################################################################################

class LockTimeout(Exception):
    """ Raised if a lock could not be obtained within the expected time.
    """

# ################################################################################################################################

class LockInfo:
    __slots__ = (
        'lock', 'namespace', 'name', 'priv_id', 'pub_id', 'ttl', 'acquired', 'lock_type', 'block', 'block_interval', 'release'
    )

    def __init__(self, lock, namespace, name, priv_id, pub_id, ttl, acquired, lock_type, block, block_interval):
        self.lock = lock
        self.namespace = namespace
        self.name = name
        self.priv_id = priv_id
        self.pub_id = pub_id
        self.ttl = ttl
        self.acquired = acquired
        self.lock_type = lock_type
        self.block = block
        self.block_interval = block_interval
        self.release = self.lock.release

    def __repr__(self):
        return make_repr(self)

    def __nonzero__(self):
        return self.acquired

# ################################################################################################################################

class Lock:
    """ Base class for all backend-specific locks.
    """
    def __init__(
        self,
        os_user_name,
        session,
        namespace,
        name,
        ttl,
        block,
        block_interval,
        raise_if_not_acquired,
        _permanent=LOCK_TYPE.PERMANENT,
        _transient=LOCK_TYPE.TRANSIENT
    ) -> 'None':
        self.os_user_name = os_user_name
        self.session = session() if session else None
        self.namespace = namespace
        self.name = name
        self.ttl = ttl
        self.priv_id = ''
        self.pub_id = ''
        self.lock_type = _permanent if ttl else _transient
        self.acquired = False
        self.released = False
        self.block = block
        self.block_interval = block_interval
        self.raise_if_not_acquired = raise_if_not_acquired

    def _acquire_impl(self, *args, **kwargs):
        raise NotImplementedError('Must be implemented in subclasses')

# ################################################################################################################################

    def __enter__(self, pub_hash_func=sha256, _permanent=LOCK_TYPE.PERMANENT):

        # Compute lock_id in PostgreSQL's internal format which is a 64-bit integer (bigint)
        self.priv_id = hash('{}{}'.format(self.namespace, self.name))
        self.pub_id = pub_hash_func(str(self.priv_id).encode('utf8')).hexdigest()

        # Try to acquire the lock
        self.acquired = self._acquire()

        # If it was acquired and we are a permanent lock we need to start a background task
        # to keep the lock around for as long as ttl or (if we are called through `with`)
        # until __exit__ is called, whichever comes first.
        if self.acquired and self.lock_type == _permanent:
            self._sustain()

        return LockInfo(self, self.namespace, self.name, self.priv_id, self.pub_id, self.ttl, self.acquired, self.lock_type,
            self.block, self.block_interval)

    acquire = __enter__

# ################################################################################################################################

    def _acquire(self, _utcnow=datetime.utcnow, _has_debug=has_debug):
        """ Try to acquire a lock by its ID. If not possible and block is not False
        sleep for that many seconds as block points to.
        """
        acquired = self._acquire_impl()

        # Ok, we do not have the lock. If configured to, let's wait until we can obtain one or we time out.

        _block = self.block
        _block_interval = self.block_interval

        if _block and not acquired:

            now = _utcnow()
            until = now + timedelta(seconds=_block)

            while now < until:
                sleep(_block_interval)
                acquired = self._acquire_impl()
                if acquired:
                    break
                now = _utcnow()

            if not acquired:
                msg = 'Could not obtain lock for `{}` `{}` within {}s'.format(self.namespace, self.name, _block)
                logger.warning(msg)
                if self.raise_if_not_acquired:
                    raise LockTimeout(msg)

        if _has_debug:
            logger.debug('Acquired status for %s (%s %s) is %s', self.priv_id, self.namespace, self.name, acquired)

        return acquired

# ################################################################################################################################

    def _wait_in_greenlet(self, _utcnow=datetime.utcnow, _timedelta=timedelta):
        """ Sleeps until self.ttl is reached or until the lock is released and then releases the lock if it is still held.
        """
        now = _utcnow()
        until = now + _timedelta(seconds=self.ttl)

        while now < until:
            if self.released:
                break
            now = _utcnow()
            sleep(0.1)

        if not self.released:
            self.release()

# ################################################################################################################################

    def release(self, *ignored_args, **ignored_kwargs):
        raise NotImplementedError()

# ################################################################################################################################

    def _sustain(self):
        """ Spawns a greenlet that will sustain the lock for at least self.ttl,
        possibly less if self.__exit__ is called earlier.
        """
        spawn(self._wait_in_greenlet)

# ################################################################################################################################

    def __exit__(self, type_, value, traceback):
        self.release()

# ################################################################################################################################

class SQLLock(Lock):
    """ Base class for all SQL-backed locks.
    """

    def release(self, _has_debug=has_debug):
        """ Releases the lock if it has not been released already assuming we managed to acquire the lock at all.
        """
        if self.acquired and not self.released:

            self.session.execute(self._release_func(self.priv_id))
            self.released = True

            if _has_debug:
                logger.debug('Released %s', self.priv_id)

        self.session.close()

# ################################################################################################################################

    def _release_func(self, *ignored_args, **ignored_kwargs):
        raise NotImplementedError()

# ################################################################################################################################

class OracleLock(SQLLock):
    pass

# ################################################################################################################################

class MySQLLock(SQLLock):
    _acquire_func = func.get_lock
    _release_func = func.release_lock

    def _acquire_impl(self):
        return self.session.execute(self._acquire_func(self.priv_id, 0)).scalar()

# ################################################################################################################################

class PostgresSQLLock(SQLLock):
    """ Distributed locks based on PostgreSQL.
    """
    _acquire_func = func.pg_try_advisory_lock
    _release_func = func.pg_advisory_unlock

    def _acquire_impl(self):
        return self.session.execute(self._acquire_func(self.priv_id)).scalar()

# ################################################################################################################################

class FCNTLLock(Lock):
    """ IPC-only lock based on Linux fcntl system calls.
    """
    lock_template = """
pid={}
greenlet_name={}
greenlet_id={}
creation_time_utc={}
user={}
""".lstrip()

    tmp_file: ... # type: BinaryIO

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.tmp_file_name = None

    def _acquire_impl(self, _flags=None, tmp_dir=gettempdir(), _utcnow=datetime.utcnow, _has_debug=has_debug):
        _flags = _flags or LOCK_EX | LOCK_NB
        current = current_thread()

        self.tmp_file_name = os.path.join(tmp_dir, 'zato-lock-{}'.format(self.pub_id))
        self.tmp_file = open(self.tmp_file_name, 'w+b')

        pid = os.getpid()
        current_name = current.name
        current_ident = current.ident

        contents = self.lock_template.format(
                pid, current_name, current_ident, _utcnow().isoformat(), self.os_user_name,
            )

        self.tmp_file.write(contents.encode('utf8'))
        self.tmp_file.flush()

        if _has_debug:
            logger.debug('Created lock file `%s` (%s %s %s)', self.tmp_file_name, pid, current_name, current_ident)

        try:
            portalocker_lock(self.tmp_file, _flags)
        except LockException:
            return False
        else:
            return True

    def release(self, _has_debug=has_debug):

        if not self.tmp_file.closed:

            logger.debug('About to unlock file %s', self.tmp_file_name)

            unlock(self.tmp_file)
            self.tmp_file.close()

            if _has_debug:
                logger.debug('Unlocked file %s', self.tmp_file_name)

            try:
                os.remove(self.tmp_file.name)
            except OSError as exc:

                # ENOENT = No such file, this is fine, apparently another process beat us to that lock's deletion.
                # But any other exception needs to be re-raised.
                if exc.errno != ENOENT:
                    raise
            else:
                if _has_debug:
                    logger.debug('Deleted lock file %s', self.tmp_file_name)

            if _has_debug:
                logger.debug('Unlocked `%s`', self.tmp_file)

# ################################################################################################################################

class PassThrough(Lock):
    """ A pass-through lock - used under Windows and for certain generic connections.
    """
    def __init__(self, *ignored_args, **ignored_kwargs) -> 'None':
        super().__init__(
            os_user_name=None,
            session=None,
            namespace=None,
            name=None,
            ttl=None,
            block=None,
            block_interval=None,
            raise_if_not_acquired=None,
        )

    def _acquire_impl(self, *ignored_args, **ignored_kwargs):
        return True

    def release(self, *ignored_args, **ignored_kwargs):
        pass

# ################################################################################################################################

# pylint: disable-next=unused-variable
class LockManager:
    """ A distributed lock manager based on SQL or, if only IPC is needed, on fcntl.
    """
    _lock_impl = {
        'postgresql+pg8000': PostgresSQLLock,
        'oracle': OracleLock,
        'mysql+pymysql': MySQLLock,
        'fcntl': FCNTLLock,
        'zato-pass-through': PassThrough,
        }

    def __init__(self, backend_type, default_namespace, session=None):
        self.backend_type = backend_type
        self.default_namespace = default_namespace
        self.session = session
        self._lock_class = self._lock_impl[backend_type]
        self.user_name = get_current_user()

    # pylint: disable-next=inconsistent-return-statements
    def __call__(self,
        name,
        namespace='',
        ttl=DEFAULT.TTL,
        block=DEFAULT.BLOCK,
        block_interval=DEFAULT.BLOCK_INTERVAL,
        max_len_ns=MAX.LEN_NS,
        max_len_name=MAX.LEN_NAME,
        max_chars=31,
        raise_if_not_acquired=True,
    ) -> 'Lock':

        try:
            if len(namespace) > max_len_ns:
                msg = 'Lock operation rejected. Namespace `{}` exceeds the limit of {} characters.'.format(namespace, max_len_ns)
                logger.warning(msg)
                raise ValueError(msg)

            if len(name) > max_len_name:

                # At times, we will have long lock names, e.g. when we want to lock access
                # to a file system path and the path is longer then MAX.LEN_NAME.
                # In such cases, the lock will contain the last N characters followed
                # by a hash of the whole name. This will fit in the MAX.LEN_NAME limit.

                if isinstance(name, str):
                    name = name.encode('utf8')
                    hash_digest = sha256(name).hexdigest()
                    name = name.decode('utf8')

                name_prefix = name[:max_chars]
                name_suffix = name[-max_chars:]
                name = '{}-{}-{}'.format(name_prefix, name_suffix, hash_digest)

            # To be on the safe side, check again if the limit is not exceeded
            if len(name) > max_len_name:

                msg = 'Lock operation rejected. Name `{}` exceeds the limit of {} characters.'.format(name, max_len_name)
                logger.warning(msg)
                raise ValueError(msg)

        except Exception:
            logger.warning('Lock could not be acquired, e:`%s`', format_exc())

        else:

            namespace = namespace or self.default_namespace

            logger.debug('Acquiring lock class:`%s` -> ns:%s, n:%s, t:%s, b:%s, bi:%s, s:%s',
                self._lock_class, namespace, name, ttl, block, block_interval, self.session)

            return self._lock_class(
                self.user_name,
                self.session,
                namespace,
                name,
                ttl,
                block,
                block_interval,
                raise_if_not_acquired
            )

    def acquire(self, *args, **kwargs):
        return self(*args, **kwargs).acquire()

# ################################################################################################################################
