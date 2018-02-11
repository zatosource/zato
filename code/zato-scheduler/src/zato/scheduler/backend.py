# -*- coding: utf-8 -*-

"""
Copyright (C) 2018, Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
import datetime
from logging import getLogger, DEBUG
from traceback import format_exc

# datetime
from dateutil.rrule import rrule, SECONDLY

# gevent
import gevent # Imported directly so it can be mocked out in tests
from gevent import lock

# paodate
from paodate import Delta

# Paste
from paste.util.converters import asbool

# Zato
from zato.common import SCHEDULER
from zato.common.util import add_scheduler_jobs, add_startup_jobs, make_repr, new_cid, spawn_greenlet

logger = getLogger(__name__)

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

    __repr__ = __str__

    def get_in_seconds(self):
        return Delta(days=self.days, hours=self.hours, minutes=self.minutes, seconds=self.seconds).total_seconds

# ################################################################################################################################

class Job(object):
    def __init__(self, id, name, type, interval, start_time=None, callback=None, cb_kwargs=None, max_repeats=None,
            on_max_repeats_reached_cb=None, is_active=True, clone_start_time=False, cron_definition=None):
        self.id = id
        self.name = name
        self.type = type
        self.interval = interval
        self.callback = callback
        self.cb_kwargs = cb_kwargs or {}
        self.max_repeats = max_repeats
        self.on_max_repeats_reached_cb = on_max_repeats_reached_cb
        self.is_active = is_active
        self.cron_definition = cron_definition

        self.current_run = 0 # Starts over each time scheduler is started
        self.max_repeats_reached = False
        self.max_repeats_reached_at = None
        self.keep_running = True

        if clone_start_time:
            self.start_time = start_time

        elif self.type == SCHEDULER.JOB_TYPE.CRON_STYLE:
            now = datetime.datetime.utcnow()
            self.start_time = now + datetime.timedelta(seconds=(self.get_sleep_time(now)))

        else:
            self.start_time = self.get_start_time(start_time if start_time is not None else datetime.datetime.utcnow())

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

    def clone(self):
        return Job(self.id, self.name, self.type, self.interval, self.start_time, self.callback, self.cb_kwargs, self.max_repeats,
            self.on_max_repeats_reached_cb, self.is_active, True, self.cron_definition)

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

        if start_time > now:
            return start_time

        first_run_time = start_time + interval

        if first_run_time > now:
            return first_run_time

        else:
            runs = rrule(SECONDLY, interval=int(self.interval.in_seconds), dtstart=start_time, count=self.max_repeats)
            last_run_time = runs.before(now)
            next_run_time = last_run_time + interval

            if next_run_time >= now:
                return next_run_time

            # The assumption here is that all one-time jobs are always active at the instant we evaluate them here.
            elif next_run_time < now and self.type == SCHEDULER.JOB_TYPE.ONE_TIME and self.is_active:

                # The delay is 100% arbitrary
                return now + datetime.timedelta(seconds=10)

            else:
                # We must have already run out of iterations
                self.max_repeats_reached = True
                self.max_repeats_reached_at = next_run_time
                self.keep_running = False

                logger.warn(
                    'Cannot compute start_time. Job `%s` max repeats reached at `%s` (UTC)',
                    self.name, self.max_repeats_reached_at)

    def get_context(self):
        ctx = {
            'cid':new_cid(),
            'start_time': self.start_time.isoformat(),
            'cb_kwargs': self.cb_kwargs
        }

        if self.type == SCHEDULER.JOB_TYPE.CRON_STYLE:
            ctx['cron_definition'] = self.cron_definition
        else:
            ctx['interval_in_seconds'] = self.interval.in_seconds

        for name in 'id', 'name', 'current_run', 'max_repeats_reached', 'max_repeats', 'type':
            ctx[name] = getattr(self, name)

        return ctx

    def get_sleep_time(self, now):
        """ Returns a number of seconds the job should sleep for before the next run.
        For interval-based jobs this is a constant value pre-computed well ahead by self.interval
        but for cron-style jobs the value is obtained each time it's needed.
        """
        if self.type == SCHEDULER.JOB_TYPE.INTERVAL_BASED:
            return self.interval.in_seconds
        elif self.type == SCHEDULER.JOB_TYPE.CRON_STYLE:
            return self.interval.next(now)
        else:
            raise ValueError('Unsupported job type `{}` ({})'.format(self.type, self.name))

    def _spawn(self, *args, **kwargs):
        """ A thin wrapper so that it is easier to mock this method out in unit-tests.
        """
        return spawn_greenlet(*args, **kwargs)

    def main_loop(self):

        if logger.isEnabledFor(DEBUG):
            logger.debug('Job entering main loop `%s`', self)

        _sleep = gevent.sleep

        try:
            while self.keep_running:
                try:
                    self.current_run += 1

                    # Perhaps we've already been executed enough times
                    if self.max_repeats and self.current_run == self.max_repeats:
                        self.keep_running = False
                        self.max_repeats_reached = True
                        self.max_repeats_reached_at = datetime.datetime.utcnow()

                        if self.on_max_repeats_reached_cb:
                            self.on_max_repeats_reached_cb(self)

                    # Invoke callback in a new greenlet so it doesn't block the current one.
                    self._spawn(self.callback, **{'ctx':self.get_context()})

                except Exception, e:
                    logger.warn(format_exc(e))

                finally:
                    # Pause the greenlet for however long is needed if it is not a one-off job
                    if self.type == SCHEDULER.JOB_TYPE.ONE_TIME:
                        return True
                    else:
                        _sleep(self.get_sleep_time(datetime.datetime.utcnow()))

            if logger.isEnabledFor(DEBUG):
                logger.debug('Job leaving main loop `%s` after %d iterations', self, self.current_run)

        except Exception, e:
            logger.warn(format_exc(e))

        return True

    def run(self):

        # OK, we're ready
        try:

            if not self.start_time:
                logger.warn('Job `%s` cannot start without start_time set', self.name)
                return

            if logger.isEnabledFor(DEBUG):
                logger.debug('Job starting `%s`', self)

            _utcnow = datetime.datetime.utcnow
            _sleep = gevent.sleep

            # If the job has a start time in the future, sleep until it's ready to go.
            now = _utcnow()

            while self.start_time > now:
                _sleep(self.wait_sleep_time)

                if self.wait_iter_cb:
                    self.wait_iter_cb(self.start_time, now, *self.wait_iter_cb_args)

                now = _utcnow()

            self.main_loop()

        except Exception, e:
            logger.warn(format_exc(e))

# ################################################################################################################################

class Scheduler(object):
    def __init__(self, config, api):
        self.config = config
        self.api = api
        self.on_job_executed_cb = config.on_job_executed_cb
        self.startup_jobs = config.startup_jobs
        self.odb = config.odb
        self.jobs = set()
        self.job_greenlets = {}
        self.keep_running = True
        self.lock = lock.RLock()
        self.sleep_time = 0.1
        self.iter_cb = None
        self.iter_cb_args = ()
        self.ready = False
        self._add_startup_jobs = config._add_startup_jobs
        self._add_scheduler_jobs = config._add_scheduler_jobs
        self.job_log = getattr(logger, config.job_log_level)
        self._has_debug = logger.isEnabledFor(DEBUG)

    def on_max_repeats_reached(self, job):
        with self.lock:
            job.is_active = False

    def _create(self, job, spawn=True):
        """ Actually creates a job. Must be called with self.lock held.
        """
        try:
            self.jobs.add(job)

            if job.is_active:
                if spawn:
                    self.spawn_job(job)

                    if self._has_debug:
                        logger.debug('Job scheduled `%s`', job)
                    else:
                        self.job_log('Job scheduled `%s` (%s, start: %s UTC)', job.name, job.type, job.start_time)

            else:
                logger.warn('Skipping inactive job `%s`', job)
        except Exception, e:
            logger.warn(format_exc(e))

    def create(self, *args, **kwargs):
        with self.lock:
            self._create(*args, **kwargs)

    def edit(self, job):
        """ Edits a job - this means an already existing job is unscheduled and created again,
        i.e. it's not an in-place update.
        """
        with self.lock:
            self.unschedule(job)
            self.create(job.clone(), True)

    def _unschedule(self, job):
        """ Actually unschedules a job. Must be called with self.lock held.
        """
        found = False
        job.keep_running = False

        if job in self.jobs:
            self.jobs.remove(job)
            found = True

        if job.name in self.job_greenlets:
            self.job_greenlets[job.name].kill(block=False, timeout=2.0)
            del self.job_greenlets[job.name]
            found = True

        return found

    def _unschedule_stop(self, job, message):
        """ API for job deletion and stopping. Must be called with a self.lock held.
        """
        if self._unschedule(job):
            if logger.isEnabledFor(DEBUG):
                logger.debug('Job %s `%s`', message, job)
            else:
                logger.info('Job %s `%s` (%s)', message, job.name, job.type)
        else:
            logger.debug('Job not found `%s`', job)

    def unschedule(self, job):
        """ Deletes a job.
        """
        with self.lock:
            self._unschedule_stop(job, 'unscheduled')

    def unschedule_by_name(self, name):
        """ Deletes a job by its name.
        """
        _job = None

        with self.lock:
            for job in self.jobs:
                if job.name == name:
                    _job = job
                    break

        # We can't do it with self.lock because deleting changes the set = RuntimeError
        if _job:
            self.unschedule(job)

    def stop_job(self, job):
        """ Stops a job by deleting it.
        """
        with self.lock:
            self._unschedule_stop(job, 'stopped')

    def stop(self):
        """ Stops all jobs and the scheduler itself.
        """
        with self.lock:
            jobs = sorted(job for job in self.jobs)
            for job in jobs:
                self._unschedule_stop(job.clone(), 'stopped')

    def sleep(self, value):
        """ A method introduced so the class is easier to mock out in tests.
        """
        gevent.sleep(value)

    def execute(self, name):
        """ Executes a job no matter if it's active or not. One-time job are not unscheduled afterwards.
        """
        with self.lock:
            for job in self.jobs:
                if job.name == name:
                    self.on_job_executed(job.get_context(), False)
                    break
            else:
                logger.warn('No such job `%s` in `%s`', name, [elem.get_context() for elem in self.jobs])

    def on_job_executed(self, ctx, unschedule_one_time=True):
        logger.debug('Executing `%s`, `%s`', ctx['name'], ctx)
        self.on_job_executed_cb(ctx)
        self.job_log('Job executed `%s`, `%s`', ctx['name'], ctx)

        if ctx['type'] == SCHEDULER.JOB_TYPE.ONE_TIME and unschedule_one_time:
            self.unschedule_by_name(ctx['name'])

    def _spawn(self, *args, **kwargs):
        """ As in the Job class, this is a thin wrapper so that it is easier to mock this method out in unit-tests.
        """
        return spawn_greenlet(*args, **kwargs)

    def spawn_job(self, job):
        """ Spawns a job's greenlet. Must be called with self.lock held.
        """
        job.callback = self.on_job_executed
        job.on_max_repeats_reached_cb = self.on_max_repeats_reached
        self.job_greenlets[job.name] = self._spawn(job.run)

    def run(self):

        try:

            # Add the statistics-related scheduler jobs to the ODB
            if self._add_startup_jobs:
                cluster_conf = self.config.main.cluster
                add_startup_jobs(cluster_conf.id, self.odb, self.startup_jobs, asbool(cluster_conf.stats_enabled))

            # All other jobs
            if self._add_scheduler_jobs:
                add_scheduler_jobs(self.api, self.odb, self.config.main.cluster.id, spawn=False)

            _sleep = self.sleep
            _sleep_time = self.sleep_time

            with self.lock:
                for job in sorted(self.jobs):
                    if job.max_repeats_reached:
                        logger.info('Job `%s` already reached max runs count (%s UTC)', job.name, job.max_repeats_reached_at)
                    else:
                        self.spawn_job(job)

            # Ok, we're good now.
            self.ready = True

            logger.info('Scheduler started')

            while self.keep_running:
                _sleep(_sleep_time)

                if self.iter_cb:
                    self.iter_cb(*self.iter_cb_args)

        except Exception, e:
            logger.warn(format_exc(e))
