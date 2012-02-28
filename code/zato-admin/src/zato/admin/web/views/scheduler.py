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


""" Views related to management of server's scheduler jobs.
"""

# stdlib
import logging
from cStringIO import StringIO
from datetime import datetime
from uuid import uuid4
from time import strptime
from traceback import format_exc

# Django
from django.http import HttpResponse, HttpResponseServerError
from django.shortcuts import render_to_response
from django.template import RequestContext

# lxml
from lxml import etree
from lxml.objectify import Element

# Validate
from validate import is_boolean

# anyjson
from anyjson import dumps

# Zato
from zato.admin.web import invoke_admin_service
from zato.admin.web.forms import ChooseClusterForm
from zato.admin.web.views import meth_allowed
from zato.admin.settings import job_type_friendly_names
from zato.admin.web.server_model import OneTimeSchedulerJob, IntervalBasedSchedulerJob
from zato.admin.web.forms.scheduler import CronStyleSchedulerJobForm, \
     IntervalBasedSchedulerJobForm, OneTimeSchedulerJobForm
from zato.common import scheduler_date_time_format, ZATO_OK, zato_namespace, \
     zato_path, ZatoException
from zato.common.odb.model import Cluster, CronStyleJob, IntervalBasedJob, Job
from zato.common.util import pprint, TRACE1

logger = logging.getLogger(__name__)

create_one_time_prefix = 'create-one_time'
create_interval_based_prefix = 'create-interval_based'
create_cron_style_prefix = 'create-cron_style'
edit_one_time_prefix = 'edit-one_time'
edit_interval_based_prefix = 'edit-interval_based'
edit_cron_style_prefix = 'edit-cron_style'

def _get_start_date(start_date, start_date_format):
    if not start_date:
        return ''

    strp = strptime(str(start_date), start_date_format)
    return datetime(year=strp.tm_year, month=strp.tm_mon, day=strp.tm_mday,
                       hour=strp.tm_hour, minute=strp.tm_min, second=strp.tm_sec)

def _one_time_job_def(start_date):
    start_date = _get_start_date(start_date, scheduler_date_time_format)
    return 'Execute once on {0} at {1}'.format(start_date.strftime('%Y-%m-%d'),
                start_date.strftime('%H:%M:%S'))

def _interval_based_job_def(start_date, repeats, weeks, days, hours, minutes, seconds):

    buf = StringIO()

    if start_date:
        buf.write('Start on {0} at {1}.'.format(start_date.strftime('%Y-%m-%d'),
                start_date.strftime('%H:%M:%S')))

    if not repeats:
        buf.write(' Repeat indefinitely.')
    else:
        if repeats == 1:
            buf.write(' Execute once.')
        elif repeats == 2:
            buf.write(' Repeat twice.')
        # .. my hand is itching to add 'repeats thrice.' here ;-)
        elif repeats > 2:
            buf.write(' Repeat ')
            buf.write(str(repeats))
            buf.write(' times.')

    interval = []
    buf.write(' Interval: ')
    for name, value in (('week',weeks), ('day',days),
                    ('hour',hours), ('minute',minutes),
                    ('second',seconds)):
        if value:
            value = int(value)
            interval.append('{0} {1}{2}'.format(value, name, 's' if value > 1 else ''))

    buf.write(', '.join(interval))
    buf.write('.')

    return buf.getvalue()

def _get_success_message(action, job_type, job_name):

    msg = 'Successfully {0} the {1} job [{2}]'
    verb = 'created' if action == 'create' else 'updated'
    job_type = job_type.replace('_', '-')
    
    return msg.format(verb, job_type, job_name)
        

def _cron_style_job_def(start_date, cron_definition):
    start_date = _get_start_date(start_date, scheduler_date_time_format)

    buf = StringIO()
    buf.write('Start on {0} at {1}.'.format(start_date.strftime('%Y-%m-%d'),
               start_date.strftime('%H:%M:%S')))
    buf.write('<br/>{0}'.format(cron_definition))
    
    return buf.getvalue()

