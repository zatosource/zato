# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import stat

# Zato
from zato.common.audit_log.common import Audit_DB_File_Name, metadata
from zato.common.db_env import dispose_env_engine, EnvDBConfig, get_env_values, set_sqlite_busy_timeout, Type_SQLite

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Connection
    Connection = Connection

# ################################################################################################################################
# ################################################################################################################################

# The files SQLite keeps next to a WAL-mode database
_sqlite_companion_suffixes = ('-wal', '-shm')

# How long a write waits for another writer once the database has refused a write, in milliseconds -
# a refused write drops its one event, and the writes after it are not to wait out the full busy timeout
# each until one of them goes through again.
_refused_write_busy_timeout_ms = 250

# Whether the most recent write to the audit database was refused - process-wide,
# as all writers in a process share one database.
_is_write_refused = False

# ################################################################################################################################
# ################################################################################################################################

# How the audit log database is selected and configured through the environment.
# The pool matters for SQLite too - without it every event opens and closes its own
# connection, and closing the last WAL connection runs a checkpoint with an fsync,
# which serializes high-volume producers like pub/sub behind disk flushes.
env_config = EnvDBConfig(
    env_prefix='Zato_Audit_Log_DB_',
    sqlite_file_name=Audit_DB_File_Name,
    metadata=metadata,
    needs_pool=True,
    needs_background_checkpoint=True,
)

# ################################################################################################################################

def _repair_sqlite_companions(db_path:'str') -> 'None':
    """ Aligns -wal and -shm permissions with the main file. SQLite creates them with
    the main file's bits, so ones born during a read-only window stay read-only and
    refuse every writer even after the main file's permissions come back.
    """
    db_mode = stat.S_IMODE(os.stat(db_path).st_mode)

    for suffix in _sqlite_companion_suffixes:

        companion_path = db_path + suffix

        if not os.path.exists(companion_path):
            continue

        if os.access(companion_path, os.W_OK):
            continue

        os.chmod(companion_path, db_mode)

        # Connections that mapped the companion while it was read-only stay read-only
        dispose_env_engine(env_config)

# ################################################################################################################################

def dispose_stale_sqlite_engine() -> 'None':
    """ Disposes the cached engine when its SQLite file was deleted or made read-only
    on disk - the engine's open descriptors would otherwise keep writing into the old inode.
    """
    values = get_env_values(env_config)

    # Only a file-based database can change on disk behind a live engine
    if values['type'] != Type_SQLite:
        return

    db_path = values['name']

    file_exists = os.path.exists(db_path)
    file_writable = os.access(db_path, os.W_OK)

    if not file_exists:
        dispose_env_engine(env_config)
        return

    if not file_writable:
        dispose_env_engine(env_config)
        return

    _repair_sqlite_companions(db_path)

# ################################################################################################################################

def _is_sqlite() -> 'bool':
    """ Whether the audit log database is a SQLite file.
    """
    values = get_env_values(env_config)

    out = values['type'] == Type_SQLite
    return out

# ################################################################################################################################

def mark_write_refused() -> 'None':
    """ Remembers that the database refused a write, which shortens the wait of the writes that follow.
    """
    global _is_write_refused
    _is_write_refused = True

# ################################################################################################################################

def mark_write_accepted() -> 'None':
    """ Forgets a refused write once one goes through again. The pooled connections carry the shortened wait,
    so they are disposed and the next write opens a fresh one with the full busy timeout.
    """
    global _is_write_refused

    if not _is_write_refused:
        return

    _is_write_refused = False
    dispose_env_engine(env_config)

# ################################################################################################################################

def apply_write_wait(connection:'Connection') -> 'None':
    """ Shortens the wait for another writer on this connection after a refused write.
    """
    if not _is_write_refused:
        return

    # Only a SQLite file has a busy timeout to shorten
    if not _is_sqlite():
        return

    set_sqlite_busy_timeout(connection, _refused_write_busy_timeout_ms)

# ################################################################################################################################
# ################################################################################################################################
