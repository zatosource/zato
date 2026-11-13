# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The connections of a SQLite database that the active-standby node replicates. The node is the only process that
# checkpoints the write-ahead log of such a database, so the connections never checkpoint it, neither when a commit
# leaves the log over a limit nor when the last connection closes. A connection opens only on a host whose node
# serves requests, and each commit of a database shipped synchronously returns once the standby has stored it.

# stdlib
import sqlite3

# Zato
from zato.common.ha.barrier import wait_for_replication
from zato.common.ha.common import is_active_standby, is_shared_storage, Synchronous_Databases

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

class ReplicatedConnection(sqlite3.Connection):
    """ A connection whose commits of changed rows wait for the replication barrier of its database.
    """

    # The name under which the node replicates the database, set when the connection is opened
    replicated_database:'str' = ''

    # Whether a commit waits until the standby has stored it
    needs_barrier:'bool' = False

    def commit(self) -> 'None':
        """ Commits the current transaction and, if it changed any row of a database shipped synchronously,
        returns once the standby has stored the commit.
        """
        has_transaction = self.in_transaction

        super().commit()

        if self.needs_barrier:
            if has_transaction:
                wait_for_replication(self.replicated_database)

# ################################################################################################################################
# ################################################################################################################################

class ReplicatedPragmas:
    """ Prepares each new connection of one replicated database.
    """

    def __init__(self, replicated_database:'str') -> 'None':
        self.replicated_database = replicated_database
        self.needs_barrier = replicated_database in Synchronous_Databases

    def on_connect(self, dbapi_connection:'ReplicatedConnection', connection_record:'any_') -> 'None':
        """ Turns off the checkpoints of the connection and confirms that the node of this host serves requests
        before the connection reads anything from the database.
        """
        dbapi_connection.replicated_database = self.replicated_database
        dbapi_connection.needs_barrier = self.needs_barrier

        # Closing the connection never checkpoints the log ..
        _ = dbapi_connection.setconfig(sqlite3.SQLITE_DBCONFIG_NO_CKPT_ON_CLOSE, True)

        # .. the database is opened only on the host that serves requests ..
        wait_for_replication(self.replicated_database)

        # .. and no commit checkpoints the log either.
        cursor = dbapi_connection.cursor()
        _ = cursor.execute(f'pragma wal_autocheckpoint={ModuleCtx.Autocheckpoint_Disabled}')
        cursor.close()

# ################################################################################################################################
# ################################################################################################################################

def holds_log_for_node(replicated_database:'str') -> 'bool':
    """ Returns whether the log of a database is left to the active-standby node, which is the case for the databases
    that the node replicates when this process runs in an environment of an active-standby pair whose hosts
    do not share one PostgreSQL database.
    """

    # Our response to produce
    out = False

    if replicated_database:
        if is_active_standby():
            out = not is_shared_storage()

    return out

# ################################################################################################################################
# ################################################################################################################################
