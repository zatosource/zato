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
from time import strptime
from traceback import format_exc

# lxml
from lxml import etree
from lxml.objectify import Element

# validate
from validate import is_boolean

# Zato
from zato.common import path, scheduler_date_time_format_interval_based, \
     scheduler_date_time_format_one_time, ZatoException, ZATO_OK, zato_path
from zato.common.odb.model import Cluster, Job, CronStyleJob, IntervalBasedJob,\
     Service
from zato.common.util import pprint, TRACE1
from zato.server.service.internal import _get_params, AdminService

def _get_interval_based_start_date(payload):
    start_date = zato_path('data.job.start_date', True).get_from(payload)
    if start_date:
        # Were optional date & time provided in a correct format?
        strptime(str(start_date), scheduler_date_time_format_interval_based)

    return str(start_date)

def _create_edit(action, payload, logger, session):
    """ Creating and updating a job requires a series of very similar steps
    so they've been all put here and depending on the 'action' parameter 
    (be it 'create'/'edit') some additional operations are performed.
    """
    core_params = ['cluster_id', 'name', 'is_active', 'job_type', 'service',
                   'start_date', 'extra']
    params = _get_params(payload, core_params, 'data.', default_value='')
    
    job_type = params['job_type']
    cluster_id = params['cluster_id']
    name = params['name']
    service_name = params['service']
    
    if job_type not in ('one_time', 'interval_based', 'cron_style'):
        msg = 'Unrecognized job type [{0}]'.format(job_type)
        logger.error(msg)
        raise ZatoException(msg)
    
    # For finding out if we don't have a job of that name already defined.
    existing_one_base = session.query(Job).\
        filter(Cluster.id==cluster_id).\
        filter(Job.name==name)
    
    if action == 'create':
        existing_one = existing_one_base.first()
    else:
        edit_params = _get_params(payload, ['id'], 'data.')
        job_id = edit_params['id']
        existing_one = existing_one_base.filter(Job.id != job_id).first()
    
    if existing_one:
        raise Exception('Job [{0}] already exists on this cluster'.format(
            name))
    
    # Is the service's name correct?
    service = session.query(Service).\
        filter(Cluster.id==cluster_id).\
        filter(Service.name==service_name).first()
    
    if not service:
        msg = 'Service [{0}] does not exist on this cluster'.format(service_name)
        logger.error(msg)
        raise Exception(msg)
    
    # We can create/edit a base Job object now and - optionally - another one
    # if the job type's is either interval-based or Cron-style. The base
    # instance will be enough if it's a one-time job.
    
    extra = params['extra'].encode('utf-8')
    is_active = is_boolean(params['is_active'])
    start_date = params['start_date']
    
    
    if action == 'create':
        job = Job(None, name, is_active, job_type, 
                  start_date, extra, 
                  cluster_id=cluster_id, service=service)
    else:
        job = session.query(Job).filter_by(id=job_id).one()
        job.name = name
        job.is_active = is_active
        job.start_date = start_date
        job.service = service
        job.extra = extra
        
    try:
        # Add but don't commit yet.
        session.add(job)

        if job_type == 'one_time':
            session.commit()
            
        elif job_type == 'interval_based':
            request_params = ['weeks', 'days', 'hours', 'minutes', 'seconds', 'repeats']
            params = _get_params(payload, request_params, 'data.',
                default_value=0, force_type=int, force_type_params=request_params)

            if not any(params[key] for key in ('weeks', 'days', 'hours', 'minutes', 'seconds')):
                msg = "At least one of ['weeks', 'days', 'hours', 'minutes', 'seconds'] must be given."
                logger.error(msg)
                raise ZatoException(msg)

            ib_job = IntervalBasedJob(None, job, params.get('weeks'), 
                                      params.get('days'), 
                    params.get('hours'), params.get('minutes'), params.get('seconds'), 
                    params.get('repeats'))
            
            session.add(ib_job)
            session.commit()
            
        else:
            # ZZZ Handle other types.
            session.commit()
    except Exception, e:
        session.rollback()
        msg = 'Could not complete the request, e=[{e}]'.format(e=format_exc(e))
        logger.error(msg)
        
        raise 
    else:
        if action == 'create':
            job_elem = Element('job')
            job_elem.id = job.id
            out = etree.tostring(job_elem)
        else:
            out = ''
        
        return ZATO_OK, out

