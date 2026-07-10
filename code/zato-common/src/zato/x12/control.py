# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import annotations

# stdlib
import os
import sqlite3
from datetime import datetime, timezone
from typing import NamedTuple

# Zato
from zato.common.defaults import default_env_base_dir

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import intnone, strnone
    intnone = intnone
    strnone = strnone

# ################################################################################################################################
# ################################################################################################################################

# The full listing of sequences one store holds.
sequence_info_list = list['SequenceInfo']

# ################################################################################################################################
# ################################################################################################################################

# The control number kinds a sequence or duplicate check applies to.
Kind_Interchange     = 'interchange'
Kind_Group           = 'group'
Kind_Transaction_Set = 'transaction-set'

# The first number a fresh sequence hands out.
First_Control_Number = 1

# The largest control number an ISA13 can carry - the field is nine digits wide.
Max_Control_Number = 999999999

# The environment variable overriding where the control number database lives.
Env_Control_DB_Path = 'Zato_X12_Control_Numbers_DB_Path'

# The file name of the default control number database, shared by servers and the Dashboard.
_control_db_file_name = 'x12-control-numbers.db'

# ################################################################################################################################
# ################################################################################################################################

_create_sequence_table = """
CREATE TABLE IF NOT EXISTS x12_control_sequence (
    pair           TEXT NOT NULL,
    kind           TEXT NOT NULL,
    next_number    INTEGER NOT NULL,
    last_used      INTEGER,
    last_used_time TEXT,
    PRIMARY KEY (pair, kind)
)
"""

# Columns added to the sequence table after its first release - each is created
# with a guarded ALTER TABLE when an existing database file predates it.
_sequence_table_added_columns = (
    ('last_used',      'INTEGER'),
    ('last_used_time', 'TEXT'),
)

_create_inbound_table = """
CREATE TABLE IF NOT EXISTS x12_inbound_control_number (
    pair           TEXT NOT NULL,
    kind           TEXT NOT NULL,
    control_number INTEGER NOT NULL,
    PRIMARY KEY (pair, kind, control_number)
)
"""

_create_seen_value_table = """
CREATE TABLE IF NOT EXISTS x12_seen_value (
    pair  TEXT NOT NULL,
    kind  TEXT NOT NULL,
    value TEXT NOT NULL,
    PRIMARY KEY (pair, kind, value)
)
"""

# ################################################################################################################################
# ################################################################################################################################

def _pair_key(sender:'str', receiver:'str') -> 'str':
    """ Builds the storage key of one sender-receiver identifier pair.
    """
    out = f'{sender}:{receiver}'
    return out

# ################################################################################################################################

def get_control_db_path() -> 'str':
    """ Returns the full path to the control number database file, shared by servers
    and the Dashboard - an environment variable overrides the default location.
    """
    if env_path := os.environ.get(Env_Control_DB_Path):
        return env_path

    # The environment directory may not exist yet, e.g. in freshly created environments.
    os.makedirs(default_env_base_dir, exist_ok=True)

    out = os.path.join(default_env_base_dir, _control_db_file_name)
    return out

# ################################################################################################################################

def _utc_now_iso() -> 'str':
    """ Returns the current UTC time as an ISO 8601 string.
    """
    now = datetime.now(timezone.utc)

    out = now.isoformat()
    return out

# ################################################################################################################################
# ################################################################################################################################

class SequenceInfo(NamedTuple):
    """ One outbound control number sequence - the sender-receiver pair, the kind
    (interchange, group or transaction set), the next number the sequence will hand out
    and the number last handed out along with when that happened.
    """
    sender: str
    receiver: str
    kind: str
    next_number: int
    last_used: 'intnone'
    last_used_time: 'strnone'

# ################################################################################################################################
# ################################################################################################################################

class ControlNumberStore:
    """ Persisted control number machinery - outbound sequences per sender-receiver
    identifier pair, so restarts never reuse a number, and inbound duplicate detection
    on interchange, group and transaction set control numbers.
    """

    def __init__(self, path:'str') -> 'None':
        self.path = path
        self._connection = sqlite3.connect(path)

        # All the tables are created idempotently on every open ..
        with self._connection:
            _ = self._connection.execute(_create_sequence_table)
            _ = self._connection.execute(_create_inbound_table)
            _ = self._connection.execute(_create_seen_value_table)

        # .. and database files predating the last-used columns receive them in place.
        self._add_missing_columns()

# ################################################################################################################################

    def _add_missing_columns(self) -> 'None':
        """ Adds the columns that were introduced after the sequence table's first release
        to database files created before them - a guarded ALTER TABLE per column.
        """

        # The names of the columns the file has today
        existing:'list[str]' = []

        cursor = self._connection.execute('PRAGMA table_info(x12_control_sequence)')

        for row in cursor.fetchall():
            column_name = row[1]
            existing.append(column_name)

        # Add whichever of the newer columns are not there yet.
        with self._connection:
            for column_name, column_type in _sequence_table_added_columns:
                if column_name not in existing:
                    _ = self._connection.execute(f'ALTER TABLE x12_control_sequence ADD COLUMN {column_name} {column_type}')

