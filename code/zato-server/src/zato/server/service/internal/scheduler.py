# -*- coding: utf-8 -*-

"""
Copyright (C) Zato Source s.r.o. https://zato.io

Licensed under LGPLv3, see LICENSE.txt for terms and conditions.
"""

from __future__ import absolute_import, division, print_function, unicode_literals

# stdlib
from contextlib import closing
from traceback import format_exc

# crontab
from crontab import CronTab

# dateutil
from dateutil.parser import parse

# Zato
from zato.common.api import scheduler_date_time_format, SCHEDULER, ZATO_NONE
from zato.common.broker_message import MESSAGE_TYPE, SCHEDULER as SCHEDULER_MSG
from zato.common.exception import ZatoException
from zato.common.odb.model import Cluster, Job, CronStyleJob, IntervalBasedJob,\
     Service
from zato.common.odb.query import job_by_id, job_by_name, job_list
from zato.server.service.internal import AdminService, AdminSIO, GetListAdminSIO

# ################################################################################################################################

_service_name_prefix = 'zato.scheduler.job.'

# ################################################################################################################################

def _create_edit(action, cid, input, payload, logger, session, broker_client, response):
    """ Creating and updating a job requires a series of very similar steps
    so they've been all put here and depending on the 'action' parameter
    (be it 'create'/'edit') some additional operations are performed.
    """
    job_type = input.job_type
    cluster_id = input.cluster_id
    name = input.name
    service_name = input.service

    cluster = session.query(Cluster).\
        filter(Cluster.id==cluster_id).\
        one()

    if job_type not in(SCHEDULER.JOB_TYPE.ONE_TIME, SCHEDULER.JOB_TYPE.INTERVAL_BASED, SCHEDULER.JOB_TYPE.CRON_STYLE):
        msg = 'Unrecognized job type [{0}]'.format(job_type)
        logger.error(msg)
        raise ZatoException(cid, msg)

    # For finding out if we don't have a job of that name already defined.
    existing_one_base = session.query(Job).\
        filter(Cluster.id==cluster_id).\
        filter(Job.name==name)

    if action == 'create':
        existing_one = existing_one_base.\
            first()
    else:
        job_id = input.id
        existing_one = existing_one_base.\
            filter(Job.id != job_id).\
            first()

    if existing_one:
        raise ZatoException(cid, 'Job `{}` already exists on this cluster'.format(name))

    # Is the service's name correct?
    service = session.query(Service).\
        filter(Cluster.id==cluster_id).\
        filter(Service.cluster_id==Cluster.id).\
        filter(Service.name==service_name).\
        first()

    if not service:
        msg = 'Service `{}` does not exist on this cluster'.format(service_name)
        logger.error(msg)
        raise ZatoException(cid, msg)

    # We can create/edit a base Job object now and - optionally - another one
    # if the job type's is either interval-based or Cron-style. The base
    # instance will be enough if it's a one-time job.

    extra = (input.extra or u'').encode('utf-8')
    is_active = input.is_active
    start_date = parse(input.start_date)

    if action == 'create':
        job = Job(None, name, is_active, job_type, start_date, extra, cluster=cluster, service=service)
    else:
        job = session.query(Job).filter_by(id=job_id).one()
        old_name = job.name
        job.name = name
        job.is_active = is_active
        job.start_date = start_date
        job.service = service
        job.extra = extra

    try:
        # Add but don't commit yet.
        session.add(job)

        if job_type == SCHEDULER.JOB_TYPE.INTERVAL_BASED:
            ib_params = ('weeks', 'days', 'hours', 'minutes', 'seconds')
            if not any(input[key] for key in ib_params):
                msg = "At least one of ['weeks', 'days', 'hours', 'minutes', 'seconds'] must be given"
                logger.error(msg)
                raise ZatoException(cid, msg)

            if action == 'create':
                ib_job = IntervalBasedJob(None, job)
            else:
                ib_job = session.query(IntervalBasedJob).filter_by(id=job.interval_based.id).one()

            for param in ib_params + ('repeats',):
                value = input[param] or None
                if value != ZATO_NONE:
                    setattr(ib_job, param, value)

            value = input['repeats'] or None
            if value != ZATO_NONE:
                setattr(ib_job, 'repeats', value)

            session.add(ib_job)

        elif job_type == SCHEDULER.JOB_TYPE.CRON_STYLE:
            cron_definition = input.cron_definition.strip()

            # Just to make sure it's syntactically correct
            CronTab(cron_definition).next(default_utc=False)

            if action == 'create':
                cs_job = CronStyleJob(None, job)
            else:
                cs_job = session.query(CronStyleJob).filter_by(id=job.cron_style.id).one()

            cs_job.cron_definition = cron_definition
            session.add(cs_job)

        # We can commit it all now.
        session.commit()

        # Now send it to the broker, but only if the job is active.
        # if is_active:
        msg_action = SCHEDULER_MSG.CREATE.value if action == 'create' else SCHEDULER_MSG.EDIT.value
        msg = {'action': msg_action, 'job_type': job_type,
               'is_active':is_active, 'start_date':start_date.isoformat(),
               'extra':extra.decode('utf8'), 'service': service.name,
               'id':job.id, 'name': name
               }

        if action == 'edit':
            msg['old_name'] = old_name

        if job_type == SCHEDULER.JOB_TYPE.INTERVAL_BASED:
            for param in ib_params + ('repeats',):
                value = input[param]
                msg[param] = int(value) if value else 0

        elif job_type == SCHEDULER.JOB_TYPE.CRON_STYLE:
            msg['cron_definition'] = cron_definition

        broker_client.publish(msg, MESSAGE_TYPE.TO_SCHEDULER)

    except Exception:
        session.rollback()
        logger.error('Could not complete the request, e:`%s`', format_exc())
        raise
    else:
        response.payload.id = job.id
        response.payload.name = input.name

        if job_type == SCHEDULER.JOB_TYPE.CRON_STYLE:
            # Needs to be returned because we might've been performing
            # a substitution like changing '@hourly' into '0 * * * *'.
            response.payload.cron_definition = cs_job.cron_definition