def _get_create_edit_message(cluster, params, form_prefix=""):
    """ Creates a base document which can be used by both 'edit' and 'create'
    actions, regardless of the job's type.
    """
    zato_message = Element('{%s}zato_message' % zato_namespace)
    zato_message.data = Element('data')
    zato_message.data.name = params[form_prefix + 'name']
    zato_message.data.cluster_id = cluster.id
    zato_message.data.id = params.get(form_prefix + 'id', '')
    zato_message.data.is_active = bool(params.get(form_prefix + 'is_active'))
    zato_message.data.service = params.get(form_prefix + 'service', '')
    zato_message.data.extra = params.get(form_prefix + 'extra', '')
    zato_message.data.start_date = params.get(form_prefix + 'start_date', '')
    
    return zato_message

def _get_create_edit_one_time_message(cluster, params, form_prefix=''):
    """ Creates a base document which can be used by both 'edit' and 'create'
    actions. Used when creating one_time jobs.
    """
    zato_message = _get_create_edit_message(cluster, params, form_prefix)
    zato_message.data.job_type = 'one_time'

    return zato_message

def _get_create_edit_interval_based_message(cluster, params, form_prefix=''):
    """ Creates a base document which can be used by both 'edit' and 'create'
    actions. Used when creating interval_based jobs.
    """
    zato_message = _get_create_edit_message(cluster, params, form_prefix)
    zato_message.data.job_type = 'interval_based'
    zato_message.data.weeks = params.get(form_prefix + 'weeks', '')
    zato_message.data.days = params.get(form_prefix + 'days', '')
    zato_message.data.hours = params.get(form_prefix + 'hours', '')
    zato_message.data.seconds = params.get(form_prefix + 'seconds', '')
    zato_message.data.minutes = params.get(form_prefix + 'minutes', '')
    zato_message.data.repeats = params.get(form_prefix + 'repeats', '')

    return zato_message

def _get_create_edit_cron_style_message(cluster, params, form_prefix=''):
    """ Creates a base document which can be used by both 'edit' and 'create'
    actions. Used when creating cron_style jobs.
    """
    zato_message = _get_create_edit_message(cluster, params, form_prefix)
    zato_message.data.job_type = 'cron_style'
    zato_message.data.cron_definition = params[form_prefix + 'cron_definition']

    return zato_message

def _create_one_time(cluster, params):
    """ Creates a one_time scheduler job.
    """
    logger.debug('About to create a one_time job, cluster.id=[{0}], params=[{1}]'.format(cluster.id, params))
    zato_message = _get_create_edit_one_time_message(cluster, params, create_one_time_prefix+'-')

    _, zato_message, soap_response = invoke_admin_service(cluster, 'zato:scheduler.job.create', zato_message)
    new_id = zato_message.data.job.id.text
    logger.debug('Successfully created a one_time job, cluster.id=[{0}], params=[{1}]'.format(cluster.id, params))

    return {'id': new_id, 
            'definition_text':_one_time_job_def(params['create-one_time-start_date'])}

def _create_interval_based(cluster, params):
    """ Creates an interval_based scheduler job.
    """
    logger.debug('About to create an interval_based job, cluster.id=[{0}], params=[{1}]'.format(cluster.id, params))
    zato_message = _get_create_edit_interval_based_message(cluster, params, create_interval_based_prefix+'-')

    _, zato_message, soap_response = invoke_admin_service(cluster, 'zato:scheduler.job.create', zato_message)
    new_id = zato_message.data.job.id.text
    logger.debug('Successfully created an interval_based job, cluster.id=[{0}], params=[{1}]'.format(cluster.id, params))

    start_date = params.get('create-interval_based-start_date')
    if start_date:
        start_date = _get_start_date(start_date, scheduler_date_time_format)
    repeats = params.get('create-interval_based-repeats')
    weeks = params.get('create-interval_based-weeks')
    days = params.get('create-interval_based-days')
    hours = params.get('create-interval_based-hours')
    minutes = params.get('create-interval_based-minutes')
    seconds = params.get('create-interval_based-seconds')

    definition = _interval_based_job_def(start_date, repeats, weeks, days, hours, 
                                         minutes, seconds)

    return {'id': new_id, 'definition_text':definition}

