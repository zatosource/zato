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
from functools import lru_cache

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from collections.abc import Iterator
    from zato.common.typing_ import any_, anytuple, callable_, strlist, strtuple

    # Dummy assignments to satisfy type checkers
    Iterator = Iterator

# ################################################################################################################################
# ################################################################################################################################

class Mechanism:

    # A batch that CommitQueue commits for its concurrent callers
    Group_Commit = 'group_commit'

    # A function that call_database runs as a transaction of its own
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

    # How many statement texts the parse of the write keywords and the table names is kept for. The statements
    # of the platform are a fixed set, so the cache holds all of them, and a statement evicted is parsed again.
    Max_Parsed_Statements = 4096

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

    # The keyword of a data-modifying common table expression, which writes rows even when the statement
    # that follows the WITH clause only reads them ..
    CTE_Write_Statement = re.compile(
        r'\bas\s+(?:not\s+)?(?:materialized\s+)?\(\s*(insert|update|delete)\b',
        re.IGNORECASE)

    # .. and the table that it writes to.
    CTE_Statement_Table = re.compile(
        r'\bas\s+(?:not\s+)?(?:materialized\s+)?\(\s*(?:insert\s+into|update|delete\s+from)\s+["`]?(\w+)',
        re.IGNORECASE)

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

@lru_cache(maxsize=ModuleCtx.Max_Parsed_Statements)
def _parse_statement(statement:'str') -> 'tuple[strtuple, strtuple]':
    """ Returns the keywords of the writes of a statement, of the statement itself and of its common table expressions,
    and the tables that these writes name. Both depend on the text of the statement alone.
    """
    keywords:'strlist' = []
    table_names:'strlist' = []

    if write_match := ModuleCtx.Write_Statement.match(statement):
        keywords.append(write_match.group(1).lower())

    for keyword in ModuleCtx.CTE_Write_Statement.findall(statement):
        keywords.append(keyword.lower())

    # A statement that does not write names no table that the guard checks
    if keywords:

        if match := ModuleCtx.Statement_Table.match(statement):
            table_names.append(match.group(1).lower())

        for table_name in ModuleCtx.CTE_Statement_Table.findall(statement):
            table_names.append(table_name.lower())

    out = (tuple(keywords), tuple(table_names))
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
    The parse of the statement is kept per statement text, while the verdict is reached on every execution
    against the mechanism of the current work.
    """
    keywords, table_names = _parse_statement(statement)

    if not keywords:
        return

    mechanism = _current_mechanism.get()

    if mechanism is None:
        raise WritePathViolation(f'Statement writes outside of every mechanism -> `{statement}`')

    if mechanism == Mechanism.Seed:
        for keyword in keywords:
            if keyword not in ModuleCtx.Seed_Statements:
                raise WritePathViolation(f'Seed changes rows with `{keyword}` -> `{statement}`')
        return

    if mechanism in ModuleCtx.Audit_Mechanisms:
        return

    for table_name in table_names:
        if table_name in ModuleCtx.Audit_Tables:
            raise WritePathViolation(f'Mechanism `{mechanism}` writes to audit table `{table_name}` -> `{statement}`')

# ################################################################################################################################
# ################################################################################################################################
