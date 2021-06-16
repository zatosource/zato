# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from datetime import datetime, timedelta
from unittest import main, TestCase

# dateutil
from dateutil.rrule import MINUTELY, rrule

# Pandas
import pandas as pd

# Zato
from zato.common.test import rand_int, rand_string
from zato.server.connection.kvdb.api import NumberRepo
from zato.server.connection.kvdb.number import usage_time_format

# ################################################################################################################################
# ################################################################################################################################

utcnow = datetime.utcnow

# ################################################################################################################################
# ################################################################################################################################

sync_threshold = 120_000
sync_interval  = 120_000

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

        current_minute  = utcnow()
        previous_minute = current_minute - timedelta(minutes=1)

        current_minute  = current_minute.strftime(usage_time_format)
        previous_minute = previous_minute.strftime(usage_time_format)

        data_current_minute  = repo.current_usage.get(current_minute, {})  # type: dict
        data_previous_minute = repo.current_usage.get(previous_minute, {}) # type: dict

        usage_current_minute  = data_current_minute.get(key_name, 0)
        usage_previous_minute = data_previous_minute.get(key_name, 0)

        total_usage = usage_current_minute + usage_previous_minute

        self.assertEqual(total_usage, n_iters)

# ################################################################################################################################

    def test_repo_sync_state(self):

        repo_name = rand_string()
        key_name = rand_string()

        repo = NumberRepo(repo_name, sync_threshold, sync_interval)

        #
        # We will create three keys, each for:
        #
        # * Current minute
        # * Previous minute
        # * Previous hour
        # * Previous day
        #
        # After we have synchronised stated, the ones for the previous day and hour
        # should no longer exist because sync_state leaves only the last hour's
        # worth of data.
        #

        current_minute  = utcnow()
        previous_minute = current_minute - timedelta(minutes=1)
        previous_hour   = current_minute - timedelta(hours=1, minutes=1)
        previous_day    = current_minute - timedelta(days=1)

        current_minute  = current_minute.strftime(usage_time_format)
        previous_minute = previous_minute.strftime(usage_time_format)
        previous_hour   = previous_hour.strftime(usage_time_format)
        previous_day    = previous_day.strftime(usage_time_format)

        usage_current_minute  = 111
        usage_previous_minute = 222
        usage_previous_hour   = 333
        usage_previous_day    = 444

        repo.current_usage[current_minute]  = {key_name: usage_current_minute}
        repo.current_usage[previous_minute] = {key_name: usage_previous_minute}
        repo.current_usage[previous_hour]   = {key_name: usage_previous_hour}
        repo.current_usage[previous_day]    = {key_name: usage_previous_day}

        # This should delete everything but the current and previous minutes
        repo.sync_state()

        repo_usage_current_minute  = repo.current_usage[current_minute]  # type: dict
        repo_usage_previous_minute = repo.current_usage[previous_minute] # type: dict

        key_usage_current_minute  = repo_usage_current_minute[key_name]
        key_usage_previous_minute  = repo_usage_previous_minute[key_name]

        self.assertEqual(key_usage_current_minute, usage_current_minute)
        self.assertEqual(key_usage_previous_minute, usage_previous_minute)

# ################################################################################################################################

    def xtest_repo_get_usage_by_key(self):

        # ZZZ This is temporary
        usage_time_format = '%Y-%m-%d %H:%M:00'

        # We will create usage data for that many keys
        how_many_keys = 3

        # This is where the usage data will be kept
        current_usage = {}

        #
        # We want to generate data for a particular hour and for some minutes later or earlier
        # that that hour. We expect only for data for this specific hour to be taken into account.
        #

        #
        # We choose the following:
        #
        # * Max minute to be taken into account (aka current minute) = 2021-06-13 11:22
        # * Min minute to be taken into account = max minute - 59 minutes (a total one hour because we include the current minute)
        # * Additional later data (to be ignored) = values for 11:23 or later
        # * Additional earlier data (to be ignored) = values for 10:22 or earlier
        #

        max_minute_str = '2021-06-13 11:22:00'
        max_minute = datetime.strptime(max_minute_str, usage_time_format)

        min_minute = max_minute - timedelta(minutes=3) # type: datetime
        min_minute_str = min_minute.strftime(usage_time_format)

        additional_later_limit   = max_minute + timedelta(hours=19)
        additional_earlier_limit = min_minute - timedelta(hours=27)

        #
        # Now, we need to create per-minute buckets spanning from
        # additional_earlier_limit -> min_minute -> max_minute up to additional_later_limit.
        #
        start = additional_earlier_limit
        stop  = additional_later_limit

        elems = []
        for elem in rrule(MINUTELY, dtstart=start, until=stop): # type: datetime

            # Skip every other minute to simulate the fact that not all minutes will have any data
            if elem.minute % 2 == 0:
                continue

            elems.append(elem)

        #
        # We need to assign usage data for each bucket. The usage for each key
        # in each minute is the same as the key index.
        #
        # For instance, within each per-minute bucket, key1's usage will be 1,
        # key2's usage will be 2, key3's usage will 3 etc.
        #

        for elem_idx, elem in enumerate(elems):

            elem_str = elem.strftime(usage_time_format)
            per_minute_usage = current_usage.setdefault(elem_str, {})

            for loop_idx, key_idx in enumerate(range(1, how_many_keys+1)):
                key_name = 'key{}'.format(key_idx)

                key_values = []

                for key_value in range(1, key_idx+1):
                    key_values.append(key_value)

                per_minute_usage[key_name] = key_values

        pd_range = pd.date_range(start=start, end=stop, freq='min')
        f = pd.DataFrame(current_usage).transpose()
        f.index = pd.DatetimeIndex(f.index)
        f = f.reindex(pd_range, fill_value=0)
        f.index.name = 'minute_bucket'

        period_data = f[min_minute_str:max_minute_str] # type: pd.DataFrame

        def calc_stats(row):
            print()
            for key in row.keys():

                values = row[key]
                values = [values] if not isinstance(values, list) else values

                #row[key] = [min(values), max(values), sum(values)]

                #row['{}_min'.format(key)] = min(values)
                #row['aaa'] = 'bbb'

                print(111, row.assign)

                return row

            print()

        #period_data.apply(calc_stats, axis=1)

        #period_data['aaa'] = '111'

        print()
        print(period_data)
        print()

        #print(111, f.index.min())
        #print(222, f.index.max())
        #print()

        #pd_range = pd.date_range(start=f.index.min(), end=f.index.max(), freq='min')
        #f2 = pd.DataFrame(f, index=pd_range)
        #print(f)

# ################################################################################################################################

if __name__ == '__main__':
    main()

# ################################################################################################################################
