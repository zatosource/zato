# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from datetime import datetime, timedelta
from random import choice, seed
from unittest import TestCase

# calllib
from calllib import apply

# dateutil
from dateutil.parser import parse

# gevent
from gevent import sleep, spawn

# mock
from mock import patch

# paodate
from paodate import Delta

# Zato
from zato.common.scheduler import Interval, Job, Scheduler
from zato.common.test import is_like_cid, rand_bool, rand_date_utc, rand_int, rand_string

seed()

class RLock(object):
    def __init__(self):
        self.called = 0

    def __enter__(self):
        self.called += 1

    def __exit__(self, exc_type, exc_val, exc_tb):
        return True

def dummy_callback(*args, **kwargs):
    pass

def get_job(name=None, start_time=None, interval_in_seconds=None, max_runs=None, callback=None):
    name = name or rand_string()
    start_time = start_time or rand_date_utc()
    interval_in_seconds = interval_in_seconds or rand_int()
    callback = callback or dummy_callback
    
    return Job(name, start_time, Interval(in_seconds=interval_in_seconds), callback, max_runs=max_runs)

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

    def check_ctx(self, ctx, job, interval_in_seconds, max_runs, idx, cb_kwargs, len_runs_ctx):

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

        self.assertTrue(job.main_loop())
        sleep(0.2)

        len_runs_ctx = len(runs_ctx)
        self.assertEquals(len_runs_ctx, max_runs)

        self.assertFalse(job.keep_running)
        self.assertIs(job.callback, callback)

        for idx, ctx in enumerate(runs_ctx, 1):
            self.check_ctx(ctx, job, interval_in_seconds, max_runs, idx, cb_kwargs, len_runs_ctx)

    def test_main_loop_sleep_spawn_called(self):

        wait_time = 0.2

        sleep_history = []
        spawn_history = []

        def sleep(value):
            if value != wait_time:
                sleep_history.append(value)

        def spawn(*args):
            spawn_history.append(args)

        with patch('gevent.sleep', sleep):
            with patch('gevent.spawn', spawn):
                interval_in_seconds = 0.01
                max_runs = choice(range(2, 5))

                cb_kwargs = {
                    rand_string():rand_string(),
                    rand_string():rand_string()
                }

                job = get_job(interval_in_seconds=interval_in_seconds, max_runs=max_runs)
                job.cb_kwargs = cb_kwargs

                self.assertTrue(job.main_loop())
                sleep(0.2)

                self.assertEquals(max_runs, len(sleep_history))
                self.assertEquals(max_runs, len(spawn_history))

                for item in sleep_history:
                    self.assertEquals(interval_in_seconds, item)

                for idx, (apply_func, callback, ctx_dict) in enumerate(spawn_history, 1):
                    self.check_ctx(ctx_dict['ctx'], job, interval_in_seconds, max_runs, idx, cb_kwargs, len(spawn_history))
                    self.assertIs(apply_func, apply)
                    self.assertIs(callback, dummy_callback)

    def test_run(self):

        data = {'main_loop_called':False, 'sleep': False}

        def main_loop():
            data['main_loop_called'] = True

        def sleep(value):
            data['sleep'] = value # Should not be executed if start_time is None

        start_time1 = None
        start_time2 = datetime.utcnow() + timedelta(seconds=1.2)

        with patch('gevent.sleep', sleep):
            for start_time in start_time1, start_time2:

                job = get_job()
                job.main_loop = main_loop
                job.start_time = start_time
        
                job.run()
        
                self.assertTrue(data['main_loop_called'])

                if start_time:
                    self.assertEquals(data['sleep'], 1)

                else:
                    self.assertFalse(data['sleep'])

    def test_hash_eq(self):
        job1 = get_job(name='a')
        job2 = get_job(name='a')
        job3 = get_job(name='b')

        self.assertEquals(job1, job2)
        self.assertNotEquals(job1, job3)
        self.assertNotEquals(job2, job3)

        self.assertEquals(hash(job1), hash('a'))
        self.assertEquals(hash(job2), hash('a'))
        self.assertEquals(hash(job3), hash('b'))

class SchedulerTestCase(TestCase):

    def test_create(self):

        def on_job_executed(*ignored):
            pass

        def job_run(*ignored):
            pass

        def spawn(func):
            self.assertIs(func, job_run)

        scheduler = Scheduler()
        scheduler.on_job_executed = on_job_executed
        scheduler.lock = RLock()

        job1 = get_job()
        job1.run = job_run

        job2 = get_job()
        job2.run = job_run

        job3 = get_job(name=job2.name)
        job3.run = job_run

        with patch('gevent.spawn', spawn):
            scheduler.create(job1)
            scheduler.create(job2)

            # These two won't be added because scheduler.jobs is a set hashed by a job's name.
            scheduler.create(job2)
            scheduler.create(job3)

            self.assertEquals(scheduler.lock.called, 4)
            self.assertEquals(len(scheduler.jobs), 2)

            self.assertIn(job1, scheduler.jobs)
            self.assertIn(job2, scheduler.jobs)

            self.assertIs(job1.callback, scheduler.on_job_executed)
            self.assertIs(job2.callback, scheduler.on_job_executed)

    def test_run(self):

        test_wait_time = 0.3
        sched_sleep_time = 0.1

        data = {'sleep': [], 'jobs':set()}

        def _sleep(value):
            data['sleep'].append(value)

        def spawn_job(job):
            data['jobs'].add(job)

        def job_run(self):
            pass

        def iter_cb(scheduler, stop_time):
            """ Stop the scheduler after stop_time is reached (test_wait_time seconds from test's start time) -
            which should plenty enough for all the jobs to be spawned and the iteration loop to 
            """
            if datetime.utcnow() >= stop_time:
                scheduler.keep_running = False

        job1, job2, job3 = [get_job() for x in range(3)]

        job1.run = job_run
        job2.run = job_run
        job3.run = job_run

        scheduler = Scheduler()
        scheduler.spawn_job = spawn_job
        scheduler.lock = RLock()
        scheduler.sleep = _sleep
        scheduler.sleep_time = sched_sleep_time
        scheduler.iter_cb = iter_cb
        scheduler.iter_cb_args = (scheduler, datetime.utcnow() + timedelta(seconds=test_wait_time))

        scheduler.create(job1)
        scheduler.create(job2)
        scheduler.create(job3)

        scheduler.run()

        self.assertEquals(3, len(data['jobs']))
        self.assertTrue(scheduler.lock.called)

        for item in data['sleep']:
            self.assertEquals(sched_sleep_time, item)

        for job in job1, job2, job3:
            self.assertIn(job, data['jobs'])