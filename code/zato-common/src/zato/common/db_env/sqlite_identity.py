# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The identity of the SQLite file of a database, as the device and the inode of the file that a process opened first.
# A file that is removed or replaced while the process runs is no longer read or written by that process,
# and the process does not create a new file in its place. Only a new process reads and writes the file again.

# stdlib
import os
from logging import getLogger
from typing import NamedTuple
from urllib.parse import quote

# gevent
from gevent.monkey import get_original

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_, anylist, stranydict, strset

    any_ = any_
    anylist = anylist
    stranydict = stranydict
    strset = strset

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# The identity of each file, by its absolute path
identity_dict = dict[str, '_FileIdentity']

# ################################################################################################################################
# ################################################################################################################################

# The lock of the threads of the operating system, under which the threads of the gevent pool record a lost file.
_allocate_thread_lock = get_original('_thread', 'allocate_lock')

# The URI under which SQLite opens an existing file for reading and writing and refuses to create a missing one
_read_write_uri_template = 'file:{}?mode=rw'

# ################################################################################################################################
# ################################################################################################################################

class DatabaseFileReplaced(Exception):
    """ Raised when the SQLite file of a database was removed or replaced after the process opened it.
    """

# ################################################################################################################################
# ################################################################################################################################

class _FileIdentity(NamedTuple):
    device: 'int'
    inode: 'int'

# ################################################################################################################################
# ################################################################################################################################

class _IdentityState:
    """ The identity of each file that the process opened, and the files that were removed or replaced since,
    both by the absolute path of the file.
    """
    def __init__(self) -> 'None':
        self.identities:'identity_dict' = {}
        self.lost_paths:'strset' = set()
        self.lock = _allocate_thread_lock()

_state = _IdentityState()

# ################################################################################################################################
# ################################################################################################################################

def _get_identity(path:'str') -> '_FileIdentity | None':
    """ Returns the identity of the file under a path, or None if no file exists under it.
    """
    try:
        stat_result = os.stat(path)
    except FileNotFoundError:
        return None

    out = _FileIdentity(stat_result.st_dev, stat_result.st_ino)
    return out

# ################################################################################################################################

def _new_exception(path:'str') -> 'DatabaseFileReplaced':
    """ Returns the exception that refuses each use of a file that was removed or replaced.
    """
    out = DatabaseFileReplaced(f'SQLite database file `{path}` was removed or replaced while the process was running')
    return out

# ################################################################################################################################

def _set_lost(path:'str', expected:'_FileIdentity', found:'_FileIdentity | None') -> 'None':
    """ Records that a file was removed or replaced, logging it once per process.
    """
    with _state.lock:
        is_new = path not in _state.lost_paths
        _state.lost_paths.add(path)

    if is_new:
        logger.critical('SQLite database file `%s` was removed or replaced while the process was running, ' + \
            'expected identity %s, found %s, the process neither reads nor writes the database until it restarts',
            path, expected, found)

# ################################################################################################################################

def check_identity(db_path:'str') -> 'None':
    """ Raises DatabaseFileReplaced if the file under a path is not the file whose identity the process recorded for it.
    A path without a recorded identity is not checked.
    """
    path = os.path.abspath(db_path)

    # A file that was lost once stays lost for the lifetime of the process ..
    if path in _state.lost_paths:
        raise _new_exception(path)

    # .. a file that the process has not opened yet has nothing to be compared with ..
    if not (expected := _state.identities.get(path)):
        return

    # .. and any other file must be the one that the process opened.
    found = _get_identity(path)

    if found != expected:
        _set_lost(path, expected, found)
        raise _new_exception(path)

# ################################################################################################################################

def record_identity(db_path:'str') -> 'None':
    """ Records the identity of the file under a path that the process opened, or, if the process recorded one before,
    raises DatabaseFileReplaced if the file is not the same one.
    """
    path = os.path.abspath(db_path)

    # A file whose identity was recorded before must still be the same one ..
    if path in _state.identities:
        check_identity(path)

    # .. a file opened for the first time has its identity recorded ..
    elif identity := _get_identity(path):
        _state.identities[path] = identity

    # .. and a file that disappeared before its identity could be recorded is refused.
    else:
        raise _new_exception(path)

# ################################################################################################################################

def is_file_lost(db_path:'str') -> 'bool':
    """ Whether the file under a path was removed or replaced after the process opened it.
    """
    path = os.path.abspath(db_path)

    out = path in _state.lost_paths
    return out

# ################################################################################################################################
# ################################################################################################################################

class IdentityGuard:
    """ Checks the identity of the SQLite file of an engine each time a connection of its pool is opened
    or checked out. A connection to a file whose identity the process recorded is opened in the read-write mode
    of SQLite, in which a missing file is not created.
    """
    def __init__(self, db_path:'str') -> 'None':
        self.db_path = db_path

    def on_connect(self, dialect:'any_', connection_record:'any_', cargs:'anylist', cparams:'stranydict') -> 'None':

        path = os.path.abspath(self.db_path)

        # A file that the process has not opened yet is created if it does not exist ..
        if path not in _state.identities:
            return

        # .. whereas a file opened before must be the same one, and it is opened without creating it.
        check_identity(path)

        quoted_path = quote(path)

        cargs[0] = _read_write_uri_template.format(quoted_path)
        cparams['uri'] = True

    def on_checkout(self, dbapi_connection:'any_', connection_record:'any_', connection_proxy:'any_') -> 'None':
        check_identity(self.db_path)

# ################################################################################################################################
# ################################################################################################################################
