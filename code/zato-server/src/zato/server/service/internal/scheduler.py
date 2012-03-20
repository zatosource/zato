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
from zato.common import scheduler_date_time_format, \
     scheduler_date_time_format, ZatoException, ZATO_OK, zato_path
from zato.common.broker_message import MESSAGE_TYPE, SCHEDULER
from zato.common.odb.model import Cluster, Job, CronStyleJob, IntervalBasedJob,\
     Service
from zato.common.odb.query import job_list
from zato.server.service import _get_params
from zato.server.service.internal import AdminService

PREDEFINED_CRON_DEFINITIONS = {
    '@yearly': '0 0 1 1 *',
    '@annually': '0 0 1 1 *', # Same as 'yearly'.
    '@monthly': '0 0 1 * *',
    '@weekly': '0 0 * * 0',
    '@daily': '0 0 * * *',
    '@hourly': '0 * * * *',
    }

CRON_EXPRESSION_LEN = 5

def _get_interval_based_start_date(payload):
    start_date = zato_path('data.job.start_date', True).get_from(payload)
    if start_date:
        # Were optional date & time provided in a correct format?
        strptime(str(start_date), scheduler_date_time_format)

    return str(start_date)

def _create_edit(action, payload, logger, session, broker_client, response):
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
            request_params = ['weeks', 'days', 'hours', 'minutes', 'seconds', 'repeats']
            ib_params = _get_params(payload, request_params, 'data.', default_value='')

            if not any(ib_params[key] for key in ('weeks', 'days', 'hours', 'minutes', 'seconds')):
                msg = "At least one of ['weeks', 'days', 'hours', 'minutes', 'seconds'] must be given."
                logger.error(msg)
                raise ZatoException(msg)
            
            if action == 'create':
                ib_job = IntervalBasedJob(None, job)
            else:
                ib_job = session.query(IntervalBasedJob).filter_by(
                    id=job.interval_based.id).one()

            for param, value in ib_params.items():
                if value:
                    setattr(ib_job, param, value)
            
            session.add(ib_job)
            
        elif job_type == 'cron_style':
            cs_params = _get_params(payload, ['cron_definition'], 'data.')
            cron_definition = cs_params['cron_definition'].strip()
            
            if cron_definition.startswith('@'):
                if not cron_definition in PREDEFINED_CRON_DEFINITIONS:
                    msg = ('If using a predefined definition, it must be '
                             'one of {0} instead of [{1}]').format(
                                 sorted(PREDEFINED_CRON_DEFINITIONS), 
                                 cron_definition)
                    logger.error(msg)
                    raise Exception(msg)
                
                cron_definition = PREDEFINED_CRON_DEFINITIONS[cron_definition]
            else:
                splitted = cron_definition.strip().split()
                if not len(splitted) == CRON_EXPRESSION_LEN:
                    msg = ('Expression [{0}] in invalid, it needs to contain '
                           'exactly {1} whitespace-separated fields').format(
                               cron_definition, CRON_EXPRESSION_LEN)
                    logger.error(msg)
                    raise Exception(msg)
                cron_definition = ' '.join(splitted)
            
            if action == 'create':
                cs_job = CronStyleJob(None, job)
            else:
                cs_job = session.query(CronStyleJob).filter_by(
                    id=job.cron_style.id).one()
                
            cs_job.cron_definition = cron_definition
            session.add(cs_job)

        # We can commit it all now.
        session.commit()
        
        # Now send it to the broker, but only if the job is active.
        if is_active:
            msg_action = SCHEDULER.CREATE if action == 'create' else SCHEDULER.EDIT
            msg = {'action': msg_action, 'job_type': job_type,
                   'is_active':is_active, 'start_date':start_date,
                   'extra':extra, 'service': service_name, 'name': name
                   }
            if action == 'edit':
                msg['old_name'] = old_name

            if job_type == 'interval_based':
                for param, value in ib_params.items():
                    msg[param] = int(value) if value else 0
            elif job_type == 'cron_style':
                msg['cron_definition'] = cron_definition
        else:
            msg = {'action': SCHEDULER.DELETE, 'name': name}
            
        broker_client.send_json(msg, MESSAGE_TYPE.TO_SINGLETON)
        
            
    except Exception, e:
        session.rollback()
        msg = 'Could not complete the request, e=[{e}]'.format(e=format_exc(e))
        logger.error(msg)
        
        raise 
    else:
        job_elem = Element('job')
        
        if action == 'create':
            job_elem.id = job.id
            
        if job_type == 'cron_style':
            # Needs to be returned because we might've been performing
            # a substitution like changing '@hourly' into '0 * * * *'.
            job_elem.cron_definition = cs_job.cron_definition

        response.payload = etree.tostring(job_elem)

