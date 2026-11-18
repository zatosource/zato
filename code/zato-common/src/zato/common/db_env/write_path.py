# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The write paths of the Zato database. Each mechanism that carries the guarantees of durability marks the work it runs,
# and every engine of the Zato database refuses a statement that writes while no mechanism is marked, or a write
# to the tables of the audit log that its mechanism is not allowed to make. A seed creates and removes rows only.
# A thread or a greenlet starts with no mark of its own, so a write handed over to one is refused as well.

# stdlib
import re
from contextlib import contextmanager
from contextvars import ContextVar

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Iterator
    from zato.common.typing_ import any_, anytuple, callable_

    # Dummy assignments to satisfy type checkers
    Iterator = Iterator

# ################################################################################################################################
# ################################################################################################################################

class Mechanism:

    # A batch that CommitQueue commits for its concurrent callers
    Group_Commit = 'group_commit'

    # A function that call_database runs, in turn with the other writes of the server to the same SQLite file
    Serialized_Write = 'serialized_write'

    # Cleanup, retention, index merge and rollup, started by their runners
    Maintenance = 'maintenance'

    # Schema creation and its seed rows
    Schema = 'schema'

    # The generation raise and its audit event
    Takeover = 'takeover'

    # Test and demo data written in bulk before the system under test uses it
    Seed = 'seed'

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The first keyword of a statement that writes rows or changes the schema, possibly after the common table expressions
    # of a WITH clause
    Write_Statement = re.compile(
        r'^\s*(?:with\b.*?\)\s*)?(insert|update|delete|replace|merge|upsert|copy|truncate|create|drop|alter|vacuum|reindex)\b',
        re.IGNORECASE | re.DOTALL)

    # The keywords that precede the table of a statement that writes rows
    Table_Keywords = (
        r'insert\s+(?:or\s+\w+\s+)?into',
        r'replace\s+into',
        r'update(?:\s+or\s+\w+)?',
        r'delete\s+from',
        r'copy',
        r'truncate(?:\s+table)?',
    )

    # The table of a statement that writes rows, after its keyword
    Statement_Table = re.compile(
        r'^\s*(?:with\b.*?\)\s*)?(?:' + '|'.join(Table_Keywords) + r')\s+["`]?(\w+)',
        re.IGNORECASE | re.DOTALL)

    # The tables of the audit log, which only a group commit, maintenance, schema creation and a takeover write
    Audit_Tables = frozenset({
        'event',
        'event_attr',
        'event_body',
        'event_count',
        'event_dedup',
        'event_link',
        'event_open',
        'event_payload',
    })

    Audit_Mechanisms = frozenset({
        Mechanism.Group_Commit,
        Mechanism.Maintenance,
        Mechanism.Schema,
        Mechanism.Takeover,
    })

    # The statements of a seed, which creates and removes seed rows and its scratch tables, refreshes the statistics
    # of the tables it filled, and never changes a row
    Seed_Statements = frozenset({
        'insert',
        'copy',
        'delete',
        'truncate',
        'create',
        'drop',
        'vacuum',
    })

# ################################################################################################################################
# ################################################################################################################################

# The mechanism that runs the current work of a thread or of a greenlet, if any
_current_mechanism:'ContextVar[str | None]' = ContextVar('zato_write_path', default=None)

# ################################################################################################################################
# ################################################################################################################################

class WritePathViolation(Exception):
    """ Raised when a statement writes to the Zato database outside of the mechanism that is allowed to make it.
    """

# ################################################################################################################################
# ################################################################################################################################

def get_write_path() -> 'str | None':
    """ Returns the mechanism that runs the current work, or None outside of every mechanism.
    """
    out = _current_mechanism.get()
    return out

# ################################################################################################################################

@contextmanager
def write_path(mechanism:'str') -> 'Iterator[None]':
    """ Marks the work that runs within the block as the work of a mechanism.
    """
    token = _current_mechanism.set(mechanism)

    try:
        yield
    finally:
        _current_mechanism.reset(token)

# ################################################################################################################################

def run_in_write_path(mechanism:'str', func:'callable_', args:'anytuple') -> 'any_':
    """ Runs a function as the work of a mechanism, in a thread or a greenlet that has no mark of its own.
    """
    with write_path(mechanism):
        out = func(*args)

    return out

# ################################################################################################################################

def check_write_path(
    conn:'any_',
    cursor:'any_',
    statement:'str',
    parameters:'any_',
    context:'any_',
    executemany:'bool',
    ) -> 'None':
    """ Refuses a statement that writes to the Zato database outside of every mechanism, or that writes
    to the tables of the audit log within a mechanism not allowed to, before it reaches the database.
    """
    if not (write_match := ModuleCtx.Write_Statement.match(statement)):
        return

    mechanism = _current_mechanism.get()

    if mechanism is None:
        raise WritePathViolation(f'Statement writes outside of every mechanism -> `{statement}`')

    if mechanism == Mechanism.Seed:
        keyword = write_match.group(1).lower()
        if keyword not in ModuleCtx.Seed_Statements:
            raise WritePathViolation(f'Seed changes rows with `{keyword}` -> `{statement}`')
        return

    if mechanism in ModuleCtx.Audit_Mechanisms:
        return

    if match := ModuleCtx.Statement_Table.match(statement):
        table_name = match.group(1).lower()
        if table_name in ModuleCtx.Audit_Tables:
            raise WritePathViolation(f'Mechanism `{mechanism}` writes to audit table `{table_name}` -> `{statement}`')

# ################################################################################################################################
# ################################################################################################################################
