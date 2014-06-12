# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from logging import basicConfig, getLogger, INFO
from traceback import format_exc

# gevent
import gevent

# paodate
from paodate import Delta

# Zato
from zato.common.util import make_repr

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
        return xmake_repr(self)

    def compute_in_seconds(self):
        return Delta(days=self.days, hours=self.hours, minutes=self.minutes, seconds=self.seconds).total_seconds

# ################################################################################################################################

class Job(object):
    def __init__(self, name, start_time, interval, callback=None, cb_args=None, cb_kwargs=None, max_runs=None):
        self.logger = getLogger(self.__class__.__name__)
        self.name = name
        self.start_time = start_time
        self.interval = interval
        self.callback = callback
        self.cb_args = cb_args or ()
        self.cb_kwargs = cb_kwargs or {}
        self.max_runs = None
        self.current_runs = 0 # Starts over each time scheduler is started
        self.success_runs = 0
        self.failure_runs = 0
        self.keep_running = True

    def __str__(self):
        return make_repr(self)

    def main_loop(self):
        while self.keep_running:

            # Perhaps we've already been run enough times
            if self.max_runs and self.current_runs == self.max_runs:
                self.keep_running = False

            # Pause the greenlet for however long is needed
            gevent.sleep(self.interval.in_seconds)

            try:
                # Invoke callback in a new greenlet so it doesn't block the current one.
                gevent.spawn(self.callback, name=self.name, *self.cb_args, **self.cb_kwargs)
                self.success_runs += 1
            except Exception, e:
                self.failure_runs += 1
                self.logger.warn(format_exc(e))
            finally:
                self.current_runs += 1

    def init(self):
        self.logger.info('Init job `%s`', self)

        # If the job has a start time in the future, sleep until it's ready to go.
        if self.start_time:
            #self.wait_for_start_time()
            self.main_loop()
        else:
            self.main_loop()

# ################################################################################################################################

class Scheduler(object):
    def __init__(self):
        self.logger = getLogger(self.__class__.__name__)
        self.jobs = []

    def create(self, job):
        self.logger.info('Creating job `%s`', job)
        self.jobs.append(job)

    def on_job_executed(self, *args, **kwargs):
        self.logger.warn('%s %s %s', 1, args, kwargs)

    def run(self):
        for job in self.jobs:
            job.callback = self.on_job_executed
            gevent.spawn(job.init)

        while True:
            gevent.sleep(0.1)

# ################################################################################################################################

if __name__ == '__main__':
    sched = Scheduler()
    interval = Interval(minutes=0, seconds=1)
    job = Job('test', None, interval)
    sched.create(job)
    sched.run()

    while True:
        gevent.sleep(1)