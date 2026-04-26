# -*- coding: utf-8 -*-

"""
Copyright (C) 2026, Zato Source s.r.o. https://zato.io

Licensed under AGPLv3, see LICENSE.txt for terms and conditions.
"""

# stdlib
import json
import logging
import time

# Django
from django.http import HttpResponse
from django.template.response import TemplateResponse

# Zato
from zato.admin.web.views import method_allowed
from zato.common.defaults import default_cluster_id

# ################################################################################################################################
# ################################################################################################################################

logger = logging.getLogger(__name__)

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def index(req):

    try:
        response = req.zato.client.invoke('zato.scheduler.job.get-current-state', {})
        if response.ok:
            data_json = json.dumps(response.data)
        else:
            data_json = '{}'
    except Exception as e:
        logger.error('Scheduler dashboard error: %s', e)
        data_json = '{}'

    return TemplateResponse(req, 'zato/scheduler/dashboard.html', {
        'cluster_id': default_cluster_id,
        'dashboard_data': data_json,
        'zato_clusters': True,
        'zato_template_name': 'zato/scheduler/dashboard.html',
    })

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('POST')
def poll(req):

    try:
        t0 = time.monotonic()
        response = req.zato.client.invoke('zato.scheduler.job.get-current-state', {})
        elapsed = time.monotonic() - t0
        if elapsed > 2.0:
            logger.warning('Scheduler dashboard poll invoke took %.1fs', elapsed)
        if response.ok:
            return HttpResponse(json.dumps(response.data), content_type='application/json')
        else:
            return HttpResponse(
                json.dumps({'error': response.details}),
                content_type='application/json',
                status=500,
            )
    except Exception as e:
        logger.error('Scheduler dashboard poll error: %s', e)
        return HttpResponse(
            json.dumps({'error': str(e)}),
            content_type='application/json',
            status=500,
        )

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def job_detail(req, job_id:'int'):

    job_data = {}

    try:
        response = req.zato.client.invoke('zato.scheduler.job.get-by-id', {
            'cluster_id': default_cluster_id,
            'id': job_id,
        })
        if response.ok:
            job_data = response.data
    except Exception as e:
        logger.error('Scheduler job detail error: %s', e)

    try:
        state_response = req.zato.client.invoke('zato.scheduler.job.get-current-state', {})
        if state_response.ok:
            state_data = state_response.data
            job_name = job_data['name']

            for entry in state_data['jobs']:
                if entry['id'] == job_id or entry['name'] == job_name:
                    job_data['next_fire_utc'] = entry['next_fire_utc']
                    job_data['is_running'] = entry['is_running']
                    job_data['current_run'] = entry['current_run']
                    job_data['interval_ms'] = entry['interval_ms']
                    job_data['recent_outcomes'] = entry['recent_outcomes']
                    job_data['last_outcome'] = entry['last_outcome']
                    job_data['last_duration_ms'] = entry['last_duration_ms']
                    break

    except Exception as e:
        logger.error('Scheduler job state error: %s', e)

    return TemplateResponse(req, 'zato/scheduler/job_detail.html', {
        'cluster_id': default_cluster_id,
        'job_id': job_id,
        'job_data': json.dumps(job_data),
        'poll_url': '/zato/dashboard/detail-poll/',
        'object_type': 'scheduler-job',
        'zato_clusters': True,
        'zato_template_name': 'zato/scheduler/job_detail.html',
    })

# ################################################################################################################################
# ################################################################################################################################

@method_allowed('GET')
def run_detail(req, job_id:'int', run_number:'int'):
    """ Shows the log entries for a single execution record of a scheduler job.
    """

    job_data = {}

    try:
        response = req.zato.client.invoke('zato.scheduler.job.get-by-id', {
            'cluster_id': default_cluster_id,
            'id': job_id,
        })
        if response.ok:
            job_data = response.data
    except Exception as e:
        logger.error('Scheduler run detail error: %s', e)

    return TemplateResponse(req, 'zato/scheduler/run_detail.html', {
        'cluster_id': default_cluster_id,
        'job_id': job_id,
        'run_number': run_number,
        'job_data': json.dumps(job_data),
        'poll_url': '/zato/dashboard/detail-poll/',
        'object_type': 'scheduler-job',
        'zato_clusters': True,
        'zato_template_name': 'zato/scheduler/run_detail.html',
    })

# ################################################################################################################################
# ################################################################################################################################
