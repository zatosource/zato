# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The faults that sessions of the test cause inside PostgreSQL - locks, transactions that stay open, backends ended
# or cancelled, forced checkpoints and connection slots that the test holds.

# stdlib
import math

# gevent
from gevent import sleep, spawn

# pg8000
from pg8000.exceptions import DatabaseError

# Zato
from faults import Fault, Fault_Application_Name, Total_Loss
from zato.common.test.pubsub_database import connect, ModuleCtx

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.test.pubsub_database import PubSubDatabase
    from zato.common.typing_ import any_, anylist, intlist, strlist

# ################################################################################################################################
# ################################################################################################################################

# The kinds of session faults of item 15.11 and the exhausted connections of item 15.10.
Session_Access_Exclusive  = 'access-exclusive'
Session_Long_Transaction  = 'long-transaction'
Session_Idle_Transaction  = 'idle-in-transaction'
Session_Terminate         = 'terminate'
Session_Cancel            = 'cancel'
Session_Checkpoint        = 'checkpoint'
Session_Connections       = 'connections'

# The kinds whose severity is the share of the pub/sub backends that each round affects.
Graded_Session_Kinds = [Session_Terminate, Session_Cancel]

# The kinds that run once, at no severity level.
Single_Session_Kinds = [Session_Access_Exclusive, Session_Long_Transaction, Session_Idle_Transaction,
    Session_Checkpoint, Session_Connections]

# How long each pub/sub table stays locked, how often backends are ended or cancelled,
# and how often a checkpoint is forced, in seconds.
_lock_seconds = 30
_round_seconds = 1
_checkpoint_seconds = 10

# What PostgreSQL reports once no connection slot is left.
_no_slots_left = ('too many clients', 'remaining connection slots are reserved')

# The tables of pub/sub, in the order in which they are locked.
_tables_query = "select tablename from pg_tables where schemaname = 'public' and tablename like 'pubsub%%' order by 1"

# The backends of pub/sub, apart from those of the faults themselves.
_backends_query = "select pid from pg_stat_activity where backend_type = 'client backend' and usename = %s " + \
    'and pid <> pg_backend_pid() and coalesce(application_name, %s) <> %s order by pid'

# ################################################################################################################################
# ################################################################################################################################

def _connect_session(database:'PubSubDatabase') -> 'any_':
    """ Opens a session of a fault, named so that the faults leave it alone.
    """
    out = connect(database)

    cursor = out.cursor()
    cursor.execute(f"set application_name = '{Fault_Application_Name}'")
    out.commit()

    return out

# ################################################################################################################################

def _read_tables(database:'PubSubDatabase') -> 'strlist':
    out:'strlist' = []
    connection = _connect_session(database)

    try:
        cursor = connection.cursor()
        cursor.execute(_tables_query)
        for row in cursor.fetchall():
            out.append(row[0])
    finally:
        connection.close()

    return out

# ################################################################################################################################
# ################################################################################################################################

class SessionFault(Fault):
    """ Item 15.11 and the connection slots of item 15.10 - what a session of the test does inside PostgreSQL
    for the duration of the fault.
    """

    def __init__(self, database:'PubSubDatabase', kind:'str') -> 'None':
        self.database = database
        self.kind = kind
        self.name = f'session-{kind}'
        self.level = 0

        # Each table is locked in turn, so the fault lasts at least as long as all of these locks.
        if kind == Session_Access_Exclusive:
            self.tables = _read_tables(database)
            self.min_duration = len(self.tables) * _lock_seconds
        else:
            self.tables:'strlist' = []

        # How many backends the rounds ended or cancelled, and how many connection slots the fault held.
        self.affected_backends = 0
        self.held_connections = 0

        self._connections:'anylist' = []
        self._greenlets:'anylist' = []

# ################################################################################################################################

    def _lock_tables(self) -> 'None':
        """ Holds an ACCESS EXCLUSIVE lock on each table in turn.
        """
        connection = self._connections[0]
        cursor = connection.cursor()

        for table_name in self.tables:
            cursor.execute(f'lock table {table_name} in access exclusive mode')
            sleep(_lock_seconds)
            connection.commit()

# ################################################################################################################################

    def _read_backends(self, cursor:'any_') -> 'intlist':
        out:'intlist' = []

        cursor.execute(_backends_query, (ModuleCtx.Username, '', Fault_Application_Name))
        for row in cursor.fetchall():
            out.append(row[0])

        return out

# ################################################################################################################################

    def _end_backends(self) -> 'None':
        """ Ends or cancels a share of the pub/sub backends in each round.
        """
        connection = self._connections[0]
        cursor = connection.cursor()

        if self.kind == Session_Terminate:
            function_name = 'pg_terminate_backend'
        else:
            function_name = 'pg_cancel_backend'

        while True:
            pids = self._read_backends(cursor)
            count = math.ceil(len(pids) * self.level / Total_Loss)

            for pid in pids[:count]:
                cursor.execute(f'select {function_name}(%s)', (pid,))

            connection.commit()
            self.affected_backends += count

            sleep(_round_seconds)

# ################################################################################################################################

    def _force_checkpoints(self) -> 'None':
        connection = self._connections[0]
        connection.autocommit = True
        cursor = connection.cursor()

        while True:
            cursor.execute('checkpoint')
            sleep(_checkpoint_seconds)

# ################################################################################################################################

    def _hold_connections(self) -> 'None':
        """ Opens connections until PostgreSQL has no slot left.
        """
        while True:
            try:
                connection = connect(self.database)
            except DatabaseError as e:
                for message in _no_slots_left:
                    if message in f'{e}':
                        return
                raise
            else:
                self._connections.append(connection)
                self.held_connections += 1

# ################################################################################################################################

    def apply(self, level:'int') -> 'None':
        self.level = level

        # Each kind has a session of its own, apart from the slots that the last kind holds with all of its connections.
        if self.kind == Session_Connections:
            self._hold_connections()
            return

        self._connections.append(_connect_session(self.database))
        connection = self._connections[0]

        if self.kind == Session_Access_Exclusive:
            self._greenlets.append(spawn(self._lock_tables))

        elif self.kind == Session_Long_Transaction:
            cursor = connection.cursor()
            cursor.execute('set transaction isolation level repeatable read')
            cursor.execute('select count(*) from pubsub_message')

        elif self.kind == Session_Idle_Transaction:
            cursor = connection.cursor()
            cursor.execute('select txid_current()')

        elif self.kind in Graded_Session_Kinds:
            self._greenlets.append(spawn(self._end_backends))

        elif self.kind == Session_Checkpoint:
            self._greenlets.append(spawn(self._force_checkpoints))

        # .. anything else is not a kind of session fault.
        else:
            raise Exception(f'Unknown session fault `{self.kind}`')

# ################################################################################################################################

    def remove(self) -> 'None':
        for greenlet in self._greenlets:
            greenlet.kill()

        self._greenlets = []

        # Closing a session rolls back what it left open and releases its locks.
        for connection in self._connections:
            connection.close()

        self._connections = []

# ################################################################################################################################
# ################################################################################################################################