class GetList(AdminService):
    """ Returns a list of all jobs defined in the SingletonServer's scheduler.
    """
    class SimpleIO:
        required = ('cluster_id',)

    def handle(self):
        
        with closing(self.odb.session()) as session:
            
            definition_list = Element('definition_list')
            definitions = job_list(session, self.request.input.cluster_id, False)
            
            for definition in definitions:
    
                definition_elem = Element('definition')
                definition_elem.id = definition.id
                definition_elem.name = definition.name
                definition_elem.is_active = definition.is_active
                definition_elem.job_type = definition.job_type
                definition_elem.start_date = definition.start_date
                definition_elem.extra = definition.extra.decode('utf-8')
                definition_elem.service_id = definition.service_id
                definition_elem.service_name = definition.service_name.decode('utf-8')
                definition_elem.weeks = definition.weeks if definition.weeks else ''
                definition_elem.days = definition.days if definition.days else ''
                definition_elem.hours = definition.hours if definition.hours else ''
                definition_elem.minutes = definition.minutes if definition.minutes else ''
                definition_elem.seconds = definition.seconds if definition.seconds else ''
                definition_elem.repeats = definition.repeats if definition.repeats else ''
                definition_elem.cron_definition = (definition.cron_definition.decode('utf-8') if 
                    definition.cron_definition else '')
                
                definition_list.append(definition_elem)
    
            self.response.payload = etree.tostring(definition_list)

class Create(AdminService):
    """ Creates a new scheduler's job.
    """
    def handle(self):
        with closing(self.odb.session()) as session:
            return _create_edit('create', self.request.payload, self.logger, 
                session, self.broker_client, self.response)
        
class Edit(AdminService):
    """ Update a new scheduler's job.
    """
    def handle(self):
        with closing(self.odb.session()) as session:
            return _create_edit('edit', self.request.payload, self.logger, 
                session, self.broker_client, self.response)

class Delete(AdminService):
    """ Deletes a scheduler's job.
    """
    class SimpleIO:
        required = ('id',)

    def handle(self):
        with closing(self.odb.session()) as session:
            try:
                job = session.query(Job).\
                    filter(Job.id==self.request.input.id).\
                    one()
                
                session.delete(job)
                session.commit()

                msg = {'action': SCHEDULER.DELETE, 'name': job.name}
                self.broker_client.send_json(msg, MESSAGE_TYPE.TO_SINGLETON)
                
            except Exception, e:
                session.rollback()
                msg = 'Could not delete the job, e=[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)
                
                raise
            
class Execute(AdminService):
    """ Executes a scheduler's job.
    """
    class SimpleIO:
        required = ('id',)

    def handle(self):
        with closing(self.odb.session()) as session:
            try:
                job = session.query(Job).\
                    filter(Job.id==self.request.input.id).\
                    one()
                
                msg = {'action': SCHEDULER.EXECUTE, 'name': job.name}
                self.broker_client.send_json(msg, MESSAGE_TYPE.TO_SINGLETON)
                
            except Exception, e:
                session.rollback()
                msg = 'Could not execute the job, e=[{e}]'.format(e=format_exc(e))
                self.logger.error(msg)
                
                raise
