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

def get_job(name=None, interval_in_seconds=None, start_time=None, repeats=None, callback=None):
    name = name or rand_string()
    interval_in_seconds = interval_in_seconds or rand_int()
    start_time = start_time or rand_date_utc()
    callback = callback or dummy_callback
    
    return Job(name, Interval(in_seconds=interval_in_seconds), start_time, callback, repeats=repeats)

def iter_cb(scheduler, stop_time):
    """ Stop the scheduler after stop_time is reached (test_wait_time seconds from test's start time) -
    which should plenty enough for all the jobs to be spawned and the iteration loop to 
    """
    if datetime.utcnow() >= stop_time:
        scheduler.keep_running = False

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

    def check_ctx(self, ctx, job, interval_in_seconds, repeats, idx, cb_kwargs, len_runs_ctx):

        self.assertEquals(ctx['name'], job.name)
        self.assertEquals(ctx['interval_in_seconds'], job.interval.in_seconds)
        self.assertEquals(ctx['repeats'], job.repeats)
        self.assertDictEqual(ctx['cb_kwargs'], job.cb_kwargs)

        self.assertEquals(ctx['interval_in_seconds'], interval_in_seconds)
        self.assertEquals(ctx['repeats'], repeats)
        self.assertEquals(ctx['current_run'], idx)
        self.assertDictEqual(ctx['cb_kwargs'], cb_kwargs)

        func = self.assertFalse if idx < len_runs_ctx else self.assertTrue
        func(ctx['repeats_reached'])

        # Don't check an exact time. Simply parse it out and confirm it's in the past.
        start_time = parse(ctx['start_time'])
        now = datetime.utcnow()
        self.assertTrue(start_time < now, 'start_time:`{}` is not less than now:`{}`'.format(start_time, now))

        self.assertTrue(is_like_cid(ctx['cid']))

    def test_get_context(self):

        name = rand_string()
        start_time = rand_date_utc()
        interval_in_seconds = rand_int()
        repeats_reached = rand_bool()
        current_run, repeats = rand_int(count=2)
        cb_kwargs = {rand_string():rand_string()}

        job = Job(name, cb_kwargs=cb_kwargs, interval=Interval(in_seconds=interval_in_seconds))
        job.start_time = start_time
        job.current_run = current_run
        job.repeats = repeats
        job.repeats_reached = repeats_reached

        ctx = job.get_context()
        cid = ctx.pop('cid')

        self.assertTrue(is_like_cid(cid))

        self.assertDictEqual(ctx, {
            'current_run': current_run,
            'interval_in_seconds': interval_in_seconds,
            'name': name,
            'start_time': start_time.isoformat(),
            'repeats': repeats,
            'repeats_reached': repeats_reached,
            'cb_kwargs': cb_kwargs
        })

    def test_main_loop_keep_running_false(self):

        job = get_job()
        job.keep_running = False

        self.assertTrue(job.main_loop())
        self.assertFalse(job.keep_running)
        self.assertFalse(job.repeats_reached)

        self.assertEquals(job.current_run, 0)

    def test_main_loop_repeats_reached(self):

        runs_ctx = []

        def callback(ctx):
            runs_ctx.append(ctx)

        cb_kwargs = {
            rand_string():rand_string(),
            rand_string():rand_string()
        }

        interval_in_seconds = 0.01
        repeats = choice(range(2, 5))

        job = get_job(interval_in_seconds=interval_in_seconds, repeats=repeats)
        job.callback = callback
        job.cb_kwargs = cb_kwargs

        self.assertTrue(job.main_loop())
        sleep(0.2)

        len_runs_ctx = len(runs_ctx)
        self.assertEquals(len_runs_ctx, repeats)

        self.assertFalse(job.keep_running)
        self.assertIs(job.callback, callback)

        for idx, ctx in enumerate(runs_ctx, 1):
            self.check_ctx(ctx, job, interval_in_seconds, repeats, idx, cb_kwargs, len_runs_ctx)

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
                repeats = choice(range(2, 5))

                cb_kwargs = {
                    rand_string():rand_string(),
                    rand_string():rand_string()
                }

                job = get_job(interval_in_seconds=interval_in_seconds, repeats=repeats)
                job.cb_kwargs = cb_kwargs
                job.start_time = datetime.utcnow()

                self.assertTrue(job.main_loop())
                sleep(0.2)

                self.assertEquals(repeats, len(sleep_history))
                self.assertEquals(repeats, len(spawn_history))

                for item in sleep_history:
                    self.assertEquals(interval_in_seconds, item)

                for idx, (apply_func, callback, ctx_dict) in enumerate(spawn_history, 1):
                    self.check_ctx(ctx_dict['ctx'], job, interval_in_seconds, repeats, idx, cb_kwargs, len(spawn_history))
                    self.assertIs(apply_func, apply)
                    self.assertIs(callback, dummy_callback)

    def test_run(self):

        data = {'main_loop_called':False, 'sleep': False}

        def main_loop():
            data['main_loop_called'] = True

        def sleep(value):
            data['sleep'] = value # Should not be executed if start_time is None

        start_time = datetime.utcnow() + timedelta(seconds=1.2)

        with patch('gevent.sleep', sleep):

            job = get_job()
            job.main_loop = main_loop
            job.start_time = start_time
    
            job.run()
    
            self.assertTrue(data['main_loop_called'])
            self.assertEquals(data['sleep'], 1)

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

