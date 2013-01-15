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
from contextlib import closing
from traceback import format_exc

# Zato
from zato.common import scheduler_date_time_format, ZatoException
from zato.common.broker_message import MESSAGE_TYPE, SCHEDULER
from zato.common.odb.model import Cluster, Job, CronStyleJob, IntervalBasedJob,\
     Service
from zato.common.odb.query import job_by_name, job_list
from zato.server.service.internal import AdminService, AdminSIO

PREDEFINED_CRON_DEFINITIONS = {
    '@yearly': '0 0 1 1 *',
    '@annually': '0 0 1 1 *', # Same as 'yearly'.
    '@monthly': '0 0 1 * *',
    '@weekly': '0 0 * * 0',
    '@daily': '0 0 * * *',
    '@hourly': '0 * * * *',
    }

CRON_EXPRESSION_LEN = 5

def _create_edit(action, cid, input, payload, logger, session, broker_client, response):
    """ Creating and updating a job requires a series of very similar steps
    so they've been all put here and depending on the 'action' parameter 
    (be it 'create'/'edit') some additional operations are performed.
    """
    job_type = input.job_type
    cluster_id = input.cluster_id
    name = input.name
    service_name = input.service
    
    if job_type not in ('one_time', 'interval_based', 'cron_style'):
        msg = 'Unrecognized job type [{0}]'.format(job_type)
        logger.error(msg)
        raise ZatoException(cid, msg)
    
    # For finding out if we don't have a job of that name already defined.
    existing_one_base = session.query(Job).\
        filter(Cluster.id==cluster_id).\
        filter(Job.name==name)
    
    if action == 'create':
        existing_one = existing_one_base.first()
    else:
        job_id = input.id
        existing_one = existing_one_base.filter(Job.id != job_id).first()
    
    if existing_one:
        raise ZatoException(cid, 'Job [{0}] already exists on this cluster'.format(name))
    
    # Is the service's name correct?
    service = session.query(Service).\
        filter(Cluster.id==cluster_id).\
        filter(Service.name==service_name).first()
    
    if not service:
        msg = 'Service [{0}] does not exist on this cluster'.format(service_name)
        logger.error(msg)
        raise ZatoException(cid, msg)
    
    # We can create/edit a base Job object now and - optionally - another one
    # if the job type's is either interval-based or Cron-style. The base
    # instance will be enough if it's a one-time job.
    
    extra = input.extra.encode('utf-8')
    is_active = input.is_active
    start_date = input.start_date
    
    if action == 'create':
        job = Job(None, name, is_active, job_type, start_date, extra, cluster_id=cluster_id, service=service)
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

        if job_type == 'interval_based':
            ib_params = ('weeks', 'days', 'hours', 'minutes', 'seconds')
            if not any(input[key] for key in ib_params):
                msg = "At least one of ['weeks', 'days', 'hours', 'minutes', 'seconds'] must be given"
                logger.error(msg)
                raise ZatoException(cid, msg)
            
            if action == 'create':
                ib_job = IntervalBasedJob(None, job)
            else:
                ib_job = session.query(IntervalBasedJob).filter_by(id=job.interval_based.id).one()

            for param in ib_params:
                value = input[param]
                if value:
                    setattr(ib_job, param, value)
            
            session.add(ib_job)
            
        elif job_type == 'cron_style':
            cron_definition = input.cron_definition.strip()
            
            if cron_definition.startswith('@'):
                if not cron_definition in PREDEFINED_CRON_DEFINITIONS:
                    msg = ('If using a predefined definition, it must be '
                             'one of {0} instead of [{1}]').format(
                                 sorted(PREDEFINED_CRON_DEFINITIONS), 
                                 cron_definition)
                    logger.error(msg)
                    raise ZatoException(cid, msg)
                
                cron_definition = PREDEFINED_CRON_DEFINITIONS[cron_definition]
            else:
                splitted = cron_definition.strip().split()
                if not len(splitted) == CRON_EXPRESSION_LEN:
                    msg = ('Expression [{0}] is invalid, it needs to contain '
                           'exactly {1} whitespace-separated fields').format(
                               cron_definition, CRON_EXPRESSION_LEN)
                    logger.error(msg)
                    raise ZatoException(cid, msg)
                cron_definition = ' '.join(splitted)
            
            if action == 'create':
                cs_job = CronStyleJob(None, job)
            else:
                cs_job = session.query(CronStyleJob).filter_by(id=job.cron_style.id).one()
                
            cs_job.cron_definition = cron_definition
            session.add(cs_job)

        # We can commit it all now.
        session.commit()
        
        # Now send it to the broker, but only if the job is active.
        if is_active:
            msg_action = SCHEDULER.CREATE if action == 'create' else SCHEDULER.EDIT
            msg = {'action': msg_action, 'job_type': job_type,
                   'is_active':is_active, 'start_date':start_date,
                   'extra':extra, 'service': service.impl_name,
                   'name': name
                   }
            if action == 'edit':
                msg['old_name'] = old_name

            if job_type == 'interval_based':
                for param in ib_params:
                    value = input[param]
                    msg[param] = int(value) if value else 0
            elif job_type == 'cron_style':
                msg['cron_definition'] = cron_definition
        else:
            msg = {'action': SCHEDULER.DELETE, 'name': name}
            
        broker_client.publish(msg, MESSAGE_TYPE.TO_SINGLETON)
        
            
    except Exception, e:
        session.rollback()
        msg = 'Could not complete the request, e:[{e}]'.format(e=format_exc(e))
        logger.error(msg)
        raise
    else:
        if action == 'create':
            response.payload.id = job.id
            
        if job_type == 'cron_style':
            # Needs to be returned because we might've been performing
            # a substitution like changing '@hourly' into '0 * * * *'.
            response.payload.cron_definition = cs_job.cron_definition

