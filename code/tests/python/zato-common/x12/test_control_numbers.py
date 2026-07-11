# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import sqlite3
import unittest

from tempfile import TemporaryDirectory

# Zato
from zato.x12.control import ControlNumberStore, Env_Control_DB_Path, Kind_Group, Kind_Interchange, Kind_Transaction_Set, \
     get_control_db_path

# ################################################################################################################################
# ################################################################################################################################

class TestControlNumberStore(unittest.TestCase):

    maxDiff = None

    def setUp(self) -> 'None':
        self._directory = TemporaryDirectory()
        self.path = os.path.join(self._directory.name, 'control-numbers.db')

# ################################################################################################################################

    def tearDown(self) -> 'None':
        self._directory.cleanup()

# ################################################################################################################################

    def test_sequence_starts_at_one_and_advances(self) -> 'None':
        store = ControlNumberStore(self.path)

        numbers:'list[int]' = []

        for _ in range(3):
            number = store.next_number('SENDERID', 'RECEIVERID', Kind_Interchange)
            numbers.append(number)

        self.assertEqual(numbers, [1, 2, 3])

        store.close()

# ################################################################################################################################

    def test_sequences_are_independent_per_kind(self) -> 'None':
        store = ControlNumberStore(self.path)

        interchange_number = store.next_number('SENDERID', 'RECEIVERID', Kind_Interchange)
        group_number = store.next_number('SENDERID', 'RECEIVERID', Kind_Group)
        set_number = store.next_number('SENDERID', 'RECEIVERID', Kind_Transaction_Set)

        # Each kind runs its own sequence, all starting at 1.
        self.assertEqual(interchange_number, 1)
        self.assertEqual(group_number, 1)
        self.assertEqual(set_number, 1)

        store.close()

# ################################################################################################################################

    def test_sequences_are_independent_per_pair(self) -> 'None':
        store = ControlNumberStore(self.path)

        first = store.next_number('SENDERID', 'RECEIVERID', Kind_Interchange)
        second = store.next_number('SENDERID', 'RECEIVERID', Kind_Interchange)
        other_pair = store.next_number('SENDERID', 'OTHERRECEIVER', Kind_Interchange)

        self.assertEqual(first, 1)
        self.assertEqual(second, 2)
        self.assertEqual(other_pair, 1)

        store.close()

# ################################################################################################################################

    def test_sequence_survives_reopening(self) -> 'None':
        store = ControlNumberStore(self.path)

        _ = store.next_number('SENDERID', 'RECEIVERID', Kind_Interchange)
        _ = store.next_number('SENDERID', 'RECEIVERID', Kind_Interchange)
        store.close()

        # A new store over the same file continues where the previous one stopped,
        # so a restart never reuses a control number.
        store = ControlNumberStore(self.path)
        number = store.next_number('SENDERID', 'RECEIVERID', Kind_Interchange)

        self.assertEqual(number, 3)

        store.close()

# ################################################################################################################################

    def test_inbound_duplicate_detection(self) -> 'None':
        store = ControlNumberStore(self.path)

        # The first time a number arrives it is not a duplicate ..
        is_duplicate = store.observe_inbound('SENDERID', 'RECEIVERID', Kind_Interchange, 905)
        self.assertFalse(is_duplicate)

        # .. the second time it is ..
        is_duplicate = store.observe_inbound('SENDERID', 'RECEIVERID', Kind_Interchange, 905)
        self.assertTrue(is_duplicate)

        # .. while another number, kind or pair stays unaffected.
        is_duplicate = store.observe_inbound('SENDERID', 'RECEIVERID', Kind_Interchange, 906)
        self.assertFalse(is_duplicate)

        is_duplicate = store.observe_inbound('SENDERID', 'RECEIVERID', Kind_Group, 905)
        self.assertFalse(is_duplicate)

        is_duplicate = store.observe_inbound('SENDERID', 'OTHERRECEIVER', Kind_Interchange, 905)
        self.assertFalse(is_duplicate)

        store.close()

# ################################################################################################################################

    def test_inbound_duplicates_survive_reopening(self) -> 'None':
        store = ControlNumberStore(self.path)

        _ = store.observe_inbound('SENDERID', 'RECEIVERID', Kind_Interchange, 905)
        store.close()

        store = ControlNumberStore(self.path)
        is_duplicate = store.observe_inbound('SENDERID', 'RECEIVERID', Kind_Interchange, 905)

        self.assertTrue(is_duplicate)

        store.close()

# ################################################################################################################################

    def test_next_number_records_last_used(self) -> 'None':
        store = ControlNumberStore(self.path)

        _ = store.next_number('SENDERID', 'RECEIVERID', Kind_Interchange)
        _ = store.next_number('SENDERID', 'RECEIVERID', Kind_Interchange)

        sequences = store.get_sequences()

        self.assertEqual(len(sequences), 1)

        info = sequences[0]

        self.assertEqual(info.sender, 'SENDERID')
        self.assertEqual(info.receiver, 'RECEIVERID')
        self.assertEqual(info.kind, Kind_Interchange)
        self.assertEqual(info.next_number, 3)

        # The last number handed out was 2 and its timestamp is an ISO UTC string.
        self.assertEqual(info.last_used, 2)
        self.assertIsNotNone(info.last_used_time)
        self.assertIn('T', info.last_used_time)
        self.assertIn('+00:00', info.last_used_time)

        store.close()

