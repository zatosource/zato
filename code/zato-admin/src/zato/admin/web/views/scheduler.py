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
from json import dumps
from uuid import uuid4
from time import strptime
from traceback import format_exc

# Django
from django.http import HttpResponse, HttpResponseServerError
from django.shortcuts import render_to_response

# lxml
from lxml import etree
from lxml.objectify import Element

# Zato
from zato.admin.web import invoke_admin_service
from zato.admin.web.forms import ChooseClusterForm
from zato.admin.web.views import meth_allowed
from zato.admin.settings import job_type_friendly_names
from zato.admin.web.server_model import OneTimeSchedulerJob, IntervalBasedSchedulerJob
from zato.admin.web.forms.scheduler import OneTimeSchedulerJobForm, IntervalBasedSchedulerJobForm
from zato.common import scheduler_date_time_format_one_time, scheduler_date_time_format_interval_based, \
     ZATO_OK, zato_namespace, zato_path, ZatoException
from zato.common.odb.model import Cluster, Job
from zato.common.util import pprint, TRACE1

logger = logging.getLogger(__name__)

create_one_time_prefix = 'create-one-time'
create_interval_based_prefix = 'create-interval-based'
edit_one_time_prefix = 'edit-one-time'
edit_interval_based_prefix = 'edit-interval-based'

def _get_start_date(start_date, start_date_format):
    if not start_date:
        return ''

    strp = strptime(str(start_date), start_date_format)
    return datetime(year=strp.tm_year, month=strp.tm_mon, day=strp.tm_mday,
                       hour=strp.tm_hour, minute=strp.tm_min)

def _get_one_time_job_definition(start_date):
    start_date = _get_start_date(start_date, scheduler_date_time_format_one_time)
    return 'Execute once on {0} at {1}'.format(start_date.strftime('%Y-%m-%d'),
                start_date.strftime('%H:%M:%S'))

def _get_interval_based_job_definition(start_date, repeat, weeks, days, hours,
                                        minutes, seconds):

    buf = StringIO()

    if start_date:
        buf.write('Start on %s, at %s.' % (start_date.strftime('%Y-%m-%d'),
                start_date.strftime('%H:%M:%S')))

    if not repeat:
        buf.write(' Repeat indefinitely.')
    else:
        if repeat == 1:
            buf.write(' Execute once.')
        elif repeat == 2:
            buf.write(' Repeat twice.')
        # .. my hand is itching to add the 'Repeat thrice.' here ;-)
        elif repeat > 2:
            buf.write(' Repeat ')
            buf.write(str(repeat))
            buf.write(' times.')

    interval = []
    buf.write(' Interval: ')
    for name, value in (('week',weeks), ('day',days),
                    ('hour',hours), ('minute',minutes),
                    ('second',seconds)):
        if value:
            interval.append('%s %s%s' % (value, name, 's' if value > 1 else ''))

    buf.write(', '.join(interval))
    buf.write('.')

    return buf.getvalue()

def _get_create_edit_message(cluster, params, form_prefix=""):
    """ Creates a base document which can be used by both 'edit' and 'create'
    actions, regardless of the job's type.
    """
    zato_message = Element('{%s}zato_message' % zato_namespace)
    zato_message.data = Element('data')
    zato_message.data.name = params[form_prefix + 'name']
    zato_message.data.cluster_id = cluster.id
    zato_message.data.is_active = bool(params.get(form_prefix + 'is_active'))
    zato_message.data.service = params.get(form_prefix + 'service', '')
    zato_message.data.extra = params.get(form_prefix + 'extra', '')

    return zato_message

def _get_create_edit_one_time_message(cluster, params, form_prefix=""):
    """ Creates a base document which can be used by both 'edit' and 'create'
    actions. Used when creating one-time jobs.
    """
    zato_message = _get_create_edit_message(cluster, params, form_prefix)
    zato_message.data.job_type = 'one_time'
    zato_message.data.start_date = params[form_prefix + 'start_date']

    return zato_message

