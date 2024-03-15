# -*- coding: utf-8 -*-

"""
Copyright (C) 2022, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import datetime
from logging import getLogger
from traceback import format_exc

# datetime
from dateutil.rrule import rrule, SECONDLY

# gevent
import gevent # Imported directly so it can be mocked out in tests
from gevent import lock, sleep

# paodate
from paodate import Delta

# Python 2/3 compatibility
from zato.common.ext.future.utils import iterkeys, itervalues

# Zato
from zato.common.api import FILE_TRANSFER, SCHEDULER
from zato.common.util.api import asbool, make_repr, new_cid, spawn_greenlet
from zato.common.util.scheduler import load_scheduler_jobs_by_api, load_scheduler_jobs_by_odb, add_startup_jobs_to_odb_by_api, \
    add_startup_jobs_to_odb_by_odb
from zato.scheduler.cleanup.cli import start_cleanup

# ################################################################################################################################
# ################################################################################################################################

if 0:
    from zato.common.typing_ import stranydict
    from zato.scheduler.server import SchedulerServerConfig, SchedulerAPI

# ################################################################################################################################
# ################################################################################################################################

logger = getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

initial_sleep = 0.1

# ################################################################################################################################
# ################################################################################################################################

class Interval:
    def __init__(self, days:'int'=0, hours:'int'=0, minutes:'int'=0, seconds:'int'=0, in_seconds:'int'=0) -> 'None':
        self.days = int(days) if days else days
        self.hours = int(hours) if hours else hours
        self.minutes = int(minutes) if minutes else minutes
        self.seconds = int(seconds) if seconds else seconds
        self.in_seconds = in_seconds or self.get_in_seconds()

    def __str__(self):
        return make_repr(self)

    __repr__ = __str__

    def get_in_seconds(self):
        return Delta(days=self.days, hours=self.hours, minutes=self.minutes, seconds=self.seconds).total_seconds

# ################################################################################################################################
# ################################################################################################################################

class Job:
    def __init__(self, id, name, type, interval, start_time=None, callback=None, cb_kwargs=None, max_repeats=None,
            on_max_repeats_reached_cb=None, is_active=True, clone_start_time=False, cron_definition=None, service=None,
            extra=None, old_name=None):
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
        self.service = service
        self.extra = extra

        # This is used by the edit action to be able to discern if an edit did not include a rename
        self.old_name = old_name

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

# ################################################################################################################################

    def __str__(self):
        return make_repr(self)

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other):
        return self.name == other.name

    def __lt__(self, other):
        return self.name < other.name

# ################################################################################################################################

    def clone(self, name=None, is_active=None):

        # It will not be None if an edit changed it from True to False or the other way around
        is_active = is_active if is_active is not None else self.is_active

        return Job(self.id, self.name, self.type, self.interval, self.start_time, self.callback, self.cb_kwargs,
            self.max_repeats, self.on_max_repeats_reached_cb, is_active, True, self.cron_definition, self.service,
            self.extra)

# ################################################################################################################################

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

                logger.info(
                    'Cannot compute start_time. Job `%s` max repeats reached at `%s` (UTC)',
                    self.name, self.max_repeats_reached_at)

# ################################################################################################################################

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

# ################################################################################################################################

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

# ################################################################################################################################

    def _spawn(self, *args, **kwargs):
        """ A thin wrapper so that it is easier to mock this method out in unit-tests.
        """
        return spawn_greenlet(*args, **kwargs)

    def main_loop(self):

        logger.info('Job entering main loop `%s`', self)

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

                except Exception:
                    logger.warning(format_exc())

                finally:
                    # pylint: disable=lost-exception

                    # Pause the greenlet for however long is needed if it is not a one-off job
                    if self.type == SCHEDULER.JOB_TYPE.ONE_TIME:
                        return True
                    else:
                        _sleep(self.get_sleep_time(datetime.datetime.utcnow()))

            logger.info('Job leaving main loop `%s` after %d iterations', self, self.current_run)

        except Exception:
            logger.warning(format_exc())

        return True

# ################################################################################################################################

    def run(self):

        # OK, we're ready
        try:

            # If we are a job that triggers file transfer channels we do not start
            # unless our extra data is filled in. Otherwise, we would not trigger any transfer anyway.
            if self.service == FILE_TRANSFER.SCHEDULER_SERVICE and (not self.extra):
                logger.warning('Skipped file transfer job `%s` without extra set `%s` (%s)', self.name, self.extra, self.service)
                return

            if not self.start_time:
                logger.warning('Job `%s` cannot start without start_time set', self.name)
                return

            logger.info('Job starting `%s`', self)

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

        except Exception:
            logger.warning(format_exc())

# ################################################################################################################################
# ################################################################################################################################

class Scheduler:

    def __init__(self, config:'SchedulerServerConfig', api:'SchedulerAPI') -> 'None':
        self.config = config
        self.api = api
        self.on_job_executed_cb = config.on_job_executed_cb
        self.current_status = config.current_status
        self.startup_jobs = config.startup_jobs
        self.odb = config.odb
        self.jobs = {}
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
        self.initial_sleep_time = self.config.main.get('misc', {}).get('initial_sleep_time') or SCHEDULER.InitialSleepTime

        # We set it to True for backward compatibility with pre-3.2
        self.prefer_odb_config = self.config.raw_config.server.get('server_prefer_odb_config', True)

# ################################################################################################################################

    def on_max_repeats_reached(self, job):
        with self.lock:
            job.is_active = False

# ################################################################################################################################

    def _create(self, job, spawn=True):
        """ Actually creates a job. Must be called with self.lock held.
        """
        try:
            self.jobs[job.name] = job
            if job.is_active:
                if spawn:
                    self.spawn_job(job)
                    self.job_log('Job scheduled `%s` (%s, start: %s UTC)', job.name, job.type, job.start_time)
            else:
                logger.info('Skipping inactive job `%s`', job)
        except Exception:
            logger.warning(format_exc())

# ################################################################################################################################

    def create(self, *args, **kwargs):
        with self.lock:
            self._create(*args, **kwargs)

# ################################################################################################################################

    def edit(self, job):
        """ Edits a job - this means an already existing job is unscheduled and created again,
        i.e. it's not an in-place update.
        """
        with self.lock:
            self._unschedule_stop(job, '(src:edit)')
            self._create(job.clone(job.is_active), True)

# ################################################################################################################################

    def _unschedule(self, job):
        """ Actually unschedules a job. Must be called with self.lock held.
        """
        # The job could have been renamed so we need to unschedule it by the previous name, if there is one
        name = job.old_name if job.old_name else job.name
        found = False
        job.keep_running = False

        if name in iterkeys(self.jobs):
            del self.jobs[name]
            found = True

        if name in iterkeys(self.job_greenlets):
            self.job_greenlets[name].kill(block=False, timeout=2.0)
            del self.job_greenlets[name]
            found = True

        return found

# ################################################################################################################################

    def _unschedule_stop(self, job, message):
        """ API for job deletion and stopping. Must be called with a self.lock held.
        """
        if self._unschedule(job):
            name = job.old_name if job.old_name else job.name
            logger.info('Unscheduled %s job %s `%s`', job.type, name, message)
        else:
            logger.info('Job not found `%s`', job)

# ################################################################################################################################

    def unschedule(self, job):
        """ Deletes a job.
        """
        with self.lock:
            self._unschedule_stop(job, '(src:unschedule)')

# ################################################################################################################################

    def unschedule_by_name(self, name):
        """ Deletes a job by its name.
        """
        _job = None

        with self.lock:
            for job in itervalues(self.jobs):
                if job.name == name:
                    _job = job
                    break

        # We can't do it with self.lock because deleting changes the set = RuntimeError
        if _job:
            self.unschedule(job)

# ################################################################################################################################

    def stop_job(self, job):
        """ Stops a job by deleting it.
        """
        with self.lock:
            self._unschedule_stop(job, 'stopped')

# ################################################################################################################################

    def stop(self):
        """ Stops all jobs and the scheduler itself.
        """
        with self.lock:
            jobs = sorted(self.jobs)
            for job in jobs:
                self._unschedule_stop(job.clone(), 'stopped')

# ################################################################################################################################

    def sleep(self, value):
        """ A method introduced so the class is easier to mock out in tests.
        """
        gevent.sleep(value)

# ################################################################################################################################

    def is_scheduler_active(self) -> 'bool':
        out = self.current_status == SCHEDULER.Status.Active
        return out

# ################################################################################################################################

    def execute(self, name):
        """ If the scheduler is active, executes a job no matter if it's active or not. One-time job are not unscheduled afterwards.
        """

        # Do not execute any jobs if we are not active
        if not self.is_scheduler_active():
            return

        with self.lock:
            for job in itervalues(self.jobs):
                if job.name == name:
                    self.on_job_executed(job.get_context(), False)
                    break
            else:
                logger.warning('No such job `%s` in `%s`', name, [elem.get_context() for elem in itervalues(self.jobs)])

# ################################################################################################################################

    def on_job_executed(self, ctx:'stranydict', unschedule_one_time:'bool'=True) -> 'None':

        # Do not execute any jobs if we are not active
        if not self.is_scheduler_active():
            return

        # If this is a specal, pub/sub cleanup job, run its underlying command in background ..
        if ctx['name'] == SCHEDULER.PubSubCleanupJob:
            start_cleanup(self.config.component_dir)

        # .. otherwise, this is a job that runs in a server.
        else:
            logger.debug('Executing `%s`, `%s`', ctx['name'], ctx)
            self.on_job_executed_cb(ctx)
            self.job_log('Job executed `%s`, `%s`', ctx['name'], ctx)

            if ctx['type'] == SCHEDULER.JOB_TYPE.ONE_TIME and unschedule_one_time:
                self.unschedule_by_name(ctx['name'])

# ################################################################################################################################

    def _spawn(self, *args, **kwargs):
        """ As in the Job class, this is a thin wrapper so that it is easier to mock this method out in unit-tests.
        """
        return spawn_greenlet(*args, **kwargs)

# ################################################################################################################################

    def spawn_job(self, job):
        """ Spawns a job's greenlet. Must be called with self.lock held.
        """
        job.callback = self.on_job_executed
        job.on_max_repeats_reached_cb = self.on_max_repeats_reached
        self.job_greenlets[job.name] = self._spawn(job.run)

# ################################################################################################################################

    def _init_jobs_by_odb(self):

        cluster_conf = self.config.main.cluster
        add_startup_jobs_to_odb_by_odb(cluster_conf.id, self.odb, self.startup_jobs, asbool(cluster_conf.stats_enabled))

        # Actually start jobs now, including any added above
        if self._add_scheduler_jobs:
            load_scheduler_jobs_by_odb(self.api, self.odb, self.config.main.cluster.id, spawn=False)

# ################################################################################################################################

    def _init_jobs_by_api(self):

        cluster_conf = self.config.main.cluster
        add_startup_jobs_to_odb_by_api(self.api, self.startup_jobs, asbool(cluster_conf.stats_enabled))

        # Actually start jobs now, including any added above
        if self._add_scheduler_jobs:
            load_scheduler_jobs_by_api(self.api, spawn=False)

# ################################################################################################################################

    def init_jobs(self):

        # Sleep to make sure that at least one server is running if the environment was started from quickstart scripts
        sleep(self.initial_sleep_time)

        # If we have ODB configuration, we will be initializing jobs in the ODB ..
        if self.prefer_odb_config:
            self._init_jobs_by_odb()

        # .. otherwise, we are initializing jobs via API calls to a remote server.
        else:
            spawn_greenlet(self._init_jobs_by_api)

# ################################################################################################################################

    def run(self):

        try:

            logger.info('Scheduler will start to execute jobs in %s seconds', self.initial_sleep_time)

            # Add default jobs to the ODB and start all of them, the default and user-defined ones
            self.init_jobs()

            _sleep = self.sleep
            _sleep_time = self.sleep_time

            with self.lock:
                for job in sorted(itervalues(self.jobs)):

                    # Ignore pre-3.2 Redis-based jobs
                    if job.name.startswith('zato.stats'):
                        continue

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

        except Exception:
            logger.warning(format_exc())

# ################################################################################################################################
# ################################################################################################################################