# ################################################################################################################################

    def next_number(self, sender:'str', receiver:'str', kind:'str') -> 'int':
        """ Returns the next control number of the given kind for the sender-receiver pair
        and advances the persisted sequence, so a number is never handed out twice.
        The number handed out is remembered as the last one used, with its timestamp.
        """
        pair = _pair_key(sender, receiver)
        now_iso = _utc_now_iso()

        # The whole read-and-advance step is one transaction ..
        with self._connection:
            cursor = self._connection.execute(
                'SELECT next_number FROM x12_control_sequence WHERE pair = ? AND kind = ?',
                (pair, kind))
            row = cursor.fetchone()

            # .. a fresh pair starts a new sequence ..
            if row is None:
                out = First_Control_Number
                _ = self._connection.execute(
                    'INSERT INTO x12_control_sequence (pair, kind, next_number, last_used, last_used_time) ' \
                    'VALUES (?, ?, ?, ?, ?)',
                    (pair, kind, out + 1, out, now_iso))

            # .. and an existing one is advanced in place.
            else:
                out = row[0]
                _ = self._connection.execute(
                    'UPDATE x12_control_sequence SET next_number = ?, last_used = ?, last_used_time = ? ' \
                    'WHERE pair = ? AND kind = ?',
                    (out + 1, out, now_iso, pair, kind))

        return out

# ################################################################################################################################

    def set_next(self, sender:'str', receiver:'str', kind:'str', next_number:'int') -> 'None':
        """ Sets the next control number a sequence will hand out - the operator action
        behind "the partner says they already received this number, bump the sequence".
        The last-used information stays untouched because it reports what actually went out.
        """
        pair = _pair_key(sender, receiver)

        # The check and the write are one transaction ..
        with self._connection:
            cursor = self._connection.execute(
                'SELECT next_number FROM x12_control_sequence WHERE pair = ? AND kind = ?',
                (pair, kind))
            row = cursor.fetchone()

            # .. a pair seen for the first time starts its sequence at the given number ..
            if row is None:
                _ = self._connection.execute(
                    'INSERT INTO x12_control_sequence (pair, kind, next_number) VALUES (?, ?, ?)',
                    (pair, kind, next_number))

            # .. and an existing sequence is repositioned in place.
            else:
                _ = self._connection.execute(
                    'UPDATE x12_control_sequence SET next_number = ? WHERE pair = ? AND kind = ?',
                    (next_number, pair, kind))

# ################################################################################################################################

    def get_sequences(self) -> 'sequence_info_list':
        """ Returns all the outbound sequences the store holds, ordered by pair and kind -
        one entry per sender-receiver pair and control number level.
        """

        # Our response to produce
        out:'sequence_info_list' = []

        cursor = self._connection.execute(
            'SELECT pair, kind, next_number, last_used, last_used_time FROM x12_control_sequence ORDER BY pair, kind')

        for row in cursor.fetchall():

            pair = row[0]

            # The pair key glues the identifiers with a colon and X12 identifiers never contain one.
            sender, _, receiver = pair.partition(':')

            info = SequenceInfo(sender, receiver, row[1], row[2], row[3], row[4])
            out.append(info)

        return out

# ################################################################################################################################

    def observe_inbound(self, sender:'str', receiver:'str', kind:'str', control_number:'int') -> 'bool':
        """ Records an inbound control number and reports whether it was already seen -
        True means the number is a duplicate of an earlier interchange, group or set.
        """
        pair = _pair_key(sender, receiver)

        # The check and the recording are one transaction ..
        with self._connection:
            cursor = self._connection.execute(
                'SELECT 1 FROM x12_inbound_control_number WHERE pair = ? AND kind = ? AND control_number = ?',
                (pair, kind, control_number))
            row = cursor.fetchone()

            # .. a number seen before is a duplicate ..
            if row is not None:
                return True

            # .. and a new one is recorded for the checks that follow.
            _ = self._connection.execute(
                'INSERT INTO x12_inbound_control_number (pair, kind, control_number) VALUES (?, ?, ?)',
                (pair, kind, control_number))

        return False

# ################################################################################################################################

    def observe_value(self, sender:'str', receiver:'str', kind:'str', value:'str') -> 'bool':
        """ Records a business value of the given kind - an SSCC-18 or an invoice number -
        and reports whether it was already seen for the sender-receiver pair,
        True meaning the value is a duplicate.
        """
        pair = _pair_key(sender, receiver)

        # The check and the recording are one transaction ..
        with self._connection:
            cursor = self._connection.execute(
                'SELECT 1 FROM x12_seen_value WHERE pair = ? AND kind = ? AND value = ?',
                (pair, kind, value))
            row = cursor.fetchone()

            # .. a value seen before is a duplicate ..
            if row is not None:
                return True

            # .. and a new one is recorded for the checks that follow.
            _ = self._connection.execute(
                'INSERT INTO x12_seen_value (pair, kind, value) VALUES (?, ?, ?)',
                (pair, kind, value))

        return False

# ################################################################################################################################

    def close(self) -> 'None':
        """ Closes the underlying database connection.
        """
        self._connection.close()

# ################################################################################################################################
# ################################################################################################################################
