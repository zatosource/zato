# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import fcntl
import os
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
from json import dumps, loads

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Iterator
    from zato.common.lets_encrypt.paths import SSLPaths
    from zato.common.typing_ import anydict, boolnone, strnone

# ################################################################################################################################
# ################################################################################################################################

_File_Mode = 0o600
_Dir_Mode = 0o700

# How much of the lock file is read to learn what the process holding the lock is doing.
_Operation_Max_Size = 64

# ################################################################################################################################
# ################################################################################################################################

class LockBusy(Exception):
    """ Raised when another process already runs the ACME client.
    """

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class Status:

    # When the certificate was last checked, whether that check succeeded and why it failed if it did not.
    last_check_utc: 'strnone'
    is_last_check_ok: 'boolnone'
    last_check_error: 'str'

    # When port 443 was last checked, whether Let's Encrypt could reach this host through it and why not if it could not.
    port_check_utc: 'strnone'
    is_port_ready: 'boolnone'
    port_check_error: 'str'

    def to_dict(self) -> 'anydict':
        out = {
            'last_check_utc': self.last_check_utc,
            'is_last_check_ok': self.is_last_check_ok,
            'last_check_error': self.last_check_error,
            'port_check_utc': self.port_check_utc,
            'is_port_ready': self.is_port_ready,
            'port_check_error': self.port_check_error,
        }
        return out

# ################################################################################################################################
# ################################################################################################################################

def utc_now() -> 'str':
    out = datetime.now(timezone.utc).isoformat()
    return out

# ################################################################################################################################

def _write_json(path:'str', data:'anydict') -> 'None':
    """ Replaces a file with new contents, so that a reader never sees a partially written one.
    """
    os.makedirs(os.path.dirname(path), mode=_Dir_Mode, exist_ok=True)

    new_path = path + '.new'
    file_descriptor = os.open(new_path, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, _File_Mode)

    with os.fdopen(file_descriptor, 'w') as output_file:
        _ = output_file.write(dumps(data))

    os.replace(new_path, path)

# ################################################################################################################################

def _read_json(path:'str') -> 'anydict':
    with open(path) as input_file:
        out = loads(input_file.read())
    return out

# ################################################################################################################################
# ################################################################################################################################

def load_is_enabled(paths:'SSLPaths') -> 'boolnone':
    """ Returns whether Let's Encrypt was enabled or disabled in the Dashboard, or None if it never was either.
    """
    if not os.path.exists(paths.settings):
        return None

    settings = _read_json(paths.settings)

    out = settings['is_enabled']
    return out

# ################################################################################################################################

def save_is_enabled(paths:'SSLPaths', is_enabled:'bool') -> 'None':
    _write_json(paths.settings, {'is_enabled': is_enabled})

# ################################################################################################################################
# ################################################################################################################################

def load_status(paths:'SSLPaths') -> 'Status':
    """ Returns the outcome of the most recent checks, with nothing in it if no check has run yet.
    """
    out = Status()

    if not os.path.exists(paths.status):
        out.last_check_utc = None
        out.is_last_check_ok = None
        out.last_check_error = ''
        out.port_check_utc = None
        out.is_port_ready = None
        out.port_check_error = ''
        return out

    data = _read_json(paths.status)

    out.last_check_utc = data['last_check_utc']
    out.is_last_check_ok = data['is_last_check_ok']
    out.last_check_error = data['last_check_error']
    out.port_check_utc = data['port_check_utc']
    out.is_port_ready = data['is_port_ready']
    out.port_check_error = data['port_check_error']

    return out

# ################################################################################################################################

def save_certificate_check(paths:'SSLPaths', is_ok:'bool', error:'str') -> 'None':
    """ Records the outcome of a certificate check, leaving the one of the port check as it is.
    """
    status = load_status(paths)

    status.last_check_utc = utc_now()
    status.is_last_check_ok = is_ok
    status.last_check_error = error

    _write_json(paths.status, status.to_dict())

# ################################################################################################################################

def save_port_check(paths:'SSLPaths', is_ready:'bool', error:'str') -> 'None':
    """ Records the outcome of a port check, leaving the one of the certificate check as it is.
    """
    status = load_status(paths)

    status.port_check_utc = utc_now()
    status.is_port_ready = is_ready
    status.port_check_error = error

    _write_json(paths.status, status.to_dict())

# ################################################################################################################################
# ################################################################################################################################

@contextmanager
def acquire_lock(paths:'SSLPaths', operation:'str') -> 'Iterator[None]':
    """ Holds the lock for as long as the ACME client runs, raising LockBusy if another process already holds it.
    """
    os.makedirs(paths.data_dir, mode=_Dir_Mode, exist_ok=True)

    file_descriptor = os.open(paths.lock, os.O_RDWR | os.O_CREAT, _File_Mode)

    # The lock is never waited for, because the process that holds it may keep it for minutes ..
    try:
        fcntl.flock(file_descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError:
        os.close(file_descriptor)
        raise LockBusy('Another certificate check is running') from None

    # .. and once it is ours, the file says what we are doing, which is what the Dashboard shows.
    try:
        os.ftruncate(file_descriptor, 0)
        _ = os.write(file_descriptor, operation.encode())
        yield
    finally:
        os.ftruncate(file_descriptor, 0)
        fcntl.flock(file_descriptor, fcntl.LOCK_UN)
        os.close(file_descriptor)

# ################################################################################################################################

def get_running_operation(paths:'SSLPaths') -> 'str':
    """ Returns what the process holding the lock is doing, or an empty string if no process holds it.
    """
    if not os.path.exists(paths.lock):
        return ''

    file_descriptor = os.open(paths.lock, os.O_RDONLY)

    try:

        # A shared lock can be taken only if no process holds the exclusive one ..
        try:
            fcntl.flock(file_descriptor, fcntl.LOCK_SH | fcntl.LOCK_NB)
        except BlockingIOError:
            operation = os.read(file_descriptor, _Operation_Max_Size)
            return operation.decode()

        # .. in which case it is released at once, because it was taken only to find that out.
        fcntl.flock(file_descriptor, fcntl.LOCK_UN)
        return ''

    finally:
        os.close(file_descriptor)

# ################################################################################################################################
# ################################################################################################################################
