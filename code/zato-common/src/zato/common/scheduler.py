# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import datetime
from logging import basicConfig, getLogger, INFO
from traceback import format_exc

# calllib
from calllib import apply

# datetime
from dateutil.rrule import rrule, SECONDLY

# gevent
import gevent # Imported directly so it can be mocked out in tests
from gevent import lock

# paodate
from paodate import Delta

# Zato
from zato.common.util import make_repr, new_cid

logger = getLogger(__name__)

basicConfig(level=INFO)

# ################################################################################################################################

class Interval(object):
    def __init__(self, days=0, hours=0, minutes=0, seconds=0, in_seconds=0):
        self.days = days
        self.hours = hours
        self.minutes = minutes
        self.seconds = seconds
        self.in_seconds = in_seconds or self.get_in_seconds()

    def __str__(self):
        return make_repr(self)

    def get_in_seconds(self):
        return Delta(days=self.days, hours=self.hours, minutes=self.minutes, seconds=self.seconds).total_seconds

# ################################################################################################################################

class Job(object):
    def __init__(self, name, interval, start_time=None, callback=None, cb_kwargs=None, repeats=None, on_repeats_reached_cb=None,
            is_active=True):
        self.logger = getLogger(self.__class__.__name__)
        self.name = name
        self.interval = interval
        self.callback = callback
        self.cb_kwargs = cb_kwargs or {}
        self.repeats = repeats
        self.on_repeats_reached_cb = on_repeats_reached_cb
        self.is_active = is_active

        self.current_run = 0 # Starts over each time scheduler is started
        self.repeats_reached = False
        self.repeats_reached_at = None
        self.keep_running = True

        self.start_time = self.get_start_time(start_time) if start_time else datetime.datetime.utcnow()

        self.wait_sleep_time = 1
        self.wait_iter_cb = None
        self.wait_iter_cb_args = ()

        # TODO: Add skip_days, skip_hours and skip_dates

    def __str__(self):
        return make_repr(self)

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name

    def get_start_time(self, start_time):
        """ Converts initial start time to the time the job should be invoked next.

        For instance, assume the scheduler has just been started. Given this job config ..

        - start_time: 2019-11-23 13:15:17
        - interval: 90 seconds
        - now: 2019-11-23 17:32:44

        .. a basic approach is to add 90 seconds to now and schedule the job. This would even
        work for jobs that have very short intervals when no one usually cares that much if a job
        is 15 seconds off or not.

        However, consider this series of events ..

        - start_time: 2019-11-23 13:00:00
        - interval: 86400 seconds (1 day)
        - the job is started
        - at 2019-11-23 21:15:00 the scheduler is stopped and started again

        .. now we don't want for the scheduler to start the job at 21:15:00 with an interval of one day,
        the job should rather wait till the next day so that the computed start_time should in fact be 2019-11-24 13:00:00.
        """

        # We have several scenarios to handle assuming that first_run_time = start_time + interval
        #
        # 1)  first_run_time > now
        # 2a) first_run_time <= now and first_run_time + interval_in_seconds > now
        # 2b) first_run_time <= now and first_run_time + interval_in_seconds <= now
        #
        # 1) is quick - start_time simply becomes first_run_time
        # 2a) means we already seen some executions of this job and there's still at least one in the future
        # 2b) means we already seen some executions of this job and it won't be run in the future anymore

        now = datetime.datetime.utcnow()
        interval = datetime.timedelta(seconds=self.interval.in_seconds)

        first_run_time = start_time + interval

        if first_run_time > now:
            return first_run_time
        else:
            runs = rrule(SECONDLY, interval=int(self.interval.in_seconds), dtstart=start_time, count=self.repeats)
            last_run_time = runs.before(now)
            next_run_time = last_run_time + interval

            if next_run_time > now:
                return next_run_time
            else:
                # We must have already run out of iterations
                self.repeats_reached = True
                self.repeats_reached_at = next_run_time
                self.keep_running = False

    def get_context(self):
        ctx = {
            'cid':new_cid(),
            'interval_in_seconds': self.interval.in_seconds,
            'start_time': self.start_time.isoformat(),
            'cb_kwargs': self.cb_kwargs
        }

        for name in 'name', 'current_run', 'repeats_reached', 'repeats':
            ctx[name] = getattr(self, name)

        return ctx

    def main_loop(self):

        _sleep = gevent.sleep
        _spawn = gevent.spawn

        while self.keep_running:
            try:
                self.current_run += 1

                # Perhaps we've already been executed enough times
                if self.repeats and self.current_run == self.repeats:
                    self.keep_running = False
                    self.repeats_reached = True
                    self.repeats_reached_at = datetime.datetime.utcnow()

                    if self.on_repeats_reached_cb:
                        self.on_repeats_reached_cb(self)

                # Pause the greenlet for however long is needed
                _sleep(self.interval.in_seconds)

                # Invoke callback in a new greenlet so it doesn't block the current one.
                _spawn(apply, self.callback, {'ctx':self.get_context()})
            except Exception, e:
                print(format_exc(e))
                self.logger.warn(format_exc(e))

        return True

    def run(self):
        self.logger.info('Init job `%s`', self)

        _utcnow = datetime.datetime.utcnow
        _sleep = gevent.sleep

        # If the job has a start time in the future, sleep until it's ready to go.
        now = _utcnow()

        while self.start_time > now:
            _sleep(self.wait_sleep_time)

            if self.wait_iter_cb:
                self.wait_iter_cb(self.start_time, now, *self.wait_iter_cb_args)

            now = _utcnow()

        # OK, we're ready
        self.main_loop()

