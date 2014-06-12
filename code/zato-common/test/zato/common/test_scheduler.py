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
from zato.common.scheduler import Interval, Job
from zato.common.test import is_like_cid, rand_bool, rand_date_utc, rand_int, rand_string

class IntervalTestCase(TestCase):

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

class JobTestCase(TestCase):
    def test_get_context(self):
        name = rand_string()
        start_time = rand_date_utc()
        interval_in_seconds = rand_int()
        max_runs_reached = rand_bool()
        current_runs, failure_runs, success_runs = rand_int(count=3)

        job = Job(name, start_time, Interval(in_seconds=interval_in_seconds))
        job.current_runs = current_runs
        job.failure_runs = failure_runs
        job.success_runs = success_runs

        ctx = job.get_context()
        cid = ctx.pop('cid')

        self.assertTrue(is_like_cid(cid))

        self.assertDictEqual(ctx, {
            'current_runs': current_runs,
            'failure_runs': failure_runs,
            'success_runs': success_runs,
            'interval_in_seconds': interval_in_seconds,
            'name': name,
            'start_time': start_time.isoformat(),
            'max_runs_reached': max_runs_reached
        })