def _create_cron_style(cluster, params):
    """ Creates a cron_style scheduler job.
    """
    logger.debug('About to create a cron_style job, cluster.id=[{0}], params=[{1}]'.format(cluster.id, params))
    zato_message = _get_create_edit_cron_style_message(cluster, params, create_cron_style_prefix+'-')

    _, zato_message, soap_response = invoke_admin_service(cluster, 'zato:scheduler.job.create', zato_message)
    new_id = zato_message.data.job.id.text
    cron_definition = zato_message.data.job.cron_definition.text
    logger.debug('Successfully created a cron_style job, cluster.id=[{0}], params=[{1}]'.format(cluster.id, params))

    return {'id': new_id, 
            'definition_text':_cron_style_job_def(
                params['create-cron_style-start_date'], cron_definition),
            'cron_definition': cron_definition}

def _edit_one_time(cluster, params):
    """ Updates a one_time scheduler job.
    """
    logger.debug('About to change a one_time job, cluster.id=[{0}, params=[{1}]]'.format(cluster.id, params))
    zato_message = _get_create_edit_one_time_message(cluster, params, edit_one_time_prefix+'-')

    _, zato_message, soap_response = invoke_admin_service(cluster, 'zato:scheduler.job.edit', zato_message)
    logger.debug('Successfully updated a one_time job, cluster.id=[{0}], params=[{1}]'.format(cluster.id, params))

    return {'definition_text':_one_time_job_def(params['edit-one_time-start_date']), 'id':params['edit-one_time-id']}

def _edit_interval_based(cluster, params):
    """ Creates an interval_based scheduler job.
    """
    logger.debug('About to change an interval_based job, cluster.id=[{0}, params=[{1}]]'.format(cluster.id, params))
    zato_message = _get_create_edit_interval_based_message(cluster, params, edit_interval_based_prefix+'-')

    _, zato_message, soap_response = invoke_admin_service(cluster, 'zato:scheduler.job.edit', zato_message)
    logger.debug('Successfully updated an interval_based job, cluster.id=[{0}], params=[{1}]'.format(cluster.id, params))

    start_date = params.get('edit-interval_based-start_date')
    if start_date:
        start_date = _get_start_date(start_date, scheduler_date_time_format)
    repeats = params.get('edit-interval_based-repeats')
    weeks = params.get('edit-interval_based-weeks')
    days = params.get('edit-interval_based-days')
    hours = params.get('edit-interval_based-hours')
    minutes = params.get('edit-interval_based-minutes')
    seconds = params.get('edit-interval_based-seconds')

    definition = _interval_based_job_def(start_date, repeats, weeks, days, hours, 
                                         minutes, seconds)

    return {'definition_text':definition, 'id':params['edit-interval_based-id']}

def _edit_cron_style(cluster, params):
    """ Creates an cron_style scheduler job.
    """
    logger.debug('About to change a cron_style job, cluster.id=[{0}, params=[{1}]]'.format(cluster.id, params))
    zato_message = _get_create_edit_cron_style_message(cluster, params, edit_cron_style_prefix+'-')

    _, zato_message, soap_response = invoke_admin_service(cluster, 'zato:scheduler.job.edit', zato_message)
    cron_definition = zato_message.data.job.cron_definition.text
    logger.debug('Successfully updated a cron_style job, cluster.id=[{0}], params=[{1}]'.format(cluster.id, params))

    start_date = _get_start_date(params.get('edit-cron_style-start_date'), 
                                 scheduler_date_time_format)
    definition = _cron_style_job_def(start_date, cron_definition)

    return {'definition_text':definition, 'cron_definition': cron_definition, 'id':params['edit-cron_style-id']}

def _execute(server_address, params):
    """ Submits a request for an execution of a job.
    """
    logger.info('About to submit a request for an execution of a job, server_address=[%s], params=[%s]' % (server_address, params))

    zato_message = Element('{%s}zato_message' % zato_namespace)
    zato_message.job = Element('job')
    zato_message.job.name = params['name']
    invoke_admin_service(server_address, 'zato:scheduler.job.execute', etree.tostring(zato_message))

    logger.info('Successfully submitted a request, server_address=[%s], params=[%s]' % (server_address, params))

