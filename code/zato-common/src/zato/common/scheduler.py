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

# gevent
from gevent import sleep, spawn
from gevent.lock import RLock

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
    def __init__(self, name, start_time, interval, callback=None, cb_args=None, cb_kwargs=None, max_runs=None,
                 on_max_runs_reached=SCHEDULER.ON_MAX_RUNS_REACHED.INACTIVATE):
        self.logger = getLogger(self.__class__.__name__)
        self.name = name
        self.start_time = start_time
        self.interval = interval
        self.callback = callback
        self.cb_args = cb_args or ()
        self.cb_kwargs = cb_kwargs or {}
        self.max_runs = max_runs
        self.on_max_runs_reached = on_max_runs_reached
        self.current_runs = 0 # Starts over each time scheduler is started
        self.success_runs = 0
        self.failure_runs = 0
        self.max_runs_reached = False
        self.keep_running = True

        # TODO: Add skip_days, skip_hours and skip_dates

    def __str__(self):
        return make_repr(self)

    def get_context(self):
        ctx = {
            'cid':new_cid(),
            'interval_in_seconds': self.interval.in_seconds,
            'start_time': self.start_time.isoformat()
        }
        for name in 'name', 'current_runs', 'success_runs', 'failure_runs', 'max_runs_reached':
            ctx[name] = getattr(self, name)

        return ctx

    def main_loop(self):
        while self.keep_running:

            # Perhaps we've already been run enough times
            if self.max_runs and self.current_runs == self.max_runs:
                self.keep_running = False
                self.max_runs_reached = True

            # Pause the greenlet for however long is needed
            sleep(self.interval.in_seconds)

            try:
                # Invoke callback in a new greenlet so it doesn't block the current one.
                spawn(self.callback, ctx=self.get_context(), *self.cb_args, **self.cb_kwargs)
                self.success_runs += 1
            except Exception, e:
                self.failure_runs += 1
                self.logger.warn(format_exc(e))
            finally:
                self.current_runs += 1

    def run(self):
        self.logger.info('Init job `%s`', self)

        # If the job has a start time in the future, sleep until it's ready to go.
        if self.start_time:
            while self.start_time >= datetime.utcnow():
                sleep(1)

        # OK, we're ready
        self.main_loop()

# ################################################################################################################################

class Scheduler(object):
    def __init__(self):
        self.logger = getLogger(self.__class__.__name__)
        self.jobs = []
        self.keep_running = True
        self.lock = RLock()

    def create(self, job):
        with self.lock:
            self.logger.info('Creating job `%s`', job)
            self.jobs.append(job)
            self.spawn_job(job)

    def on_job_executed(self, *args, **kwargs):
        self.logger.warn('%s %s %s', 1, args, kwargs)

    def spawn_job(self, job):
        job.callback = self.on_job_executed
        spawn(job.run)

    def run(self):
        with self.lock:
            for job in self.jobs:
                self.spawn_job(job)

        while self.keep_running:
            sleep(0.1)

# ################################################################################################################################

if __name__ == '__main__':
    sched = Scheduler()
    interval = Interval(minutes=0, seconds=1)
    job = Job('test', None, interval, max_runs=5)
    sched.create(job)
    sched.run()

    while True:
        sleep(1)
