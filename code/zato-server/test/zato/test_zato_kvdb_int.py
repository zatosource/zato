# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import main, TestCase

# Zato
from zato.common.test import rand_int, rand_string
from zato.server.connection.kvdb.api import IntData, NumberRepo

# ################################################################################################################################
# ################################################################################################################################


# ################################################################################################################################
# ################################################################################################################################

sync_threshold = 1
sync_interval  = 1

# ################################################################################################################################
# ################################################################################################################################

class NumberTestCase(TestCase):


    def test_repo_init(self):

        name1 = rand_string()
        name2 = rand_string()

        max_value1 = rand_int()
        max_value2 = rand_int()

        allow_negative1 = False
        allow_negative2 = True

        repo1 = NumberRepo(name1, sync_threshold, sync_interval, max_value1, allow_negative1)
        repo2 = NumberRepo(name2, sync_threshold, sync_interval, max_value2, allow_negative2)

        self.assertEqual(repo1.name, name1)
        self.assertEqual(repo1.max_value, max_value1)
        self.assertEqual(repo1.name, name1)
        self.assertFalse(repo1.allow_negative)

        self.assertEqual(repo2.name, name2)
        self.assertEqual(repo2.max_value, max_value2)
        self.assertEqual(repo2.name, name2)
        self.assertTrue(repo2.allow_negative)

# ################################################################################################################################

    def test_repo_incr(self):
        repo_name = rand_string()
        key_name = rand_string()

        repo = NumberRepo(repo_name, sync_threshold, sync_interval)

        value = repo.incr(key_name)

        self.assertEqual(value, 1)

        value = repo.incr(key_name)
        value = repo.incr(key_name)
        value = repo.incr(key_name)

        self.assertEqual(value, 4)

# ################################################################################################################################

    def test_repo_incr_max_value(self):
        repo_name = rand_string()
        key_name = rand_string()
        max_value = 2

        repo = NumberRepo(repo_name, sync_threshold, sync_interval, max_value=max_value)

        # By multiplying we ensure that max_value is reached ..
        for x in range(max_value * 2):
            value = repo.incr(key_name)

        # .. yet, it will never be exceeded.
        self.assertEqual(value, max_value)

# ################################################################################################################################

    def test_repo_decr(self):
        repo_name = rand_string()
        key_name = rand_string()

        repo = NumberRepo(repo_name, sync_threshold, sync_interval)

        repo.incr(key_name)
        repo.incr(key_name)
        repo.incr(key_name)
        repo.incr(key_name)

        repo.decr(key_name)
        value = repo.decr(key_name)

        self.assertEqual(value, 2)

# ################################################################################################################################

    def test_repo_decr_below_zero_allow_negative_true(self):

        repo_name = rand_string()
        key_name = rand_string()
        allow_negative = True

        len_items = 3

        total_increases = len_items
        total_decreases = len_items * 2
        expected_value = total_increases - total_decreases

        repo = NumberRepo(repo_name, sync_threshold, sync_interval, allow_negative=allow_negative)

        # Add new items ..
        for x in range(total_increases):
            repo.incr(key_name)

        # By multiplying we ensure that we decrement it below zero ..
        for x in range(total_decreases):
            value = repo.decr(key_name)

        # .. and we confirm that the below-zero value is as expected (remember, allow_negative is True).
        self.assertEqual(value, expected_value)

# ################################################################################################################################

    def test_repo_decr_below_zero_allow_negative_false(self):

        repo_name = rand_string()
        key_name = rand_string()
        allow_negative = False

        len_items = 3

        total_increases = len_items
        total_decreases = len_items * 2

        repo = NumberRepo(repo_name, sync_threshold, sync_interval, allow_negative=allow_negative)

        # Add new items ..
        for x in range(total_increases):
            repo.incr(key_name)

        # By multiplying we ensure that we decrement it below zero ..
        for x in range(total_decreases):
            value = repo.decr(key_name)

        # .. and we confirm that the value is zero (remember, allow_negative is True).
        self.assertEqual(value, 0)

# ################################################################################################################################

    def test_repo_get(self):
        repo_name = rand_string()
        key_name = rand_string()

        repo = NumberRepo(repo_name, sync_threshold, sync_interval)

        repo.incr(key_name)
        repo.incr(key_name)
        repo.incr(key_name)

        data = repo.get(key_name) # type: CounterData

        self.assertEqual(data['value'], 3)

# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
