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

# gevent
import gevent # Imported directly so it can be mocked out in tests
from gevent import lock

# paodate
from paodate import Delta

# Zato
from zato.common import SCHEDULER
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
    def __init__(self, name, interval, start_time=None, callback=None, cb_kwargs=None, max_runs=None,
                 on_max_runs_reached=SCHEDULER.ON_MAX_RUNS_REACHED.INACTIVATE):
        self.logger = getLogger(self.__class__.__name__)
        self.name = name
        self.interval = interval
        self.start_time = self.get_start_time(start_time) if start_time else None
        self.callback = callback
        self.cb_kwargs = cb_kwargs or {}
        self.max_runs = max_runs
        self.on_max_runs_reached = on_max_runs_reached
        self.current_run = 0 # Starts over each time scheduler is started
        self.max_runs_reached = False
        self.keep_running = True

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

        # We have a couple of scenarios to handle
        #
        # 1) start_time + interval > now
        # 2) start_time + interval <= now
        #
        # Scenario 1) is quick - start_time simply becomes start_time + interval
        #
        # Scenario 2) means we dub last_run_time the last occurrence of the job before now.
        # The new start_time is now last_run_time + interval and will be either now or in the future.

        first_run_time = start_time + datetime.timedelta(seconds=self.interval.in_seconds)

        if first_run_time > datetime.datetime.utcnow():
            return first_run_time
        else:
            raise NotImplementedError()

    def get_context(self):
        ctx = {
            'cid':new_cid(),
            'interval_in_seconds': self.interval.in_seconds,
            'start_time': self.start_time.isoformat(),
            'cb_kwargs': self.cb_kwargs
        }

        for name in 'name', 'current_run', 'max_runs_reached', 'max_runs':
            ctx[name] = getattr(self, name)

        return ctx

    def main_loop(self):

        _sleep = gevent.sleep
        _spawn = gevent.spawn

        while self.keep_running:
            try:
                self.current_run += 1

                # Perhaps we've already been executed enough times
                if self.max_runs and self.current_run == self.max_runs:
                    self.keep_running = False
                    self.max_runs_reached = True

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
        self.keep_running = True
        self.lock = lock.RLock()
        self.sleep_time = 0.1
        self.iter_cb = None
        self.iter_cb_args = ()

    def create(self, job):
        with self.lock:
            self.logger.info('Creating job `%s`', job)
            self.jobs.add(job)
            self.spawn_job(job)

    def sleep(self, value):
        """ A method introduced so the class is easier to mock out in tests.
        """
        gevent.sleep(value)

    def on_job_executed(self, *args, **kwargs):
        self.logger.warn('%s %s %s', 1, args, kwargs)

    def spawn_job(self, job):
        job.callback = self.on_job_executed
        gevent.spawn(job.run)

    def run(self):
        _sleep = self.sleep
        _sleep_time = self.sleep_time

        with self.lock:
            for job in self.jobs:
                self.spawn_job(job)

        while self.keep_running:
            _sleep(_sleep_time)
    
            if self.iter_cb:
                self.iter_cb(*self.iter_cb_args)

# ################################################################################################################################

if __name__ == '__main__':
    sched = Scheduler()
    interval = Interval(minutes=0, seconds=1)
    job = Job('test', None, interval, max_runs=5)
    sched.create(job)
    sched.run()

    while True:
        gevent.sleep(1)