# ################################################################################################################################

    def test_get_sequences_is_ordered_and_complete(self) -> 'None':
        store = ControlNumberStore(self.path)

        _ = store.next_number('SENDERID', 'RECEIVERID', Kind_Interchange)
        _ = store.next_number('SENDERID', 'RECEIVERID', Kind_Group)
        _ = store.next_number('AAASENDER', 'RECEIVERID', Kind_Transaction_Set)

        sequences = store.get_sequences()

        # The listing is ordered by pair and kind.
        self.assertEqual(len(sequences), 3)

        self.assertEqual(sequences[0].sender, 'AAASENDER')
        self.assertEqual(sequences[0].kind, Kind_Transaction_Set)

        self.assertEqual(sequences[1].sender, 'SENDERID')
        self.assertEqual(sequences[1].kind, Kind_Group)

        self.assertEqual(sequences[2].sender, 'SENDERID')
        self.assertEqual(sequences[2].kind, Kind_Interchange)

        store.close()

# ################################################################################################################################

    def test_set_next_repositions_a_sequence(self) -> 'None':
        store = ControlNumberStore(self.path)

        _ = store.next_number('SENDERID', 'RECEIVERID', Kind_Interchange)
        store.set_next('SENDERID', 'RECEIVERID', Kind_Interchange, 500)

        number = store.next_number('SENDERID', 'RECEIVERID', Kind_Interchange)

        self.assertEqual(number, 500)

        store.close()

# ################################################################################################################################

    def test_set_next_keeps_last_used_untouched(self) -> 'None':
        store = ControlNumberStore(self.path)

        _ = store.next_number('SENDERID', 'RECEIVERID', Kind_Interchange)
        store.set_next('SENDERID', 'RECEIVERID', Kind_Interchange, 500)

        info = store.get_sequences()[0]

        # The next number moved but what actually went out did not change.
        self.assertEqual(info.next_number, 500)
        self.assertEqual(info.last_used, 1)
        self.assertIsNotNone(info.last_used_time)

        store.close()

# ################################################################################################################################

    def test_set_next_starts_a_new_sequence(self) -> 'None':
        store = ControlNumberStore(self.path)

        store.set_next('SENDERID', 'RECEIVERID', Kind_Group, 77)

        info = store.get_sequences()[0]

        # A sequence created by hand has no last-used information yet.
        self.assertEqual(info.next_number, 77)
        self.assertIsNone(info.last_used)
        self.assertIsNone(info.last_used_time)

        number = store.next_number('SENDERID', 'RECEIVERID', Kind_Group)
        self.assertEqual(number, 77)

        store.close()

# ################################################################################################################################

    def test_set_next_survives_reopening(self) -> 'None':
        store = ControlNumberStore(self.path)

        store.set_next('SENDERID', 'RECEIVERID', Kind_Interchange, 12345)
        store.close()

        store = ControlNumberStore(self.path)
        number = store.next_number('SENDERID', 'RECEIVERID', Kind_Interchange)

        self.assertEqual(number, 12345)

        store.close()

# ################################################################################################################################

    def test_old_schema_receives_last_used_columns(self) -> 'None':

        # Build a database file the way the first release did, without the last-used columns.
        connection = sqlite3.connect(self.path)

        with connection:
            _ = connection.execute("""
            CREATE TABLE x12_control_sequence (
                pair        TEXT NOT NULL,
                kind        TEXT NOT NULL,
                next_number INTEGER NOT NULL,
                PRIMARY KEY (pair, kind)
            )
            """)
            _ = connection.execute(
                'INSERT INTO x12_control_sequence (pair, kind, next_number) VALUES (?, ?, ?)',
                ('SENDERID:RECEIVERID', Kind_Interchange, 42))

        connection.close()

        # Opening the store adds the missing columns and keeps the existing data.
        store = ControlNumberStore(self.path)

        info = store.get_sequences()[0]

        self.assertEqual(info.sender, 'SENDERID')
        self.assertEqual(info.receiver, 'RECEIVERID')
        self.assertEqual(info.next_number, 42)
        self.assertIsNone(info.last_used)
        self.assertIsNone(info.last_used_time)

        # The migrated sequence keeps advancing and starts tracking last-used information.
        number = store.next_number('SENDERID', 'RECEIVERID', Kind_Interchange)
        self.assertEqual(number, 42)

        info = store.get_sequences()[0]
        self.assertEqual(info.last_used, 42)
        self.assertIsNotNone(info.last_used_time)

        store.close()

# ################################################################################################################################

    def test_control_db_path_env_override(self) -> 'None':

        previous = os.environ.get(Env_Control_DB_Path)
        os.environ[Env_Control_DB_Path] = self.path

        try:
            self.assertEqual(get_control_db_path(), self.path)
        finally:
            if previous is None:
                del os.environ[Env_Control_DB_Path]
            else:
                os.environ[Env_Control_DB_Path] = previous

        # Without the override the default lives under the environment's base directory.
        default_path = get_control_db_path()
        self.assertTrue(default_path.endswith('x12-control-numbers.db'))

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
