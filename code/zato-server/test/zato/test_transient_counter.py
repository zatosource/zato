# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import main, TestCase

# Zato
from zato.common.test import rand_int, rand_string
from zato.server.connection.kvdb.api import ObjectCtx, CounterRepo
from zato.server.connection.kvdb.core import KVDB

# ################################################################################################################################
# ################################################################################################################################

class TransientCounterTestCase(TestCase):

    def test_repo_init(self):

        name1 = rand_string()
        name2 = rand_string()

        max_value1 = rand_int()
        max_value2 = rand_int()

        allow_negative1 = False
        allow_negative2 = True

        repo1 = CounterRepo(name1, max_value1, allow_negative1)
        repo2 = CounterRepo(name2, max_value2, allow_negative2)

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

        repo = CounterRepo(repo_name)

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

        repo = CounterRepo(repo_name, max_value=max_value)

        # By multiplying we ensure that max_value is reached ..
        for x in range(max_value * 2):
            value = repo.incr(key_name)

        # .. yet, it will never be exceeded.
        self.assertEqual(value, max_value)

# ################################################################################################################################

    def test_repo_decr(self):
        repo_name = rand_string()
        key_name = rand_string()

        repo = CounterRepo(repo_name)

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

        repo = CounterRepo(repo_name, allow_negative=allow_negative)

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

        repo = CounterRepo(repo_name, allow_negative=allow_negative)

        # Add new items ..
        for x in range(total_increases):
            repo.incr(key_name)

        # By multiplying we ensure that we decrement it below zero ..
        for x in range(total_decreases):
            value = repo.decr(key_name)

        # .. and we confirm that the value is zero (remember, allow_negative is True).
        self.assertEqual(value, 0)

# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
