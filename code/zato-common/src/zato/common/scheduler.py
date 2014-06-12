# -*- coding: utf-8 -*-

"""
Copyright (C) 2014 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from logging import basicConfig, getLogger, INFO

logger = getLogger(__name__)

basicConfig(level=INFO)

# ################################################################################################################################

class Job(object):
    def __init__(self, name):
        self.logger = getLogger(self.__class__.__name__)
        self.name = name

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
    job = Job('test')
    sched.create(job)
    sched.run()