# ################################################################################################################################

class Scheduler(object):
    def __init__(self):
        self.logger = getLogger(self.__class__.__name__)
        self.jobs = set()
        self.job_greenlets = {}
        self.keep_running = True
        self.lock = lock.RLock()
        self.sleep_time = 0.1
        self.iter_cb = None
        self.iter_cb_args = ()

    def on_repeats_reached(self, job):
        with self.lock:
            job.is_active = False

    def create(self, job, spawn=True):
        with self.lock:
                self.logger.info('Creating job `%s`', job)
                self.jobs.add(job)

                if job.is_active:
                    if spawn:
                        self.spawn_job(job)
                else:
                    self.logger.warn('Skipping inactive job `%s`', job)

    def _delete(self, job):
        """ Actually deletes a job. Must be called with self.lock held.
        """
        job.keep_running = False
        self.jobs.remove(job)
        self.job_greenlets[job.name].kill(timeout=2.0)
        del self.job_greenlets[job.name]

    def delete(self, job):
        """ Public API for job deletion.
        """
        with self.lock:
            return self._delete(job)

    def sleep(self, value):
        """ A method introduced so the class is easier to mock out in tests.
        """
        gevent.sleep(value)

    def on_job_executed(self, *args, **kwargs):
        self.logger.warn('%s %s %s', 1, args, kwargs)

    def spawn_job(self, job):
        """ Spawns a job's greenlet. Must be called with self.lock held.
        """
        job.callback = self.on_job_executed
        job.on_repeats_reached_cb = self.on_repeats_reached
        self.job_greenlets[job.name] = gevent.spawn(job.run)

    def run(self):
        _sleep = self.sleep
        _sleep_time = self.sleep_time

        with self.lock:
            for job in self.jobs:
                if job.repeats_reached:
                    self.logger.info('Job `%s` already reached max runs count (%s UTC)', job.name, job.repeats_reached_at)
                else:
                    self.spawn_job(job)

        while self.keep_running:
            _sleep(_sleep_time)

            if self.iter_cb:
                self.iter_cb(*self.iter_cb_args)

if __name__ == '__main__':
    job = Job('a', start_time=datetime.datetime.utcnow(), interval=Interval(seconds=1), repeats=2)
    scheduler = Scheduler()
    scheduler.create(job, False)
    scheduler.run()
