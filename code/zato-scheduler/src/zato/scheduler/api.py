# -*- coding: utf-8 -*-

"""
Copyright (C) 2023, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import logging
from traceback import format_exc

# ciso8601
try:
    from zato.common.util.api import parse_datetime
except ImportError:
    from dateutil.parser import parse as parse_datetime

# crontab
from crontab import CronTab

# gevent
from gevent import sleep

# Zato
from zato.common.api import MISC, SCHEDULER, ZATO_NONE
from zato.common.broker_message import SCHEDULER as SCHEDULER_MSG
from zato.common.util.api import new_cid, spawn_greenlet
from zato.common.util.config import parse_url_address
from zato.scheduler.backend import Interval, Job, Scheduler as _Scheduler

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.broker.client import BrokerClient
    from zato.common.typing_ import strdict, strdictnone
    from zato.scheduler.server import SchedulerServerConfig
    BrokerClient = BrokerClient

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger('zato_scheduler')
_has_debug = logger.isEnabledFor(logging.DEBUG)

# ################################################################################################################################
# ################################################################################################################################

def _start_date(job_data):
    if isinstance(job_data.start_date, str):
        # Remove timezone information as we assume that all times are in UTC
        start_date = job_data.start_date.split('+')
        start_date = start_date[0]
        return parse_datetime(start_date)
    return job_data.start_date

# ################################################################################################################################
# ################################################################################################################################

class SchedulerAPI:
    """ The job scheduler server. All of the operations assume the data was already validated
    by relevant Zato public API services.
    """
    def __init__(self, config:'SchedulerServerConfig'=None, run:'bool'=False):
        self.config = config
        self.broker_client = None # type: BrokerClient
        self.config.on_job_executed_cb = self.on_job_executed
        self.scheduler = _Scheduler(self.config, self)

        if run:
            self.serve_forever()

# ################################################################################################################################

    def serve_forever(self):
        try:
            try:
                spawn_greenlet(self.scheduler.run)
            except Exception:
                logger.warning(format_exc())

            while not self.scheduler.ready:
                sleep(0.1)

        except Exception:
            logger.warning(format_exc())

# ################################################################################################################################

    def invoke_service(self, name:'str', request:'strdictnone'=None) -> 'strdict':

        # Make sure we have a request to send
        request = request or {}

        # Assume there is no response until we have one
        response = None

        # Enrich the business data ..
        request['cluster_id'] = MISC.Default_Cluster_ID

        # .. keep looping until we have a response ..
        while not response:

            try:
                # .. log what we are about to do ..
                logger.info(f'Invoking service `{name}` with `{request}`')

                # .. invoke the server ..
                response = self.broker_client.zato_client.invoke(name, request, timeout=0.5)

            except Exception as e:

                logger.info(f'Service invocation error -> `{name}` -> {e}')

            finally:

                # .. if there is still none, wait a bit longer ..
                logger.info(f'Waiting for response from service `{name}`')

                # .. do wait now ..
                sleep(1)

        # .. if we are here, we have a response to return.
        logger.info(f'Returning response from service {name}')
        return response.data

# ################################################################################################################################

    def on_job_executed(self, ctx, extra_data_format=ZATO_NONE):
        """ Invoked by the underlying scheduler when a job is executed. Sends the actual execution request to the broker
        so it can be picked up by one of the parallel server's broker clients.
        """
        name = ctx['name']

        payload = ctx['cb_kwargs']['extra']
        if isinstance(payload, bytes):
            payload = payload.decode('utf8')

        msg = {
            'action': SCHEDULER_MSG.JOB_EXECUTED.value,
            'name':name,
            'service': ctx['cb_kwargs']['service'],
            'payload':payload,
            'cid':ctx['cid'],
            'job_type': ctx['type']
        }

        if extra_data_format != ZATO_NONE:
            msg['data_format'] = extra_data_format

        self.broker_client.invoke_async(msg, from_scheduler=True)

        if _has_debug:
            msg = 'Sent a job execution request, name [{}], service [{}], extra [{}]'.format(
                name, ctx['cb_kwargs']['service'], ctx['cb_kwargs']['extra'])
            logger.debug(msg)

        # Now, if it was a one-time job, it needs to be deactivated.
        if ctx['type'] == SCHEDULER.JOB_TYPE.ONE_TIME:
            msg = {
                'action': SCHEDULER_MSG.DELETE.value,
                'service': 'zato.scheduler.job.delete',
                'payload': {
                    'id':ctx['id'],
                },
                'cid': new_cid(),
            }
            self.broker_client.publish(msg, from_scheduler=True)

# ################################################################################################################################

    def create_edit(self, action, job_data, **kwargs):
        """ Invokes a handler appropriate for the given action and job_data.job_type.
        """
        handler = '{0}_{1}'.format(action, job_data.job_type)
        handler = getattr(self, handler)

        try:
            handler(job_data, **kwargs)
        except Exception:
            logger.error('Caught exception `%s`', format_exc())

# ################################################################################################################################

    def create_edit_job(self, id, name, old_name, start_time, job_type, service, is_create=True, max_repeats=1, days=0, hours=0,
            minutes=0, seconds=0, extra=None, cron_definition=None, is_active=None, **kwargs):
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
            is_active=is_active, cron_definition=cron_definition, service=service, extra=extra, old_name=old_name)

        func = self.scheduler.create if is_create else self.scheduler.edit
        func(job, **kwargs)

# ################################################################################################################################

    def create_edit_one_time(self, job_data, is_create=True, **kwargs):
        """ Re-/schedules the execution of a one-time job.
        """
        self.create_edit_job(job_data.id, job_data.name, job_data.get('old_name'), _start_date(job_data),
            SCHEDULER.JOB_TYPE.ONE_TIME, job_data.service, is_create, extra=job_data.extra,
            is_active=job_data.is_active, **kwargs)

    def create_one_time(self, job_data, **kwargs):
        """ Schedules the execution of a one-time job.
        """
        self.create_edit_one_time(job_data, **kwargs)

    def edit_one_time(self, job_data, **kwargs):
        """ First unschedules a one-time job and then schedules its execution.
        The operations aren't parts of an atomic transaction.
        """
        self.create_edit_one_time(job_data, False, **kwargs)

# ################################################################################################################################

    def create_edit_interval_based(self, job_data, is_create=True, **kwargs):
        """ Re-/schedules the execution of an interval-based job.
        """
        start_date = _start_date(job_data)

        weeks = job_data.weeks if job_data.get('weeks') else 0
        days = job_data.days if job_data.get('days') else 0
        hours = job_data.hours if job_data.get('hours') else 0
        minutes = job_data.minutes if job_data.get('minutes') else 0
        seconds = job_data.seconds if job_data.get('seconds') else 0
        max_repeats = job_data.repeats if job_data.get('repeats') else None

        weeks = int(weeks)
        days = int(days)
        hours = int(hours)
        minutes = int(minutes)
        seconds = int(seconds)
        max_repeats = int(max_repeats) if max_repeats is not None else max_repeats

        self.create_edit_job(job_data.id, job_data.name, job_data.get('old_name'), start_date, SCHEDULER.JOB_TYPE.INTERVAL_BASED,
            job_data.service, is_create, max_repeats, days+weeks*7, hours, minutes, seconds, job_data.extra,
            is_active=job_data.is_active, **kwargs)

    def create_interval_based(self, job_data, **kwargs):
        """ Schedules the execution of an interval-based job.
        """
        self.create_edit_interval_based(job_data, **kwargs)

    def edit_interval_based(self, job_data, **kwargs):
        """ First unschedules an interval-based job and then schedules its execution.
        The operations aren't parts of an atomic transaction.
        """
        self.create_edit_interval_based(job_data, False, **kwargs)

# ################################################################################################################################

    def create_edit_cron_style(self, job_data,  is_create=True, **kwargs):
        """ Re-/schedules the execution of a cron-style job.
        """
        start_date = _start_date(job_data)
        self.create_edit_job(job_data.id, job_data.name, job_data.get('old_name'), start_date, SCHEDULER.JOB_TYPE.CRON_STYLE,
            job_data.service, is_create, max_repeats=None, extra=job_data.extra, is_active=job_data.is_active,
            cron_definition=job_data.cron_definition, **kwargs)

    def create_cron_style(self, job_data,  **kwargs):
        """ Schedules the execution of a cron-style job.
        """
        self.create_edit_cron_style(job_data,  **kwargs)

    def edit_cron_style(self, job_data,  **kwargs):
        """ First unschedules a cron-style job and then schedules its execution.
        The operations aren't parts of an atomic transaction.
        """
        self.create_edit_cron_style(job_data, False, **kwargs)

# ################################################################################################################################

    def delete(self, job_data, **kwargs):
        """ Deletes the job from the scheduler.
        """
        old_name = job_data.get('old_name')
        name = job_data.old_name if old_name else job_data.name

        logger.info('Deleting job %s (old_name:%s)', name, old_name)

        self.scheduler.unschedule_by_name(name, **kwargs)

# ################################################################################################################################

    def execute(self, job_data):
        self.scheduler.execute(job_data.name)

# ################################################################################################################################

    def stop(self):
        self.scheduler.stop()

# ################################################################################################################################

    def filter(self, *ignored):
        """ Accept broker messages destined to our client.
        """
        return True

# ################################################################################################################################

    def on_broker_msg_SCHEDULER_CREATE(self, msg, *ignored_args):
        self.create_edit('create', msg)

# ################################################################################################################################

    def on_broker_msg_SCHEDULER_EDIT(self, msg, *ignored_args):
        self.create_edit('edit', msg)

# ################################################################################################################################

    def on_broker_msg_SCHEDULER_DELETE(self, msg, *ignored_args):
        self.delete(msg)

# ################################################################################################################################

    def on_broker_msg_SCHEDULER_EXECUTE(self, msg, *ignored_args):
        self.execute(msg)

# ################################################################################################################################

    def on_broker_msg_SCHEDULER_SET_SERVER_ADDRESS(self, msg, *ignored_args):
        url = parse_url_address(msg.address, SCHEDULER.Default_Server_Port)
        self.broker_client.set_zato_client_address(url)
        logger.info('Set server address to -> %s', url)

# ################################################################################################################################
# ################################################################################################################################
