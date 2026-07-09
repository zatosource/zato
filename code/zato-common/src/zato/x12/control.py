# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import annotations

# stdlib
import sqlite3

# ################################################################################################################################
# ################################################################################################################################

# The control number kinds a sequence or duplicate check applies to.
Kind_Interchange     = 'interchange'
Kind_Group           = 'group'
Kind_Transaction_Set = 'transaction-set'

# The first number a fresh sequence hands out.
First_Control_Number = 1

# ################################################################################################################################
# ################################################################################################################################

_create_sequence_table = """
CREATE TABLE IF NOT EXISTS x12_control_sequence (
    pair        TEXT NOT NULL,
    kind        TEXT NOT NULL,
    next_number INTEGER NOT NULL,
    PRIMARY KEY (pair, kind)
)
"""

_create_inbound_table = """
CREATE TABLE IF NOT EXISTS x12_inbound_control_number (
    pair           TEXT NOT NULL,
    kind           TEXT NOT NULL,
    control_number INTEGER NOT NULL,
    PRIMARY KEY (pair, kind, control_number)
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
# ################################################################################################################################

class ControlNumberStore:
    """ Persisted control number machinery - outbound sequences per sender-receiver
    identifier pair, so restarts never reuse a number, and inbound duplicate detection
    on interchange, group and transaction set control numbers.
    """

    def __init__(self, path:'str') -> 'None':
        self.path = path
        self._connection = sqlite3.connect(path)

        # Both tables are created idempotently on every open.
        with self._connection:
            _ = self._connection.execute(_create_sequence_table)
            _ = self._connection.execute(_create_inbound_table)

# ################################################################################################################################

    def next_number(self, sender:'str', receiver:'str', kind:'str') -> 'int':
        """ Returns the next control number of the given kind for the sender-receiver pair
        and advances the persisted sequence, so a number is never handed out twice.
        """
        pair = _pair_key(sender, receiver)

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
                    'INSERT INTO x12_control_sequence (pair, kind, next_number) VALUES (?, ?, ?)',
                    (pair, kind, out + 1))

            # .. and an existing one is advanced in place.
            else:
                out = row[0]
                _ = self._connection.execute(
                    'UPDATE x12_control_sequence SET next_number = ? WHERE pair = ? AND kind = ?',
                    (out + 1, pair, kind))

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

    def close(self) -> 'None':
        """ Closes the underlying database connection.
        """
        self._connection.close()

# ################################################################################################################################
# ################################################################################################################################
