# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import stat

# Zato
from zato.common.db_env.database import dispose_database_engine, get_database_sqlite_path

# ################################################################################################################################
# ################################################################################################################################

# The files SQLite keeps next to a WAL-mode database
_sqlite_companion_suffixes = ('-wal', '-shm')

# ################################################################################################################################
# ################################################################################################################################

def _repair_sqlite_companions(db_path:'str') -> 'None':
    """ Aligns -wal and -shm permissions with the main file. SQLite creates them with
    the main file's bits, so ones created during a read-only window stay read-only and
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
        dispose_database_engine()

# ################################################################################################################################

def dispose_stale_sqlite_engine() -> 'None':
    """ Disposes the cached engine when its SQLite file was deleted or made read-only
    on disk - the engine's open descriptors would otherwise keep writing into the old inode.
    """
    db_path = get_database_sqlite_path()

    # Only a file-based database can change on disk behind a live engine
    if db_path is None:
        return

    file_exists = os.path.exists(db_path)
    file_writable = os.access(db_path, os.W_OK)

    if not file_exists:
        dispose_database_engine()
        return

    if not file_writable:
        dispose_database_engine()
        return

    _repair_sqlite_companions(db_path)

# ################################################################################################################################
# ################################################################################################################################