class GetList(AdminService):
    """ Returns a list of all jobs defined in the SingletonServer's scheduler.
    """
    def handle(self, *args, **kwargs):
        with closing(self.server.odb.session()) as session:
            
            params = _get_params(kwargs.get('payload'), ['cluster_id'], 'data.')
            definition_list = Element('definition_list')
            
            definitions = session.query(Job.id, Job.name, Job.is_active,
                Job.job_type, Job.start_date,  Job.extra,
                Service.name.label('service_name'), Service.id.label('service_id'),
                IntervalBasedJob.weeks, IntervalBasedJob.days,
                IntervalBasedJob.hours, IntervalBasedJob.minutes, 
                IntervalBasedJob.seconds, IntervalBasedJob.repeats,
                CronStyleJob.definition.label('cron_definition')).\
                    outerjoin(IntervalBasedJob, Job.id==IntervalBasedJob.job_id).\
                    outerjoin(CronStyleJob, Job.id==CronStyleJob.job_id).\
                    filter(Cluster.id==params['cluster_id']).\
                    filter(Job.service_id==Service.id).\
                    order_by('job.name').\
                    all()
    
            for definition in definitions:
    
                definition_elem = Element('definition')
                definition_elem.id = definition.id
                definition_elem.name = definition.name
                definition_elem.is_active = definition.is_active
                definition_elem.job_type = definition.job_type
                definition_elem.start_date = definition.start_date
                definition_elem.extra = definition.extra
                definition_elem.service_id = definition.service_id
                definition_elem.service_name = definition.service_name
                definition_elem.weeks = definition.weeks
                definition_elem.days = definition.days
                definition_elem.hours = definition.hours
                definition_elem.minutes = definition.minutes
                definition_elem.seconds = definition.seconds
                definition_elem.repeats = definition.repeats
                
                definition_list.append(definition_elem)
    
            return ZATO_OK, etree.tostring(definition_list)

class Create(AdminService):
    """ Creates a new scheduler's job.
    """
    def handle(self, *args, **kwargs):
        return _create_edit('create', kwargs.get('payload'), self.logger, 
                            self.server.odb.session())

        '''
        def _handle_interval_based(payload, name, service, extra):
            request_params = ['weeks', 'days', 'hours', 'minutes', 'seconds', 'repeat', 'start_date']
            params = _get_params(payload, request_params, 'data.job.',
                                     default_value=0, force_type=int,
                                     force_type_params=request_params[:-1])

            if not any(params[key] for key in ('weeks', 'days', 'hours', 'minutes', 'seconds')):
                msg = 'At least one of [\'weeks\', \'days\', \'hours\', \'minutes\', \'seconds\'] must be given.'
                self.logger.error(msg)
                raise ZatoException(msg)

            params['start_date'] = _get_interval_based_start_date(payload)
            
            params_pprinted = pprint((name, service, extra, params))
            self.logger.debug('About to create an interval-based job, params=[%s]'.format(
                params_pprinted))

            result, response = self.server.send_config_request('CREATE_JOB',
                            ['interval_based', name, service, extra, params],
                            timeout=6.0)
            self.logger.log(TRACE1, 'result=[%s], response1=[%s]' % (result, response))
            return result, response
            '''
        
        # Let the handler take care the rest.
        #return locals()['_handle_' + job_type](payload, core_params, extra)
        
class Edit(AdminService):
    """ Update a new scheduler's job.
    """
    def handle(self, *args, **kwargs):
        return _create_edit('edit', kwargs.get('payload'), self.logger, 
                            self.server.odb.session())

class Delete(AdminService):
    """ Deletes a scheduler's job.
    """
    def handle(self, *args, **kwargs):
        with closing(self.server.odb.session()) as session:
            try:
                payload = kwargs.get('payload')
                request_params = ['id']
                params = _get_params(payload, request_params, 'data.')
                
                id = params['id']
                
                job = session.query(Job).\
                    filter(Job.id==id).\
                    one()
                
                session.delete(job)
                session.commit()
            except Exception, e:
                session.rollback()
                msg = 'Could not delete the job, e=[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)
                
                raise
            
            return ZATO_OK, ''
