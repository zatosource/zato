# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from datetime import datetime
from random import choice, seed
from unittest import TestCase

# dateutil
from dateutil.parser import parse

# gevent
from gevent import sleep, spawn

# paodate
from paodate import Delta

# Zato
from zato.common.scheduler import Interval, Job
from zato.common.test import is_like_cid, rand_bool, rand_date_utc, rand_int, rand_string

seed()

def get_job(name=None, start_time=None, interval_in_seconds=None, max_runs=None):
    name = name or rand_string()
    start_time = start_time or rand_date_utc()
    interval_in_seconds = interval_in_seconds or rand_int()
    
    return Job(name, start_time, max_runs=max_runs, interval=Interval(in_seconds=interval_in_seconds))

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
        current_run, max_runs = rand_int(count=2)
        cb_kwargs = {rand_string():rand_string()}

        job = Job(name, start_time, cb_kwargs=cb_kwargs, interval=Interval(in_seconds=interval_in_seconds))
        job.current_run = current_run
        job.max_runs = max_runs
        job.max_runs_reached = max_runs_reached

        ctx = job.get_context()
        cid = ctx.pop('cid')

        self.assertTrue(is_like_cid(cid))

        self.assertDictEqual(ctx, {
            'current_run': current_run,
            'interval_in_seconds': interval_in_seconds,
            'name': name,
            'start_time': start_time.isoformat(),
            'max_runs': max_runs,
            'max_runs_reached': max_runs_reached,
            'cb_kwargs': cb_kwargs
        })

    def test_main_loop_keep_running_false(self):

        job = get_job()
        job.keep_running = False

        self.assertTrue(job.main_loop())
        self.assertFalse(job.keep_running)
        self.assertFalse(job.max_runs_reached)

        self.assertEquals(job.current_run, 0)

    def test_main_loop_max_runs_reached(self):

        runs_ctx = []

        def callback(ctx):
            runs_ctx.append(ctx)

        cb_kwargs = {
            rand_string():rand_string(),
            rand_string():rand_string()
        }

        interval_in_seconds = 0.01
        max_runs = choice(range(2, 5))

        job = get_job(interval_in_seconds=interval_in_seconds, max_runs=max_runs)
        job.callback = callback
        job.cb_kwargs = cb_kwargs

        job.main_loop()
        sleep(0.2)

        len_runs_ctx = len(runs_ctx)
        self.assertEquals(len_runs_ctx, max_runs)

        for idx, ctx in enumerate(runs_ctx, 1):
            self.assertEquals(ctx['name'], job.name)
            self.assertEquals(ctx['interval_in_seconds'], job.interval.in_seconds)
            self.assertEquals(ctx['max_runs'], job.max_runs)
            self.assertDictEqual(ctx['cb_kwargs'], job.cb_kwargs)

            self.assertEquals(ctx['interval_in_seconds'], interval_in_seconds)
            self.assertEquals(ctx['max_runs'], max_runs)
            self.assertEquals(ctx['current_run'], idx)
            self.assertDictEqual(ctx['cb_kwargs'], cb_kwargs)

            func = self.assertFalse if idx < len_runs_ctx else self.assertTrue
            func(ctx['max_runs_reached'])

            # Don't check an exact time. Simply parse it out and confirm it's in the past.
            start_time = parse(ctx['start_time'])
            self.assertTrue(start_time < datetime.utcnow())

            self.assertTrue(is_like_cid(ctx['cid']))
