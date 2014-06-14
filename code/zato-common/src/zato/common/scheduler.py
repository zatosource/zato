# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from datetime import datetime
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
        self.in_seconds = in_seconds or self.compute_in_seconds()

    def __str__(self):
        return make_repr(self)

    def compute_in_seconds(self):
        return Delta(days=self.days, hours=self.hours, minutes=self.minutes, seconds=self.seconds).total_seconds

# ################################################################################################################################

class Job(object):
    def __init__(self, name, start_time, interval, callback=None, cb_kwargs=None, max_runs=None,
                 on_max_runs_reached=SCHEDULER.ON_MAX_RUNS_REACHED.INACTIVATE):
        self.logger = getLogger(self.__class__.__name__)
        self.name = name
        self.start_time = start_time
        self.interval = interval
        self.callback = callback
        self.cb_kwargs = cb_kwargs or {}
        self.max_runs = max_runs
        self.on_max_runs_reached = on_max_runs_reached
        self.current_run = 0 # Starts over each time scheduler is started
        self.max_runs_reached = False
        self.keep_running = True

        # TODO: Add skip_days, skip_hours and skip_dates

    def __str__(self):
        return make_repr(self)

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name

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

        _sleep = gevent.sleep

        # If the job has a start time in the future, sleep until it's ready to go.
        if self.start_time:
            while self.start_time >= datetime.utcnow():
                _sleep(1)

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
        sleep(1)
