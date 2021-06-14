# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime, timedelta
from unittest import main, TestCase

# Zato
from zato.common.test import rand_int, rand_string
from zato.server.connection.kvdb.api import NumberRepo
from zato.server.connection.kvdb.number import usage_time_format

# ################################################################################################################################
# ################################################################################################################################

sync_threshold = 120_000
sync_interval  = 120_000

# ################################################################################################################################
# ################################################################################################################################

class NumberTestCase(TestCase):

    def xtest_repo_init(self):

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

    def xtest_repo_incr(self):
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

    def xtest_repo_incr_max_value(self):
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

    def xtest_repo_decr(self):
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

    def xtest_repo_decr_below_zero_allow_negative_true(self):

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

    def xtest_repo_decr_below_zero_allow_negative_false(self):

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

    def xtest_repo_get(self):
        repo_name = rand_string()
        key_name = rand_string()

        repo = NumberRepo(repo_name, sync_threshold, sync_interval)

        repo.incr(key_name)
        repo.incr(key_name)
        repo.incr(key_name)

        data = repo.get(key_name) # type: dict

        self.assertEqual(data['value'], 3)

# ################################################################################################################################

    def test_update_key_usage(self):

        repo_name = rand_string()
        key_name = rand_string()

        repo = NumberRepo(repo_name, sync_threshold, sync_interval)

        n_iters = 7

        for x in range(n_iters):
            repo.incr(key_name)

        # Our usage will be stored under keys pointing to the current minute
        # or under one pointing to the previous minute. This is because it is possible
        # that we may start with an .incr in minute, in the very last nano-second, and during one
        # of the subsequent ones it is already another minute. However, because it is only
        # a handful of operations, we assume that they will never take more than one minute.

        current_minute  = datetime.utcnow()
        previous_minute = current_minute - timedelta(minutes=1)

        current_minute  = current_minute.strftime(usage_time_format)
        previous_minute = previous_minute.strftime(usage_time_format)

        data_current_minute  = repo.current_usage.get(current_minute, {})   # type: dict
        data_previous_minute = repo.current_usage.get(previous_minute, {}) # type: dict

        usage_current_minute  = data_current_minute.get(key_name, 0)
        usage_previous_minute = data_previous_minute.get(key_name, 0)

        total_usage = usage_current_minute + usage_previous_minute

        self.assertEqual(total_usage, n_iters)

# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################