'''

# stdlib
import json

# Spring Python
from springpython.util import synchronized

# Zato
from zato.common.util import pprint, TRACE1
from zato.common import(path, zato_path, ZatoException, scheduler_date_time_format_one_time,
                       scheduler_date_time_format_interval_based)
from zato.server.service.internal import _get_params, AdminService






class EditJob(AdminService):
    """ Changes the properties of a job.
    """
    @synchronized()
    def handle(self, *args, **kwargs):

        def _handle_one_time(payload, name, original_name, service, extra):
            request_params = ['date_time']
            params = _get_params(payload, request_params, 'data.job.')

            # Were date & time provided in a correct format?
            strptime(params['date_time'], scheduler_date_time_format_one_time)

            params_pprinted = pprint((name, service, extra, params))

            self.logger.debug('About to edit a one-time job, params=[%s]' % params_pprinted)
            result, response = self.server.send_config_request('EDIT_JOB',
                                ['one_time', name, original_name, service, extra, params],
                                timeout=5.0)
            self.logger.log(TRACE1, 'result=[%s], response1=[%s]' % (result, response))
            if response:
                response = json.loads(response)
            self.logger.log(TRACE1, 'response2=[%s]' % response)

            return result, response

        def _handle_interval_based(payload, name, original_name, service, extra):
            request_params = ['weeks', 'days', 'hours', 'minutes', 'seconds', 'repeat']
            params = _get_params(payload, request_params, 'data.job.',
                                     default_value=0, force_type=int,
                                     force_type_params=request_params[:-1])

            if not any(params[key] for key in ('weeks', 'days', 'hours', 'minutes', 'seconds')):
                msg = 'At least one of ['weeks', 'days', 'hours', 'minutes', 'seconds'] must be given.'
                self.logger.error(msg)
                raise ZatoException(msg)

            # Were optional date & time provided in a correct format?
            start_date = zato_path('job.start_date').get_from(payload)
            if start_date:
                strptime(str(start_date), scheduler_date_time_format_interval_based)
            else:
                start_date = ''
            params['start_date'] = str(start_date)

            params_pprinted = pprint((name, service, extra, start_date, params))

            self.logger.debug('About to edit an interval-based job, params=[%s]' % params_pprinted)
            result, response = self.server.send_config_request('EDIT_JOB',
                                ['interval_based', name, original_name, service, extra, params],
                                timeout=5.0)
            self.logger.log(TRACE1, 'result=[%s], response1=[%s]' % (result, response))
            return result, response

        payload = kwargs.get('payload')
        job_type = zato_path('data.job.job_type', True).get_from(payload)

        # Make sure we know what kind of job it is.
        if job_type not in ('one_time', 'interval_based', 'cron_style'):
            msg = 'Unrecognized job type [%s]' % job_type
            self.logger.error(msg)
            raise ZatoException(msg)

        name = unicode(zato_path('data.job.name', True).get_from(payload))
        original_name = unicode(zato_path('data.job.original_name', True).get_from(payload))
        service = unicode(zato_path('data.job.service', True).get_from(payload))

        # Extra parameters are not mandatory.
        extra = path('zato_message.data.job.extra').get_from(payload)
        extra = unicode(extra) if extra else ''

        # Let the handler take care of it.
        return locals()['_handle_' + job_type](payload, name, original_name, service, extra)

class ExecuteJob(AdminService):
    """ Executes a scheduler's job.
    """
    def handle(self, *args, **kwargs):
        payload = kwargs.get('payload')
        name = unicode(zato_path('job.name', True).get_from(payload))

        result, response = self.server.send_config_request('EXECUTE_JOB', name,
                            timeout=3.0)
        self.logger.log(TRACE1, 'result=[%s], response1=[%s]' % (result, response))
        return result, response

class DeleteJob(AdminService):
    """ Deletes a scheduler's job.
    """
    @synchronized()
    def handle(self, *args, **kwargs):
        payload = kwargs.get('payload')
        name = unicode(zato_path('job.name', True).get_from(payload))

        result, response = self.server.send_config_request('DELETE_JOB', name,
                            timeout=3.0)
        self.logger.log(TRACE1, 'result=[%s], response1=[%s]' % (result, response))
        return result, response
        
'''