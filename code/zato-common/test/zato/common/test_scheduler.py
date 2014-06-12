# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from unittest import TestCase

# paodate
from paodate import Delta

# Zato
from zato.common.scheduler import Interval
from zato.common.test import rand_int

class TestInterval(TestCase):

    def test_interval_has_in_seconds(self):
        in_seconds = rand_int()
        interval = Interval(in_seconds=in_seconds)
        self.assertEquals(interval.in_seconds, in_seconds)

    def test_interval_compute_in_seconds(self):

        for days, hours, minutes, seconds, expected in (
            (55, 83, 69, 75, 5055015.0),
            (31, 2, 6, 23, 2685983.0),
            (68, 55, 57, 82, 6076702.0),
            (0, 69, 42, 12, 250932.0),
            (0, 48, 0, 17, 172817.0),
            (0, 0, 192, 17, 11537.0),
            (0, 0, 7, 0, 420.0),
            (0, 0, 0, 32, 32.0)):

            interval = Interval(days, hours, minutes, seconds)
            self.assertEquals(interval.in_seconds, expected)