def _get_create_edit_interval_based_message(params, form_prefix=""):
    """ Creates a base document which can be used by both 'edit' and 'create'
    actions. Used when creating interval-based jobs.
    """
    zato_message = _get_create_edit_message(params, form_prefix)
    zato_message.data.job_type = 'interval_based'
    zato_message.data.weeks = unicode(params.get(form_prefix + 'weeks', ''))
    zato_message.data.days = unicode(params.get(form_prefix + 'days', ''))
    zato_message.data.hours = unicode(params.get(form_prefix + 'hours', ''))
    zato_message.data.seconds = unicode(params.get(form_prefix + 'seconds', ''))
    zato_message.data.minutes = unicode(params.get(form_prefix + 'minutes', ''))
    zato_message.data.repeat = unicode(params.get(form_prefix + 'repeat', ''))
    zato_message.data.start_date = params.get(form_prefix + 'start_date', '')

    return zato_message

def _create_one_time(cluster, params):
    """ Creates a one-time scheduler job.
    """
    logger.info('About to create a one-time job, cluster.id=[{0}], params=[{1}]'.format(cluster.id, params))
    zato_message = _get_create_edit_one_time_message(cluster, params, create_one_time_prefix+'-')

    _, zato_message, soap_response = invoke_admin_service(cluster, 'zato:scheduler.job.create', zato_message)
    new_id = zato_message.data.job.id.text
    logger.info('Successfully created a one-time job, cluster.id=[{0}], params=[{1}]'.format(cluster.id, params))

    return dumps({'id': new_id, 
            'definition_text':_get_one_time_job_definition(params['create-one-time-start_date'])})

def _create_interval_based(server_address, params):
    """ Creates an interval-based scheduler job.
    """
    logger.info('About to create an interval-based job, server_address=[%s], params=[%s]' % (server_address, params))
    zato_message = _get_create_edit_interval_based_message(params, create_interval_based_prefix+'-')

    invoke_admin_service(server_address, 'zato:scheduler.job.create', etree.tostring(zato_message))

    start_date = params.get('create-interval-based-start_date')
    if start_date:
        start_date = _get_start_date(start_date, scheduler_date_time_format_one_time)
    repeat = params.get('create-interval-based-repeat')
    weeks = params.get('create-interval-based-weeks')
    days = params.get('create-interval-based-days')
    hours = params.get('create-interval-based-hours')
    minutes = params.get('create-interval-based-minutes')
    seconds = params.get('create-interval-based-seconds')

    definition = _get_interval_based_job_definition(start_date, repeat, weeks,
                    days, hours, minutes, seconds)

    logger.info('Successfully created an interval-based job, server_address=[%s], params=[%s]' % (server_address, params))
    logger.log(TRACE1, 'definition=[%s]' % definition)

    return definition

def _edit_one_time(server_address, params):
    """ Updates a one-time scheduler job.
    """
    logger.info('About to change a one-time job, server_address=[%s], params=[%s]' % (server_address, params))
    zato_message = _get_create_edit_one_time_message(params, edit_one_time_prefix+'-')

    # original_name is needed only by an 'edit' action.
    zato_message.data.job.original_name = params.get('edit-one-time-original_name')
    invoke_admin_service(server_address, 'zato:scheduler.job.edit', etree.tostring(zato_message))

    dt = _get_start_date(params['edit-one-time-start_date'], scheduler_date_time_format_one_time)
    logger.log(TRACE1, 'dt=[%s]' % dt)

    job = OneTimeSchedulerJob(start_date=dt)

    logger.info('Successfully changed a one-time job, server_address=[%s], params=[%s]' % (server_address, params))
    logger.log(TRACE1, 'job.definition=[%s]' % job.definition)

    return job.definition

