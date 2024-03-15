# -*- coding: utf-8 -*-

"""
Copyright (C) 2021, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
from unittest import main, TestCase

# Zato
from zato.common.util.stats import collect_current_usage

# ################################################################################################################################
# ################################################################################################################################

class StatsTestCase(TestCase):

    def test_collect_current_usage_one_elem(self):

        value1 = 24
        last_timestamp1 = '2021-06-13T19:46:43.910465'
        last_duration1 = 0.216

        data = [{
            'value': value1,
            'last_timestamp': last_timestamp1,
            'last_duration': last_duration1,
        }]

        result = collect_current_usage(data)

        self.assertEqual(result['value'], value1)
        self.assertEqual(result['last_timestamp'], last_timestamp1)
        self.assertEqual(result['last_duration'], last_duration1)

# ################################################################################################################################

    def test_collect_current_usage_multiple_elems(self):

        value1 = 24
        last_timestamp1 = '2021-11-22T11:22:33.445566'
        last_duration1 = 0.216

        value2 = 297
        last_timestamp2 = '2020-10-20T10:20:30.405060'
        last_duration2 = 82

        value3 = 51
        last_timestamp3 = '2022-12-22T12:22:32.425262'
        last_duration3 = 219

        data = [
            {'value': value1, 'last_timestamp': last_timestamp1, 'last_duration': last_duration1},
            {'value': value2, 'last_timestamp': last_timestamp2, 'last_duration': last_duration2},
            {'value': value3, 'last_timestamp': last_timestamp3, 'last_duration': last_duration3},
        ]

        result = collect_current_usage(data)

        self.assertEqual(result['value'], value1 + value2 + value3)
        self.assertEqual(result['last_timestamp'], last_timestamp3)
        self.assertEqual(result['last_duration'], last_duration3)

# ################################################################################################################################
# ################################################################################################################################

if __name__ == '__main__':
    _ = main()

# ################################################################################################################################
# ################################################################################################################################
