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
# stdlib
import copy, logging
from time import strptime
from threading import Event
from traceback import format_exc
from datetime import datetime, timedelta

# PyYAML
from yaml import load, Loader

'''
# stdlib
import copy, logging
from time import strptime
from threading import Event
from traceback import format_exc
from datetime import datetime, timedelta

# PyYAML
from yaml import load, Loader

# lxml
from lxml import objectify

# APScheduler
from apscheduler.scheduler import Job, Scheduler as APScheduler
from apscheduler.triggers import SimpleTrigger, IntervalTrigger

# Spring Python
from springpython.context import InitializingObject, DisposableObject
from springpython.util import synchronized

# Zato
from zato.common import ZatoException, soap_body_xpath, scheduler_date_time_format_one_time
from zato.server.channel.soap import get_body_payload
from zato.server.service.internal import AdminService

logger = logging.getLogger(__name__)

def _parse_date_time(date_time):
    strp = strptime(date_time, scheduler_date_time_format_one_time)
    return datetime(year=strp.tm_year, month=strp.tm_mon, day=strp.tm_mday,
                       hour=strp.tm_hour, minute=strp.tm_min, second=strp.tm_sec)

class JobWrapper(object):
    """ A base class for wrappers invoked by APScheduler,
    """
    def __init__(self, job_name=None, service=None, extra=None, _app_context=None):
        self.__name__ = self.job_name = job_name # APScheduler's needs __name__
        self.service = service
        self.extra = extra
        self._app_context = _app_context

    def __getitem__(self, key):
        # Let it quack like a dict. Comes handy in private scheduler's functions
        # which may treat all parameters as if they were always dicts.
        return object.__getattribute__(self, key)

    def __call__(self):
        logger.debug("About to execute a job [%s]" % self)

        service_class = self._app_context.get_object("service_store").services.get(self.service)
        if not service_class:
            msg = "Could not execute job [%s], service [%s] doesn't exist." % (self.job_name, self.service)
            logger.error(msg)
            raise ZatoException(msg)

        extra = self.extra

        # Let's see if extra is an XML document.
        try:
            extra = objectify.fromstring(extra)
        except Exception, e:
            # Well, it wasn't.
            logger.debug("Job's extra data is not an XML [%s], e=[%s]" % (
                self.extra, format_exc()))
        else:
            try:
                # Could it be a SOAP message?
                extra = get_body_extra(soap_body_xpath(extra))
            except Exception, e:
                # Nope, some other XML.
                logger.debug("Job's extra data is not a SOAP message [%s], e=[%s]" % (
                    self.extra, format_exc()))

        service_instance = service_class()

        # Admin services are given direct access to the server's internals.
        if isinstance(service_instance, AdminService):
            service_instance.server = self._app_context.get_object("server")

        response = service_instance.handle(extra=extra, raw_request=self.extra)
        logger.debug("Successfully executed a job [%s], service response [%s]" % (self, response))

class OneTimeJobWrapper(JobWrapper):
    """ Encapsulates all the data needed to execute a one-time job.
    """
    def __init__(self, job_name, service, extra, _app_context, params):
        super(OneTimeJobWrapper, self).__init__(job_name, service, extra,
                                                _app_context)
        self.date_time = params["date_time"]

    def __str__(self):
        return "<%s at %s job_name=[%s] service=[%s] extra=[%s] date_time=[%s]>" % (
            self.__class__.__name__, hex(id(self)), self.job_name, self.service,
            self.extra, self.date_time)

class IntervalBasedJobWrapper(JobWrapper):
    """ Encapsulates all the data needed to execute an interval-based job.
    """
    def __init__(self, job_name, service, extra, _app_context, params):
        super(IntervalBasedJobWrapper, self).__init__(job_name, service, extra,
                                                _app_context)
        self.start_date = params["start_date"]
        self.weeks = params["weeks"]
        self.days = params["days"]
        self.hours = params["hours"]
        self.minutes = params["minutes"]
        self.seconds = params["seconds"]
        self.repeat = params["repeat"]

    def __str__(self):
        return "<%s at %s job_name=[%s] service=[%s] extra=[%s] start_date=[%s]" \
            " weeks=[%s] days=[%s] hours=[%s] minutes=[%s] seconds=[%s]" \
            " repeat=[%s]>" % (
                self.__class__.__name__, hex(id(self)), self.job_name, self.service,
                self.extra, self.start_date, self.weeks, self.days, self.hours,
                self.minutes, self.seconds, self.repeat)

class Scheduler(APScheduler, DisposableObject):
    """ A container for APScheduler's instances. Tasks may be either single
    fire jobs or complex interval-based jobs. Interval-based ones support
    cron syntax as well as Zato's own configuration format. No other updates to
    the scheduler are allowed while the job's being updated, which could mean
    adding a new job, editing an existing one or deleting one.
    """
    def __init__(self, destroy_wait_time=10, job_list={},
                 config_repo_manager=None):
        super(Scheduler, self).__init__()

        self.server = None # SingletonServer will be assigned in self.init
        self.destroy_wait_time = destroy_wait_time

        # A list of all configured jobs, including those which are not active
        # anymore.
        self.job_list = job_list

        # Indicates whether it's safe to update the scheduler. The flag is set
        # when there are any modifications to the scheduler being performed,
        # in that case the calling thread will wait until the scheduler may be
        # updated again. Note that reads are always allowed.
        self.is_update_allowed = Event()

        # By default it's okay to update the scheduler.
        self.is_update_allowed.set()

        self.config_repo_manager = config_repo_manager
        self.logger = logging.getLogger("%s.%s" % (__name__, self.__class__.__name__))

    def read_job_list(self, location):
        data = load(open(location), Loader=Loader)
        self.job_list = data["job_list"]

    @synchronized()
    def init(self, server=None):

        # Assign a SingletonServer to scheduler.
        self.server = server

        # Wait until other updates will have been finished (although, in this
        # particular case of 'init', there shouldn't be any concurrent updates).
        self.is_update_allowed.wait()

        # Do not allow for any updates while the configuration is being updated.
        self.is_update_allowed.clear()

        try:
            self.logger.debug("Starting the scheduler")
            self.start()

            for job_name in self.job_list:
                params = self.job_list[job_name]

                self.logger.debug("Configuring job_name=[%s], params=[%s]." % (job_name, params))

                trigger = self._create_job_trigger(params["type"], params)
                job_wrapper = self._create_job_wrapper(params["type"], job_name,
                                            params["service"], params["extra"], params)

                aps_job = Job(trigger, job_wrapper, [], {})
                self.jobs.append(aps_job)

                self.logger.debug("Job configured [%s], params=[%s]." % (job_name, params))

            self.logger.debug("Scheduler started successfully")
        except Exception, e:
            self.logger.error(format_exc())
        else:
            # Tell APScheduler to schedule new jobs.
            self.wakeup.set()
        finally:
            self.is_update_allowed.set()

################################################################################

    def _update_job_params(self, job_type, source_params, target_params):
        """ Updates target params dictionary with appropriate parameters from
        the source dictionary which depend on the job's type.
        """
        _job_attrs = {
            "one_time": ["date_time"],
            "interval_based": ["start_date", "weeks", "days", "hours",
                               "minutes", "seconds", "repeat"]
            }

        for attr in _job_attrs[job_type]:
            target_params[attr] = source_params[attr]

        return target_params

    def _create_job_trigger(self, job_type, source_params):
        """ Creates a job trigger for a given job type.
        """
        if job_type == "one_time":
            return SimpleTrigger(_parse_date_time(str(source_params["date_time"])))
        elif job_type == "interval_based":
            interval = timedelta(weeks=source_params["weeks"],
                days=source_params["days"], hours=source_params["hours"],
                minutes=source_params["minutes"], seconds=source_params["seconds"])

            if source_params["start_date"]:
                date_time = _parse_date_time(source_params["start_date"])
            else:
                date_time = None

            return IntervalTrigger(interval, int(source_params["repeat"]), date_time)
        else:
            msg = "Unrecognized job type [%s]" % job_type
            self.logger.error(msg)
            raise ZatoException(msg)

    def _create_job_wrapper(self, job_type, job_name, service, extra, source_params):
        """ Creates a job wrapper for a given job type.
        """
        if job_type == "one_time":
            return OneTimeJobWrapper(job_name, service, extra, self.app_context,
                            self._update_job_params(job_type, source_params, {}))
        elif job_type == "interval_based":
            return IntervalBasedJobWrapper(job_name, service, extra,
                                self.app_context,
                                self._update_job_params(job_type, source_params, {}))
        else:
            msg = "Unrecognized job type [%s]" % job_type
            self.logger.error(msg)
            raise ZatoException(msg)

    def _create_job(self, job_type, job_name, service, extra, params):
        """ A utility method for creating new jobs. Private API,
        not to be called directly from outside of other scheduler's methods.
        """
        # Do not allow for any updates while the configuration is being updated.
        self.is_update_allowed.clear()
        self.jobs_lock.acquire()
        try:
            if job_name in self.job_list:
                msg = "Could not create a new job, name is not unique [%s]." % job_name
                self.logger.error(msg)
                raise ZatoException(msg)

            new_job = {}
            new_job["type"] = job_type
            new_job["extra"] = extra
            new_job["service"] = service

            # Update job's parameters.
            self._update_job_params(job_type, params, new_job)

            new_job_list = copy.deepcopy(self.job_list)
            new_job_list[job_name] = new_job

            # First save the changes.
            self.config_repo_manager.update_job_list(new_job_list)

            # APScheduler's trigger and a job's wrapper.
            trigger = self._create_job_trigger(job_type, params)
            job_wrapper = self._create_job_wrapper(job_type, job_name, service, extra, params)

            # APScheduler's job.
            aps_job = Job(trigger, job_wrapper, [], {})

            # Update our list of all jobs defined.
            self.job_list = new_job_list

            # Tell APScheduler to schedule the new job.
            self.jobs.append(aps_job)
            self.wakeup.set()

            self.logger.info("Job [%s] created." % job_name)

        except Exception, e:
            self.logger.error(format_exc())
            raise
        finally:
            self.is_update_allowed.set()
            self.jobs_lock.release()

    @synchronized()
    def create_one_time(self, job_name, service, extra, params):
        """ Creates a one-time job.
        """
        self._create_job("one_time", job_name, service, extra, params)

    @synchronized()
    def create_interval_based(self, job_name, service, extra, params):
        """ Creates an interval-based job.
        """
        self._create_job("interval_based", job_name, service, extra, params)

################################################################################

    def _edit_aps_job(self, rename_only, job_wrapper, job_type, original_job_name, success_msg):
        """ A utility method for updating APScheduler's jobs. Private API,
        not to be called directly from outside of other scheduler's methods.
        """
        try:
            self.jobs_lock.acquire()

            if not rename_only:
                trigger = self._create_job_trigger(job_type, job_wrapper)

                # APScheduler's job.
                aps_job = Job(trigger, job_wrapper, [], {})

            for active_job in self.jobs:
                if active_job.name == original_job_name:
                    self.logger.debug("Found an active job=[%s]." % active_job.name)
                    if rename_only:
                        active_job.name = job_wrapper.job_name
                    else:
                        # Remove the old one ..
                        self.jobs.remove(active_job)
                        self.logger.debug("Unscheduled an active_job=[%s]" % active_job)

                        # .. and append the new one to the list of APScheduler's jobs.
                        self.jobs.append(aps_job)
                        self.logger.debug("Scheduled a new version of a job=[%s]" % aps_job)
                    break
            else:
                self.logger.debug("Did not find an active job=[%s]" % original_job_name)

                if not rename_only:
                    # Nothing to remove, simply append a new job.
                    self.jobs.append(aps_job)
                    self.logger.debug("Scheduled a new job=[%s]" % aps_job)

        except Exception, e:
            msg = "Could not update an active job [%s], e=[%s]." % (
                original_job_name, format_exc())
            self.logger.error(msg)
            raise ZatoException(msg)
        else:
            self.logger.debug(success_msg)
        finally:
            self.jobs_lock.release()

    def _edit_job(self, job_type, job_name, original_job_name, service, extra, params):
        """ Changes the properties of a job. Private API, not to be called
        directly from outside of other scheduler's methods.
        """
        def _is_rename_only(job_type, old_job, job_renamed, service, extra, params):
            """ Returns True if the sole modification to a job is a name change.
            """
            if job_type == "one_time":
                return job_renamed and service == old_job["service"] and \
                        extra == old_job["extra"] and \
                        params["date_time"] == old_job["date_time"]
            elif job_type == "interval_based":
                pass
            elif job_type == "cron_style":
                pass
            else:
                msg = "Unrecognized job type [%s], original_job_name=[%s]" % (
                    job_type, original_job_name)
                self.logger.error(msg)
                raise ZatoException(msg)

        # Do not allow for any updates while the configuration is being updated.
        self.is_update_allowed.clear()

        job_renamed = original_job_name != job_name

        if job_renamed and job_name in self.job_list:
            msg = "Could not update a job, new name is not unique [%s]." % job_name
            self.logger.error(msg)
            raise ZatoException(msg)

        try:
            old_job = self.job_list.get(original_job_name)
            if not old_job:
                msg = "Job [%s] does not exist" % original_job_name
                self.logger.error(msg)
                raise ZatoException(msg)

            # New parameters to use if update goes well.
            new_job_list = copy.deepcopy(self.job_list)

            # Are we changing the name of a job only?
            rename_only = _is_rename_only(job_type, old_job, job_renamed, service,
                                          extra, params)
            if job_renamed and rename_only:
                self.logger.debug("About to rename a job from [%s] to [%s]." % (
                    original_job_name, job_name))

                # Just save the same object under a new key.
                new_job_list[job_name] = new_job_list.pop(original_job_name)

                # Whatever happens next, save the changes on-disk first.
                self.config_repo_manager.update_job_list(new_job_list)

                self.logger.debug("job_renamed=[%s], old_job=[%s], params=[%s]." % (
                    job_renamed, old_job, params))

                aps_success_msg = "List of active jobs updated, [%s] renamed to [%s]" % (original_job_name, job_name)

            # .. nope, we need to create a new one with updated parameters.
            else:
                self.logger.debug("About to fully update a job [%s]." % original_job_name)

                new_job_name = job_name if job_renamed else original_job_name
                new_job = new_job_list.pop(original_job_name)
                new_job["extra"] = extra
                new_job["service"] = service

                # Assign new parameters.
                self._update_job_params(job_type, params, new_job)

                # Save the changes on-disk first.
                new_job_list[new_job_name] = new_job
                self.config_repo_manager.update_job_list(new_job_list)

                aps_success_msg = "List of active jobs updated, original_job_name=[%s]" % (original_job_name)

            # Update APScheduler
            job_wrapper = self._create_job_wrapper(job_type, job_name, service, extra, params)
            self._edit_aps_job(rename_only, job_wrapper, job_type, original_job_name, aps_success_msg)

            # Update our list of all jobs defined.
            self.job_list = new_job_list

            # Reschedule APScheduler's machinery
            self.wakeup.set()

        except Exception, e:
            self.logger.error(format_exc())
            raise
        finally:
            self.is_update_allowed.set()

    @synchronized()
    def edit_one_time(self, job_name, original_job_name, service, extra, params):
        """ Changes the properties of a one-time job.
        """
        self._edit_job("one_time", job_name, original_job_name, service, extra, params)

    @synchronized()
    def edit_interval_based(self, job_name, original_job_name, service, extra, params):
        """ Changes the properties of an interval-based job.
        """
        self._edit_job("interval_based", job_name, original_job_name, service, extra, params)


################################################################################

    @synchronized()
    def execute(self, job_name):
        """ Tells APScheduler to run a given job.
        """
        for active_job in self.jobs:
            if active_job.name == job_name:
                active_job.run()
                break
        else:
            self.logger.warning("Job [%s] is not active, could not execute it." % job_name)

    @synchronized()
    def delete(self, job_name):
        """ Deletes a job definition and unshedules it if it's active.
        """
        # Do not allow for any updates while the configuration is being updated.
        self.is_update_allowed.clear()
        self.jobs_lock.acquire()
        try:
            if job_name not in self.job_list:
                # Job's not configured so it can't be an active one, no need
                # for asking APScheduler.
                msg = "Job [%s] does not exist." % job_name
                self.logger.error(msg)
                raise ZatoException(msg)

            # New parameters to use if delete goes well.
            new_job_list = copy.deepcopy(self.job_list)
            new_job_list.pop(job_name)

            # First commit the changes.
            self.config_repo_manager.update_job_list(new_job_list)

            for active_job in self.jobs:
                if active_job.name == job_name:
                    self.jobs.remove(active_job)
                    break
            else:
                self.logger.info("Job [%s] is not active, did not unschedule it." % job_name)

            # Update our list of all jobs defined.
            self.job_list = new_job_list

            self.logger.info("Job [%s] removed." % job_name)

        except Exception, e:
            self.logger.error(format_exc())
            raise
        finally:
            self.is_update_allowed.set()
            self.jobs_lock.release()

################################################################################

    def destroy(self):
        self.logger.debug("Shutting down the scheduler, destroy_wait_time=[%s]s." % self.destroy_wait_time)
        self.shutdown(int(self.destroy_wait_time))
        self.logger.info("Scheduler shut down successfully.")
'''