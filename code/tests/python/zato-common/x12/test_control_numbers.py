# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import os
import unittest

from tempfile import TemporaryDirectory

# Zato
from zato.x12.control import ControlNumberStore, Kind_Group, Kind_Interchange, Kind_Transaction_Set

# ################################################################################################################################
# ################################################################################################################################

class TestControlNumberStore(unittest.TestCase):

    maxDiff = None

    def setUp(self) -> None:
        self._directory = TemporaryDirectory()
        self.path = os.path.join(self._directory.name, 'control-numbers.db')

    def tearDown(self) -> None:
        self._directory.cleanup()

    def test_sequence_starts_at_one_and_advances(self) -> None:
        store = ControlNumberStore(self.path)

        numbers:'list[int]' = []

        for _ in range(3):
            number = store.next_number('SENDERID', 'RECEIVERID', Kind_Interchange)
            numbers.append(number)

        self.assertEqual(numbers, [1, 2, 3])

        store.close()

    def test_sequences_are_independent_per_kind(self) -> None:
        store = ControlNumberStore(self.path)

        interchange_number = store.next_number('SENDERID', 'RECEIVERID', Kind_Interchange)
        group_number = store.next_number('SENDERID', 'RECEIVERID', Kind_Group)
        set_number = store.next_number('SENDERID', 'RECEIVERID', Kind_Transaction_Set)

        # Each kind runs its own sequence, all starting at 1.
        self.assertEqual(interchange_number, 1)
        self.assertEqual(group_number, 1)
        self.assertEqual(set_number, 1)

        store.close()

    def test_sequences_are_independent_per_pair(self) -> None:
        store = ControlNumberStore(self.path)

        first = store.next_number('SENDERID', 'RECEIVERID', Kind_Interchange)
        second = store.next_number('SENDERID', 'RECEIVERID', Kind_Interchange)
        other_pair = store.next_number('SENDERID', 'OTHERRECEIVER', Kind_Interchange)

        self.assertEqual(first, 1)
        self.assertEqual(second, 2)
        self.assertEqual(other_pair, 1)

        store.close()

    def test_sequence_survives_reopening(self) -> None:
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

    def test_inbound_duplicate_detection(self) -> None:
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

    def test_inbound_duplicates_survive_reopening(self) -> None:
        store = ControlNumberStore(self.path)

        _ = store.observe_inbound('SENDERID', 'RECEIVERID', Kind_Interchange, 905)
        store.close()

        store = ControlNumberStore(self.path)
        is_duplicate = store.observe_inbound('SENDERID', 'RECEIVERID', Kind_Interchange, 905)

        self.assertTrue(is_duplicate)

        store.close()

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = unittest.main()

# ################################################################################################################################
# ################################################################################################################################
