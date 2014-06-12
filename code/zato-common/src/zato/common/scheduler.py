# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from logging import basicConfig, getLogger, INFO

# paodate
from paodate import Delta

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

    def compute_in_seconds(self):
        return Delta(days=self.days, hours=self.hours, minutes=self.minutes, seconds=self.seconds).total_seconds

# ################################################################################################################################

class Job(object):
    def __init__(self, name, start_time, interval):
        self.logger = getLogger(self.__class__.__name__)
        self.name = name
        self.start_time = start_time
        self.interval = interval

    def __str__(self):
        return '<{} at {}, name:`{}`>'.format(self.__class__.__name__, hex(id(self)), self.name)

# ################################################################################################################################

class Scheduler(object):
    def __init__(self):
        self.logger = getLogger(self.__class__.__name__)
        self.jobs = []

    def create(self, job):
        self.logger.info('Creating job `%s`', job)

    def run(self):
        pass

# ################################################################################################################################

if __name__ == '__main__':
    sched = Scheduler()
    interval = Interval(minutes=3, seconds=20)
    job = Job('test')
    sched.create(job)
    sched.run()