# ################################################################################################################################
# ################################################################################################################################

class _CreateEdit(AdminService):
    """ A base class for both creating and editing scheduler jobs.
    """
    class SimpleIO(AdminSIO):
        input_required = ('cluster_id', 'name', 'is_active', 'job_type', 'service', 'start_date')
        input_optional = ('id', 'extra', 'weeks', 'days', 'hours', 'minutes', 'seconds', 'repeats', 'cron_definition')
        output_required = ('id', 'name')
        output_optional = ('cron_definition',)
        default_value = ''

    def handle(self):
        with closing(self.odb.session()) as session:
            _create_edit(self.__class__.__name__.lower(), self.cid, self.request.input, self.request.payload,
                    self.logger, session, self.broker_client, self.response)

# ################################################################################################################################
# ################################################################################################################################

class _Get(AdminService):
    class SimpleIO(AdminSIO):
        input_required = ('cluster_id',)
        output_required = 'id', 'name', 'is_active', 'job_type', 'start_date', 'service_id', 'service_name'
        output_optional = 'extra', 'weeks', 'days', 'hours', 'minutes', 'seconds', 'repeats', 'cron_definition'
        output_repeated = True
        default_value = ''
        date_time_format = scheduler_date_time_format

# ################################################################################################################################
# ################################################################################################################################

class GetList(_Get):
    """ Returns a list of all jobs defined in the scheduler.
    """
    _filter_by = Job.name,
    name = _service_name_prefix + 'get-list'

    class SimpleIO(_Get.SimpleIO):
        request_elem = 'zato_scheduler_job_get_list_request'
        response_elem = 'zato_scheduler_job_get_list_response'
        input_optional = GetListAdminSIO.input_optional + ('service_name',)

    def get_data(self, session):
        input = self.request.input
        return self._search(job_list, session, input.cluster_id, input.get('service_name'), False)

    def handle(self):
        with closing(self.odb.session()) as session:
            data = self.get_data(session)
            self.response.payload[:] = data

        for item in self.response.payload:
            item.start_date = item.start_date.isoformat()

# ################################################################################################################################
# ################################################################################################################################

