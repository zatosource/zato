# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# The database settings that relax durability. They are held here as data, from which the static scan builds its patterns
# and the refusal tests build the arguments of their containers, so that no source file of the repository spells one of them out.

# stdlib
import re
from dataclasses import dataclass

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import strlist, strtuple

# ################################################################################################################################
# ################################################################################################################################

@dataclass(init=False)
class ForbiddenValue:

    # The name of the setting
    name: str

    # The values of the setting that relax durability
    values: 'strtuple'

forbidden_value_tuple = tuple[ForbiddenValue, ...]

# ################################################################################################################################
# ################################################################################################################################

def _new_value(name:'str', values:'strtuple') -> 'ForbiddenValue':
    out = ForbiddenValue()
    out.name = name
    out.values = values
    return out

# ################################################################################################################################
# ################################################################################################################################

class ModuleCtx:

    # The SQLite pragmas and their values that let a commit return before the write-ahead log is on disk
    SQLite_Pragmas = (
        _new_value('synchronous', ('off', 'normal', '0', '1')),
        _new_value('journal_mode', ('off', 'memory')),
    )

    # The PostgreSQL settings and their values that let a commit return before its record is on disk
    PostgreSQL_Settings = (
        _new_value('synchronous_commit', ('off', 'local', 'remote_write')),
        _new_value('fsync', ('off', 'false', 'no', '0')),
        _new_value('full_page_writes', ('off', 'false', 'no', '0')),
    )

    # The PostgreSQL statements that relax durability whatever value they set
    PostgreSQL_Statements = (
        r'\bunlogged\s+table\b',
        r'\bset\s+unlogged\b',
        r'\bset\s+local\s+synchronous_commit\b',
        r'\balter\s+system\s+set\s+synchronous_commit\b',
        r'\balter\s+(?:database|role|user)\s+\S+\s+set\s+synchronous_commit\b',
    )

    # The value under which a PostgreSQL server is started for a refusal test, one setting at a time
    Server_Refusal_Value = 'off'

    # The setting of a primary that keeps its standbys asynchronous when it is empty
    Synchronous_Standby_Names = 'synchronous_standby_names'

# ################################################################################################################################
# ################################################################################################################################

def _join_values(values:'strtuple') -> 'str':
    escaped = [re.escape(value) for value in values]
    out = '|'.join(escaped)
    return out

# ################################################################################################################################

def _get_sqlite_patterns() -> 'strlist':
    """ Returns the patterns of a pragma statement and of a rusqlite pragma update that set a forbidden value.
    """
    out:'strlist' = []

    for item in ModuleCtx.SQLite_Pragmas:
        values = _join_values(item.values)
        name = re.escape(item.name)

        statement = rf'\bpragma\s+(?:\w+\.)?{name}\s*=\s*[\'"]?(?:{values})\b'
        update = rf'\bpragma_update\s*\([^;]*?[\'"]{name}[\'"]\s*,\s*[\'"]?(?:{values})\b'

        out.append(statement)
        out.append(update)

    return out

# ################################################################################################################################

def _get_postgresql_patterns() -> 'strlist':
    """ Returns the patterns of an assignment of a forbidden value in SQL, in a configuration file or on a command line.
    """
    out:'strlist' = []

    for item in ModuleCtx.PostgreSQL_Settings:
        values = _join_values(item.values)
        name = re.escape(item.name)

        assignment = rf'\b{name}\s*(?:=|\bto\b)\s*[\'"]?(?:{values})\b'
        out.append(assignment)

    out.extend(ModuleCtx.PostgreSQL_Statements)

    return out

# ################################################################################################################################

def get_forbidden_patterns() -> 'list[re.Pattern[str]]':
    """ Returns every pattern of a forbidden durability setting, compiled without regard to case.
    """
    sources = _get_sqlite_patterns() + _get_postgresql_patterns()

    out = [re.compile(source, re.IGNORECASE) for source in sources]
    return out

# ################################################################################################################################

def get_server_refusal_arguments() -> 'strlist':
    """ Returns each command-line option that starts PostgreSQL with one of its durability settings turned off,
    for the tests that assert that Zato refuses such a server.
    """
    out:'strlist' = []

    for item in ModuleCtx.PostgreSQL_Settings:
        if item.name != 'synchronous_commit':
            argument = f'{item.name}={ModuleCtx.Server_Refusal_Value}'
            out.append(argument)

    return out

# ################################################################################################################################
# ################################################################################################################################
