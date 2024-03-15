# -*- coding: utf-8 -*-

"""
Copyright (C) 2019, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import time
from datetime import datetime, timedelta
from random import choice, seed
from unittest import TestCase

# Bunch
from bunch import Bunch

# crontab
from crontab import CronTab

# ciso8601
try:
    from zato.common.util.api import parse_datetime
except ImportError:
    from dateutil.parser import parse as parse_datetime

# gevent
from gevent import sleep, spawn

# mock
from mock import patch

# Zato
from zato.common.api import SCHEDULER
from zato.common.test import is_like_cid, rand_bool, rand_date_utc, rand_int, rand_string
from zato.scheduler.backend import Interval, Job, Scheduler

seed()

DEFAULT_CRON_DEFINITION = '* * * * *'

class RLock:
    def __init__(self):
        self.called = 0

    def __enter__(self):
        self.called += 1

    def __exit__(self, exc_type, exc_val, exc_tb):
        return True

def dummy_callback(*args, **kwargs):
    pass

def get_job(name=None, interval_in_seconds=None, start_time=None, max_repeats=None, callback=None, prefix='job'):
    name = name or '{}-{}'.format(prefix, rand_string())
    interval_in_seconds = interval_in_seconds or rand_int()
    start_time = start_time or rand_date_utc()
    callback = callback or dummy_callback

    return Job(rand_int(), name, SCHEDULER.JOB_TYPE.INTERVAL_BASED, Interval(in_seconds=interval_in_seconds),
        start_time, callback, max_repeats=max_repeats)

def iter_cb(scheduler, stop_time):
    """ Stop the scheduler after stop_time is reached (test_wait_time seconds from test's start time) -
    which should plenty enough for all the jobs to be spawned and the iteration loop to
    """
    if datetime.utcnow() >= stop_time:
        scheduler.keep_running = False

def get_scheduler_config():
    config = Bunch()
    config.on_job_executed_cb = dummy_callback
    config._add_startup_jobs = False
    config._add_scheduler_jobs = False
    config.startup_jobs = []
    config.odb = None
    config.job_log_level = 'info'

    return config

class IntervalTestCase(TestCase):

    def test_interval_has_in_seconds(self):

        in_seconds = rand_int()
        interval = Interval(in_seconds=in_seconds)
        self.assertEqual(interval.in_seconds, in_seconds)

    def test_interval_compute_in_seconds(self):

        for days, hours, minutes, seconds, expected in (
            (55, 83, 69, 75, 5055015.0),
            (31, 2, 6, 23, 2685983.0),
            (68, 55, 57, 82, 6076702.0),
            (0, 69, 42, 12, 250932.0),
            (0, 48, 0, 17, 172817.0),
            (0, 0, 192, 17, 11537.0),
            (0, 0, 7, 0, 420.0),
            (0, 0, 0, 32, 32.0)): # noqa

            interval = Interval(days, hours, minutes, seconds)
            self.assertEqual(interval.in_seconds, expected)

class JobTestCase(TestCase):

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

    def check_ctx(self, ctx, job, interval_in_seconds, max_repeats, idx, cb_kwargs,
            len_runs_ctx, job_type=SCHEDULER.JOB_TYPE.INTERVAL_BASED):

        self.assertEqual(ctx['name'], job.name)
        self.assertEqual(ctx['max_repeats'], job.max_repeats)
        self.assertDictEqual(ctx['cb_kwargs'], job.cb_kwargs)

        if job_type == SCHEDULER.JOB_TYPE.INTERVAL_BASED:
            self.assertEqual(ctx['interval_in_seconds'], interval_in_seconds)
        else:
            self.assertEqual(ctx['cron_definition'], DEFAULT_CRON_DEFINITION)

        self.assertEqual(ctx['max_repeats'], max_repeats)
        self.assertEqual(ctx['current_run'], idx)
        self.assertDictEqual(ctx['cb_kwargs'], cb_kwargs)

        func = self.assertFalse if idx < len_runs_ctx else self.assertTrue
        func(ctx['max_repeats_reached'])

        # Don't check an exact time. Simply parse it out and confirm it's in the past.
        start_time = parse_datetime(ctx['start_time'])
        now = datetime.utcnow()
        self.assertTrue(start_time < now, 'start_time:`{}` is not less than now:`{}`'.format(start_time, now))

        self.assertTrue(is_like_cid(ctx['cid']))

    def test_clone(self):

        interval = Interval(seconds=5)
        start_time = datetime.utcnow()

        def callback():
            pass

        def on_max_repeats_reached_cb():
            pass

        job = Job(rand_int(), 'a', SCHEDULER.JOB_TYPE.INTERVAL_BASED, interval, start_time)
        job.callback = callback
        job.on_max_repeats_reached_cb = on_max_repeats_reached_cb

        clone = job.clone()
        sleep(0.1)

        for name in 'name', 'interval', 'cb_kwargs', 'max_repeats', 'is_active':
            expected = getattr(job, name)
            given = getattr(clone, name)
            self.assertEqual(expected, given, '{} != {} ({})'.format(expected, given, name))

        self.assertEqual(job.start_time, clone.start_time)

        self.assertIs(job.callback, clone.callback)
        self.assertIs(job.on_max_repeats_reached_cb, clone.on_max_repeats_reached_cb)

    def test_get_context(self):

        id = rand_int()
        name = rand_string()
        start_time = rand_date_utc()
        interval_in_seconds = rand_int()
        max_repeats_reached = rand_bool()
        current_run, max_repeats = rand_int(count=2)
        cb_kwargs = {rand_string():rand_string()}

        for job_type in SCHEDULER.JOB_TYPE.INTERVAL_BASED, SCHEDULER.JOB_TYPE.CRON_STYLE:

            interval=Interval(in_seconds=interval_in_seconds) if \
                job_type == SCHEDULER.JOB_TYPE.INTERVAL_BASED else CronTab(DEFAULT_CRON_DEFINITION)

            job = Job(id, name, job_type, cb_kwargs=cb_kwargs, interval=interval)
            job.start_time = start_time
            job.current_run = current_run
            job.max_repeats = max_repeats
            job.max_repeats_reached = max_repeats_reached

            if job_type == SCHEDULER.JOB_TYPE.CRON_STYLE:
                job.cron_definition = DEFAULT_CRON_DEFINITION

            ctx = job.get_context()
            cid = ctx.pop('cid')

            self.assertTrue(is_like_cid(cid))

            expected = {
                'current_run': current_run,
                'id': id,
                'name': name,
                'start_time': start_time.isoformat(),
                'max_repeats': max_repeats,
                'max_repeats_reached': max_repeats_reached,
                'cb_kwargs': cb_kwargs,
                'type': job_type,
            }

            if job_type == SCHEDULER.JOB_TYPE.CRON_STYLE:
                expected['cron_definition'] = job.cron_definition
            else:
                expected['interval_in_seconds'] = job.interval.in_seconds

            self.assertDictEqual(ctx, expected)

    def test_main_loop_keep_running_false(self):

        job = get_job()
        job.keep_running = False

        self.assertTrue(job.main_loop())
        self.assertFalse(job.keep_running)
        self.assertFalse(job.max_repeats_reached)

        self.assertEqual(job.current_run, 0)

    def test_main_loop_max_repeats_reached(self):

        runs_ctx = []

        def callback(ctx):
            runs_ctx.append(ctx)

        cb_kwargs = {
            rand_string():rand_string(),
            rand_string():rand_string()
        }

        interval_in_seconds = 0.01
        max_repeats = choice(range(2, 5))

        job = get_job(interval_in_seconds=interval_in_seconds, max_repeats=max_repeats)
        job.callback = callback
        job.cb_kwargs = cb_kwargs

        self.assertTrue(job.main_loop())
        sleep(0.2)

        len_runs_ctx = len(runs_ctx)
        self.assertEqual(len_runs_ctx, max_repeats)

        self.assertFalse(job.keep_running)
        self.assertIs(job.callback, callback)

        for idx, ctx in enumerate(runs_ctx, 1):
            self.check_ctx(ctx, job, interval_in_seconds, max_repeats, idx, cb_kwargs, len_runs_ctx)

    def test_main_loop_sleep_spawn_called(self):

        wait_time = 0.2
        sleep_time = rand_int()

        now_values = [parse_datetime('2019-12-23 22:19:03'), parse_datetime('2021-05-13 17:35:48')]

        sleep_history = []
        spawn_history = []
        sleep_time_history = []

        def sleep(value):
            if value != wait_time:
                sleep_history.append(value)

        def spawn(*args, **kwargs):
            spawn_history.append([args, kwargs])

        def get_sleep_time(*args, **kwargs):
            sleep_time_history.append(args[1])
            return sleep_time

        with patch('gevent.sleep', sleep):
            with patch('zato.scheduler.backend.Job._spawn', spawn):
                with patch('zato.scheduler.backend.Job.get_sleep_time', get_sleep_time):
                    for now in now_values:
                        self.now = now
                        with patch('zato.scheduler.backend.datetime', self._datetime):
                            for job_type in SCHEDULER.JOB_TYPE.CRON_STYLE, SCHEDULER.JOB_TYPE.INTERVAL_BASED:

                                max_repeats = choice(range(2, 5))

                                cb_kwargs = {
                                    rand_string():rand_string(),
                                    rand_string():rand_string()
                                }

                                interval = Interval(seconds=sleep_time) if job_type == SCHEDULER.JOB_TYPE.INTERVAL_BASED \
                                    else CronTab(DEFAULT_CRON_DEFINITION)

                                job = Job(rand_int(), rand_string(), job_type, interval, max_repeats=max_repeats)

                                if job.type == SCHEDULER.JOB_TYPE.CRON_STYLE:
                                    job.cron_definition = DEFAULT_CRON_DEFINITION

                                job.cb_kwargs = cb_kwargs
                                job.start_time = datetime.utcnow()
                                job.callback = dummy_callback

                                self.assertTrue(job.main_loop())
                                time.sleep(0.5)

                                self.assertEqual(max_repeats, len(sleep_history))
                                self.assertEqual(max_repeats, len(spawn_history))

                                for item in sleep_history:
                                    self.assertEqual(sleep_time, item)

                                for idx, (callback, ctx_dict) in enumerate(spawn_history, 1):
                                    self.assertEqual(2, len(callback))
                                    callback = callback[1]
                                    self.check_ctx(
                                        ctx_dict['ctx'], job, sleep_time, max_repeats, idx, cb_kwargs, len(spawn_history), job_type)
                                    self.assertIs(callback, dummy_callback)

                                del sleep_history[:]
                                del spawn_history[:]

                            for item in sleep_time_history:
                                self.assertEqual(item, now)

                            del sleep_time_history[:]

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
            self.assertEqual(data['sleep'], 1)

    def test_hash_eq(self):
        job1 = get_job(name='a')
        job2 = get_job(name='a')
        job3 = get_job(name='b')

        self.assertEqual(job1, job2)
        self.assertNotEquals(job1, job3)
        self.assertNotEquals(job2, job3)

        self.assertEqual(hash(job1), hash('a'))
        self.assertEqual(hash(job2), hash('a'))
        self.assertEqual(hash(job3), hash('b'))

    def test_get_sleep_time(self):
        now = parse_datetime('2015-11-27 19:13:37.274')

        job1 = Job(1, 'a', SCHEDULER.JOB_TYPE.INTERVAL_BASED, Interval(seconds=5), now)
        self.assertEqual(job1.get_sleep_time(now), 5)

        job2 = Job(2, 'b', SCHEDULER.JOB_TYPE.CRON_STYLE, CronTab(DEFAULT_CRON_DEFINITION), now)
        self.assertEqual(job2.get_sleep_time(now), 22.726)

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

        start_time = parse_datetime(start_time)
        self.now = parse_datetime(now)
        expected = parse_datetime(expected)

        interval = 1 # Days
        data = {'start_time':[], 'now':[]}

        def wait_iter_cb(start_time, now, *ignored):
            data['start_time'].append(start_time)
            data['now'].append(now)

        with patch('zato.scheduler.backend.datetime', self._datetime):

            interval = Interval(days=interval)
            job = Job(rand_int(), rand_string(), SCHEDULER.JOB_TYPE.INTERVAL_BASED, start_time=start_time, interval=interval)
            job.wait_iter_cb = wait_iter_cb
            job.wait_sleep_time = 0.1

            self.assertEqual(job.start_time, expected)
            self.assertTrue(job.keep_running)
            self.assertFalse(job.max_repeats_reached)
            self.assertIs(job.max_repeats_reached_at, None)

            spawn(job.run)
            sleep(0.2)

            len_start_time = len(data['start_time'])
            len_now = len(data['now'])

            self.assertNotEquals(len_start_time, 0)
            self.assertNotEquals(len_now, 0)

            for item in data['start_time']:
                self.assertEqual(expected, item)

            for item in data['now']:
                self.assertEqual(self.now, item)

    def test_get_start_time_result_in_future(self):
        self.check_get_start_time('2017-03-20 19:11:37', '2017-03-21 15:11:37', '2017-03-21 19:11:37')

    def test_get_start_time_last_run_in_past_next_run_in_future(self):
        self.check_get_start_time('2017-03-20 19:11:37', '2017-03-21 21:11:37', '2017-03-22 19:11:37')

    def test_get_start_time_last_run_in_past_next_run_in_past(self):
        start_time = parse_datetime('2017-03-20 19:11:23')
        self.now = parse_datetime('2019-05-13 05:19:37')
        expected = parse_datetime('2017-04-04 19:11:23')

        with patch('zato.scheduler.backend.datetime', self._datetime):

            interval = Interval(days=3)
            job = Job(rand_int(), rand_string(), SCHEDULER.JOB_TYPE.INTERVAL_BASED, start_time=start_time, interval=interval, max_repeats=5)

            self.assertFalse(job.keep_running)
            self.assertTrue(job.max_repeats_reached)
            self.assertEqual(job.max_repeats_reached_at, expected)
            self.assertFalse(job.start_time)

class SchedulerTestCase(TestCase):

    def test_create(self):

        data = {'spawned_jobs': 0}

        def on_job_executed(*ignored):
            pass

        def job_run(*ignored):
            pass

        def spawn(scheduler_instance, func):
            self.assertIs(func, job_run)
            data['spawned_jobs'] += 1

        with patch('zato.scheduler.backend.Scheduler._spawn', spawn):

            scheduler = Scheduler(get_scheduler_config(), None)
            scheduler.lock = RLock()
            scheduler.on_job_executed = on_job_executed

            job1 = get_job()
            job1.run = job_run

            job2 = get_job()
            job2.run = job_run

            job3 = get_job(name=job2.name)
            job3.run = job_run

            job4 = get_job()
            job5 = get_job()

            job6 = get_job(prefix='inactive')
            job6.is_active = False

            scheduler.create(job1)
            scheduler.create(job2)

            # These two won't be added because scheduler.jobs is a set hashed by a job's name.
            scheduler.create(job2)
            scheduler.create(job3)

            # The first one won't be spawned but the second one will.
            scheduler.create(job4, spawn=False)
            scheduler.create(job5, spawn=True)

            # Won't be added anywhere nor spawned because it's inactive.
            scheduler.create(job6)

            self.assertEqual(scheduler.lock.called, 7)
            self.assertEqual(len(scheduler.jobs), 5)

            self.assertIn(job1, scheduler.jobs)
            self.assertIn(job2, scheduler.jobs)

            self.assertIs(job1.callback, scheduler.on_job_executed)
            self.assertIs(job2.callback, scheduler.on_job_executed)

            self.assertEqual(data['spawned_jobs'], 4)

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

        # Already run out of max_repeats and should not be started
        job4 = Job(rand_int(), rand_string(), SCHEDULER.JOB_TYPE.INTERVAL_BASED, start_time=parse_datetime('1997-12-23 21:24:27'),
            interval=Interval(seconds=5), max_repeats=3)

        job1.run = job_run
        job2.run = job_run
        job3.run = job_run
        job4.run = job_run

        config = Bunch()
        config.on_job_executed_cb = dummy_callback
        config._add_startup_jobs = False
        config._add_scheduler_jobs = False
        config.startup_jobs = []
        config.odb = None
        config.job_log_level = 'info'

        scheduler = Scheduler(get_scheduler_config(), None)
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

        self.assertEqual(3, len(data['jobs']))
        self.assertTrue(scheduler.lock.called)

        for item in data['sleep']:
            self.assertEqual(sched_sleep_time, item)

        for job in job1, job2, job3:
            self.assertIn(job, data['jobs'])

        self.assertNotIn(job4, data['jobs'])

    def test_on_max_repeats_reached(self):

        test_wait_time = 0.5
        job_sleep_time = 0.02
        job_max_repeats = 3

        data = {'job':None, 'called':0}

        job = Job(rand_int(), 'a', SCHEDULER.JOB_TYPE.INTERVAL_BASED, Interval(seconds=0.1), max_repeats=job_max_repeats)
        job.wait_sleep_time = job_sleep_time

        # Just to make sure it's inactive by default.
        self.assertTrue(job.is_active)

        scheduler = Scheduler(get_scheduler_config(), None)
        data['old_on_max_repeats_reached'] = scheduler.on_max_repeats_reached

        def on_max_repeats_reached(job):
            data['job'] = job
            data['called'] += 1
            data['old_on_max_repeats_reached'](job)

        scheduler.on_max_repeats_reached = on_max_repeats_reached
        scheduler.iter_cb = iter_cb
        scheduler.iter_cb_args = (scheduler, datetime.utcnow() + timedelta(seconds=test_wait_time))

        scheduler.create(job)
        scheduler.run()

        now = datetime.utcnow()

        # Now the job should have reached the max_repeats limit within the now - test_wait_time period.
        self.assertIs(job, data['job'])
        self.assertEqual(1, data['called'])
        self.assertTrue(job.max_repeats_reached)
        self.assertFalse(job.keep_running)
        self.assertTrue(job.max_repeats_reached_at < now)
        self.assertTrue(job.max_repeats_reached_at >= now + timedelta(seconds=-test_wait_time))

        # Having run out of max_repeats it should not be active now.
        self.assertFalse(job.is_active)

    def test_delete(self):
        test_wait_time = 0.5
        job_sleep_time = 10
        job_max_repeats = 30

        job1 = Job(rand_int(), 'a', SCHEDULER.JOB_TYPE.INTERVAL_BASED, Interval(seconds=0.1), max_repeats=job_max_repeats)
        job1.wait_sleep_time = job_sleep_time

        job2 = Job(rand_int(), 'b', SCHEDULER.JOB_TYPE.INTERVAL_BASED, Interval(seconds=0.1), max_repeats=job_max_repeats)
        job2.wait_sleep_time = job_sleep_time

        scheduler = Scheduler(get_scheduler_config(), None)
        scheduler.lock = RLock()
        scheduler.iter_cb = iter_cb
        scheduler.iter_cb_args = (scheduler, datetime.utcnow() + timedelta(seconds=test_wait_time))

        scheduler.create(job1)
        scheduler.create(job2)
        scheduler.run()

        scheduler.unschedule(job1)

        self.assertIn(job2, scheduler.jobs)
        self.assertNotIn(job1, scheduler.jobs)
        self.assertFalse(job1.keep_running)

        # run - 1
        # create - 2
        # delete - 1
        # on_max_repeats_reached - 0 (because of how long it takes to run job_max_repeats with test_wait_time)
        # 1+2+1 = 4
        self.assertEqual(scheduler.lock.called, 4)

    def test_job_greenlets(self):

        data = {'spawned':[], 'stopped': []}

        class FakeGreenlet:
            def __init__(_self, run):
                _self.run = _self._run = run

            def kill(_self, *args, **kwargs):
                data['stopped'].append([_self, args, kwargs])

        def spawn(scheduler_instance, job, *args, **kwargs):
            g = FakeGreenlet(job)
            data['spawned'].append(g)
            return g

        with patch('zato.scheduler.backend.Scheduler._spawn', spawn):

            test_wait_time = 0.5
            job_sleep_time = 10
            job_max_repeats = 30

            job1 = Job(rand_int(), 'a', SCHEDULER.JOB_TYPE.INTERVAL_BASED, Interval(seconds=0.1), max_repeats=job_max_repeats)
            job1.wait_sleep_time = job_sleep_time

            job2 = Job(rand_int(), 'b', SCHEDULER.JOB_TYPE.INTERVAL_BASED, Interval(seconds=0.1), max_repeats=job_max_repeats)
            job2.wait_sleep_time = job_sleep_time

            scheduler = Scheduler(get_scheduler_config(), None)
            scheduler.lock = RLock()
            scheduler.iter_cb = iter_cb
            scheduler.iter_cb_args = (scheduler, datetime.utcnow() + timedelta(seconds=test_wait_time))

            scheduler.create(job1)
            scheduler.create(job2)
            scheduler.run()

            self.assertEqual(scheduler.job_greenlets[job1.name]._run, job1.run)
            self.assertEqual(scheduler.job_greenlets[job2.name]._run, job2.run)

            self.assertTrue(job1.keep_running)
            self.assertTrue(job2.keep_running)

            scheduler.unschedule(job1)

            self.assertFalse(job1.keep_running)
            self.assertTrue(job2.keep_running)

            self.assertNotIn(job1.name, scheduler.job_greenlets)
            self.assertEqual(scheduler.job_greenlets[job2.name]._run, job2.run)

            self.assertEqual(len(data['stopped']), 1)
            g, args, kwargs = data['stopped'][0]
            self.assertIs(g.run.im_func, job1.run.im_func) # That's how we know it was job1 deleted not job2
            self.assertIs(args, ())
            self.assertDictEqual(kwargs, {'timeout':2.0, 'block':False})

    def test_edit(self):

        def callback():
            pass

        def on_max_repeats_reached_cb():
            pass

        start_time = datetime.utcnow()
        test_wait_time = 0.5
        job_interval1, job_interval2 = 2, 3
        job_sleep_time = 10
        job_max_repeats1, job_max_repeats2 = 20, 30

        scheduler = Scheduler(get_scheduler_config(), None)
        scheduler.lock = RLock()
        scheduler.iter_cb = iter_cb
        scheduler.iter_cb_args = (scheduler, datetime.utcnow() + timedelta(seconds=test_wait_time))

        def check(scheduler, job, label):
            self.assertIn(job.name, scheduler.job_greenlets)
            self.assertIn(job, scheduler.jobs)

            self.assertEqual(1, len(scheduler.job_greenlets))
            self.assertEqual(1, len(scheduler.jobs))

            self.assertIs(job.run.im_func, scheduler.job_greenlets.values()[0]._run.im_func)

            clone = list(scheduler.jobs)[0]

            for name in 'name', 'interval', 'cb_kwargs', 'max_repeats', 'is_active':
                expected = getattr(job, name)
                given = getattr(clone, name)
                self.assertEqual(expected, given, '{} != {} ({})'.format(expected, given, name))

            job_cb = job.callback
            clone_cb = clone.callback

            job_on_max_cb = job.on_max_repeats_reached_cb
            clone_on_max_cb = clone.on_max_repeats_reached_cb

            if label == 'first':
                self.assertEqual(job.start_time, clone.start_time)
                self.assertIs(job_cb.im_func, clone_cb.im_func)
                self.assertIs(job_on_max_cb.im_func, clone_on_max_cb.im_func)

            else:
                self.assertEqual(job.start_time, clone.start_time)
                self.assertIs(clone_cb.im_func, scheduler.on_job_executed.im_func)
                self.assertIs(clone_on_max_cb.im_func, scheduler.on_max_repeats_reached.im_func)

        job1 = Job(rand_int(), 'a', SCHEDULER.JOB_TYPE.INTERVAL_BASED, Interval(seconds=job_interval1), start_time, max_repeats=job_max_repeats1)
        job1.callback = callback
        job1.on_max_repeats_reached_cb = on_max_repeats_reached_cb
        job1.wait_sleep_time = job_sleep_time

        job2 = Job(rand_int(), 'a', SCHEDULER.JOB_TYPE.INTERVAL_BASED, Interval(seconds=job_interval2), start_time, max_repeats=job_max_repeats2)
        job2.callback = callback
        job2.on_max_repeats_reached_cb = on_max_repeats_reached_cb
        job2.wait_sleep_time = job_sleep_time

        scheduler.run()
        scheduler.create(job1)

        sleep(test_wait_time)

        # We have only job1 at this point
        check(scheduler, job1, 'first')

        # Removes job1 along the way ..
        scheduler.edit(job2)

        # .. so now job2 is the now removed job1.
        check(scheduler, job2, 'second')

    def test_on_job_executed_cb(self):

        data = {'runs':[], 'ctx':[]}

        def get_context():
            ctx = {'name': rand_string(), 'type':SCHEDULER.JOB_TYPE.INTERVAL_BASED}
            data['ctx'].append(ctx)
            return ctx

        def on_job_executed_cb(ctx):
            data['runs'].append(ctx)

        test_wait_time = 0.5
        job_sleep_time = 0.1
        job_max_repeats = 10

        job = Job(rand_int(), 'a', SCHEDULER.JOB_TYPE.INTERVAL_BASED, Interval(seconds=0.1), max_repeats=job_max_repeats)
        job.wait_sleep_time = job_sleep_time
        job.get_context = get_context

        scheduler = Scheduler(get_scheduler_config(), None)
        scheduler.lock = RLock()
        scheduler.iter_cb = iter_cb
        scheduler.iter_cb_args = (scheduler, datetime.utcnow() + timedelta(seconds=test_wait_time))
        scheduler.on_job_executed_cb = on_job_executed_cb

        scheduler.create(job, spawn=False)
        scheduler.run()

        self.assertEqual(len(data['runs']), len(data['ctx']))

        for idx, item in enumerate(data['runs']):
            self.assertEqual(data['ctx'][idx], item)