class JobStartTimeTestCase(TestCase):
    def setUp(self):

        class _datetime(datetime):
        
            class datetime:
                @staticmethod
                def utcnow():
                    return self.now
        
            @staticmethod
            def timedelta(*args, **kwargs):
                return timedelta(*args, **kwargs)

        self._datetime = _datetime

    def check_get_start_time(self, start_time, now, expected):

        start_time = parse(start_time)
        self.now = parse(now)
        expected = parse(expected)

        interval = 1 # Days
        data = {'start_time':[], 'now':[]}

        def wait_iter_cb(start_time, now, *ignored):
            data['start_time'].append(start_time)
            data['now'].append(now)

        with patch('zato.common.scheduler.datetime', self._datetime):

            interval = Interval(days=interval)
            job = Job(rand_string(), start_time=start_time, interval=interval)
            job.wait_iter_cb = wait_iter_cb
            job.wait_sleep_time = 0.1
    
            self.assertEquals(job.start_time, expected)
            self.assertTrue(job.keep_running)
            self.assertFalse(job.repeats_reached)
            self.assertIs(job.repeats_reached_at, None)

            spawn(job.run)
            sleep(0.2)

            len_start_time = len(data['start_time'])
            len_now = len(data['now'])

            self.assertNotEquals(len_start_time, 0)
            self.assertNotEquals(len_now, 0)

            for item in data['start_time']:
                self.assertEquals(expected, item)

            for item in data['now']:
                self.assertEquals(self.now, item)

    def test_get_start_time_result_in_future(self):
        self.check_get_start_time('2017-03-20 19:11:37', '2017-03-21 15:11:37', '2017-03-21 19:11:37')

    def test_get_start_time_last_run_in_past_next_run_in_future(self):
        self.check_get_start_time('2017-03-20 19:11:37', '2017-03-21 21:11:37', '2017-03-22 19:11:37')

    def test_get_start_time_last_run_in_past_next_run_in_past(self):
        start_time = parse('2017-03-20 19:11:23')
        self.now = parse('2019-05-13 05:19:37')
        expected = parse('2017-04-04 19:11:23')

        with patch('zato.common.scheduler.datetime', self._datetime):

            interval = Interval(days=3)
            job = Job(rand_string(), start_time=start_time, interval=interval, repeats=5)

            self.assertFalse(job.keep_running)
            self.assertTrue(job.repeats_reached)
            self.assertEquals(job.repeats_reached_at, expected)
            self.assertFalse(job.start_time)

