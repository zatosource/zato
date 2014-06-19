# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at zato.io>

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging
from traceback import format_exc

# crontab
from crontab import CronTab

# dateutil
from dateutil.parser import parse

# gevent
from gevent import sleep, spawn

# Zato 
from zato.common import CHANNEL, DATA_FORMAT, ENSURE_SINGLETON_JOB, SCHEDULER
from zato.common.broker_message import MESSAGE_TYPE, SCHEDULER as SCHEDULER_MSG, SERVICE
from zato.common.scheduler import Interval, Job, Scheduler as _Scheduler
from zato.common.util import new_cid

logger = logging.getLogger('zato_scheduler')

def _start_date(job_data):
    if isinstance(job_data.start_date, basestring):
        return parse(job_data.start_date)
    return job_data.start_date

class Scheduler(object):
    """ The Zato's job scheduler. All of the operations assume the data's being
    first validated and sanitized by relevant Zato public API services.
    """
    def __init__(self, singleton=None, init=False):
        self.singleton = singleton
        self.broker_token = None
        self.client_push_broker_pull = None
        self.sched = _Scheduler(self.on_job_executed)

        if init:
            self.init()

    def init(self):
        spawn(self.sched.run)

        while not self.sched.ready:
            sleep(0.1)

# ################################################################################################################################

    def on_job_executed(self, ctx):
        """ Invoked by the underlying scheduler when a job is executed. Sends
        the actual execution request to the broker so it can be picked up by
        one of the parallel server's broker clients.
        """
        name = ctx['name']

        msg = {
            'action': SCHEDULER_MSG.JOB_EXECUTED,
            'name':name,
            'service': ctx['cb_kwargs']['service'], 
            'payload':ctx['cb_kwargs']['extra'],
            'cid':ctx['cid'],
            'job_type': ctx['type']
        }

        # Special case an internal job that needs to be delivered to all parallel
        # servers.
        if name == ENSURE_SINGLETON_JOB:
            self.singleton.broker_client.publish(msg)
        else:
            self.singleton.broker_client.invoke_async(msg)

        if logger.isEnabledFor(logging.DEBUG):
            msg = 'Sent a job execution request, name [{}], service [{}], extra [{}]'.format(
                name, ctx['cb_kwargs']['service'], ctx['cb_kwargs']['extra'])
            logger.debug(msg)

        # Now, if it was a one-time job, it needs to be deactivated.
        if ctx['type'] == SCHEDULER.JOB_TYPE.ONE_TIME:
            msg = {
                'action': SERVICE.PUBLISH,
                'service': 'zato.scheduler.job.set-active-status',
                'payload': {'id':ctx['id'], 'is_active':False},
                'cid': new_cid(),
                'channel': CHANNEL.SCHEDULER,
                'data_format': DATA_FORMAT.JSON,
            }
            self.singleton.broker_client.publish(msg)

# ################################################################################################################################

    def create_edit(self, action, job_data, broker_msg_type=MESSAGE_TYPE.TO_PARALLEL_ANY):
        """ Invokes a handler appropriate for the given action and job_data.job_type.
        """
        if logger.isEnabledFor(logging.DEBUG):
            logger.debug(job_data)

        if not job_data.is_active:
            msg = 'Job [{0}] is not active, not scheduling it'.format(job_data.name)
            logger.info(msg)
            return

        handler = '{0}_{1}'.format(action, job_data.job_type)
        handler = getattr(self, handler)

        try:
            handler(job_data, broker_msg_type)
        except Exception, e:
            msg = 'Caught exception [{0}]'.format(format_exc(e))
            logger.error(msg)

