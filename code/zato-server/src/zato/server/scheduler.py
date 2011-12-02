# -*- coding: utf-8 -*-

"""
Copyright (C) 2010 Dariusz Suchojad <dsuch at gefira.pl>

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import logging, time
from datetime import datetime, timedelta
from threading import Event
from traceback import format_exc

# APScheduler
from apscheduler.scheduler import Scheduler as APScheduler

# Zato 
from zato.common import scheduler_date_time_format
from zato.common.broker_message import MESSAGE_TYPE, SCHEDULER
from zato.common.util import new_rid

logger = logging.getLogger(__name__)

def _start_date(job_data):
    if isinstance(job_data.start_date, basestring):
        return datetime.strptime(job_data.start_date, scheduler_date_time_format)
    return job_data.start_date

class Scheduler(object):
    """ The Zato's job scheduler. All of the operations assume the data's being
    first validated and sanitized by relevant Zato public API services.
    """
    def __init__(self, singleton=None, init=False):
        self.singleton = singleton
        
        if init:
            self._init()
            
    def _init(self):
        self._sched = APScheduler()
        self._sched.start()
        
    def _parse_cron(self, def_):
        minute, hour, day_of_month, month, day_of_week = [elem.strip() for elem in def_.split()]
        return minute, hour, day_of_month, month, day_of_week
        
    def _on_job_execution(self, name, service, extra):
        """ Invoked by the underlying APScheduler when a job is executed. Sends
        the actual execution request to the broker so it can be picked up by
        one of the parallel server's broker clients.
        """
        msg = {'action': SCHEDULER.JOB_EXECUTED, 'name':name, 'service': service, 'extra':extra,
               'rid':new_rid()}
        self.singleton.broker_client.send_json(msg)
        
        if logger.isEnabledFor(logging.DEBUG):
            msg = 'Sent a job execution request, name [{0}], service [{1}], extra [{2}]'.format(
                name, service, extra)
            logger.debug(msg)

    def create_edit(self, action, job_data):
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
            handler(job_data)
        except Exception, e:
            msg = 'Caught exception [{0}]'.format(format_exc(e))
            logger.error(msg)
        
    def create_one_time(self, job_data):
        """ Schedules the execution of a one-time job.
        """
        start_date = _start_date(job_data)
        self._sched.add_date_job(self._on_job_execution, start_date, 
            [job_data.name, job_data.service, job_data.extra], name=job_data.name)
        
        logger.info('One-time job [{0}] scheduled'.format(job_data.name))
        
    def create_interval_based(self, job_data):
        """ Schedules the execution of an interval-based job.
        """
        start_date = _start_date(job_data)
        weeks = job_data.weeks if job_data.weeks else 0
        days = job_data.days if job_data.days else 0
        hours = job_data.hours if job_data.hours else 0
        minutes = job_data.minutes if job_data.minutes else 0
        seconds = job_data.seconds if job_data.seconds else 0
        max_runs = job_data.repeats if job_data.repeats else None
        
        self._sched.add_interval_job(self._on_job_execution, 
            weeks, days, hours, minutes,  seconds, start_date, 
            [job_data.name, job_data.service, job_data.extra], 
            name=job_data.name, max_runs=max_runs)
        
        logger.info('Interval-based job [{0}] scheduled'.format(job_data.name))
        
    def create_cron_style(self, job_data):
        """ Schedules the execution of a one-time job.
        """
        start_date = _start_date(job_data)
        minute, hour, day_of_month, month, day_of_week = self._parse_cron(job_data.cron_definition)
        self._sched.add_cron_job(self._on_job_execution, 
            year=None, month=month, day=day_of_month, hour=hour,
            minute=minute, second=None, start_date=start_date, 
            args=[job_data.name, job_data.service, job_data.extra], 
            name=job_data.name)
        
        logger.info('Cron-style job [{0}] scheduled'.format(job_data.name))

    def delete(self, job_data):
        """ Deletes the job or warns if it hasn't been scheduled.
        """
        # If there's an old_name then we're performing an edit, 
        # otherwise we're using the current name.
        _name = job_data.old_name if job_data.get('old_name') else job_data.name
        for job in self._sched.get_jobs():
            if job.name == _name:
                self._sched.unschedule_job(job)
                logger.info('Job [{0}] unscheduled'.format(_name))
                break
        else:
            logger.warn('Job [{0}] was not scheduled, could not unschedule it'.format(_name))
            
    def edit_one_time(self, job_data):
        """ First deletes a one-time job and then schedules its execution. 
        The operations aren't parts of an atomic transaction.
        """
        self.delete(job_data)
        self.create_one_time(job_data)
        
    def edit_interval_based(self, job_data):
        """ First deletes an interval-based job and then schedules its execution. 
        The operations aren't parts of an atomic transaction.
        """
        self.delete(job_data)
        self.create_interval_based(job_data)
        
    def edit_cron_style(self, job_data):
        """ First deletes a cron-style job and then schedules its execution. 
        The operations aren't parts of an atomic transaction.
        """
        self.delete(job_data)
        self.create_cron_style(job_data)
            
    def execute(self, job_data):
        for job in self._sched.get_jobs():
            if job.name == job_data.name:
                self._on_job_execution(*job.args)
                logger.info('Job [{0}] executed'.format(job_data.name))
                break
        else:
            logger.warn('Job [{0}] is not scheduled, could not execute it'.format(job_data.name))
        
if __name__ == '__main__':
    from bunch import Bunch
    job_data1 = Bunch(
        {"name": "zzz", 
         "service": "zato.server.service.internal.Ping", 
         "extra": "aabbcc", 
         "job_type": 
         "cron_style", 
         "cron_definition": "* * * * *", 
         "is_active": True, 
         "action": "1000", 
         "start_date": "2011-10-14 22:36:00"}
    )
    
    job_data2 = Bunch({'name':'zzz'})
    
    s = Scheduler()
    s.create(job_data1)
    #s.delete(job_data2)
    s.execute(job_data2)
    
    import time
    time.sleep(100)