class _CreateEdit(AdminService):
    """ A base class for both creating and editing scheduler jobs.
    """
    class SimpleIO(AdminSIO):
        input_required = ('cluster_id', 'name', 'is_active', 'job_type', 'service', 'start_date', 'extra')
        input_optional = ('id', 'weeks', 'days', 'hours', 'minutes', 'seconds', 'repeats', 'cron_definition')
        output_optional = ('id', 'cron_definition')
        default_value = ''
        
    def handle(self):
        with closing(self.odb.session()) as session:
            _create_edit(self.__class__.__name__.lower(), self.cid, self.request.input, self.request.payload, 
                    self.logger, session, self.broker_client, self.response)

class _Get(AdminService):
    class SimpleIO(AdminSIO):
        input_required = ('cluster_id',)
        output_required = ('id', 'name', 'is_active', 'job_type', 'start_date', 'extra', 'service_id', 'service_name')
        output_optional = ('weeks', 'days', 'hours', 'minutes', 'seconds', 'repeats', 'cron_definition')
        output_repeated = True
        default_value = ''
        date_time_format = scheduler_date_time_format

class GetList(_Get):
    """ Returns a list of all jobs defined in the SingletonServer's scheduler.
    """
    class SimpleIO(_Get.SimpleIO):
        request_elem = 'zato_scheduler_job_get_list_request'
        response_elem = 'zato_scheduler_job_get_list_response'

    def get_data(self, session):
        return job_list(session, self.request.input.cluster_id, False)

    def handle(self):
        with closing(self.odb.session()) as session:
            self.response.payload[:] = self.get_data(session)
            
class GetByName(_Get):
    """ Returns a job by its name.
    """
    class SimpleIO(_Get.SimpleIO):
        request_elem = 'zato_scheduler_job_get_by_name_request'
        response_elem = 'zato_scheduler_job_get_by_name_response'
        input_required = ('name',)
        
    def get_data(self, session):
        return job_by_name(session, self.server.cluster_id, self.request.input.name)

    def handle(self):
        with closing(self.odb.session()) as session:
            self.response.payload = self.get_data(session)

class Create(_CreateEdit):
    """ Creates a new scheduler's job.
    """
    class SimpleIO(_CreateEdit.SimpleIO):
        request_elem = 'zato_scheduler_job_create_request'
        response_elem = 'zato_scheduler_job_create_response'
        
class Edit(_CreateEdit):
    """ Updates a scheduler's job.
    """
    class SimpleIO(_CreateEdit.SimpleIO):
        request_elem = 'zato_scheduler_job_edit_request'
        response_elem = 'zato_scheduler_job_edit_response'

class Delete(AdminService):
    """ Deletes a scheduler's job.
    """
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

                msg = {'action': SCHEDULER.DELETE, 'name': job.name}
                self.broker_client.publish(msg, MESSAGE_TYPE.TO_SINGLETON)
                
            except Exception, e:
                session.rollback()
                msg = 'Could not delete the job, e:[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)
                
                raise
            
class Execute(AdminService):
    """ Executes a scheduler's job.
    """
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
                
                msg = {'action': SCHEDULER.EXECUTE, 'name': job.name}
                self.broker_client.publish(msg, MESSAGE_TYPE.TO_SINGLETON)
                
            except Exception, e:
                session.rollback()
                msg = 'Could not execute the job, e:[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)
                
                raise
