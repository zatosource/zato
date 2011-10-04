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
from time import strptime
from traceback import format_exc

# lxml
from lxml import etree
from lxml.objectify import Element

# Zato
from zato.common import path, scheduler_date_time_format_interval_based, \
     scheduler_date_time_format_one_time, ZatoException, ZATO_OK, zato_path
from zato.common.odb.model import Cluster, Job, CronStyleJob, IntervalBasedJob
from zato.common.util import pprint, TRACE1
from zato.server.service.internal import _get_params, AdminService

def _get_interval_based_start_date(payload):
    start_date = zato_path('data.job.start_date', True).get_from(payload)
    if start_date:
        # Were optional date & time provided in a correct format?
        strptime(str(start_date), scheduler_date_time_format_interval_based)
    else:
        start_date
    return str(start_date)

class GetList(AdminService):
    """ Returns a list of all jobs defined in the SingletonServer's scheduler.
    """
    def handle(self, *args, **kwargs):
        definition_list = Element('definition_list')

        definitions = self.server.odb.query(Job).order_by('name').all()

        for definition in definitions:

            definition_elem = Element('definition')
            definition_elem.id = definition.id
            definition_elem.name = definition.name
            definition_elem.is_active = definition.is_active
            
            '''definition_elem.def_items = Element('def_items')
            
            for item in definition.items:
                item_elem = Element('item')
                item_elem.field = item.field
                item_elem.operator = item.operator
                item_elem.value = item.value
                
                definition_elem.def_items.append(item_elem)'''

            definition_list.append(definition_elem)

        return ZATO_OK, etree.tostring(definition_list)
    
class Create(AdminService):
    """ Creates a new scheduler's job.
    """
    def handle(self, *args, **kwargs):

        def _handle_one_time(payload, job_name, service, extra):
            request_params = ['date_time']
            params = _get_params(payload, request_params, 'data.job.')

            # Were date & time provided in a correct format?
            strptime(params['date_time'], scheduler_date_time_format_one_time)

            params_pprinted = pprint((job_name, service, extra, params))

            self.logger.debug('About to create a one-time job, params=[%s]'.format(
                params_pprinted))
            '''result, response = self.server.send_config_request('CREATE_JOB',
                                ['one_time', job_name, service, extra, params],
                                timeout=4.0)
            self.logger.log(TRACE1, 'result=[%s], response1=[%s]' % (result, response))
            '''
            return ZATO_OK, ''

        def _handle_interval_based(payload, job_name, service, extra):
            request_params = ['weeks', 'days', 'hours', 'minutes', 'seconds', 'repeat', 'start_date']
            params = _get_params(payload, request_params, 'data.job.',
                                     default_value=0, force_type=int,
                                     force_type_params=request_params[:-1])

            if not any(params[key] for key in ('weeks', 'days', 'hours', 'minutes', 'seconds')):
                msg = 'At least one of [\'weeks\', \'days\', \'hours\', \'minutes\', \'seconds\'] must be given.'
                self.logger.error(msg)
                raise ZatoException(msg)

            params['start_date'] = _get_interval_based_start_date(payload)
            
            params_pprinted = pprint((job_name, service, extra, params))
            self.logger.debug('About to create an interval-based job, params=[%s]'.format(
                params_pprinted))

            result, response = self.server.send_config_request('CREATE_JOB',
                            ['interval_based', job_name, service, extra, params],
                            timeout=6.0)
            self.logger.log(TRACE1, 'result=[%s], response1=[%s]' % (result, response))
            return result, response

        payload = kwargs.get('payload')
        self.logger.log(TRACE1, 'payload=[%r]' % payload)
        job_type = zato_path('data.job.job_type', True).get_from(payload)

        # Sanity check.
        if job_type not in ('one_time', 'interval_based', 'cron_style'):
            msg = 'Unrecognized job type [%s]' % job_type
            self.logger.error(msg)
            raise ZatoException(msg)

        job_name = unicode(zato_path('data.job.job_name', True).get_from(payload))
        service = unicode(zato_path('data.job.service', True).get_from(payload))

        # Extra parameters are not mandatory.
        extra = path('data.job.extra').get_from(payload)
        extra = unicode(extra) if extra else ''

        # Let the handler take care the rest.
        return locals()['_handle_' + job_type](payload, job_name, service, extra)


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

        def _handle_one_time(payload, job_name, original_job_name, service, extra):
            request_params = ['date_time']
            params = _get_params(payload, request_params, 'data.job.')

            # Were date & time provided in a correct format?
            strptime(params['date_time'], scheduler_date_time_format_one_time)

            params_pprinted = pprint((job_name, service, extra, params))

            self.logger.debug('About to edit a one-time job, params=[%s]' % params_pprinted)
            result, response = self.server.send_config_request('EDIT_JOB',
                                ['one_time', job_name, original_job_name, service, extra, params],
                                timeout=5.0)
            self.logger.log(TRACE1, 'result=[%s], response1=[%s]' % (result, response))
            if response:
                response = json.loads(response)
            self.logger.log(TRACE1, 'response2=[%s]' % response)

            return result, response

        def _handle_interval_based(payload, job_name, original_job_name, service, extra):
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

            params_pprinted = pprint((job_name, service, extra, start_date, params))

            self.logger.debug('About to edit an interval-based job, params=[%s]' % params_pprinted)
            result, response = self.server.send_config_request('EDIT_JOB',
                                ['interval_based', job_name, original_job_name, service, extra, params],
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

        job_name = unicode(zato_path('data.job.job_name', True).get_from(payload))
        original_job_name = unicode(zato_path('data.job.original_job_name', True).get_from(payload))
        service = unicode(zato_path('data.job.service', True).get_from(payload))

        # Extra parameters are not mandatory.
        extra = path('zato_message.data.job.extra').get_from(payload)
        extra = unicode(extra) if extra else ''

        # Let the handler take care of it.
        return locals()['_handle_' + job_type](payload, job_name, original_job_name, service, extra)

class ExecuteJob(AdminService):
    """ Executes a scheduler's job.
    """
    def handle(self, *args, **kwargs):
        payload = kwargs.get('payload')
        job_name = unicode(zato_path('job.job_name', True).get_from(payload))

        result, response = self.server.send_config_request('EXECUTE_JOB', job_name,
                            timeout=3.0)
        self.logger.log(TRACE1, 'result=[%s], response1=[%s]' % (result, response))
        return result, response

class DeleteJob(AdminService):
    """ Deletes a scheduler's job.
    """
    @synchronized()
    def handle(self, *args, **kwargs):
        payload = kwargs.get('payload')
        job_name = unicode(zato_path('job.job_name', True).get_from(payload))

        result, response = self.server.send_config_request('DELETE_JOB', job_name,
                            timeout=3.0)
        self.logger.log(TRACE1, 'result=[%s], response1=[%s]' % (result, response))
        return result, response
        
'''