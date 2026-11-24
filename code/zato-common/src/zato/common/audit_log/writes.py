# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The group commit of the writes to the tables of the audit log that are not new events - lineage links, the dedup ledger,
# and the updates and log lines of scheduler runs and file transfers. Each caller waits until the transaction
# with its write is committed, in a commit shared with the writes of concurrent callers.

# Zato
from zato.common.audit_log.common import get_commit_max_events
from zato.common.db_env.commit_queue import CommitQueue
from zato.common.db_env.engine import call_database

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from sqlalchemy.engine import Connection, Engine
    from zato.common.typing_ import any_, anylist, anytuple, callable_

    # Dummy assignments to satisfy type checkers
    Connection = Connection
    Engine = Engine

# ################################################################################################################################
# ################################################################################################################################

# Each write counts as much as one event towards the size of a commit
_write_weight = 1

# ################################################################################################################################
# ################################################################################################################################

class _AuditWrite:
    """ One write of a caller - a function that receives the connection of the shared transaction and its arguments,
    with what it returned once the transaction is committed.
    """

    def __init__(self, engine:'Engine', func:'callable_', args:'anytuple') -> 'None':
        self.engine = engine
        self.func = func
        self.args = args
        self.result:'any_' = None

# ################################################################################################################################
# ################################################################################################################################

def _run_writes(engine:'Engine', writes:'list[_AuditWrite]') -> 'None':
    """ Runs the writes of one engine in a single transaction.
    """
    with engine.begin() as connection:
        for write in writes:
            write.result = write.func(connection, *write.args)

# ################################################################################################################################

def _write_batch(batch:'anylist') -> 'None':
    """ Runs the writes of the callers of one group commit, in one transaction for each engine they write to.
    """
    writes_by_engine:'dict[Engine, list[_AuditWrite]]' = {}

    for write in batch:
        if write.engine not in writes_by_engine:
            writes_by_engine[write.engine] = []
        writes_by_engine[write.engine].append(write)

    for engine, writes in writes_by_engine.items():
        call_database(engine, _run_writes, engine, writes)

# ################################################################################################################################
# ################################################################################################################################

# The one queue of the process, shared by all the writers of the audit log
_commit_queue = CommitQueue(write_batch=_write_batch, max_weight=get_commit_max_events())

# ################################################################################################################################
# ################################################################################################################################

def write_audit(engine:'Engine', func:'callable_', *args:'any_') -> 'any_':
    """ Runs a function that writes to the tables of the audit log with the connection of a transaction shared
    with concurrent callers, and returns what it returned once the transaction is committed.
    """
    write = _AuditWrite(engine, func, args)
    _commit_queue.write(write, weight=_write_weight, is_urgent=False)

    out = write.result
    return out

# ################################################################################################################################

def _execute_statement(connection:'Connection', statement:'any_', *params:'any_') -> 'any_':
    out = connection.execute(statement, *params)
    return out

# ################################################################################################################################

def execute_audit_write(engine:'Engine', statement:'any_', *params:'any_') -> 'any_':
    """ Runs one statement that writes to the tables of the audit log in a transaction shared with concurrent callers.
    """
    out = write_audit(engine, _execute_statement, statement, *params)
    return out

# ################################################################################################################################
# ################################################################################################################################
