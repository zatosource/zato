# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The connections of the Zato database when the active-standby node replicates it. The node is the only process that
# checkpoints the write-ahead log of the database, so the connections never checkpoint it, neither when a commit
# leaves the log over a limit nor when the last connection closes. A connection opens only on a host whose node
# serves requests, and each change returns once the standby has stored it.

# stdlib
import sqlite3

# Zato
from zato.common.ha.barrier import wait_for_replication
from zato.common.ha.common import is_active_standby, is_shared_storage

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import any_

    # Dummy assignments to satisfy type checkers
    any_ = any_

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The number of pages after which a commit checkpoints the log, which is never for a replicated database
    Autocheckpoint_Disabled = 0

# ################################################################################################################################
# ################################################################################################################################

class ReplicatedCursor(sqlite3.Cursor):
    """ A cursor whose statements that commit on their own, outside a transaction, return once the standby
    has stored what they changed.
    """

    connection: 'ReplicatedConnection'

    def execute(self, sql:'str', parameters:'any_'=()) -> 'ReplicatedCursor':
        _ = super().execute(sql, parameters)
        self._sync_outside_transaction()
        return self

    def executemany(self, sql:'str', seq_of_parameters:'any_') -> 'ReplicatedCursor':
        _ = super().executemany(sql, seq_of_parameters)
        self._sync_outside_transaction()
        return self

    def executescript(self, sql_script:'str') -> 'ReplicatedCursor':
        _ = super().executescript(sql_script)
        self._sync_outside_transaction()
        return self

    def _sync_outside_transaction(self) -> 'None':

        # A statement in a transaction is replicated when the transaction commits
        if not self.connection.in_transaction:
            self.connection.sync_changes(needs_schema_version=False)

# ################################################################################################################################

class ReplicatedConnection(sqlite3.Connection):
    """ A connection whose changes, of rows and of the schema alike, return once the standby has stored them.
    A commit, a rollback and a close request the barrier whenever the number of changed rows or the version
    of the schema differs from its value at the previous barrier, and so does a statement that commits on its own,
    outside a transaction, whenever it changed any row.
    """

    def __init__(self, *args:'any_', **kwargs:'any_') -> 'None':
        super().__init__(*args, **kwargs)

        # What the connection had changed at the previous barrier, which mark_synced reads once the connection is set up
        self._synced_changes = 0
        self._synced_schema_version = 0

    def cursor(self, factory:'any_'=ReplicatedCursor) -> 'ReplicatedCursor':  # type: ignore[override]
        out = super().cursor(factory)
        return out

    def _get_schema_version(self) -> 'int':

        # A plain cursor, which requests no barrier of its own
        cursor = sqlite3.Cursor(self)

        try:
            row = cursor.execute('pragma schema_version').fetchone()
        finally:
            cursor.close()

        out = row[0]
        return out

    def mark_synced(self) -> 'None':
        """ Records what the connection has changed as replicated.
        """
        self._synced_changes = self.total_changes
        self._synced_schema_version = self._get_schema_version()

    def sync_changes(self, *, needs_schema_version:'bool') -> 'None':
        """ Returns once the standby has stored the changes of the connection made since the previous barrier.
        """
        changes = self.total_changes

        if needs_schema_version:
            schema_version = self._get_schema_version()
        else:
            schema_version = self._synced_schema_version

        if changes != self._synced_changes or schema_version != self._synced_schema_version:
            wait_for_replication()

            self._synced_changes = changes
            self._synced_schema_version = schema_version

    def commit(self) -> 'None':
        """ Commits the current transaction and returns once the standby has stored what the connection changed.
        """
        super().commit()
        self.sync_changes(needs_schema_version=True)

    def rollback(self) -> 'None':
        """ Rolls back the current transaction and returns once the standby has stored what the connection changed
        outside of it, e.g. in statements that committed on their own.
        """
        super().rollback()
        self.sync_changes(needs_schema_version=True)

    def close(self) -> 'None':
        """ Returns once the standby has stored what the connection changed and closes the connection,
        which is closed even if the barrier fails.
        """
        try:
            self.sync_changes(needs_schema_version=True)
        finally:
            super().close()

# ################################################################################################################################
# ################################################################################################################################

def set_replicated_pragmas(dbapi_connection:'ReplicatedConnection', connection_record:'any_') -> 'None':
    """ Turns off the checkpoints of a new connection of the replicated database and confirms that the node
    of this host serves requests before the connection reads anything from the database.
    """

    # Closing the connection never checkpoints the log ..
    _ = dbapi_connection.setconfig(sqlite3.SQLITE_DBCONFIG_NO_CKPT_ON_CLOSE, True)

    # .. the database is opened only on the host that serves requests ..
    wait_for_replication()

    # .. no commit checkpoints the log either ..
    cursor = dbapi_connection.cursor()
    _ = cursor.execute(f'pragma wal_autocheckpoint={ModuleCtx.Autocheckpoint_Disabled}')
    cursor.close()

    # .. and what the connection changes from here on is compared with what it holds now.
    dbapi_connection.mark_synced()

# ################################################################################################################################
# ################################################################################################################################

def holds_log_for_node(is_replicated:'bool') -> 'bool':
    """ Returns whether the log of a database is left to the active-standby node, which is the case for the Zato database
    when this process runs in an environment of an active-standby pair whose hosts do not share one PostgreSQL database.
    """

    # Our response to produce
    out = False

    if is_replicated:
        if is_active_standby():
            out = not is_shared_storage()

    return out

# ################################################################################################################################
# ################################################################################################################################