def _edit_interval_based(server_address, params):
    """ Creates an interval-based scheduler job.
    """
    logger.info('About to change an interval-based job, server_address=[%s], params=[%s]' % (server_address, params))
    zato_message = _get_create_edit_interval_based_message(params, edit_interval_based_prefix+'-')

    # original_name is needed only by an 'edit' action.
    zato_message.data.job.original_name = params.get('edit-interval-based-original_name')
    invoke_admin_service(server_address, 'zato:scheduler.job.edit', etree.tostring(zato_message))

    start_date = params.get('edit-interval-based-start_date')
    if start_date:
        start_date = _get_start_date(start_date, scheduler_date_time_format_one_time)
    repeat = params.get('edit-interval-based-repeat')
    weeks = params.get('edit-interval-based-weeks')
    days = params.get('edit-interval-based-days')
    hours = params.get('edit-interval-based-hours')
    minutes = params.get('edit-interval-based-minutes')
    seconds = params.get('edit-interval-based-seconds')

    definition = _get_interval_based_job_definition(start_date, repeat, weeks,
                    days, hours, minutes, seconds)

    logger.info('Saved changes to an interval-based job, server_address=[%s], params=[%s]' % (server_address, params))
    logger.log(TRACE1, 'definition=[%s]' % definition)

    return definition

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
                
                job = None
                
                id = job_elem.id.text
                name = job_elem.name.text
                is_active = job_elem.is_active.text
                job_type = job_elem.job_type.text
                
                #service = job_elem.service.text
                job_type_friendly = job_type_friendly_names[job_type]
                
                if job_type == 'one_time':

                    '''job = OneTimeSchedulerJob(uuid4().hex, original_name, name, job_type,
                                       job_type_friendly, service, extra,
                                       _get_start_date(job_elem.start_date, scheduler_date_time_format_one_time),
                                       job_elem.start_date)
                                       '''
                    job = Job(id, name, is_active, job_type_friendly=job_type_friendly)

                elif job_type == 'interval_based':
                    start_date = _get_start_date(job_elem.start_date, scheduler_date_time_format_interval_based)
                    definition = _get_interval_based_job_definition(start_date,
                            job_elem.repeat, job_elem.weeks, job_elem.days,
                            job_elem.hours, job_elem.minutes, job_elem.seconds)
                    job = IntervalBasedSchedulerJob(uuid4().hex, original_name, name, job_type,
                                       job_type_friendly, service, extra,
                                       start_date,  job_elem.start_date, job_elem.weeks,
                                       job_elem.days, job_elem.hours, job_elem.minutes,
                                       job_elem.seconds, job_elem.repeat,
                                       definition)
                else:
                    msg = 'Unrecognized job type, name=[%s], type=[%s]'.format(name, job_type)
                    logger.error(msg)
                    raise ZatoException(msg)

                jobs.append(job)
        else:
            logger.info('No jobs found, soap_response=[%s]'.format(soap_response))

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


        cluster = req.odb.query(Cluster).filter_by(id=cluster_id).one()

        # Try to match the action and a job type with an action handler..
        handler_name = '_' + action
        if action != 'execute':
            handler_name += '_' + job_type

        handler = globals().get(handler_name)
        if not handler:
            msg = ('No handler found for action [%s], job_type=[%s], '
                   'req.POST=[%s], req.GET=[%s].') % (action, job_type,
                      pprint(req.POST), pprint(req.GET))

            logger.error(msg)
            return HttpResponseServerError(msg)

        # .. invoke the action handler.
        try:
            response = handler(cluster, req.POST)
            response = response if response else ''
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
        'edit_one_time_form':OneTimeSchedulerJobForm(prefix=edit_one_time_prefix),
        'edit_interval_based_form':IntervalBasedSchedulerJobForm(prefix=edit_interval_based_prefix)
        })

@meth_allowed("POST")
def delete(req):
    """ Deletes a scheduler's job.
    """
    try:
        server_id = req.GET.get('server')
        name = req.GET.get('name')

        if not server_id:
            raise ZatoException('No [server] parameter found, req.GET=[%s]' % req.GET)

        if not name:
            raise ZatoException('No [name] parameter found, req.GET=[%s]' % req.GET)

        server = Server.objects.get(id=server_id)
        zato_message = Element('{%s}zato_message' % zato_namespace)
        zato_message.job = Element('job')
        zato_message.job.name = name

        invoke_admin_service(server.address, 'zato:scheduler.job.delete', etree.tostring(zato_message))

    except Exception, e:
        msg = 'Could not delete the job. server_id=[%s], name=[%s], e=[%s]' % (req.GET.get('server'), req.GET.get('name'), format_exc())
        logger.error(msg)
        return HttpResponseServerError(msg)
    else:
        # 200 OK
        return HttpResponse()

@meth_allowed('POST')
def get_definition(req, start_date, repeat, weeks, days, hours, minutes, seconds):
    start_date = _get_start_date(start_date, scheduler_date_time_format_interval_based)

    definition = _get_interval_based_job_definition(start_date, repeat, weeks, days, hours, minutes, seconds)
    logger.log(TRACE1, 'definition=[%s]' % definition)

    return HttpResponse(definition)