@meth_allowed('GET', 'POST')
def index(req):
    
    try:
        jobs = []
        zato_clusters = req.odb.query(Cluster).order_by('name').all()
        choose_cluster_form = ChooseClusterForm(zato_clusters, req.GET)
        cluster_id = req.GET.get('cluster')
    
        # Build a list of schedulers for a given Zato cluster.
        if cluster_id and req.method == 'GET':
    
            # We have a server to pick the schedulers from, try to invoke it now.
            cluster = req.odb.query(Cluster).filter_by(id=cluster_id).first()
            zato_message = Element('{%s}zato_message' % zato_namespace)
            zato_message.data = Element('data')
            zato_message.data.cluster_id = cluster_id
            _, zato_message, soap_response  = invoke_admin_service(cluster, 
                    'zato:scheduler.job.get-list', zato_message)
            
            if zato_path('data.definition_list.definition').get_from(zato_message) is not None:
                for job_elem in zato_message.data.definition_list.definition:
                    
                    id = job_elem.id.text
                    name = job_elem.name.text
                    is_active = is_boolean(job_elem.is_active.text)
                    job_type = job_elem.job_type.text
                    start_date = job_elem.start_date.text
                    service_name = job_elem.service_name.text
                    extra = job_elem.extra.text if job_elem.extra.text else ''
                    job_type_friendly = job_type_friendly_names[job_type]
                    
                    job = Job(id, name, is_active, job_type, start_date,
                              extra, service_name=service_name, 
                              job_type_friendly=job_type_friendly)
                    
                    if job_type == 'one_time':
                        definition_text=_one_time_job_def(start_date)
                        
                    elif job_type == 'interval_based':
                        definition_text = _interval_based_job_def(
                            _get_start_date(job_elem.start_date, scheduler_date_time_format),
                                job_elem.repeats, job_elem.weeks, job_elem.days,
                                job_elem.hours, job_elem.minutes, job_elem.seconds)
                        
                        weeks = job_elem.weeks.text if job_elem.weeks.text else ''
                        days = job_elem.days.text if job_elem.days.text else ''
                        hours = job_elem.hours.text if job_elem.hours.text else ''
                        minutes = job_elem.minutes.text if job_elem.minutes.text else ''
                        seconds = job_elem.seconds.text if job_elem.seconds.text else ''
                        repeats = job_elem.repeats.text if job_elem.repeats.text else ''
                        
                        ib_job = IntervalBasedJob(None, None, weeks, days, hours, minutes,
                                            seconds, repeats)
                        job.interval_based = ib_job
                        
                    elif job_type == 'cron_style':
                        cron_definition = (job_elem.cron_definition.text if job_elem.cron_definition.text else '')
                        definition_text=_cron_style_job_def(start_date,  cron_definition)
                        
                        cs_job = CronStyleJob(None, None, cron_definition)
                        job.cron_style = cs_job
                        
                    else:
                        msg = 'Unrecognized job type, name=[{0}], type=[{1}]'.format(name, job_type)
                        logger.error(msg)
                        raise ZatoException(msg)
    
                    job.definition_text = definition_text
                    jobs.append(job)
            else:
                logger.info('No jobs found, soap_response=[{0}]'.format(soap_response))
    
        if req.method == 'POST':

            action = req.POST.get('zato_action', '')
            if not action:
                msg = 'req.POST contains no [zato_action] parameter.'
                logger.error(msg)
                return HttpResponseServerError(msg)
    
            job_type = req.POST.get('job_type', '')
            if action != 'execute' and not job_type:
                msg = 'req.POST contains no [job_type] parameter.'
                logger.error(msg)
                return HttpResponseServerError(msg)
    
            
            job_name = req.POST['{0}-{1}-name'.format(action, job_type)]
            cluster = req.odb.query(Cluster).filter_by(id=cluster_id).one()
    
            # Try to match the action and a job type with an action handler..
            handler_name = '_' + action
            if action != 'execute':
                handler_name += '_' + job_type
    
            handler = globals().get(handler_name)
            if not handler:
                msg = ('No handler found for action [{0}], job_type=[{1}], '
                       'req.POST=[{2}], req.GET=[{3}].'.format(action, job_type,
                          pprint(req.POST), pprint(req.GET)))
    
                logger.error(msg)
                return HttpResponseServerError(msg)
    
            # .. invoke the action handler.
            try:
                response = handler(cluster, req.POST)
                response = response if response else ''
                if response:
                    response['message'] = _get_success_message(action, job_type, job_name)
                    response = dumps(response)
                return HttpResponse(response, mimetype='application/javascript')
            except Exception, e:
                msg = ('Could not invoke action [%s], job_type=[%s], e=[%s]'
                       'req.POST=[%s], req.GET=[%s]') % (action, job_type,
                          format_exc(), pprint(req.POST), pprint(req.GET))
    
                logger.error(msg)
                return HttpResponseServerError(msg)
    
        # TODO: Log the data returned here.
        logger.log(TRACE1, 'Returning render_to_response.')
    
        return render_to_response('zato/scheduler.html',
            {'zato_clusters':zato_clusters,
            'cluster_id':cluster_id,
            'choose_cluster_form':choose_cluster_form,
            'jobs':jobs, 
            'cluster_id':cluster_id,
            'friendly_names':job_type_friendly_names.items(),
            'create_one_time_form':OneTimeSchedulerJobForm(prefix=create_one_time_prefix),
            'create_interval_based_form':IntervalBasedSchedulerJobForm(prefix=create_interval_based_prefix),
            'create_cron_style_form':CronStyleSchedulerJobForm(prefix=create_cron_style_prefix),
            'edit_one_time_form':OneTimeSchedulerJobForm(prefix=edit_one_time_prefix),
            'edit_interval_based_form':IntervalBasedSchedulerJobForm(prefix=edit_interval_based_prefix),
            'edit_cron_style_form':CronStyleSchedulerJobForm(prefix=edit_cron_style_prefix),
            }, context_instance=RequestContext(req))
    except Exception, e:
        msg = '<pre>Could not invoke the method, e=[{0}]</pre>'.format(format_exc(e))
        logger.error(msg)
        return HttpResponseServerError(msg)