# ################################################################################################################################

    def create_edit_job(self, id, name, start_time, job_type, service, is_create=True, max_repeats=1, days=0, hours=0,
            minutes=0, seconds=0, extra=None, cron_definition=None):
        """ A base method for scheduling of jobs.
        """
        cb_kwargs = {
            'service': service,
            'extra': extra,
        }

        if job_type == SCHEDULER.JOB_TYPE.CRON_STYLE:
            interval = CronTab(cron_definition)
        else:
            interval = Interval(days=days, hours=hours, minutes=minutes, seconds=seconds)

        job = Job(id, name, job_type, interval, start_time, cb_kwargs=cb_kwargs, max_repeats=max_repeats,
            cron_definition=cron_definition)

        func = self.sched.create if is_create else self.sched.edit
        func(job)

# ################################################################################################################################

    def create_edit_one_time(self, job_data, broker_msg_type, is_create=True):
        """ Re-/schedules the execution of a one-time job.
        """
        self.create_edit_job(job_data.id, job_data.name, _start_date(job_data), SCHEDULER.JOB_TYPE.ONE_TIME,
            job_data.service, is_create)

    def create_one_time(self, job_data, broker_msg_type):
        """ Schedules the execution of a one-time job.
        """
        self.create_edit_one_time(job_data, broker_msg_type)

    def edit_one_time(self, job_data, broker_msg_type):
        """ First unschedules a one-time job and then schedules its execution. 
        The operations aren't parts of an atomic transaction.
        """
        self.create_edit_one_time(job_data, broker_msg_type, False)

# ################################################################################################################################

    def create_edit_interval_based(self, job_data, broker_msg_type, is_create=True):
        """ Re-/schedules the execution of an interval-based job.
        """
        start_date = _start_date(job_data)
        weeks = job_data.weeks if job_data.get('weeks') else 0
        days = job_data.days if job_data.get('days') else 0
        hours = job_data.hours if job_data.get('hours') else 0
        minutes = job_data.minutes if job_data.get('minutes') else 0
        seconds = job_data.seconds if job_data.get('seconds') else 0
        max_repeats = job_data.repeats if job_data.get('repeats') else None

        self.create_edit_job(job_data.id, job_data.name, start_date, SCHEDULER.JOB_TYPE.INTERVAL_BASED, job_data.service,
            is_create, max_repeats, days+weeks*7, hours, minutes, seconds, job_data.extra, )

    def create_interval_based(self, job_data, broker_msg_type):
        """ Schedules the execution of an interval-based job.
        """
        self.create_edit_interval_based(job_data, broker_msg_type)

    def edit_interval_based(self, job_data, broker_msg_type):
        """ First unschedules an interval-based job and then schedules its execution. 
        The operations aren't parts of an atomic transaction.
        """
        self.create_edit_interval_based(job_data, broker_msg_type, False)

# ################################################################################################################################

    def create_edit_cron_style(self, job_data, broker_msg_type, is_create=True):
        """ Re-/schedules the execution of a cron-style job.
        """
        start_date = _start_date(job_data)
        self.create_edit_job(job_data.id, job_data.name, start_date, SCHEDULER.JOB_TYPE.CRON_STYLE, job_data.service,
            is_create, max_repeats=None, extra=job_data.extra, cron_definition=job_data.cron_definition)

    def create_cron_style(self, job_data, broker_msg_type):
        """ Schedules the execution of a cron-style job.
        """
        self.create_edit_cron_style(job_data, broker_msg_type)

    def edit_cron_style(self, job_data, broker_msg_type):
        """ First unschedules a cron-style job and then schedules its execution. 
        The operations aren't parts of an atomic transaction.
        """
        self.create_edit_cron_style(job_data, broker_msg_type, False)

# ################################################################################################################################

    def delete(self, job_data):
        """ Deletes the job from the scheduler.
        """
        self.sched.unschedule_by_name(job_data.old_name if job_data.get('old_name') else job_data.name)

# ################################################################################################################################

    def execute(self, job_data):
        self.sched.execute(job_data.name)

# ################################################################################################################################

    def stop(self):
        self.sched.stop()

# ################################################################################################################################