class SchedulerTestCase(TestCase):

    def test_create(self):

        data = {'spawned_jobs': 0}

        def on_job_executed(*ignored):
            pass

        def job_run(*ignored):
            pass

        def spawn(func):
            self.assertIs(func, job_run)
            data['spawned_jobs'] += 1

        scheduler = Scheduler()
        scheduler.on_job_executed = on_job_executed
        scheduler.lock = RLock()

        job1 = get_job()
        job1.run = job_run

        job2 = get_job()
        job2.run = job_run

        job3 = get_job(name=job2.name)
        job3.run = job_run

        job4 = get_job()
        job5 = get_job()

        with patch('gevent.spawn', spawn):
            scheduler.create(job1)
            scheduler.create(job2)

            # These two won't be added because scheduler.jobs is a set hashed by a job's name.
            scheduler.create(job2)
            scheduler.create(job3)

            # The first one won't be spawned but the second one will.
            scheduler.create(job4, spawn=False)
            scheduler.create(job5, spawn=True)

            self.assertEquals(scheduler.lock.called, 6)
            self.assertEquals(len(scheduler.jobs), 4)

            self.assertIn(job1, scheduler.jobs)
            self.assertIn(job2, scheduler.jobs)

            self.assertIs(job1.callback, scheduler.on_job_executed)
            self.assertIs(job2.callback, scheduler.on_job_executed)

            self.assertEquals(data['spawned_jobs'], 4)

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

        job1, job2, job3 = [get_job(str(x)) for x in range(3)]

        # Already run out of repeats and should not be started
        job4 = Job(rand_string(), start_time=parse('1997-12-23 21:24:27'), interval=Interval(seconds=5), repeats=3)

        job1.run = job_run
        job2.run = job_run
        job3.run = job_run
        job4.run = job_run

        scheduler = Scheduler()
        scheduler.spawn_job = spawn_job
        scheduler.lock = RLock()
        scheduler.sleep = _sleep
        scheduler.sleep_time = sched_sleep_time
        scheduler.iter_cb = iter_cb
        scheduler.iter_cb_args = (scheduler, datetime.utcnow() + timedelta(seconds=test_wait_time))

        scheduler.create(job1, spawn=False)
        scheduler.create(job2, spawn=False)
        scheduler.create(job3, spawn=False)
        scheduler.create(job4, spawn=False)

        scheduler.run()

        self.assertEquals(3, len(data['jobs']))
        self.assertTrue(scheduler.lock.called)

        for item in data['sleep']:
            self.assertEquals(sched_sleep_time, item)

        for job in job1, job2, job3:
            self.assertIn(job, data['jobs'])

        self.assertNotIn(job4, data['jobs'])

    def test_on_repeats_reached(self):

        test_wait_time = 0.2
        sched_sleep_time = job_sleep_time = 0.02
        job_repeats = 3

        data = {'job':None, 'called':0}

        def on_repeats_reached(job):
            data['job'] = job
            data['called'] += 1

        job = Job('a', Interval(seconds=0.1), repeats=job_repeats)
        job.wait_sleep_time = job_sleep_time

        scheduler = Scheduler()
        scheduler.on_repeats_reached = on_repeats_reached
        scheduler.iter_cb = iter_cb
        scheduler.iter_cb_args = (scheduler, datetime.utcnow() + timedelta(seconds=test_wait_time))

        scheduler.create(job)
        scheduler.run()

        now = datetime.utcnow()

        # Now the job should have reached the repeats limit within the now - test_wait_time period.
        self.assertIs(job, data['job'])
        self.assertEquals(1, data['called'])
        self.assertTrue(job.repeats_reached)
        self.assertFalse(job.keep_running)
        self.assertTrue(job.repeats_reached_at < now)
        self.assertTrue(job.repeats_reached_at >= now + timedelta(seconds=-test_wait_time))