@meth_allowed('POST')
def delete(req, job_id, cluster_id):
    """ Deletes a scheduler's job.
    """
    try:
        cluster = req.odb.query(Cluster).filter_by(id=cluster_id).first()
        zato_message = Element('{%s}zato_message' % zato_namespace)
        zato_message.data = Element('data')
        zato_message.data.id = job_id

        invoke_admin_service(cluster, 'zato:scheduler.job.delete', zato_message)

    except Exception, e:
        msg = 'Could not delete the job. job_id=[{0}], cluster_id=[{1}], e=[{2}]'.format(
            job_id, cluster_id, format_exc(e))
        logger.error(msg)
        return HttpResponseServerError(msg)
    else:
        # 200 OK
        return HttpResponse()
    
@meth_allowed('POST')
def execute(req, job_id, cluster_id):
    """ Executes a scheduler's job.
    """
    try:
        cluster = req.odb.query(Cluster).filter_by(id=cluster_id).first()
        zato_message = Element('{%s}zato_message' % zato_namespace)
        zato_message.data = Element('data')
        zato_message.data.id = job_id

        invoke_admin_service(cluster, 'zato:scheduler.job.execute', zato_message)

    except Exception, e:
        msg = 'Could not execute the job. job_id=[{0}], cluster_id=[{1}], e=[{2}]'.format(
            job_id, cluster_id, format_exc(e))
        logger.error(msg)
        return HttpResponseServerError(msg)
    else:
        # 200 OK
        return HttpResponse()

@meth_allowed('POST')
def get_definition(req, start_date, repeats, weeks, days, hours, minutes, seconds):
    start_date = _get_start_date(start_date, scheduler_date_time_format)

    definition = _interval_based_job_def(start_date, repeats, weeks, days, hours, minutes, seconds)
    logger.log(TRACE1, 'definition=[%s]' % definition)

    return HttpResponse(definition)