class GetByID(_Get):
    """ Returns a job by its ID.
    """
    name = _service_name_prefix + 'get-by-id'

    class SimpleIO(_Get.SimpleIO):
        request_elem = 'zato_scheduler_job_get_by_id_request'
        response_elem = None
        input_required = _Get.SimpleIO.input_required + ('id',)
        output_repeated = False

    def get_data(self, session):
        return job_by_id(session, self.server.cluster_id, self.request.input.id)

    def handle(self):
        with closing(self.odb.session()) as session:
            self.response.payload = self.get_data(session)
            self.response.payload.start_date = self.response.payload.start_date.isoformat()

# ################################################################################################################################
# ################################################################################################################################

class GetByName(_Get):
    """ Returns a job by its name.
    """
    name = _service_name_prefix + 'get-by-name'

    class SimpleIO(_Get.SimpleIO):
        request_elem = 'zato_scheduler_job_get_by_name_request'
        response_elem = None
        input_required = _Get.SimpleIO.input_required + ('name',)
        output_repeated = False

    def get_data(self, session):
        return job_by_name(session, self.server.cluster_id, self.request.input.name)

    def handle(self):
        with closing(self.odb.session()) as session:
            self.response.payload = self.get_data(session)
            self.response.payload.start_date = self.response.payload.start_date.isoformat()

# ################################################################################################################################
# ################################################################################################################################

class Create(_CreateEdit):
    """ Creates a new scheduler's job.
    """
    name = _service_name_prefix + 'create'

    class SimpleIO(_CreateEdit.SimpleIO):
        request_elem = 'zato_scheduler_job_create_request'
        response_elem = 'zato_scheduler_job_create_response'

# ################################################################################################################################
# ################################################################################################################################

class Edit(_CreateEdit):
    """ Updates a scheduler's job.
    """
    name = _service_name_prefix + 'edit'

    class SimpleIO(_CreateEdit.SimpleIO):
        request_elem = 'zato_scheduler_job_edit_request'
        response_elem = 'zato_scheduler_job_edit_response'

# ################################################################################################################################
# ################################################################################################################################

class Delete(AdminService):
    """ Deletes a scheduler's job.
    """
    name = _service_name_prefix + 'delete'

    class SimpleIO(AdminSIO):
        request_elem = 'zato_scheduler_job_delete_request'
        response_elem = 'zato_scheduler_job_delete_response'
        input_required = ('id',)

    def handle(self):
        with closing(self.odb.session()) as session:
            try:
                job = session.query(Job).\
                    filter(Job.id==self.request.input.id).\
                    one()

                session.delete(job)
                session.commit()

                msg = {'action': SCHEDULER_MSG.DELETE.value, 'name': job.name}
                self.broker_client.publish(msg, MESSAGE_TYPE.TO_SCHEDULER)

            except Exception:
                session.rollback()
                self.logger.error('Could not delete the job, e:`%s`', format_exc())

                raise

# ################################################################################################################################
# ################################################################################################################################

class Execute(AdminService):
    """ Executes a scheduler's job.
    """
    name = _service_name_prefix + 'execute'

    class SimpleIO(AdminSIO):
        request_elem = 'zato_scheduler_job_execute_request'
        response_elem = 'zato_scheduler_job_execute_response'
        input_required = ('id',)

    def handle(self):
        with closing(self.odb.session()) as session:
            try:
                job = session.query(Job).\
                    filter(Job.id==self.request.input.id).\
                    one()

                msg = {'action': SCHEDULER_MSG.EXECUTE.value, 'name': job.name}
                self.broker_client.publish(msg, MESSAGE_TYPE.TO_SCHEDULER)

            except Exception:
                session.rollback()
                self.logger.error('Could not execute the job, e:`%s`', format_exc())

                raise

# ################################################################################################################################
# ################################################################################################################################

class SetActiveStatus(AdminService):
    """ Actives or deactivates a job.
    """
    name = _service_name_prefix + 'set-active-status'

    class SimpleIO(AdminSIO):
        request_elem = 'zato_scheduler_job_set_active_status_request'
        response_elem = 'zato_scheduler_job_set_active_status_response'
        input_required = ('id', 'is_active')

    def handle(self):
        with closing(self.odb.session()) as session:
            try:
                session.query(Job).\
                    filter(Job.id==self.request.input.id).\
                    one().is_active = self.request.input.is_active
                session.commit()

            except Exception:
                session.rollback()
                self.logger.error('Could not update is_active status, e:`%s`', format_exc())

                raise

# ################################################################################################################################
# ################################################################################################################################
