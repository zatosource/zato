from typing import Any, TYPE_CHECKING

import logging
import os
from datetime import datetime, timedelta
from errno import ENOENT
from hashlib import sha256
from tempfile import gettempdir
from threading import current_thread
from traceback import format_exc
from sqlalchemy import func
from zato.common.util.api import get_current_user, make_repr
from zato.common.util.time_ import utcnow
from portalocker import lock as portalocker_lock, LockException, LOCK_NB, LOCK_EX, unlock
from typing import BinaryIO


class MAX:
    LEN_NS: Any
    LEN_NAME: Any

class DEFAULT:
    TTL: Any
    BLOCK: Any
    BLOCK_INTERVAL: Any

class LOCK_TYPE:
    PERMANENT: Any
    TRANSIENT: Any

class LockTimeout(Exception):
    ...

class LockInfo:
    lock: Any
    namespace: Any
    name: Any
    priv_id: Any
    pub_id: Any
    ttl: Any
    acquired: Any
    lock_type: Any
    block: Any
    block_interval: Any
    release: Any
    def __init__(self: Any, lock: Any, namespace: Any, name: Any, priv_id: Any, pub_id: Any, ttl: Any, acquired: Any, lock_type: Any, block: Any, block_interval: Any) -> None: ...
    def __repr__(self: Any) -> None: ...
    def __nonzero__(self: Any) -> None: ...

class Lock:
    acquire: Any
    os_user_name: Any
    session: Any
    namespace: Any
    name: Any
    ttl: Any
    priv_id: Any
    pub_id: Any
    lock_type: Any
    acquired: Any
    released: Any
    block: Any
    block_interval: Any
    raise_if_not_acquired: Any
    def __init__(self: Any, os_user_name: Any, session: Any, namespace: Any, name: Any, ttl: Any, block: Any, block_interval: Any, raise_if_not_acquired: Any, _permanent: Any = ..., _transient: Any = ...) -> None: ...
    def _acquire_impl(self: Any, *args: Any, **kwargs: Any) -> None: ...
    def __enter__(self: Any, pub_hash_func: Any = ..., _permanent: Any = ...) -> None: ...
    def _acquire(self: Any, _utcnow: Any = ..., _has_debug: Any = ...) -> None: ...
    def _wait_in_greenlet(self: Any, _utcnow: Any = ..., _timedelta: Any = ...) -> None: ...
    def release(self: Any, *ignored_args: Any, **ignored_kwargs: Any) -> None: ...
    def _sustain(self: Any) -> None: ...
    def __exit__(self: Any, type_: Any, value: Any, traceback: Any) -> None: ...

class SQLLock(Lock):
    def release(self: Any, _has_debug: Any = ...) -> None: ...
    def _release_func(self: Any, *ignored_args: Any, **ignored_kwargs: Any) -> None: ...

class OracleLock(SQLLock):
    ...

class MySQLLock(SQLLock):
    _acquire_func: Any
    _release_func: Any
    def _acquire_impl(self: Any) -> None: ...

class PostgresSQLLock(SQLLock):
    _acquire_func: Any
    _release_func: Any
    def _acquire_impl(self: Any) -> None: ...

class FCNTLLock(Lock):
    lock_template: Any
    tmp_file: Ellipsis
    tmp_file_name: Any
    def __init__(self: Any, *args: Any, **kwargs: Any) -> None: ...
    def _acquire_impl(self: Any, _flags: Any = ..., tmp_dir: Any = ..., _utcnow: Any = ..., _has_debug: Any = ...) -> None: ...
    def release(self: Any, _has_debug: Any = ...) -> None: ...

class PassThrough(Lock):
    def __init__(self: Any, *ignored_args: Any, **ignored_kwargs: Any) -> None: ...
    def _acquire_impl(self: Any, *ignored_args: Any, **ignored_kwargs: Any) -> None: ...
    def release(self: Any, *ignored_args: Any, **ignored_kwargs: Any) -> None: ...

class LockManager:
    _lock_impl: Any
    backend_type: Any
    default_namespace: Any
    session: Any
    _lock_class: Any
    user_name: get_current_user
    def __init__(self: Any, backend_type: Any, default_namespace: Any, session: Any = ...) -> None: ...
    def __call__(self: Any, name: Any, namespace: Any = ..., ttl: Any = ..., block: Any = ..., block_interval: Any = ..., max_len_ns: Any = ..., max_len_name: Any = ..., max_chars: Any = ..., raise_if_not_acquired: Any = ...) -> Lock: ...
    def acquire(self: Any, *args: Any, **kwargs: Any) -> None: ...
